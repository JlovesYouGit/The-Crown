"""
energy_concentration.py — CRISPR-ASI Energy Concentration System
Integrates lifecondensation spectrum ranges with molecular physics for energy trapping,
concentration, and dispersion using SHA-256 JSON state tracking and CRISPR-ASI seed logic.
"""

import hashlib
import json
import numpy as np
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading

# CRISPR-ASI imports
from engine.core.constants import ANCHOR_CONST, RESONANCE_BASE
from engine.core.hash_pipeline import build_sequence_hash, query_entropy
from engine.core.spectrum_routing import SpectrumRouter, SpectrumSeed
from engine.core.celestial_routing import CelestialRouter, CelestialCoordinate

logger = logging.getLogger("light-asi.energy_concentration")



# ─── Spectrum Range Constants (from lifecondensation physics) ───────────────────

class SpectrumRange(Enum):
    """Electromagnetic spectrum ranges for energy concentration."""
    GAMMA = (1e-12, 1e-10, "gamma")
    XRAY = (1e-10, 1e-8, "xray")
    ULTRAVIOLET = (1e-8, 4e-7, "ultraviolet")
    VISIBLE = (4e-7, 7e-7, "visible")
    INFRARED = (7e-7, 1e-3, "infrared")
    MICROWAVE = (1e-3, 1e-1, "microwave")
    RADIO = (1e-1, 1e6, "radio")
    
    @property
    def wavelength_min(self) -> float:
        return self.value[0]
    
    @property
    def wavelength_max(self) -> float:
        return self.value[1]
    
    @property
    def name(self) -> str:
        return self.value[2]


# Physics Constants (from lifecondensation spatial_wep-EA)
GOLDEN_RATIO = 1.618033988749
ELECTRODE_RADIUS = 0.0618
TRAP_HEIGHT = 0.15
NM_INERTIA = 5555
AIR_DENSITY = 1.225
IONIZATION_ENERGY_AIR = 14.53e6  # J/m³
PLANCK_CONSTANT = 6.626e-34  # J·s
SPEED_OF_LIGHT = 2.998e8  # m/s


# ─── SHA-256 JSON State Tracking ───────────────────────────────────────────────

@dataclass
class EnergyState:
    """Energy state tracked with SHA-256 JSON using CRISPR-ASI seed logic."""
    timestamp: float
    spectrum_range: str
    energy_density: float
    molecular_weight: float
    trapped_energy: float
    concentration_factor: float
    activation_level: float
    connector_hash: str
    seed_hash: str
    state_hash: str
    
    def to_json(self) -> str:
        """Convert state to JSON for SHA-256 hashing."""
        return json.dumps(asdict(self), sort_keys=True)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EnergyState':
        """Create state from JSON."""
        data = json.loads(json_str)
        return cls(**data)
    
    def compute_state_hash(self) -> str:
        """Compute SHA-256 hash of the entire state."""
        return hashlib.sha256(self.to_json().encode()).hexdigest()


class StateTracker:
    """Tracks energy states using SHA-256 JSON with CRISPR-ASI seed logic."""
    
    def __init__(self, seed: str = ANCHOR_CONST):
        self.seed = seed
        self.states: Dict[str, EnergyState] = {}
        self.state_history: List[EnergyState] = []
        self.lock = threading.Lock()
        
    def generate_connector_hash(self, connector_id: int) -> str:
        """Generate connector hash using CRISPR-ASI seed logic."""
        raw = f"{self.seed}:connector:{connector_id}"
        return hashlib.sha256(raw.encode()).hexdigest()
    
    def generate_seed_hash(self, additional_data: str = "") -> str:
        """Generate seed hash with additional data."""
        raw = f"{self.seed}:{additional_data}"
        return hashlib.sha256(raw.encode()).hexdigest()
    
    def track_state(self, state: EnergyState) -> str:
        """Track a new energy state with SHA-256 verification."""
        with self.lock:
            state.state_hash = state.compute_state_hash()
            self.states[state.state_hash] = state
            self.state_history.append(state)
            
            # Keep history manageable
            if len(self.state_history) > 10000:
                self.state_history = self.state_history[-5000:]
            
            logger.debug(f"Tracked state: {state.state_hash[:16]}… spectrum={state.spectrum_range}")
            return state.state_hash
    
    def get_state(self, state_hash: str) -> Optional[EnergyState]:
        """Retrieve state by hash."""
        return self.states.get(state_hash)
    
    def verify_state_integrity(self, state: EnergyState) -> bool:
        """Verify state integrity using SHA-256."""
        computed_hash = state.compute_state_hash()
        return computed_hash == state.state_hash
    
    def get_latest_state(self) -> Optional[EnergyState]:
        """Get the most recent state."""
        if self.state_history:
            return self.state_history[-1]
        return None


# ─── Connector-Based Activation Focus System ───────────────────────────────────

@dataclass
class Connector:
    """Connector for activation focus system."""
    connector_id: int
    position: np.ndarray
    activation_level: float
    focus_strength: float
    connected_molecules: List[int] = field(default_factory=list)
    energy_flow: float = 0.0
    
    def update_activation(self, target_level: float, rate: float = 0.1):
        """Update activation level towards target."""
        self.activation_level += (target_level - self.activation_level) * rate
        self.activation_level = np.clip(self.activation_level, 0.0, 1.0)


class ConnectorNetwork:
    """Network of connectors for activation focus."""
    
    def __init__(self, num_connectors: int = 12):
        self.connectors: List[Connector] = []
        self.num_connectors = num_connectors
        self.focus_pattern = np.zeros(num_connectors)
        self._initialize_connectors()
        
    def _initialize_connectors(self):
        """Initialize connectors in golden ratio pattern."""
        for i in range(self.num_connectors):
            # Golden ratio spiral pattern
            angle = i * (2 * np.pi / GOLDEN_RATIO)
            radius = ELECTRODE_RADIUS * (i ** 0.5)
            position = np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                (i / self.num_connectors) * TRAP_HEIGHT
            ])
            
            connector = Connector(
                connector_id=i,
                position=position,
                activation_level=0.0,
                focus_strength=1.0 / (i + 1)
            )
            self.connectors.append(connector)
    
    def set_focus_pattern(self, pattern: np.ndarray):
        """Set activation focus pattern."""
        assert len(pattern) == self.num_connectors
        self.focus_pattern = pattern
        
    def update_connectors(self, dt: float):
        """Update all connectors towards focus pattern."""
        for connector, target in zip(self.connectors, self.focus_pattern):
            connector.update_activation(target, dt)
    
    def get_total_activation(self) -> float:
        """Get total network activation."""
        return sum(c.activation_level for c in self.connectors)
    
    def get_energy_flow(self) -> float:
        """Calculate total energy flow through network."""
        total_flow = 0.0
        for connector in self.connectors:
            connector.energy_flow = connector.activation_level * connector.focus_strength
            total_flow += connector.energy_flow
        return total_flow


# ─── Spectrum Range Energy Concentration ────────────────────────────────────────

class SpectrumEnergyConcentrator:
    """Concentrates energy using spectrum ranges from lifecondensation physics."""
    
    def __init__(self, state_tracker: StateTracker):
        self.state_tracker = state_tracker
        self.active_range = SpectrumRange.VISIBLE
        self.concentration_history: List[float] = []
        
    def set_spectrum_range(self, range_enum: SpectrumRange):
        """Set active spectrum range."""
        self.active_range = range_enum
        logger.info(f"Spectrum range set to: {range_enum.name}")
    
    def calculate_photon_energy(self, wavelength: float) -> float:
        """Calculate photon energy using E = hc/λ."""
        return (PLANCK_CONSTANT * SPEED_OF_LIGHT) / wavelength
    
    def calculate_energy_density(self, photon_count: int, wavelength: float) -> float:
        """Calculate energy density using lifecondensation formula."""
        volume = np.pi * (ELECTRODE_RADIUS ** 2) * TRAP_HEIGHT
        photon_energy = self.calculate_photon_energy(wavelength)
        total_energy = photon_count * photon_energy
        return total_energy / volume
    
    def concentrate_energy(self, input_energy: float, target_range: SpectrumRange) -> float:
        """Concentrate energy into target spectrum range."""
        # Calculate concentration factor based on wavelength ratio
        avg_wavelength = (target_range.wavelength_min + target_range.wavelength_max) / 2
        reference_wavelength = (SpectrumRange.VISIBLE.wavelength_min + SpectrumRange.VISIBLE.wavelength_max) / 2
        
        wavelength_ratio = reference_wavelength / avg_wavelength
        concentration_factor = wavelength_ratio ** 2  # Energy scales with λ²
        
        concentrated_energy = input_energy * concentration_factor
        
        self.concentration_history.append(concentrated_energy)
        if len(self.concentration_history) > 1000:
            self.concentration_history = self.concentration_history[-500:]
        
        return concentrated_energy
    
    def get_spectrum_efficiency(self, target_range: SpectrumRange) -> float:
        """Get concentration efficiency for spectrum range."""
        # Efficiency based on molecular alignment with spectrum
        efficiencies = {
            SpectrumRange.GAMMA: 0.95,
            SpectrumRange.XRAY: 0.90,
            SpectrumRange.ULTRAVIOLET: 0.85,
            SpectrumRange.VISIBLE: 0.80,
            SpectrumRange.INFRARED: 0.75,
            SpectrumRange.MICROWAVE: 0.70,
            SpectrumRange.RADIO: 0.65
        }
        return efficiencies.get(target_range, 0.5)


# ─── Molecular Weight Equivalence Energy Trapping ────────────────────────────────

# Used by MolecularEnergyTrap for weight-equivalence calculations.
OXYGEN_MASS = 15.999


class MolecularEnergyTrap:

    """Traps energy by finding equivalent weight to simulation state."""
    
    def __init__(self, state_tracker: StateTracker):
        self.state_tracker = state_tracker
        self.trapped_energy: Dict[str, float] = {}  # molecule_id -> energy
        self.weight_equivalences: Dict[str, float] = {}  # molecule_id -> equivalent_weight
        
    def calculate_molecular_weight(self, molecule_position: np.ndarray, velocity: np.ndarray) -> float:
        """Calculate equivalent molecular weight based on simulation state."""
        # Weight based on kinetic energy and position in trap
        kinetic_energy = 0.5 * OXYGEN_MASS * np.linalg.norm(velocity) ** 2
        potential_energy = np.linalg.norm(molecule_position) * 9.81 * OXYGEN_MASS
        
        total_energy = kinetic_energy + potential_energy
        equivalent_weight = total_energy / (SPEED_OF_LIGHT ** 2)  # E = mc²
        
        return equivalent_weight
    
    def trap_energy(self, molecule_id: str, energy: float, molecular_weight: float) -> bool:
        """Trap energy in molecule based on weight equivalence."""
        # Check if energy can be trapped (weight equivalence match)
        if abs(energy - molecular_weight * (SPEED_OF_LIGHT ** 2)) < molecular_weight * 1e-10:
            self.trapped_energy[molecule_id] = energy
            self.weight_equivalences[molecule_id] = molecular_weight
            logger.debug(f"Trapped {energy:.2e} J in molecule {molecule_id}")
            return True
        return False
    
    def release_energy(self, molecule_id: str) -> Optional[float]:
        """Release trapped energy from molecule."""
        if molecule_id in self.trapped_energy:
            energy = self.trapped_energy.pop(molecule_id)
            self.weight_equivalences.pop(molecule_id, None)
            logger.debug(f"Released {energy:.2e} J from molecule {molecule_id}")
            return energy
        return None
    
    def get_total_trapped_energy(self) -> float:
        """Get total trapped energy across all molecules."""
        return sum(self.trapped_energy.values())
    
    def get_trapping_efficiency(self) -> float:
        """Calculate energy trapping efficiency."""
        total_capacity = len(self.trapped_energy) * OXYGEN_MASS * (SPEED_OF_LIGHT ** 2)
        if total_capacity > 0:
            return self.get_total_trapped_energy() / total_capacity
        return 0.0


# ─── Self-Replication and Energy Dispersion ─────────────────────────────────────

class EnergyReplicator:
    """Self-replicates energy and disperses to molecules in range."""
    
    def __init__(self, state_tracker: StateTracker, replication_range: float = 2.0):
        self.state_tracker = state_tracker
        self.replication_range = replication_range
        self.replication_count = 0
        self.dispersion_history: List[Dict] = []
        
    def replicate_energy(self, source_energy: float, replication_factor: float = 1.5) -> float:
        """Replicate energy with golden ratio scaling."""
        replicated_energy = source_energy * replication_factor * GOLDEN_RATIO
        self.replication_count += 1
        logger.debug(f"Replicated energy: {source_energy:.2e} -> {replicated_energy:.2e} J")
        return replicated_energy
    
    def find_molecules_in_range(self, center: np.ndarray, molecule_positions: List[np.ndarray]) -> List[int]:
        """Find molecules within replication range."""
        in_range = []
        for i, pos in enumerate(molecule_positions):
            distance = np.linalg.norm(pos - center)
            if distance <= self.replication_range:
                in_range.append(i)
        return in_range
    
    def disperse_energy(self, energy: float, target_molecules: List[int], 
                       molecule_positions: List[np.ndarray]) -> Dict[int, float]:
        """Disperse energy to molecules in range."""
        if not target_molecules:
            return {}
        
        # Calculate dispersion weights based on distance
        center = np.mean([molecule_positions[i] for i in target_molecules], axis=0)
        total_weight = 0.0
        weights = {}
        
        for mol_id in target_molecules:
            distance = np.linalg.norm(molecule_positions[mol_id] - center)
            weight = 1.0 / (distance + 1e-10)
            weights[mol_id] = weight
            total_weight += weight
        
        # Distribute energy
        dispersed = {}
        for mol_id, weight in weights.items():
            dispersed[mol_id] = energy * (weight / total_weight)
        
        # Record dispersion
        self.dispersion_history.append({
            'timestamp': time.time(),
            'total_energy': energy,
            'target_count': len(target_molecules),
            'dispersed': dispersed
        })
        
        if len(self.dispersion_history) > 1000:
            self.dispersion_history = self.dispersion_history[-500:]
        
        logger.debug(f"Dispersed {energy:.2e} J to {len(target_molecules)} molecules")
        return dispersed
    
    def get_replication_stats(self) -> Dict:
        """Get replication statistics."""
        return {
            'replication_count': self.replication_count,
            'total_dispersions': len(self.dispersion_history),
            'avg_targets': np.mean([d['target_count'] for d in self.dispersion_history]) if self.dispersion_history else 0
        }


# ─── Main Energy Concentration System ───────────────────────────────────────────

class EnergyConcentrationSystem:

    """

    Main energy concentration system integrating all components.
    Uses SHA-256 JSON state tracking, connector activation focus,
    spectrum range concentration, molecular trapping, and self-replication.
    """
    
    def __init__(self, seed: str = ANCHOR_CONST, num_connectors: int = 12):
        # Initialize components
        self.state_tracker = StateTracker(seed)
        self.connector_network = ConnectorNetwork(num_connectors)
        self.spectrum_concentrator = SpectrumEnergyConcentrator(self.state_tracker)
        self.molecular_trap = MolecularEnergyTrap(self.state_tracker)
        self.replicator = EnergyReplicator(self.state_tracker)

        # Spectrum-driven persistent routing (seed -> molecule edges)
        self.spectrum_router = SpectrumRouter(max_edges=5000)
        # Celestial great-circle routing overlay for faster long-range hops.
        self.celestial_router = CelestialRouter(celestial_radius_km=6371.0, max_block_slots=10_000_000)
        self.latest_celestial_snapshot: Dict[str, Any] = {
            "updated_at": None,
            "spectrum_range": None,
            "num_hops": 0,
            "hops": [],
        }
        self.latest_routing_snapshot: Dict[str, Any] = {
            'updated_at': None,
            'spectrum_range': None,
            'num_edges': 0,
            'created_or_updated': 0,
            'edges': [],
        }

        
        # System state
        self.running = False
        self.thread = None
        self.dt = 0.01
        self.step_count = 0
        
        # Callbacks
        self.energy_callbacks: List[Callable[[EnergyState], None]] = []
        
    def start(self):
        """Start energy concentration system in background thread."""
        if self.running:
            logger.warning("Energy concentration system already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Energy concentration system started")
    
    def stop(self):
        """Stop energy concentration system."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Energy concentration system stopped")
    
    def _run_loop(self):
        """Main energy concentration loop."""
        while self.running:
            try:
                self._update_system()
                self.step_count += 1
                
                # Update state tracking every 10 steps
                if self.step_count % 10 == 0:
                    self._update_energy_state()
                
                time.sleep(self.dt)
            except Exception as e:
                logger.error(f"Energy concentration error: {e}")
                self.running = False
    
    def _update_system(self):
        """Update all system components."""
        # Update connector network
        self.connector_network.update_connectors(self.dt)
        
        # Calculate current energy flow
        energy_flow = self.connector_network.get_energy_flow()
        
        # Concentrate energy
        concentrated = self.spectrum_concentrator.concentrate_energy(
            energy_flow, self.spectrum_concentrator.active_range
        )
        
        # Update molecular trap capacity
        trap_efficiency = self.molecular_trap.get_trapping_efficiency()
        
    def _update_energy_state(self):
        """Update energy state with SHA-256 JSON tracking."""
        # Create current energy state
        state = EnergyState(
            timestamp=time.time(),
            spectrum_range=self.spectrum_concentrator.active_range.name,
            energy_density=self.connector_network.get_energy_flow(),
            molecular_weight=self.molecular_trap.get_total_trapped_energy(),
            trapped_energy=self.molecular_trap.get_total_trapped_energy(),
            concentration_factor=GOLDEN_RATIO,
            activation_level=self.connector_network.get_total_activation(),
            connector_hash=self.state_tracker.generate_connector_hash(self.step_count),
            seed_hash=self.state_tracker.generate_seed_hash(str(self.step_count)),
            state_hash=""  # Will be computed by track_state
        )
        
        # Track state
        state_hash = self.state_tracker.track_state(state)
        
        # Notify callbacks
        for callback in self.energy_callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error(f"Energy callback error: {e}")
    
    def register_energy_callback(self, callback: Callable[[EnergyState], None]):
        """Register callback for energy state updates."""
        self.energy_callbacks.append(callback)
    
    def intensify_routing_from_spectrum(
        self,
        *,
        seeds: List[SpectrumSeed],
        molecule_positions: List[np.ndarray],
        spectrum_range: SpectrumRange,
        seed_strength_scale: float = 1.0,
        base_radius: float = 0.05,
        growth_rate: float = 0.02,
        energy_per_tick_scale: float = 1.0,
        topk_per_seed: int = 4,
    ) -> Dict[str, Any]:
        """Map spectrum seeds into molecular-equivalent energy routing.

        - Creates/updates persistent edges.
        - Edges have unbounded (limitless) radius growth and remain active.
        - Returns a JSON-serializable snapshot.
        """
        snapshot = self.spectrum_router.upsert_edges_unbounded_growth(
            seeds=seeds,
            molecule_positions=molecule_positions,
            spectrum_range_name=spectrum_range.name,
            seed_strength_scale=seed_strength_scale,
            base_radius=base_radius,
            growth_rate=growth_rate,
            energy_per_tick_scale=energy_per_tick_scale,
            topk_per_seed=topk_per_seed,
        )

        self.latest_routing_snapshot = snapshot
        return snapshot

    def intensify_celestial_routing(
        self,
        *,
        seeds: List[SpectrumSeed],
        molecule_positions: List[np.ndarray],
        spectrum_range: SpectrumRange,
        molecule_block_ids: Optional[List[str]] = None,
        seed_strength_scale: float = 1.0,
        energy_per_tick_scale: float = 1.0,
        topk_per_seed: int = 4,
        top_anchors: int = 3,
    ) -> Dict[str, Any]:
        """Project spectrum seeds/molecules to celestial coordinates and route via great-circle arcs.

        This bypasses purely local Euclidean hops with faster celestial routing through
        bright-star anchor waypoints. Returns a JSON-serializable snapshot appended
        to the latest routing state.
        """
        snapshot = self.celestial_router.route_celestial(
            seeds=seeds,
            molecule_positions=molecule_positions,
            molecule_block_ids=molecule_block_ids,
            spectrum_range_name=spectrum_range.name,
            seed_strength_scale=seed_strength_scale,
            energy_per_tick_scale=energy_per_tick_scale,
            topk_per_seed=topk_per_seed,
            top_anchors=top_anchors,
        )
        self.latest_celestial_snapshot = snapshot
        # keep the legacy snapshot shape compatible; merge in celestial metadata
        merged = dict(self.latest_routing_snapshot)
        merged.update(
            {
                "updated_at": snapshot["updated_at"],
                "spectrum_range": snapshot["spectrum_range"],
                "celestial_num_hops": snapshot.get("num_hops", 0),
                "celestial_hops": snapshot.get("hops", []),
                "celestial_waypoints_used": snapshot.get("waypoints_used", []),
                "celestial_radius_km": snapshot.get("celestial_radius_km"),
                "block_capacities": snapshot.get("block_capacities", {}),
            }
        )
        self.latest_routing_snapshot = merged
        return merged

    def concentrate_from_spectrum(self, spectrum_range: SpectrumRange, input_energy: float) -> str:

        """Concentrate energy from specific spectrum range."""
        self.spectrum_concentrator.set_spectrum_range(spectrum_range)
        concentrated = self.spectrum_concentrator.concentrate_energy(input_energy, spectrum_range)
        
        # Create state for this concentration event
        state = EnergyState(
            timestamp=time.time(),
            spectrum_range=spectrum_range.name,
            energy_density=concentrated,
            molecular_weight=0.0,
            trapped_energy=0.0,
            concentration_factor=concentrated / input_energy if input_energy > 0 else 0.0,
            activation_level=0.0,
            connector_hash=self.state_tracker.generate_connector_hash(self.step_count),
            seed_hash=self.state_tracker.generate_seed_hash(spectrum_range.name),
            state_hash=""
        )
        
        return self.state_tracker.track_state(state)
    
    def trap_molecular_energy(self, molecule_id: str, energy: float, 
                             position: np.ndarray, velocity: np.ndarray) -> bool:
        """Trap energy in molecule using weight equivalence."""
        molecular_weight = self.molecular_trap.calculate_molecular_weight(position, velocity)
        success = self.molecular_trap.trap_energy(molecule_id, energy, molecular_weight)
        
        if success:
            # Update state
            self._update_energy_state()
        
        return success
    
    def replicate_and_disperse(self, source_molecule_id: str, source_position: np.ndarray,
                              all_positions: List[np.ndarray]) -> Dict[int, float]:
        """Replicate energy and disperse to nearby molecules."""
        # Get trapped energy
        source_energy = self.molecular_trap.trapped_energy.get(source_molecule_id, 0.0)
        
        if source_energy <= 0:
            return {}
        
        # Replicate energy
        replicated = self.replicator.replicate_energy(source_energy)
        
        # Find molecules in range
        target_molecules = self.replicator.find_molecules_in_range(source_position, all_positions)
        
        # Disperse energy
        dispersed = self.replicator.disperse_energy(replicated, target_molecules, all_positions)
        
        # Release source energy
        self.molecular_trap.release_energy(source_molecule_id)
        
        # Trap dispersed energy
        for mol_id, energy in dispersed.items():
            if mol_id < len(all_positions):
                self.molecular_trap.trap_energy(
                    str(mol_id), energy, 
                    self.molecular_trap.calculate_molecular_weight(
                        all_positions[mol_id], np.zeros(3)
                    )
                )
        
        # Update state
        self._update_energy_state()
        
        return dispersed
    
    def set_focus_pattern(self, pattern: np.ndarray):
        """Set connector focus pattern."""
        self.connector_network.set_focus_pattern(pattern)
    
    def get_system_state(self) -> Dict:

        """Get complete system state."""
        latest_state = self.state_tracker.get_latest_state()
        
        return {
            'running': self.running,
            'step_count': self.step_count,
            'connector_network': {
                'total_activation': self.connector_network.get_total_activation(),
                'energy_flow': self.connector_network.get_energy_flow(),
                'num_connectors': self.connector_network.num_connectors
            },
            'spectrum_concentrator': {
                'active_range': self.spectrum_concentrator.active_range.name,
                'concentration_history_size': len(self.spectrum_concentrator.concentration_history)
            },
            'molecular_trap': {
                'total_trapped_energy': self.molecular_trap.get_total_trapped_energy(),
                'trapping_efficiency': self.molecular_trap.get_trapping_efficiency(),
                'num_trapped_molecules': len(self.molecular_trap.trapped_energy)
            },
            'replicator': self.replicator.get_replication_stats(),
            'latest_state_hash': latest_state.state_hash if latest_state else None,
            'state_history_size': len(self.state_tracker.state_history),
            'spectrum_routing': self.latest_routing_snapshot,
            'celestial_routing': self.latest_celestial_snapshot,
        }

    
    def __repr__(self) -> str:
        return (
            f"EnergyConcentrationSystem(running={self.running}, "
            f"trapped_energy={self.molecular_trap.get_total_trapped_energy():.2e} J, "
            f"activation={self.connector_network.get_total_activation():.2f})"
        )
