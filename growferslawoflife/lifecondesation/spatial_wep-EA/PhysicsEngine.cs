using System;
using UnityEngine;

namespace ElectromagneticWeapon.Core
{
    public static class PhysicsEngine
    {
        public const float GOLDEN_RATIO = 1.618033988749f;
        public const float PILLAR_GAP = 0.0618f; // φ⁻¹ * 0.1
        public const float ELECTRODE_RADIUS = 0.0618f;
        public const float TRAP_HEIGHT = 0.15f;
        public const float NM_INERTIA = 5555f;
        public const float AIR_DENSITY = 1.225f; // Sea level
        public const float IONIZATION_ENERGY_AIR = 14.53e6f; // J/m³ (approximate for dry air)
        public const float STEEL_DENSITY = 7850f; // kg/m³
        public const float STEEL_SPECIFIC_HEAT = 490f; // J/(kg·K)
        public const float STEEL_MELTING_POINT = 1811f; // Kelvin
        public const float ION_VELOCITY_TARGET = 2.5e6f;
        public const float BATTERY_NOMINAL_VOLTAGE = 48f;
        public const float K_S_THRESHOLD = 123.5f;

        /// <summary>
        /// Calculates the released energy based on the EA Release Formula:
        /// E = (ρ^(ω/k_s)) * (π*r/24) * m² * φ
        /// </summary>
        public static float CalculateEAReleaseEnergy(float ρ, float ω, float k_s, float r, float m_squared)
        {
            float term1 = Mathf.Pow(ρ, ω / k_s);
            float term2 = (Mathf.PI * r) / 24f;
            return term1 * term2 * m_squared * GOLDEN_RATIO;
        }

        /// <summary>
        /// Checks if the threshold for release is met.
        /// (ρ ≥ 4) AND (ω/k_s > 24/(π*r))
        /// </summary>
        public static bool IsReleaseThresholdMet(float ρ, float ω, float k_s, float r)
        {
            if (ρ < 4) return false;
            
            float ratio = ω / k_s;
            float thresholdValue = 24f / (Mathf.PI * r);
            
            return ratio > thresholdValue;
        }

        /// <summary>
        /// Calculates the effective electromagnetic field strength:
        /// B_effective = 0.5T * φ² = 1.309T
        /// </summary>
        public static float CalculateEffectiveEMField()
        {
            return 0.5f * Mathf.Pow(GOLDEN_RATIO, 2);
        }

        /// <summary>
        /// Calculates the radial suction force of the air vortex:
        /// F_suction = (nm_inertia * ρ_air * ω²) / r_vortex
        /// </summary>
        public static float CalculateVortexSuctionForce(float ω)
        {
            return (NM_INERTIA * AIR_DENSITY * Mathf.Pow(ω, 2)) / ELECTRODE_RADIUS;
        }

        /// <summary>
        /// Calculates the pressure differential in the concentration zone.
        /// Target is -2.5 kPa.
        /// </summary>
        public static float CalculatePressureDifferential(float currentSuctionForce)
        {
            // Simplified model for suction to pressure conversion
            // In a real scenario this would involve more fluid dynamics
            // For now, we return a value scaled towards the target -2.5 kPa
            return -2.5f * (currentSuctionForce / 164.7f); // 164.7N is target force at 22 rad/s
        }

        /// <summary>
        /// Calculates the ion velocity based on battery energy and route length.
        /// </summary>
        public static float CalculateIonVelocity(float batteryEnergy, float efficiency, float ionMass, float routeLength)
        {
            return (batteryEnergy * efficiency) / (ionMass * routeLength);
        }

        /// <summary>
        /// Calculates the unified positive zone voltage after field duplication.
        /// V_unified = 2 * V_battery = 96V
        /// </summary>
        public static float CalculateUnifiedVoltage(float batteryVoltage)
        {
            return 2 * batteryVoltage;
        }

        /// <summary>
        /// Calculates energy density from photon count and volume.
        /// </summary>
        public static float CalculateEnergyDensity(int photonCount, float photonEnergy)
        {
            float volume = Mathf.PI * Mathf.Pow(ELECTRODE_RADIUS, 2) * TRAP_HEIGHT;
            float totalEnergy = photonCount * photonEnergy;
            // Assuming mass-light-photon units correlate to energy in this simplified model
            return totalEnergy / volume;
        }

        /// <summary>
        /// Translates Quantum Energy Density from QSR into EA Release Energy.
        /// E_release = ρ_quantum * (π * r / 24) * φ
        /// </summary>
        public static float CalculateEnergyFromQSR(double quantumDensity, float r)
        {
            return (float)quantumDensity * (Mathf.PI * r / 24f) * GOLDEN_RATIO;
        }

        /// <summary>
        /// Calculates the effective range of the energy beam based on release energy.
        /// R = (E * φ) / 1000
        /// </summary>
        public static float CalculateRange(float releaseEnergy)
        {
            return (releaseEnergy * GOLDEN_RATIO) / 1000f;
        }

        /// <summary>
        /// Calculates the impact results for a target coordinate.
        /// </summary>
        public static LaunchResult CalculateTargetImpact(Vector3 origin, Vector3 target, float energy)
        {
            Vector3 direction = (target - origin).normalized;
            float distance = Vector3.Distance(origin, target);
            float maxRange = CalculateRange(energy);
            
            bool success = distance <= maxRange;
            float energyAtImpact = success ? energy * Mathf.Pow(GOLDEN_RATIO, -(distance / maxRange)) : 0;
            
            return new LaunchResult
            {
                Success = success,
                EnergyReleased = energy,
                PhotonsLaunched = (int)(energy / 1e-18), // Simplified conversion
                BeamTrajectory = new Trajectory { Origin = origin, Direction = direction, Velocity = 2.99e8f, Range = maxRange },
                LaunchTimestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                ResidualEnergy = energy - energyAtImpact
            };
        }

        /// <summary>
        /// Calculates the blast radius at the point of impact.
        /// r_blast = ρ * φ * 0.5
        /// </summary>
        public static float CalculateBlastRadius(float density)
        {
            return density * GOLDEN_RATIO * 0.5f;
        }

        /// <summary>
        /// Calculates the percentage of air ionized along the beam path.
        /// </summary>
        public static float CalculateIonizationEffect(float energy, float range)
        {
            float beamVolume = Mathf.PI * Mathf.Pow(ELECTRODE_RADIUS, 2) * range;
            float energyRequiredForFullIonization = beamVolume * IONIZATION_ENERGY_AIR;
            return Mathf.Clamp01(energy / energyRequiredForFullIonization) * 100f;
        }

        /// <summary>
        /// Calculates the penetration depth in structural steel.
        /// Depth = Energy / (Density * Area * (C_p * ΔT + L_f))
        /// </summary>
        public static float CalculatePenetrationDepth(float impactEnergy)
        {
            float impactArea = Mathf.PI * Mathf.Pow(ELECTRODE_RADIUS, 2);
            // Energy to melt 1m of steel at impact area
            float energyToMeltPerMeter = STEEL_DENSITY * impactArea * (STEEL_SPECIFIC_HEAT * (STEEL_MELTING_POINT - 293f) + 272000f); 
            return impactEnergy / energyToMeltPerMeter;
        }
    }
}


