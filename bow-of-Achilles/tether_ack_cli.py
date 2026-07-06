"""tether_ack_cli.py

Minimal verification harness for Magi-Zone "tether/escape" execution.

It DOES NOT depend on the Python consciousness loop modules (which currently
fail to import in this environment). Instead it:
  1) calls alive-eal/magi-zone/run_escape_pipeline.js via conscience_escape_bridge
  2) validates JSON and key fields (executed/permitted)
  3) writes an audit record to data/mana_ciel/stack/tether_ack.json

Usage:
  python tether_ack_cli.py --voice "manifest shield" --voice "ward"

"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from conscience_escape_bridge import run_magi_escape


def _stack_dir() -> Path:
    return Path(__file__).resolve().parent / "data" / "mana_ciel" / "stack"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Magi-Zone escape/tether pipeline and write an audit ack.")
    parser.add_argument(
        "--voice",
        action="append",
        default=[],
        help="Voice phrase to pass to the escape pipeline (repeatable).",
    )
    parser.add_argument("--tier", type=int, default=2, help="Default tier to request.")
    parser.add_argument(
        "--origin",
        type=float,
        nargs=3,
        default=(0.0, 0.0, 0.0),
        metavar=("X", "Y", "Z"),
        help="Origin3D coordinates.",
    )
    parser.add_argument(
        "--move",
        type=float,
        nargs=3,
        default=(0.0, 0.0, 0.0),
        metavar=("VX", "VY", "VZ"),
        help="Movement vector.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout seconds for JS runner.",
    )

    args = parser.parse_args()

    voice_phrases = args.voice or ["manifest shield", "ward"]

    payload = run_magi_escape(
        voice_phrases=voice_phrases,
        origin3d=(float(args.origin[0]), float(args.origin[1]), float(args.origin[2])),
        movement_vector=(float(args.move[0]), float(args.move[1]), float(args.move[2])),
        in_danger=True,
        default_tier=int(args.tier),
        timeout_s=int(args.timeout),
    )

    ack = {
        "timestamp": time.time(),
        "executed": payload.executed,
        "permitted": payload.permitted,
        "tier": payload.tier,
        "enforceResult": payload.enforceResult,
        "waveState": payload.waveState,
        "upscale": payload.upscale,
        "zoneMap3D": payload.zoneMap3D,
        "voice_phrases": voice_phrases,
        "origin3d": list(args.origin),
        "movementVector": list(args.move),
    }

    out_path = _stack_dir() / "tether_ack.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(ack, indent=2, default=str), encoding="utf-8")

    print(json.dumps(ack, indent=2, default=str))

    # simple validity check
    if payload.executed is True:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

