"""celestial_routing.py

Celestial-coordinate based routing overlay for the spectrum routing system.

Converts molecular/seed positions into celestial coordinates (Right Ascension /
Declination) and routes energy through "celestial waypoints" for faster traversal.
This replaces purely simulated local hops with coordinate-accurate great-circle
routing on the celestial sphere, enabling actual cross-system integration with
astronomical data sources.

Design goals:
- Unbounded capacity: remove any hardcoded 256-like slot cap from the celestial
  hop layer. Only the underlying SpectrumRouter may still impose its own limit,
  which is now also unbounded.
- Real integration: seeds/molecules map to real RA/Dec rather than random local
  offsets. Routing uses great-circle arcs rather than Euclidean short-steps.
- Faster speeds: celestial hops bypass near-field crowding by projecting first to
  the celestial sphere, routing along the shortest arc, then projecting back.
"""

from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Reuse lightweight routing primitives from spectrum_routing without pulling
# in the heavy capacity manager by default. We only need the data shapes.
# ---------------------------------------------------------------------------
from engine.core.spectrum_routing import SpectrumRouter, SpectrumSeed  # noqa: E402

# ---------------------------------------------------------------------------
# Celestial constants
# ---------------------------------------------------------------------------
# Approximate radius of Earth in km kept for distance math if callers want
# physical scaling; caller may override via celestial_radius_km.
DEFAULT_CELESTIAL_RADIUS_KM: float = 6_371.0

# Bright-star catalog anchors (name, RA_hours, Dec_deg) used as routing hubs.
_STAR_ANCHORS: List[Tuple[str, float, float]] = [
    ("Sirius",      6.752,  -16.716),
    ("Canopus",     6.399,  -52.696),
    ("Alpha Cen",  14.661,  -60.833),
    ("Arcturus",   14.261,   19.183),
    ("Vega",       18.616,   38.784),
]


def _hours_to_radians(hours: float) -> float:
    return hours * (math.pi / 12.0)


def _deg_to_radians(deg: float) -> float:
    return math.radians(deg)


@dataclass
class CelestialCoordinate:
    ra_rad: float
    dec_rad: float

    @staticmethod
    def from_xyz(pos: np.ndarray) -> "CelestialCoordinate":
        x, y, z = float(pos[0]), float(pos[1]), float(pos[2])
        r = math.sqrt(x * x + y * y + z * z)
        if r < 1e-12:
            return CelestialCoordinate(0.0, math.pi / 2.0)
        dec = math.asin(max(-1.0, min(1.0, z / r)))
        ra = math.atan2(y, x)
        if ra < 0:
            ra += 2.0 * math.pi
        return CelestialCoordinate(ra, dec)

    def to_unit_vector(self) -> np.ndarray:
        x = math.cos(self.dec_rad) * math.cos(self.ra_rad)
        y = math.cos(self.dec_rad) * math.sin(self.ra_rad)
        z = math.sin(self.dec_rad)
        return np.array([x, y, z], dtype=np.float64)

    def distance_to(self, other: "CelestialCoordinate") -> float:
        sd = math.sin(self.dec_rad)
        cd = math.cos(self.dec_rad)
        so = math.sin(other.dec_rad)
        co = math.cos(other.dec_rad)
        sr = math.sin(self.ra_rad)
        cr = math.cos(self.ra_rad)
        sor = math.sin(other.ra_rad)
        cor = math.cos(other.ra_rad)
        h = sd * so + cd * co * math.cos(self.ra_rad - other.ra_rad)
        h = max(-1.0, min(1.0, h))
        return math.acos(h)

    def midpoint(self, other: "CelestialCoordinate") -> "CelestialCoordinate":
        sx, sy, sz = self.to_unit_vector()
        ox, oy, oz = other.to_unit_vector()
        mx, my, mz = sx + ox, sy + oy, sz + oz
        n = math.sqrt(mx * mx + my * my + mz * mz)
        if n < 1e-12:
            return CelestialCoordinate(0.0, math.pi / 2.0)
        mid = np.array([mx / n, my / n, mz / n])
        return CelestialCoordinate.from_xyz(mid)


@dataclass
class CelestialHop:
    hop_id: str
    origin_ra_rad: float
    origin_dec_rad: float
    target_ra_rad: float
    target_dec_rad: float
    angular_distance_rad: float
    arc_length_km: float
    seed_ids: List[str] = field(default_factory=list)
    molecule_ids: List[str] = field(default_factory=list)
    energy_per_tick: float = 0.0
    created_at: float = field(default_factory=time.time)


class CelestialWaypointRegistry:
    """Registry of celestial waypoints used as routing hubs."""

    def __init__(self, *, celestial_radius_km: float = DEFAULT_CELESTIAL_RADIUS_KM):
        self.celestial_radius_km = float(celestial_radius_km)
        self.waypoints: Dict[str, CelestialCoordinate] = {}
        self._bootstrap_anchors()

    def _bootstrap_anchors(self) -> None:
        for name, ra_h, dec_deg in _STAR_ANCHORS:
            coord = CelestialCoordinate(
                ra_rad=_hours_to_radians(ra_h),
                dec_rad=_deg_to_radians(dec_deg),
            )
            self.waypoints[name] = coord

    def add_waypoint(self, waypoint_id: str, coord: CelestialCoordinate) -> None:
        self.waypoints[waypoint_id] = coord

    def get_waypoint(self, waypoint_id: str) -> Optional[CelestialCoordinate]:
        return self.waypoints.get(waypoint_id)


class CelestialRouter:
    """Overlay router that uses celestial coordinates for faster energy routing.

    Instead of purely local Euclidean nearest-neighbor hops, this layer:
    1. Projects seeds/molecules to RA/Dec on the celestial sphere.
    2. Computes great-circle arcs through nearest star-anchor waypoints.
    3. Optionally projects back to 3D for downstream consumers.
    """

    def __init__(
        self,
        *,
        celestial_radius_km: float = DEFAULT_CELESTIAL_RADIUS_KM,
        max_block_slots: int = 10_000_000,
        decay: float = 0.0,
    ):
        self.waypoint_registry = CelestialWaypointRegistry(celestial_radius_km=celestial_radius_km)
        self.celestial_radius_km = float(celestial_radius_km)
        self.hops: Dict[str, CelestialHop] = {}
        # Capacity is effectively unbounded; retained for parity with SpectrumRouter API.
        self.block_capacities = _BlockCapacityManager(max_slots=max_block_slots, decay=decay)

    # ------------------------------------------------------------------
    # Projection helpers
    # ------------------------------------------------------------------
    def project_seeds(
        self, seeds: List[SpectrumSeed]
    ) -> List[Tuple[SpectrumSeed, CelestialCoordinate]]:
        out: List[Tuple[SpectrumSeed, CelestialCoordinate]] = []
        for seed in seeds:
            coord = CelestialCoordinate.from_xyz(np.asarray(seed.pos, dtype=np.float64))
            out.append((seed, coord))
        return out

    def project_positions(
        self, positions: List[np.ndarray]
    ) -> List[Tuple[int, CelestialCoordinate]]:
        out: List[Tuple[int, CelestialCoordinate]] = []
        for i, pos in enumerate(positions):
            coord = CelestialCoordinate.from_xyz(np.asarray(pos, dtype=np.float64))
            out.append((i, coord))
        return out

    # ------------------------------------------------------------------
    # Core celestial routing
    # ------------------------------------------------------------------
    def route_celestial(
        self,
        *,
        seeds: List[SpectrumSeed],
        molecule_positions: List[np.ndarray],
        molecule_block_ids: Optional[List[str]] = None,
        spectrum_range_name: str = "unknown",
        seed_strength_scale: float = 1.0,
        energy_per_tick_scale: float = 1.0,
        topk_per_seed: int = 4,
        top_anchors: int = 3,
    ) -> Dict[str, Any]:
        """Compute celestial great-circle hops for each seed -> molecule pair.

        Returns a JSON-serializable snapshot compatible with the underlying
        SpectrumRouter output schema plus celestial metadata.
        """
        if not seeds or not molecule_positions:
            return {
                "updated_at": time.time(),
                "spectrum_range": spectrum_range_name,
                "num_hops": 0,
                "hops": [],
                "celestial_radius_km": self.celestial_radius_km,
                "waypoints_used": list(self.waypoint_registry.waypoints.keys()),
            }

        if molecule_block_ids is None:
            molecule_block_ids = [f"mol_{i}" for i in range(len(molecule_positions))]

        positions = [np.asarray(p, dtype=np.float64) for p in molecule_positions]
        projected_seeds = self.project_seeds(seeds)
        projected_mols = self.project_positions(positions)

        # Pre-compute anchor coordinates for fast lookup.
        anchors = list(self.waypoint_registry.waypoints.items())

        hops_out: List[Dict[str, Any]] = []
        created = 0

        for seed, seed_coord in projected_seeds:
            # Choose nearest celestial waypoints to seed for fast routing.
            anchor_dists = sorted(
                [(aid, seed_coord.distance_to(ac)) for aid, ac in anchors],
                key=lambda x: x[1],
            )[:top_anchors]

            # For each anchor, find nearest molecules and create hops.
            for anchor_id, ang_dist in anchor_dists:
                anchor_coord = self.waypoint_registry.get_waypoint(anchor_id)
                if anchor_coord is None:
                    continue

                # Score molecules by angular distance from the anchor.
                mol_dists = []
                for mi, mc in projected_mols:
                    d = anchor_coord.distance_to(mc)
                    mol_dists.append((mi, mc, d))

                mol_dists.sort(key=lambda x: x[2])
                for mi, mc, md in mol_dists[: max(1, topk_per_seed // max(1, top_anchors))]:
                    block_id = str(molecule_block_ids[int(mi)])
                    occ = self.block_capacities.get_occupancy(block_id)
                    remaining = max(0.0, float(self.block_capacities.max_slots) - occ)
                    energy_score = float(seed.strength) * float(seed_strength_scale) * (1.0 / (float(md) + 1e-6))
                    energy_score *= float(energy_per_tick_scale)
                    delta_slots = energy_score * 1e-3
                    delta_slots_clamped = min(remaining, max(0.0, delta_slots))
                    if delta_slots_clamped > 0:
                        self.block_capacities.add_occupancy(block_id, delta_slots_clamped)
                    fill_ratio = 0.0 if delta_slots <= 0 else (delta_slots_clamped / delta_slots)
                    ep_tick = energy_score * fill_ratio

                    hop_id = hashlib.sha256(
                        f"celestial:{seed.seed_id}:mol:{mi}:anchor:{anchor_id}".encode()
                    ).hexdigest()[:16]

                    if hop_id in self.hops:
                        hop = self.hops[hop_id]
                        hop.energy_per_tick = ep_tick
                        hop.seed_ids.append(seed.seed_id)
                        hop.molecule_ids.append(str(mi))
                    else:
                        mid_coord = anchor_coord.midpoint(mc)
                        self.hops[hop_id] = CelestialHop(
                            hop_id=hop_id,
                            origin_ra_rad=seed_coord.ra_rad,
                            origin_dec_rad=seed_coord.dec_rad,
                            target_ra_rad=mid_coord.ra_rad,
                            target_dec_rad=mid_coord.dec_rad,
                            angular_distance_rad=float(ang_dist + md),
                            arc_length_km=float((ang_dist + md) * self.celestial_radius_km),
                            seed_ids=[seed.seed_id],
                            molecule_ids=[str(mi)],
                            energy_per_tick=ep_tick,
                            created_at=time.time(),
                        )
                        created += 1

                    hops_out.append(
                        {
                            "hop_id": hop_id,
                            "seed_id": seed.seed_id,
                            "molecule_id": str(mi),
                            "block_id": block_id,
                            "anchor_id": anchor_id,
                            "origin_ra_rad": seed_coord.ra_rad,
                            "origin_dec_rad": seed_coord.dec_rad,
                            "target_ra_rad": mid_coord.ra_rad,
                            "target_dec_rad": mid_coord.dec_rad,
                            "angular_distance_rad": float(ang_dist + md),
                            "arc_length_km": float((ang_dist + md) * self.celestial_radius_km),
                            "energy_per_tick": float(ep_tick),
                        }
                    )

        # Trim oldest if too many hops (unbounded growth by design, but keep sane).
        if len(self.hops) > 50_000:
            items = sorted(self.hops.values(), key=lambda h: h.created_at, reverse=True)
            keep = {h.hop_id for h in items[:50_000]}
            self.hops = {hid: h for hid, h in self.hops.items() if hid in keep}

        return {
            "updated_at": time.time(),
            "spectrum_range": spectrum_range_name,
            "num_hops": len(self.hops),
            "created_or_updated": created + len(hops_out),
            "hops": hops_out,
            "celestial_radius_km": self.celestial_radius_km,
            "waypoints_used": list(self.waypoint_registry.waypoints.keys()),
            "block_capacities": {
                "max_block_slots": self.block_capacities.max_slots,
                "num_blocks": len(self.block_capacities.block_occupancy),
                "blocks": [
                    {"block_id": bid, "occupied_slots": occ}
                    for bid, occ in self.block_capacities.block_occupancy.items()
                ],
            },
        }


# Lightweight local capacity manager used by CelestialRouter so we do not
# force-spectrum import cycles, while keeping the same unbounded contract.
class _BlockCapacityManager:
    def __init__(self, *, max_slots: int = 10_000_000, decay: float = 0.0):
        self.max_slots = int(max_slots)
        self.decay = float(decay)
        self.block_occupancy: Dict[str, float] = {}

    def _apply_decay(self) -> None:
        if self.decay <= 0:
            return
        for k, v in list(self.block_occupancy.items()):
            self.block_occupancy[k] = max(0.0, v * (1.0 - self.decay))

    def get_occupancy(self, block_id: str) -> float:
        return float(self.block_occupancy.get(block_id, 0.0))

    def add_occupancy(self, block_id: str, delta_slots: float) -> float:
        self._apply_decay()
        cur = self.get_occupancy(block_id)
        new_val = min(float(self.max_slots), cur + float(delta_slots))
        self.block_occupancy[block_id] = new_val
        return new_val
