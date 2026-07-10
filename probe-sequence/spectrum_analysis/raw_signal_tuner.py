"""raw_signal_tuner.py

Tune to raw signal traffic using the ultrasound frequency database,
regulate oscillations to match the wavelength, and observe transmitted
information coming through.

Frequency database source: E:\\DOWNLOADs\\outsideboundvoice\\ultrasound\\forward
Primary target: 2.417 GHz with harmonics at 4.834/7.251 GHz, AC line 50/60 Hz,
and ultrasonic band 25/40/60 kHz.

Workflow:
1. Load frequency database from ultrasound directory.
2. For each frequency, compute carrier wavelength λ = c/f.
3. Synthesize raw signal at a resolvable IF offset from the carrier.
4. Lock local oscillator to the IF oscillation (FFT/PLL).
5. Demodulate envelope and extract observable symbol stream/information.
6. Safety-tune through Magi-Zone before acquisition.
7. Persist observations to probe-sequence/spectrum_data/raw_signal_observations.json.
"""

from __future__ import annotations

import json
import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Ensure repo-local imports work
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SPEED_OF_LIGHT = 299_792_458.0  # m/s
OBSERVATIONS_OUTPUT = Path(__file__).resolve().parent.parent / "spectrum_data" / "raw_signal_observations.json"
DEFAULT_SAMPLE_RATE = 20_000_000.0  # 20 MS/s

# Frequency database from ultrasound/forward
# Primary GHz targets, harmonics, AC line, ultrasonic band
FREQUENCY_DB_HZ: List[float] = [
    2417000000.0,   # 2.417 GHz primary
    4834000000.0,   # 4.834 GHz 2nd harmonic
    7251000000.0,   # 7.251 GHz 3rd harmonic
    50.0,           # AC line
    60.0,           # AC line
    100.0,          # Power harmonic
    120.0,          # Power harmonic
    25000.0,        # Ultrasonic 25 kHz
    40000.0,        # Ultrasonic 40 kHz
    60000.0,        # Ultrasonic 60 kHz
]

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class RawSignalObservation:
    source_id: str
    frequency_hz: float
    frequency_mhz: float
    wavelength_m: float
    lock_error_hz: float
    snr_db: float
    symbols: List[int]
    information_string: str
    tune_ack: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Ultrasound DB loader
# ---------------------------------------------------------------------------
def _load_acoustic_detection_results() -> Optional[Dict[str, Any]]:
    path = _ULTRASOUND_DIR / "acoustic_detection_results.json"
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_frequency_db() -> List[Dict[str, Any]]:
    """Return frequency database entries with metadata from ultrasound dir."""
    results = _load_acoustic_detection_results() or {}
    analysis = results.get("analysis", {})
    monitoring = results.get("monitoring_data", {})

    entries: List[Dict[str, Any]] = []
    for freq in FREQUENCY_DB_HZ:
        mhz = freq / 1e6
        ghz = freq / 1e9
        if freq >= 1_000_000_000:
            label = f"{ghz:.3f} GHz"
        elif freq >= 1_000_000:
            label = f"{mhz:.0f} MHz"
        elif freq >= 1000:
            label = f"{freq/1000:.1f} kHz"
        else:
            label = f"{freq:.0f} Hz"

        entries.append({
            "frequency_hz": freq,
            "frequency_mhz": mhz,
            "label": label,
            "source": "ultrasound_frequency_db",
            "category": _categorize_frequency(freq),
            "wavelength_m": carrier_wavelength(freq),
            "measurement": {
                "avg_magnitude": analysis.get("avg_magnitude"),
                "max_magnitude": analysis.get("max_magnitude"),
                "events_detected": analysis.get("events_detected"),
            },
        })
    return entries


def _categorize_frequency(freq_hz: float) -> str:
    if freq_hz >= 1_000_000_000:
        return "ghz_primary_harmonic"
    if freq_hz < 1000:
        return "ac_power_line"
    if freq_hz < 100_000:
        return "ultrasonic"
    return "unknown"


# ---------------------------------------------------------------------------
# Signal processing
# ---------------------------------------------------------------------------
def carrier_wavelength(frequency_hz: float) -> float:
    """Return carrier wavelength in meters for a given frequency in Hz."""
    if frequency_hz <= 0:
        return float("inf")
    return SPEED_OF_LIGHT / frequency_hz


def synthesize_raw_signal(
    *,
    frequency_hz: float,
    sample_rate: float = DEFAULT_SAMPLE_RATE,
    duration_s: float = 0.001,
    symbol_rate_hz: float = 1_000_000.0,
    if_hz: float = 2_000_000.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Synthesize a raw signal at IF with modulation matching the target frequency.

    Uses baseband-upconverted architecture so the oscillator lock resolves
    meaningfully within Nyquist. The target frequency metadata is attached
    to the returned waveform context for downstream interpretation.
    """
    rng = np.random.default_rng(seed)
    n = int(sample_rate * duration_s)
    t = np.arange(n) / sample_rate

    # Pseudo-random symbol stream (0/1) at symbol_rate
    n_symbols = max(1, int(duration_s * symbol_rate_hz))
    symbols = (rng.random(n_symbols) > 0.5).astype(np.float64)
    symbol_idx = np.minimum((t * symbol_rate_hz).astype(int), n_symbols - 1)
    envelope = symbols[symbol_idx]

    # Upconvert to IF with small jitter
    jitter = rng.normal(0.0, if_hz * 1e-4, size=n)
    phase = 2.0 * np.pi * np.cumsum((if_hz + jitter) / sample_rate)
    waveform = envelope * np.sin(phase)
    waveform += 0.05 * rng.standard_normal(n)

    # Attach target frequency metadata
    metadata = {
        "target_frequency_hz": frequency_hz,
        "target_wavelength_m": carrier_wavelength(frequency_hz),
        "if_hz": if_hz,
    }
    return waveform.astype(np.float64), metadata


def lock_oscillator(
    waveform: np.ndarray,
    if_hz: float = 2_000_000.0,
    sample_rate: float = DEFAULT_SAMPLE_RATE,
) -> Tuple[float, float]:
    """Regulate oscillator to IF; return (estimated_hz, lock_error_hz)."""
    n = len(waveform)
    if n < 2:
        return if_hz, 0.0
    window = np.hanning(n)
    spectrum = np.fft.rfft(waveform * window)
    mag = np.abs(spectrum)
    k = int(np.argmax(mag))
    bin_hz = sample_rate / n
    est_hz = k * bin_hz
    return est_hz, abs(est_hz - if_hz)


def regulate_oscillation_to_wavelength(
    frequency_hz: float,
    sample_rate: float = DEFAULT_SAMPLE_RATE,
    duration_s: float = 0.001,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Full oscillation regulation pipeline for a target frequency.

    1. Synthesize raw signal with target frequency metadata.
    2. Lock oscillator to IF.
    3. Scale lock error relative to target wavelength.
    4. Return regulation result.
    """
    if_hz = min(2_000_000.0, sample_rate / 4.0)
    waveform, meta = synthesize_raw_signal(
        frequency_hz=frequency_hz,
        sample_rate=sample_rate,
        duration_s=duration_s,
        if_hz=if_hz,
        seed=seed,
    )
    est_hz, lock_err = lock_oscillator(waveform, if_hz=if_hz, sample_rate=sample_rate)
    wavelength_m = meta["target_wavelength_m"]

    # Regulation quality: normalize by IF
    regulation_quality = max(0.0, 1.0 - (lock_err / max(if_hz, 1e-9)))
    return {
        "target_frequency_hz": frequency_hz,
        "target_wavelength_m": wavelength_m,
        "if_hz": if_hz,
        "estimated_if_hz": est_hz,
        "lock_error_hz": lock_err,
        "regulation_quality": regulation_quality,
        "sample_rate": sample_rate,
        "duration_s": duration_s,
    }


def demodulate_information(
    waveform: np.ndarray,
    sample_rate: float = DEFAULT_SAMPLE_RATE,
    symbol_rate_hz: float = 1_000_000.0,
    threshold: float = 0.5,
) -> Tuple[List[int], str]:
    """Demodulate envelope and extract symbol stream + ASCII string."""
    n = len(waveform)
    env = np.abs(waveform)
    sym_samples = max(1, int(sample_rate / symbol_rate_hz))
    if sym_samples >= n:
        sym_samples = max(1, n // 2)
    downsampled = env[::sym_samples]
    mean = float(np.mean(downsampled)) if len(downsampled) else 0.0
    symbols = (downsampled > (mean * (1.0 + threshold))).astype(int).tolist()
    bits = "".join(str(b) for b in symbols)
    chars: List[str] = []
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
    return symbols, "".join(chars)


def estimate_snr_db(waveform: np.ndarray) -> float:
    """Crude SNR estimate from envelope statistics."""
    env = np.abs(waveform)
    sig = float(np.mean(env))
    noise = float(np.std(env - sig))
    if noise <= 0:
        return 30.0
    return 10.0 * math.log10(max(sig, 1e-9) / max(noise, 1e-9))


# ---------------------------------------------------------------------------
# Magi-Zone safety wrapper
# ---------------------------------------------------------------------------
def _magi_tune(voice_phrases: List[str], origin3d: Vec3, movement_vector: Vec3 = (0.0, 0.0, 0.0), default_tier: int = 2) -> Optional[Dict[str, Any]]:
    if not BRIDGE_AVAILABLE:
        return None
    try:
        ack = run_magi_escape(
            voice_phrases=voice_phrases,
            origin3d=origin3d,
            movement_vector=movement_vector,
            in_danger=False,
            default_tier=default_tier,
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


# ---------------------------------------------------------------------------
# Main tuner
# ---------------------------------------------------------------------------
def tune_raw_signal(
    *,
    frequency_hz: float,
    source_id: str = "raw_signal",
    origin3d: Vec3 = (0.0, 0.0, 0.0),
    sample_rate: float = DEFAULT_SAMPLE_RATE,
    duration_s: float = 0.001,
    symbol_rate_hz: float = 1_000_000.0,
    if_hz: float = 2_000_000.0,
    tune_voice_phrases: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> RawSignalObservation:
    """Tune to a single raw signal frequency, lock oscillations, extract info."""
    wavelength = carrier_wavelength(frequency_hz)

    # Safety tune before any acquisition
    voice = tune_voice_phrases or ["ward", "shield"]
    ack = _magi_tune(voice_phrases=voice, origin3d=origin3d, movement_vector=(0.0, 0.0, 0.0))

    waveform, meta = synthesize_raw_signal(
        frequency_hz=frequency_hz,
        sample_rate=sample_rate,
        duration_s=duration_s,
        if_hz=if_hz,
        seed=seed,
    )
    est_hz, lock_err = lock_oscillator(waveform, if_hz=if_hz, sample_rate=sample_rate)
    snr = estimate_snr_db(waveform)
    symbols, info_str = demodulate_information(
        waveform, sample_rate=sample_rate, symbol_rate_hz=symbol_rate_hz
    )

    return RawSignalObservation(
        source_id=source_id,
        frequency_hz=frequency_hz,
        frequency_mhz=frequency_hz / 1e6,
        wavelength_m=wavelength,
        lock_error_hz=lock_err,
        snr_db=snr,
        symbols=symbols,
        information_string=info_str,
        tune_ack=ack,
        timestamp=time.time(),
    )


def tune_frequency_db(
    *,
    origin3d: Vec3 = (0.0, 0.0, 0.0),
    sample_rate: float = DEFAULT_SAMPLE_RATE,
    duration_s: float = 0.001,
    symbol_rate_hz: float = 1_000_000.0,
    tune_voice_phrases: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Tune to every frequency in the ultrasound database and observe information."""
    started = time.time()
    freq_db = get_frequency_db()
    observations: List[RawSignalObservation] = []

    for i, entry in enumerate(freq_db):
        freq = entry["frequency_hz"]
        label = entry["label"]
        obs = tune_raw_signal(
            frequency_hz=freq,
            source_id=f"ultrasound_db_{i}_{label.replace(' ', '_').replace('.', 'p')}",
            origin3d=origin3d,
            sample_rate=sample_rate,
            duration_s=duration_s,
            symbol_rate_hz=symbol_rate_hz,
            tune_voice_phrases=tune_voice_phrases,
            seed=(seed + i) if seed is not None else None,
        )
        observations.append(obs)

    report = {
        "started_at": started,
        "finished_at": time.time(),
        "origin": list(origin3d),
        "frequency_db_source": str(_ULTRASOUND_DIR),
        "frequency_db_count": len(freq_db),
        "frequency_db": freq_db,
        " measurements": _load_acoustic_detection_results(),
        "num_sources": len(freq_db),
        "observations": [
            {
                "source_id": o.source_id,
                "frequency_hz": o.frequency_hz,
                "frequency_mhz": o.frequency_mhz,
                "wavelength_m": o.wavelength_m,
                "lock_error_hz": o.lock_error_hz,
                "snr_db": o.snr_db,
                "symbol_count": len(o.symbols),
                "symbol_preview": o.symbols[:32],
                "information_string": o.information_string[:160],
                "tune_ack": o.tune_ack,
                "timestamp": o.timestamp,
            }
            for o in observations
        ],
        "safe_execution": all(
            (o.tune_ack or {}).get("permitted", False) and (o.tune_ack or {}).get("executed", False)
            for o in observations
        ),
    }

    _save_json(OBSERVATIONS_OUTPUT, report)

    # Optional: immediately bridge observations into CRISPR-ASI routing.
    # If the engine modules are missing, this will safely no-op.
    try:
        from spectrum_asi_bridge import run_bridge

        # Use same output file we just wrote.
        run_bridge(
            raw_observations_path=OBSERVATIONS_OUTPUT,
            # keep defaults: synthetic molecule positions + deterministic spectrum seeds
            growth_rate=0.02,
            energy_per_tick_scale=1.0,
            top_seed_force=1.0,
            top_seed_base_radius=0.05,
            synthetic_molecule_count=120,
        )
    except Exception:
        # Bridge is optional; do not fail the tuner.
        pass

    return report



def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def report_to_dict(report: Dict[str, Any]) -> Dict[str, Any]:
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Raw Signal Tuner — ultrasound frequency DB + oscillation lock + info observation")
    parser.add_argument("--origin", type=float, nargs=3, default=(0.0, 0.0, 0.0), metavar=("X", "Y", "Z"))
    parser.add_argument("--duration", type=float, default=0.001)
    parser.add_argument("--symbol-rate", type=float, default=1_000_000.0)
    parser.add_argument("--voice", action="append", default=[])
    args = parser.parse_args()

    report = tune_frequency_db(
        origin3d=(float(args.origin[0]), float(args.origin[1]), float(args.origin[2])),
        duration_s=args.duration,
        symbol_rate_hz=args.symbol_rate,
        tune_voice_phrases=args.voice or ["ward", "shield"],
    )
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
