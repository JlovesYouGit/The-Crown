#ifndef DISPLAY_PORT_OPTIMIZER_H
#define DISPLAY_PORT_OPTIMIZER_H

#include <string>
#include <vector>
#include <memory>

// Structure to represent display device information
struct DisplayDeviceInfo {
    std::string deviceId;
    std::string deviceName;
    std::string connectionType;  // HDMI, DisplayPort, USB, etc.
    int resolutionWidth;
    int resolutionHeight;
    int refreshRate;
    int colorDepth;
    bool isVRDevice;
    bool isUSBConnected;
    double linkSpeed;  // In Gbps
    double bandwidthUtilization;
};

// Structure to represent USB device optimization settings
struct USBDeviceOptimization {
    bool enableLowLatencyMode;
    bool enableHighBandwidthMode;
    int usbVersion;  // 2, 3, 3.1, 3.2, 4.0
    double maxBandwidth;  // In Gbps
    bool enableAdaptiveSynchronization;
    bool enableMotionCompensation;
    int packetSizeOptimization;
    bool enableErrorCorrection;
};

// Structure to represent link speed optimization
struct LinkSpeedOptimization {
    double targetLinkSpeed;  // In Gbps
    bool enableDynamicSpeedAdjustment;
    double minAcceptableSpeed;
    bool enableForwardErrorCorrection;
    int laneCount;
    bool enableSpreadSpectrum;
};

class DisplayPortOptimizer {
public:
    // Constructor
    DisplayPortOptimizer();
    
    // Device detection and management
    void detectConnectedDisplays();
    std::vector<DisplayDeviceInfo> getConnectedDisplays() const;
    DisplayDeviceInfo getDisplayInfo(const std::string& deviceId) const;
    
    // USB device optimization (NEW)
    void optimizeUSBDevices();
    void configureUSBOptimization(const USBDeviceOptimization& settings);
    void applyUSBEnhancements(const std::string& deviceId);
    void enableLowLatencyForUSBVR();
    
    // Link speed optimization (NEW)
    void optimizeLinkSpeeds();
    void configureLinkSpeedOptimization(const LinkSpeedOptimization& settings);
    void increaseLinkSpeedForDevice(const std::string& deviceId);
    double getCurrentLinkSpeed(const std::string& deviceId) const;
    void applyHighSpeedLinkProtocol(const std::string& deviceId);
    
    // Display optimization
    void optimizeDisplaySettings(const std::string& deviceId);
    void setResolution(const std::string& deviceId, int width, int height);
    void setRefreshRate(const std::string& deviceId, int refreshRate);
    void setColorDepth(const std::string& deviceId, int colorDepth);
    
    // Motion compensation
    void enableMotionCompensation(const std::string& deviceId);
    void setSharpnessEnhancement(const std::string& deviceId, float level);
    void setContrastAdaptation(const std::string& deviceId, float level);
    
    // Frame delay elimination
    void eliminateFrameDelay();
    void enableTripleBuffering();
    void enableVSync();
    void predictFrameRendering();
    
    // Pixel quality enhancement
    void enhancePixelQuality(const std::string& deviceId);
    void applySharpeningAlgorithm(const std::string& deviceId);
    void optimizeColorSaturation(const std::string& deviceId);
    void adjustGammaCorrection(const std::string& deviceId);
    void activateHDRSupport(const std::string& deviceId);
    
    // Specialized Oculus Quest 3 support (NEW)
    void detectOculusQuest3();
    void optimizeOculusQuest3();
    void applyQuest3LowLatencyProfile();
    void enableQuest3AdaptiveSync();
    void configureQuest3USBProtocol();
    
    // Performance reporting
    std::string getOptimizationReport() const;
    void generatePerformanceReport();
    
private:
    std::vector<DisplayDeviceInfo> connectedDisplays;
    USBDeviceOptimization usbSettings;
    LinkSpeedOptimization linkSettings;
    bool isInitialized;
    bool isMotionCompensationEnabled;
    bool isFrameDelayEliminated;
    
    // Private helper methods
    void initializeDefaultSettings();
    void scanForUSBDevices();
    void applyUSBDeviceSettings(const std::string& deviceId);
    void boostUSBSignalingRate(const std::string& deviceId);
    void optimizeUSBPacketTransmission(const std::string& deviceId);
    void reduceUSBProtocolOverhead(const std::string& deviceId);
    void increaseUSBPowerDelivery(const std::string& deviceId);
    void applyLinkSpeedBoost(const std::string& deviceId);
    void enableHighSpeedLanes(const std::string& deviceId);
    void optimizeSignalIntegrity(const std::string& deviceId);
    void reduceElectromagneticInterference(const std::string& deviceId);
    bool isOculusQuest3Device(const std::string& deviceName) const;
};

#endif // DISPLAY_PORT_OPTIMIZER_H