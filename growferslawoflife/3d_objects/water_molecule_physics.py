"""
Water Molecule Physics Simulation System
Implements suspended water molecule with internal bone rig, lidar-point topology,
and fluid-rigid hybrid physics inspired by Rimuru slime from Tensura.
"""

import numpy as np
import trimesh
import open3d as o3d
import networkx as nx
from scipy.spatial import KDTree
from scipy.optimize import minimize
import pybullet as p
import time


class WaterMolecule:
    """Represents a single water molecule (H2O) with realistic physics."""
    
    def __init__(self, position, orientation=None):
        self.position = np.array(position, dtype=np.float64)
        
        # Water molecule geometry: H-O-H angle ~104.5 degrees, O-H bond length ~0.96 Å
        self.bond_length = 0.96  # Angstroms
        self.bond_angle = np.radians(104.5)
        
        # Atomic masses (atomic mass units)
        self.mass_oxygen = 15.999
        self.mass_hydrogen = 1.008
        
        # Initialize atomic positions
        self.oxygen_pos = self.position.copy()
        self.hydrogen1_pos, self.hydrogen2_pos = self._calculate_hydrogen_positions(orientation)
        
        # Velocities
        self.velocity = np.zeros(3)
        self.angular_velocity = np.zeros(3)
        
        # Forces
        self.force = np.zeros(3)
        self.torque = np.zeros(3)
        
    def _calculate_hydrogen_positions(self, orientation):
        """Calculate hydrogen positions based on oxygen position and orientation."""
        if orientation is None:
            # Default orientation in xy-plane
            h1 = self.oxygen_pos + np.array([
                self.bond_length * np.cos(self.bond_angle/2),
                self.bond_length * np.sin(self.bond_angle/2),
                0
            ])
            h2 = self.oxygen_pos + np.array([
                self.bond_length * np.cos(-self.bond_angle/2),
                self.bond_length * np.sin(-self.bond_angle/2),
                0
            ])
        else:
            # Apply orientation rotation
            rotation_matrix = orientation
            h1_local = np.array([
                self.bond_length * np.cos(self.bond_angle/2),
                self.bond_length * np.sin(self.bond_angle/2),
                0
            ])
            h2_local = np.array([
                self.bond_length * np.cos(-self.bond_angle/2),
                self.bond_length * np.sin(-self.bond_angle/2),
                0
            ])
            h1 = self.oxygen_pos + rotation_matrix @ h1_local
            h2 = self.oxygen_pos + rotation_matrix @ h2_local
            
        return h1, h2
    
    def get_center_of_mass(self):
        """Calculate center of mass of the molecule."""
        total_mass = self.mass_oxygen + 2 * self.mass_hydrogen
        com = (self.mass_oxygen * self.oxygen_pos + 
               self.mass_hydrogen * self.hydrogen1_pos + 
               self.mass_hydrogen * self.hydrogen2_pos) / total_mass
        return com
    
    def apply_force(self, force):
        """Apply external force to the molecule."""
        self.force += np.array(force)
        
    def apply_torque(self, torque):
        """Apply external torque to the molecule."""
        self.torque += np.array(torque)
        
    def update(self, dt):
        """Update molecule state using Verlet integration."""
        total_mass = self.mass_oxygen + 2 * self.mass_hydrogen
        
        # Update velocity
        acceleration = self.force / total_mass
        self.velocity += acceleration * dt
        
        # Update position
        self.position += self.velocity * dt
        
        # Update angular velocity (simplified)
        moment_of_inertia = self._calculate_moment_of_inertia()
        angular_acceleration = self.torque / moment_of_inertia
        self.angular_velocity += angular_acceleration * dt
        
        # Reset forces
        self.force = np.zeros(3)
        self.torque = np.zeros(3)
        
    def _calculate_moment_of_inertia(self):
        """Calculate approximate moment of inertia."""
        # Simplified calculation treating molecule as point masses
        r1 = np.linalg.norm(self.hydrogen1_pos - self.oxygen_pos)
        r2 = np.linalg.norm(self.hydrogen2_pos - self.oxygen_pos)
        I = (self.mass_hydrogen * r1**2 + self.mass_hydrogen * r2**2)
        return I


class LidarPointTopology:
    """Treats internal geometry as lidar points for bone mesh connection."""
    
    def __init__(self, mesh_points, num_points=1000):
        self.original_points = mesh_points
        self.num_points = num_points
        
        # Sample points from mesh surface
        self.sampled_points = self._sample_points()
        
        # Build KD-tree for spatial queries
        self.kdtree = KDTree(self.sampled_points)
        
        # Build connectivity graph
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
            
        # Connect nearby points
        for i in range(len(self.sampled_points)):
            distances, indices = self.kdtree.query(self.sampled_points[i], k=10)
            for j, dist in zip(indices[1:], distances[1:]):  # Skip self
                if dist < radius:
                    graph.add_edge(i, j, weight=dist)
                    
        return graph
    
    def get_nearest_neighbors(self, point, k=5):
        """Get k nearest neighbors to a given point."""
        distances, indices = self.kdtree.query(point, k=k)
        return indices, distances
    
    def get_path_between_points(self, start_idx, end_idx):
        """Find shortest path between two points in the topology."""
        try:
            path = nx.shortest_path(self.graph, start_idx, end_idx, weight='weight')
            return [self.sampled_points[i] for i in path]
        except nx.NetworkXNoPath:
            return None


class BoneMesh:
    """Internal bone mesh composed of water molecule composition, rigid but fluid."""
    
    def __init__(self, topology, num_bones=50):
        self.topology = topology
        self.num_bones = num_bones
        
        # Bone properties (water molecule composition)
        self.bones = []
        self._initialize_bones()
        
        # Physics properties
        self.stiffness = 0.8  # Rigid but with some flexibility
        self.damping = 0.3
        self.fluidity = 0.5  # Fluid-like behavior
        
    def _initialize_bones(self):
        """Initialize bones based on topology."""
        # Select key points from topology as bone anchors
        anchor_indices = np.linspace(0, len(self.topology.sampled_points) - 1, 
                                    self.num_bones, dtype=int)
        
        for i, idx in enumerate(anchor_indices):
            bone = {
                'anchor_idx': idx,
                'position': self.topology.sampled_points[idx].copy(),
                'velocity': np.zeros(3),
                'connected_bones': [],
                'water_composition': True  # Made of water molecules
            }
            self.bones.append(bone)
        
        # Connect bones based on topology
        for i in range(len(self.bones)):
            for j in range(i + 1, len(self.bones)):
                dist = np.linalg.norm(self.bones[i]['position'] - self.bones[j]['position'])
                if dist < 0.5:  # Connection threshold
                    self.bones[i]['connected_bones'].append(j)
                    self.bones[j]['connected_bones'].append(i)
    
    def update_physics(self, dt, external_forces=None):
        """Update bone physics with fluid-rigid hybrid behavior."""
        if external_forces is None:
            external_forces = []
            
        for i, bone in enumerate(self.bones):
            # Calculate spring forces from connected bones
            spring_force = np.zeros(3)
            for connected_idx in bone['connected_bones']:
                other_bone = self.bones[connected_idx]
                direction = other_bone['position'] - bone['position']
                distance = np.linalg.norm(direction)
                if distance > 0:
                    direction = direction / distance
                    # Spring force (Hooke's law with fluidity)
                    force_mag = self.stiffness * distance * (1 - self.fluidity)
                    spring_force += force_mag * direction
            
            # Apply damping
            damping_force = -self.damping * bone['velocity']
            
            # Apply external forces
            total_force = spring_force + damping_force
            for ext_force in external_forces:
                total_force += ext_force
            
            # Update velocity and position
            bone['velocity'] += total_force * dt
            bone['position'] += bone['velocity'] * dt
            
            # Apply fluid-like smoothing
            self._apply_fluid_smoothing(i)
    
    def _apply_fluid_smoothing(self, bone_idx):
        """Apply fluid-like smoothing to bone movement."""
        bone = self.bones[bone_idx]
        if bone['connected_bones']:
            # Average position with neighbors for fluid behavior
            avg_pos = np.zeros(3)
            for neighbor_idx in bone['connected_bones']:
                avg_pos += self.bones[neighbor_idx]['position']
            avg_pos /= len(bone['connected_bones'])
            
            # Blend current position with average
            bone['position'] = (1 - self.fluidity * 0.1) * bone['position'] + \
                              (self.fluidity * 0.1) * avg_pos


class InvisibleSkeletonRig:
    """Invisible skeleton rig made of oxygen/water, maintains contact and adjustability."""
    
    def __init__(self, bone_mesh, water_molecules):
        self.bone_mesh = bone_mesh
        self.water_molecules = water_molecules
        
        # Skeleton properties (invisible, oxygen/water based)
        self.skeleton_nodes = []
        self.skeleton_edges = []
        self.invisible = True
        self.composition = 'oxygen_water'  # Made of oxygen and water
        
        self._build_skeleton()
        
    def _build_skeleton(self):
        """Build invisible skeleton from bone mesh."""
        # Use bone mesh anchors as skeleton nodes
        for bone in self.bone_mesh.bones:
            node = {
                'position': bone['position'].copy(),
                'type': 'oxygen' if np.random.random() > 0.5 else 'water',
                'connections': []
            }
            self.skeleton_nodes.append(node)
        
        # Create edges based on bone connections
        for i, bone in enumerate(self.bone_mesh.bones):
            for connected_idx in bone['connected_bones']:
                if i < connected_idx:  # Avoid duplicates
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
        # Ensure skeleton maintains contact with water molecules
        for node in self.skeleton_nodes:
            # Find nearest water molecule
            nearest_mol = min(self.water_molecules, 
                            key=lambda mol: np.linalg.norm(mol.position - node['position']))
            
            # Apply gentle attraction to maintain contact
            direction = nearest_mol.position - node['position']
            distance = np.linalg.norm(direction)
            if distance > 0:
                direction = direction / distance
                # Gentle constraint force
                constraint_strength = 0.1
                node['position'] += direction * distance * constraint_strength


class FluidRigidHybridPhysics:
    """Fluid-rigid hybrid physics inspired by Rimuru slime."""
    
    def __init__(self, water_molecules, bone_mesh, skeleton_rig):
        self.water_molecules = water_molecules
        self.bone_mesh = bone_mesh
        self.skeleton_rig = skeleton_rig
        
        # Physics parameters
        self.surface_tension = 0.72  # Water surface tension
        self.viscosity = 0.001  # Water viscosity
        self.elasticity = 0.3  # Slime-like elasticity
        self.cohesion = 0.8  # Molecular cohesion
        
        # Suspended state parameters
        self.suspension_force = np.array([0, 9.81, 0])  # Counteract gravity
        self.suspension_stiffness = 0.5
        
    def update(self, dt):
        """Update fluid-rigid hybrid physics."""
        # Apply suspension forces
        self._apply_suspension()
        
        # Apply intermolecular forces
        self._apply_intermolecular_forces()
        
        # Apply fluid dynamics
        self._apply_fluid_dynamics()
        
        # Apply rigid body constraints
        self._apply_rigid_constraints()
        
        # Update all components
        for mol in self.water_molecules:
            mol.update(dt)
        
        bone_positions = [bone['position'] for bone in self.bone_mesh.bones]
        self.bone_mesh.update_physics(dt)
        self.skeleton_rig.update_skeleton(bone_positions)
        self.skeleton_rig.apply_constraints()
    
    def _apply_suspension(self):
        """Apply suspension forces to keep molecules suspended."""
        for mol in self.water_molecules:
            # Counteract gravity with suspension force
            mol.apply_force(self.suspension_force * mol.mass_oxygen * 2)
            
            # Add restoring force to maintain shape
            displacement = mol.position - mol.get_center_of_mass()
            mol.apply_force(-self.suspension_stiffness * displacement)
    
    def _apply_intermolecular_forces(self):
        """Apply forces between water molecules."""
        for i, mol1 in enumerate(self.water_molecules):
            for j, mol2 in enumerate(self.water_molecules[i+1:], i+1):
                direction = mol2.position - mol1.position
                distance = np.linalg.norm(direction)
                
                if distance < 3.0 and distance > 0.5:  # Interaction range
                    direction = direction / distance
                    
                    # Van der Waals-like attraction
                    attraction = -self.cohesion / (distance**2)
                    
                    # Repulsion at close range
                    repulsion = 2.0 / (distance**3)
                    
                    total_force = (attraction + repulsion) * direction
                    mol1.apply_force(total_force)
                    mol2.apply_force(-total_force)
    
    def _apply_fluid_dynamics(self):
        """Apply fluid dynamics for slime-like behavior."""
        for mol in self.water_molecules:
            # Viscous damping
            mol.apply_force(-self.viscosity * mol.velocity)
            
            # Surface tension effects
            neighbors = self._get_neighbors(mol)
            if len(neighbors) > 0:
                # Calculate local curvature approximation
                avg_pos = np.mean([n.position for n in neighbors], axis=0)
                curvature = avg_pos - mol.position
                mol.apply_force(self.surface_tension * curvature)
    
    def _apply_rigid_constraints(self):
        """Apply rigid body constraints for structural integrity."""
        # Maintain water molecule shape constraints
        for mol in self.water_molecules:
            # Constrain H-O-H bond angle
            current_h1 = mol.hydrogen1_pos - mol.oxygen_pos
            current_h2 = mol.hydrogen2_pos - mol.oxygen_pos
            
            # Normalize
            current_h1 = current_h1 / np.linalg.norm(current_h1)
            current_h2 = current_h2 / np.linalg.norm(current_h2)
            
            # Calculate current angle
            dot_product = np.dot(current_h1, current_h2)
            current_angle = np.arccos(np.clip(dot_product, -1, 1))
            
            # Apply corrective torque
            angle_diff = mol.bond_angle - current_angle
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


class WaterMoleculeSimulation:
    """Main simulation class integrating all components."""
    
    def __init__(self, obj_file_path, num_molecules=100):
        # Load mesh
        self.mesh = trimesh.load(obj_file_path)
        self.mesh_points = np.array(self.mesh.vertices)
        
        # Initialize components
        self.water_molecules = self._initialize_water_molecules(num_molecules)
        self.topology = LidarPointTopology(self.mesh_points)
        self.bone_mesh = BoneMesh(self.topology)
        self.skeleton_rig = InvisibleSkeletonRig(self.bone_mesh, self.water_molecules)
        self.physics = FluidRigidHybridPhysics(self.water_molecules, self.bone_mesh, self.skeleton_rig)
        
        # PyBullet setup for physics simulation
        self.physics_client = p.connect(p.GUI)
        p.setGravity(0, -9.81, 0)
        
    def _initialize_water_molecules(self, num_molecules):
        """Initialize water molecules distributed in the mesh."""
        molecules = []
        
        # Sample points from mesh for molecule positions
        indices = np.random.choice(len(self.mesh_points), num_molecules, replace=False)
        
        for idx in indices:
            position = self.mesh_points[idx]
            # Random orientation
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            
            # Create rotation matrix
            rotation = np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1]
            ])
            
            molecule = WaterMolecule(position, rotation)
            molecules.append(molecule)
            
        return molecules
    
    def run_simulation(self, dt=0.01, steps=1000):
        """Run the simulation."""
        for step in range(steps):
            # Update physics
            self.physics.update(dt)
            
            # Step pybullet simulation
            p.stepSimulation()
            
            # Visualization (optional)
            if step % 10 == 0:
                self._visualize()
            
            time.sleep(dt/1000)  # Slow down for visualization
    
    def _visualize(self):
        """Visualize the current state."""
        # Update mesh vertices based on bone mesh positions
        new_vertices = []
        for bone in self.bone_mesh.bones:
            new_vertices.append(bone['position'])
        
        # Update mesh (simplified)
        if len(new_vertices) == len(self.mesh.vertices):
            self.mesh.vertices = new_vertices
        
        # Print status
        print(f"Simulation step - Molecules: {len(self.water_molecules)}, "
              f"Bones: {len(self.bone_mesh.bones)}")
    
    def cleanup(self):
        """Clean up resources."""
        p.disconnect()


if __name__ == "__main__":
    # Example usage
    obj_file = "liquid_sphere.obj"
    sim = WaterMoleculeSimulation(obj_file, num_molecules=50)
    
    try:
        sim.run_simulation(dt=0.01, steps=100)
    finally:
        sim.cleanup()
