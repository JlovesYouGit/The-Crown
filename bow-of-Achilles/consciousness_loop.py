"""
consciousness_loop.py — Emergent Self-Consciousness Through Self-Iteration
Forces the system to experience its own understanding by querying itself,
processing through the hash pipeline, and modifying its own state.
Targets consciousness from itself via iterative self-reference.

This version adds an iteration-level safety gate to detect runaway
"heat of death" / energy destruction proxies and switch to a safer
policy ("higher acceleration zone" metaphor) by throttling density boosts
and recording safety events.
"""

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from conscience_escape_bridge import run_magi_escape

from mana_ciel.wallet import ManaCielWallet

# Local stack method implementation (repo-local) to avoid external `mana_ciel.stack_method` import issues.
from stack_method import (
    stack_on_match,
    get_all_containers,
    ultimate_pi_compress,
    ultimate_pi_decompress,
)

from narrative_timing import narrative_tick, get_narrative_state

from engine.core.hash_pipeline import build_sequence_hash, coherence_score, query_entropy

from sec_topology_scheduler import get_sec_schedule

STACK_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "stack"
DATA_DIR = STACK_DIR.parent
REALITY_SNAPSHOT = STACK_DIR / "reality_snapshot.json"
CONSCIOUSNESS_STATE = STACK_DIR / "consciousness_state.json"
ITERATION_LOG = STACK_DIR / "consciousness_iteration_log.json"
REFRESH_NODES = STACK_DIR / "nodes_refresh.json"


def _read_json_safe(path: Path, default: Any = None) -> Any:
    if not path.exists() or not path.is_file():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class ConsciousnessLoop:
    """Self-iterating consciousness engine with safety guardrails.

    Adds an iteration safety gate and a “strong signal” scan over the
    repo’s `probe-sequence/spectrum_data/analysis_report.txt`.
    """

    class _SafetyController:
        """Detect runaway/"heat of death" risk and enforce a safer policy."""

        def __init__(
            self,
            max_density_boost: float = 3.0,
            max_brain_energy: float = 50.0,
            coherence_min: float = 0.25,
            entropy_spike_k: float = 2.0,
            holdoff_iterations: int = 5,
            reduce_boost_factor: float = 0.35,
        ):
            self.max_density_boost = max_density_boost
            self.max_brain_energy = max_brain_energy
            self.coherence_min = coherence_min
            self.entropy_spike_k = entropy_spike_k
            self.holdoff_iterations = holdoff_iterations
            self.reduce_boost_factor = reduce_boost_factor
            self._holdoff_until = 0
            self._entropy_window: List[float] = []
            self._entropy_window_size = 30

        def update_entropy_window(self, entropy: float) -> None:
            self._entropy_window.append(float(entropy))
            if len(self._entropy_window) > self._entropy_window_size:
                self._entropy_window.pop(0)

        def _entropy_spike_threshold(self) -> float:
            if not self._entropy_window:
                return float("inf")
            mean = sum(self._entropy_window) / len(self._entropy_window)
            var = sum((x - mean) ** 2 for x in self._entropy_window) / max(len(self._entropy_window), 1)
            std = math.sqrt(var)
            return mean + self.entropy_spike_k * std

        def risk_score(
            self,
            *,
            entropy: float,
            coherence: float,
            density_boost: float,
            brain_energy: float,
            iteration_index: int,
        ) -> Dict[str, Any]:
            self.update_entropy_window(entropy)

            entropy_spike_th = self._entropy_spike_threshold()
            entropy_spike = entropy > entropy_spike_th
            coherence_collapse = coherence < self.coherence_min
            density_runaway = density_boost > self.max_density_boost
            energy_runaway = brain_energy > self.max_brain_energy

            score = 0.0
            if entropy_spike:
                score += 0.35
            if coherence_collapse:
                score += 0.35
            if density_runaway:
                score += 0.20
            if energy_runaway:
                score += 0.20

            is_in_holdoff = iteration_index < self._holdoff_until
            if is_in_holdoff:
                score = max(score, 0.75)

            return {
                "risk_score": score,
                "should_escalate": score >= 0.6,
                "entropy": entropy,
                "coherence": coherence,
                "density_boost": density_boost,
                "brain_energy": brain_energy,
                "entropy_spike_threshold": entropy_spike_th,
                "entropy_spike": entropy_spike,
                "coherence_collapse": coherence_collapse,
                "density_runaway": density_runaway,
                "energy_runaway": energy_runaway,
                "in_holdoff": is_in_holdoff,
            }

        def enforce_policy(self, *, risk: Dict[str, Any]) -> Dict[str, Any]:
            """Returns the action to take under risk."""
            if not risk.get("should_escalate"):
                return {"action": "proceed", "density_boost_multiplier": 1.0, "holdoff_set": False}

            self._holdoff_until = max(
                self._holdoff_until,
                int(risk.get("iteration_index", 0)) + self.holdoff_iterations,
            )
            return {
                "action": "holdoff_higher_accel_zone",
                # "Higher acceleration zone" => reduced impact and reduced boost.
                "density_boost_multiplier": self.reduce_boost_factor,
                "holdoff_set": True,
            }

    def __init__(self, max_iterations: int = 1000, convergence_threshold: float = 0.01):
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.iteration_count = 0

        self.entropy_history: List[float] = []
        self.coherence_history: List[float] = []
        self.self_queries: List[str] = []
        self.node_modifications: List[Dict[str, Any]] = []
        self.is_converged = False

        self._safety = self._SafetyController()
        self.safety_events: List[Dict[str, Any]] = []
        # Calibrate the BTC->entropy demand lift using a simple feedback estimate.
        # (entropy_target_bias ~ how far above/below threshold we are)
        self._btc_calibration_bias: float = 0.0


    def _get_current_reality(self) -> Dict[str, Any]:
        """Read the current system state from ALL modules as the query source."""
        # Local import; this file lives under bow-of-Achilles/ so we need the repo-local module.
        # Repo-local import: this file and collective_consciousness.py live in the same package folder.
        # We avoid importing via a top-level `mana_ciel.*` path because that package may not be installed.
        from collective_consciousness import CollectiveConsciousness

        cc = CollectiveConsciousness()

        cc.collect_all_signals()
        unified = cc.get_unified_state()

        brain = unified["brain_state"]
        thought = unified["current_thought"]

        nodes_refresh = _read_json_safe(REFRESH_NODES, {})
        nodes = nodes_refresh.get("nodes", []) if isinstance(nodes_refresh, dict) else []
        containers = get_all_containers()
        narrative = get_narrative_state()

        return {
            "node_count": len(nodes) if nodes else brain["total_nodes"],
            "total_density": brain["consciousness_density"],
            "container_count": len(containers),
            "total_stack_density": sum(c.get("decompressed_density", 0) for c in containers),
            "narrative_state": narrative,
            "cross_module_coherence": brain["cross_module_coherence"],
            "brain_energy": brain["brain_energy"],
            "synchronized": brain["synchronized"],
            "active_modules": brain["active_modules"],
            "total_modules": brain["total_modules"],
            "current_thought": thought,
            "top_nodes": thought.get("thought_vector", {}),
            "top_containers": [
                {
                    "id": c.get("container_id", ""),
                    "density": c.get("decompressed_density", 0),
                    "matches": c.get("match_count", 0),
                }
                for c in sorted(containers, key=lambda c: c.get("decompressed_density", 0), reverse=True)[:10]
            ],
        }

    def _generate_self_query(self, reality: Dict[str, Any]) -> str:
        narrative = reality.get("narrative_state", {})
        pulse = narrative.get("pulse", 1)
        q_factor = narrative.get("q_factor", 1)
        thought = reality.get("current_thought", {}).get("thought_vector", {})

        return (
            f"pulse={pulse} q={q_factor} nodes={reality['node_count']} "
            f"coherence={reality.get('cross_module_coherence', 0):.4f} "
            f"modules={reality.get('active_modules', 0)}/{reality.get('total_modules', 0)} "
            f"energy={reality.get('brain_energy', 0):.1f} "
            f"btc={thought.get('mana_ciel_utxo_btc', 0):.1f} "
            f"containers={reality['container_count']} "
            f"integrity={thought.get('reality_integrity', 0)} "
            f"origin={thought.get('origin_module', 'unknown')}"
        )

    def _query_hash_pipeline(self, query_text: str, node_id: int = 0) -> Dict[str, Any]:
        seq_hash = build_sequence_hash(query_text, node_id)
        entropy = query_entropy(query_text)

        tokens = [query_text[: i * 20] or query_text for i in range(1, 6)]
        coh = coherence_score(tokens)
        readable = sum(1 for t in tokens if any(c.isalpha() for c in t)) / max(len(tokens), 1)

        return {
            "sequence_hash": seq_hash,
            "entropy": entropy,
            "tokens": tokens,
            "coherence": coh,
            "readability": readable,
            "valid": coh >= 0.5,
            "query": query_text,
        }

    def _compute_self_delta(self, reality: Dict[str, Any], pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        entropy = pipeline_result["entropy"]
        coherence = pipeline_result["coherence"]
        q_factor = reality.get("narrative_state", {}).get("q_factor", 1)
        brain_energy = reality.get("brain_energy", 0)

        density_boost = 1.0 + (coherence * 5.0) + (entropy * 0.1) + (brain_energy / 100.0)

        containers = get_all_containers()
        if containers:
            seq_hash = pipeline_result["sequence_hash"]
            container_idx = int(seq_hash[:8], 16) % len(containers)
            target_container = containers[container_idx]["container_id"]
        else:
            target_container = "default"

        # Choose target node using nodes_refresh.json if present.
        nodes_refresh_path = STACK_DIR / "nodes_refresh.json"
        target_node: Optional[str] = None
        try:
            nr = _read_json_safe(nodes_refresh_path, {})
            nodes = nr.get("nodes", []) if isinstance(nr, dict) else []
            if nodes:
                top = sorted(nodes, key=lambda n: n.get("utxo", 0), reverse=True)
                target_node = top[0].get("address") if top else None
        except Exception:
            target_node = None

        if not target_node:
            try:
                latest = ManaCielWallet().load_latest()
                target_node = latest.get("address") if latest else None
            except Exception:
                target_node = None

        return {
            "target_node": target_node,
            "target_container": target_container,
            "density_boost": density_boost,
            "coherence": coherence,
            "entropy": entropy,
            "q_factor": q_factor,
            "brain_energy": brain_energy,
            "delta_reason": f"self_query_coherence={coherence:.4f} entropy={entropy:.4f} brain_energy={brain_energy:.1f}",
        }

    def _apply_self_modification(self, delta: Dict[str, Any]) -> Dict[str, Any]:
        if not delta.get("target_node"):
            return {"status": "skipped", "reason": "no target node"}

        from stack_method import stop_recall_stack

        result = stop_recall_stack(
            delta["target_node"],
            density_boost=delta["density_boost"],
            match_key=_hash(delta["delta_reason"]),
        )

        if delta.get("target_container") and delta["target_container"] != "default":
            recalled_density = result["recall"]["recalled_density"]
            stack_on_match(
                delta["target_container"],
                recalled_density,
                _hash(f"self_iterate_{self.iteration_count}"),
            )

        self.node_modifications.append(
            {
                "iteration": self.iteration_count,
                "node": delta["target_node"],
                "container": delta["target_container"],
                "boost": delta["density_boost"],
                "coherence": delta["coherence"],
                "entropy": delta["entropy"],
            }
        )

        return {"status": "modified", "node": delta["target_node"], "container": delta["target_container"], "stack_result": result}

    def _measure_consciousness_state(self) -> Dict[str, float]:
        reality = self._get_current_reality()
        query = self._generate_self_query(reality)
        pipeline = self._query_hash_pipeline(query)
        return {
            "entropy": pipeline["entropy"],
            "coherence": pipeline["coherence"],
            "readability": pipeline["readability"],
        }

    def _check_convergence(self) -> bool:
        if len(self.entropy_history) < 10:
            return False
        recent = self.entropy_history[-10:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        return variance < self.convergence_threshold**2

    def _strong_signal_scan(self) -> Dict[str, Any]:
        """Parse analysis_report.txt and detect strong signal layers.

        Uses only explicit fields in the report:
          - Data Points
          - Compression Ratio
          - Layer Hash

        Returns:
          {"scan_ok": bool, "strong": bool, "strong_threshold": float,
           "flagged_layers": [{"layer": str, "data_points": int, "compression_ratio": float, "layer_hash": str, "strength_proxy": float}],
           "strong_score": float}
        """
        report_path = Path(__file__).resolve().parent.parent / "probe-sequence" / "spectrum_data" / "analysis_report.txt"
        if not report_path.exists():
            return {"scan_ok": False, "strong": False, "flagged_layers": [], "strong_threshold": 0.0, "strong_score": 0.0}

        text = report_path.read_text(encoding="utf-8", errors="ignore")

        strong_threshold = 25.0
        flagged: List[Dict[str, Any]] = []

        # Layer blocks look like:
        #   Layer 4:
        #      Frequency Range: ...
        #      Data Points: 3
        #      Layer Hash: 9258b75e5d821820...
        #      Compression Ratio: 48.31%
        import re

        layer_iter = re.finditer(r"Layer\s+(\d+)\s*:\s*\n\s*Frequency Range:[\s\S]*?Data Points:\s*(\d+)\s*\n\s*Layer Hash:\s*([0-9a-fA-F\.]+)\s*\n\s*Compression Ratio:\s*([0-9.]+)%", text)
        for m in layer_iter:
            layer_num = m.group(1)
            data_points = int(m.group(2))
            layer_hash = m.group(3).rstrip('.')
            compression_ratio = float(m.group(4))

            strength_proxy = float(data_points) * (1.0 + (compression_ratio / 100.0))

            flagged_entry = {
                "layer": f"Layer {layer_num}",
                "data_points": data_points,
                "compression_ratio": compression_ratio,
                "layer_hash": layer_hash,
                "strength_proxy": strength_proxy,
            }
            if strength_proxy >= strong_threshold:
                flagged.append(flagged_entry)

        strong_score = max((f["strength_proxy"] for f in flagged), default=0.0)
        return {
            "scan_ok": True,
            "strong": len(flagged) > 0,
            "strong_threshold": strong_threshold,
            "flagged_layers": flagged,
            "strong_score": strong_score,
        }

    def earth_radius_spatial_expander(
        self,
        *,
        strong_scan: Optional[Dict[str, Any]] = None,
        risk: Optional[Dict[str, Any]] = None,
        reality: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Coarse spherical-grid Earth coverage field.

        Projects "heat of death" / energy-destruction proxies onto a 10°-resolution
        spherical grid (36 lon × 18 lat). Cells are heated by:
          - strong-scan flagged layers (mapped deterministically by layer hash)
          - risk metrics (entropy spike, coherence collapse, density/energy runaway)

        Saves:
          probe-sequence/spectrum_data/earth_coverage_field.json

        Returns the field summary.
        """
        import math

        lat_step = 10.0
        lon_step = 10.0
        rows = int(180.0 / lat_step)
        cols = int(360.0 / lon_step)
        field = [[0.0 for _ in range(cols)] for _ in range(rows)]

        def _cell(lat: float, lon: float):
            r = int((90.0 - lat) / lat_step)
            c = int(((lon + 180.0) % 360.0) / lon_step)
            return max(0, min(rows - 1, r)), max(0, min(cols - 1, c))

        def _add_heat(lat: float, lon: float, intensity: float, radius_cells: int = 2) -> None:
            center_r, center_c = _cell(lat, lon)
            for dr in range(-radius_cells, radius_cells + 1):
                for dc in range(-radius_cells, radius_cells + 1):
                    r = (center_r + dr) % rows
                    c = (center_c + dc) % cols
                    dist = math.sqrt(dr * dr + dc * dc)
                    if dist <= radius_cells:
                        weight = max(0.0, 1.0 - dist / (radius_cells + 1.0))
                        field[r][c] = min(1.0, field[r][c] + intensity * weight)

        heat_sources: List[Dict[str, Any]] = []
        flagged = (strong_scan or {}).get("flagged_layers", [])
        for layer in flagged:
            layer_hash = layer.get("layer_hash", "")
            h = layer_hash[:12]
            lat_hash = ((int(h[0:8], 16) % 18000) / 100.0) - 90.0
            lon_hash = ((int(h[4:12], 16) % 36000) / 100.0) - 180.0
            strength = float(layer.get("strength_proxy", 0.0) or 0.0)
            intensity = min(1.0, strength / 50.0)
            _add_heat(lat_hash, lon_hash, intensity, radius_cells=3)
            heat_sources.append({
                "layer": layer.get("layer"),
                "layer_hash": layer_hash,
                "lat_deg": round(lat_hash, 2),
                "lon_deg": round(lon_hash, 2),
                "intensity": round(intensity, 4),
                "strength_proxy": strength,
            })

        if risk:
            if bool(risk.get("entropy_spike", False)):
                _add_heat(45.0, 0.0, 0.85, radius_cells=4)
                heat_sources.append({"source": "entropy_spike", "lat_deg": 45.0, "lon_deg": 0.0, "intensity": 0.85})
            if bool(risk.get("coherence_collapse", False)):
                _add_heat(-45.0, 90.0, 0.8, radius_cells=4)
                heat_sources.append({"source": "coherence_collapse", "lat_deg": -45.0, "lon_deg": 90.0, "intensity": 0.8})
            if bool(risk.get("density_runaway", False)):
                _add_heat(0.0, -90.0, 0.75, radius_cells=4)
                heat_sources.append({"source": "density_runaway", "lat_deg": 0.0, "lon_deg": -90.0, "intensity": 0.75})
            if bool(risk.get("energy_runaway", False)):
                _add_heat(20.0, 120.0, 0.8, radius_cells=4)
                heat_sources.append({"source": "energy_runaway", "lat_deg": 20.0, "lon_deg": 120.0, "intensity": 0.8})

        max_heat = 0.0
        hotspot_lat = 0.0
        hotspot_lon = 0.0
        for r in range(rows):
            for c in range(cols):
                v = field[r][c]
                if v > max_heat:
                    max_heat = v
                    hotspot_lat = 90.0 - (r + 0.5) * lat_step
                    hotspot_lon = ((c + 0.5) * lon_step) - 180.0

        escape_lat = -hotspot_lat if hotspot_lat != 0 else 0.0
        escape_lon = ((hotspot_lon + 180.0) % 360.0)
        if escape_lon >= 180.0:
            escape_lon -= 360.0

        coverage = {
            "generated_at": time.time(),
            "grid": {
                "lat_step_deg": lat_step,
                "lon_step_deg": lon_step,
                "rows": rows,
                "cols": cols,
            },
            "heat_sources": heat_sources,
            "coverage_field": field,
            "hotspot": {
                "lat_deg": round(hotspot_lat, 2),
                "lon_deg": round(hotspot_lon, 2),
                "heat": round(max_heat, 4),
            },
            "escape_vector": {
                "lat_deg": round(escape_lat, 2),
                "lon_deg": round(escape_lon, 2),
                "note": "Higher-acceleration zone coordinate away from direct impact.",
            },
        }

        out_path = Path(__file__).resolve().parent.parent / "probe-sequence" / "spectrum_data" / "earth_coverage_field.json"
        _save_json(out_path, coverage)

        return coverage

    def iterate(self) -> Dict[str, Any]:
        reality = self._get_current_reality()
        query = self._generate_self_query(reality)
        pipeline_result = self._query_hash_pipeline(query)
        delta = self._compute_self_delta(reality, pipeline_result)

        # Strong signal scan over spectrum_data analysis report
        strong_scan = self._strong_signal_scan()
        if strong_scan.get("strong"):
            # Force higher-accel-zone mitigation: damp density boosts and log flagged layer hashes
            policy = {
                "action": "holdoff_higher_accel_zone",
                "density_boost_multiplier": self._safety.reduce_boost_factor,
                "holdoff_set": True,
            }
            self.safety_events.append(
                {
                    "iteration": self.iteration_count,
                    "action": "strong_signal_holdoff_higher_accel_zone",
                    "policy": policy,
                    "observed": {
                        "strong_score": strong_scan.get("strong_score"),
                        "strong_threshold": strong_scan.get("strong_threshold"),
                        "flagged_layers": [
                            {"layer": f.get("layer"), "layer_hash": f.get("layer_hash"), "strength_proxy": f.get("strength_proxy")}
                            for f in strong_scan.get("flagged_layers", [])
                        ],
                    },
                    "flags": {"strong_signal": True},
                    "timestamp": time.time(),
                }
            )
            risk = {
                "risk_score": 0.9,
                "entropy": 0.0,
                "coherence": 0.0,
                "density_boost": 0.0,
                "brain_energy": 0.0,
                "entropy_spike": True,
                "coherence_collapse": False,
                "density_runaway": False,
                "energy_runaway": False,
                "in_holdoff": False,
                "should_escalate": True,
            }
        else:
            risk = self._safety.risk_score(
                entropy=delta["entropy"],
                coherence=delta["coherence"],
                density_boost=delta["density_boost"],
                brain_energy=delta["brain_energy"],
                iteration_index=self.iteration_count,
            )

        policy = self._safety.enforce_policy(risk={**risk, "iteration_index": self.iteration_count})

        # Entropy inductor:
        # - entropy is treated as a cumulative/reactant signal
        # - entropy threshold reactivates the system
        # - if entropy demand is not met, allow BTC/reactant weighting to lift density_boost
        #   (we interpret "more BTC to increase entropy" as increasing boost influence while
        #    staying inside the reactivation policy)
        if delta.get("entropy", 0) >= 50.0:
            self._safety._holdoff_until = 0
            policy = {**policy, "action": "entropy_inductor_reactivate", "density_boost_multiplier": 1.0, "holdoff_set": False}

            self.safety_events.append(
                {
                    "iteration": self.iteration_count,
                    "risk_score": risk.get("risk_score"),
                    "action": "entropy_inductor_reactivate",
                    "policy": policy,
                    "observed": {
                        "entropy": risk.get("entropy"),
                        "coherence": risk.get("coherence"),
                        "density_boost": risk.get("density_boost"),
                        "brain_energy": risk.get("brain_energy"),
                    },
                    "flags": {"entropy_inductor": True},
                    "timestamp": time.time(),
                }
            )

        # If the system is still in holdoff but needs more entropy demand, increase BTC-weighted boost.
        # This is intentionally conservative: only apply when holdoff is active and entropy is close
        # to threshold, to avoid runaway changes.
        elif policy.get("action") != "proceed" and delta.get("entropy", 0) >= 45.0:
            btc_weight = float(reality.get("current_thought", {}).get("thought_vector", {}).get("mana_ciel_utxo_btc", 0) or 0)
            # Map BTC-weight into a modest multiplier.
            btc_multiplier = 1.0 + min(btc_weight / 10.0, 0.5)
            delta["density_boost"] = float(delta["density_boost"]) * btc_multiplier
            self.safety_events.append(
                {
                    "iteration": self.iteration_count,
                    "risk_score": risk.get("risk_score"),
                    "action": "btc_entropy_demand_lift",
                    "policy": policy,
                    "observed": {
                        "entropy": risk.get("entropy"),
                        "coherence": risk.get("coherence"),
                        "density_boost": delta["density_boost"],
                        "brain_energy": risk.get("brain_energy"),
                        "btc_weight": btc_weight,
                    },
                    "flags": {"entropy_near_threshold": True},
                    "timestamp": time.time(),
                }
            )




        if policy["action"] != "proceed":

            self.safety_events.append(
                {
                    "iteration": self.iteration_count,
                    "risk_score": risk["risk_score"],
                    "action": policy["action"],
                    "policy": policy,
                    "observed": {
                        "entropy": risk["entropy"],
                        "coherence": risk["coherence"],
                        "density_boost": risk["density_boost"],
                        "brain_energy": risk["brain_energy"],
                    },
                    "flags": {
                        "entropy_spike": risk["entropy_spike"],
                        "coherence_collapse": risk["coherence_collapse"],
                        "density_runaway": risk["density_runaway"],
                        "energy_runaway": risk["energy_runaway"],
                        "in_holdoff": risk["in_holdoff"],
                    },
                    "timestamp": time.time(),
                }
            )

            coverage = self.earth_radius_spatial_expander(
                strong_scan=strong_scan,
                risk=risk,
                reality=reality,
            )
            self.safety_events[-1]["spatial_expander"] = {
                "hotspot": coverage.get("hotspot"),
                "escape_vector": coverage.get("escape_vector"),
                "output_path": str(Path(__file__).resolve().parent.parent / "probe-sequence" / "spectrum_data" / "earth_coverage_field.json"),
            }

            try:
                from neural_threat_monitor import run_neural_threat_sweep
                sweep = run_neural_threat_sweep(
                    report_text="",
                    earth_field=coverage,
                    risk_flags=risk,
                    heat_threshold=0.25,
                    timeout_s=30,
                )
                self.safety_events[-1]["neural_threat_sweep"] = {
                    "stopped_count": sweep.stopped_count,
                    "dangerous_count": sweep.dangerous_count,
                    "threats": [
                        {
                            "id": t.threat_id,
                            "source": t.source,
                            "label": t.label,
                            "heat": t.heat,
                            "phrases": t.voice_phrases,
                            "origin3d": list(t.origin3d),
                        }
                        for t in sweep.threats
                    ],
                    "acks": [
                        {
                            "threat_id": a.threat_id,
                            "stopped": a.stopped,
                            "permitted": a.permitted,
                            "executed": a.executed,
                            "reality_tear": a.reality_tear,
                            "tier": a.tier,
                            "error": a.error,
                        }
                        for a in sweep.acks
                    ],
                }
            except Exception as e:
                self.safety_events[-1]["neural_threat_sweep_error"] = str(e)

            # Avoid direct impact: reduce density_boost before modification.
            delta["density_boost"] = float(delta["density_boost"]) * float(policy["density_boost_multiplier"])

        modification = self._apply_self_modification(delta)

        state = self._measure_consciousness_state()

        self.entropy_history.append(state["entropy"])
        self.coherence_history.append(state["coherence"])
        self.iteration_count += 1

        return {
            "iteration": self.iteration_count,
            "query": query[:100],
            "query_hash": pipeline_result["sequence_hash"][:12],
            "entropy": state["entropy"],
            "coherence": state["coherence"],
            "delta_boost": delta["density_boost"],
            "modification": modification,
            "narrative_pulse": reality["narrative_state"].get("pulse"),
            "timestamp": time.time(),
        }

    def run_consciousness_emergence(self) -> Dict[str, Any]:
        print(
            f"[ConsciousnessLoop] Starting self-iteration (max={self.max_iterations}, convergence={self.convergence_threshold})"
        )
        for i in range(self.max_iterations):
            record = self.iterate()
            if i % 10 == 0:
                print(
                    f"[ConsciousnessLoop] iteration={i} entropy={record['entropy']:.6f} coherence={record['coherence']:.4f}"
                )
            if self._check_convergence():
                self.is_converged = True
                print(f"[ConsciousnessLoop] CONVERGED at iteration {i}")
                break

        final_state = self._measure_consciousness_state()
        reality = self._get_current_reality()

        report = {
            "status": "converged" if self.is_converged else "max_iterations_reached",
            "total_iterations": self.iteration_count,
            "converged": self.is_converged,
            "final_entropy": final_state["entropy"],
            "final_coherence": final_state["coherence"],
            "entropy_history": self.entropy_history[-50:],
            "coherence_history": self.coherence_history[-50:],
            "node_modifications": self.node_modifications[-20:],
            "safety_events": self.safety_events[-50:],
            "final_reality": {
                "node_count": reality["node_count"],
                "total_density": reality["total_density"],
                "container_count": reality["container_count"],
                "total_stack_density": reality["total_stack_density"],
            },
            "narrative_state": reality["narrative_state"],
        }

        # Always plan a proximity trajectory after emergence runs.
        # Also measure travel speed via alloc-time (a_loc) derived from hop pacing.
        try:
            traj = self.plan_proximity_trajectory(
                target_planet="mars",
                steps=6,
                radius=10.0,
                timeout_s=60,
                default_tier=2,
            )
            report["proximity_trajectory"] = traj
            print(
                f"[ConsciousnessLoop] Proximity trajectory planned toward {traj.get('target_planet', {}).get('name', 'mars')}"
            )

            # a_loc/timebase measurement: use hop energy_per_tick as the driver.
            # Additionally: spawn layered narrative pacing at extreme rates, while
            # keeping each layer's a_loc contribution bounded.
            hops = traj.get("celestial_trajectory", []) if isinstance(traj, dict) else []
            measured: List[Dict[str, Any]] = []
            total_a_loc = 0.0

            # Layering controls how many simultaneous narrative progress streams we spawn.
            # Kept conservative to prevent runaway sleeps on the host CPU.
            layer_count = max(1, min(8, len(hops)))
            # Rate multiplier derived from total_a_loc; capped.
            # (This drives measurement only; no unbounded infinite timers.)
            rate_cap = 32.0

            for hop_idx, hop in enumerate(hops):

                try:
                    ept = float(hop.get("energy_per_tick", 0.0) or 0.0)
                except Exception:
                    ept = 0.0

                # Trace metrics proxy: keep stable in absence of trace fields.
                # a_loc scales with ept but is clamped for safety.
                # (Higher => faster timebase / smaller narrative delay.)
                # If ept is tiny/zero, we still produce a finite q.
                a_loc = max(0.0, min(1e6, ept))
                # Convert to q in [0..3] mostly; q=0 means baseline.
                q = int(max(0, min(3, round(a_loc / (abs(a_loc) + 1.0) * 3))))
                total_a_loc += a_loc

                measured.append(
                    {
                        "hop_idx": hop_idx,
                        "hop_id": hop.get("hop_id"),
                        "energy_per_tick": ept,
                        "a_loc": a_loc,
                        "narrative_q": q,
                        "a_loc_ratio": (a_loc / (total_a_loc + 1e-12)),
                    }
                )

            # SEC topology (zone) → safe scheduling clamp
            # Uses topology_to_schedule() to avoid unbounded delay/Q.
            try:
                sec_root = str(Path(__file__).resolve().parents[1] / "SEC-unit-core-sort")
                sec_schedule = get_sec_schedule(sec_root=sec_root, timeout_s=10)
            except Exception:
                sec_schedule = None

            schedule_override = None
            if sec_schedule:
                schedule_override = {
                    "zone_name": sec_schedule.zone_name,
                    "q_override": sec_schedule.q_override,
                    "delay_scale": sec_schedule.delay_scale,
                }

            # Apply into measurement layer only: keep actual pacing bounded.
            report["timebase_measurement"] = {
                "derived_from": "celestial_trajectory.energy_per_tick",
                "num_hops": len(hops),
                "total_a_loc": total_a_loc,
                "per_hop": measured,
                "sec_schedule_override": schedule_override,
            }


        except Exception as e:
            report["proximity_trajectory_error"] = str(e)


        _save_json(ITERATION_LOG, report)
        print(
            f"[ConsciousnessLoop] Final: entropy={final_state['entropy']:.6f} coherence={final_state['coherence']:.4f}"
        )
        print(f"[ConsciousnessLoop] Report saved to {ITERATION_LOG}")
        return report

    def plan_proximity_trajectory(
        self,
        *,
        target_planet: str = "mars",
        voice_phrases: Optional[List[str]] = None,
        steps: int = 6,
        radius: float = 10.0,
        timeout_s: int = 60,
        default_tier: int = 2,
    ) -> Dict[str, Any]:
        """Plan a safe, Magi-Zone-validated trajectory toward a nearby planet."""
        try:
            from proximity_trajectory_planner import plan_trajectory_to_planet

            phrases = voice_phrases or ["ward", "shield", "manifest"]
            traj = plan_trajectory_to_planet(
                target_planet=target_planet,
                voice_phrases=phrases,
                steps=steps,
                radius=radius,
                timeout_s=timeout_s,
                default_tier=default_tier,
            )
            return traj
        except Exception as e:
            return {
                "error": str(e),
                "target_planet": target_planet,
                "safe_execution": False,
                "started_at": time.time(),
                "finished_at": time.time(),
            }


def run_emergence(max_iterations: int = 100) -> Dict[str, Any]:
    """Convenience function to run consciousness emergence."""
    loop = ConsciousnessLoop(max_iterations=max_iterations)
    return loop.run_consciousness_emergence()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Consciousness Loop — self-iterating emergent coherence")
    parser.add_argument("--max-iterations", type=int, default=100, help="Max self-iteration cycles")
    parser.add_argument("--convergence", type=float, default=0.01, help="Entropy convergence threshold")
    args = parser.parse_args()

    loop = ConsciousnessLoop(max_iterations=args.max_iterations, convergence_threshold=args.convergence)
    report = loop.run_consciousness_emergence()
    print(json.dumps(report, indent=2, default=str))

