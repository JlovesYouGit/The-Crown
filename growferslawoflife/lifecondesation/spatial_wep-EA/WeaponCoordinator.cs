using System;
using System.Collections;
using UnityEngine;

namespace ElectromagneticWeapon
{
    using Core;
    using Components;

    public class WeaponCoordinator : MonoBehaviour
    {
        [Header("System State")]
        public Phase CurrentPhase = Phase.IDLE;
        public float KineticScaling = PhysicsEngine.K_S_THRESHOLD;

        [Header("Subsystems")]
        private BatterySystem _battery;
        private DualPillarManager _pillars;
        private FrontPillarController _frontPillar;
        private RearSpinnerController _rearSpinner;
        private AirVortexManager _vortex;
        private EnergyMonitor _monitor;
        private StaticZoneController _staticZone;
        private ReleaseMechanism _release;

        public event Action<Phase> OnPhaseChanged;

        private void Awake()
        {
            _battery = GetComponent<BatterySystem>();
            _pillars = GetComponent<DualPillarManager>();
            _frontPillar = GetComponent<FrontPillarController>();
            _rearSpinner = GetComponent<RearSpinnerController>();
            _vortex = GetComponent<AirVortexManager>();
            _monitor = GetComponent<EnergyMonitor>();
            _staticZone = GetComponent<StaticZoneController>();
            _release = GetComponent<ReleaseMechanism>();
        }

        private void Start()
        {
            // Set up event listeners
            _battery.OnThresholdReached += StartConcentration;
            _monitor.OnThresholdReached += TryTriggerStaticZone;
            _staticZone.OnStaticZoneEstablished += InitiateRelease;
            _release.OnReleaseComplete += HandleReleaseComplete;

            TransitionTo(Phase.IDLE);
            StartSystem();
        }

        public void StartSystem()
        {
            if (_battery.GetCapacityPercentage() < 59f)
            {
                TransitionTo(Phase.CHARGING);
            }
            else
            {
                StartConcentration();
            }
        }

        private void TransitionTo(Phase nextPhase)
        {
            CurrentPhase = nextPhase;
            Debug.Log($"[SYSTEM] Phase changed to: {nextPhase}");
            OnPhaseChanged?.Invoke(nextPhase);
        }

        private void StartConcentration()
        {
            if (CurrentPhase == Phase.CONCENTRATING) return;

            TransitionTo(Phase.CONCENTRATING);
            
            _pillars.StartConduction();
            _frontPillar.StartRotation();
            _rearSpinner.StartConcentration();
            _vortex.ActivateVortex();
        }

        private void TryTriggerStaticZone()
        {
            if (CurrentPhase != Phase.CONCENTRATING) return;

            // Requirement 13.1: Check density AND revolution ratio
            if (_monitor.CheckRevolutionRatio(_frontPillar.TargetVelocity, KineticScaling))
            {
                TransitionTo(Phase.STATIC_ZONE);
                _staticZone.Activate();
            }
        }

        private void InitiateRelease()
        {
            if (CurrentPhase != Phase.STATIC_ZONE) return;

            TransitionTo(Phase.RELEASING);
            _release.ExecuteRelease(_monitor.CurrentEnergyDensity.Value, _frontPillar.TargetVelocity, KineticScaling);
        }

        private void HandleReleaseComplete()
        {
            TransitionTo(Phase.COOLDOWN);
            StartCoroutine(CooldownSequence());
        }

        private IEnumerator CooldownSequence()
        {
            // Requirement 15.7: Complete full reset within 400ms
            yield return new WaitForSeconds(0.4f);
            
            _monitor.ResetMonitor();
            _staticZone.Deactivate();
            
            // Re-evaluate next state
            if (_battery.GetCapacityPercentage() < 59f)
            {
                TransitionTo(Phase.CHARGING);
            }
            else
            {
                StartConcentration();
            }
        }
    }
}
