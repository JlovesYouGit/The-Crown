/*
 * AMD Quantum QBit Stress Management Test
 * Simple test to verify the new qbit stress management features
 */

#include "QuantumMeshBoost.h"
#include <iostream>

int main() {
    std::cout << "Testing AMD Quantum QBit Stress Management Features" << std::endl;
    std::cout << "=================================================" << std::endl;
    
    // Initialize the quantum mesh system
    if (!InitializeQuantumMeshSystem()) {
        std::cerr << "❌ Failed to initialize quantum mesh system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Quantum mesh system initialized" << std::endl;
    
    // Create sample qbits
    const int qbitCount = 5;
    QuantumQBit qbits[qbitCount];
    
    // Initialize qbits with sample data
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
    }
    
    // Test applying stress to qbits
    if (ApplyQBitStress(qbits, qbitCount, 0.7f)) {
        std::cout << "✅ ApplyQBitStress test passed" << std::endl;
    } else {
        std::cout << "❌ ApplyQBitStress test failed" << std::endl;
    }
    
    // Verify qbits are stressed
    bool allStressed = true;
    for (int i = 0; i < qbitCount; i++) {
        if (!qbits[i].isStressed || qbits[i].stressY < 0.6f) {
            allStressed = false;
            break;
        }
    }
    
    if (allStressed) {
        std::cout << "✅ QBits successfully stressed" << std::endl;
    } else {
        std::cout << "❌ QBits not properly stressed" << std::endl;
    }
    
    // Test controlling Y-axis stretching
    if (ControlQBitStretchY(qbits, qbitCount, 1.8f)) {
        std::cout << "✅ ControlQBitStretchY test passed" << std::endl;
    } else {
        std::cout << "❌ ControlQBitStretchY test failed" << std::endl;
    }
    
    // Verify qbits are stretched
    bool allStretched = true;
    for (int i = 0; i < qbitCount; i++) {
        if (qbits[i].stretchFactor < 1.7f) {
            allStretched = false;
            break;
        }
    }
    
    if (allStretched) {
        std::cout << "✅ QBits successfully stretched" << std::endl;
    } else {
        std::cout << "❌ QBits not properly stretched" << std::endl;
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
    
    // Test enhanced hyperprocessing with stressed qbits
    double boostFactor = ApplyHyperprocessing(qbits, qbitCount);
    if (boostFactor > 1.0) {
        std::cout << "✅ ApplyHyperprocessing with stress management passed (" << boostFactor << "x boost)" << std::endl;
    } else {
        std::cout << "❌ ApplyHyperprocessing with stress management failed" << std::endl;
    }
    
    // Shutdown the system
    ShutdownQuantumMeshSystem();
    std::cout << "✅ All qbit stress management tests completed" << std::endl;
    
    return 0;
}