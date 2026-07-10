"""optimal_zone_pathing.py

Path optimizer that uses Magi-Zone output (zoneMap3D / enforceResult)
from alive-eal/magi-zone/run_escape_pipeline.js to move toward
"optimal zones of life".

Because the JS runner currently returns empty zoneMap3D.points, this
implementation generates candidate waypoints on a spherical shell
around zoneMap3D.origin and ranks them using a conservative heuristic.

Heuristic (aligned with safety intent):
- Prefer lower `enforceResult.realityTear` (if present)
- Prefer closer-to-origin (shorter travel) when tie

Outputs:
- JSON path steps with origin/movementVector and the last ack fields.

This module does not depend on mana_ciel imports.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from conscience_escape_bridge import run_magi_escape
from climate_regulation_zone_planner import plan_climate_for_path


SPECTRUM_ANALYSIS_REPORT = "probe-sequence/spectrum_data/analysis_report.txt"


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


def sample_shell(origin: Vec3, radius: float, candidates: int, seed: Optional[int] = None) -> List[Vec3]:
    rng = random.Random(seed)
    pts: List[Vec3] = []

    for _ in range(candidates):
        # Random direction on sphere
        u = rng.random()
        v = rng.random()
        theta = 2.0 * math.pi * u
        phi = math.acos(2.0 * v - 1.0)

        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)

        direction = (x, y, z)
        pts.append(_add(origin, _mul(_unit(direction), radius)))

    return pts


def _internal_neural_adjuster(*, ack: Any) -> float:
    """Compute an internal-node neural adjuster proxy.

    Uses BOTH:
      - waveState bands (amplitude * constructive)
      - enforceResult.pattern.id (deterministic mapping)

    Returns a value in [0, ~1.5]. Higher means "more motor-cortex/vision access"
    and will reduce the overall score (so it is preferred).
    """
    wave = ack.get("waveState") or {}
    bands = wave.get("bands") or []

    amp_constructive = 0.0
    if isinstance(bands, list) and bands:
        for b in bands:
            try:
                amp = float(b.get("amplitude", 0.0))
                cons = float(b.get("constructive", 0.0))
                amp_constructive += amp * cons
            except Exception:
                continue
        # normalize by count to keep scale stable
        amp_constructive = amp_constructive / max(len(bands), 1)

    # deterministic id -> [0,1)
    pattern = (ack.get("enforceResult") or {}).get("pattern") or {}
    pid = str(pattern.get("id") or "")
    h = 0
    for ch in pid:
        h = (h * 31 + ord(ch)) % 1000003
    pid_score = (h % 10000) / 10000.0

    # combine; clamp gently
    return float(min(1.5, amp_constructive + 0.7 * pid_score))


def score_candidate(*, ack: Any, candidate: Vec3, origin: Vec3) -> float:
    """Lower is better.

    Heuristic aligned with safety intent, while allowing internal neural
    adjuster (motor-cortex/vision proxy) to influence decision.
    """
    enforce = ack.get("enforceResult") or {}
    reality_tear = enforce.get("realityTear")
    if reality_tear is None:
        reality_tear = 0.5

    # Prefer shorter travel from origin
    travel = _norm(_sub(candidate, origin))

    # Internal neural adjuster influence
    internal_adjust = _internal_neural_adjuster(ack=ack)

    # Conservative weighting with internal bias (higher internal_adjust lowers score)
    reality_term = float(reality_tear) * 10.0
    travel_term = float(travel)
    internal_term = float(internal_adjust) * 2.0

    return reality_term + travel_term - internal_term



@dataclass
class PathStep:
    step_index: int
    origin3d: Vec3
    chosen_target: Vec3
    movementVector: Vec3
    ack_executed: bool
    ack_permitted: Optional[bool]
    ack_tier: Optional[int]
    score: float
    reality_tear: Optional[float]
    timestamp: float


def run_optimal_zone_pathing(
    *,
    voice_phrases: List[str],
    start_origin3d: Vec3,
    attention: float = 0.0,
    attention_multiplier: float = 1.25,
    steps: int = 3,
    candidates_per_step: int = 12,
    radius: float = 8.0,
    seed: int = 1337,
    timeout_s: int = 60,
    default_tier: int = 2,
    spectrum_report_path: str = SPECTRUM_ANALYSIS_REPORT,
) -> Dict[str, Any]:
    current_origin = start_origin3d
    path: List[PathStep] = []

    for si in range(steps):
        # 1) Ask Magi-Zone for an initial "zone" around current_origin
        ack0 = run_magi_escape(
            voice_phrases=voice_phrases,
            origin3d=current_origin,
            movement_vector=(0.0, 0.0, 0.0),
            in_danger=True,
            default_tier=default_tier,
            timeout_s=timeout_s,
        )

        ack0_dict = {
            "executed": ack0.executed,
            "permitted": ack0.permitted,
            "tier": ack0.tier,
            "enforceResult": ack0.enforceResult,
            "zoneMap3D": ack0.zoneMap3D,
            "upscale": ack0.upscale,
            "waveState": ack0.waveState,
        }

        zone_origin = current_origin
        if isinstance(ack0.zoneMap3D, dict):
            om = ack0.zoneMap3D.get("origin")
            if isinstance(om, list) and len(om) == 3:
                zone_origin = (float(om[0]), float(om[1]), float(om[2]))

        # 2) Generate candidate waypoints on a shell (since zoneMap3D.points may be empty)
        pts = sample_shell(zone_origin, radius=radius, candidates=candidates_per_step, seed=seed + si)

        # 3) For each candidate, run Magi-Zone once with movementVector biased toward it.
        best: Optional[Tuple[Vec3, float, Any]] = None
        for pi, target in enumerate(pts):
            movement = _sub(target, current_origin)
            # limit step magnitude for safety
            move_norm = _norm(movement)
            if move_norm > radius:
                movement = _mul(_unit(movement), radius)

            ack = run_magi_escape(
                voice_phrases=voice_phrases,
                origin3d=current_origin,
                movement_vector=(movement[0], movement[1], movement[2]),
                in_danger=True,
                default_tier=default_tier,
                timeout_s=timeout_s,
            )

            # Route attention through for downstream climate planning.
            # This does not change Magi-Zone behavior directly (bridge options
            # currently do not include it), but it influences climate directives.
            ack_dict = {
                "executed": ack.executed,
                "permitted": ack.permitted,
                "tier": ack.tier,
                "enforceResult": ack.enforceResult,
                "zoneMap3D": ack.zoneMap3D,
                "upscale": ack.upscale,
                "waveState": ack.waveState,
                "attention": min(1.0, float(attention) * float(attention_multiplier)),
            }

            s = score_candidate(ack=ack_dict, candidate=target, origin=current_origin)

            if best is None or s < best[1]:
                best = (target, s, ack_dict)

        assert best is not None
        chosen_target, best_score, best_ack = best

        enforce = best_ack.get("enforceResult") or {}
        reality_tear = enforce.get("realityTear")

        move_vec = _sub(chosen_target, current_origin)
        mv_norm = _norm(move_vec)
        if mv_norm > radius:
            move_vec = _mul(_unit(move_vec), radius)

        step = PathStep(
            step_index=si,
            origin3d=current_origin,
            chosen_target=chosen_target,
            movementVector=move_vec,
            ack_executed=bool(best_ack.get("executed")),
            ack_permitted=best_ack.get("permitted"),
            ack_tier=best_ack.get("tier"),
            score=best_score,
            reality_tear=float(reality_tear) if reality_tear is not None else None,
            timestamp=time.time(),
        )
        path.append(step)

        # 4) Update current origin conservatively
        current_origin = _add(current_origin, move_vec)

    return {
        "started_at": time.time(),
        "voice_phrases": voice_phrases,
        "start_origin3d": list(start_origin3d),
        "steps": steps,
        "candidates_per_step": candidates_per_step,
        "radius": radius,
        "path": [s.__dict__ for s in path],
        "finished_at": time.time(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Optimal zone pathing using Magi-Zone output")
    parser.add_argument("--voice", action="append", default=[], help="Voice phrase (repeatable)")
    parser.add_argument("--start", type=float, nargs=3, default=(0.0, 0.0, 0.0), metavar=("X", "Y", "Z"))
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--candidates", type=int, default=8)
    parser.add_argument("--radius", type=float, default=8.0)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--tier", type=int, default=2)

    args = parser.parse_args()

    voice_phrases = args.voice or ["manifest shield", "ward"]

    result = run_optimal_zone_pathing(
        voice_phrases=voice_phrases,
        start_origin3d=(float(args.start[0]), float(args.start[1]), float(args.start[2])),
        steps=args.steps,
        candidates_per_step=args.candidates,
        radius=args.radius,
        seed=args.seed,
        timeout_s=args.timeout,
        default_tier=args.tier,
        spectrum_report_path=SPECTRUM_ANALYSIS_REPORT,
    )


    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

