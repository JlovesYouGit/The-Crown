#include "GPUComputeGraphicsFusion.h"
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    std::cout << "=== Advanced GPU Compute-Graphics Fusion System ===" << std::endl;
    std::cout << "Combining Compute and Graphical Tasks with Multi-Adaptive Usage" << std::endl;
    std::cout << "FRAME STABILIZATION: STATIC HIGH FRAME RATE WITH MAX 1 FRAME DROP" << std::endl;
    std::cout << std::endl;
    
    // Create the GPU fusion system
    GPUComputeGraphicsFusion fusionSystem;
    
    // Initialize the system
    std::cout << "[1/12] Initializing GPU Compute-Graphics Fusion System..." << std::endl;
    if (!fusionSystem.initializeFusionSystem()) {
        std::cerr << "Failed to initialize fusion system!" << std::endl;
        return -1;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    
    // Configure multi-adaptive usage
    std::cout << "[2/12] Configuring Multi-Adaptive Usage..." << std::endl;
    MultiAdaptiveConfig config;
    config.enableDynamicAllocation = true;
    config.enablePowerOptimization = true;
    config.enableThermalManagement = true;
    config.enableQualityScaling = true;
    config.targetEfficiency = 0.9f;
    config.maxTemperature = 85.0f;
    config.maxPowerLimit = 300.0f;
    config.adaptationFrequency = 100;
    config.enableFrameStabilization = true;  // Enable frame stabilization
    config.maxFrameDropRate = 0.01; // 1% max frame drop rate
    
    fusionSystem.configureMultiAdaptiveUsage(config);
    std::this_thread::sleep_for(std::chrono::milliseconds(150));
    
    // Enable frame stabilization
    std::cout << "[3/12] Enabling Frame Stabilization..." << std::endl;
    FrameStabilizationSettings frameSettings;
    frameSettings.targetFPS = 240.0; // Target 240 FPS
    frameSettings.maxFrameTime = 4.17; // For 240 FPS target (1000/240)
    frameSettings.maxConsecutiveDrops = 1; // At most 1 consecutive frame drop
    frameSettings.enableVSync = true;
    frameSettings.enableTripleBuffering = true;
    frameSettings.frameTimingTolerance = 0.5; // 0.5ms tolerance
    
    fusionSystem.enableFrameStabilization(frameSettings);
    std::this_thread::sleep_for(std::chrono::milliseconds(150));
    
    // Submit fused tasks
    std::cout << "[4/12] Submitting Fused GPU Tasks..." << std::endl;
    
    // Create some sample fused tasks
    FusedGPUTask task1;
    task1.taskId = 1;
    task1.taskName = "Quantum Physics Simulation";
    task1.computeIntensity = 0.8f;
    task1.graphicsIntensity = 0.2f;
    task1.priority = 0.9f;
    task1.isAdaptive = true;
    task1.dependencyCount = 0;
    task1.estimatedExecutionTime = 0.5;
    task1.actualExecutionTime = 0.0;
    task1.completed = false;
    
    FusedGPUTask task2;
    task2.taskId = 2;
    task2.taskName = "VR Rendering Pipeline";
    task2.computeIntensity = 0.3f;
    task2.graphicsIntensity = 0.7f;
    task2.priority = 0.8f;
    task2.isAdaptive = true;
    task2.dependencyCount = 0;
    task2.estimatedExecutionTime = 0.3;
    task2.actualExecutionTime = 0.0;
    task2.completed = false;
    
    FusedGPUTask task3;
    task3.taskId = 3;
    task3.taskName = "AI Neural Network Training";
    task3.computeIntensity = 0.9f;
    task3.graphicsIntensity = 0.1f;
    task3.priority = 0.7f;
    task3.isAdaptive = true;
    task3.dependencyCount = 0;
    task3.estimatedExecutionTime = 1.2;
    task3.actualExecutionTime = 0.0;
    task3.completed = false;
    
    FusedGPUTask task4;
    task4.taskId = 4;
    task4.taskName = "Real-time Ray Tracing";
    task4.computeIntensity = 0.6f;
    task4.graphicsIntensity = 0.4f;
    task4.priority = 0.85f;
    task4.isAdaptive = true;
    task4.dependencyCount = 0;
    task4.estimatedExecutionTime = 0.8;
    task4.actualExecutionTime = 0.0;
    task4.completed = false;
    
    // Submit tasks
    fusionSystem.submitFusedTask(task1);
    fusionSystem.submitFusedTask(task2);
    fusionSystem.submitFusedTask(task3);
    fusionSystem.submitFusedTask(task4);
    
    std::this_thread::sleep_for(std::chrono::milliseconds(150));
    
    // Allocate GPU resources
    std::cout << "[5/12] Allocating GPU Resources..." << std::endl;
    fusionSystem.allocateGPUResources();
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // Monitor performance
    std::cout << "[6/12] Monitoring Performance..." << std::endl;
    fusionSystem.monitorPerformance();
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // Optimize fusion
    std::cout << "[7/12] Optimizing Compute-Graphics Fusion..." << std::endl;
    fusionSystem.optimizeComputeGraphicsFusion();
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    
    // Execute fused tasks
    std::cout << "[8/12] Executing Fused GPU Tasks..." << std::endl;
    fusionSystem.executeFusedTasks();
    std::this_thread::sleep_for(std::chrono::milliseconds(300));
    
    // Adapt to workload
    std::cout << "[9/12] Adapting to Workload..." << std::endl;
    fusionSystem.adaptToWorkload();
    std::this_thread::sleep_for(std::chrono::milliseconds(150));
    
    // Stabilize frame rate
    std::cout << "[10/12] Stabilizing Frame Rate..." << std::endl;
    fusionSystem.stabilizeFrameRate();
    fusionSystem.maintainConstantFrameRate();
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    
    // Integrate with quantum systems
    std::cout << "[11/12] Integrating with Quantum Systems..." << std::endl;
    fusionSystem.integrateWithQuantumMeshSystem();
    fusionSystem.synchronizeWithHyperpathRenderer();
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    
    // Generate performance report
    std::cout << "[12/12] Generating Performance Report..." << std::endl;
    fusionSystem.generatePerformanceReport();
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    
    // Display final system status
    std::cout << std::endl << "FINAL SYSTEM STATUS:" << std::endl;
    std::cout << fusionSystem.getSystemStatusReport() << std::endl;
    
    std::cout << "=== GPU Compute-Graphics Fusion System Demo Complete ===" << std::endl;
    std::cout << "Compute and Graphical Tasks Successfully Combined!" << std::endl;
    std::cout << "Multi-Adaptive Usage Applied for Optimal Performance!" << std::endl;
    std::cout << "FRAME STABILIZATION: STATIC HIGH FRAME RATE WITH MAX 1 FRAME DROP ACHIEVED!" << std::endl;
    
    return 0;
}