"""spectrum_routing.py

Spectrum-to-routing mapping layer.

This module is intentionally lightweight and math-focused; integration is done
from EnergyConcentrationSystem.
"""

from __future__ import annotations

import math
import time
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional

import numpy as np


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


@dataclass
class SpectrumSeed:
    seed_id: str
    pos: np.ndarray  # shape (3,)
    strength: float


@dataclass
class RoutingEdge:
    edge_id: str
    source_seed_id: str
    source_type: str  # "seed"
    target_molecule_id: str
    target_type: str  # "molecule"
    created_at: float
    active: bool
    radius: float
    growth_rate: float
    energy_per_tick: float


class BlockCapacityManager:
    """Tracks cumulative occupancy per block with configurable capacity."""

    def __init__(self, *, max_slots: int = 10_000_000, decay: float = 0.0):
        self.max_slots = int(max_slots)
        self.decay = float(decay)
        self.block_occupancy: Dict[str, float] = {}  # block_id -> occupied_slots (0..max_slots)

    def _apply_decay(self) -> None:
        if self.decay <= 0:
            return
        if not self.block_occupancy:
            return
        for k, v in list(self.block_occupancy.items()):
            self.block_occupancy[k] = max(0.0, v * (1.0 - self.decay))

    def get_occupancy(self, block_id: str) -> float:
        return float(self.block_occupancy.get(block_id, 0.0))

    def add_occupancy(self, block_id: str, delta_slots: float) -> float:
        """Cumulative fill (never decreases when decay=0)."""
        self._apply_decay()
        cur = self.get_occupancy(block_id)
        new_val = min(float(self.max_slots), cur + float(delta_slots))
        self.block_occupancy[block_id] = new_val
        return new_val


class SpectrumRouter:

    """Maintains a persistent routing graph driven by spectrum seeds."""

    def __init__(self, *, max_edges: int = 10000, max_block_slots: int = 10_000_000):
        self.max_edges = max_edges
        self.edges: Dict[str, RoutingEdge] = {}
        self.latest_update: float = 0.0

        # Cumulative per-block occupancy (configurable capacity)
        self.block_capacities = BlockCapacityManager(max_slots=max_block_slots, decay=0.0)


    def _edge_id(self, seed_id: str, mol_id: str) -> str:
        return _sha256_hex(f"seed:{seed_id}|mol:{mol_id}")

    def upsert_edges_unbounded_growth(
        self,
        *,
        seeds: List[SpectrumSeed],
        molecule_positions: List[np.ndarray],
        spectrum_range_name: str,
        seed_strength_scale: float = 1.0,
        base_radius: float = 0.05,
        growth_rate: float = 0.02,
        energy_per_tick_scale: float = 1.0,
        topk_per_seed: int = 4,
        # block definitions are handled upstream; we just accept a block_id per molecule.
        molecule_block_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        """Create/update edges based on proximity; edges grow forever.

        Returns a JSON-serializable routing snapshot.
        """

        if not seeds or not molecule_positions:
            self.latest_update = time.time()
            return {
                "updated_at": self.latest_update,
                "num_edges": 0,
                "edges": [],
                "spectrum_range": spectrum_range_name,
            }

        # Build molecule index based on distance from each seed.
        # We keep this O(N_seeds * N_molecules) since N is small in your sim.
        positions = np.asarray(molecule_positions, dtype=np.float64)

        if molecule_block_ids is None:
            # Fallback: each molecule is its own block.
            molecule_block_ids = [f"mol_{i}" for i in range(len(positions))]

        # Ensure length match
        if len(molecule_block_ids) != len(positions):
            raise ValueError(
                f"molecule_block_ids length mismatch: got {len(molecule_block_ids)} blocks for {len(positions)} molecules"
            )


        created = 0
        activated = 0

        for seed in seeds:
            # distances from this seed
            dists = np.linalg.norm(positions - seed.pos[None, :], axis=1)
            # choose closest molecules
            k = min(topk_per_seed, len(dists))
            nearest_idx = np.argpartition(dists, k - 1)[:k]

            for mol_i in nearest_idx:
                mol_id = str(mol_i)
                edge_id = self._edge_id(seed.seed_id, mol_id)
                # energy_per_tick increases as distance decreases
                inv_dist = 1.0 / (float(dists[mol_i]) + 1e-6)

                # Cumulative block capacity clamp (configurable via BlockCapacityManager).
                block_id = str(molecule_block_ids[int(mol_i)])
                occ = self.block_capacities.get_occupancy(block_id)
                remaining = max(0.0, float(self.block_capacities.max_slots) - occ)

                # Proposed energy-per-tick maps to desired slot fill.
                # Keep the mapping simple: convert energy score -> slots delta.
                energy_score = seed.strength * seed_strength_scale * inv_dist * energy_per_tick_scale
                # Convert to slot delta with a small gain so it fills gradually.
                # (You can tune SLOT_PER_ENERGY_GAIN later.)
                SLOT_PER_ENERGY_GAIN = 1e-3
                delta_slots = float(energy_score) * SLOT_PER_ENERGY_GAIN

                # Clamp by remaining capacity.
                delta_slots_clamped = min(remaining, max(0.0, delta_slots))
                if delta_slots_clamped > 0:
                    self.block_capacities.add_occupancy(block_id, delta_slots_clamped)

                # Only allocate proportional energy for the clamped portion.
                # If remaining is 0, this yields 0 energy_per_tick.
                fill_ratio = 0.0 if delta_slots <= 0 else (delta_slots_clamped / delta_slots)
                energy_per_tick = float(energy_score) * float(fill_ratio)


                if edge_id in self.edges:
                    e = self.edges[edge_id]
                    e.active = True
                    e.radius += e.growth_rate
                    e.energy_per_tick = energy_per_tick
                    activated += 1
                else:
                    self.edges[edge_id] = RoutingEdge(
                        edge_id=edge_id,
                        source_seed_id=seed.seed_id,
                        source_type="seed",
                        target_molecule_id=mol_id,
                        target_type="molecule",
                        created_at=time.time(),
                        active=True,
                        radius=base_radius,
                        growth_rate=growth_rate,
                        energy_per_tick=energy_per_tick,
                    )
                    created += 1

        # Trim if too large (keep newest)
        if len(self.edges) > self.max_edges:
            # sort by created_at descending, keep first max_edges
            items = sorted(self.edges.values(), key=lambda x: x.created_at, reverse=True)
            keep = set(e.edge_id for e in items[: self.max_edges])
            self.edges = {eid: e for eid, e in self.edges.items() if eid in keep}

        self.latest_update = time.time()

        # Snapshot limited for JSON size
        # (You can remove limiting later.)
        edges_out = [
            {
                "edge_id": e.edge_id,
                "source_seed_id": e.source_seed_id,
                "target_molecule_id": e.target_molecule_id,
                "active": e.active,
                "radius": e.radius,
                "growth_rate": e.growth_rate,
                "energy_per_tick": e.energy_per_tick,
                "created_at": e.created_at,
            }
            for e in self.edges.values()
        ]

        # Snapshot block occupancy as JSON
        block_occ_out = {
            "max_block_slots": self.block_capacities.max_slots,
            "num_blocks": len(self.block_capacities.block_occupancy),
            "blocks": [
                {"block_id": bid, "occupied_slots": occ}
                for bid, occ in self.block_capacities.block_occupancy.items()
            ],
        }

        return {
            "updated_at": self.latest_update,
            "spectrum_range": spectrum_range_name,
            "num_edges": len(self.edges),
            "created_or_updated": created + activated,
            "edges": edges_out,
            "block_capacities": block_occ_out,
        }


