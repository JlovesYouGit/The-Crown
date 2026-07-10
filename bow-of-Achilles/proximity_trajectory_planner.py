"""proximity_trajectory_planner.py

Optimal, safety-constrained trajectory planner that uses the live celestial
routing layer to move the system's origin closer to a nearby planet capable
of supporting high-intelligence life (Mars, Jupiter, etc.).

Workflow:
1. Read current origin from earth_coverage_field.json (hotspot + escape vector).
2. Select target planet(s) by celestial coordinates.
3. Use CelestialRouter to compute great-circle hops toward the target.
4. Refine each hop through Magi-Zone safety policy via optimal_zone_pathing.
5. Output a JSON trajectory file for system access.

The resulting trajectory can be consumed by consciousness_loop.py or
zero_brain_overseer_coordinator.py to bias future iterations.
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

# Ensure growferslawoflife CRISPR-ASI engine is importable when this module
# is run directly from bow-of-Achilles without installing the package.
_ASI_ENGINE_ROOT = Path(__file__).resolve().parent.parent / "growferslawoflife" / "CRISPR-ASI" / "ASI-"
if str(_ASI_ENGINE_ROOT) not in sys.path:
    # Prepend so it takes precedence over any local `engine/` package shadow.
    sys.path.insert(0, str(_ASI_ENGINE_ROOT))

from conscience_escape_bridge import run_magi_escape
from optimal_zone_pathing import run_optimal_zone_pathing

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
EARTH_FIELD_PATH = Path(__file__).resolve().parent.parent / "bow-of-Achilles" / "probe-sequence" / "spectrum_data" / "earth_coverage_field.json"
TRAJECTORY_OUTPUT_PATH = Path(__file__).resolve().parent.parent / "bow-of-Achilles" / "probe-sequence" / "spectrum_data" / "trajectory_to_planet.json"

# ---------------------------------------------------------------------------
# Target planet catalog (approximate J2000 RA/Dec for Mars/Jupiter/Venus)
# ---------------------------------------------------------------------------
_PLANET_CATALOG: Dict[str, Dict[str, Any]] = {
    "mars": {
        "ra_hours": 2.6,
        "dec_deg": 15.0,
        "name": "Mars",
        "life_potential": 0.8,
        "intelligence_potential": 0.7,
    },
    "jupiter": {
        "ra_hours": 6.0,
        "dec_deg": -15.0,
        "name": "Jupiter",
        "life_potential": 0.5,
        "intelligence_potential": 0.4,
    },
    "venus": {
        "ra_hours": 3.5,
        "dec_deg": -20.0,
        "name": "Venus",
        "life_potential": 0.3,
        "intelligence_potential": 0.2,
    },
    "saturn": {
        "ra_hours": 4.5,
        "dec_deg": -15.0,
        "name": "Saturn",
        "life_potential": 0.4,
        "intelligence_potential": 0.3,
    },
}


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
# Coordinate helpers
# ---------------------------------------------------------------------------
Vec3 = Tuple[float, float, float]


def _norm(v: Vec3) -> float:
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a: Vec3, k: float) -> Vec3:
    return (a[0] * k, a[1] * k, a[2] * k)


def _unit(v: Vec3) -> Vec3:
    n = _norm(v)
    if n <= 1e-12:
        return (0.0, 1.0, 0.0)
    return (v[0] / n, v[1] / n, v[2] / n)


def _hours_to_radians(hours: float) -> float:
    return hours * (math.pi / 12.0)


def _deg_to_radians(deg: float) -> float:
    return math.radians(deg)


def _celestial_to_unit_vector(ra_hours: float, dec_deg: float) -> np.ndarray:
    ra = _hours_to_radians(ra_hours)
    dec = _deg_to_radians(dec_deg)
    x = math.cos(dec) * math.cos(ra)
    y = math.cos(dec) * math.sin(ra)
    z = math.sin(dec)
    return np.array([x, y, z], dtype=np.float64)


# ---------------------------------------------------------------------------
# Origin derivation from earth_coverage_field.json
# ---------------------------------------------------------------------------
def _derive_origin_from_earth_field(earth_field: Optional[Dict[str, Any]] = None) -> Tuple[Vec3, Vec3]:
    """Return (origin3d, escape_movement) from the Earth coverage field.

    Falls back to a conservative in-system origin if no field is available.
    """
    field = earth_field or _read_json(EARTH_FIELD_PATH, {}) or {}
    hotspot = field.get("hotspot") or {}
    escape = field.get("escape_vector") or {}

    hotspot_lat = float(hotspot.get("lat_deg", 0.0) or 0.0)
    hotspot_lon = float(hotspot.get("lon_deg", 0.0) or 0.0)
    escape_lat = float(escape.get("lat_deg", 0.0) or 0.0)
    escape_lon = float(escape.get("lon_deg", 0.0) or 0.0)

    radius = 6371.0
    phi_h = math.radians(90.0 - hotspot_lat)
    theta_h = math.radians(hotspot_lon + 180.0)
    origin = (
        radius * math.sin(phi_h) * math.cos(theta_h),
        radius * math.sin(phi_h) * math.sin(theta_h),
        radius * math.cos(phi_h),
    )

    phi_e = math.radians(90.0 - escape_lat)
    theta_e = math.radians(escape_lon + 180.0)
    escape_vec = (
        radius * math.sin(phi_e) * math.cos(theta_e),
        radius * math.sin(phi_e) * math.sin(theta_e),
        radius * math.cos(phi_e),
    )
    movement = _sub(escape_vec, origin)
    return origin, movement


def _select_best_target(target_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """Select the highest-life-potential target within the candidate list."""
    names = target_names or list(_PLANET_CATALOG.keys())
    best = max(
        (p for p in [_PLANET_CATALOG[n] for n in names if n in _PLANET_CATALOG]),
        key=lambda p: p.get("life_potential", 0.0) + p.get("intelligence_potential", 0.0),
    )
    return best


# ---------------------------------------------------------------------------
# Celestial trajectory computation
# ---------------------------------------------------------------------------
def compute_celestial_trajectory(
    *,
    origin: Vec3,
    target_ra_hours: float,
    target_dec_deg: float,
    num_hops: int = 8,
    celestial_radius_km: float = 6_371.0,
) -> List[Dict[str, Any]]:
    """Compute a sequence of celestial great-circle hops from origin toward target.

    Uses importlib to load the growferslawoflife CRISPR-ASI engine modules
    directly, bypassing any local `engine` package shadow in bow-of-Achilles.
    """
    try:
        import importlib.util
        import types

        _ASI_ENGINE_ROOT = Path(__file__).resolve().parent.parent / "growferslawoflife" / "CRISPR-ASI" / "ASI-"

        def _load_from_file(module_name: str, rel_path: str):
            full_path = str(_ASI_ENGINE_ROOT / rel_path)
            spec = importlib.util.spec_from_file_location(
                module_name,
                full_path,
                submodule_search_locations=[],
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            if spec.loader is None:
                raise ImportError(f"no loader for {full_path}")
            spec.loader.exec_module(mod)
            return mod

        # Remove any cached local `engine` packages so Python re-resolves from
        # sys.path, where _ASI_ENGINE_ROOT is the authoritative source.
        for _mod in list(sys.modules.keys()):
            if _mod == "engine" or _mod.startswith("engine."):
                del sys.modules[_mod]

        # Load spectrum_routing and register it under the standard module name
        # that celestial_routing expects: engine.core.spectrum_routing
        spectrum_routing = _load_from_file(
            "engine.core.spectrum_routing",
            "engine/core/spectrum_routing.py",
        )
        celestial_routing = _load_from_file(
            "engine.core.celestial_routing",
            "engine/core/celestial_routing.py",
        )
        CelestialRouter = celestial_routing.CelestialRouter
        SpectrumSeed = spectrum_routing.SpectrumSeed
    except Exception:
        return []

    router = CelestialRouter(celestial_radius_km=celestial_radius_km)
    target_dir = _celestial_to_unit_vector(target_ra_hours, target_dec_deg)

    seeds = [SpectrumSeed(seed_id="proximity_seed", pos=np.array(origin, dtype=np.float64), strength=1.0)]

    mol_positions: List[np.ndarray] = []
    for step in range(1, num_hops + 1):
        scale = 1.0 + 0.5 * step
        mol_positions.append(np.array(origin, dtype=np.float64) + target_dir * scale)

    try:
        snap = router.route_celestial(
            seeds=seeds,
            molecule_positions=mol_positions,
            spectrum_range_name="proximity_trajectory",
            top_anchors=3,
            topk_per_seed=num_hops,
        )
    except Exception:
        return []

    hops = snap.get("hops", [])
    trajectory: List[Dict[str, Any]] = []
    for hop in hops:
        ra = float(hop.get("target_ra_rad", 0.0) or 0.0)
        dec = float(hop.get("target_dec_rad", 0.0) or 0.0)
        x = math.cos(dec) * math.cos(ra) * celestial_radius_km
        y = math.cos(dec) * math.sin(ra) * celestial_radius_km
        z = math.sin(dec) * celestial_radius_km
        trajectory.append(
            {
                "hop_id": hop.get("hop_id"),
                "origin_ra_rad": hop.get("origin_ra_rad"),
                "origin_dec_rad": hop.get("origin_dec_rad"),
                "target_ra_rad": ra,
                "target_dec_rad": dec,
                "position_xyz": [x, y, z],
                "arc_length_km": hop.get("arc_length_km"),
                "angular_distance_rad": hop.get("angular_distance_rad"),
                "energy_per_tick": hop.get("energy_per_tick"),
                "anchor_id": hop.get("anchor_id"),
            }
        )
    return trajectory


# ---------------------------------------------------------------------------
# Optimal pathing toward target planet
# ---------------------------------------------------------------------------
def plan_trajectory_to_planet(
    *,
    target_planet: str = "mars",
    voice_phrases: Optional[List[str]] = None,
    steps: int = 6,
    candidates_per_step: int = 8,
    radius: float = 10.0,
    timeout_s: int = 60,
    default_tier: int = 2,
    target_names: Optional[List[str]] = None,
    earth_field: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Plan an optimal, safety-checked trajectory toward the target planet."""
    started = time.time()

    origin, escape_movement = _derive_origin_from_earth_field(earth_field)
    planet = _PLANET_CATALOG.get(target_planet.lower()) or _select_best_target(target_names)
    target_name = planet.get("name", target_planet)
    ra_hours = float(planet.get("ra_hours", 0.0) or 0.0)
    dec_deg = float(planet.get("dec_deg", 0.0) or 0.0)

    celestial_trajectory = compute_celestial_trajectory(
        origin=origin,
        target_ra_hours=ra_hours,
        target_dec_deg=dec_deg,
        num_hops=max(steps, 4),
        celestial_radius_km=6371.0,
    )

    phrases = voice_phrases or ["ward", "shield", "manifest"]
    magi_result = run_optimal_zone_pathing(
        voice_phrases=phrases,
        start_origin3d=origin,
        steps=steps,
        candidates_per_step=candidates_per_step,
        radius=radius,
        seed=1337,
        timeout_s=timeout_s,
        default_tier=default_tier,
    )

    # Proximity metric: approximate closeness via angular delta
    target_dir = _celestial_to_unit_vector(ra_hours, dec_deg)
    origin_dir = _unit(origin)
    dot = float(np.clip(float(np.dot(target_dir, origin_dir)), -1.0, 1.0))
    angular_sep_rad = math.acos(dot)
    approx_distance_km = angular_sep_rad * 6371.0

    report = {
        "started_at": started,
        "finished_at": time.time(),
        "origin": {
            "source": "earth_coverage_field",
            "origin3d": list(origin),
            "escape_movement": list(escape_movement),
        },
        "target_planet": {
            "key": target_planet.lower(),
            "name": target_name,
            "ra_hours": ra_hours,
            "dec_deg": dec_deg,
            "life_potential": planet.get("life_potential"),
            "intelligence_potential": planet.get("intelligence_potential"),
            "approximate_distance_km": round(approx_distance_km, 3),
            "angular_separation_rad": round(angular_sep_rad, 6),
        },
        "celestial_trajectory": celestial_trajectory,
        "magi_zone_pathing": magi_result,
        "safe_execution": all(
            step.get("ack_executed") and step.get("ack_permitted")
            for step in magi_result.get("path", [])
        ),
    }

    _save_json(TRAJECTORY_OUTPUT_PATH, report)
    return report


def report_to_dict(report: Dict[str, Any]) -> Dict[str, Any]:
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Proximity Trajectory Planner — planet approach via celestial routing")
    parser.add_argument("--planet", type=str, default="mars")
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--radius", type=float, default=10.0)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--tier", type=int, default=2)
    parser.add_argument("--voice", action="append", default=[])
    parser.add_argument("--output", type=str, default=str(TRAJECTORY_OUTPUT_PATH))
    args = parser.parse_args()

    out_path = Path(args.output)
    report = plan_trajectory_to_planet(
        target_planet=args.planet,
        voice_phrases=args.voice or ["ward", "shield", "manifest"],
        steps=args.steps,
        radius=args.radius,
        timeout_s=args.timeout,
        default_tier=args.tier,
    )
    _save_json(out_path, report)
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
