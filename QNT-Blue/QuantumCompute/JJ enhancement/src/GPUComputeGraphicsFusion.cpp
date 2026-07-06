#include "GPUComputeGraphicsFusion.h"
#include <iostream>
#include <algorithm>
#include <thread>
#include <chrono>
#include <random>
#include <cmath>
#include <deque>

// Forward declaration classes
class QuantumMeshProcessor {
public:
    void processMeshes() {
        // Simulate mesh processing
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    
    double getProcessingEfficiency() const {
        return 0.95; // 95% efficiency
    }
};

class ComputeTaskScheduler {
public:
    void scheduleTasks() {
        // Simulate task scheduling
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    
    int getPendingTasks() const {
        return 15; // 15 pending tasks
    }
};

class GraphicsRenderer {
public:
    void renderFrames() {
        // Simulate frame rendering
        std::this_thread::sleep_for(std::chrono::milliseconds(8));
    }
    
    double getCurrentFPS() const {
        return 240.0; // 240 FPS
    }
    
    float getRenderEfficiency() const {
        return 0.88; // 88% efficiency
    }
};

class AdaptiveResourceAllocator {
public:
    void allocateResources(float computeRatio, float graphicsRatio) {
        // Simulate resource allocation
        std::this_thread::sleep_for(std::chrono::milliseconds(3));
    }
    
    float getAllocatedCompute() const {
        return 0.65; // 65% compute allocation
    }
    
    float getAllocatedGraphics() const {
        return 0.35; // 35% graphics allocation
    }
};

class MultiTaskOptimizer {
public:
    void optimizeTaskExecution() {
        // Simulate task optimization
        std::this_thread::sleep_for(std::chrono::milliseconds(7));
    }
    
    int getOptimizedTaskCount() const {
        return 25; // 25 optimized tasks
    }
    
    float getOptimizationFactor() const {
        return 1.4; // 40% performance improvement
    }
};

// NEW: Frame Stabilizer class for frame rate stabilization
class FrameStabilizer {
private:
    std::deque<double> frameTimes;
    int maxFrameHistory;
    double targetFrameTime;
    int consecutiveDrops;
    int maxConsecutiveDrops;
    
public:
    FrameStabilizer() : maxFrameHistory(60), targetFrameTime(16.67), 
                       consecutiveDrops(0), maxConsecutiveDrops(3) {}
    
    void setTargetFPS(double fps) {
        targetFrameTime = 1000.0 / fps; // Convert FPS to ms per frame
    }
    
    void setMaxConsecutiveDrops(int maxDrops) {
        maxConsecutiveDrops = maxDrops;
    }
    
    void recordFrameTime(double frameTimeMs) {
        frameTimes.push_back(frameTimeMs);
        if (frameTimes.size() > maxFrameHistory) {
            frameTimes.pop_front();
        }
        
        // Check if this frame was a drop
        if (frameTimeMs > targetFrameTime * 1.5) { // 50% over target time
            consecutiveDrops++;
        } else {
            consecutiveDrops = 0; // Reset counter for good frames
        }
    }
    
    bool isFrameRateStable() const {
        if (frameTimes.size() < 10) return true; // Not enough data yet
        
        // Calculate average frame time
        double sum = 0;
        for (double time : frameTimes) {
            sum += time;
        }
        double average = sum / frameTimes.size();
        
        // Check if average is within acceptable range
        return (average <= targetFrameTime * 1.1) && (consecutiveDrops <= maxConsecutiveDrops);
    }
    
    double getAverageFrameTime() const {
        if (frameTimes.empty()) return 0.0;
        
        double sum = 0;
        for (double time : frameTimes) {
            sum += time;
        }
        return sum / frameTimes.size();
    }
    
    int getConsecutiveDrops() const {
        return consecutiveDrops;
    }
    
    void reset() {
        frameTimes.clear();
        consecutiveDrops = 0;
    }
};

GPUComputeGraphicsFusion::GPUComputeGraphicsFusion() 
    : isInitialized(false), isOptimizing(false), isFrameStabilizationEnabled(false) {
    // Initialize with default resource allocation
    currentAllocation.computeUnits = 0.5f;
    currentAllocation.graphicsUnits = 0.5f;
    currentAllocation.memoryBandwidth = 0.5f;
    currentAllocation.powerBudget = 0.5f;
    currentAllocation.thermalHeadroom = 0.7f;
    
    // Initialize with default performance metrics
    performanceMetrics.currentFPS = 120.0;
    performanceMetrics.targetFPS = 240.0;
    performanceMetrics.gpuUtilization = 0.6f;
    performanceMetrics.computeUtilization = 0.5f;
    performanceMetrics.graphicsUtilization = 0.7f;
    performanceMetrics.memoryUtilization = 0.4f;
    performanceMetrics.powerConsumption = 150.0f;
    performanceMetrics.temperature = 65.0f;
    performanceMetrics.efficiencyRating = 0.8f;
    performanceMetrics.frameDropCount = 0;  // NEW
    performanceMetrics.lastFrameTime = 0.0; // NEW
    
    // Initialize with default adaptive configuration
    adaptiveConfig.enableDynamicAllocation = true;
    adaptiveConfig.enablePowerOptimization = true;
    adaptiveConfig.enableThermalManagement = true;
    adaptiveConfig.enableQualityScaling = true;
    adaptiveConfig.targetEfficiency = 0.9f;
    adaptiveConfig.maxTemperature = 85.0f;
    adaptiveConfig.maxPowerLimit = 300.0f;
    adaptiveConfig.adaptationFrequency = 100; // 100ms
    adaptiveConfig.enableFrameStabilization = true;  // NEW
    adaptiveConfig.maxFrameDropRate = 0.01; // 1% max frame drop rate  // NEW
    
    // Initialize frame stabilization settings  // NEW
    frameSettings.targetFPS = 240.0;
    frameSettings.maxFrameTime = 16.67; // For 60 FPS target
    frameSettings.maxConsecutiveDrops = 1; // At most 1 consecutive frame drop
    frameSettings.enableVSync = true;
    frameSettings.enableTripleBuffering = true;
    frameSettings.frameTimingTolerance = 1.0; // 1ms tolerance
    
    lastAdaptationTime = std::chrono::steady_clock::now();
    lastFrameTime = std::chrono::steady_clock::now(); // NEW
}

bool GPUComputeGraphicsFusion::initializeFusionSystem() {
    std::cout << "Initializing GPU Compute-Graphics Fusion System..." << std::endl;
    
    // Initialize component systems
    meshProcessor = std::make_unique<QuantumMeshProcessor>();
    taskScheduler = std::make_unique<ComputeTaskScheduler>();
    graphicsRenderer = std::make_unique<GraphicsRenderer>();
    resourceAllocator = std::make_unique<AdaptiveResourceAllocator>();
    taskOptimizer = std::make_unique<MultiTaskOptimizer>();
    frameStabilizer = std::make_unique<FrameStabilizer>(); // NEW
    
    // Configure frame stabilizer
    if (frameStabilizer) {
        frameStabilizer->setTargetFPS(frameSettings.targetFPS);
        frameStabilizer->setMaxConsecutiveDrops(frameSettings.maxConsecutiveDrops);
    }
    
    // Simulate initialization time
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    isInitialized = true;
    std::cout << "GPU Compute-Graphics Fusion System initialized successfully!" << std::endl;
    
    return true;
}

void GPUComputeGraphicsFusion::configureMultiAdaptiveUsage(const MultiAdaptiveConfig& config) {
    adaptiveConfig = config;
    std::cout << "Multi-adaptive usage configuration updated." << std::endl;
}

int GPUComputeGraphicsFusion::submitFusedTask(const FusedGPUTask& task) {
    if (!isInitialized) {
        std::cerr << "Error: System not initialized!" << std::endl;
        return -1;
    }
    
    taskQueue.push_back(task);
    std::cout << "Submitted fused GPU task: " << task.taskName << " (ID: " << task.taskId << ")" << std::endl;
    
    return task.taskId;
}

bool GPUComputeGraphicsFusion::executeFusedTasks() {
    if (!isInitialized) {
        std::cerr << "Error: System not initialized!" << std::endl;
        return false;
    }
    
    if (taskQueue.empty()) {
        std::cout << "No tasks to execute." << std::endl;
        return true;
    }
    
    std::cout << "Executing " << taskQueue.size() << " fused GPU tasks..." << std::endl;
    
    // Prioritize tasks before execution
    prioritizeTasks();
    
    // Execute tasks
    for (auto& task : taskQueue) {
        if (!task.completed) {
            auto startTime = std::chrono::high_resolution_clock::now();
            
            std::cout << "Executing task: " << task.taskName << "..." << std::endl;
            
            // Simulate task execution based on intensity
            int executionTime = static_cast<int>(10 * (task.computeIntensity + task.graphicsIntensity));
            std::this_thread::sleep_for(std::chrono::milliseconds(executionTime));
            
            auto endTime = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(endTime - startTime);
            
            task.actualExecutionTime = duration.count() / 1000000.0;
            task.completed = true;
            
            std::cout << "  Completed task: " << task.taskName 
                      << " (Execution time: " << task.actualExecutionTime << "s)" << std::endl;
        }
    }
    
    // Clear completed tasks
    taskQueue.erase(
        std::remove_if(taskQueue.begin(), taskQueue.end(), 
                      [](const FusedGPUTask& task) { return task.completed; }),
        taskQueue.end()
    );
    
    std::cout << "All fused GPU tasks executed successfully!" << std::endl;
    return true;
}

void GPUComputeGraphicsFusion::prioritizeTasks() {
    // Sort tasks by priority (highest first) and then by intensity
    std::sort(taskQueue.begin(), taskQueue.end(), 
              [](const FusedGPUTask& a, const FusedGPUTask& b) {
                  if (a.priority != b.priority) {
                      return a.priority > b.priority; // Higher priority first
                  }
                  // If priorities are equal, higher intensity tasks first
                  return (a.computeIntensity + a.graphicsIntensity) > 
                         (b.computeIntensity + b.graphicsIntensity);
              });
    
    std::cout << "Tasks prioritized for execution." << std::endl;
}

void GPUComputeGraphicsFusion::allocateGPUResources() {
    if (!isInitialized) {
        std::cerr << "Error: System not initialized!" << std::endl;
        return;
    }
    
    std::cout << "Allocating GPU resources for fused compute-graphics tasks..." << std::endl;
    
    // Calculate optimal resource allocation based on task queue
    float totalComputeIntensity = 0.0f;
    float totalGraphicsIntensity = 0.0f;
    
    for (const auto& task : taskQueue) {
        if (!task.completed) {
            totalComputeIntensity += task.computeIntensity;
            totalGraphicsIntensity += task.graphicsIntensity;
        }
    }
    
    float totalIntensity = totalComputeIntensity + totalGraphicsIntensity;
    if (totalIntensity > 0) {
        currentAllocation.computeUnits = totalComputeIntensity / totalIntensity;
        currentAllocation.graphicsUnits = totalGraphicsIntensity / totalIntensity;
    } else {
        // Default 50-50 split if no tasks
        currentAllocation.computeUnits = 0.5f;
        currentAllocation.graphicsUnits = 0.5f;
    }
    
    // Ensure minimum allocation for both
    if (currentAllocation.computeUnits < 0.1f) currentAllocation.computeUnits = 0.1f;
    if (currentAllocation.graphicsUnits < 0.1f) currentAllocation.graphicsUnits = 0.1f;
    
    // Normalize to sum to 1.0
    float sum = currentAllocation.computeUnits + currentAllocation.graphicsUnits;
    currentAllocation.computeUnits /= sum;
    currentAllocation.graphicsUnits /= sum;
    
    std::cout << "  Compute Units: " << (currentAllocation.computeUnits * 100) << "%" << std::endl;
    std::cout << "  Graphics Units: " << (currentAllocation.graphicsUnits * 100) << "%" << std::endl;
    
    // Apply allocation to resource allocator
    if (resourceAllocator) {
        resourceAllocator->allocateResources(
            currentAllocation.computeUnits, 
            currentAllocation.graphicsUnits
        );
    }
}

void GPUComputeGraphicsFusion::rebalanceResources() {
    std::cout << "Rebalancing GPU resources..." << std::endl;
    
    // Get current utilization metrics
    updatePerformanceMetrics();
    
    // Adjust allocation based on utilization
    if (performanceMetrics.computeUtilization > 0.8f && 
        performanceMetrics.graphicsUtilization < 0.6f) {
        // Shift more resources to compute
        currentAllocation.computeUnits = std::min(0.9f, currentAllocation.computeUnits + 0.1f);
        currentAllocation.graphicsUnits = 1.0f - currentAllocation.computeUnits;
    } else if (performanceMetrics.graphicsUtilization > 0.8f && 
               performanceMetrics.computeUtilization < 0.6f) {
        // Shift more resources to graphics
        currentAllocation.graphicsUnits = std::min(0.9f, currentAllocation.graphicsUnits + 0.1f);
        currentAllocation.computeUnits = 1.0f - currentAllocation.graphicsUnits;
    }
    
    std::cout << "  Rebalanced allocation - Compute: " << (currentAllocation.computeUnits * 100) 
              << "%, Graphics: " << (currentAllocation.graphicsUnits * 100) << "%" << std::endl;
}

GPUResourceAllocation GPUComputeGraphicsFusion::getCurrentResourceAllocation() const {
    return currentAllocation;
}

void GPUComputeGraphicsFusion::monitorPerformance() {
    if (!isInitialized) {
        std::cerr << "Error: System not initialized!" << std::endl;
        return;
    }
    
    std::cout << "Monitoring GPU performance metrics..." << std::endl;
    
    // Update performance metrics
    updatePerformanceMetrics();
    
    std::cout << "  Current FPS: " << performanceMetrics.currentFPS << std::endl;
    std::cout << "  GPU Utilization: " << (performanceMetrics.gpuUtilization * 100) << "%" << std::endl;
    std::cout << "  Compute Utilization: " << (performanceMetrics.computeUtilization * 100) << "%" << std::endl;
    std::cout << "  Graphics Utilization: " << (performanceMetrics.graphicsUtilization * 100) << "%" << std::endl;
    std::cout << "  Memory Utilization: " << (performanceMetrics.memoryUtilization * 100) << "%" << std::endl;
    std::cout << "  Power Consumption: " << performanceMetrics.powerConsumption << "W" << std::endl;
    std::cout << "  Temperature: " << performanceMetrics.temperature << "°C" << std::endl;
    std::cout << "  Efficiency Rating: " << performanceMetrics.efficiencyRating << std::endl;
    std::cout << "  Frame Drops: " << performanceMetrics.frameDropCount << std::endl; // NEW
}

AdaptivePerformanceMetrics GPUComputeGraphicsFusion::getPerformanceMetrics() const {
    return performanceMetrics;
}

void GPUComputeGraphicsFusion::adaptToWorkload() {
    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastAdaptationTime);
    
    // Only adapt if enough time has passed
    if (duration.count() >= adaptiveConfig.adaptationFrequency) {
        std::cout << "Adapting to current workload..." << std::endl;
        
        // Apply multi-adaptive usage
        applyMultiAdaptiveUsage();
        
        // Update last adaptation time
        lastAdaptationTime = now;
    }
}

void GPUComputeGraphicsFusion::optimizeComputeGraphicsFusion() {
    if (!isInitialized || isOptimizing) {
        return;
    }
    
    isOptimizing = true;
    std::cout << "Optimizing Compute-Graphics Fusion..." << std::endl;
    
    // Optimize task execution order
    optimizeTaskExecutionOrder();
    
    // Balance compute and graphics load
    balanceComputeGraphicsLoad();
    
    // Apply multi-adaptive usage
    applyMultiAdaptiveUsage();
    
    // Stabilize frame rate if enabled
    if (isFrameStabilizationEnabled) {
        stabilizeFrameRate();
    }
    
    isOptimizing = false;
    std::cout << "Compute-Graphics Fusion optimization completed!" << std::endl;
}

void GPUComputeGraphicsFusion::applyMultiAdaptiveUsage() {
    std::cout << "Applying multi-adaptive usage optimizations..." << std::endl;
    
    // Apply dynamic allocation if enabled
    if (adaptiveConfig.enableDynamicAllocation) {
        allocateGPUResources();
    }
    
    // Apply power optimization if enabled
    if (adaptiveConfig.enablePowerOptimization) {
        applyPowerOptimization();
    }
    
    // Apply thermal management if enabled
    if (adaptiveConfig.enableThermalManagement) {
        applyThermalManagement();
    }
    
    // Update performance metrics
    updatePerformanceMetrics();
}

void GPUComputeGraphicsFusion::balanceComputeGraphicsLoad() {
    std::cout << "Balancing compute and graphics workload..." << std::endl;
    
    // Get current utilization
    updatePerformanceMetrics();
    
    // If compute is overloaded and graphics is underloaded, shift resources
    if (performanceMetrics.computeUtilization > 0.85f && 
        performanceMetrics.graphicsUtilization < 0.7f) {
        currentAllocation.computeUnits = std::max(0.1f, currentAllocation.computeUnits - 0.1f);
        currentAllocation.graphicsUnits = 1.0f - currentAllocation.computeUnits;
        std::cout << "  Shifting resources toward graphics" << std::endl;
    }
    // If graphics is overloaded and compute is underloaded, shift resources
    else if (performanceMetrics.graphicsUtilization > 0.85f && 
             performanceMetrics.computeUtilization < 0.7f) {
        currentAllocation.graphicsUnits = std::max(0.1f, currentAllocation.graphicsUnits - 0.1f);
        currentAllocation.computeUnits = 1.0f - currentAllocation.graphicsUnits;
        std::cout << "  Shifting resources toward compute" << std::endl;
    }
    
    std::cout << "  Balanced allocation - Compute: " << (currentAllocation.computeUnits * 100) 
              << "%, Graphics: " << (currentAllocation.graphicsUnits * 100) << "%" << std::endl;
}

// NEW: Frame stabilization methods
void GPUComputeGraphicsFusion::enableFrameStabilization(const FrameStabilizationSettings& settings) {
    frameSettings = settings;
    isFrameStabilizationEnabled = true;
    
    // Configure frame stabilizer
    if (frameStabilizer) {
        frameStabilizer->setTargetFPS(frameSettings.targetFPS);
        frameStabilizer->setMaxConsecutiveDrops(frameSettings.maxConsecutiveDrops);
    }
    
    std::cout << "Frame stabilization enabled with target FPS: " << frameSettings.targetFPS << std::endl;
    std::cout << "Maximum consecutive frame drops allowed: " << frameSettings.maxConsecutiveDrops << std::endl;
}

void GPUComputeGraphicsFusion::stabilizeFrameRate() {
    std::cout << "Stabilizing frame rate..." << std::endl;
    
    if (!isFrameStabilizationEnabled) {
        std::cout << "  Frame stabilization not enabled." << std::endl;
        return;
    }
    
    // Record current frame time
    recordFrameTime();
    
    // Check for frame drops
    if (detectFrameDrop()) {
        std::cout << "  Frame drop detected! Taking corrective action..." << std::endl;
        preventFrameDrops();
    }
    
    // Maintain constant frame rate
    maintainConstantFrameRate();
    
    // Check stability
    if (isFrameRateStable()) {
        std::cout << "  Frame rate is stable." << std::endl;
    } else {
        std::cout << "  Frame rate needs adjustment." << std::endl;
    }
}

void GPUComputeGraphicsFusion::preventFrameDrops() {
    std::cout << "Preventing frame drops..." << std::endl;
    
    // Reduce graphics quality temporarily if needed
    if (performanceMetrics.graphicsUtilization > 0.95f) {
        std::cout << "  Reducing graphics quality to prevent frame drops..." << std::endl;
        currentAllocation.graphicsUnits = std::max(0.1f, currentAllocation.graphicsUnits - 0.05f);
        currentAllocation.computeUnits = 1.0f - currentAllocation.graphicsUnits;
    }
    
    // Prioritize critical rendering tasks
    std::cout << "  Prioritizing critical rendering tasks..." << std::endl;
    
    // Increase GPU clock if thermal headroom available
    if (performanceMetrics.temperature < adaptiveConfig.maxTemperature * 0.8f) {
        std::cout << "  Boosting GPU performance to maintain frame rate..." << std::endl;
        currentAllocation.powerBudget = std::min(1.0f, currentAllocation.powerBudget + 0.1f);
    }
}

void GPUComputeGraphicsFusion::maintainConstantFrameRate() {
    std::cout << "Maintaining constant frame rate..." << std::endl;
    
    // Ensure we're targeting the correct FPS
    performanceMetrics.targetFPS = frameSettings.targetFPS;
    
    // Adjust resource allocation to maintain target FPS
    if (frameStabilizer && !frameStabilizer->isFrameRateStable()) {
        std::cout << "  Adjusting resources to maintain target frame rate..." << std::endl;
        
        // If we're below target FPS, try to optimize
        double avgFrameTime = frameStabilizer->getAverageFrameTime();
        double targetFrameTime = 1000.0 / frameSettings.targetFPS;
        
        if (avgFrameTime > targetFrameTime * 1.1) {
            // We're running slow, try to optimize
            std::cout << "  Frame time is " << avgFrameTime << "ms, target is " << targetFrameTime << "ms" << std::endl;
            
            // Try different optimization strategies
            if (performanceMetrics.computeUtilization < 0.8f) {
                // Shift more resources to graphics
                currentAllocation.graphicsUnits = std::min(0.9f, currentAllocation.graphicsUnits + 0.05f);
                currentAllocation.computeUnits = 1.0f - currentAllocation.graphicsUnits;
                std::cout << "  Shifting resources to graphics for better frame rate" << std::endl;
            }
        }
    }
}

bool GPUComputeGraphicsFusion::isFrameRateStable() const {
    if (frameStabilizer) {
        return frameStabilizer->isFrameRateStable();
    }
    return true; // Assume stable if no stabilizer
}

void GPUComputeGraphicsFusion::integrateWithQuantumMeshSystem() {
    std::cout << "Integrating with Quantum Mesh System..." << std::endl;
    
    // Simulate integration
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    
    if (meshProcessor) {
        meshProcessor->processMeshes();
        std::cout << "  Quantum mesh processing efficiency: " 
                  << (meshProcessor->getProcessingEfficiency() * 100) << "%" << std::endl;
    }
    
    std::cout << "Quantum Mesh System integration completed!" << std::endl;
}

void GPUComputeGraphicsFusion::synchronizeWithHyperpathRenderer() {
    std::cout << "Synchronizing with Hyperpath Renderer..." << std::endl;
    
    // Simulate synchronization
    std::this_thread::sleep_for(std::chrono::milliseconds(30));
    
    std::cout << "Hyperpath Renderer synchronization completed!" << std::endl;
}

std::string GPUComputeGraphicsFusion::getSystemStatusReport() const {
    std::string report = "GPU Compute-Graphics Fusion System Status Report:\n";
    report += "  System Initialized: " + std::string(isInitialized ? "YES" : "NO") + "\n";
    report += "  Tasks in Queue: " + std::to_string(taskQueue.size()) + "\n";
    report += "  Compute Units Allocation: " + std::to_string(currentAllocation.computeUnits * 100) + "%\n";
    report += "  Graphics Units Allocation: " + std::to_string(currentAllocation.graphicsUnits * 100) + "%\n";
    report += "  Current FPS: " + std::to_string(performanceMetrics.currentFPS) + "\n";
    report += "  GPU Utilization: " + std::to_string(performanceMetrics.gpuUtilization * 100) + "%\n";
    report += "  Efficiency Rating: " + std::to_string(performanceMetrics.efficiencyRating) + "\n";
    report += "  Temperature: " + std::to_string(performanceMetrics.temperature) + "°C\n";
    report += "  Power Consumption: " + std::to_string(performanceMetrics.powerConsumption) + "W\n";
    report += "  Frame Drops: " + std::to_string(performanceMetrics.frameDropCount) + "\n"; // NEW
    report += "  Frame Stabilization: " + std::string(isFrameStabilizationEnabled ? "ENABLED" : "DISABLED") + "\n"; // NEW
    
    return report;
}

void GPUComputeGraphicsFusion::generatePerformanceReport() {
    std::cout << "Generating Performance Report..." << std::endl;
    
    // Update metrics before generating report
    updatePerformanceMetrics();
    
    std::cout << "\n=== GPU COMPUTE-GRAPHICS FUSION PERFORMANCE REPORT ===" << std::endl;
    std::cout << "System Status: " << (isInitialized ? "OPERATIONAL" : "NOT INITIALIZED") << std::endl;
    std::cout << "Tasks in Queue: " << taskQueue.size() << std::endl;
    std::cout << "Current FPS: " << performanceMetrics.currentFPS << " (Target: " << performanceMetrics.targetFPS << ")" << std::endl;
    std::cout << "GPU Utilization: " << (performanceMetrics.gpuUtilization * 100) << "%" << std::endl;
    std::cout << "Compute Utilization: " << (performanceMetrics.computeUtilization * 100) << "%" << std::endl;
    std::cout << "Graphics Utilization: " << (performanceMetrics.graphicsUtilization * 100) << "%" << std::endl;
    std::cout << "Memory Utilization: " << (performanceMetrics.memoryUtilization * 100) << "%" << std::endl;
    std::cout << "Power Consumption: " << performanceMetrics.powerConsumption << "W" << std::endl;
    std::cout << "Temperature: " << performanceMetrics.temperature << "°C" << std::endl;
    std::cout << "Efficiency Rating: " << performanceMetrics.efficiencyRating << " (Performance/Watt)" << std::endl;
    std::cout << "Frame Drops: " << performanceMetrics.frameDropCount << std::endl; // NEW
    std::cout << "Frame Stabilization: " << (isFrameStabilizationEnabled ? "ENABLED" : "DISABLED") << std::endl; // NEW
    
    if (taskOptimizer) {
        std::cout << "Optimized Tasks: " << taskOptimizer->getOptimizedTaskCount() << std::endl;
        std::cout << "Optimization Factor: " << taskOptimizer->getOptimizationFactor() << "x" << std::endl;
    }
    
    if (taskScheduler) {
        std::cout << "Pending Compute Tasks: " << taskScheduler->getPendingTasks() << std::endl;
    }
    
    std::cout << "Resource Allocation:" << std::endl;
    std::cout << "  Compute Units: " << (currentAllocation.computeUnits * 100) << "%" << std::endl;
    std::cout << "  Graphics Units: " << (currentAllocation.graphicsUnits * 100) << "%" << std::endl;
    std::cout << "  Memory Bandwidth: " << (currentAllocation.memoryBandwidth * 100) << "%" << std::endl;
    std::cout << "  Power Budget: " << (currentAllocation.powerBudget * 100) << "%" << std::endl;
    std::cout << "  Thermal Headroom: " << (currentAllocation.thermalHeadroom * 100) << "%" << std::endl;
    std::cout << "=====================================================" << std::endl;
}

void GPUComputeGraphicsFusion::initializeResourceAllocation() {
    // Initialize with balanced allocation
    currentAllocation.computeUnits = 0.5f;
    currentAllocation.graphicsUnits = 0.5f;
    currentAllocation.memoryBandwidth = 0.5f;
    currentAllocation.powerBudget = 0.5f;
    currentAllocation.thermalHeadroom = 0.7f;
}

void GPUComputeGraphicsFusion::updatePerformanceMetrics() {
    // Simulate updating performance metrics
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_real_distribution<float> dis(0.0f, 0.1f);
    
    // Add some randomness to metrics
    performanceMetrics.gpuUtilization = 0.6f + dis(gen);
    performanceMetrics.computeUtilization = 0.5f + dis(gen);
    performanceMetrics.graphicsUtilization = 0.7f + dis(gen);
    performanceMetrics.memoryUtilization = 0.4f + dis(gen);
    performanceMetrics.powerConsumption = 150.0f + (dis(gen) * 50.0f);
    performanceMetrics.temperature = 65.0f + (dis(gen) * 10.0f);
    performanceMetrics.efficiencyRating = calculateEfficiencyRating();
    
    // Get metrics from components
    if (graphicsRenderer) {
        performanceMetrics.currentFPS = graphicsRenderer->getCurrentFPS();
    }
    
    // Update frame time
    recordFrameTime();
}

void GPUComputeGraphicsFusion::adjustResourceAllocation() {
    // Adjust allocation based on current metrics
    if (performanceMetrics.computeUtilization > 0.8f) {
        currentAllocation.computeUnits = std::min(0.9f, currentAllocation.computeUnits + 0.05f);
    } else if (performanceMetrics.computeUtilization < 0.3f) {
        currentAllocation.computeUnits = std::max(0.1f, currentAllocation.computeUnits - 0.05f);
    }
    
    if (performanceMetrics.graphicsUtilization > 0.8f) {
        currentAllocation.graphicsUnits = std::min(0.9f, currentAllocation.graphicsUnits + 0.05f);
    } else if (performanceMetrics.graphicsUtilization < 0.3f) {
        currentAllocation.graphicsUnits = std::max(0.1f, currentAllocation.graphicsUnits - 0.05f);
    }
    
    // Normalize
    float sum = currentAllocation.computeUnits + currentAllocation.graphicsUnits;
    if (sum > 0) {
        currentAllocation.computeUnits /= sum;
        currentAllocation.graphicsUnits /= sum;
    }
}

void GPUComputeGraphicsFusion::optimizeTaskExecutionOrder() {
    std::cout << "Optimizing task execution order..." << std::endl;
    
    if (taskOptimizer) {
        taskOptimizer->optimizeTaskExecution();
        std::cout << "  Optimized " << taskOptimizer->getOptimizedTaskCount() << " tasks" << std::endl;
        std::cout << "  Performance improvement: " << ((taskOptimizer->getOptimizationFactor() - 1.0f) * 100) << "%" << std::endl;
    }
}

void GPUComputeGraphicsFusion::applyThermalManagement() {
    std::cout << "Applying thermal management..." << std::endl;
    
    // If temperature is too high, reduce power
    if (performanceMetrics.temperature > adaptiveConfig.maxTemperature * 0.9f) {
        currentAllocation.powerBudget = std::max(0.1f, currentAllocation.powerBudget - 0.1f);
        std::cout << "  Reducing power budget to manage temperature" << std::endl;
    } else if (performanceMetrics.temperature < adaptiveConfig.maxTemperature * 0.7f) {
        currentAllocation.powerBudget = std::min(1.0f, currentAllocation.powerBudget + 0.05f);
        std::cout << "  Increasing power budget - thermal headroom available" << std::endl;
    }
}

void GPUComputeGraphicsFusion::applyPowerOptimization() {
    std::cout << "Applying power optimization..." << std::endl;
    
    // Adjust power based on efficiency target
    float currentEfficiency = calculateEfficiencyRating();
    if (currentEfficiency < adaptiveConfig.targetEfficiency) {
        // Increase power to improve efficiency
        currentAllocation.powerBudget = std::min(1.0f, currentAllocation.powerBudget + 0.05f);
        std::cout << "  Increasing power budget to improve efficiency" << std::endl;
    } else if (currentEfficiency > adaptiveConfig.targetEfficiency * 1.1f) {
        // Reduce power if we're significantly above target
        currentAllocation.powerBudget = std::max(0.1f, currentAllocation.powerBudget - 0.05f);
        std::cout << "  Reducing power budget - efficiency target exceeded" << std::endl;
    }
}

float GPUComputeGraphicsFusion::calculateEfficiencyRating() const {
    // Calculate efficiency as performance per watt
    if (performanceMetrics.powerConsumption > 0) {
        // Use FPS per watt as efficiency metric
        return static_cast<float>(performanceMetrics.currentFPS / performanceMetrics.powerConsumption);
    }
    return 0.0f;
}

// NEW: Frame time recording and drop detection
void GPUComputeGraphicsFusion::recordFrameTime() {
    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(now - lastFrameTime);
    double frameTimeMs = duration.count() / 1000.0;
    
    performanceMetrics.lastFrameTime = frameTimeMs;
    lastFrameTime = now;
    
    // Record in frame stabilizer
    if (frameStabilizer) {
        frameStabilizer->recordFrameTime(frameTimeMs);
    }
}

bool GPUComputeGraphicsFusion::detectFrameDrop() {
    // A frame drop is detected if frame time exceeds target by more than tolerance
    double targetFrameTime = 1000.0 / frameSettings.targetFPS;
    double maxAllowedTime = targetFrameTime + frameSettings.frameTimingTolerance;
    
    if (performanceMetrics.lastFrameTime > maxAllowedTime) {
        performanceMetrics.frameDropCount++;
        return true;
    }
    
    return false;
}