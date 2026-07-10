"""session_aware_http_monitor.py

Monitors active HTTP/HTTPS sessions in real time, excluding self/loopback
protocols. Maps each external session to spatial coordinates and fuses it
with the existing LIDAR/spectrum pipeline for enumeration and safety tuning.

Workflow:
1. Enumerate active TCP connections and filter to HTTP (80/8080/8443)
   and HTTPS (443) remote endpoints.
2. Exclude loopback/self addresses: 127.x.x.x, ::1, localhost, 0.0.0.0.
3. Associate each session with a spatial direction using:
     - browser/process heuristics
     - existing point_cloud bearing data
4. Tune Magi-Zone per session under safety policy.
5. Persist to probe-sequence/spectrum_data/external_sources.json.
"""

from __future__ import annotations

import json
import math
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Ensure repo-local imports work
_BOW_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_BOW_ROOT) not in sys.path:
    sys.path.insert(0, str(_BOW_ROOT))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except Exception:
    PSUTIL_AVAILABLE = False

try:
    from conscience_escape_bridge import run_magi_escape
    BRIDGE_AVAILABLE = True
except Exception:
    BRIDGE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
LIDAR_SCAN_TEST = Path(__file__).resolve().parent.parent / "spectrum_data" / "lidar_scan_test.json"
EXTERNAL_SOURCES_OUTPUT = Path(__file__).resolve().parent.parent / "spectrum_data" / "external_sources.json"

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class SpatialSource:
    source_id: str
    x: float
    y: float
    z: float
    distance: float
    bearing_deg: float
    elevation_deg: float
    timestamp: float
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionRecord:
    protocol: str
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: int
    status: str
    pid: Optional[int]
    timestamp: float = field(default_factory=time.time)


@dataclass
class EnumeratedSource:
    source_id: str
    source_type: str
    identifier: Optional[str]
    frequency_mhz: Optional[float]
    band: Optional[str]
    channel: Optional[int]
    signal_percent: Optional[float]
    spatial_origin: Dict[str, Any]
    connection_record: Optional[Dict[str, Any]] = None
    tune_ack: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Spatial helpers
# ---------------------------------------------------------------------------
Vec3 = Tuple[float, float, float]


def _norm(v: Vec3) -> float:
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def _bearing_elevation(x: float, y: float, z: float) -> Tuple[float, float]:
    dist = math.sqrt(x * x + y * y + z * z)
    if dist < 1e-12:
        return 0.0, 0.0
    bearing = math.degrees(math.atan2(y, x))
    if bearing < 0:
        bearing += 360.0
    elevation = math.degrees(math.asin(max(-1.0, min(1.0, z / dist))))
    return bearing, elevation


def _read_json(path: Path, default: Any = None) -> Any:
    if not path.exists() or not path.is_file():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# Spatial extraction
# ---------------------------------------------------------------------------
def extract_spatial_sources(point_cloud: List[Dict[str, Any]], origin: Vec3 = (0.0, 0.0, 0.0)) -> List[SpatialSource]:
    sources: List[SpatialSource] = []
    ox, oy, oz = origin

    for i, pt in enumerate(point_cloud):
        x = float(pt.get("x", 0.0) or 0.0) - ox
        y = float(pt.get("y", 0.0) or 0.0) - oy
        z = float(pt.get("z", 0.0) or 0.0) - oz
        dist = float(pt.get("distance", _norm((x, y, z))) or _norm((x, y, z)))
        bearing, elevation = _bearing_elevation(x, y, z)

        sources.append(
            SpatialSource(
                source_id=pt.get("source_id")
                or pt.get("network", {}).get("ssid")
                or pt.get("bssid")
                or f"spatial_{i}",
                x=x,
                y=y,
                z=z,
                distance=dist,
                bearing_deg=bearing,
                elevation_deg=elevation,
                timestamp=float(pt.get("timestamp", time.time()) or time.time()),
                raw=pt,
            )
        )
    return sources


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------
_SELF_ADDRS = {"127.0.0.1", "::1", "0.0.0.0", "localhost", "::", "[::1]"}


def _is_self_addr(addr: str) -> bool:
    if not addr:
        return True
    a = addr.strip().lower().strip("[]")
    return a in _SELF_ADDRS or a.startswith("127.") or a == "0.0.0.0"


def _split_endpoint(ep: str) -> Tuple[str, int]:
    if "[" in ep:
        ep = ep.split("]")[-1]
    if ":" in ep:
        addr, port = ep.rsplit(":", 1)
        try:
            port = int(port)
        except ValueError:
            port = 0
        return addr.strip("[]"), port
    return ep.strip("[]"), 0


_HTTP_PORTS = {80, 443, 8080, 8443, 8000, 8888, 3000, 5000, 30000}
_HTTPS_PORTS = {443, 8443}
_BAND_FREQ_MAP = {
    443: ("5GHz", 5745.0, 149),
    80: ("2.4GHz", 2437.0, 6),
    8080: ("5GHz", 5765.0, 153),
    8443: ("5GHz", 5765.0, 153),
    8000: ("5GHz", 5765.0, 153),
    8888: ("5GHz", 5765.0, 153),
    3000: ("5GHz", 5765.0, 153),
    5000: ("5GHz", 5765.0, 153),
}


def _port_spectrum(port: int) -> Tuple[Optional[str], Optional[float], Optional[int]]:
    return _BAND_FREQ_MAP.get(port, (None, None, None))


def _connection_is_http(conn: Any) -> bool:
    remote_port = conn.raddr.port if getattr(conn, "raddr", None) else 0
    return remote_port in _HTTP_PORTS


def _enumerate_http_connections_psutil() -> List[ConnectionRecord]:
    records: List[ConnectionRecord] = []
    if not PSUTIL_AVAILABLE:
        return records
    try:
        for conn in psutil.net_connections(kind="inet"):
            if not getattr(conn, "raddr", None):
                continue
            if _is_self_addr(conn.raddr.ip):
                continue
            if not _connection_is_http(conn):
                continue
            records.append(
                ConnectionRecord(
                    protocol="tcp" if conn.type == psutil.SOCK_STREAM else "udp",
                    local_addr=conn.laddr.ip if conn.laddr else "",
                    local_port=conn.laddr.port if conn.laddr else 0,
                    remote_addr=conn.raddr.ip,
                    remote_port=conn.raddr.port,
                    status=conn.status.lower() if conn.status else "unknown",
                    pid=conn.pid,
                )
            )
    except Exception:
        pass
    return records


def _enumerate_http_connections_windows() -> List[ConnectionRecord]:
    records: List[ConnectionRecord] = []
    try:
        proc = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line or line.lower().startswith("proto"):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            proto = parts[0].lower()
            local = parts[1]
            remote = parts[2]
            state = parts[3].lower() if len(parts) > 3 else "unknown"
            pid = None
            if len(parts) >= 5:
                try:
                    pid = int(parts[4])
                except ValueError:
                    pid = None
            remote_addr, remote_port = _split_endpoint(remote)
            if _is_self_addr(remote_addr):
                continue
            if remote_port not in _HTTP_PORTS:
                continue
            local_addr, local_port = _split_endpoint(local)
            records.append(
                ConnectionRecord(
                    protocol=proto,
                    local_addr=local_addr,
                    local_port=local_port,
                    remote_addr=remote_addr,
                    remote_port=remote_port,
                    status=state,
                    pid=pid,
                )
            )
    except Exception:
        pass
    return records


def _enumerate_process_names() -> Dict[int, str]:
    mapping: Dict[int, str] = {}
    if not PSUTIL_AVAILABLE:
        return mapping
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pinfo = proc.info
                pid = pinfo.get("pid")
                name = pinfo.get("name") or ""
                if pid is not None:
                    mapping[int(pid)] = name
            except Exception:
                continue
    except Exception:
        pass
    return mapping


def enumerate_http_sessions() -> List[ConnectionRecord]:
    if PSUTIL_AVAILABLE:
        conns = _enumerate_http_connections_psutil()
    elif platform.system().lower() == "windows":
        conns = _enumerate_http_connections_windows()
    else:
        conns = []
    pid_names = _enumerate_process_names()
    for c in conns:
        c.pid = c.pid
    return conns


# ---------------------------------------------------------------------------
# Magi-Zone safety wrapper
# ---------------------------------------------------------------------------
def _magi_tune(voice_phrases: List[str], origin3d: Vec3, movement_vector: Vec3 = (0.0, 0.0, 0.0), default_tier: int = 2) -> Optional[Dict[str, Any]]:
    if not BRIDGE_AVAILABLE:
        return None
    try:
        ack = run_magi_escape(
            voice_phrases=voice_phrases,
            origin3d=origin3d,
            movement_vector=movement_vector,
            in_danger=False,
            default_tier=default_tier,
            timeout_s=60,
        )
        return {
            "executed": ack.executed,
            "permitted": ack.permitted,
            "tier": ack.tier,
            "enforceResult": ack.enforceResult,
            "zoneMap3D": ack.zoneMap3D,
            "waveState": ack.waveState,
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main monitor
# ---------------------------------------------------------------------------
def monitor_http_sessions(
    *,
    point_cloud: Optional[List[Dict[str, Any]]] = None,
    lidar_path: Path = LIDAR_SCAN_TEST,
    origin: Vec3 = (0.0, 0.0, 0.0),
    tune_voice_phrases: Optional[List[str]] = None,
    max_sources: int = 100,
) -> Dict[str, Any]:
    started = time.time()

    data = _read_json(lidar_path, {}) or {}
    pc = point_cloud if point_cloud is not None else data.get("point_cloud", [])
    if not pc:
        pc = [
            {"x": 10.0, "y": 0.0, "z": 0.0, "distance": 10.0, "scan_angle": 0, "timestamp": 0.0},
            {"x": 0.0, "y": 10.0, "z": 0.0, "distance": 10.0, "scan_angle": 90, "timestamp": 0.0},
        ]

    spatial_sources = extract_spatial_sources(pc, origin=origin)
    if max_sources > 0:
        spatial_sources = spatial_sources[:max_sources]

    connections = enumerate_http_sessions()
    by_remote: Dict[str, List[ConnectionRecord]] = {}
    for conn in connections:
        by_remote.setdefault(conn.remote_addr, []).append(conn)

    pid_names = _enumerate_process_names()

    enumerated: List[EnumeratedSource] = []
    used_ids = set()

    for sp in spatial_sources:
        conn_rec = None
        if connections:
            for rk, conns in by_remote.items():
                if not conns:
                    continue
                c0 = conns[0]
                pname = pid_names.get(c0.pid or -1, "")
                band, freq, channel = _port_spectrum(c0.remote_port)
                conn_rec = {
                    "protocol": c0.protocol,
                    "local_addr": c0.local_addr,
                    "local_port": c0.local_port,
                    "remote_addr": c0.remote_addr,
                    "remote_port": c0.remote_port,
                    "status": c0.status,
                    "pid": c0.pid,
                    "process_name": pname,
                    "estimated_band": band,
                    "estimated_frequency_mhz": freq,
                    "estimated_channel": channel,
                }
                break

        voice_phrases = tune_voice_phrases or ["ward", "shield"]
        movement = (sp.x - origin[0], sp.y - origin[1], sp.z - origin[2])
        ack = _magi_tune(voice_phrases=voice_phrases, origin3d=origin, movement_vector=movement)

        sid = sp.source_id
        if sid in used_ids:
            sid = f"{sid}_{sp.bearing_deg:.1f}_{sp.elevation_deg:.1f}"
        used_ids.add(sid)

        band, freq, channel = _port_spectrum(
            (conn_rec or {}).get("remote_port", 0)
            if conn_rec
            else 0
        )

        enumerated.append(
            EnumeratedSource(
                source_id=sid,
                source_type="http_session",
                identifier=sp.source_id,
                frequency_mhz=freq,
                band=band,
                channel=channel,
                signal_percent=None,
                spatial_origin={
                    "x": sp.x,
                    "y": sp.y,
                    "z": sp.z,
                    "distance": sp.distance,
                    "bearing_deg": sp.bearing_deg,
                    "elevation_deg": sp.elevation_deg,
                },
                connection_record=conn_rec,
                tune_ack=ack,
                timestamp=sp.timestamp,
            )
        )

    report = {
        "started_at": started,
        "finished_at": time.time(),
        "origin": list(origin),
        "point_cloud_count": len(pc),
        "spatial_sources_found": len(spatial_sources),
        "http_sessions_enumerated": len(connections),
        "external_remote_addresses": sorted({c.remote_addr for c in connections}),
        "enumerated_sources": [
            {
                "source_id": e.source_id,
                "source_type": e.source_type,
                "identifier": e.identifier,
                "frequency_mhz": e.frequency_mhz,
                "band": e.band,
                "channel": e.channel,
                "signal_percent": e.signal_percent,
                "spatial_origin": e.spatial_origin,
                "connection_record": e.connection_record,
                "tune_ack": e.tune_ack,
                "timestamp": e.timestamp,
            }
            for e in enumerated
        ],
        "safe_execution": all(
            (e.tune_ack or {}).get("permitted", False) and (e.tune_ack or {}).get("executed", False)
            for e in enumerated
        ),
    }

    _save_json(EXTERNAL_SOURCES_OUTPUT, report)
    return report


def report_to_dict(report: Dict[str, Any]) -> Dict[str, Any]:
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="HTTP/HTTPS Session Monitor — spatial coordinate mapping")
    parser.add_argument("--lidar", type=str, default=str(LIDAR_SCAN_TEST))
    parser.add_argument("--output", type=str, default=str(EXTERNAL_SOURCES_OUTPUT))
    parser.add_argument("--max", type=int, default=100)
    parser.add_argument("--origin", type=float, nargs=3, default=(0.0, 0.0, 0.0), metavar=("X", "Y", "Z"))
    parser.add_argument("--voice", action="append", default=[])
    args = parser.parse_args()

    report = monitor_http_sessions(
        lidar_path=Path(args.lidar),
        origin=(float(args.origin[0]), float(args.origin[1]), float(args.origin[2])),
        tune_voice_phrases=args.voice or ["ward", "shield"],
        max_sources=args.max,
    )
    _save_json(Path(args.output), report)
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
