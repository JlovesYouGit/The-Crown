/*
 * AMD Quantum State Manipulation Test
 * Demonstrates the new multi-phase quantum state manipulation features
 */

#include "QuantumMeshBoost.h"
#include <iostream>
#include <vector>
#include <chrono>

int main() {
    std::cout << "AMD Quantum State Manipulation Test" << std::endl;
    std::cout << "===================================" << std::endl << std::endl;

    // Initialize the quantum mesh system
    if (!InitializeQuantumMeshSystem()) {
        std::cerr << "❌ Failed to initialize quantum mesh system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Quantum mesh system initialized successfully!" << std::endl << std::endl;

    // Create sample qbits
    const int qbitCount = 10;
    QuantumQBit qbits[qbitCount];
    
    // Initialize qbits with sample data
    for (int i = 0; i < qbitCount; i++) {
        qbits[i].real_part = 0.5f + (i * 0.1f);
        qbits[i].imaginary_part = 0.3f + (i * 0.05f);
        qbits[i].state = (i % 3); // Alternate between 0, 1, and superposition (2)
        qbits[i].probability = 0.5f;
        qbits[i].stressY = 0.0f;
        qbits[i].recoveryRate = 0.1f;
        qbits[i].energy = 50.0f;
        qbits[i].maxEnergy = 100.0f;
        qbits[i].isStressed = false;
        qbits[i].stretchFactor = 1.0f;
        qbits[i].adaptiveLevel = 0.5f;
        qbits[i].boostMultiplier = 1.0f;
        qbits[i].optConstant = 1.0f;
    }
    std::cout << "✅ Created " << qbitCount << " sample qbits" << std::endl << std::endl;

    // Initialize quantum phase manipulator
    std::cout << "1. Initializing Quantum Phase Manipulator..." << std::endl;
    QuantumPhaseManipulator manipulator;
    if (InitializeQuantumPhaseManipulator(&manipulator, 20.0f)) {
        std::cout << "✅ Quantum Phase Manipulator initialized with 20km effect radius" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to initialize Quantum Phase Manipulator!" << std::endl << std::endl;
    }

    // Test phase 1: Overlap with matter states
    std::cout << "2. Testing Phase 1 - Qstate overlap with matter states..." << std::endl;
    QuantumStateManipulationParams params1;
    params1.phase = 1;
    params1.equilibriumRange = 20.0f;
    params1.interactionStrength = 0.8f;
    params1.enableLongRange = false;
    params1.empowermentFactor = 0.0f;
    params1.qenergyBoost = 1.0f;
    for (int i = 0; i < 10; i++) {
        params1.phaseSpecificParams[i] = 0.1f * i;
    }

    if (ManipulateQuantumStatesPhase1(qbits, qbitCount, &params1)) {
        std::cout << "✅ Phase 1 completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to execute Phase 1!" << std::endl << std::endl;
    }

    // Test phase 2: Interact with first particle
    std::cout << "3. Testing Phase 2 - Particle interaction and empowerment..." << std::endl;
    QuantumStateManipulationParams params2;
    params2.phase = 2;
    params2.equilibriumRange = 20.0f;
    params2.interactionStrength = 0.0f;
    params2.enableLongRange = false;
    params2.empowermentFactor = 0.9f;
    params2.qenergyBoost = 1.5f;
    for (int i = 0; i < 10; i++) {
        params2.phaseSpecificParams[i] = 0.1f * i;
    }

    if (ManipulateQuantumStatesPhase2(qbits, qbitCount, &params2)) {
        std::cout << "✅ Phase 2 completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to execute Phase 2!" << std::endl << std::endl;
    }

    // Test phase 3: Large-scale interaction
    std::cout << "4. Testing Phase 3 - Large-scale quantum state realization..." << std::endl;
    QuantumStateManipulationParams params3;
    params3.phase = 3;
    params3.equilibriumRange = 20.0f;
    params3.interactionStrength = 0.0f;
    params3.enableLongRange = true;
    params3.empowermentFactor = 0.0f;
    params3.qenergyBoost = 2.0f;
    for (int i = 0; i < 10; i++) {
        params3.phaseSpecificParams[i] = 0.1f * i;
    }

    if (ManipulateQuantumStatesPhase3(qbits, qbitCount, &params3)) {
        std::cout << "✅ Phase 3 completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to execute Phase 3!" << std::endl << std::endl;
    }

    // Test phase 4: Matter shaping
    std::cout << "5. Testing Phase 4 - Matter shaping and state manipulation..." << std::endl;
    QuantumStateManipulationParams params4;
    params4.phase = 4;
    params4.equilibriumRange = 20.0f;
    params4.interactionStrength = 0.0f;
    params4.enableLongRange = false;
    params4.empowermentFactor = 0.0f;
    params4.qenergyBoost = 2.5f;
    for (int i = 0; i < 10; i++) {
        params4.phaseSpecificParams[i] = 0.1f * i;
    }

    if (ManipulateQuantumStatesPhase4(qbits, qbitCount, &params4)) {
        std::cout << "✅ Phase 4 completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to execute Phase 4!" << std::endl << std::endl;
    }

    // Test complete phase cycle
    std::cout << "6. Testing Complete Phase Cycle Execution..." << std::endl;
    if (ExecuteQuantumPhaseCycle(&manipulator, qbits, qbitCount)) {
        std::cout << "✅ Complete phase cycle executed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to execute complete phase cycle!" << std::endl << std::endl;
    }

    // Test matter state interaction
    std::cout << "7. Testing Matter State Interaction..." << std::endl;
    MatterStateInteraction interaction;
    float matterState[10] = {0.1f, 0.2f, 0.3f, 0.4f, 0.5f, 0.6f, 0.7f, 0.8f, 0.9f, 1.0f};
    
    if (InteractWithMatterStates(qbits, qbitCount, &interaction, matterState)) {
        std::cout << "✅ Matter state interaction completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to interact with matter states!" << std::endl << std::endl;
    }

    // Test reaction empowerment
    std::cout << "8. Testing Reaction Empowerment Through QEnergy..." << std::endl;
    if (EmpowerReactionThroughQEnergy(qbits, qbitCount, 1.2f)) {
        std::cout << "✅ Reaction empowerment completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to empower reaction through qenergy!" << std::endl << std::endl;
    }

    // Test large-scale quantum effects
    std::cout << "9. Testing Large-Scale Quantum Effects..." << std::endl;
    if (ApplyLargeScaleQuantumEffects(qbits, qbitCount, 12742.0f)) { // Earth's diameter
        std::cout << "✅ Large-scale quantum effects applied successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to apply large-scale quantum effects!" << std::endl << std::endl;
    }

    // Display final qbit states
    std::cout << "Final Qbit States:" << std::endl;
    for (int i = 0; i < qbitCount; i++) {
        std::cout << "  Qbit " << i << ": Energy=" << qbits[i].energy 
                  << ", Boost=" << qbits[i].boostMultiplier 
                  << ", Stress=" << qbits[i].stressY << std::endl;
    }
    std::cout << std::endl;

    // Shutdown the quantum mesh system
    ShutdownQuantumMeshSystem();
    std::cout << "✅ Quantum mesh system shut down successfully!" << std::endl;

    std::cout << std::endl << "🎉 All quantum state manipulation tests completed!" << std::endl;
    return 0;
}