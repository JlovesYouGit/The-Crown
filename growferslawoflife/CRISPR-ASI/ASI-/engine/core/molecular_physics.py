"""
molecular_physics.py — CRISPR-ASI Molecular Physics Engine
Continuous water molecule simulation integrated into ASI knowledge graph.
Manages molecular combination, sustaining, and physics-based knowledge representation.
Now integrated with energy concentration system using SHA-256 JSON state tracking.
"""

import numpy as np
import trimesh
import networkx as nx
from scipy.spatial import KDTree
from scipy.optimize import minimize
import logging
import time
import threading
from pathlib import Path
from typing import Callable, Any, Optional
from dataclasses import dataclass, field

# Energy concentration integration
from engine.core.energy_concentration import (
    EnergyConcentrationSystem, SpectrumRange, EnergyState
)
from engine.core.celestial_routing import CelestialRouter, CelestialCoordinate

logger = logging.getLogger("light-asi.molecular_physics")


# ─── Molecular Physics Constants ───────────────────────────────────────────────

WATER_BOND_LENGTH = 0.96  # Angstroms
WATER_BOND_ANGLE = np.radians(104.5)
OXYGEN_MASS = 15.999  # atomic mass units
HYDROGEN_MASS = 1.008
SURFACE_TENSION = 0.72
VISCOSITY = 0.001
ELASTICITY = 0.3
COHESION = 0.8
SUSPENSION_FORCE = np.array([0, 9.81, 0])


# ─── Water Molecule ─────────────────────────────────────────────────────────────

@dataclass
class WaterMolecule:
    """Represents a single water molecule (H2O) with realistic physics."""
    
    position: np.ndarray
    orientation: Optional[np.ndarray] = None
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    angular_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    force: np.ndarray = field(default_factory=lambda: np.zeros(3))
    torque: np.ndarray = field(default_factory=lambda: np.zeros(3))
    
    def __post_init__(self):
        self.position = np.array(self.position, dtype=np.float64)
        self.oxygen_pos = self.position.copy()
        self.hydrogen1_pos, self.hydrogen2_pos = self._calculate_hydrogen_positions()
        
    def _calculate_hydrogen_positions(self):
        """Calculate hydrogen positions based on oxygen position and orientation."""
        if self.orientation is None:
            h1 = self.oxygen_pos + np.array([
                WATER_BOND_LENGTH * np.cos(WATER_BOND_ANGLE/2),
                WATER_BOND_LENGTH * np.sin(WATER_BOND_ANGLE/2),
                0
            ])
            h2 = self.oxygen_pos + np.array([
                WATER_BOND_LENGTH * np.cos(-WATER_BOND_ANGLE/2),
                WATER_BOND_LENGTH * np.sin(-WATER_BOND_ANGLE/2),
                0
            ])
        else:
            rotation_matrix = self.orientation
            h1_local = np.array([
                WATER_BOND_LENGTH * np.cos(WATER_BOND_ANGLE/2),
                WATER_BOND_LENGTH * np.sin(WATER_BOND_ANGLE/2),
                0
            ])
            h2_local = np.array([
                WATER_BOND_LENGTH * np.cos(-WATER_BOND_ANGLE/2),
                WATER_BOND_LENGTH * np.sin(-WATER_BOND_ANGLE/2),
                0
            ])
            h1 = self.oxygen_pos + rotation_matrix @ h1_local
            h2 = self.oxygen_pos + rotation_matrix @ h2_local
        return h1, h2
    
    def get_center_of_mass(self):
        """Calculate center of mass of the molecule."""
        total_mass = OXYGEN_MASS + 2 * HYDROGEN_MASS
        com = (OXYGEN_MASS * self.oxygen_pos + 
               HYDROGEN_MASS * self.hydrogen1_pos + 
               HYDROGEN_MASS * self.hydrogen2_pos) / total_mass
        return com
    
    def apply_force(self, force):
        """Apply external force to the molecule."""
        self.force += np.array(force)
        
    def apply_torque(self, torque):
        """Apply external torque to the molecule."""
        self.torque += np.array(torque)
        
    def update(self, dt):
        """Update molecule state using Verlet integration."""
        total_mass = OXYGEN_MASS + 2 * HYDROGEN_MASS
        
        # Update velocity
        acceleration = self.force / total_mass
        self.velocity += acceleration * dt
        
        # Update position
        self.position += self.velocity * dt
        
        # Update angular velocity
        moment_of_inertia = self._calculate_moment_of_inertia()
        angular_acceleration = self.torque / moment_of_inertia
        self.angular_velocity += angular_acceleration * dt
        
        # Reset forces
        self.force = np.zeros(3)
        self.torque = np.zeros(3)
        
    def _calculate_moment_of_inertia(self):
        """Calculate approximate moment of inertia."""
        r1 = np.linalg.norm(self.hydrogen1_pos - self.oxygen_pos)
        r2 = np.linalg.norm(self.hydrogen2_pos - self.oxygen_pos)
        I = (HYDROGEN_MASS * r1**2 + HYDROGEN_MASS * r2**2)
        return I


# ─── Lidar Point Topology ───────────────────────────────────────────────────────

class LidarPointTopology:
    """Treats internal geometry as lidar points for bone mesh connection."""
    
    def __init__(self, mesh_points, num_points=1000):
        self.original_points = mesh_points
        self.num_points = num_points
        self.sampled_points = self._sample_points()
        self.kdtree = KDTree(self.sampled_points)
        self.graph = self._build_connectivity_graph()
        
    def _sample_points(self):
        """Sample points from the mesh surface."""
        if len(self.original_points) > self.num_points:
            indices = np.random.choice(len(self.original_points), self.num_points, replace=False)
            return self.original_points[indices]
        return self.original_points
    
    def _build_connectivity_graph(self, radius=0.1):
        """Build connectivity graph based on spatial proximity."""
        graph = nx.Graph()
        
        for i, point in enumerate(self.sampled_points):
            graph.add_node(i, pos=point)
            
        for i in range(len(self.sampled_points)):
            distances, indices = self.kdtree.query(self.sampled_points[i], k=10)
            for j, dist in zip(indices[1:], distances[1:]):
                if dist < radius:
                    graph.add_edge(i, j, weight=dist)
                    
        return graph
    
    def get_nearest_neighbors(self, point, k=5):
        """Get k nearest neighbors to a given point."""
        distances, indices = self.kdtree.query(point, k=k)
        return indices, distances


# ─── Bone Mesh ─────────────────────────────────────────────────────────────────

class BoneMesh:
    """Internal bone mesh composed of water molecule composition, rigid but fluid."""
    
    def __init__(self, topology, num_bones=50):
        self.topology = topology
        self.num_bones = num_bones
        self.bones = []
        self.stiffness = 0.8
        self.damping = 0.3
        self.fluidity = 0.5
        self._initialize_bones()
        
    def _initialize_bones(self):
        """Initialize bones based on topology."""
        anchor_indices = np.linspace(0, len(self.topology.sampled_points) - 1, 
                                    self.num_bones, dtype=int)
        
        for i, idx in enumerate(anchor_indices):
            bone = {
                'anchor_idx': idx,
                'position': self.topology.sampled_points[idx].copy(),
                'velocity': np.zeros(3),
                'connected_bones': [],
                'water_composition': True
            }
            self.bones.append(bone)
        
        for i in range(len(self.bones)):
            for j in range(i + 1, len(self.bones)):
                dist = np.linalg.norm(self.bones[i]['position'] - self.bones[j]['position'])
                if dist < 0.5:
                    self.bones[i]['connected_bones'].append(j)
                    self.bones[j]['connected_bones'].append(i)
    
    def update_physics(self, dt, external_forces=None):
        """Update bone physics with fluid-rigid hybrid behavior."""
        if external_forces is None:
            external_forces = []
            
        for i, bone in enumerate(self.bones):
            spring_force = np.zeros(3)
            for connected_idx in bone['connected_bones']:
                other_bone = self.bones[connected_idx]
                direction = other_bone['position'] - bone['position']
                distance = np.linalg.norm(direction)
                if distance > 0:
                    direction = direction / distance
                    force_mag = self.stiffness * distance * (1 - self.fluidity)
                    spring_force += force_mag * direction
            
            damping_force = -self.damping * bone['velocity']
            total_force = spring_force + damping_force
            for ext_force in external_forces:
                total_force += ext_force
            
            bone['velocity'] += total_force * dt
            bone['position'] += bone['velocity'] * dt
            self._apply_fluid_smoothing(i)
    
    def _apply_fluid_smoothing(self, bone_idx):
        """Apply fluid-like smoothing to bone movement."""
        bone = self.bones[bone_idx]
        if bone['connected_bones']:
            avg_pos = np.zeros(3)
            for neighbor_idx in bone['connected_bones']:
                avg_pos += self.bones[neighbor_idx]['position']
            avg_pos /= len(bone['connected_bones'])
            bone['position'] = (1 - self.fluidity * 0.1) * bone['position'] + \
                              (self.fluidity * 0.1) * avg_pos


# ─── Invisible Skeleton Rig ─────────────────────────────────────────────────────

class InvisibleSkeletonRig:
    """Invisible skeleton rig made of oxygen/water, maintains contact and adjustability."""
    
    def __init__(self, bone_mesh, water_molecules):
        self.bone_mesh = bone_mesh
        self.water_molecules = water_molecules
        self.skeleton_nodes = []
        self.skeleton_edges = []
        self.invisible = True
        self.composition = 'oxygen_water'
        self._build_skeleton()
        
    def _build_skeleton(self):
        """Build invisible skeleton from bone mesh."""
        for bone in self.bone_mesh.bones:
            node = {
                'position': bone['position'].copy(),
                'type': 'oxygen' if np.random.random() > 0.5 else 'water',
                'connections': []
            }
            self.skeleton_nodes.append(node)
        
        for i, bone in enumerate(self.bone_mesh.bones):
            for connected_idx in bone['connected_bones']:
                if i < connected_idx:
                    edge = {
                        'node1': i,
                        'node2': connected_idx,
                        'strength': 1.0,
                        'flexibility': 0.3
                    }
                    self.skeleton_edges.append(edge)
    
    def update_skeleton(self, bone_mesh_positions):
        """Update skeleton positions based on bone mesh."""
        for i, node in enumerate(self.skeleton_nodes):
            node['position'] = bone_mesh_positions[i].copy()
    
    def apply_constraints(self):
        """Apply constraints to maintain water molecule contact."""
        for node in self.skeleton_nodes:
            nearest_mol = min(self.water_molecules, 
                            key=lambda mol: np.linalg.norm(mol.position - node['position']))
            direction = nearest_mol.position - node['position']
            distance = np.linalg.norm(direction)
            if distance > 0:
                direction = direction / distance
                constraint_strength = 0.1
                node['position'] += direction * distance * constraint_strength


# ─── Fluid-Rigid Hybrid Physics ─────────────────────────────────────────────────

class FluidRigidHybridPhysics:
    """Fluid-rigid hybrid physics inspired by Rimuru slime."""
    
    def __init__(self, water_molecules, bone_mesh, skeleton_rig):
        self.water_molecules = water_molecules
        self.bone_mesh = bone_mesh
        self.skeleton_rig = skeleton_rig
        self.surface_tension = SURFACE_TENSION
        self.viscosity = VISCOSITY
        self.elasticity = ELASTICITY
        self.cohesion = COHESION
        self.suspension_force = SUSPENSION_FORCE
        self.suspension_stiffness = 0.5
        
    def update(self, dt):
        """Update fluid-rigid hybrid physics."""
        self._apply_suspension()
        self._apply_intermolecular_forces()
        self._apply_fluid_dynamics()
        self._apply_rigid_constraints()
        
        for mol in self.water_molecules:
            mol.update(dt)
        
        bone_positions = [bone['position'] for bone in self.bone_mesh.bones]
        self.bone_mesh.update_physics(dt)
        self.skeleton_rig.update_skeleton(bone_positions)
        self.skeleton_rig.apply_constraints()
    
    def _apply_suspension(self):
        """Apply suspension forces to keep molecules suspended."""
        for mol in self.water_molecules:
            mol.apply_force(self.suspension_force * OXYGEN_MASS * 2)
            displacement = mol.position - mol.get_center_of_mass()
            mol.apply_force(-self.suspension_stiffness * displacement)
    
    def _apply_intermolecular_forces(self):
        """Apply forces between water molecules."""
        for i, mol1 in enumerate(self.water_molecules):
            for j, mol2 in enumerate(self.water_molecules[i+1:], i+1):
                direction = mol2.position - mol1.position
                distance = np.linalg.norm(direction)
                
                if distance < 3.0 and distance > 0.5:
                    direction = direction / distance
                    attraction = -self.cohesion / (distance**2)
                    repulsion = 2.0 / (distance**3)
                    total_force = (attraction + repulsion) * direction
                    mol1.apply_force(total_force)
                    mol2.apply_force(-total_force)
    
    def _apply_fluid_dynamics(self):
        """Apply fluid dynamics for slime-like behavior."""
        for mol in self.water_molecules:
            mol.apply_force(-self.viscosity * mol.velocity)
            neighbors = self._get_neighbors(mol)
            if len(neighbors) > 0:
                avg_pos = np.mean([n.position for n in neighbors], axis=0)
                curvature = avg_pos - mol.position
                mol.apply_force(self.surface_tension * curvature)
    
    def _apply_rigid_constraints(self):
        """Apply rigid body constraints for structural integrity."""
        for mol in self.water_molecules:
            current_h1 = mol.hydrogen1_pos - mol.oxygen_pos
            current_h2 = mol.hydrogen2_pos - mol.oxygen_pos
            current_h1 = current_h1 / np.linalg.norm(current_h1)
            current_h2 = current_h2 / np.linalg.norm(current_h2)
            dot_product = np.dot(current_h1, current_h2)
            current_angle = np.arccos(np.clip(dot_product, -1, 1))
            angle_diff = WATER_BOND_ANGLE - current_angle
            correction = angle_diff * self.elasticity
            mol.apply_torque(np.array([0, 0, correction]))
    
    def _get_neighbors(self, molecule, radius=2.0):
        """Get neighboring molecules within radius."""
        neighbors = []
        for mol in self.water_molecules:
            if mol is not molecule:
                distance = np.linalg.norm(mol.position - molecule.position)
                if distance < radius:
                    neighbors.append(mol)
        return neighbors


# ─── Molecular Physics Engine ───────────────────────────────────────────────────

class MolecularPhysicsEngine:
    """
    Main molecular physics engine integrated into CRISPR-ASI.
    Runs continuously as a background process, managing molecular simulation
    and providing physics-based knowledge to the ASI graph.
    """
    
    def __init__(self, obj_file_path: Optional[Path] = None, num_molecules: int = 100):
        self.obj_file_path = obj_file_path
        self.num_molecules = num_molecules
        self.mesh = None
        self.mesh_points = None
        
        # Physics components
        self.water_molecules = []
        self.topology = None
        self.bone_mesh = None
        self.skeleton_rig = None
        self.physics = None
        
        # Energy concentration system
        self.energy_system = EnergyConcentrationSystem(num_connectors=12)
        
        # Engine state
        self.running = False
        self.thread = None
        self.dt = 0.01
        self.step_count = 0
        
        # Knowledge graph integration
        self.knowledge_callbacks = []
        
        # Load mesh if provided
        if obj_file_path and obj_file_path.exists():
            self._load_mesh(obj_file_path)
            self._initialize_simulation()
    
    def _load_mesh(self, obj_file_path: Path):
        """Load 3D mesh from file."""
        try:
            self.mesh = trimesh.load(str(obj_file_path))
            self.mesh_points = np.array(self.mesh.vertices)
            logger.info(f"Loaded mesh with {len(self.mesh_points)} vertices")
        except Exception as e:
            logger.error(f"Failed to load mesh: {e}")
            self.mesh_points = np.random.rand(1000, 3)  # Fallback
    
    def _initialize_simulation(self):
        """Initialize molecular physics simulation."""
        if self.mesh_points is None:
            self.mesh_points = np.random.rand(1000, 3)
        
        # Initialize water molecules
        indices = np.random.choice(len(self.mesh_points), self.num_molecules, replace=False)
        for idx in indices:
            position = self.mesh_points[idx]
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            rotation = np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1]
            ])
            molecule = WaterMolecule(position, rotation)
            self.water_molecules.append(molecule)
        
        # Initialize topology and bone mesh
        self.topology = LidarPointTopology(self.mesh_points)
        self.bone_mesh = BoneMesh(self.topology)
        self.skeleton_rig = InvisibleSkeletonRig(self.bone_mesh, self.water_molecules)
        self.physics = FluidRigidHybridPhysics(self.water_molecules, self.bone_mesh, self.skeleton_rig)
        
        logger.info(f"Initialized simulation with {len(self.water_molecules)} molecules")
    
    def start(self):
        """Start the molecular physics engine in background thread."""
        if self.running:
            logger.warning("Molecular physics engine already running")
            return
        
        self.running = True
        # Start energy concentration system
        self.energy_system.start()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Molecular physics engine started with energy concentration")
    
    def stop(self):
        """Stop the molecular physics engine."""
        self.running = False
        self.energy_system.stop()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Molecular physics engine stopped")
    
    def _run_loop(self):
        """Main physics simulation loop."""
        while self.running:
            try:
                self.physics.update(self.dt)
                self.step_count += 1
                
                # Integrate energy concentration
                self._integrate_energy_concentration()
                
                # Update knowledge graph periodically
                if self.step_count % 100 == 0:
                    self._update_knowledge_graph()
                
                # Control simulation speed
                time.sleep(self.dt)
            except Exception as e:
                logger.error(f"Physics simulation error: {e}")
                self.running = False
    
    def _update_knowledge_graph(self):
        """Update knowledge graph with current molecular state."""
        state = self.get_state()
        for callback in self.knowledge_callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error(f"Knowledge callback error: {e}")
    
    def _integrate_energy_concentration(self):
        """Integrate energy concentration with molecular physics."""
        # Get molecule positions and velocities
        positions = [mol.position for mol in self.water_molecules]
        velocities = [mol.velocity for mol in self.water_molecules]
        
        # Set connector focus pattern based on molecular distribution
        if len(positions) > 0:
            center = np.mean(positions, axis=0)
            distances = np.linalg.norm(np.array(positions) - center, axis=1)
            normalized_distances = distances / (np.max(distances) + 1e-10)
            focus_pattern = 1.0 - normalized_distances[:12]  # Focus on center molecules
            self.energy_system.set_focus_pattern(focus_pattern)
        
        # Trap energy in molecules periodically
        if self.step_count % 50 == 0 and len(self.water_molecules) > 0:
            for i, mol in enumerate(self.water_molecules):
                # Calculate energy based on kinetic energy
                kinetic_energy = 0.5 * OXYGEN_MASS * np.linalg.norm(mol.velocity) ** 2

                if kinetic_energy > 1e-20:  # Minimum threshold
                    self.energy_system.trap_molecular_energy(
                        str(i), kinetic_energy, mol.position, mol.velocity
                    )
        
        # Spectrum->celestial routing intensification (seed->molecule great-circle hops)
        if self.step_count % 100 == 0 and len(self.water_molecules) > 0:
            positions_arr = np.array([mol.position for mol in self.water_molecules], dtype=np.float64)
            center = np.mean(positions_arr, axis=0)
            dists = np.linalg.norm(positions_arr - center, axis=1)
            denom = (np.max(dists) + 1e-12)
            density_score = 1.0 - (dists / denom)
            top_seed_count = min(12, len(self.water_molecules))
            seed_indices = np.argpartition(density_score, -top_seed_count)[-top_seed_count:]
            seeds = []
            spectrum_range = self.energy_system.spectrum_concentrator.active_range
            efficiency = self.energy_system.spectrum_concentrator.get_spectrum_efficiency(spectrum_range)
            for si in seed_indices:
                seeds.append({
                    'seed_id': f'seed_{int(si)}_{self.step_count}',
                    'pos': positions_arr[int(si)],
                    'strength': float(max(0.0, density_score[int(si)]) * efficiency),
                })

            molecule_positions = [np.asarray(p, dtype=np.float64) for p in positions_arr.tolist()]
            from engine.core.spectrum_routing import SpectrumSeed
            spectrum_seeds = [SpectrumSeed(**s) for s in seeds]

            self.energy_system.intensify_celestial_routing(
                seeds=spectrum_seeds,
                molecule_positions=molecule_positions,
                spectrum_range=spectrum_range,
                molecule_block_ids=[f"mol_{i}" for i in range(len(molecule_positions))],
                seed_strength_scale=1.0,
                energy_per_tick_scale=1.0,
                topk_per_seed=4,
                top_anchors=3,
            )

        # Replicate and disperse energy periodically
        if self.step_count % 200 == 0 and len(self.water_molecules) > 0:

            # Select random molecule as source
            source_idx = np.random.randint(0, len(self.water_molecules))
            source_mol = self.water_molecules[source_idx]
            
            # Replicate and disperse
            self.energy_system.replicate_and_disperse(
                str(source_idx), source_mol.position, positions
            )
    
    def register_knowledge_callback(self, callback: Callable[[dict], None]):
        """Register a callback to receive molecular state updates."""
        self.knowledge_callbacks.append(callback)
    
    def get_state(self) -> dict:
        """Get current molecular physics state."""
        base_state = {
            'step_count': self.step_count,
            'num_molecules': len(self.water_molecules),
            'num_bones': len(self.bone_mesh.bones) if self.bone_mesh else 0,
            'molecule_positions': [mol.position.tolist() for mol in self.water_molecules[:10]],  # Sample
            'bone_positions': [bone['position'].tolist() for bone in self.bone_mesh.bones[:10]] if self.bone_mesh else [],
            'collective_resonance': self._calculate_collective_resonance(),
            'fluidity': self.physics.fluidity if self.physics else 0.0,
            'cohesion': self.physics.cohesion if self.physics else 0.0,
        }
        
        # Add energy concentration state
        base_state['energy_concentration'] = self.energy_system.get_system_state()
        
        return base_state
    
    def _calculate_collective_resonance(self) -> float:
        """Calculate collective resonance from molecular state."""
        if not self.water_molecules:
            return 0.0
        
        # Calculate based on molecular alignment and cohesion
        positions = np.array([mol.position for mol in self.water_molecules])
        center = np.mean(positions, axis=0)
        distances = np.linalg.norm(positions - center, axis=1)
        coherence = 1.0 / (1.0 + np.std(distances))
        
        return float(coherence)
    
    def query_molecular_state(self, query: str) -> dict:
        """Query molecular physics state with natural language."""
        state = self.get_state()
        
        # Simple query processing
        query_lower = query.lower()
        
        if 'position' in query_lower or 'where' in query_lower:
            return {
                'type': 'position_query',
                'answer': f"Molecules distributed in 3D space with {state['num_molecules']} entities",
                'data': state['molecule_positions']
            }
        elif 'resonance' in query_lower or 'coherence' in query_lower:
            return {
                'type': 'resonance_query',
                'answer': f"Collective resonance: {state['collective_resonance']:.4f}",
                'data': state['collective_resonance']
            }
        elif 'fluid' in query_lower or 'slime' in query_lower:
            return {
                'type': 'fluidity_query',
                'answer': f"Fluidity: {state['fluidity']:.2f}, Cohesion: {state['cohesion']:.2f}",
                'data': {'fluidity': state['fluidity'], 'cohesion': state['cohesion']}
            }
        else:
            return {
                'type': 'general_query',
                'answer': f"Simulation running with {state['num_molecules']} molecules, step {state['step_count']}",
                'data': state
            }
    
    def index_molecular_knowledge(self, text: str, metadata: dict = None) -> str:
        """Index molecular knowledge into the physics engine."""
        # Create a molecular representation of the knowledge
        if len(self.water_molecules) < 200:  # Add molecules for knowledge
            position = np.random.rand(3)
            molecule = WaterMolecule(position)
            self.water_molecules.append(molecule)
            
            if self.physics:
                self.physics.water_molecules = self.water_molecules
        
        # Store metadata in molecular state
        if metadata:
            for i, mol in enumerate(self.water_molecules):
                if i < len(text.split()):
                    mol.knowledge_tag = text.split()[i]
        
        logger.info(f"Indexed molecular knowledge: {text[:50]}...")
        return f"molecular_hash_{hash(text) % 1000000}"
    
    def status(self) -> dict:
        """Get engine status."""
        base_status = {
            'running': self.running,
            'step_count': self.step_count,
            'num_molecules': len(self.water_molecules),
            'num_bones': len(self.bone_mesh.bones) if self.bone_mesh else 0,
            'collective_resonance': self._calculate_collective_resonance(),
            'mesh_loaded': self.mesh is not None,
            'thread_alive': self.thread.is_alive() if self.thread else False
        }
        
        # Add energy system status
        base_status['energy_system'] = self.energy_system.get_system_state()
        
        return base_status
    
    def __repr__(self) -> str:
        return (
            f"MolecularPhysicsEngine(running={self.running}, "
            f"molecules={len(self.water_molecules)}, "
            f"resonance={self._calculate_collective_resonance():.4f})"
        )
