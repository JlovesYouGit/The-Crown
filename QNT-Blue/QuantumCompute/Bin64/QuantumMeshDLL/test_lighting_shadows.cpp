/*
 * AMD Quantum Mesh Lighting and Shadow Enhancement Test
 * Demonstrates the new lighting and shadow optimization features
 */

#include "QuantumMeshBoost.h"
#include <iostream>
#include <vector>
#include <chrono>

int main() {
    std::cout << "AMD Quantum Mesh Lighting and Shadow Enhancement Test" << std::endl;
    std::cout << "====================================================" << std::endl << std::endl;

    // Initialize the quantum mesh system
    if (!InitializeQuantumMeshSystem()) {
        std::cerr << "❌ Failed to initialize quantum mesh system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Quantum mesh system initialized successfully!" << std::endl << std::endl;

    // Create sample meshes
    const int meshCount = 5;
    QuantumMesh meshes[meshCount];
    
    // Initialize meshes with sample data
    for (int i = 0; i < meshCount; i++) {
        meshes[i].vertexCount = 100 + i * 50;
        meshes[i].indexCount = 300 + i * 150;
        meshes[i].vertices = nullptr; // In a real app, this would point to vertex data
        meshes[i].indices = nullptr;  // In a real app, this would point to index data
        meshes[i].position[0] = i * 2.0f;  // X position
        meshes[i].position[1] = i * 1.5f;  // Y position
        meshes[i].position[2] = i * 3.0f;  // Z position
        meshes[i].rotation[0] = 0.0f;
        meshes[i].rotation[1] = 0.0f;
        meshes[i].rotation[2] = 0.0f;
        meshes[i].scale[0] = 1.0f;
        meshes[i].scale[1] = 1.0f;
        meshes[i].scale[2] = 1.0f;
        meshes[i].velocity[0] = 0.0f;
        meshes[i].velocity[1] = 0.0f;
        meshes[i].velocity[2] = 0.0f;
        meshes[i].acceleration[0] = 0.0f;
        meshes[i].acceleration[1] = 0.0f;
        meshes[i].acceleration[2] = 0.0f;
        meshes[i].mass = 1.0f;
        meshes[i].distance = 0.0f;
        meshes[i].visibility = 1.0f;
        meshes[i].lodLevel = 0;
        meshes[i].isVRObject = (i % 2 == 0); // Alternate VR objects
        meshes[i].vrDepth = 0.0f;
        meshes[i].parallaxFactor = 0.1f * i;
    }
    std::cout << "✅ Created " << meshCount << " sample meshes" << std::endl << std::endl;

    // Test advanced lighting
    std::cout << "1. Testing Advanced Lighting..." << std::endl;
    LightingParams lightingParams;
    lightingParams.ambientIntensity = 0.3f;
    lightingParams.diffuseIntensity = 0.8f;
    lightingParams.specularIntensity = 0.5f;
    lightingParams.lightPosition[0] = 10.0f;
    lightingParams.lightPosition[1] = 15.0f;
    lightingParams.lightPosition[2] = 5.0f;
    lightingParams.lightColor[0] = 1.0f;
    lightingParams.lightColor[1] = 1.0f;
    lightingParams.lightColor[2] = 1.0f;
    lightingParams.shininess = 32.0f;
    lightingParams.enableShadows = true;
    lightingParams.shadowIntensity = 0.6f;
    lightingParams.shadowBias = 0.005f;
    lightingParams.enableNormalMapping = true;
    lightingParams.normalMapStrength = 0.7f;

    if (ApplyAdvancedLighting(meshes, meshCount, &lightingParams)) {
        std::cout << "✅ Advanced lighting applied successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to apply advanced lighting!" << std::endl << std::endl;
    }

    // Test enhanced shadows
    std::cout << "2. Testing Enhanced Shadows..." << std::endl;
    ShadowParams shadowParams;
    shadowParams.shadowMapSize = 2048.0f;
    shadowParams.shadowSoftness = 0.7f;
    shadowParams.shadowDistance = 100.0f;
    shadowParams.enableCSM = true;
    shadowParams.csmSplits = 4;
    shadowParams.enablePCF = true;
    shadowParams.pcfSamples = 16.0f;
    shadowParams.shadowBias = 0.005f;

    if (ApplyEnhancedShadows(meshes, meshCount, &shadowParams)) {
        std::cout << "✅ Enhanced shadows applied successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to apply enhanced shadows!" << std::endl << std::endl;
    }

    // Test normal mapping optimization
    std::cout << "3. Testing Normal Mapping Optimization..." << std::endl;
    if (OptimizeNormalMapping(meshes, meshCount, 0.8f)) {
        std::cout << "✅ Normal mapping optimization completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to optimize normal mapping!" << std::endl << std::endl;
    }

    // Test depth-aware optimization
    std::cout << "4. Testing Depth-Aware Optimization..." << std::endl;
    float cameraPosition[3] = {0.0f, 0.0f, 0.0f};
    if (ApplyDepthAwareOptimization(meshes, meshCount, cameraPosition)) {
        std::cout << "✅ Depth-aware optimization completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to apply depth-aware optimization!" << std::endl << std::endl;
    }

    // Create a sample frame for image depth enhancement
    std::cout << "5. Testing Image Depth Enhancement..." << std::endl;
    FrameData frame;
    frame.width = 1920;
    frame.height = 1080;
    frame.pixelData = new float[frame.width * frame.height]; // In a real app, this would contain actual pixel data
    frame.motionVectorX = 0.0f;
    frame.motionVectorY = 0.0f;
    frame.frameNumber = 1;
    frame.timestamp = 0.0;
    frame.sharpness = 0.5f;
    frame.noiseLevel = 0.1f;

    if (EnhanceImageDepth(&frame, 0.7f, 1.2f)) {
        std::cout << "✅ Image depth enhancement completed successfully!" << std::endl;
        std::cout << "   Enhanced sharpness: " << frame.sharpness << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to enhance image depth!" << std::endl << std::endl;
    }

    // Clean up
    delete[] frame.pixelData;

    // Shutdown the quantum mesh system
    ShutdownQuantumMeshSystem();
    std::cout << "✅ Quantum mesh system shut down successfully!" << std::endl;

    std::cout << std::endl << "🎉 All lighting and shadow enhancement tests completed!" << std::endl;
    return 0;
}