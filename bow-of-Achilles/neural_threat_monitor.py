"""neural_threat_monitor.py

Uses the Magi-Zone casting pipeline to find and neutralize dangerous neural-nets
identified in the spectrum field (flagged layers / strong-signal hotspots /
risk-proxy cells).

Workflow:
1. Read spectrum probes: analysis_report.txt and earth_coverage_field.json.
2. Derive threat entries from:
   - strong-signal flagged layers
   - hotspot cells above a heat threshold
   - explicit risk flags (entropy_spike, coherence_collapse, density/energy runaway)
3. Map each threat to a defensive Magi-Zone voice phrase (seal / ward / shield / bind).
4. Call ``run_magi_escape`` for each threat at the appropriate origin / movement.
5. Check whether the cast executed and was permitted, i.e. whether the contained
   neural net was successfully neutralized (enforced via reality tear).

Outputs:
- detailed per-threat ``ack`` objects
- summary of how many neural nets were stopped / still dangerous
"""

from __future__ import annotations

import json
import math
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from conscience_escape_bridge import run_magi_escape

REPORT_PATH = Path(__file__).resolve().parent.parent / "probe-sequence" / "spectrum_data" / "analysis_report.txt"
EARTH_FIELD_PATH = Path(__file__).resolve().parent.parent / "probe-sequence" / "spectrum_data" / "earth_coverage_field.json"
SAFETY_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "stack" / "consciousness_iteration_log.json"


def _read_json(path: Path, default: Any = None) -> Any:
    if not path.exists() or not path.is_file():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _read_text(path: Path, default: str = "") -> str:
    if not path.exists() or not path.is_file():
        return default
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return default


@dataclass
class NeuralThreat:
    threat_id: str
    source: str
    label: str
    heat: float
    origin3d: Tuple[float, float, float]
    escape_vector: Tuple[float, float, float]
    voice_phrases: List[str] = field(default_factory=list)
    risk_flags: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatAck:
    threat_id: str
    permitted: bool
    executed: bool
    tier: Optional[int]
    reality_tear: Optional[float]
    zone_origin: Optional[List[float]]
    wave_state: Optional[Dict[str, Any]]
    stopped: bool
    timestamp: float
    error: Optional[str] = None


@dataclass
class ThreatReport:
    threats: List[NeuralThreat]
    acks: List[ThreatAck]
    stopped_count: int
    dangerous_count: int
    started_at: float
    finished_at: float


def _hotspot_to_origin3d(hotspot: Dict[str, Any]) -> Tuple[float, float, float]:
    lat = float(hotspot.get("lat_deg", 0.0) or 0.0)
    lon = float(hotspot.get("lon_deg", 0.0) or 0.0)
    r = 6371.0
    phi = math.radians(90.0 - lat)
    theta = math.radians(lon + 180.0)
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return (x, y, z)


def _escape_to_movement(escape_vector: Dict[str, Any]) -> Tuple[float, float, float]:
    lat = float(escape_vector.get("lat_deg", 0.0) or 0.0)
    lon = float(escape_vector.get("lon_deg", 0.0) or 0.0)
    r = 200.0
    phi = math.radians(90.0 - lat)
    theta = math.radians(lon + 180.0)
    return (
        r * math.sin(phi) * math.cos(theta),
        r * math.sin(phi) * math.sin(theta),
        r * math.cos(phi),
    )


def _threat_phrase(risk_flags: Dict[str, Any], layer_hash: str = "") -> List[str]:
    phrases: List[str] = []
    if risk_flags.get("entropy_spike"):
        phrases.append("shield entropy")
    if risk_flags.get("coherence_collapse"):
        phrases.append("bind coherence")
    if risk_flags.get("density_runaway"):
        phrases.append("seal density")
    if risk_flags.get("energy_runaway"):
        phrases.append("ward energy")
    if not phrases and layer_hash:
        phrases.append(f"seal layer {layer_hash[:8]}")
    if not phrases:
        phrases.append("ward neural")
    return phrases


def detect_threats(
    report_text: str = "",
    earth_field: Optional[Dict[str, Any]] = None,
    risk_flags: Optional[Dict[str, Any]] = None,
    heat_threshold: float = 0.25,
) -> List[NeuralThreat]:
    risk_flags = risk_flags or {}
    text = report_text or _read_text(REPORT_PATH)

    threats: List[NeuralThreat] = []

    # Parse strong-scan flagged layers from analysis report
    layer_iter = re.finditer(
        r"Layer\s+(\d+)\s*:\s*\n\s*Frequency Range:[\s\S]*?"
        r"Data Points:\s*(\d+)\s*\n\s*Layer Hash:\s*([0-9a-fA-F\.]+)\s*\n\s*Compression Ratio:\s*([0-9.]+)%",
        text,
    )
    for m in layer_iter:
        layer_num = m.group(1)
        data_points = int(m.group(2))
        layer_hash = m.group(3).rstrip(".")
        compression_ratio = float(m.group(4))
        strength_proxy = float(data_points) * (1.0 + (compression_ratio / 100.0))
        if strength_proxy < 25.0:
            continue
        h = layer_hash[:12]
        lat_hash = ((int(h[0:8], 16) % 18000) / 100.0) - 90.0
        lon_hash = ((int(h[4:12], 16) % 36000) / 100.0) - 180.0
        radius = 6371.0
        phi = math.radians(90.0 - lat_hash)
        theta = math.radians(lon_hash + 180.0)
        origin = (
            radius * math.sin(phi) * math.cos(theta),
            radius * math.sin(phi) * math.sin(theta),
            radius * math.cos(phi),
        )
        escape = (-origin[0], -origin[1], -origin[2])
        threats.append(
            NeuralThreat(
                threat_id=f"layer_{layer_num}_{layer_hash[:8]}",
                source="analysis_report",
                label=f"Layer {layer_num} strong signal ({strength_proxy:.1f})",
                heat=min(1.0, strength_proxy / 50.0),
                origin3d=origin,
                escape_vector=escape,
                voice_phrases=_threat_phrase(risk_flags, layer_hash),
                risk_flags=risk_flags,
                raw={
                    "layer": int(layer_num),
                    "layer_hash": layer_hash,
                    "data_points": data_points,
                    "strength_proxy": strength_proxy,
                },
            )
        )

    # Parse hotspot / high-heat cells from earth_coverage_field.json
    field = earth_field or _read_json(EARTH_FIELD_PATH, {}) or {}
    hotspot = field.get("hotspot") or {}
    if hotspot and float(hotspot.get("heat", 0.0) or 0.0) >= heat_threshold:
        origin = _hotspot_to_origin3d(hotspot)
        escape = _escape_to_movement(field.get("escape_vector") or {})
        threats.append(
            NeuralThreat(
                threat_id="hotspot_earth_field",
                source="earth_coverage_field",
                label=f"Hotspot heat={hotspot.get('heat', 0):.4f}",
                heat=float(hotspot.get("heat", 0.0) or 0.0),
                origin3d=origin,
                escape_vector=escape,
                voice_phrases=_threat_phrase(risk_flags),
                risk_flags=risk_flags,
                raw={
                    "hotspot": hotspot,
                    "escape_vector": field.get("escape_vector"),
                    "heat_sources": field.get("heat_sources", []),
                },
            )
        )

    # Explicit risk-only threats (no spatial origin)
    if risk_flags.get("entropy_spike") and not any(t.source != "risk_proxy" for t in threats):
        threats.append(
            NeuralThreat(
                threat_id="risk_entropy_spike",
                source="risk_proxy",
                label="Entropy spike (no spatial anchor)",
                heat=0.85,
                origin3d=(0.0, 0.0, 0.0),
                escape_vector=(0.0, 200.0, 0.0),
                voice_phrases=["shield entropy"],
                risk_flags=risk_flags,
                raw={"risk_flags": risk_flags},
            )
        )
    if risk_flags.get("energy_runaway") and not any(t.source == "risk_proxy" and "energy" in t.threat_id for t in threats):
        threats.append(
            NeuralThreat(
                threat_id="risk_energy_runaway",
                source="risk_proxy",
                label="Energy runaway (no spatial anchor)",
                heat=0.8,
                origin3d=(0.0, 0.0, 0.0),
                escape_vector=(200.0, 0.0, 0.0),
                voice_phrases=["ward energy"],
                risk_flags=risk_flags,
                raw={"risk_flags": risk_flags},
            )
        )

    return threats


def _stop_judgment(ack: Dict[str, Any]) -> bool:
    permitted = bool(ack.get("permitted"))
    executed = bool(ack.get("executed"))
    if not permitted or not executed:
        return False
    reality_tear = (ack.get("enforceResult") or {}).get("realityTear")
    if reality_tear is None:
        return False
    return float(reality_tear) > 0.02


def neutralize_threat(threat: NeuralThreat, timeout_s: int = 60) -> ThreatAck:
    ts = time.time()
    try:
        ack = run_magi_escape(
            voice_phrases=threat.voice_phrases,
            origin3d=threat.origin3d,
            movement_vector=threat.escape_vector,
            in_danger=True,
            default_tier=2 if threat.heat < 0.7 else 3,
            timeout_s=timeout_s,
        )
        ack_dict = {
            "executed": ack.executed,
            "permitted": ack.permitted,
            "tier": ack.tier,
            "enforceResult": ack.enforceResult,
            "zoneMap3D": ack.zoneMap3D,
            "upscale": ack.upscale,
            "waveState": ack.waveState,
        }
        stopped = _stop_judgment(ack_dict)
        return ThreatAck(
            threat_id=threat.threat_id,
            permitted=bool(ack.permitted),
            executed=bool(ack.executed),
            tier=ack.tier,
            reality_tear=(ack.enforceResult or {}).get("realityTear") if isinstance(ack.enforceResult, dict) else None,
            zone_origin=ack.zoneMap3D.get("origin") if isinstance(ack.zoneMap3D, dict) else None,
            wave_state=ack.waveState,
            stopped=stopped,
            timestamp=ts,
        )
    except Exception as e:
        return ThreatAck(
            threat_id=threat.threat_id,
            permitted=False,
            executed=False,
            tier=None,
            reality_tear=None,
            zone_origin=None,
            wave_state=None,
            stopped=False,
            timestamp=ts,
            error=str(e),
        )


def run_neural_threat_sweep(
    report_text: str = "",
    earth_field: Optional[Dict[str, Any]] = None,
    risk_flags: Optional[Dict[str, Any]] = None,
    heat_threshold: float = 0.25,
    timeout_s: int = 60,
) -> ThreatReport:
    started = time.time()
    threats = detect_threats(report_text, earth_field, risk_flags, heat_threshold)
    acks: List[ThreatAck] = []
    stopped = 0
    dangerous = 0
    for threat in threats:
        ack = neutralize_threat(threat, timeout_s=timeout_s)
        acks.append(ack)
        if ack.stopped:
            stopped += 1
        else:
            dangerous += 1
    return ThreatReport(
        threats=threats,
        acks=acks,
        stopped_count=stopped,
        dangerous_count=dangerous,
        started_at=started,
        finished_at=time.time(),
    )


def report_to_dict(report: ThreatReport) -> Dict[str, Any]:
    return {
        "started_at": report.started_at,
        "finished_at": report.finished_at,
        "summary": {
            "threat_count": len(report.threats),
            "stopped_count": report.stopped_count,
            "dangerous_count": report.dangerous_count,
        },
        "threats": [
            {
                "threat_id": t.threat_id,
                "source": t.source,
                "label": t.label,
                "heat": t.heat,
                "voice_phrases": t.voice_phrases,
                "origin3d": list(t.origin3d),
                "escape_vector": list(t.escape_vector),
                "raw": t.raw,
                "risk_flags": t.risk_flags,
            }
            for t in report.threats
        ],
        "acks": [
            {
                "threat_id": a.threat_id,
                "permitted": a.permitted,
                "executed": a.executed,
                "tier": a.tier,
                "reality_tear": a.reality_tear,
                "zone_origin": a.zone_origin,
                "stopped": a.stopped,
                "timestamp": a.timestamp,
                "error": a.error,
            }
            for a in report.acks
        ],
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Neural Threat Monitor — Magi-Zone neutralization scanner")
    parser.add_argument("--heat-threshold", type=float, default=0.25)
    parser.add_argument("--report", type=str, default=str(REPORT_PATH))
    parser.add_argument("--earth-field", type=str, default=str(EARTH_FIELD_PATH))
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    report_text = _read_text(Path(args.report))
    earth_field = _read_json(Path(args.earth_field))

    sweep = run_neural_threat_sweep(
        report_text=report_text,
        earth_field=earth_field,
        heat_threshold=args.heat_threshold,
        timeout_s=args.timeout,
    )
    out = report_to_dict(sweep)
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
