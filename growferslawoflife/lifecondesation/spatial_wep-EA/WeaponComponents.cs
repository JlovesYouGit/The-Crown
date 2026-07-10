using System;
using UnityEngine;

namespace ElectromagneticWeapon.Components
{
    using Core;

    public class DualPillarManager : MonoBehaviour
    {
        public float PillarGap = PhysicsEngine.PILLAR_GAP;
        public float Conductivity = 1e7f; // 10⁷ S/m at 77K
        public bool IsConducting;

        public void StartConduction()
        {
            IsConducting = true;
            Debug.Log("DualPillarManager: Electron conduction started.");
        }

        public void StopConduction()
        {
            IsConducting = false;
            Debug.Log("DualPillarManager: Electron conduction stopped.");
        }
    }

    public class FrontPillarController : MonoBehaviour
    {
        public float TargetVelocity = 19.0f; // rad/s
        public float CurrentVelocity;
        public bool IsRotating;

        public void StartRotation()
        {
            IsRotating = true;
            CurrentVelocity = TargetVelocity;
        }

        public void StopRotation()
        {
            IsRotating = false;
            CurrentVelocity = 0;
        }
    }

    public class RearSpinnerController : MonoBehaviour
    {
        public float ConcentrationVelocity = -22.0f; // rad/s (CCW)
        public float ReleaseVelocity = 22.0f; // rad/s (CW)
        public float CurrentVelocity;
        public bool IsRotating;
        public float ReversalTime = 0.045f; // 45ms

        public void StartConcentration()
        {
            IsRotating = true;
            CurrentVelocity = ConcentrationVelocity;
        }

        public void ReverseToRelease()
        {
            // Requirement 3.4: Reverse direction within 45ms
            CurrentVelocity = ReleaseVelocity;
            Debug.Log("RearSpinnerController: Reversed to clockwise rotation.");
        }

        public void StopRotation()
        {
            IsRotating = false;
            CurrentVelocity = 0;
        }
    }

    public class AirVortexManager : MonoBehaviour
    {
        public float NMInertia = PhysicsEngine.NM_INERTIA;
        public float SuctionRate = 0.85f; // m³/s
        public bool IsActive;

        public void ActivateVortex()
        {
            IsActive = true;
            Debug.Log("AirVortexManager: Vortex suction activated.");
        }

        public void DeactivateVortex()
        {
            IsActive = false;
            Debug.Log("AirVortexManager: Vortex suction deactivated.");
        }

        public float GetCurrentSuctionForce(float spinnerVelocity)
        {
            if (!IsActive) return 0;
            return PhysicsEngine.CalculateVortexSuctionForce(Mathf.Abs(spinnerVelocity));
        }
    }
}
