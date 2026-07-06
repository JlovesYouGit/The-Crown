#ifndef LIGHT_MANIPULATION_ENGINE_H
#define LIGHT_MANIPULATION_ENGINE_H

#include <string>
#include <vector>
#include <memory>
#include <chrono>

// Forward declarations
class QuantumPhotonicProcessor;
class SlowLightModulator;
class LightAccelerationChamber;

struct LightState {
    double frequency;           // Light frequency in Hz
    double wavelength;          // Wavelength in nanometers
    double speed;              // Speed of light in medium (m/s)
    double intensity;          // Light intensity
    double coherence;          // Quantum coherence level (0.0 to 1.0)
    std::chrono::steady_clock::time_point creationTime;
    
    LightState() : frequency(193.4e12), wavelength(1550.0), speed(2.0e8), 
                   intensity(1.0), coherence(0.95) {
        creationTime = std::chrono::steady_clock::now();
    }
};

struct BandwidthMetrics {
    double currentMbps;
    double maxMbps;
    double latencyMs;
    double packetLossPercent;
    double lightSpeedFactor;    // Ratio of current light speed to vacuum speed
    std::string transmissionMode;
    
    BandwidthMetrics() : currentMbps(55.0), maxMbps(94.0), latencyMs(25.0), 
                        packetLossPercent(0.2), lightSpeedFactor(0.67), 
                        transmissionMode("NORMAL") {}
};

class LightManipulationEngine {
public:
    // Constructor
    LightManipulationEngine();
    
    // Light manipulation methods
    void initializeLightSystem();
    void freezeLightTemporarily();
    void accelerateLightTransmission();
    void balanceLightStates();
    
    // Data transmission enhancement
    void enhanceDataEncoding();
    void optimizePhotonRouting();
    void implementQuantumCoherence();
    
    // System monitoring
    BandwidthMetrics getBandwidthMetrics() const;
    std::string getSystemStatus() const;
    void runDiagnostics();
    
    // Advanced features
    void enableSlowLightProcessing();
    void activateLightAccelerationMode();
    void synchronizeQuantumStates();
    
private:
    std::unique_ptr<QuantumPhotonicProcessor> photonicProcessor;
    std::unique_ptr<SlowLightModulator> slowLightModulator;
    std::unique_ptr<LightAccelerationChamber> accelerationChamber;
    BandwidthMetrics metrics;
    std::vector<LightState> lightStates;
    bool isLightFrozen;
    bool isAccelerationActive;
    
    // Helper methods
    void updateBandwidthMetrics();
    void adjustLightParameters();
    void processLightStates();
    void calculateEnhancedBandwidth();
};

#endif // LIGHT_MANIPULATION_ENGINE_H