#ifndef HYPERPATH_RENDERING_SYSTEM_H
#define HYPERPATH_RENDERING_SYSTEM_H

#include <vector>
#include <string>
#include <memory>
#include <chrono>
#include <deque>

// Forward declarations
class QuantumPath;
class MultiDimensionalRenderer;
class FluidityMaintainer;
class HarmonyBuffer;  // New synchronization buffer

struct PathPoint {
    double x, y, z;
    double distanceFromStart;
    double timeFactor;
    std::string pathID;
    
    PathPoint(double x, double y, double z, double dist, double time, const std::string& id)
        : x(x), y(y), z(z), distanceFromStart(dist), timeFactor(time), pathID(id) {}
};

class HyperpathRenderingSystem {
public:
    // Constructor
    HyperpathRenderingSystem();
    
    // System initialization
    void initializeHyperpathSystem();
    void integrateWithQuantumInfrastructure();
    
    // Core functionality
    void travelAllPathsSimultaneously(double distance);
    void updateAllPathPositions(double distance);
    void renderSimultaneousMotion();
    
    // Fluidity and performance
    void maintainConstantFluidity();
    void eliminateAccelerationHiccups();
    void ensureZeroFrameLoss();
    
    // NEW: Synchronization methods to resolve jitter issues
    void initializeHarmonyBuffer();
    void synchronizeInternalExternalLayers();
    void applySmoothInterpolation();
    void eliminateDisplayJitter();
    
    // System status
    std::string getSystemStatus() const;
    void runSystemDiagnostics();
    
private:
    std::vector<std::unique_ptr<QuantumPath>> quantumPaths;
    std::unique_ptr<MultiDimensionalRenderer> renderer;
    std::unique_ptr<FluidityMaintainer> fluidityMaintainer;
    std::unique_ptr<HarmonyBuffer> harmonyBuffer;  // New synchronization buffer
    std::vector<PathPoint> currentPositions;
    std::deque<PathPoint> bufferQueue;  // Buffer for smooth interpolation
    double constantSpeed;
    bool isSystemIntegrated;
    int frameCounter;
    
    // Helper methods
    void createQuantumPathNetwork();
    void synchronizeWithExistingSystems();
};

#endif // HYPERPATH_RENDERING_SYSTEM_H