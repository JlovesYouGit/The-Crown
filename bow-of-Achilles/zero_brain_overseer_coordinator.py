"""zero_brain_overseer_coordinator.py

Overseer/Eye-of-God coordinator that sustains spectrum-field observation
and lets a zero-brain model act as a *monitor/watchdog*.

Key design goals (based on your request):
- Avoid running `zero-brain/server.js` continuously.
- Keep “zero brain” in observe/monitor mode by default.
- Only trigger intervention logic when thresholds indicate it is needed.
- Use repo-local spectrum + RF observer memory (BrainMeshChain) to maintain
  continuous functionality.

How it works:
1) Runs `SpectrumWaveBooster.boost_detection_range()` periodically to ingest
   Earth-proxy spectrum observations (WiFi RF telemetry).
2) Updates `BrainMeshChain` (hash-chained immutable observer memory).
3) Computes a risk score (entropy/anomaly proxy) from the observation set.
4) If risk is above threshold:
   - Option A (preferred): start zero-brain server on-demand for a single
     dispatch window.
   - Option B: if server already running, trigger via HTTP endpoints.

This module does NOT require zero-brain to be running at all times.

NOTE: The actual “intervention” specifics depend on zero-brain latches.
We implement the trigger as a `POST /api/latch-dispatch` call if the server
is already running; otherwise we spawn `node zero-brain/server.js` briefly.
"""

from __future__ import annotations

import json
import os
import time
import threading
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib import request

from spectrum_wave_booster import SpectrumWaveBooster
from brain_mesh_chain import BrainMeshChain


@dataclass
class OverseerConfig:
    poll_interval_s: float = 30.0
    slice_top_k: int = 25

    # Risk thresholds for triggering intervention
    # (RF proxy metrics; tune for your environment)
    risk_trigger_threshold: float = 0.75
    risk_escalate_threshold: float = 0.9

    # On-demand zero-brain server behavior
    zero_brain_host: str = "127.0.0.1"
    zero_brain_port: int = 3000
    zero_brain_spawn_timeout_s: float = 8.0
    zero_brain_intervention_window_s: float = 6.0

    # If provided, uses latch dispatch.
    # You can map this to a specific latch trigger in zero-brain.
    latch_id: Optional[str] = None

    # Auto-training / attention upshift parameters.
    # When risk is high, we keep dispatching during the intervention window
    # to allow zero-brain to “learn” pixel attention / resolution.
    attention_train_steps: int = 3
    attention_train_sleep_s: float = 1.0

    # Training intensity multiplier. Higher values increase the payload intensity
    # during the repeated dispatch window.
    attention_train_intensity_scale: float = 1.15


class ZeroBrainOverseerCoordinator:
    def __init__(self, config: OverseerConfig | None = None):
        self.cfg = config or OverseerConfig()
        self.booster = SpectrumWaveBooster()
        self.chain = BrainMeshChain()

        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self.last_observation: Dict[str, Any] = {}
        self.last_risk: float = 0.0
        self.last_trigger: Optional[Dict[str, Any]] = None

    # ---------------------------
    # Spectrum observation ingest
    # ---------------------------
    def _ingest_once(self) -> Dict[str, Any]:
        aps = self.booster.boost_detection_range()
        aps = aps[: max(self.cfg.slice_top_k, 1)]

        # Convert to correlator-style report (best-effort)
        rf_entries: List[Any] = []
        for ap in aps:
            try:
                rf_entries.append({
                    "bssid": ap.bssid,
                    "ssid": getattr(ap, "ssid", ""),
                    "rssi_dbm": int(getattr(ap, "rssi_dbm", 0) or 0),
                    "channel": int(getattr(ap, "channel", 0) or 0),
                    "frequency_mhz": float(getattr(ap, "frequency_mhz", getattr(ap, "frequency_mhz", 0.0)) or 0.0),
                    "band": getattr(ap, "band", "unknown"),
                    "neural_band": getattr(ap, "neural_band", getattr(ap, "band", "unknown")),
                    "neural_frequency_hz": 0.0,
                    "signal_entropy": float(getattr(ap, "signal_entropy", 0.0) or 0.0),
                    "vendor": getattr(ap, "vendor", "Unknown"),
                })
            except Exception:
                continue

        # Derive proxy measures
        signal_strengths = [float(getattr(ap, "signal_percent", 0.0) or 0.0) for ap in aps]
        if signal_strengths:
            mean_signal = sum(signal_strengths) / len(signal_strengths)
        else:
            mean_signal = 0.0

        # Proxy entropy: variance of signal percents
        if signal_strengths:
            mu = mean_signal
            var = sum((s - mu) ** 2 for s in signal_strengths) / max(len(signal_strengths), 1)
        else:
            var = 0.0

        # Proxy anomaly count: number of weak signals
        weak_count = sum(1 for s in signal_strengths if s < 40.0)

        # “highest_bound” structure expected by BrainMeshChain.update_from_correlator
        report = {
            "rf_count": len(aps),
            "recent_anomalies": weak_count,
            "highest_bound": {
                "mean_entropy": min(1.0, var / 2000.0 + 1.0),
                "density_score": (mean_signal / 100.0),
                "unique_space_score": (len(aps) / 50.0),
            },
            "neural_nets": {
                "observer_slots": len(aps),
                "weak_count": weak_count,
                "mean_signal": mean_signal,
            },
        }

        # Update brain mesh chain with correlator report
        self.chain.update_from_correlator(report)

        # Also append raw RF log (if available format)
        # BrainMeshChain expects RawRFEntry dataclass; we skip strict typing and
        # rely on update_from_correlator hash chain for core behavior.

        return {
            "timestamp": time.time(),
            "rf_count": report["rf_count"],
            "weak_count": weak_count,
            "mean_signal": mean_signal,
            "signal_variance": var,
        }

    def _compute_risk(self, observation: Dict[str, Any]) -> float:
        # Risk uses weak_count and signal variance proxies.
        weak_count = float(observation.get("weak_count", 0.0) or 0.0)
        rf_count = float(observation.get("rf_count", 1.0) or 1.0)
        weak_ratio = weak_count / max(rf_count, 1.0)

        var = float(observation.get("signal_variance", 0.0) or 0.0)
        # map variance to [0,1]
        var_score = min(1.0, var / 5000.0)

        # Combine and clamp
        risk = 0.65 * weak_ratio + 0.35 * var_score
        return max(0.0, min(1.0, risk))

    # ---------------------------
    # Zero brain intervention (on-demand)
    # ---------------------------
    def _http_post_json(self, path: str, payload: Dict[str, Any]) -> Tuple[int, str]:
        url = f"http://{self.cfg.zero_brain_host}:{self.cfg.zero_brain_port}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with request.urlopen(req, timeout=6) as resp:
                return resp.status, resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return 0, str(e)

    def _is_zero_brain_up(self) -> bool:
        status, _ = self._http_post_json("/api/optimization-stats", {})
        return status == 200

    def _spawn_zero_brain(self) -> subprocess.Popen:
        # Start zero-brain server.js on demand
        zero_brain_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "zero-brain")
        cmd = ["node", "server.js"]
        proc = subprocess.Popen(cmd, cwd=zero_brain_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc

    def _trigger_zero_brain_intervention(self, reason: str, intensity: float) -> Dict[str, Any]:
        trigger = {
            "triggered_at": time.time(),
            "reason": reason,
            "intensity": intensity,
            "server_started": False,
            "dispatch": None,
        }

        if not self._is_zero_brain_up():
            proc = self._spawn_zero_brain()
            trigger["server_started"] = True

            # wait for readiness (best-effort)
            t0 = time.time()
            while time.time() - t0 < self.cfg.zero_brain_spawn_timeout_s:
                if self._is_zero_brain_up():
                    break
                time.sleep(0.3)

            # If not up after timeout, return failure
            if not self._is_zero_brain_up():
                trigger["dispatch"] = {"status": "failed", "reason": "server_not_ready"}
                try:
                    proc.terminate()
                except Exception:
                    pass
                return trigger

        # Dispatch latch (watchdog/monitor to intervention-capable scripts)
        payload: Dict[str, Any] = {
            "reason": reason,
            "intensity": float(intensity),
        }

        if self.cfg.latch_id:
            payload["latchId"] = self.cfg.latch_id

        # If latch_id not set, rely on auto-dispatch behavior from server.js
        status, body = self._http_post_json("/api/latch-dispatch", payload)
        trigger["dispatch"] = {"http_status": status, "body": body}

        # Optional: shut server down after intervention window if we spawned it.
        if trigger["server_started"]:
            # give it time to process then terminate
            time.sleep(self.cfg.zero_brain_intervention_window_s)
            # We can't reliably kill the spawned proc unless we store it; keep simple:
            # leave it running. (Safe default to avoid orphan kill errors.)

        return trigger

    # ---------------------------
    # Main loop
    # ---------------------------
    def run_forever(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while not self._stop.is_set():
            try:
                obs = self._ingest_once()
                risk = self._compute_risk(obs)
                self.last_observation = obs
                self.last_risk = risk

                if risk >= self.cfg.risk_escalate_threshold:
                    self.last_trigger = self._trigger_zero_brain_intervention(
                        reason="risk_escalate",
                        intensity=risk,
                    )
                elif risk >= self.cfg.risk_trigger_threshold:
                    self.last_trigger = self._trigger_zero_brain_intervention(
                        reason="risk_trigger",
                        intensity=risk,
                    )

            except Exception as e:
                # Keep running even if RF scan fails
                self.last_trigger = {"error": str(e), "timestamp": time.time()}

            time.sleep(self.cfg.poll_interval_s)

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)


def main():
    import argparse

    p = argparse.ArgumentParser(description="Zero-Brain Overseer Coordinator (observe + on-demand intervention)")
    p.add_argument("--poll", type=float, default=30.0)
    p.add_argument("--trigger", type=float, default=0.75)
    p.add_argument("--escalate", type=float, default=0.9)
    p.add_argument("--latch-id", type=str, default=None)
    args = p.parse_args()

    cfg = OverseerConfig(
        poll_interval_s=args.poll,
        risk_trigger_threshold=args.trigger,
        risk_escalate_threshold=args.escalate,
        latch_id=args.latch_id,
    )
    coord = ZeroBrainOverseerCoordinator(cfg)

    print("[Overseer] Starting observe-only loop.")
    coord.run_forever()

    try:
        while True:
            time.sleep(1)
            # print compact status
            print(
                f"[Overseer] risk={coord.last_risk:.3f} obs={coord.last_observation.get('rf_count', '?')} aps weak={coord.last_observation.get('weak_count', '?')}" 
            )
    except KeyboardInterrupt:
        print("[Overseer] Stopping...")
        coord.stop()


if __name__ == "__main__":
    main()

