#ifndef SECURE_INTERNET_OPTIMIZER_H
#define SECURE_INTERNET_OPTIMIZER_H

#include <string>
#include <vector>
#include <memory>
#include <chrono>

// Forward declarations
class KiberBitCompressor;
class LocationObfuscator;
class TrafficEncryptor;

struct NetworkMetrics {
    double bandwidthMbps;
    double latencyMs;
    double packetLossPercent;
    std::string securityLevel;
    std::chrono::steady_clock::time_point lastUpdate;
    
    NetworkMetrics() : bandwidthMbps(0.0), latencyMs(0.0), packetLossPercent(0.0), securityLevel("UNKNOWN") {}
};

class SecureInternetOptimizer {
public:
    // Constructor
    SecureInternetOptimizer();
    
    // Network optimization methods
    void initializeSecureConnection();
    void optimizeEthernetBandwidth();
    void applyKiberBitCompression();
    
    // Security methods
    void obfuscateLocationData();
    void encryptNetworkTraffic();
    void detectAndRemoveTrackers();
    
    // Monitoring methods
    NetworkMetrics getNetworkMetrics() const;
    std::string getSecurityStatus() const;
    void runSecurityScan();
    
    // Advanced features
    void enableQuantumEncryption();
    void routeThroughSecureNodes();
    void compressInternetProtocolBits();
    
private:
    std::unique_ptr<KiberBitCompressor> bitCompressor;
    std::unique_ptr<LocationObfuscator> locationObfuscator;
    std::unique_ptr<TrafficEncryptor> trafficEncryptor;
    NetworkMetrics currentMetrics;
    bool isSecureConnectionActive;
    std::vector<std::string> blockedTrackers;
    
    // Helper methods
    void updateNetworkMetrics();
    void applyAdvancedCompressionAlgorithms();
    void establishEncryptedTunnel();
};

#endif // SECURE_INTERNET_OPTIMIZER_H