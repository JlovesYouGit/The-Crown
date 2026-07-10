using System;
using System.Collections.Generic;
using UnityEngine;

namespace ElectromagneticWeapon.Core
{
    public enum Phase
    {
        IDLE,
        CHARGING,
        CONCENTRATING,
        STATIC_ZONE,
        RELEASING,
        COOLDOWN
    }

    public enum RotationDirection
    {
        CLOCKWISE,
        COUNTER_CLOCKWISE,
        STOPPED
    }

    public enum EnergyUnit
    {
        MASS_LIGHT_PHOTON,
        JOULES,
        ELECTRON_VOLTS
    }

    public enum ThresholdStatus
    {
        BELOW_THRESHOLD,
        AT_THRESHOLD,
        ABOVE_THRESHOLD
    }

    public struct SystemState
    {
        public Phase CurrentPhase;
        public float CurrentEnergyDensity;
        public float FrontPillarVelocity;
        public float RearSpinnerVelocity;
        public bool StaticZoneActive;
        public int PhotonCount;
        public long Timestamp;

        public void Validate()
        {
            if (CurrentEnergyDensity < 0) throw new ArgumentException("EnergyDensity must be non-negative.");
            if (PhotonCount < 0) throw new ArgumentException("PhotonCount must be non-negative.");
            
            if (CurrentPhase == Phase.CONCENTRATING)
            {
                if (Mathf.Abs(FrontPillarVelocity - 19) > 0.1f) 
                    Debug.LogWarning("FrontPillarVelocity should be 19 during CONCENTRATING phase.");
            }
            else if (CurrentPhase == Phase.STATIC_ZONE)
            {
                if (FrontPillarVelocity != 0)
                    Debug.LogWarning("FrontPillarVelocity should be 0 during STATIC_ZONE.");
            }

            if (StaticZoneActive && (CurrentPhase != Phase.STATIC_ZONE && CurrentPhase != Phase.RELEASING))
                throw new ArgumentException("StaticZoneActive must be true only during STATIC_ZONE or RELEASING phases.");
        }
    }

    public struct RotationState
    {
        public RotationDirection Direction;
        public float Velocity;
        public float CurrentAngle;
        public bool IsRotating;
        public float TargetVelocity;

        public void Validate()
        {
            if (IsRotating && Direction == RotationDirection.STOPPED)
                throw new ArgumentException("IsRotating must be false when direction is STOPPED.");
            
            if (Direction == RotationDirection.CLOCKWISE && Velocity < 0)
                throw new ArgumentException("Velocity must be positive for CLOCKWISE direction.");
            
            if (Direction == RotationDirection.COUNTER_CLOCKWISE && Velocity > 0)
                throw new ArgumentException("Velocity must be negative for COUNTER_CLOCKWISE direction.");

            if (CurrentAngle < 0 || CurrentAngle >= 360)
                CurrentAngle = (CurrentAngle % 360 + 360) % 360;
        }
    }

    public struct EnergyDensity
    {
        public float Value;
        public EnergyUnit Unit;
        public float MassEquivalent;
        public int PhotonCount;
        public ThresholdStatus Status;

        public void Validate()
        {
            if (Value < 0) throw new ArgumentException("Energy density value must be non-negative.");
            
            if (Value < 4 && Status != ThresholdStatus.BELOW_THRESHOLD)
                throw new ArgumentException("ThresholdStatus must be BELOW_THRESHOLD when value < 4.");
            
            if (Value >= 4 && Status == ThresholdStatus.BELOW_THRESHOLD)
                throw new ArgumentException("ThresholdStatus must be AT_THRESHOLD or ABOVE_THRESHOLD when value >= 4.");
        }
    }

    [Serializable]
    public struct Photon
    {
        public float Energy;
        public float Wavelength;
        public Vector3 Momentum;
        public float Polarization;
    }

    public struct PhotonStream
    {
        public List<Photon> Photons;
        public float TotalEnergy;
        public float Wavelength;
        public float Intensity;
        public Vector3 Direction;
    }

    public struct ElectromagneticField
    {
        public Vector3 ElectricField;
        public Vector3 MagneticField;
        public float FieldStrength;
        public float Frequency;
        public float PillarGap;

        public void Validate()
        {
            // Electric and Magnetic fields must be perpendicular (dot product = 0)
            if (Mathf.Abs(Vector3.Dot(ElectricField, MagneticField)) > 0.001f)
                Debug.LogWarning("Electric and Magnetic fields are not perpendicular.");
        }
    }

    public struct Trajectory
    {
        public Vector3 Origin;
        public Vector3 Direction;
        public float Velocity;
        public float Range;
    }

    public struct LaunchResult
    {
        public bool Success;
        public float EnergyReleased;
        public int PhotonsLaunched;
        public Trajectory BeamTrajectory;
        public long LaunchTimestamp;
        public float ResidualEnergy;
    }
}
