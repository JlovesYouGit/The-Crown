/*
 * AMD Quantum VR and Far Rendering Test
 * Simple test to verify the new VR and far rendering features
 */

#include "QuantumMeshBoost.h"
#include <iostream>

int main() {
    std::cout << "Testing AMD Quantum VR and Far Rendering Features" << std::endl;
    std::cout << "=============================================" << std::endl;
    
    // Initialize the quantum mesh system
    if (!InitializeQuantumMeshSystem()) {
        std::cerr << "❌ Failed to initialize quantum mesh system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Quantum mesh system initialized" << std::endl;
    
    // Create sample meshes
    const int meshCount = 5;
    QuantumMesh meshes[meshCount];
    
    // Initialize meshes with sample data
    for (int i = 0; i < meshCount; i++) {
        meshes[i].vertexCount = 100 + i * 50;
        meshes[i].indexCount = 300 + i * 150;
        meshes[i].vertices = nullptr;
        meshes[i].indices = nullptr;
        meshes[i].position[0] = static_cast<float>(i * 10);
        meshes[i].position[1] = static_cast<float>(i * 5);
        meshes[i].position[2] = static_cast<float>(i * 20);
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
        meshes[i].isVRObject = false;
        meshes[i].vrDepth = 0.0f;
        meshes[i].parallaxFactor = 0.0f;
    }
    
    // Test VR optimization
    VRParams vrParams;
    vrParams.enableVR = true;
    vrParams.ipd = 0.065f;
    vrParams.fov = 110.0f;
    vrParams.eyeResolution[0] = 2160;
    vrParams.eyeResolution[1] = 2160;
    vrParams.nearPlane = 0.1f;
    vrParams.farPlane = 1000.0f;
    vrParams.stereoRendering = true;
    vrParams.depthPerception = 1.5f;
    
    if (OptimizeForVR(meshes, meshCount, &vrParams)) {
        std::cout << "✅ OptimizeForVR test passed" << std::endl;
    } else {
        std::cout << "❌ OptimizeForVR test failed" << std::endl;
    }
    
    // Verify VR properties
    bool allVROptimized = true;
    for (int i = 0; i < meshCount; i++) {
        if (!meshes[i].isVRObject || meshes[i].parallaxFactor <= 0.0f) {
            allVROptimized = false;
            break;
        }
    }
    
    if (allVROptimized) {
        std::cout << "✅ Meshes successfully optimized for VR" << std::endl;
    } else {
        std::cout << "❌ Meshes not properly optimized for VR" << std::endl;
    }
    
    // Test far rendering optimizations
    FarRenderingParams farParams;
    farParams.maxDistance = 1000.0f;
    farParams.lodLevels = 5;
    farParams.lodDistanceFactor = 1.0f;
    farParams.fogEnabled = true;
    farParams.fogDensity = 0.002f;
    farParams.fogColor[0] = 0.5f;
    farParams.fogColor[1] = 0.5f;
    farParams.fogColor[2] = 0.6f;
    farParams.atmosphericEffects = true;
    
    if (ApplyFarRendering(meshes, meshCount, &farParams)) {
        std::cout << "✅ ApplyFarRendering test passed" << std::endl;
    } else {
        std::cout << "❌ ApplyFarRendering test failed" << std::endl;
    }
    
    // Test LOD calculation
    float cameraPosition[3] = {0.0f, 0.0f, 0.0f};
    if (CalculateLOD(meshes, meshCount, cameraPosition)) {
        std::cout << "✅ CalculateLOD test passed" << std::endl;
    } else {
        std::cout << "❌ CalculateLOD test failed" << std::endl;
    }
    
    // Verify LOD calculations
    bool lodCalculated = true;
    for (int i = 0; i < meshCount; i++) {
        if (meshes[i].lodLevel < 0 || meshes[i].lodLevel > 4) {
            lodCalculated = false;
            break;
        }
    }
    
    if (lodCalculated) {
        std::cout << "✅ LOD levels successfully calculated" << std::endl;
    } else {
        std::cout << "❌ LOD levels not properly calculated" << std::endl;
    }
    
    // Test parallax correction
    float viewerPosition[3] = {0.0f, 0.0f, 0.0f};
    if (ApplyParallaxCorrection(meshes, meshCount, viewerPosition)) {
        std::cout << "✅ ApplyParallaxCorrection test passed" << std::endl;
    } else {
        std::cout << "❌ ApplyParallaxCorrection test failed" << std::endl;
    }
    
    // Test atmospheric effects optimization
    if (OptimizeAtmosphericEffects(meshes, meshCount, &farParams)) {
        std::cout << "✅ OptimizeAtmosphericEffects test passed" << std::endl;
    } else {
        std::cout << "❌ OptimizeAtmosphericEffects test failed" << std::endl;
    }
    
    // Shutdown the system
    ShutdownQuantumMeshSystem();
    std::cout << "✅ All VR and far rendering tests completed" << std::endl;
    
    return 0;
}