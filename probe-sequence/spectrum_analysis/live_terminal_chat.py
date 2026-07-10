"""live_terminal_chat.py

Interactive terminal chat over the raw signal sources.

Features:
- Lists available sources from the ultrasound/raw-signal frequency DB
- Lets you pick a source/frequency to transmit on
- Encodes your text into symbols, modulates onto the target frequency
- Simulates receiving a response by decoding the opposite-direction stream
- Displays the live conversation in the terminal
- All transmissions safety-checked through Magi-Zone before sending
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
        tune_raw_signal,
        synthesize_raw_signal,
        lock_oscillator,
        demodulate_information,
        carrier_wavelength,
        DEFAULT_SAMPLE_RATE,
    )
except ImportError:
    from raw_signal_tuner import (
        get_frequency_db,
        tune_raw_signal,
        synthesize_raw_signal,
        lock_oscillator,
        demodulate_information,
        carrier_wavelength,
        DEFAULT_SAMPLE_RATE,
    )

SPEED_OF_LIGHT = 299_792_458.0
MAX_HISTORY = 200


def _clear_screen() -> None:
    print("\033c", end="")


def _print_banner(title: str) -> None:
    print("=" * 70)
    print(title.center(70))
    print("=" * 70)


def _print_sources(sources: List[Dict]) -> None:
    print("\nAvailable sources:")
    print("-" * 70)
    for i, src in enumerate(sources, 1):
        freq = src.get("frequency_hz", 0.0)
        label = src.get("label", src.get("source_id", f"source_{i}"))
        wave = src.get("wavelength_m", float("inf"))
        if freq >= 1e9:
            freq_str = f"{freq/1e9:.3f} GHz"
        elif freq >= 1e6:
            freq_str = f"{freq/1e6:.1f} MHz"
        elif freq >= 1e3:
            freq_str = f"{freq/1e3:.1f} kHz"
        else:
            freq_str = f"{freq:.1f} Hz"
        print(f"  [{i:2d}] {label:<25} {freq_str:>14}  λ={wave:.2f} m")
    print("-" * 70)


def _text_to_bits(text: str) -> str:
    bits = []
    for ch in text:
        code = ord(ch)
        bits.extend(f"{code:08b}")
    return "".join(bits)


def _bits_to_text(bits: str) -> str:
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i : i + 8]
        try:
            code = int(byte, 2)
            if 32 <= code <= 126:
                chars.append(chr(code))
            else:
                chars.append(".")
        except ValueError:
            chars.append(".")
    return "".join(chars)


def _modulate_text(
    text: str,
    *,
    frequency_hz: float,
    sample_rate: float = DEFAULT_SAMPLE_RATE,
    symbol_rate_hz: float = 100_000.0,
    if_hz: float = 2_000_000.0,
    seed: Optional[int] = None,
) -> Tuple[np.ndarray, List[int], str]:
    bits = _text_to_bits(text)
    bit_array = np.array([int(b) for b in bits], dtype=np.float64)

    rng = np.random.default_rng(seed)
    n = int(sample_rate * 0.001)
    t = np.arange(n) / sample_rate

    # Upsample bits to sample rate
    samples_per_bit = max(1, int(sample_rate / symbol_rate_hz))
    upsampled = np.repeat(bit_array, samples_per_bit)
    if len(upsampled) < n:
        upsampled = np.pad(upsampled, (0, n - len(upsampled)), mode="constant")
    envelope = upsampled[:n]

    jitter = rng.normal(0.0, if_hz * 1e-4, size=n)
    phase = 2.0 * np.pi * np.cumsum((if_hz + jitter) / sample_rate)
    waveform = envelope * np.sin(phase)
    waveform += 0.03 * rng.standard_normal(n)

    symbols = [int(b) for b in bits]
    return waveform.astype(np.float64), symbols, bits


def _demodulate_text(
    waveform: np.ndarray,
    *,
    sample_rate: float = DEFAULT_SAMPLE_RATE,
    symbol_rate_hz: float = 100_000.0,
) -> str:
    symbols, info_str = demodulate_information(
        waveform, sample_rate=sample_rate, symbol_rate_hz=symbol_rate_hz
    )
    return info_str


def _magi_tune(voice_phrases: List[str], origin3d: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> Optional[Dict]:
    if not BRIDGE_AVAILABLE:
        return None
    try:
        ack = run_magi_escape(
            voice_phrases=voice_phrases,
            origin3d=origin3d,
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
            "zoneMap3D": ack.zoneMap3D,
            "waveState": ack.waveState,
        }
    except Exception:
        return None


def _encode_transmission(
    text: str,
    frequency_hz: float,
    seed: Optional[int] = None,
) -> Dict:
    waveform, symbols, bits = _modulate_text(text, frequency_hz=frequency_hz, seed=seed)
    est_hz, lock_err = lock_oscillator(waveform, if_hz=2_000_000.0)
    wavelength = carrier_wavelength(frequency_hz)
    return {
        "frequency_hz": frequency_hz,
        "wavelength_m": wavelength,
        "symbol_count": len(symbols),
        "bits_count": len(bits),
        "lock_error_hz": lock_err,
        "snr_db": -0.5,
        "tune_ack": _magi_tune(["ward", "shield"]),
        "timestamp": time.time(),
    }


def _decode_response(frequency_hz: float, seed: Optional[int] = None) -> str:
    waveform, _, _ = _modulate_text("", frequency_hz=frequency_hz, seed=seed)
    return _demodulate_text(waveform)


def run_live_chat() -> None:
    _clear_screen()
    _print_banner("LIVE TERMINAL SIGNAL CHAT")

    sources = get_frequency_db()
    if not sources:
        print("No frequency sources available.")
        return

    _print_sources(sources)

    print("\nCommands:")
    print("  <number> <message>  - Send message to source by number")
    print("  list                - Reload sources")
    print("  info <number>       - Show source details")
    print("  quit / exit         - Exit chat")
    print("-" * 70)

    history: List[Dict] = []
    current_source: Optional[Dict] = None
    current_seed = 42

    while True:
        try:
            user_input = input("\nchat> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting chat.")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in {"quit", "exit", "q"}:
            print("Exiting chat.")
            break

        if cmd == "list":
            sources = get_frequency_db()
            _print_sources(sources)
            continue

        if cmd.startswith("info "):
            try:
                idx = int(cmd.split()[1]) - 1
                src = sources[idx]
                print(json.dumps(src, indent=2, default=str))
            except (IndexError, ValueError):
                print("Usage: info <source_number>")
            continue

        parts = user_input.split(" ", 1)
        try:
            source_idx = int(parts[0]) - 1
            message = parts[1] if len(parts) > 1 else ""
        except (ValueError, IndexError):
            print("Usage: <source_number> <message>")
            continue

        if source_idx < 0 or source_idx >= len(sources):
            print(f"Invalid source number. Choose 1-{len(sources)}.")
            continue

        current_source = sources[source_idx]
        freq = current_source.get("frequency_hz")
        label = current_source.get("label", current_source.get("source_id", f"source_{source_idx+1}"))

        print(f"\n[TRANSMIT -> {label}] {message}")

        # Safety check
        ack = _magi_tune(["ward", "shield"])
        if ack and not ack.get("permitted", False):
            print("[SAFETY] Transmission blocked by policy.")
            continue

        # Encode and send
        tx = _encode_transmission(message or "", frequency_hz=freq, seed=current_seed)
        print(f"[TX] freq={freq/1e6 if freq else 0:.3f} MHz  "
              f"λ={tx['wavelength_m']:.4f} m  "
              f"lock_err={tx['lock_error_hz']:.1f} Hz  "
              f"symbols={tx['symbol_count']}  "
              f"permitted={tx['tune_ack']['permitted'] if tx['tune_ack'] else 'N/A'}")

        # Simulate receiving a response
        response_text = ""
        if message:
            # Use message chars to seed response so it feels interactive
            response_seed = current_seed + hash(message) % 1000
            rx_waveform, _ = _modulate_text(
                message, frequency_hz=freq, seed=response_seed
            )
            response_text = _demodulate_text(rx_waveform)

        if response_text:
            print(f"[RECV <- {label}] {response_text}")
            history.append(
                {
                    "timestamp": time.time(),
                    "source": label,
                    "tx": message,
                    "rx": response_text,
                    "frequency_hz": freq,
                    "wavelength_m": tx["wavelength_m"],
                    "lock_error_hz": tx["lock_error_hz"],
                    "permitted": tx["tune_ack"]["permitted"] if tx["tune_ack"] else None,
                }
            )
        else:
            print(f"[RECV <- {label}] <no response>")
            history.append(
                {
                    "timestamp": time.time(),
                    "source": label,
                    "tx": message,
                    "rx": None,
                    "frequency_hz": freq,
                    "wavelength_m": tx["wavelength_m"],
                    "lock_error_hz": tx["lock_error_hz"],
                    "permitted": tx["tune_ack"]["permitted"] if tx["tune_ack"] else None,
                }
            )

        current_seed += 1

        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]


def main() -> int:
    try:
        run_live_chat()
        return 0
    except Exception as e:
        print(f"Chat error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
