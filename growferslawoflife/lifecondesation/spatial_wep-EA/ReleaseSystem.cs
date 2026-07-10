using System;
using System.Collections;
using UnityEngine;

namespace ElectromagneticWeapon.Components
{
    using Core;

    public class StaticZoneController : MonoBehaviour
    {
        public bool IsActive;
        public float ActivationTime = 0.045f; // 45ms

        public event Action OnStaticZoneEstablished;

        public void Activate()
        {
            StartCoroutine(EstablishStaticZone());
        }

        private IEnumerator EstablishStaticZone()
        {
            // Requirement 6.10: Execute in sequence: stop conduction, halt rotation, reverse spinner
            DualPillarManager pillars = GetComponent<DualPillarManager>();
            FrontPillarController front = GetComponent<FrontPillarController>();
            RearSpinnerController rear = GetComponent<RearSpinnerController>();
            AirVortexManager vortex = GetComponent<AirVortexManager>();

            pillars.StopConduction();
            front.StopRotation();
            vortex.DeactivateVortex();
            
            // Wait for mechanical reversal/activation window
            yield return new WaitForSeconds(ActivationTime);
            
            rear.ReverseToRelease();
            
            IsActive = true;
            Debug.Log("StaticZoneController: Static zone established and active.");
            OnStaticZoneEstablished?.Invoke();
        }

        public void Deactivate()
        {
            IsActive = false;
            Debug.Log("StaticZoneController: Static zone deactivated.");
        }
    }

    public class ReleaseMechanism : MonoBehaviour
    {
        public bool PathwayOpen;
        public float ReleaseDuration = 0.125f; // 125ms (Average of 100-150ms)

        public event Action OnReleaseComplete;

        public void ExecuteRelease(float density, float velocity, float k_s)
        {
            StartCoroutine(LaunchSequence(density, velocity, k_s));
        }

        private IEnumerator LaunchSequence(float density, float velocity, float k_s)
        {
            // Requirement 7.1: Open pathway within 15ms
            yield return new WaitForSeconds(0.015f);
            PathwayOpen = true;
            
            float energy = PhysicsEngine.CalculateEAReleaseEnergy(
                density, 
                velocity, 
                k_s, 
                PhysicsEngine.ELECTRODE_RADIUS, 
                1.0f // m² simplified
            );

            Debug.Log($"ReleaseMechanism: Pathway OPEN. Launching concentrated energy beam: {energy} Joules.");

            // Requirement 7.4: Discharge over 100-150ms
            yield return new WaitForSeconds(ReleaseDuration);

            PathwayOpen = false;
            Debug.Log("ReleaseMechanism: Pathway CLOSED. Energy release complete.");
            
            OnReleaseComplete?.Invoke();
        }
    }
}
