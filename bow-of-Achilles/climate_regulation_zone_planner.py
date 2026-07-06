"""Climate regulation zone planner.

This converts a waypoint path (Vec3 coordinates) into discrete Earth-like
zones and attaches an intervention plan per zone.

Important: The repo does not contain a real physical climate model.
So the fields are computed as *proxies* derived from:
  - the spectral report text (analysis_report.txt)
  - Magi-Zone ack fields (enforceResult.realityTear, pattern ids)

Outputs are therefore deterministic *control directives* (not physical simulation).
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


Vec3 = Tuple[float, float, float]


def _norm(v: Vec3) -> float:
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def _hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _parse_spectrum_analysis_report(report_text: str) -> Dict[str, Any]:
    """Extract coarse metrics from analysis_report.txt.

    The report is human readable; we parse:
    - dimensional layers and their compression ratios
    - spatial point count

    We then create normalized proxy scalars.
    """
    layers = {}
    for m in re.finditer(r"Layer\s+(\d+):\s+\n\s+Frequency Range:.*?\n\s+Data Points:\s+(\d+)\s+\n\s+Layer Hash:.*?\n\s+Compression Ratio:\s+([0-9.]+)%", report_text, re.S):
        li = int(m.group(1))
        dp = int(m.group(2))
        cr = float(m.group(3)) / 100.0
        layers[li] = {"data_points": dp, "compression_ratio": cr}

    spatial_points = 0
    sm = re.search(r"Total Spatial Points:\s+(\d+)", report_text)
    if sm:
        spatial_points = int(sm.group(1))

    if not layers:
        return {
            "layer_count": 0,
            "avg_compression_ratio": 0.0,
            "spatial_points": spatial_points,
        }

    avg_comp = sum(v["compression_ratio"] for v in layers.values()) / len(layers)
    return {
        "layer_count": len(layers),
        "avg_compression_ratio": avg_comp,
        "spatial_points": spatial_points,
        "layers": layers,
    }


def load_spectrum_report(report_path: str) -> Dict[str, Any]:
    p = Path(report_path)
    text = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
    return _parse_spectrum_analysis_report(text)


def waypoint_to_zone_id(waypoint: Vec3) -> str:
    """Map Vec3 to a stable zone id using quantization of vector direction + magnitude."""
    x, y, z = waypoint
    mag = _norm(waypoint)

    # Quantize "latitude" proxy in [-90, 90]
    # Using y component for proxy.
    lat_proxy = 90.0 * (y / (mag + 1e-9))
    lat_bin = int(math.floor((lat_proxy + 90.0) / 5.0))  # 5° bins

    # Quantize "biome" proxy using sign/magnitude hash
    h = int(_hash_text(f"{x:.3f}|{y:.3f}|{z:.3f}")[:8], 16)
    biome_idx = h % 20

    return f"zone_{lat_bin:03d}_b{biome_idx:02d}"


@dataclass
class ZoneClimatePlan:
    zone_id: str
    intervention_type: str
    intervention_intensity: float  # 0..100
    target_temp_range_c: Tuple[float, float]
    current_temp_c: float
    altitude_layer: str
    teleconnection_risk: str
    ecosystem_tolerance: float
    ecosystem_tolerance_change_per_decade_c: float
    zone_impact: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "intervention_type": self.intervention_type,
            "intervention_intensity": self.intervention_intensity,
            "target_temp_range_c": [self.target_temp_range_c[0], self.target_temp_range_c[1]],
            "current_temp_c": self.current_temp_c,
            "altitude_layer": self.altitude_layer,
            "teleconnection_risk": self.teleconnection_risk,
            "ecosystem_tolerance": self.ecosystem_tolerance,
            "ecosystem_tolerance_change_per_decade_c": self.ecosystem_tolerance_change_per_decade_c,
            "zone_impact": self.zone_impact,
        }


def choose_intervention_type(zone_hash_int: int) -> str:
    types = [
        "SRM",
        "afforestation",
        "albedo",
        "ocean",
    ]
    return types[zone_hash_int % len(types)]


def zone_climate_plan(
    *,
    zone_id: str,
    waypoint: Vec3,
    ack: Dict[str, Any],
    spectrum_metrics: Dict[str, Any],
) -> ZoneClimatePlan:
    """Create a deterministic proxy intervention plan for a zone."""
    h = int(_hash_text(zone_id)[:10], 16)

    # realityTear proxy safety steering
    enforce = ack.get("enforceResult") or {}
    reality_tear = enforce.get("realityTear")
    if reality_tear is None:
        reality_tear = 0.5

    tear_norm = _clamp01(float(reality_tear) / 2.0)  # assume worst ~2.0

    # Spectrum-derived influence
    avg_comp = float(spectrum_metrics.get("avg_compression_ratio", 0.0))

    # Current temp proxy in °C
    mag = _norm(waypoint)
    mag_norm = _clamp01((mag % 1000.0) / 1000.0)

    current_temp = 10.0 + 20.0 * (0.3 * mag_norm + 0.7 * (1.0 - tear_norm))

    # Target range narrows as safety improves (lower tear)
    width = 2.0 + 3.0 * tear_norm
    target_min = current_temp - width
    target_max = current_temp + width * 0.7

    # Intensity: higher when tear is low and spectrum comp suggests stronger modulation
    intensity = 100.0 * _clamp01((1.0 - tear_norm) * (0.4 + 0.6 * avg_comp))

    # Altitude layer based on intensity
    if intensity > 70:
        altitude = "10-15km stratosphere"
    elif intensity > 40:
        altitude = "surface"
    else:
        altitude = "surface (low-tune)"

    risk_val = 1.0 - (1.0 - tear_norm) * 0.8
    if risk_val < 0.33:
        risk = "low"
    elif risk_val < 0.66:
        risk = "med"
    else:
        risk = "high"

    tol = _clamp01(1.0 - risk_val * 0.9)
    tol_change = 0.5 + 2.0 * tol  # °C/decade (proxy)

    intervention_type = choose_intervention_type(h)

    return ZoneClimatePlan(
        zone_id=zone_id,
        intervention_type=intervention_type,
        intervention_intensity=float(intensity),
        target_temp_range_c=(float(target_min), float(target_max)),
        current_temp_c=float(current_temp),
        altitude_layer=altitude,
        teleconnection_risk=risk,
        ecosystem_tolerance=float(tol),
        ecosystem_tolerance_change_per_decade_c=float(tol_change),
        zone_impact={
            "target_zone_id": zone_id,
            "realityTear": float(reality_tear),
            "spectrum_avg_compression_ratio": float(avg_comp),
        },
    )


def plan_climate_for_path(
    *,
    path_steps: List[Dict[str, Any]],
    spectrum_report_path: str,
    default_zone_count: int = 1,
) -> Dict[str, Any]:
    """Plan climate interventions for zones around each path target.

    By default: one zone per step (derived from chosen_target).
    """
    spectrum_metrics = load_spectrum_report(spectrum_report_path)

    zones: List[Dict[str, Any]] = []
    for si, step in enumerate(path_steps):
        target = step.get("chosen_target")
        if not isinstance(target, list) or len(target) != 3:
            continue

        waypoint = (float(target[0]), float(target[1]), float(target[2]))

        # ack is stored in the step only as deltas; we use the step’s ack_executed/permitted
        # and we expect enforceResult to be embedded under step in next iteration.
        # For now, we use a conservative ack envelope.
        ack_env = step.get("best_ack") or {
            "enforceResult": {"realityTear": 0.5},
        }

        zone_id = waypoint_to_zone_id(waypoint)

        plan = zone_climate_plan(
            zone_id=zone_id,
            waypoint=waypoint,
            ack=ack_env,
            spectrum_metrics=spectrum_metrics,
        )
        zones.append({"step_index": si, **plan.to_dict()})

    return {
        "spectrum_metrics": spectrum_metrics,
        "zones": zones,
        "zone_count": len(zones),
    }

