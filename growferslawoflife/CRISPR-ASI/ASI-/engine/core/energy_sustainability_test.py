"""
energy_sustainability_test.py — Energy Sustainability Testing System
Tests energy concentration sustainability via spectrum ranges with attention-based
concentration while preserving molecular structure using weight equivalent validation.
"""

import numpy as np
import logging
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import threading

from engine.core.energy_concentration import (
    EnergyConcentrationSystem, SpectrumRange, EnergyState, StateTracker
)
from engine.core.molecular_physics import WaterMolecule, FluidRigidHybridPhysics

logger = logging.getLogger("light-asi.energy_sustainability_test")


# ─── Test Configuration ─────────────────────────────────────────────────────────

@dataclass
class TestConfig:
    """Configuration for energy sustainability tests."""
    num_molecules: int = 50
    test_duration: float = 10.0  # seconds
    spectrum_ranges: List[SpectrumRange] = field(default_factory=lambda: list(SpectrumRange))
    energy_input_range: Tuple[float, float] = (1e-18, 1e-15)  # Joules
    attention_threshold: float = 0.7  # Minimum attention for concentration
    structure_preservation_threshold: float = 0.95  # Minimum structure integrity
    max_energy_density: float = 1e12  # Maximum energy density before structure damage


# ─── Molecular Structure Integrity Metrics ─────────────────────────────────────

@dataclass
class StructureMetrics:
    """Metrics for molecular structure integrity."""
    bond_angle_deviation: float  # Deviation from ideal 104.5°
    bond_length_deviation: float  # Deviation from ideal 0.96Å
    molecular_coherence: float  # Overall coherence (0-1)
    structure_integrity: float  # Overall integrity (0-1)
    energy_stress: float  # Energy-induced stress (0-1)
    
    def is_preserved(self, threshold: float = 0.95) -> bool:
        """Check if structure is preserved above threshold."""
        return self.structure_integrity >= threshold


class StructureValidator:
    """Validates molecular structure integrity during energy concentration."""
    
    def __init__(self, ideal_bond_angle: float = np.radians(104.5), 
                 ideal_bond_length: float = 0.96):
        self.ideal_bond_angle = ideal_bond_angle
        self.ideal_bond_length = ideal_bond_length
        
    def validate_molecule(self, molecule: WaterMolecule) -> StructureMetrics:
        """Validate individual molecule structure."""
        # Calculate bond angle deviation
        h1_vec = molecule.hydrogen1_pos - molecule.oxygen_pos
        h2_vec = molecule.hydrogen2_pos - molecule.oxygen_pos
        h1_vec = h1_vec / np.linalg.norm(h1_vec)
        h2_vec = h2_vec / np.linalg.norm(h2_vec)
        
        current_angle = np.arccos(np.clip(np.dot(h1_vec, h2_vec), -1, 1))
        angle_deviation = abs(current_angle - self.ideal_bond_angle)
        
        # Calculate bond length deviation
        h1_length = np.linalg.norm(molecule.hydrogen1_pos - molecule.oxygen_pos)
        h2_length = np.linalg.norm(molecule.hydrogen2_pos - molecule.oxygen_pos)
        length_deviation = (abs(h1_length - self.ideal_bond_length) + 
                           abs(h2_length - self.ideal_bond_length)) / 2
        
        # Calculate molecular coherence
        angle_coherence = 1.0 - (angle_deviation / np.pi)
        length_coherence = 1.0 - (length_deviation / 2.0)
        molecular_coherence = (angle_coherence + length_coherence) / 2
        
        # Calculate overall structure integrity
        structure_integrity = molecular_coherence
        
        # Calculate energy stress (based on velocity)
        energy_stress = min(np.linalg.norm(molecule.velocity) / 1e-5, 1.0)
        
        return StructureMetrics(
            bond_angle_deviation=angle_deviation,
            bond_length_deviation=length_deviation,
            molecular_coherence=molecular_coherence,
            structure_integrity=structure_integrity,
            energy_stress=energy_stress
        )
    
    def validate_system(self, molecules: List[WaterMolecule]) -> Dict:
        """Validate entire molecular system."""
        metrics = [self.validate_molecule(mol) for mol in molecules]
        
        avg_angle_deviation = np.mean([m.bond_angle_deviation for m in metrics])
        avg_length_deviation = np.mean([m.bond_length_deviation for m in metrics])
        avg_coherence = np.mean([m.molecular_coherence for m in metrics])
        avg_integrity = np.mean([m.structure_integrity for m in metrics])
        avg_stress = np.mean([m.energy_stress for m in metrics])
        
        preserved_count = sum(1 for m in metrics if m.is_preserved())
        preservation_rate = preserved_count / len(metrics)
        
        return {
            'avg_angle_deviation': avg_angle_deviation,
            'avg_length_deviation': avg_length_deviation,
            'avg_coherence': avg_coherence,
            'avg_integrity': avg_integrity,
            'avg_stress': avg_stress,
            'preservation_rate': preservation_rate,
            'total_molecules': len(molecules),
            'preserved_molecules': preserved_count
        }


# ─── Attention-Based Concentration ─────────────────────────────────────────────

class AttentionConcentrator:
    """Attention-based energy concentration focusing on specific molecular regions."""
    
    def __init__(self, num_attention_heads: int = 4):
        self.num_attention_heads = num_attention_heads
        self.attention_weights = np.zeros(num_attention_heads)
        self.attention_history: List[np.ndarray] = []
        
    def calculate_attention(self, molecule_positions: List[np.ndarray], 
                           energy_density: np.ndarray) -> np.ndarray:
        """Calculate attention weights based on energy density and position."""
        positions = np.array(molecule_positions)
        center = np.mean(positions, axis=0)
        
        # Calculate distances from center
        distances = np.linalg.norm(positions - center, axis=1)
        
        # Normalize distances
        if np.max(distances) > 0:
            normalized_distances = distances / np.max(distances)
        else:
            normalized_distances = distances
        
        # Attention: higher for molecules with higher energy density and closer to center
        attention = (1.0 - normalized_distances) * energy_density
        
        # Normalize attention to sum to 1
        if np.sum(attention) > 0:
            attention = attention / np.sum(attention)
        
        return attention
    
    def apply_attention_concentration(self, energy_system: EnergyConcentrationSystem,
                                     attention_weights: np.ndarray,
                                     target_range: SpectrumRange) -> float:
        """Apply attention-based energy concentration."""
        # Set focus pattern based on attention weights
        num_connectors = energy_system.connector_network.num_connectors
        if len(attention_weights) >= num_connectors:
            focus_pattern = attention_weights[:num_connectors]
        else:
            # Pad with zeros if not enough weights
            focus_pattern = np.pad(attention_weights, (0, num_connectors - len(attention_weights)))
        
        energy_system.set_focus_pattern(focus_pattern)
        
        # Calculate concentrated energy
        total_attention = np.sum(attention_weights)
        concentrated_energy = total_attention * 1e-15  # Base energy scale
        
        # Concentrate using spectrum range
        state_hash = energy_system.concentrate_from_spectrum(target_range, concentrated_energy)
        
        self.attention_history.append(attention_weights)
        if len(self.attention_history) > 1000:
            self.attention_history = self.attention_history[-500:]
        
        return concentrated_energy
    
    def get_attention_statistics(self) -> Dict:
        """Get attention statistics."""
        if not self.attention_history:
            return {'mean_attention': 0.0, 'std_attention': 0.0, 'max_attention': 0.0}
        
        all_attention = np.concatenate(self.attention_history)
        return {
            'mean_attention': np.mean(all_attention),
            'std_attention': np.std(all_attention),
            'max_attention': np.max(all_attention),
            'min_attention': np.min(all_attention),
            'history_size': len(self.attention_history)
        }


# ─── Spectrum Field Weight Equivalent Calculator ───────────────────────────────

class SpectrumWeightCalculator:
    """Calculates weight equivalent in spectrum field for energy sustainability."""
    
    def __init__(self):
        self.spectrum_weights: Dict[SpectrumRange, float] = {}
        self.weight_history: List[Dict] = []
        
    def calculate_spectrum_weight(self, spectrum_range: SpectrumRange, 
                                 energy: float) -> float:
        """Calculate weight equivalent for energy in spectrum field."""
        # Weight equivalent based on photon energy and spectrum range
        avg_wavelength = (spectrum_range.wavelength_min + spectrum_range.wavelength_max) / 2
        
        # Photon energy: E = hc/λ
        photon_energy = (6.626e-34 * 2.998e8) / avg_wavelength
        
        # Number of photons equivalent to input energy
        num_photons = energy / photon_energy if photon_energy > 0 else 0
        
        # Weight equivalent: m = E/c² (scaled by photon count)
        weight_equivalent = (energy / (2.998e8 ** 2)) * num_photons
        
        self.spectrum_weights[spectrum_range] = weight_equivalent
        self.weight_history.append({
            'spectrum_range': spectrum_range.name,
            'energy': energy,
            'weight_equivalent': weight_equivalent,
            'timestamp': time.time()
        })
        
        if len(self.weight_history) > 1000:
            self.weight_history = self.weight_history[-500:]
        
        return weight_equivalent
    
    def validate_weight_sustainability(self, spectrum_range: SpectrumRange,
                                    molecular_weight: float) -> bool:
        """Validate if weight equivalent is sustainable for molecular structure."""
        weight_equivalent = self.spectrum_weights.get(spectrum_range, 0.0)
        
        # Sustainability check: weight equivalent should not exceed molecular weight by factor of 10
        sustainability_ratio = weight_equivalent / (molecular_weight + 1e-30)
        
        return sustainability_ratio < 10.0
    
    def get_spectrum_sustainability_metrics(self) -> Dict:
        """Get sustainability metrics across spectrum ranges."""
        metrics = {}
        for spectrum_range, weight in self.spectrum_weights.items():
            metrics[spectrum_range.name] = {
                'weight_equivalent': weight,
                'sustainability': weight < 1e-25  # Threshold for sustainability
            }
        return metrics


# ─── Energy Sustainability Test System ─────────────────────────────────────────

class EnergySustainabilityTest:
    """
    Main test system for energy sustainability via spectrum ranges with
    attention-based concentration and molecular structure preservation.
    """
    
    def __init__(self, config: TestConfig):
        self.config = config
        
        # Initialize components
        self.energy_system = EnergyConcentrationSystem(num_connectors=12)
        self.structure_validator = StructureValidator()
        self.attention_concentrator = AttentionConcentrator()
        self.weight_calculator = SpectrumWeightCalculator()
        
        # Test state
        self.molecules: List[WaterMolecule] = []
        self.test_results: Dict = {}
        self.running = False
        self.thread = None
        
        # Initialize molecules
        self._initialize_molecules()
        
    def _initialize_molecules(self):
        """Initialize test molecules."""
        for i in range(self.config.num_molecules):
            position = np.random.rand(3) * 2.0 - 1.0  # Random position in [-1, 1]
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            rotation = np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1]
            ])
            molecule = WaterMolecule(position, rotation)
            self.molecules.append(molecule)
    
    def run_sustainability_test(self) -> Dict:
        """Run complete energy sustainability test."""
        logger.info("Starting energy sustainability test...")
        
        # Start energy system
        self.energy_system.start()
        
        # Test each spectrum range
        spectrum_results = {}
        
        for spectrum_range in self.config.spectrum_ranges:
            logger.info(f"Testing spectrum range: {spectrum_range.name}")
            result = self._test_spectrum_range(spectrum_range)
            spectrum_results[spectrum_range.name] = result
        
        # Stop energy system
        self.energy_system.stop()
        
        # Compile final results
        self.test_results = {
            'config': {
                'num_molecules': self.config.num_molecules,
                'test_duration': self.config.test_duration,
                'spectrum_ranges_tested': len(self.config.spectrum_ranges)
            },
            'spectrum_results': spectrum_results,
            'attention_stats': self.attention_concentrator.get_attention_statistics(),
            'spectrum_metrics': self.weight_calculator.get_spectrum_sustainability_metrics(),
            'overall_sustainability': self._calculate_overall_sustainability(spectrum_results)
        }
        
        logger.info("Energy sustainability test complete")
        return self.test_results
    
    def _test_spectrum_range(self, spectrum_range: SpectrumRange) -> Dict:
        """Test energy sustainability for a specific spectrum range."""
        start_time = time.time()
        test_steps = 0
        structure_integrity_history = []
        energy_retention_history = []
        
        while time.time() - start_time < self.config.test_duration:
            # Calculate attention weights
            positions = [mol.position for mol in self.molecules]
            energy_density = np.random.rand(len(positions)) * 1e-15  # Random energy density
            attention = self.attention_concentrator.calculate_attention(positions, energy_density)
            
            # Apply attention-based concentration
            input_energy = np.random.uniform(*self.config.energy_input_range)
            concentrated = self.attention_concentrator.apply_attention_concentration(
                self.energy_system, attention, spectrum_range
            )
            
            # Calculate weight equivalent
            weight_equivalent = self.weight_calculator.calculate_spectrum_weight(
                spectrum_range, concentrated
            )
            
            # Validate weight sustainability
            avg_molecular_weight = 15.999  # Oxygen mass
            sustainable = self.weight_calculator.validate_weight_sustainability(
                spectrum_range, avg_molecular_weight
            )
            
            # Validate structure integrity
            structure_metrics = self.structure_validator.validate_system(self.molecules)
            structure_integrity_history.append(structure_metrics['avg_integrity'])
            
            # Calculate energy retention
            energy_retention = concentrated / input_energy if input_energy > 0 else 0
            energy_retention_history.append(energy_retention)
            
            # Update molecules (simulate physics)
            for mol in self.molecules:
                mol.velocity += np.random.rand(3) * 1e-8  # Small random perturbation
                mol.position += mol.velocity * 0.01
            
            test_steps += 1
            time.sleep(0.01)  # Small delay
        
        # Calculate results
        avg_structure_integrity = np.mean(structure_integrity_history)
        avg_energy_retention = np.mean(energy_retention_history)
        min_structure_integrity = np.min(structure_integrity_history)
        
        # Determine if test passed
        structure_preserved = avg_structure_integrity >= self.config.structure_preservation_threshold
        energy_sustained = avg_energy_retention >= 0.5  # At least 50% retention
        
        return {
            'spectrum_range': spectrum_range.name,
            'test_steps': test_steps,
            'avg_structure_integrity': avg_structure_integrity,
            'min_structure_integrity': min_structure_integrity,
            'avg_energy_retention': avg_energy_retention,
            'structure_preserved': structure_preserved,
            'energy_sustained': energy_sustained,
            'test_passed': structure_preserved and energy_sustained,
            'weight_equivalent': self.weight_calculator.spectrum_weights.get(spectrum_range, 0.0)
        }
    
    def _calculate_overall_sustainability(self, spectrum_results: Dict) -> Dict:
        """Calculate overall sustainability metrics."""
        passed_tests = sum(1 for r in spectrum_results.values() if r['test_passed'])
        total_tests = len(spectrum_results)
        
        avg_integrity = np.mean([r['avg_structure_integrity'] for r in spectrum_results.values()])
        avg_retention = np.mean([r['avg_energy_retention'] for r in spectrum_results.values()])
        
        return {
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'avg_structure_integrity': avg_integrity,
            'avg_energy_retention': avg_retention,
            'overall_sustainable': avg_integrity >= self.config.structure_preservation_threshold and avg_retention >= 0.5
        }
    
    def generate_report(self) -> str:
        """Generate human-readable test report."""
        if not self.test_results:
            return "No test results available. Run test first."
        
        report = []
        report.append("=" * 80)
        report.append("ENERGY SUSTAINABILITY TEST REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Configuration
        config = self.test_results['config']
        report.append(f"Configuration:")
        report.append(f"  Molecules: {config['num_molecules']}")
        report.append(f"  Test Duration: {config['test_duration']}s")
        report.append(f"  Spectrum Ranges Tested: {config['spectrum_ranges_tested']}")
        report.append("")
        
        # Overall results
        overall = self.test_results['overall_sustainability']
        report.append("Overall Results:")
        report.append(f"  Passed Tests: {overall['passed_tests']}/{overall['total_tests']}")
        report.append(f"  Success Rate: {overall['success_rate']:.1%}")
        report.append(f"  Avg Structure Integrity: {overall['avg_structure_integrity']:.3f}")
        report.append(f"  Avg Energy Retention: {overall['avg_energy_retention']:.3f}")
        report.append(f"  Overall Sustainable: {overall['overall_sustainable']}")
        report.append("")
        
        # Spectrum-specific results
        report.append("Spectrum Range Results:")
        for name, result in self.test_results['spectrum_results'].items():
            status = "✓ PASS" if result['test_passed'] else "✗ FAIL"
            report.append(f"  {name:15s} {status}")
            report.append(f"    Structure Integrity: {result['avg_structure_integrity']:.3f}")
            report.append(f"    Energy Retention: {result['avg_energy_retention']:.3f}")
            report.append(f"    Weight Equivalent: {result['weight_equivalent']:.2e} kg")
            report.append("")
        
        # Attention statistics
        attention = self.test_results['attention_stats']
        report.append("Attention Statistics:")
        report.append(f"  Mean Attention: {attention['mean_attention']:.3f}")
        report.append(f"  Std Attention: {attention['std_attention']:.3f}")
        report.append(f"  Max Attention: {attention['max_attention']:.3f}")
        report.append("")
        
        # Spectrum metrics
        report.append("Spectrum Weight Metrics:")
        for name, metrics in self.test_results['spectrum_metrics'].items():
            sustainable = "✓" if metrics['sustainability'] else "✗"
            report.append(f"  {name:15s} {sustainable} Weight: {metrics['weight_equivalent']:.2e} kg")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


# ─── Quick Test Function ─────────────────────────────────────────────────────

def run_quick_sustainability_test() -> Dict:
    """Run a quick sustainability test with default configuration."""
    config = TestConfig(
        num_molecules=20,
        test_duration=5.0,
        spectrum_ranges=[SpectrumRange.VISIBLE, SpectrumRange.INFRARED, SpectrumRange.ULTRAVIOLET]
    )
    
    test_system = EnergySustainabilityTest(config)
    results = test_system.run_sustainability_test()
    
    print(test_system.generate_report())
    
    return results


if __name__ == "__main__":
    # Run quick test
    logging.basicConfig(level=logging.INFO)
    results = run_quick_sustainability_test()
