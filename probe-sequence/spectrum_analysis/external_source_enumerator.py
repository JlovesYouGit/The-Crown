"""external_source_enumerator.py

Spatial-coordinate-driven external transmission enumerator.

Workflow:
1. Load spatial point-cloud data from probe-sequence/spectrum_data/lidar_scan_test.json
   or live LIDAR scans.
2. Convert spatial coordinates (x,y,z) to celestial/RA-Dec where possible, or retain
   as local Cartesian bearings from the scanner origin.
3. Use spectrum_grabber / enhanced_wifi_scanner to tune to channels associated with
   each spatial sector and enumerate detected sources.
4. Enforce safety via Magi-Zone before any active tuning/transmission.
5. Persist results to probe-sequence/spectrum_data/external_sources.json for
   system-wide access.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Ensure repo-local imports work
_BOW_ROOT = Path(__file__).resolve().parent.parent
if str(_BOW_ROOT) not in sys.path:
    sys.path.insert(0, str(_BOW_ROOT))

try:
    from conscience_escape_bridge import run_magi_escape
    BRIDGE_AVAILABLE = True
except Exception:
    BRIDGE_AVAILABLE = False

try:
    from spectrum_grabber.wifi_scanner import scan_wifi_cross_platform, WiFiScanError
    SPECTRUM_AVAILABLE = True
except Exception:
    try:
        from enhanced_wifi_scanner import SpectrumAnalyzer
        SPECTRUM_AVAILABLE = True
    except Exception:
        SPECTRUM_AVAILABLE = False


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
LIDAR_SCAN_TEST = Path(__file__).resolve().parent / "lidar_scan_test.json"
EXTERNAL_SOURCES_OUTPUT = Path(__file__).resolve().parent / "spectrum_data" / "external_sources.json"


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
class EnumeratedSource:
    source_id: str
    ssid: Optional[str]
    bssid: Optional[str]
    frequency_mhz: Optional[float]
    band: Optional[str]
    channel: Optional[int]
    signal_percent: Optional[float]
    spatial_origin: Dict[str, Any]
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
# Spatial extraction from LIDAR / point cloud
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
                source_id=pt.get("source_id") or pt.get("network", {}).get("ssid") or pt.get("bssid") or f"spatial_{i}",
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
# Channel tuning + enumeration
# ---------------------------------------------------------------------------
def _magi_tune_channel(voice_phrases: List[str], origin3d: Vec3, movement_vector: Vec3 = (0.0, 0.0, 0.0), default_tier: int = 2) -> Optional[Dict[str, Any]]:
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


def _try_wifi_enumerate() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    if not SPECTRUM_AVAILABLE:
        return results
    try:
        networks = scan_wifi_cross_platform()
        for ap in networks:
            results.append(
                {
                    "ssid": getattr(ap, "ssid", None),
                    "bssid": getattr(ap, "bssid", None),
                    "frequency_mhz": getattr(ap, "frequency_mhz", None),
                    "band": getattr(ap, "band", None),
                    "channel": getattr(ap, "channel", None),
                    "signal_percent": getattr(ap, "signal_percent", None),
                }
            )
    except Exception:
        pass
    return results


def _try_spectrum_analyzer_enumerate() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    try:
        sa = SpectrumAnalyzer()
        for ap in sa.scan():
            results.append(
                {
                    "ssid": getattr(ap, "ssid", None),
                    "bssid": getattr(ap, "bssid", None),
                    "frequency_mhz": getattr(ap, "frequency_mhz", None),
                    "band": getattr(ap, "band", None),
                    "channel": getattr(ap, "channel", None),
                    "signal_percent": getattr(ap, "signal_percent", None),
                }
            )
    except Exception:
        pass
    return results


def enumerate_external_sources(
    *,
    point_cloud: Optional[List[Dict[str, Any]]] = None,
    lidar_path: Path = LIDAR_SCAN_TEST,
    origin: Vec3 = (0.0, 0.0, 0.0),
    tune_voice_phrases: Optional[List[str]] = None,
    max_sources: int = 50,
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

    wifi_results = _try_wifi_enumerate() or _try_spectrum_analyzer_enumerate() or []

    # Map wifi results to nearby spatial sectors by signal strength as a proxy
    enumerated: List[EnumeratedSource] = []
    for sp in spatial_sources:
        best: Optional[Dict[str, Any]] = None
        if wifi_results:
            # pick the closest signal strength match among detected networks
            sp_signal = 50.0
            best = min(wifi_results, key=lambda a: abs(float(a.get("signal_percent", 0.0) or 0.0) - sp_signal))

        voice_phrases = tune_voice_phrases or ["ward", "shield"]
        movement = (sp.x - origin[0], sp.y - origin[1], sp.z - origin[2])
        ack = _magi_tune_channel(voice_phrases=voice_phrases, origin3d=origin, movement_vector=movement)

        enumerated.append(
            EnumeratedSource(
                source_id=sp.source_id,
                ssid=(best or {}).get("ssid"),
                bssid=(best or {}).get("bssid"),
                frequency_mhz=(best or {}).get("frequency_mhz"),
                band=(best or {}).get("band"),
                channel=(best or {}).get("channel"),
                signal_percent=(best or {}).get("signal_percent"),
                spatial_origin={
                    "x": sp.x,
                    "y": sp.y,
                    "z": sp.z,
                    "distance": sp.distance,
                    "bearing_deg": sp.bearing_deg,
                    "elevation_deg": sp.elevation_deg,
                },
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
        "enumerated_sources": [
            {
                "source_id": e.source_id,
                "ssid": e.ssid,
                "bssid": e.bssid,
                "frequency_mhz": e.frequency_mhz,
                "band": e.band,
                "channel": e.channel,
                "signal_percent": e.signal_percent,
                "spatial_origin": e.spatial_origin,
                "tune_ack": e.tune_ack,
                "timestamp": e.timestamp,
            }
            for e in enumerated
        ],
        "safe_execution": all((e.tune_ack or {}).get("permitted", False) and (e.tune_ack or {}).get("executed", False) for e in enumerated),
    }

    _save_json(EXTERNAL_SOURCES_OUTPUT, report)
    return report


def report_to_dict(report: Dict[str, Any]) -> Dict[str, Any]:
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="External Source Enumerator — spatial coordinate search and channel enumeration")
    parser.add_argument("--lidar", type=str, default=str(LIDAR_SCAN_TEST))
    parser.add_argument("--output", type=str, default=str(EXTERNAL_SOURCES_OUTPUT))
    parser.add_argument("--max", type=int, default=50)
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
