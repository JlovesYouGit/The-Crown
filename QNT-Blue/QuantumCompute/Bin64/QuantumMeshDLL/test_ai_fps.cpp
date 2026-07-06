/*
 * AMD Quantum AI FPS Adjustment Test
 * Simple test to verify the new AI FPS adjustment features
 */

#include "QuantumMeshBoost.h"
#include <iostream>

int main() {
    std::cout << "Testing AMD Quantum AI FPS Adjustment Features" << std::endl;
    std::cout << "===========================================" << std::endl;
    
    // Initialize the quantum mesh system
    if (!InitializeQuantumMeshSystem()) {
        std::cerr << "❌ Failed to initialize quantum mesh system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Quantum mesh system initialized" << std::endl;
    
    // Initialize lightweight AI model
    if (InitializeLightweightModel("../Models/quantum_render_optimization.gguf")) {
        std::cout << "✅ Lightweight AI model initialized" << std::endl;
    } else {
        std::cerr << "⚠️  Failed to initialize lightweight AI model (continuing anyway)" << std::endl;
    }
    
    // Create sample input frames
    const int inputFrameCount = 3;
    FrameData inputFrames[inputFrameCount];
    
    // Initialize with sample data
    for (int i = 0; i < inputFrameCount; i++) {
        inputFrames[i].width = 1920;
        inputFrames[i].height = 1080;
        inputFrames[i].pixelData = new float[inputFrames[i].width * inputFrames[i].height];
        inputFrames[i].motionVectorX = static_cast<float>(i) * 0.5f;
        inputFrames[i].motionVectorY = static_cast<float>(i) * 0.3f;
        inputFrames[i].frameNumber = i;
        inputFrames[i].timestamp = static_cast<double>(i) / 30.0;
        inputFrames[i].sharpness = 0.8f;
        inputFrames[i].noiseLevel = 0.1f;
        
        // Initialize with sample pixel data
        for (int j = 0; j < inputFrames[i].width * inputFrames[i].height; j++) {
            inputFrames[i].pixelData[j] = static_cast<float>(j % 100) / 100.0f;
        }
    }
    
    // Test tracking moving objects
    TrackingParams trackingParams;
    trackingParams.enableTracking = true;
    trackingParams.trackingSensitivity = 0.5f;
    trackingParams.maxTrackedObjects = 5;
    trackingParams.unrealEngineCompat = true;
    trackingParams.predictionAccuracy = 0.9f;
    
    if (TrackMovingObjects(inputFrames, inputFrameCount, &trackingParams)) {
        std::cout << "✅ TrackMovingObjects test passed" << std::endl;
    } else {
        std::cout << "❌ TrackMovingObjects test failed" << std::endl;
    }
    
    // Test AI FPS adjustment
    FrameData* outputFrames = nullptr;
    FPSParams fpsParams;
    fpsParams.targetFPS = 120;
    fpsParams.motionAdaptive = true;
    fpsParams.motionThreshold = 0.1f;
    fpsParams.interpolationMethod = 3; // Quantum AI
    fpsParams.preserveEdges = true;
    fpsParams.temporalStability = 0.9f;
    fpsParams.ultraHighFPS = false;
    
    int outputFrameCount = AdjustFPS(inputFrames, inputFrameCount, &outputFrames, &fpsParams);
    if (outputFrameCount > 0) {
        std::cout << "✅ AdjustFPS test passed (" << outputFrameCount << " frames generated)" << std::endl;
    } else {
        std::cout << "❌ AdjustFPS test failed" << std::endl;
    }
    
    // Test frame quality enhancement
    if (outputFrameCount > 0) {
        if (EnhanceFrameQuality(&outputFrames[0], false)) {
            std::cout << "✅ EnhanceFrameQuality test passed" << std::endl;
        } else {
            std::cout << "❌ EnhanceFrameQuality test failed" << std::endl;
        }
    }
    
    // Test temporal consistency
    if (outputFrameCount >= 2) {
        if (ApplyTemporalConsistency(outputFrames, 2)) {
            std::cout << "✅ ApplyTemporalConsistency test passed" << std::endl;
        } else {
            std::cout << "❌ ApplyTemporalConsistency test failed" << std::endl;
        }
    }
    
    // Test Unreal Engine optimization
    if (outputFrameCount >= 2) {
        if (OptimizeForUnrealEngine(outputFrames, 2, false)) {
            std::cout << "✅ OptimizeForUnrealEngine test passed" << std::endl;
        } else {
            std::cout << "❌ OptimizeForUnrealEngine test failed" << std::endl;
        }
    }
    
    // Test future frame prediction
    FrameData* predictedFrames = nullptr;
    int predictedCount = PredictFutureFrames(inputFrames, inputFrameCount, &predictedFrames, 1);
    if (predictedCount > 0) {
        std::cout << "✅ PredictFutureFrames test passed (" << predictedCount << " frames predicted)" << std::endl;
    } else {
        std::cout << "❌ PredictFutureFrames test failed" << std::endl;
    }
    
    // Clean up
    for (int i = 0; i < inputFrameCount; i++) {
        delete[] inputFrames[i].pixelData;
    }
    
    if (outputFrames != nullptr) {
        for (int i = 0; i < outputFrameCount; i++) {
            delete[] outputFrames[i].pixelData;
        }
        delete[] outputFrames;
    }
    
    if (predictedFrames != nullptr) {
        for (int i = 0; i < predictedCount; i++) {
            delete[] predictedFrames[i].pixelData;
        }
        delete[] predictedFrames;
    }
    
    // Shutdown the system
    ShutdownQuantumMeshSystem();
    std::cout << "✅ All AI FPS adjustment tests completed" << std::endl;
    
    return 0;
}