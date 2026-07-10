using System;
using UnityEngine;

namespace ElectromagneticWeapon.Core
{
    public class BatterySystem : MonoBehaviour
    {
        public float MaxCapacity = 20.0f; // Ah
        public float CurrentCapacity;
        public float NominalVoltage = 48.0f;
        public float TargetThreshold = 0.59f; // 59%

        [Header("State")]
        public bool HighVelocityDeliveryActive;
        public bool FieldDuplicated;
        public float CurrentVoltage;
        public float IonVelocity;

        public event Action OnThresholdReached;

        private void Start()
        {
            CurrentCapacity = MaxCapacity;
            CurrentVoltage = NominalVoltage;
        }

        public void Update()
        {
            float percentage = GetCapacityPercentage();
            
            if (!HighVelocityDeliveryActive && percentage <= TargetThreshold * 100f)
            {
                ActivateHighVelocityDelivery();
                OnThresholdReached?.Invoke();
            }
        }

        public float GetCapacityPercentage()
        {
            return (CurrentCapacity / MaxCapacity) * 100f;
        }

        public void ActivateHighVelocityDelivery()
        {
            HighVelocityDeliveryActive = true;
            IonVelocity = PhysicsEngine.ION_VELOCITY_TARGET;
            
            // Field Duplication: - to ++
            DuplicateField();
            
            // Unify to Positive Zone
            UnifyToPositiveZone();
        }

        private void DuplicateField()
        {
            // Requirement 11.6: Complete field duplication within 8ms
            // In a real-time simulation, this might be handled by a Coroutine or a state change
            FieldDuplicated = true;
            Debug.Log("BatterySystem: Field duplication (- to ++) completed.");
        }

        private void UnifyToPositiveZone()
        {
            // Requirement 11.7: Unify terminals into single 96V positive zone
            CurrentVoltage = PhysicsEngine.CalculateUnifiedVoltage(NominalVoltage);
            Debug.Log($"BatterySystem: Unified Positive Zone established at {CurrentVoltage}V.");
        }

        public void ConsumeEnergy(float amountAh)
        {
            CurrentCapacity = Mathf.Max(0, CurrentCapacity - amountAh);
        }

        public bool IsReadyForRotationSwitch()
        {
            // Requirement 11.10: Complete electrode coverage before rotation switch occurs
            return HighVelocityDeliveryActive && FieldDuplicated;
        }
    }
}
