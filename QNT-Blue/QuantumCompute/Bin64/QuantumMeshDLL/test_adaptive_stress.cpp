/*
 * AMD Quantum Adaptive Stress Management Test
 * Simple test to verify the new adaptive stress management features
 */

#include "QuantumMeshBoost.h"
#include <iostream>

int main() {
    std::cout << "Testing AMD Quantum Adaptive Stress Management Features" << std::endl;
    std::cout << "=================================================" << std::endl;
    
    // Initialize the quantum mesh system
    if (!InitializeQuantumMeshSystem()) {
        std::cerr << "❌ Failed to initialize quantum mesh system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Quantum mesh system initialized" << std::endl;
    
    // Create sample qbits
    const int qbitCount = 6;
    QuantumQBit qbits[qbitCount];
    
    // Initialize qbits with sample data and adaptive parameters
    for (int i = 0; i < qbitCount; i++) {
        qbits[i].real_part = static_cast<float>(i) / qbitCount;
        qbits[i].imaginary_part = static_cast<float>(qbitCount - i) / qbitCount;
        qbits[i].state = i % 3;
        qbits[i].probability = static_cast<float>(i) / (qbitCount - 1);
        qbits[i].stressY = 0.0f;
        qbits[i].recoveryRate = 0.15f;
        qbits[i].energy = 1.0f;
        qbits[i].maxEnergy = 5.0f;
        qbits[i].isStressed = false;
        qbits[i].stretchFactor = 1.0f;
        qbits[i].adaptiveLevel = 0.0f; // Will be optimized
        qbits[i].boostMultiplier = 1.0f;
        qbits[i].optConstant = 1.0f;
    }
    
    // Test optimizing stress levels for each qbit
    if (OptimizeQBitStressLevels(qbits, qbitCount)) {
        std::cout << "✅ OptimizeQBitStressLevels test passed" << std::endl;
    } else {
        std::cout << "❌ OptimizeQBitStressLevels test failed" << std::endl;
    }
    
    // Verify qbits have adaptive levels
    bool allOptimized = true;
    for (int i = 0; i < qbitCount; i++) {
        if (qbits[i].adaptiveLevel <= 0.0f) {
            allOptimized = false;
            break;
        }
    }
    
    if (allOptimized) {
        std::cout << "✅ QBits successfully optimized with adaptive levels" << std::endl;
    } else {
        std::cout << "❌ QBits not properly optimized" << std::endl;
    }
    
    // Test calculating stress multiplier
    float multiplier = CalculateStressMultiplier(qbits, qbitCount);
    if (multiplier >= 1.0f) {
        std::cout << "✅ CalculateStressMultiplier test passed (multiplier: " << multiplier << ")" << std::endl;
    } else {
        std::cout << "❌ CalculateStressMultiplier test failed" << std::endl;
    }
    
    // Apply the multiplier to all qbits
    for (int i = 0; i < qbitCount; i++) {
        qbits[i].boostMultiplier = multiplier;
    }
    
    // Test applying adaptive stress leveling
    if (ApplyAdaptiveStressLeveling(qbits, qbitCount)) {
        std::cout << "✅ ApplyAdaptiveStressLeveling test passed" << std::endl;
    } else {
        std::cout << "❌ ApplyAdaptiveStressLeveling test failed" << std::endl;
    }
    
    // Verify qbits are stressed with adaptive levels
    bool allAdaptiveStressed = true;
    for (int i = 0; i < qbitCount; i++) {
        if (!qbits[i].isStressed || qbits[i].stressY <= 0.0f) {
            allAdaptiveStressed = false;
            break;
        }
    }
    
    if (allAdaptiveStressed) {
        std::cout << "✅ QBits successfully stressed with adaptive levels" << std::endl;
    } else {
        std::cout << "❌ QBits not properly stressed with adaptive levels" << std::endl;
    }
    
    // Test extracting qenergy
    float extractedEnergy = ExtractQEnergy(qbits, qbitCount);
    if (extractedEnergy > 0.0f) {
        std::cout << "✅ ExtractQEnergy test passed (" << extractedEnergy << " Joules extracted)" << std::endl;
    } else {
        std::cout << "❌ ExtractQEnergy test failed" << std::endl;
    }
    
    // Test managing qbit recovery
    if (ManageQBitRecovery(qbits, qbitCount)) {
        std::cout << "✅ ManageQBitRecovery test passed" << std::endl;
    } else {
        std::cout << "❌ ManageQBitRecovery test failed" << std::endl;
    }
    
    // Test enhanced hyperprocessing with adaptive stress
    double boostFactor = ApplyHyperprocessing(qbits, qbitCount);
    if (boostFactor > 1.0) {
        std::cout << "✅ ApplyHyperprocessing with adaptive stress management passed (" << boostFactor << "x boost)" << std::endl;
    } else {
        std::cout << "❌ ApplyHyperprocessing with adaptive stress management failed" << std::endl;
    }
    
    // Shutdown the system
    ShutdownQuantumMeshSystem();
    std::cout << "✅ All adaptive stress management tests completed" << std::endl;
    
    return 0;
}