/*
 * AMD Quantum VR and Far Rendering Demo
 * Demonstrates advanced VR optimization and far rendering capabilities
 */

#include "QuantumMeshBoost.h"
#include <iostream>
#include <vector>
#include <chrono>
#include <random>

int main() {
    std::cout << "🌟 AMD Quantum VR and Far Rendering Demo 🌟" << std::endl;
    std::cout << "========================================" << std::endl;
    
    // Initialize the quantum mesh system
    std::cout << "Initializing quantum mesh rendering system..." << std::endl;
    if (!InitializeQuantumMeshSystem()) {
        std::cerr << "Failed to initialize quantum mesh system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Quantum mesh system initialized successfully!" << std::endl << std::endl;
    
    // Create sample meshes for VR and far rendering
    std::cout << "Creating sample meshes for VR and far rendering..." << std::endl;
    const int meshCount = 15;
    std::vector<QuantumMesh> meshes(meshCount);
    
    // Initialize meshes with sample data at various distances
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> posDis(-500.0f, 500.0f);
    std::uniform_real_distribution<float> scaleDis(0.5f, 5.0f);
    
    for (int i = 0; i < meshCount; i++) {
        meshes[i].vertexCount = 100 + i * 20;
        meshes[i].indexCount = 300 + i * 60;
        meshes[i].vertices = nullptr; // In a real app, this would point to vertex data
        meshes[i].indices = nullptr;  // In a real app, this would point to index data
        meshes[i].position[0] = posDis(gen);
        meshes[i].position[1] = posDis(gen);
        meshes[i].position[2] = posDis(gen);
        meshes[i].rotation[0] = 0.0f;
        meshes[i].rotation[1] = 0.0f;
        meshes[i].rotation[2] = 0.0f;
        meshes[i].scale[0] = scaleDis(gen);
        meshes[i].scale[1] = scaleDis(gen);
        meshes[i].scale[2] = scaleDis(gen);
        meshes[i].velocity[0] = 0.0f;
        meshes[i].velocity[1] = 0.0f;
        meshes[i].velocity[2] = 0.0f;
        meshes[i].acceleration[0] = 0.0f;
        meshes[i].acceleration[1] = 0.0f;
        meshes[i].acceleration[2] = 0.0f;
        meshes[i].mass = 1.0f + (i * 0.1f);
        meshes[i].distance = 0.0f;
        meshes[i].visibility = 1.0f;
        meshes[i].lodLevel = 0;
        meshes[i].isVRObject = false;
        meshes[i].vrDepth = 0.0f;
        meshes[i].parallaxFactor = 0.0f;
    }
    std::cout << "✅ Created " << meshCount << " sample meshes at various distances!" << std::endl << std::endl;
    
    // Display initial mesh positions and distances
    std::cout << "Initial Mesh Positions:" << std::endl;
    for (int i = 0; i < std::min(5, meshCount); i++) {
        float distance = sqrt(meshes[i].position[0] * meshes[i].position[0] + 
                             meshes[i].position[1] * meshes[i].position[1] + 
                             meshes[i].position[2] * meshes[i].position[2]);
        std::cout << "  Mesh " << i << ": Position=(" << meshes[i].position[0] 
                  << ", " << meshes[i].position[1] << ", " << meshes[i].position[2] 
                  << "), Distance=" << distance << std::endl;
    }
    std::cout << std::endl;
    
    // Optimize meshes for VR rendering
    std::cout << "Optimizing meshes for VR rendering..." << std::endl;
    VRParams vrParams;
    vrParams.enableVR = true;
    vrParams.ipd = 0.065f; // 65mm average IPD
    vrParams.fov = 110.0f; // 110-degree FOV
    vrParams.eyeResolution[0] = 2160; // Eye width
    vrParams.eyeResolution[1] = 2160; // Eye height
    vrParams.nearPlane = 0.1f;
    vrParams.farPlane = 1000.0f;
    vrParams.stereoRendering = true;
    vrParams.depthPerception = 1.5f;
    
    auto vrStart = std::chrono::high_resolution_clock::now();
    if (OptimizeForVR(meshes.data(), meshCount, &vrParams)) {
        auto vrEnd = std::chrono::high_resolution_clock::now();
        auto vrDuration = std::chrono::duration_cast<std::chrono::milliseconds>(vrEnd - vrStart);
        std::cout << "✅ VR optimization completed in " << vrDuration.count() << "ms!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ VR optimization failed!" << std::endl << std::endl;
    }
    
    // Display VR-optimized mesh properties
    std::cout << "VR-Optimized Mesh Properties:" << std::endl;
    for (int i = 0; i < std::min(3, meshCount); i++) {
        std::cout << "  Mesh " << i << ": VR Object=" << (meshes[i].isVRObject ? "Yes" : "No")
                  << ", Depth=" << meshes[i].vrDepth 
                  << ", Parallax=" << meshes[i].parallaxFactor << std::endl;
    }
    std::cout << std::endl;
    
    // Apply far rendering optimizations
    std::cout << "Applying far rendering optimizations..." << std::endl;
    FarRenderingParams farParams;
    farParams.maxDistance = 1000.0f;
    farParams.lodLevels = 5;
    farParams.lodDistanceFactor = 1.0f;
    farParams.fogEnabled = true;
    farParams.fogDensity = 0.002f;
    farParams.fogColor[0] = 0.5f; // Gray fog
    farParams.fogColor[1] = 0.5f;
    farParams.fogColor[2] = 0.6f;
    farParams.atmosphericEffects = true;
    
    auto farStart = std::chrono::high_resolution_clock::now();
    if (ApplyFarRendering(meshes.data(), meshCount, &farParams)) {
        auto farEnd = std::chrono::high_resolution_clock::now();
        auto farDuration = std::chrono::duration_cast<std::chrono::milliseconds>(farEnd - farStart);
        std::cout << "✅ Far rendering optimizations applied in " << farDuration.count() << "ms!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Far rendering optimizations failed!" << std::endl << std::endl;
    }
    
    // Display far rendering properties
    std::cout << "Far Rendering Properties:" << std::endl;
    for (int i = 0; i < std::min(5, meshCount); i++) {
        std::cout << "  Mesh " << i << ": Distance=" << meshes[i].distance 
                  << ", Visibility=" << meshes[i].visibility << std::endl;
    }
    std::cout << std::endl;
    
    // Calculate Level of Detail for meshes
    std::cout << "Calculating Level of Detail (LOD)..." << std::endl;
    float cameraPosition[3] = {0.0f, 0.0f, 0.0f}; // Camera at origin
    
    auto lodStart = std::chrono::high_resolution_clock::now();
    if (CalculateLOD(meshes.data(), meshCount, cameraPosition)) {
        auto lodEnd = std::chrono::high_resolution_clock::now();
        auto lodDuration = std::chrono::duration_cast<std::chrono::milliseconds>(lodEnd - lodStart);
        std::cout << "✅ LOD calculation completed in " << lodDuration.count() << "ms!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ LOD calculation failed!" << std::endl << std::endl;
    }
    
    // Display LOD results
    std::cout << "LOD Results:" << std::endl;
    for (int i = 0; i < std::min(5, meshCount); i++) {
        std::cout << "  Mesh " << i << ": LOD=" << meshes[i].lodLevel 
                  << ", Visibility=" << meshes[i].visibility << std::endl;
    }
    std::cout << std::endl;
    
    // Apply parallax correction for VR depth perception
    std::cout << "Applying parallax correction for VR depth perception..." << std::endl;
    float viewerPosition[3] = {0.0f, 0.0f, 0.0f}; // Viewer at origin
    
    auto parallaxStart = std::chrono::high_resolution_clock::now();
    if (ApplyParallaxCorrection(meshes.data(), meshCount, viewerPosition)) {
        auto parallaxEnd = std::chrono::high_resolution_clock::now();
        auto parallaxDuration = std::chrono::duration_cast<std::chrono::milliseconds>(parallaxEnd - parallaxStart);
        std::cout << "✅ Parallax correction applied in " << parallaxDuration.count() << "ms!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Parallax correction failed!" << std::endl << std::endl;
    }
    
    // Optimize for atmospheric effects
    std::cout << "Optimizing for atmospheric effects..." << std::endl;
    auto atmosphereStart = std::chrono::high_resolution_clock::now();
    if (OptimizeAtmosphericEffects(meshes.data(), meshCount, &farParams)) {
        auto atmosphereEnd = std::chrono::high_resolution_clock::now();
        auto atmosphereDuration = std::chrono::duration_cast<std::chrono::milliseconds>(atmosphereEnd - atmosphereStart);
        std::cout << "✅ Atmospheric effects optimization completed in " << atmosphereDuration.count() << "ms!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Atmospheric effects optimization failed!" << std::endl << std::endl;
    }
    
    // Optimize mesh rendering using quantum parallelism
    std::cout << "Optimizing mesh rendering with quantum parallelism..." << std::endl;
    auto renderStart = std::chrono::high_resolution_clock::now();
    RenderingResult result = OptimizeMeshRendering(meshes.data(), meshCount);
    auto renderEnd = std::chrono::high_resolution_clock::now();
    auto renderDuration = std::chrono::duration_cast<std::chrono::milliseconds>(renderEnd - renderStart);
    
    if (result.success) {
        std::cout << "✅ Mesh rendering optimization completed in " << renderDuration.count() << "ms!" << std::endl;
        std::cout << "   Rendering time: " << result.renderingTime << " seconds" << std::endl;
        std::cout << "   FPS improvement: " << result.fpsImprovement << "x" << std::endl;
        std::cout << "   Rendered meshes: " << result.renderedMeshes << std::endl << std::endl;
    } else {
        std::cerr << "❌ Mesh rendering optimization failed!" << std::endl << std::endl;
    }
    
    // Shutdown the quantum mesh system
    std::cout << "Shutting down quantum mesh rendering system..." << std::endl;
    ShutdownQuantumMeshSystem();
    std::cout << "✅ Quantum mesh system shut down successfully!" << std::endl << std::endl;
    
    std::cout << "✨ Quantum VR and far rendering demo completed successfully! ✨" << std::endl;
    std::cout << "The system successfully demonstrated:" << std::endl;
    std::cout << "  • VR rendering optimization with stereo support" << std::endl;
    std::cout << "  • Far rendering with distance-based optimizations" << std::endl;
    std::cout << "  • Level of Detail (LOD) calculation" << std::endl;
    std::cout << "  • Parallax correction for depth perception" << std::endl;
    std::cout << "  • Atmospheric effects for distant objects" << std::endl;
    std::cout << "  • Quantum-parallel mesh rendering" << std::endl;
    
    return 0;
}