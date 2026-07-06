/*
 * AMD Quantum Mesh Rendering Boost - Grain & Upscaling Test
 * Simple test to verify the new grain processing and upscaling features
 */

#include "QuantumMeshBoost.h"
#include <iostream>

int main() {
    std::cout << "Testing AMD Quantum Grain & Upscaling Features" << std::endl;
    std::cout << "=============================================" << std::endl;
    
    // Initialize the quantum mesh system
    if (!InitializeQuantumMeshSystem()) {
        std::cerr << "❌ Failed to initialize quantum mesh system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Quantum mesh system initialized" << std::endl;
    
    // Create sample frame data
    FrameData frame;
    frame.width = 1920;
    frame.height = 1080;
    frame.pixelData = new float[frame.width * frame.height];
    
    // Initialize with sample data
    for (int i = 0; i < frame.width * frame.height; i++) {
        frame.pixelData[i] = static_cast<float>(i % 1000) / 1000.0f;
    }
    
    // Test upscaling
    FrameData outputFrame;
    outputFrame.width = 3840;
    outputFrame.height = 2160;
    outputFrame.pixelData = new float[outputFrame.width * outputFrame.height];
    
    UpscaleParams upscaleParams;
    upscaleParams.scaleFactor = 2;
    upscaleParams.sharpness = 0.5f;
    upscaleParams.noiseReduction = 0.3f;
    upscaleParams.preserveEdges = true;
    upscaleParams.algorithm = 3; // Quantum-enhanced
    
    if (UpscaleFrame(&frame, &outputFrame, &upscaleParams)) {
        std::cout << "✅ Upscaling test passed" << std::endl;
    } else {
        std::cout << "❌ Upscaling test failed" << std::endl;
    }
    
    // Test grain processing
    GrainParams grainParams;
    grainParams.intensity = 0.3f;
    grainParams.size = 0.5f;
    grainParams.contrast = 1.0f;
    grainParams.patternType = 3; // Quantum grain
    grainParams.adaptive = true;
    
    if (ApplyGrainProcessing(&outputFrame, &grainParams)) {
        std::cout << "✅ Grain processing test passed" << std::endl;
    } else {
        std::cout << "❌ Grain processing test failed" << std::endl;
    }
    
    // Test QLED optimization
    if (OptimizeForQLEDDisplay(&outputFrame, true)) {
        std::cout << "✅ QLED optimization test passed" << std::endl;
    } else {
        std::cout << "❌ QLED optimization test failed" << std::endl;
    }
    
    // Test noise reduction
    if (ApplyQuantumNoiseReduction(&outputFrame, 0.5f)) {
        std::cout << "✅ Noise reduction test passed" << std::endl;
    } else {
        std::cout << "❌ Noise reduction test failed" << std::endl;
    }
    
    // Test color enhancement
    if (EnhanceColorFidelity(&outputFrame, 1.2f, 1.1f)) {
        std::cout << "✅ Color enhancement test passed" << std::endl;
    } else {
        std::cout << "❌ Color enhancement test failed" << std::endl;
    }
    
    // Test adaptive sharpening
    if (ApplyAdaptiveSharpening(&outputFrame, 0.5f)) {
        std::cout << "✅ Adaptive sharpening test passed" << std::endl;
    } else {
        std::cout << "❌ Adaptive sharpening test failed" << std::endl;
    }
    
    // Clean up
    delete[] frame.pixelData;
    delete[] outputFrame.pixelData;
    
    // Shutdown the system
    ShutdownQuantumMeshSystem();
    std::cout << "✅ All tests completed" << std::endl;
    
    return 0;
}