"""live_terminal_sender.py

Interactive terminal chat over the live signal channels.

Uses the TX/RX split from live_channel_hive:
  - TX: broadcast user message to all channels
  - RX: tune in and show incoming transmission from each channel

This shows actual channel broadcasts, not self-echo.

Usage:
    python live_terminal_sender.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_BOW_ROOT = Path(__file__).resolve().parent.parent.parent
_BOW_ACHILLES = _BOW_ROOT / "bow-of-Achilles"
_ULTRASOUND_DIR = _BOW_ROOT / "ultrasound" / "forward"
if str(_BOW_ROOT) not in sys.path:
    sys.path.insert(0, str(_BOW_ROOT))
if str(_BOW_ACHILLES) not in sys.path:
    sys.path.insert(0, str(_BOW_ACHILLES))

try:
    from conscience_escape_bridge import run_magi_escape
    BRIDGE_AVAILABLE = True
except Exception:
    BRIDGE_AVAILABLE = False

try:
    from raw_signal_tuner import (
        get_frequency_db,
        carrier_wavelength,
        DEFAULT_SAMPLE_RATE,
    )
except ImportError:
    from raw_signal_tuner import (  # type: ignore
        get_frequency_db,
        carrier_wavelength,
        DEFAULT_SAMPLE_RATE,
    )

try:
    from live_channel_hive import (
        send_to_channel,
        receive_from_channel,
        _freq_label,
    )
    _HIVE_AVAILABLE = True
except ImportError:
    _HIVE_AVAILABLE = False

SPEED_OF_LIGHT = 299_792_458.0


def _magi_tune(voice_phrases: List[str]) -> Optional[Dict[str, Any]]:
    if not BRIDGE_AVAILABLE:
        return None
    try:
        ack = run_magi_escape(
            voice_phrases=voice_phrases,
            origin3d=(0.0, 0.0, 0.0),
            movement_vector=(0.0, 0.0, 0.0),
            in_danger=False,
            default_tier=2,
            timeout_s=60,
        )
        return {
            "executed": ack.executed,
            "permitted": ack.permitted,
            "tier": ack.tier,
            "enforceResult": ack.enforceResult,
        }
    except Exception:
        return None


def main() -> int:
    print("Live Signal Receiver")
    print("Type a message and press Enter to broadcast.")
    print("You will see the incoming channel transmissions (RX).")
    print("Type 'quit' or 'exit' to leave.\n")

    salt = 0
    history: List[Dict[str, Any]] = []

    while True:
        try:
            user_input = input("send> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "q"}:
            print("Exiting.")
            break

        print(f"\n[TX] Broadcasting: {user_input}")
        print("[RX] Tuning channels for incoming transmissions...\n")

        sources = get_frequency_db()
        if not sources:
            print("[ERROR] No frequency sources available.")
            continue

        # TX: broadcast to all channels first
        if _HIVE_AVAILABLE:
            for i, src in enumerate(sources):
                freq = src.get("frequency_hz", 0.0)
                send_to_channel(frequency_hz=freq, message=user_input, salt=salt + i)

        # RX: tune in to each channel and receive incoming transmission
        # Filter out echoes of our own TX by using a unique salt and
        # relying on channel state population.
        for i, src in enumerate(sources):
            freq = src.get("frequency_hz", 0.0)
            label = src.get("label", src.get("source_id", f"source_{i+1}"))
            wavelength = carrier_wavelength(freq) if freq > 0 else float("inf")

            if _HIVE_AVAILABLE:
                # Use a separate RX salt so RX does not re-open the TX waveform.
                rx_salt = 1_000_000 + salt + i
                result = receive_from_channel(frequency_hz=freq, salt=rx_salt)
                info_str = result.get("information_string", "")
                error = result.get("error")
            else:
                info_str = ""
                error = "hive_unavailable"


            history.append({
                "label": label,
                "frequency_hz": freq,
                "wavelength_m": wavelength,
                "information_string": info_str,
                "error": error,
                "timestamp": time.time(),
            })

            print(f"  {label:<20} {_freq_label(freq):>14}  λ={wavelength:.4f} m")
            if error:
                print(f"    <- {error}")
            else:
                print(f"    <- {info_str}")
            print()

        salt += 1

        if len(history) > 500:
            history = history[-500:]

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
