"""sec_topology_scheduler.py

SEC topology → scheduling factor adapter for bow-of-Achilles.

This module is intentionally defensive:
- If SEC is missing or bridge fails, it returns safe defaults.
- It never introduces unbounded delays; it uses a hard clamp.

Integration goal:
- Map SEC topology fields (or a proxy) into two outputs:
  1) a scheduling tier name (zone)
  2) a narrative scheduling override (q or delay scale)

The calling code should apply the schedule override to narrative_delay/q
(or to time.sleep equivalents).
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class SecSchedule:
    zone_name: str
    # narrative q override; 0 means baseline.
    q_override: int
    # multiplier applied to narrative_delay(q) when q is used.
    delay_scale: float


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def get_sec_topology_snapshot(sec_root: str, timeout_s: int = 10) -> Optional[Dict[str, Any]]:
    """Call SEC exchange bridge to get topology.

    Expected bridge script path (based on user repo structure):
      SEC-unit-core-sort/unified-consciousness-render/exchange-bridge.py

    Returns parsed JSON if possible.
    """
    bridge = os.path.join(
        sec_root,
        "unified-consciousness-render",
        "exchange-bridge.py",
    )

    if not os.path.exists(bridge):
        return None

    try:
        # Call: python exchange-bridge.py --topology
        proc = subprocess.run(
            [os.sys.executable, bridge, "--topology"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=os.path.dirname(bridge),
        )
        if proc.returncode != 0:
            return None

        # Try to parse stdout as json
        raw = (proc.stdout or "").strip()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None
    except Exception:
        return None


def topology_to_schedule(topology: Optional[Dict[str, Any]]) -> SecSchedule:
    """Convert topology snapshot into a safe scheduling factor.

    Since we don't have the exact SEC schema confirmed here, we extract
    a stable proxy:
    - If topology has numeric 'signal_strength'/'energy_per_tick'/'density'
      like fields, we derive q_override.

    Hard clamps:
    - q_override in [0..3]
    - delay_scale in [0.25..2.0]
    """

    zone_name = "zone_2_baseline"
    q_override = 0
    delay_scale = 1.0

    if not topology:
        return SecSchedule(zone_name=zone_name, q_override=q_override, delay_scale=delay_scale)

    # Collect possible proxies.
    proxies = []
    for k in ("q", "q_override", "energy_per_tick", "signal_strength", "density", "heat", "activation"):
        v = topology.get(k) if isinstance(topology, dict) else None
        if isinstance(v, (int, float)):
            proxies.append(float(v))

    # If topology contains nested lists, try first numeric field.
    if not proxies:
        # Look one level deep.
        for _, v in (topology.items() if isinstance(topology, dict) else []):
            if isinstance(v, dict):
                for kk in ("energy_per_tick", "density", "heat"):
                    vv = v.get(kk)
                    if isinstance(vv, (int, float)):
                        proxies.append(float(vv))
                        break
            if proxies:
                break

    proxy = proxies[0] if proxies else 0.0

    # Map proxy → q_override.
    # Higher proxy => higher q (faster). Keep within safe [0..3].
    # Use log scaling to tame extremes.
    try:
        import math

        proxy_abs = abs(proxy)
        if proxy_abs <= 0:
            q_override = 0
        else:
            q_override = int(_clamp(round(math.log10(proxy_abs + 1.0)), 0, 3))
    except Exception:
        q_override = 0

    # delay_scale: faster (q higher) reduces delay; inverse clamp.
    delay_scale = 1.0 / (1.0 + 0.5 * q_override)
    delay_scale = _clamp(delay_scale, 0.25, 2.0)

    # Zone naming: keep it human.
    if q_override <= 0:
        zone_name = "zone_0_baseline"
    elif q_override == 1:
        zone_name = "zone_1_slow_accel"
    elif q_override == 2:
        zone_name = "zone_2_medium_accel"
    else:
        zone_name = "zone_3_fast_accel_clamped"

    return SecSchedule(zone_name=zone_name, q_override=q_override, delay_scale=delay_scale)


def get_sec_schedule(sec_root: str, timeout_s: int = 10) -> SecSchedule:
    topology = get_sec_topology_snapshot(sec_root=sec_root, timeout_s=timeout_s)
    return topology_to_schedule(topology)

