"""traffic_based_enumerator.py

Spatial-coordinate-driven external source enumerator that primarily uses
live TCP/UDP connection state and related connection-based protocol evidence,
rather than only raw RF scans.

Workflow:
1. Load spatial point-cloud data from probe-sequence/spectrum_data/lidar_scan_test.json
   or live LIDAR scans.
2. Convert spatial coordinates to bearings/elevations relative to scanner origin.
3. Enumerate active TCP connections via psutil/OS network stats.
4. Fuse connection data with spatial sectors and spectrum channel data.
5. Safety-check any active tuning/scanning through Magi-Zone before execution.
6. Persist results to probe-sequence/spectrum_data/external_sources.json.
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
    from conscience_escape_bridge import run_magi_escape
    BRIDGE_AVAILABLE = True
except Exception:
    BRIDGE_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except Exception:
    PSUTIL_AVAILABLE = False

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
# TCP / connection enumeration
# ---------------------------------------------------------------------------
def _enumerate_connections_psutil() -> List[ConnectionRecord]:
    records: List[ConnectionRecord] = []
    if not PSUTIL_AVAILABLE:
        return records
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.raddr:
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


def _enumerate_connections_windows() -> List[ConnectionRecord]:
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
            if len(parts) >= 4:
                proto = parts[0].lower()
                state = parts[3].lower() if len(parts) > 3 else "unknown"
                local = parts[1]
                remote = parts[2]
                pid = None
                if len(parts) >= 5:
                    try:
                        pid = int(parts[4])
                    except ValueError:
                        pid = None

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

                local_addr, local_port = _split_endpoint(local)
                remote_addr, remote_port = _split_endpoint(remote)
                if remote_addr in ("0.0.0.0", "::", "*"):
                    continue
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


def enumerate_connections() -> List[ConnectionRecord]:
    if PSUTIL_AVAILABLE:
        return _enumerate_connections_psutil()
    if platform.system().lower() == "windows":
        return _enumerate_connections_windows()
    return []


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
# Channel mapping
# ---------------------------------------------------------------------------
def _port_to_channel_estimates(port: int) -> Tuple[Optional[int], Optional[float], Optional[str]]:
    """Rough mapping from remote port to likely WiFi/spectrum channel/frequency/band."""
    if 1 <= port <= 65535:
        if port in (80, 443, 8080, 8443):
            return None, None, "http/https"
        if port == 53:
            return 6, 2437.0, "2.4GHz"
        if port == 22:
            return 153, 5765.0, "5GHz"
        if port == 3389:
            return 149, 5745.0, "5GHz"
    return None, None, "unknown"


# ---------------------------------------------------------------------------
# Main enumerator
# ---------------------------------------------------------------------------
def enumerate_external_sources(
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

    connections = enumerate_connections()
    by_remote: Dict[str, List[ConnectionRecord]] = {}
    for conn in connections:
        by_remote.setdefault(conn.remote_addr, []).append(conn)

    wifi_networks = []
    try:
        from spectrum_grabber.wifi_scanner import scan_wifi_cross_platform
        wifi_networks = scan_wifi_cross_platform()
    except Exception:
        try:
            from enhanced_wifi_scanner import enhanced_wifi_scan
            wifi_networks = enhanced_wifi_scan(extended_range=True, multiple_scans=1)
        except Exception:
            pass

    wifi_by_bssid = {}
    for ap in wifi_networks:
        bssid = getattr(ap, "bssid", None)
        if bssid:
            wifi_by_bssid[bssid.lower()] = ap

    enumerated: List[EnumeratedSource] = []
    used_ids = set()

    for sp in spatial_sources:
        channel, freq, band = _port_to_channel_estimates(sp.distance)
        best_wifi = None
        if wifi_networks:
            sp_signal = 50.0
            best = min(
                wifi_networks,
                key=lambda a: abs(float(getattr(a, "signal_percent", 0.0) or 0.0) - sp_signal),
            )
            best_wifi = best

        source_type = "spatial"
        identifier = sp.source_id
        if best_wifi:
            source_type = "spatial+wifi"
            identifier = getattr(best_wifi, "ssid", None) or getattr(best_wifi, "bssid", None) or identifier

        voice_phrases = tune_voice_phrases or ["ward", "shield"]
        movement = (sp.x - origin[0], sp.y - origin[1], sp.z - origin[2])
        ack = _magi_tune(voice_phrases=voice_phrases, origin3d=origin, movement_vector=movement)

        sid = identifier or sp.source_id
        if sid in used_ids:
            sid = f"{sid}_{sp.bearing_deg:.1f}_{sp.elevation_deg:.1f}"
        used_ids.add(sid)

        conn_rec = None
        if connections:
            remote_key = next(iter(by_remote.keys()))
            for rk, conns in by_remote.items():
                if conns:
                    c0 = conns[0]
                    conn_rec = {
                        "protocol": c0.protocol,
                        "local_addr": c0.local_addr,
                        "local_port": c0.local_port,
                        "remote_addr": c0.remote_addr,
                        "remote_port": c0.remote_port,
                        "status": c0.status,
                        "pid": c0.pid,
                        "estimated_channel": channel,
                        "estimated_frequency_mhz": freq,
                        "estimated_band": band,
                    }
                    break

        enumerated.append(
            EnumeratedSource(
                source_id=sid,
                source_type=source_type,
                identifier=identifier,
                frequency_mhz=getattr(best_wifi, "frequency_mhz", None) or freq,
                band=getattr(best_wifi, "band", None) or band,
                channel=getattr(best_wifi, "channel", None) or channel,
                signal_percent=getattr(best_wifi, "signal_percent", None),
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
        "connections_enumerated": len(connections),
        "connection_based_sources": len([e for e in enumerated if e.connection_record]),
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

    parser = argparse.ArgumentParser(description="Traffic-Based External Source Enumerator")
    parser.add_argument("--lidar", type=str, default=str(LIDAR_SCAN_TEST))
    parser.add_argument("--output", type=str, default=str(EXTERNAL_SOURCES_OUTPUT))
    parser.add_argument("--max", type=int, default=100)
    parser.add_argument("--origin", type=float, nargs=3, default=(0.0, 0.0, 0.0), metavar=("X", "Y", "Z"))
    parser.add_argument("--voice", action="append", default=[])
    args = parser.parse_args()

    report = enumerate_external_sources(
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
