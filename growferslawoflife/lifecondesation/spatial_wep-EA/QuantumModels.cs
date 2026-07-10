using System;
using UnityEngine;

namespace ElectromagneticWeapon.Quantum
{
    [Serializable]
    public struct QuantumElectrode
    {
        public Vector3 Position;
        public double Charge; // Coulombs
        public double Mass;   // kg
        public double QuantumStateSize; // meters (q)
        public double EnergyDensity;    // J/m^3
        public double Frequency;        // Hz
        public Vector3 Velocity;
        
        public QuantumElectrode(Vector3 pos, double q, double m, double initialQSize, double freq)
        {
            Position = pos;
            Charge = q;
            Mass = m;
            QuantumStateSize = initialQSize;
            Frequency = freq;
            EnergyDensity = 0;
            Velocity = Vector3.zero;
        }
    }

    public struct QuantumConstants
    {
        public const double H_BAR = 1.054e-34;
        public const double C = 2.998e8;
        public const double G = 6.674e-11;
        public const double K_E = 8.988e9;
        public const double ALPHA = 0.007297; // Fine-structure constant as a scaling factor
    }

    public struct QSRState
    {
        public bool UpforceTriggered;
        public double SingularityParameter;
        public double DecompressionRate;
        public long StepCount;
    }
}
