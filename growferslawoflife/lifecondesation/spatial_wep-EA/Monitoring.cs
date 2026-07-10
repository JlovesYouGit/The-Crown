using System;
using UnityEngine;

namespace ElectromagneticWeapon.Components
{
    using Core;

    public class EnergyMonitor : MonoBehaviour
    {
        public EnergyDensity CurrentEnergyDensity;
        public float TargetDensityThreshold = 4.0f;
        public float SamplingFrequency = 10000f; // 10 kHz

        [Header("State")]
        public int AccumulatedPhotons;
        public float PhotonEnergy = 0.5f; // Assumption for mass-equivalence calculation

        public event Action OnThresholdReached;

        private void Update()
        {
            float deltaTime = Time.deltaTime;
            
            // Simulate photon accumulation (this would be driven by the RearSpinner in a real system)
            if (GetComponent<RearSpinnerController>().IsRotating)
            {
                // Simple linear accumulation for simulation purposes
                AccumulatedPhotons += (int)(1000 * deltaTime);
            }

            // Calculate density
            float densityValue = PhysicsEngine.CalculateEnergyDensity(AccumulatedPhotons, PhotonEnergy);
            
            CurrentEnergyDensity.Value = densityValue;
            CurrentEnergyDensity.PhotonCount = AccumulatedPhotons;
            CurrentEnergyDensity.Status = densityValue >= TargetDensityThreshold ? ThresholdStatus.AT_THRESHOLD : ThresholdStatus.BELOW_THRESHOLD;

            if (CurrentEnergyDensity.Status == ThresholdStatus.AT_THRESHOLD && OnThresholdReached != null)
            {
                OnThresholdReached.Invoke();
            }
        }

        public void ResetMonitor()
        {
            AccumulatedPhotons = 0;
            CurrentEnergyDensity.Value = 0;
            CurrentEnergyDensity.Status = ThresholdStatus.BELOW_THRESHOLD;
        }

        public bool CheckRevolutionRatio(float ω, float k_s)
        {
            return PhysicsEngine.IsReleaseThresholdMet(CurrentEnergyDensity.Value, ω, k_s, PhysicsEngine.ELECTRODE_RADIUS);
        }
    }
}
