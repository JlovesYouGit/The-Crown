#ifndef QETHER_NETWORK_H
#define QETHER_NETWORK_H

#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <map>
#include <set>

// Forward declarations
class QuantumBitManager;
class ElectronTransmitter;
class LightConduit;
class QEtherNode;
class DataRetentionSystem;
class AccelerationEngine;
class TraceNodeManager;
class SecurityProtector;
class GlobalRoutingSystem;

// Structure to represent a quantum bit (qbit)
struct QBit {
    int id;
    double probability0;     // Probability of being 0
    double probability1;     // Probability of being 1
    bool isEntangled;       // Whether this qbit is entangled with others
    std::vector<int> entangledWith; // List of entangled qbit IDs
    double coherenceTime;   // Time until decoherence (in seconds)
    std::chrono::steady_clock::time_point creationTime;
    std::string originNode; // Origin node identifier
    std::vector<std::string> tracePath; // Path this qbit has traveled
};

// Structure to represent a QEther node with enhanced management capabilities
struct QEtherNode {
    int nodeId;
    std::string nodeName;
    std::string location;
    std::string geographicRegion; // Geographic region of the node
    double processingPower;     // Quantum processing power rating
    double transmissionRate;    // Qbits per second transmission rate
    double storageCapacity;     // Number of qbits that can be stored
    std::vector<QBit> storedQBits;
    bool isOnline;
    std::chrono::steady_clock::time_point lastActivity;
    std::vector<std::string> connectedNodes; // Nodes this node is connected to
    double healthStatus;        // Node health status (0.0 - 1.0)
    bool isManaged;             // Whether node is self-managed
    std::chrono::steady_clock::time_point lastHealthCheck; // Last health check time
    int failureCount;           // Number of consecutive failures
    bool isCompromised;         // Security status
};

// Structure to represent a trace node for global routing
struct TraceNode {
    std::string traceId;
    std::string originNode;
    std::string destinationNode;
    std::vector<std::string> routingPath; // Global routing path
    std::chrono::steady_clock::time_point creationTime;
    std::chrono::steady_clock::time_point lastUpdate;
    double securityLevel; // Security level of this trace
    bool isEncrypted;
    std::string encryptionKey; // Encryption key for this trace
    bool isActive;
};

// Structure to represent QEther network configuration
struct QEtherConfig {
    double targetTransmissionSpeed;  // Target qbits per second
    double maxCoherenceTime;         // Maximum coherence time to maintain
    double dataRetentionPeriod;      // How long to retain data (in seconds)
    bool enableEntanglement;         // Whether to enable qbit entanglement
    double accelerationFactor;       // Acceleration multiplier for data transmission
    bool enableErrorCorrection;      // Whether to enable quantum error correction
    bool enableGlobalTracing;        // Whether to enable global trace nodes
    double securityLevel;            // Security level for data transmission
    bool enableAntiBacktrack;        // Whether to enable anti-backtracking
};

class QEtherNetwork {
public:
    // Constructor
    QEtherNetwork();
    
    // Initialization and setup
    bool initializeNetwork();
    void configureQEther(const QEtherConfig& config);
    
    // Enhanced node management with self-management capabilities
    int createQEtherNode(const std::string& name, const std::string& location, const std::string& region = "global");
    bool connectQEtherNode(int nodeId);
    void disconnectQEtherNode(int nodeId);
    std::vector<QEtherNode> getNetworkNodes() const;
    QEtherNode getNodeInfo(int nodeId) const;
    std::vector<std::string> getNodeConnections(int nodeId) const;
    
    // NEW: Self-management and automatic node handling
    void enableNodeSelfManagement(int nodeId);
    void disableNodeSelfManagement(int nodeId);
    void performAutomaticNodeMaintenance();
    void handleNewNodeDetection();
    void manageBrokenNodes();
    bool isNodeHealthy(int nodeId) const;
    void repairNode(int nodeId);
    void isolateBrokenNode(int nodeId);
    void replaceBrokenNode(int nodeId);
    void addNodeToGlobalMap(const QEtherNode& node);
    void removeNodeFromGlobalMap(int nodeId);
    
    // QBit management
    QBit createQBit(const std::string& originNode = "default");
    std::vector<QBit> createQBits(int count, const std::string& originNode = "default");
    bool storeQBit(int nodeId, const QBit& qbit);
    QBit retrieveQBit(int nodeId, int qbitId);
    bool transmitQBit(int sourceNodeId, int destinationNodeId, int qbitId);
    
    // Electron and light transmission
    void transmitViaElectrons(int sourceNodeId, int destinationNodeId, const std::vector<QBit>& qbits);
    void transmitViaLight(int sourceNodeId, int destinationNodeId, const std::vector<QBit>& qbits);
    void optimizeElectronFlow();
    void enhanceLightConduit();
    
    // Data manipulation and acceleration
    void accelerateQBits(int nodeId, const std::vector<QBit>& qbits);
    void manipulateQBits(int nodeId, const std::vector<QBit>& qbits);
    void retainQBitData(int nodeId, const std::vector<QBit>& qbits);
    
    // Entanglement operations
    void entangleQBits(int nodeId, std::vector<QBit>& qbits);
    void maintainCoherence(int nodeId, std::vector<QBit>& qbits);
    
    // Trace node management (NEW FEATURE)
    TraceNode createTraceNode(const std::string& origin, const std::string& destination);
    bool activateTraceNode(const std::string& traceId);
    void updateTraceNodePath(const std::string& traceId, const std::string& newNode);
    void secureTraceNode(const std::string& traceId);
    void deactivateTraceNode(const std::string& traceId);
    TraceNode getTraceNodeInfo(const std::string& traceId) const;
    std::vector<TraceNode> getAllTraceNodes() const;
    void enableAntiBacktrackProtection(const std::string& traceId);
    
    // Global routing system (NEW FEATURE)
    std::vector<std::string> calculateGlobalRoute(const std::string& origin, const std::string& destination);
    void transmitViaGlobalRoute(const std::string& traceId, const std::vector<QBit>& qbits);
    double getRouteEfficiency(const std::vector<std::string>& route) const;
    
    // Security system (NEW FEATURE)
    void applyQuantumEncryption(const std::string& traceId, std::vector<QBit>& qbits);
    void verifyDataIntegrity(const std::string& traceId, const std::vector<QBit>& qbits);
    bool detectBacktrackingAttempts(const std::string& traceId);
    void isolateCompromisedNodes(const std::vector<std::string>& compromisedNodes);
    
    // Network performance monitoring
    void monitorNetworkPerformance();
    double getNetworkTransmissionRate() const;
    double getAverageCoherenceTime() const;
    double getDataRetentionEfficiency() const;
    std::map<std::string, double> getGlobalNetworkMetrics() const;
    
    // Error handling and correction
    void detectTransmissionErrors();
    void applyErrorCorrection();
    void recoverLostQBits();
    
    // System integration
    void integrateWithQuantumMeshSystem();
    void synchronizeWithHyperpathRenderer();
    void connectToLightTransmissionOptimizer();
    
    // Status and reporting
    std::string getNetworkStatusReport() const;
    void generatePerformanceReport();
    std::string getGlobalTraceReport() const;
    
private:
    std::unique_ptr<QuantumBitManager> qbitManager;
    std::unique_ptr<ElectronTransmitter> electronTransmitter;
    std::unique_ptr<LightConduit> lightConduit;
    std::unique_ptr<DataRetentionSystem> dataRetentionSystem;
    std::unique_ptr<AccelerationEngine> accelerationEngine;
    std::unique_ptr<TraceNodeManager> traceNodeManager; // NEW COMPONENT
    std::unique_ptr<SecurityProtector> securityProtector; // NEW COMPONENT
    std::unique_ptr<GlobalRoutingSystem> globalRoutingSystem; // NEW COMPONENT
    
    std::vector<QEtherNode> networkNodes;
    std::map<std::string, TraceNode> traceNodes; // NEW: Track all trace nodes
    std::map<std::string, std::vector<std::string>> globalNodeMap; // NEW: Global node mapping
    QEtherConfig networkConfig;
    
    bool isInitialized;
    bool isNetworkActive;
    double currentTransmissionRate;
    double averageCoherenceTime;
    double dataRetentionEfficiency;
    std::chrono::steady_clock::time_point lastPerformanceCheck;
    
    // Helper methods
    void initializeNetworkMetrics();
    void updateNetworkMetrics();
    int findAvailableNodeId() const;
    bool validateNodeConnection(int nodeId) const;
    void optimizeTransmissionPaths();
    void balanceNetworkLoad();
    void applyQuantumAcceleration();
    void preserveQBitCoherence();
    
    // NEW helper methods for trace functionality
    std::string generateTraceId() const;
    std::string generateEncryptionKey() const;
    void updateGlobalNodeMap();
    bool isNodeCompromised(const std::string& nodeId) const;
    void logSecurityEvent(const std::string& event, const std::string& details);
    
    // NEW helper methods for node management
    void initializeNodeHealth(int nodeId);
    void updateNodeHealth(int nodeId);
    bool checkNodeConnectivity(int nodeId) const;
    void logNodeEvent(int nodeId, const std::string& event, const std::string& details);
    std::vector<int> getBrokenNodes() const;
    std::vector<int> getHealthyNodes() const;
    void rebalanceNetworkLoad();
};

#endif // QETHER_NETWORK_H