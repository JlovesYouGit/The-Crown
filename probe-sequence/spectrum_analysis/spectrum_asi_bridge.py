"""spectrum_asi_bridge.py

Bridge adapter:
- loads probe-sequence/spectrum_data/raw_signal_observations.json
- maps observations -> SpectrumSeed objects (deterministic)
- calls CRISPR-ASI EnergyConcentrationSystem.intensify_routing_from_spectrum

This is intentionally standalone and uses synthetic molecule positions
by default (configurable).
"""

from __future__ import annotations

import json
import math
import os
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# CRISPR-ASI engine imports (path assumed repo-local)
_BOW_ROOT = Path(__file__).resolve().parents[2]
_ENGINE_ROOT = _BOW_ROOT / "CRISPR-ASI" / "ASI-"  # may or may not exist; kept for compatibility

try:
    # prefer growferslawoflife style path if present
    alt_root = _BOW_ROOT.parent / "growferslawoflife" / "CRISPR-ASI" / "ASI-"
    if alt_root.exists():
        import sys

        sys.path.insert(0, str(alt_root))
        sys.path.insert(0, str(alt_root.parent))

    from engine.core.energy_concentration import EnergyConcentrationSystem, SpectrumRange
    from engine.core.spectrum_routing import SpectrumRouter, SpectrumSeed
except Exception:
    EnergyConcentrationSystem = None
    SpectrumRange = None
    SpectrumSeed = None


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _deterministic_unit_direction(seed_key: str) -> np.ndarray:
    h = sha256_hex(seed_key)
    a = int(h[:8], 16) / 0xFFFFFFFF
    b = int(h[8:16], 16) / 0xFFFFFFFF

    theta = 2.0 * math.pi * a
    z = 2.0 * b - 1.0  # [-1,1]
    r = math.sqrt(max(0.0, 1.0 - z * z))

    return np.array([r * math.cos(theta), r * math.sin(theta), z], dtype=np.float64)


def _spectrum_range_from_wavelength(wavelength_m: float):
    # mirror SpectrumRange bounds in engine
    # fallback if SpectrumRange import fails
    if SpectrumRange is None:
        return "visible"
    for r in SpectrumRange:
        if r.wavelength_min <= wavelength_m < r.wavelength_max:
            return r
    return SpectrumRange.RADIO


def observations_to_seeds(
    *,
    report: Dict[str, Any],
    base_radius: float = 0.05,
    radius_scale: float = 0.15,
    strength_scale: float = 1.0,
) -> List["SpectrumSeed"]:
    if SpectrumSeed is None:
        raise RuntimeError("SpectrumSeed import failed; ensure CRISPR-ASI engine is on PYTHONPATH")

    origin = report.get("origin", [0.0, 0.0, 0.0])
    origin = np.array(origin, dtype=np.float64)

    observations = report.get("observations", [])

    seeds: List[SpectrumSeed] = []

    # Deterministic ordering so radius/angles are stable.
    observations_sorted = sorted(
        observations,
        key=lambda o: (float(o.get("frequency_mhz", 0.0)), str(o.get("source_id", ""))),
    )

    for idx, obs in enumerate(observations_sorted):
        source_id = str(obs.get("source_id", f"seed_{idx}"))
        f_mhz = float(obs.get("frequency_mhz", 0.0))
        wavelength_m = float(obs.get("wavelength_m", 1.0))
        snr_db = float(obs.get("snr_db", 0.0))
        lock_error_hz = float(obs.get("lock_error_hz", 0.0) or 0.0)

        # strength: use SNR (clamp) and penalize lock_error
        snr_pos = max(0.0, snr_db)
        lock_penalty = 1.0 / (1.0 + lock_error_hz / (abs(f_mhz) * 1e6 + 1e-9))
        strength = strength_scale * (snr_pos / (snr_pos + 10.0)) * lock_penalty

        # radius: “surrounding frequency determines size” + emission density proxy.
        # Map wavelength band to a stable multiplier.
        rs = _spectrum_range_from_wavelength(wavelength_m)
        band_mul = 1.0
        if SpectrumRange is not None and hasattr(rs, "name"):
            order = ["gamma", "xray", "ultraviolet", "visible", "infrared", "microwave", "radio"]
            try:
                band_mul = 0.6 + 0.1 * order.index(rs.name)
            except Exception:
                band_mul = 1.0

        # Direction: deterministic unit vector from (frequency, source_id)
        direction = _deterministic_unit_direction(f"{source_id}:{f_mhz}:{idx}")

        # Distance from origin: base + density proxy
        density_proxy = snr_pos / 30.0  # 0..~1
        radius = base_radius + band_mul * radius_scale * (0.2 + density_proxy)

        pos = origin + direction * radius

        seeds.append(SpectrumSeed(seed_id=source_id, pos=pos, strength=float(strength)))

    return seeds


def synthetic_molecule_positions(*, n: int = 120, origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> List[np.ndarray]:
    origin_np = np.array(origin, dtype=np.float64)

    rng = np.random.default_rng(1337)
    # cluster around origin (like a dense “condensation core”)
    r = rng.random(n) ** 2  # bias near 0
    angles1 = rng.random(n) * 2.0 * math.pi
    angles2 = np.arccos(2.0 * rng.random(n) - 1.0)

    x = r * np.sin(angles2) * np.cos(angles1)
    y = r * np.sin(angles2) * np.sin(angles1)
    z = r * np.cos(angles2)

    pts = np.stack([x, y, z], axis=1) * 0.5  # scale radius
    pts = pts + origin_np
    return [pts[i] for i in range(n)]


def run_bridge(
    *,
    raw_observations_path: Path,
    spectrum_range: Optional[Any] = None,
    top_seed_force: float = 1.0,
    top_seed_base_radius: float = 0.05,
    growth_rate: float = 0.02,
    energy_per_tick_scale: float = 1.0,
    synthetic_molecule_count: int = 120,
) -> Dict[str, Any]:
    if EnergyConcentrationSystem is None:
        raise RuntimeError("EnergyConcentrationSystem import failed")

    report = json.loads(raw_observations_path.read_text(encoding="utf-8"))

    seeds = observations_to_seeds(
        report=report,
        base_radius=top_seed_base_radius,
        radius_scale=0.15,
        strength_scale=top_seed_force,
    )

    # Choose a spectrum range from first observation (or user-provided)
    if spectrum_range is None:
        obs0 = report.get("observations", [{}])[0] if report.get("observations") else {}
        wl = float(obs0.get("wavelength_m", 1.0) or 1.0)
        spectrum_range = _spectrum_range_from_wavelength(wl)

    molecule_positions = synthetic_molecule_positions(origin=tuple(report.get("origin", [0, 0, 0])), n=synthetic_molecule_count)

    energy_system = EnergyConcentrationSystem(seed=None)
    # start components? We only need routing update (no thread)
    routing_snapshot = energy_system.intensify_routing_from_spectrum(
        seeds=seeds,
        molecule_positions=molecule_positions,
        spectrum_range=spectrum_range,
        seed_strength_scale=1.0,
        base_radius=top_seed_base_radius,
        growth_rate=growth_rate,
        energy_per_tick_scale=energy_per_tick_scale,
        topk_per_seed=4,
    )

    return {
        "loaded_at": time.time(),
        "raw_path": str(raw_observations_path),
        "num_seeds": len(seeds),
        "spectrum_range": getattr(spectrum_range, "name", str(spectrum_range)),
        "routing_snapshot": routing_snapshot,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Bridge raw spectrum observations into CRISPR-ASI routing")
    parser.add_argument("--raw", type=str, default=str(Path(__file__).resolve().parents[1] / "spectrum_data" / "raw_signal_observations.json"))
    parser.add_argument("--synthetic-molecules", type=int, default=120)
    parser.add_argument("--growth-rate", type=float, default=0.02)
    parser.add_argument("--energy-per-tick-scale", type=float, default=1.0)
    parser.add_argument("--seed-strength-force", type=float, default=1.0)
    args = parser.parse_args()

    raw_path = Path(args.raw)
    if not raw_path.exists():
        raise SystemExit(f"Missing raw observations: {raw_path}")

    out = run_bridge(
        raw_observations_path=raw_path,
        growth_rate=args.growth_rate,
        energy_per_tick_scale=args.energy_per_tick_scale,
        top_seed_force=args.seed_strength_force,
        synthetic_molecule_count=args.synthetic_molecules,
    )
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

