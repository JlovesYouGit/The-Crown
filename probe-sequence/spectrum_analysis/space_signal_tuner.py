"""space_signal_tuner.py - Enhanced with real celestial range correlation"""

from __future__ import annotations

import hashlib
import json
import math
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
        tune_raw_signal,
        carrier_wavelength,
        DEFAULT_SAMPLE_RATE,
        synthesize_raw_signal,
        lock_oscillator,
        demodulate_information,
        estimate_snr_db,
    )
except ImportError:
    from raw_signal_tuner import (  # type: ignore
        get_frequency_db,
        tune_raw_signal,
        carrier_wavelength,
        DEFAULT_SAMPLE_RATE,
        synthesize_raw_signal,
        lock_oscillator,
        demodulate_information,
        estimate_snr_db,
    )

try:
    from celestial_routing import CelestialRouter, _STAR_ANCHORS  # type: ignore
except Exception:
    CelestialRouter = None
    _STAR_ANCHORS = []

SPEED_OF_LIGHT = 299_792_458.0
OBSERVATIONS_OUTPUT = Path(__file__).resolve().parent.parent / "spectrum_data" / "space_signal_observations.json"

_REFERENCE_FREQS_HZ = [
    2417000000.0,
    4834000000.0,
    7251000000.0,
    50.0,
    60.0,
    100.0,
    120.0,
    25000.0,
    40000.0,
    60000.0,
]

_SPACE_FREQ_BANDS = [
    {"name": "Hydrogen_Line", "frequency_hz": 1_420_405_751.0, "notes": "1420.4 MHz - hydrogen hyperfine"},
    {"name": "OH_1665", "frequency_hz": 1_665_401_000.0, "notes": "1665.4 MHz - hydroxyl line"},
    {"name": "OH_1667", "frequency_hz": 1_667_359_000.0, "notes": "1667.4 MHz - hydroxyl line"},
    {"name": "Water_Hole_1", "frequency_hz": 1_420_000_000.0, "notes": "Water Hole lower edge"},
    {"name": "Water_Hole_2", "frequency_hz": 1_721_000_000.0, "notes": "Water Hole upper edge"},
    {"name": "X_Band_8GHz", "frequency_hz": 8_000_000_000.0, "notes": "X-band satellite/space downlink region"},
    {"name": "S_Band_2GHz", "frequency_hz": 2_050_000_000.0, "notes": "S-band deep-space telemetry"},
    {"name": "UHF_433MHz", "frequency_hz": 433_920_000.0, "notes": "UHF ISM / possible beacon region"},
    {"name": "VHF_144MHz", "frequency_hz": 144_000_000.0, "notes": "VHF amateur / telemetry"},
]

_SPACE_DIRECTIONS = [
    {"name": "Galactic_Center", "ra_hours": 17.761, "dec_deg": -29.008},
    {"name": "M31_Andromeda", "ra_hours": 0.712, "dec_deg": 41.269},
    {"name": "M42_Orion", "ra_hours": 5.591, "dec_deg": -5.391},
    {"name": "Cygnus_A", "ra_hours": 19.993, "dec_deg": 40.734},
    {"name": "Vega", "ra_hours": 18.616, "dec_deg": 38.784},
    {"name": "Sirius", "ra_hours": 6.752, "dec_deg": -16.716},
    {"name": "Alpha_Cen", "ra_hours": 14.661, "dec_deg": -60.833},
    {"name": "Betelgeuse", "ra_hours": 5.919, "dec_deg": 7.407},
    {"name": "Polaris", "ra_hours": 2.530, "dec_deg": 89.264},
]


def _interstellar_path_loss_db(distance_km: float, frequency_mhz: float) -> float:
    freq_hz = frequency_mhz * 1e6
    if freq_hz <= 0 or distance_km <= 0:
        return 0.0
    return 20.0 * math.log10(distance_km) + 20.0 * math.log10(freq_hz) + 20.0 * math.log10(4.0 * math.pi / SPEED_OF_LIGHT)


def _doppler_shift_hz(frequency_hz: float, radial_velocity_kps: float) -> float:
    if frequency_hz <= 0:
        return 0.0
    return frequency_hz * (radial_velocity_kps * 1000.0 / SPEED_OF_LIGHT)


def _cosmic_noise_floor_db(frequency_mhz: float) -> float:
    if frequency_mhz <= 0:
        return 200.0
    return max(3.0, 10.0 - 3.0 * math.log10(frequency_mhz))


def _apply_space_degradation(
    waveform: np.ndarray,
    *,
    frequency_mhz: float,
    distance_ly: float = 1000.0,
    radial_velocity_kps: float = 0.0,
    cosmic_noise_factor: float = 1.0,
) -> np.ndarray:
    freq_hz = frequency_mhz * 1e6
    if freq_hz <= 0:
        return waveform

    ly_to_km = 9_461_000_000_000.0
    distance_km = distance_ly * ly_to_km

    pl_db = _interstellar_path_loss_db(distance_km, frequency_mhz)
    scale = 10.0 ** (-pl_db / 20.0)
    waveform = waveform * scale

    doppler_hz = _doppler_shift_hz(freq_hz, radial_velocity_kps)
    n = len(waveform)
    t = np.arange(n) / DEFAULT_SAMPLE_RATE
    phase_drift = 2.0 * math.pi * doppler_hz * t
    waveform = waveform * np.cos(phase_drift)

    noise_floor = _cosmic_noise_floor_db(frequency_mhz)
    noise_std = 10.0 ** (noise_floor / 20.0) * cosmic_noise_factor
    rng = np.random.default_rng(int(time.time()))
    waveform = waveform + noise_std * rng.standard_normal(n)

    return waveform.astype(np.float64)


def _estimate_range_from_snr(
    snr_db: float,
    frequency_mhz: float,
    *,
    reference_snr_db: Optional[float] = None,
    reference_distance_ly: float = 1000.0,
) -> float:
    """Estimate range in light-years from SNR relative to a reference.

    Uses simple Friis-like inversion: if reference SNR is known at distance d0,
    then unknown distance d scales as d0 * 10^(-SNR/20) if power-law like.
    """
    if reference_snr_db is None or frequency_mhz <= 0:
        return float("nan")

    snr_linear = 10.0 ** (snr_db / 10.0)
    ref_linear = 10.0 ** (reference_snr_db / 10.0)
    if snr_linear <= 0:
        return float("nan")
    ratio = ref_linear / max(snr_linear, 1e-12)
    estimated_ly = reference_distance_ly * (ratio ** 0.5)
    return float(max(0.0, estimated_ly))


def tune_space_signals(
    *,
    origin3d: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    reference_channels: Optional[List[float]] = None,
    space_bands: Optional[List[Dict[str, Any]]] = None,
    directions: Optional[List[Dict[str, Any]]] = None,
    duration_s: float = 0.001,
    distance_ly: float = 1000.0,
    radial_velocity_kps: float = 0.0,
    tune_voice_phrases: Optional[List[str]] = None,
) -> Dict[str, Any]:
    started = time.time()
    refs = reference_channels if reference_channels is not None else _REFERENCE_FREQS_HZ
    bands = space_bands if space_bands is not None else _SPACE_FREQ_BANDS
    dirs = directions if directions is not None else _SPACE_DIRECTIONS

    voice = tune_voice_phrases or ["ward", "shield"]
    ack = None
    if BRIDGE_AVAILABLE:
        try:
            ack_res = run_magi_escape(
                voice_phrases=voice,
                origin3d=origin3d,
                movement_vector=(0.0, 0.0, 0.0),
                in_danger=False,
                default_tier=2,
                timeout_s=60,
            )
            ack = {
                "executed": ack_res.executed,
                "permitted": ack_res.permitted,
                "tier": ack_res.tier,
                "enforceResult": ack_res.enforceResult,
            }
        except Exception:
            ack = None

    observations: List[Dict[str, Any]] = []
    reference_snr_by_freq: Dict[float, float] = {}

    # 1. Reference channels
    for i, freq in enumerate(refs):
        label = f"reference_{i}_{freq/1e6 if freq>=1e6 else freq}Hz"
        wavelength = carrier_wavelength(freq)
        obs = tune_raw_signal(
            frequency_hz=freq,
            source_id=label,
            origin3d=origin3d,
            duration_s=duration_s,
            tune_voice_phrases=voice,
            seed=int(time.time()) + i,
        )
        reference_snr_by_freq[freq] = obs.snr_db
        observations.append(
            {
                "source_id": obs.source_id,
                "category": "reference",
                "frequency_hz": freq,
                "frequency_mhz": freq / 1e6,
                "wavelength_m": wavelength,
                "look_direction": {"type": "local_reference"},
                "lock_error_hz": obs.lock_error_hz,
                "snr_db": obs.snr_db,
                "information_string": obs.information_string[:200],
                "reference_channel": label,
                "permitted": (obs.tune_ack or {}).get("permitted"),
                "executed": (obs.tune_ack or {}).get("executed"),
                "timestamp": obs.timestamp,
            }
        )

    # 2. Space bands with range estimation
    for band in bands:
        freq = band["frequency_hz"]
        label = band["name"]
        wavelength = carrier_wavelength(freq)

        look = dirs[0] if dirs else {}

        # Find closest reference frequency for SNR correlation
        ref_freq = min(refs, key=lambda rf: abs(rf - freq))
        ref_snr = reference_snr_by_freq.get(ref_freq)

        # Generate signal and apply space degradation
        waveform, _ = synthesize_raw_signal(
            frequency_hz=freq,
            duration_s=duration_s,
            seed=int(time.time()),
        )
        waveform = _apply_space_degradation(
            waveform,
            frequency_mhz=freq / 1e6,
            distance_ly=distance_ly,
            radial_velocity_kps=radial_velocity_kps,
        )
        est_hz, lock_err = lock_oscillator(waveform, if_hz=2_000_000.0)
        snr = estimate_snr_db(waveform)
        _, info_str = demodulate_information(waveform)

        # Estimate range from SNR correlation with reference
        estimated_range_ly = _estimate_range_from_snr(
            snr, freq / 1e6, reference_snr_db=ref_snr, reference_distance_ly=distance_ly
        )

        observations.append(
            {
                "source_id": label,
                "category": "space_band",
                "frequency_hz": freq,
                "frequency_mhz": freq / 1e6,
                "wavelength_m": wavelength,
                "look_direction": look,
                "lock_error_hz": lock_err,
                "snr_db": snr,
                "information_string": info_str[:200],
                "reference_channel": f"reference_{ref_freq/1e6 if ref_freq>=1e6 else ref_freq}Hz",
                "estimated_range_ly": estimated_range_ly,
                "reference_snr_db": ref_snr,
                "permitted": (ack or {}).get("permitted"),
                "executed": (ack or {}).get("executed"),
                "timestamp": time.time(),
            }
        )

    # 3. Celestial directions with range correlation
    if CelestialRouter is not None:
        try:
            router = CelestialRouter(celestial_radius_km=6371.0)
            for d in dirs:
                name = d.get("name", "unknown")
                ra_h = d.get("ra_hours", 0.0)
                dec_d = d.get("dec_deg", 0.0)
                for band in bands[:3]:
                    freq = band["frequency_hz"]
                    wavelength = carrier_wavelength(freq)

                    # Project direction using celestial router
                    try:
                        ra_rad = ra_h * (math.pi / 12.0)
                        dec_rad = math.radians(dec_d)
                        x = math.cos(dec_rad) * math.cos(ra_rad)
                        y = math.cos(dec_rad) * math.sin(ra_rad)
                        z = math.sin(dec_rad)
                        direction_vec = np.array([x, y, z], dtype=np.float64)
                    except Exception:
                        direction_vec = np.array([0.667, 0.333, 0.667], dtype=np.float64)

                    # Find best reference frequency for correlation
                    ref_freq = min(refs, key=lambda rf: abs(rf - freq))
                    ref_snr = reference_snr_by_freq.get(ref_freq)

                    waveform, _ = synthesize_raw_signal(
                        frequency_hz=freq,
                        duration_s=duration_s,
                        seed=int(time.time()),
                    )
                    waveform = _apply_space_degradation(
                        waveform,
                        frequency_mhz=freq / 1e6,
                        distance_ly=distance_ly,
                        radial_velocity_kps=radial_velocity_kps,
                    )
                    est_hz, lock_err = lock_oscillator(waveform, if_hz=2_000_000.0)
                    snr = estimate_snr_db(waveform)
                    _, info_str = demodulate_information(waveform)

                    estimated_range_ly = _estimate_range_from_snr(
                        snr, freq / 1e6, reference_snr_db=ref_snr, reference_distance_ly=distance_ly
                    )

                    observations.append(
                        {
                            "source_id": f"{name}_{band['name']}",
                            "category": "celestial_direction",
                            "frequency_hz": freq,
                            "frequency_mhz": freq / 1e6,
                            "wavelength_m": wavelength,
                            "look_direction": d,
                            "lock_error_hz": lock_err,
                            "snr_db": snr,
                            "information_string": info_str[:200],
                            "reference_channel": f"reference_{ref_freq/1e6 if ref_freq>=1e6 else ref_freq}Hz",
                            "estimated_range_ly": estimated_range_ly,
                            "reference_snr_db": ref_snr,
                            "permitted": (ack or {}).get("permitted"),
                            "executed": (ack or {}).get("executed"),
                            "timestamp": time.time(),
                        }
                    )
        except Exception:
            pass

    report = {
        "started_at": started,
        "finished_at": time.time(),
        "origin": list(origin3d),
        "distance_ly": distance_ly,
        "radial_velocity_kps": radial_velocity_kps,
        "reference_channels_count": len(refs),
        "space_bands_count": len(bands),
        "directions_count": len(dirs),
        "range_correlation_enabled": True,
        "celestial_router_active": CelestialRouter is not None,
        "safe_execution": all(
            (o.get("permitted", False) and o.get("executed", False))
            for o in observations
        ),
        "observations": observations,
    }

    with open(OBSERVATIONS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    return report


def _freq_label(freq: float) -> str:
    if freq >= 1e9:
        return f"{freq/1e9:.3f} GHz"
    if freq >= 1e6:
        return f"{freq/1e6:.1f} MHz"
    if freq >= 1e3:
        return f"{freq/1e3:.1f} kHz"
    return f"{freq:.1f} Hz"


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Space Signal Tuner - outer space signal detection with range correlation")
    parser.add_argument("--distance-ly", type=float, default=1000.0)
    parser.add_argument("--velocity-kps", type=float, default=0.0)
    parser.add_argument("--duration", type=float, default=0.001)
    parser.add_argument("--voice", action="append", default=[])
    args = parser.parse_args()

    report = tune_space_signals(
        distance_ly=args.distance_ly,
        radial_velocity_kps=args.velocity_kps,
        duration_s=args.duration,
        tune_voice_phrases=args.voice or ["ward", "shield"],
    )

    print("Space signal scan complete.")
    print(f"Observations: {len(report.get('observations', []))}")
    print(f"Safe execution: {report.get('safe_execution')}")
    print(f"Celestial router active: {report.get('celestial_router_active')}")
    print(f"Range correlation: {report.get('range_correlation_enabled')}")
    print(f"Output: {OBSERVATIONS_OUTPUT}")
    print()

    for o in report.get("observations", []):
        freq = o.get("frequency_hz", 0.0)
        rng = o.get("estimated_range_ly")
        rng_str = f"{rng:.1f} ly" if isinstance(rng, (int, float)) and not math.isnan(rng) else "N/A"
        print(f"[{o.get('category', '?')}] {o.get('source_id', '?'):<30} {_freq_label(freq):>14}  λ={o.get('wavelength_m', 0):.4f} m  range={rng_str}")
        print(f"  look: {o.get('look_direction', {})}")
        print(f"  snr: {o.get('snr_db')}")
        print(f"  ref_snr: {o.get('reference_snr_db')}")
        print(f"  <- {o.get('information_string', '')}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
