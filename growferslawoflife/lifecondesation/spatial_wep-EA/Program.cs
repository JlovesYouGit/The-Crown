using System;
using UnityEngine;
using ElectromagneticWeapon;
using ElectromagneticWeapon.Core;
using ElectromagneticWeapon.Components;

namespace ElectromagneticWeapon.Tests
{
    class BasicSimulation
    {
        public static void BasicMain(string[] args)
        {
            Console.WriteLine("=== Electromagnetic Energy Weapon System CLI Simulator ===");
            
            // 1. Setup Simulation Environment
            UnityEngine.Simulator sim = UnityEngine.Simulator.Instance;
            
            // 2. Add Components to Mocked GameObject
            var battery = sim.AddComponent<BatterySystem>();
            var pillars = sim.AddComponent<DualPillarManager>();
            var front = sim.AddComponent<FrontPillarController>();
            var rear = sim.AddComponent<RearSpinnerController>();
            var vortex = sim.AddComponent<AirVortexManager>();
            var monitor = sim.AddComponent<EnergyMonitor>();
            var staticZone = sim.AddComponent<StaticZoneController>();
            var release = sim.AddComponent<ReleaseMechanism>();
            var coordinator = sim.AddComponent<WeaponCoordinator>();

            // 3. Configure Initial State
            battery.CurrentCapacity = 12.0f; // 12/20 = 60%, just above threshold (59%)
            
            // 4. Run Life-Cycle Simulation
            // We need enough steps to see the concentration (density 0 to 4) 
            // and the release timing (static zone 45ms + release 125ms + cooldown 400ms)
            // 1 step = 16ms
            sim.RunSimulation(500); 

            Console.WriteLine("\n=== Simulation Complete ===");
        }
    }
}
