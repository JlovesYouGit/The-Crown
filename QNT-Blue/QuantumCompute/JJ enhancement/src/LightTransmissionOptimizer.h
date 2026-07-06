#ifndef LIGHT_TRANSMISSION_OPTIMIZER_H
#define LIGHT_TRANSMISSION_OPTIMIZER_H

#include <string>
#include <vector>
#include <memory>
#include <chrono>

// Forward declarations
class FiberOpticAnalyzer;
class EthernetInterface;
class RouterConnector;
class ModemInterface;
class LightPathCalculator;
class DerivativeCurveOptimizer;

// Structure to represent network connection information
struct NetworkConnectionInfo {
    std::string ethernetInterface;
    std::string routerAddress;
    std::string modemAddress;
    std::string fiberEntryPoint;
    double ethernetSpeedMbps;
    double routerSpeedMbps;
    double modemSpeedMbps;
    double fiberSpeedGbps;
};

// Structure to represent light transmission metrics
struct LightTransmissionMetrics {
    double lightSpeedConstant;      // Speed of light in fiber (c. 200,000 km/s)
    double lightDelayConstant;      // Base delay constant (0.2)
    double currentLightDelay;       // Current measured delay
    double optimalLightDelay;       // Target delay (0.1)
    double lightBendAngle;          // Angle of light bending in fiber
    double currentAdjustment;       // Current adjustment factor
    double dataTransmissionRate;    // Current data rate
    double signalQuality;           // Signal quality metric (0.0-1.0)
    double bandwidthUtilization;    // Bandwidth utilization percentage
};

// Structure to represent derivative curve calculations
struct DerivativeCurveData {
    std::vector<double> timePoints;
    std::vector<double> lightPathValues;
    std::vector<double> derivatives;
    double optimalCurveFactor;
    double curveAdjustmentNeeded;
    bool needsRecalculation;
};

class LightTransmissionOptimizer {
public:
    // Constructor
    LightTransmissionOptimizer();
    
    // Initialization and setup
    bool initializeOptimizer();
    void configureNetworkConnection(const NetworkConnectionInfo& connectionInfo);
    
    // Network interface management
    void detectEthernetConnection();
    void connectToRouter();
    void establishModemLink();
    void initializeFiberConnection();
    
    // Light transmission optimization
    void analyzeLightTransmission();
    void calculateLightDerivativeCurve();
    void optimizeLightPath();
    void adjustLightSpeed();
    void bendLightPathOptimally();
    
    // Derivative curve optimization
    void calculateDerivativeCurve();
    void findOptimalCurvePath();
    void applyCurveAdjustments();
    DerivativeCurveData getDerivativeCurveData() const;
    
    // Performance monitoring
    void monitorTransmissionPerformance();
    LightTransmissionMetrics getTransmissionMetrics() const;
    void adaptToNetworkConditions();
    
    // Speed adjustment
    void adjustCurrentFlow();
    void optimizeDataTransmissionRate();
    void mitigateTransmissionDelays();
    
    // System integration
    void integrateWithQuantumMeshSystem();
    void synchronizeWithHyperpathRenderer();
    
    // Status and reporting
    std::string getSystemStatusReport() const;
    void generatePerformanceReport();
    
private:
    std::unique_ptr<FiberOpticAnalyzer> fiberAnalyzer;
    std::unique_ptr<EthernetInterface> ethernetInterface;
    std::unique_ptr<RouterConnector> routerConnector;
    std::unique_ptr<ModemInterface> modemInterface;
    std::unique_ptr<LightPathCalculator> lightPathCalculator;
    std::unique_ptr<DerivativeCurveOptimizer> curveOptimizer;
    
    NetworkConnectionInfo connectionInfo;
    LightTransmissionMetrics transmissionMetrics;
    DerivativeCurveData curveData;
    
    bool isInitialized;
    bool isOptimizing;
    bool isConnectedToNetwork;
    std::chrono::steady_clock::time_point lastOptimizationTime;
    
    // Helper methods
    void initializeTransmissionMetrics();
    void updateTransmissionMetrics();
    void calculateOptimalLightDelay();
    void adjustLightPathForMinimumDelay();
    double calculateLightPathDerivative(double timePoint) const;
    void recalculateDerivativeCurve();
    void optimizeNetworkPath();
    void applyLightSpeedAdjustment();
    bool detectNetworkBottlenecks();
};

#endif // LIGHT_TRANSMISSION_OPTIMIZER_H