using System;
using System.Collections.Generic;
using UnityEngine;

namespace ElectromagneticWeapon.Quantum
{
    public class QuantumStateResizer : MonoBehaviour
    {
        private List<QuantumElectrode> _electrodes = new List<QuantumElectrode>();
        private QSRState _state;
        
        public QSRState State => _state;
        public IReadOnlyList<QuantumElectrode> Electrodes => _electrodes;

        public void AddElectrode(Vector3 position, double charge, double mass, double initialQSize, double frequency)
        {
            _electrodes.Add(new QuantumElectrode(position, charge, mass, initialQSize, frequency));
            Debug.Log($"QSR: Electrode added at {position} (Charge: {charge}, Freq: {frequency}Hz)");
        }

        public void TriggerUpforceMoment(float duration)
        {
            _state.UpforceTriggered = true;
            Debug.Log($"QSR: Upforce Moment Triggered for {duration}s");
            // In a real Unity implementation, this would be a Coroutine to auto-reset.
        }

        public void SimulateStep(double dt)
        {
            for (int i = 0; i < _electrodes.Count; i++)
            {
                var e = _electrodes[i];
                
                // 1. Calculate External Forces (Gravity + EM)
                Vector3 fTotal = CalculateNetForce(e, i);

                // 2. Upforce Factor
                double freqFactor = e.Frequency / 1e14; // Arbitrary normalization
                double compressionFactor = 1.0 / (e.QuantumStateSize + 1e-20);
                double upforceMultiplier = _state.UpforceTriggered ? 1.618 : 1.0; // Golden ratio boost during trigger
                
                double fUp = fTotal.magnitude * freqFactor * compressionFactor * upforceMultiplier;

                // 3. Quantum State Evolution (dq/dt)
                // dq/dt = α × |F_up| × q × time_dilation_factor
                double timeDilation = 1.0 / Math.Sqrt(1.0 - Math.Min(0.99, (e.Velocity.sqrMagnitude / Math.Pow(QuantumConstants.C, 2))));
                double dqVal = QuantumConstants.ALPHA * fUp * e.QuantumStateSize * timeDilation * dt;
                
                e.QuantumStateSize += dqVal;

                // 4. Singularity Transition (Decompression Rate)
                // decompression_rate = 10⁻³ × exp(-singularity_parameter × 10)
                _state.DecompressionRate = 1e-3 * Math.Exp(-_state.SingularityParameter * 10.0);
                
                // Update Energy Density
                e.EnergyDensity = (e.Mass * Math.Pow(QuantumConstants.C, 2)) / (Math.PI * Math.Pow(e.QuantumStateSize, 2));

                _electrodes[i] = e;
            }

            _state.StepCount++;
        }

        public void RunSimulation(int steps, double dt)
        {
            for (int i = 0; i < steps; i++)
            {
                SimulateStep(dt);
            }
            Debug.Log($"QSR: Simulation run complete ({steps} steps).");
        }

        private Vector3 CalculateNetForce(QuantumElectrode target, int index)
        {
            Vector3 force = Vector3.zero;
            
            for (int i = 0; i < _electrodes.Count; i++)
            {
                if (i == index) continue;
                
                var other = _electrodes[i];
                Vector3 rVec = other.Position - target.Position;
                float r = rVec.magnitude;
                if (r < 1e-15) r = 1e-15f; // Prevent singularity at zero distance
                Vector3 rHat = rVec.normalized;

                // Coulomb Force
                double fElectric = (QuantumConstants.K_E * target.Charge * other.Charge) / (r * r);
                // Gravity Force
                double fGravity = (QuantumConstants.G * target.Mass * other.Mass) / (r * r);

                force += rHat * (float)(fElectric + fGravity);
            }

            return force;
        }

        public void VisualizeSystem()
        {
            // Implementation-specific: in CLI we log, in Unity we gizmo
            Debug.Log($"[QSR VIEW] Step: {_state.StepCount} | Decompression: {_state.DecompressionRate}");
            foreach (var e in _electrodes)
            {
                Debug.Log($" - Electrode: Size={e.QuantumStateSize:E2}, Density={e.EnergyDensity:E2}");
            }
        }
    }
}
