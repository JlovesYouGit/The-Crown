using System;
using UnityEngine;
using ElectromagneticWeapon.Core;
using ElectromagneticWeapon.Quantum;
using ElectromagneticWeapon.Components;

namespace ElectromagneticWeapon.Tests
{
    class FullSpectrumSimulation
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=== FULL SPECTRUM WEAPON SIMULATION (QSR BRIDGE) ===");
            
            // 1. Initialize Simulator
            UnityEngine.Simulator sim = UnityEngine.Simulator.Instance;
            
            // 2. Setup Quantum Layer (QSR)
            var qsr = sim.AddComponent<QuantumStateResizer>();
            qsr.AddElectrode(Vector3.zero, -1e-19, 1.67e-27, 1e-15, 1e15);
            qsr.AddElectrode(new Vector3(1e-14f, 0, 0), -1e-19, 1.67e-27, 1e-15, 5e14);

            // 3. Trigger Upforce Moment
            Console.WriteLine("[STEP 1] Triggering Upforce Moment...");
            qsr.TriggerUpforceMoment(1e-6f);
            
            // 4. Run Quantum Simulation to reach Singularity
            Console.WriteLine("[STEP 2] Resizing Quantum State...");
            qsr.RunSimulation(100, 1e-10);
            
            var densityAtSingularity = qsr.Electrodes[0].EnergyDensity;
            Console.WriteLine($"[STEP 3] Quantum Singularity reached. Density: {densityAtSingularity:E2}");

            // 5. Bridge to Main Physics Engine
            float eaEnergy = PhysicsEngine.CalculateEnergyFromQSR(densityAtSingularity, PhysicsEngine.ELECTRODE_RADIUS);
            Console.WriteLine($"[STEP 4] Bridged to EA Release Formula. Energy: {eaEnergy:E2} J");

            // 6. Execute Coordinate Strike
            Vector3 targetPos = new Vector3(500, 0, 0); // Target at 500m
            Console.WriteLine($"[STEP 5] Targeting Coordinates: {targetPos}");
            
            var result = PhysicsEngine.CalculateTargetImpact(Vector3.zero, targetPos, eaEnergy);

            if (result.Success)
            {
                Console.WriteLine(">> STRIKE SUCCESSFUL <<");
                float blastRadius = PhysicsEngine.CalculateBlastRadius((float)densityAtSingularity / 1e30f); 
                float ionization = PhysicsEngine.CalculateIonizationEffect(eaEnergy, result.BeamTrajectory.Range);
                float penetration = PhysicsEngine.CalculatePenetrationDepth(eaEnergy);

                Console.WriteLine($"Beam Range: {result.BeamTrajectory.Range:F2} m");
                Console.WriteLine($"Blast Radius at Impact: {blastRadius:F2} m");
                Console.WriteLine($"Atmospheric Ionization: {ionization:F1} %");
                Console.WriteLine($"Material Penetration (Steel): {penetration * 1000:F1} mm");
            }
            else
            {
                Console.WriteLine(">> STRIKE FAILED: OUT OF RANGE <<");
                Console.WriteLine($"Max Range for current Energy: {result.BeamTrajectory.Range:F2} m");
            }

            Console.WriteLine("=== SIMULATION COMPLETE ===");
        }
    }
}
