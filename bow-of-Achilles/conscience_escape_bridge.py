"""Bridge utilities for triggering Magi-Zone escape/merge pipeline from the
Python consciousness loop.

This module shells out to:
  alive-eal/magi-zone/run_escape_pipeline.js

It expects the JS runner to output JSON to stdout.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class EscapePayload:
    waveState: Optional[Dict[str, Any]] = None
    upscale: Optional[Dict[str, Any]] = None
    enforceResult: Optional[Dict[str, Any]] = None
    zoneMap3D: Optional[Dict[str, Any]] = None
    tier: Optional[int] = None
    permitted: Optional[bool] = None
    executed: Optional[bool] = None


def _project_root() -> Path:
    # bow-of-Achilles/ -> repo root
    return Path(__file__).resolve().parent.parent


def run_magi_escape(
    *,
    voice_phrases: List[str],
    origin3d: Tuple[float, float, float],
    movement_vector: Tuple[float, float, float],
    in_danger: bool = True,
    default_tier: int = 2,
    timeout_s: int = 60,
) -> EscapePayload:
    root = _project_root()
    runner = root / "alive-eal" / "magi-zone" / "run_escape_pipeline.js"

    voice_json = json.dumps(voice_phrases, ensure_ascii=False)
    options = {
        "origin3D": [origin3d[0], origin3d[1], origin3d[2]],
        "movementVector": [movement_vector[0], movement_vector[1], movement_vector[2]],
        "inDanger": in_danger,
        "defaultTier": default_tier,
    }
    options_json = json.dumps(options, ensure_ascii=False)

    # Use node explicitly.
    cmd = [
        "node",
        str(runner),
        voice_json,
        options_json,
    ]

    proc = subprocess.run(
        cmd,
        cwd=str(runner.parent),
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"Magi escape bridge failed (code={proc.returncode}).\n"
            f"STDERR:\n{proc.stderr}\nSTDOUT:\n{proc.stdout}"
        )

    raw = proc.stdout.strip()
    if not raw:
        raise RuntimeError("Magi escape bridge produced empty stdout.")

    data = json.loads(raw)

    return EscapePayload(
        waveState=data.get("waveState"),
        upscale=data.get("upscale"),
        enforceResult=data.get("enforceResult"),
        zoneMap3D=data.get("zoneMap3D"),
        tier=data.get("tier"),
        permitted=data.get("permitted"),
        executed=data.get("executed"),
    )

