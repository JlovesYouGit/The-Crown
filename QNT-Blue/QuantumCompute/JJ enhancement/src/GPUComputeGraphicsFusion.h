#ifndef GPU_COMPUTE_GRAPHICS_FUSION_H
#define GPU_COMPUTE_GRAPHICS_FUSION_H

#include <string>
#include <vector>
#include <memory>
#include <chrono>

// Forward declarations
class QuantumMeshProcessor;
class ComputeTaskScheduler;
class GraphicsRenderer;
class AdaptiveResourceAllocator;
class MultiTaskOptimizer;
class FrameStabilizer;  // NEW: For frame stabilization

// Structure to represent a fused GPU task that combines compute and graphics
struct FusedGPUTask {
    int taskId;
    std::string taskName;
    float computeIntensity;     // 0.0-1.0 scale of compute intensity
    float graphicsIntensity;    // 0.0-1.0 scale of graphics intensity
    float priority;             // Task priority (0.0-1.0)
    bool isAdaptive;            // Whether task can adapt its resource usage
    int dependencyCount;        // Number of task dependencies
    std::vector<int> dependencies; // Task IDs this task depends on
    double estimatedExecutionTime; // Estimated execution time in seconds
    double actualExecutionTime;    // Actual execution time in seconds
    bool completed;             // Completion status
};

// Structure to represent GPU resource allocation
struct GPUResourceAllocation {
    float computeUnits;         // Percentage of compute units allocated (0.0-1.0)
    float graphicsUnits;        // Percentage of graphics units allocated (0.0-1.0)
    float memoryBandwidth;      // Percentage of memory bandwidth allocated (0.0-1.0)
    float powerBudget;          // Percentage of power budget allocated (0.0-1.0)
    float thermalHeadroom;      // Available thermal headroom (0.0-1.0)
};

// Structure to represent adaptive performance metrics
struct AdaptivePerformanceMetrics {
    double currentFPS;          // Current frames per second
    double targetFPS;           // Target frames per second
    float gpuUtilization;       // Overall GPU utilization (0.0-1.0)
    float computeUtilization;   // Compute unit utilization (0.0-1.0)
    float graphicsUtilization;  // Graphics unit utilization (0.0-1.0)
    float memoryUtilization;    // Memory utilization (0.0-1.0)
    float powerConsumption;     // Current power consumption in watts
    float temperature;          // Current GPU temperature in Celsius
    float efficiencyRating;     // Performance per watt rating
    int frameDropCount;         // Number of frame drops recorded  // NEW
    double lastFrameTime;       // Time of last frame render      // NEW
};

// Structure to represent multi-adaptive usage configuration
struct MultiAdaptiveConfig {
    bool enableDynamicAllocation;   // Enable dynamic resource allocation
    bool enablePowerOptimization;   // Enable power optimization
    bool enableThermalManagement;   // Enable thermal management
    bool enableQualityScaling;      // Enable dynamic quality scaling
    float targetEfficiency;         // Target efficiency rating (performance/watt)
    float maxTemperature;           // Maximum allowed temperature
    float maxPowerLimit;            // Maximum power limit in watts
    int adaptationFrequency;        // How often to adapt (in milliseconds)
    bool enableFrameStabilization;  // Enable frame stabilization    // NEW
    double maxFrameDropRate;        // Maximum allowed frame drop rate  // NEW
};

// Structure to represent frame stabilization settings  // NEW
struct FrameStabilizationSettings {
    double targetFPS;               // Target frames per second
    double maxFrameTime;            // Maximum time allowed per frame (ms)
    int maxConsecutiveDrops;        // Maximum consecutive frame drops allowed
    bool enableVSync;               // Enable vertical sync
    bool enableTripleBuffering;     // Enable triple buffering
    double frameTimingTolerance;    // Frame timing tolerance (ms)
};

class GPUComputeGraphicsFusion {
public:
    // Constructor
    GPUComputeGraphicsFusion();
    
    // Initialization and setup
    bool initializeFusionSystem();
    void configureMultiAdaptiveUsage(const MultiAdaptiveConfig& config);
    
    // Task management
    int submitFusedTask(const FusedGPUTask& task);
    bool executeFusedTasks();
    void prioritizeTasks();
    
    // Resource management
    void allocateGPUResources();
    void rebalanceResources();
    GPUResourceAllocation getCurrentResourceAllocation() const;
    
    // Performance monitoring
    void monitorPerformance();
    AdaptivePerformanceMetrics getPerformanceMetrics() const;
    void adaptToWorkload();
    
    // Fusion optimization
    void optimizeComputeGraphicsFusion();
    void applyMultiAdaptiveUsage();
    void balanceComputeGraphicsLoad();
    
    // Frame stabilization (NEW)
    void enableFrameStabilization(const FrameStabilizationSettings& settings);
    void stabilizeFrameRate();
    void preventFrameDrops();
    void maintainConstantFrameRate();
    bool isFrameRateStable() const;
    
    // Integration with existing systems
    void integrateWithQuantumMeshSystem();
    void synchronizeWithHyperpathRenderer();
    
    // Status and reporting
    std::string getSystemStatusReport() const;
    void generatePerformanceReport();
    
private:
    std::vector<FusedGPUTask> taskQueue;
    std::unique_ptr<QuantumMeshProcessor> meshProcessor;
    std::unique_ptr<ComputeTaskScheduler> taskScheduler;
    std::unique_ptr<GraphicsRenderer> graphicsRenderer;
    std::unique_ptr<AdaptiveResourceAllocator> resourceAllocator;
    std::unique_ptr<MultiTaskOptimizer> taskOptimizer;
    std::unique_ptr<FrameStabilizer> frameStabilizer;  // NEW
    
    GPUResourceAllocation currentAllocation;
    AdaptivePerformanceMetrics performanceMetrics;
    MultiAdaptiveConfig adaptiveConfig;
    FrameStabilizationSettings frameSettings;  // NEW
    
    bool isInitialized;
    bool isOptimizing;
    bool isFrameStabilizationEnabled;  // NEW
    std::chrono::steady_clock::time_point lastAdaptationTime;
    std::chrono::steady_clock::time_point lastFrameTime;  // NEW
    
    // Helper methods
    void initializeResourceAllocation();
    void updatePerformanceMetrics();
    void adjustResourceAllocation();
    void optimizeTaskExecutionOrder();
    void applyThermalManagement();
    void applyPowerOptimization();
    float calculateEfficiencyRating() const;
    void recordFrameTime();  // NEW
    bool detectFrameDrop();  // NEW
};

#endif // GPU_COMPUTE_GRAPHICS_FUSION_H