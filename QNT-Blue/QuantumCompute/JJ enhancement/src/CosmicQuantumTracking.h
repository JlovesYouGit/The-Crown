#ifndef COSMIC_QUANTUM_TRACKING_H
#define COSMIC_QUANTUM_TRACKING_H

#include <vector>
#include <string>
#include <memory>
#include <map>

// Forward declarations
class QuantumStateContainer;
struct EnvironmentalConditions;
struct QuantumTechnology;
struct WarpTransmission;
struct QuantumStateWarp;
template<typename T>
class EVoltreeNode;

// Structure definitions
struct EnvironmentalConditions {
    double radiationLevel;
    double gravityForce;
    std::string stability;
    std::string typeName;
    
    EnvironmentalConditions() : radiationLevel(0.0), gravityForce(1.0), stability("Stable"), typeName("Unknown") {}
    EnvironmentalConditions(double rad, double grav, const std::string& stab, const std::string& type) 
        : radiationLevel(rad), gravityForce(grav), stability(stab), typeName(type) {}
};

struct QuantumTechnology {
    std::string id;
    std::string name;
    std::string type;
    std::string location;
    std::string status;
    
    QuantumTechnology() : id(""), name(""), type(""), location(""), status("Unknown") {}
    QuantumTechnology(const std::string& i, const std::string& n, const std::string& t, const std::string& loc, const std::string& stat)
        : id(i), name(n), type(t), location(loc), status(stat) {}
};

struct WarpTransmission {
    std::string id;
    double warpFactor;
    double distance;
    std::string destination;
    bool isActive;
    
    WarpTransmission() : id(""), warpFactor(1.0), distance(0.0), destination(""), isActive(false) {}
    WarpTransmission(const std::string& i, double factor, double dist, const std::string& dest)
        : id(i), warpFactor(factor), distance(dist), destination(dest), isActive(true) {}
};

struct QuantumStateWarp {
    std::string id;
    std::string stateType;
    double energyLevel;
    std::string targetLocation;
    bool isWarped;
    
    QuantumStateWarp() : id(""), stateType(""), energyLevel(0.0), targetLocation(""), isWarped(false) {}
    QuantumStateWarp(const std::string& i, const std::string& type, double energy, const std::string& target)
        : id(i), stateType(type), energyLevel(energy), targetLocation(target), isWarped(true) {}
};

class CosmicQuantumTracker {
public:
    // Constructor
    CosmicQuantumTracker();
    
    // Technology registration and tracking
    void registerQuantumTechnology(const QuantumTechnology& tech);
    std::vector<QuantumTechnology> getTrackedTechnologies() const;
    
    // Warp transmission capabilities
    bool initiateWarpTransmission(const WarpTransmission& transmission);
    std::vector<WarpTransmission> getActiveTransmissions() const;
    
    // Quantum state warping and recall
    bool warpQuantumState(const QuantumStateWarp& warp);
    bool recallQuantumState(const std::string& stateId);
    
    // Environmental adaptation
    void adaptToEnvironment(const EnvironmentalConditions& conditions);
    EnvironmentalConditions getCurrentEnvironment() const;
    
    // Cosmic spanning capabilities
    void extendToCosmicDistance(double lightYears);
    double getCurrentCosmicReach() const;
    
    // Data extraction and processing
    std::vector<std::string> extractReactiveDataTraces();
    void processEVoltreeData();
    
    // Quantum state container integration
    void initializeStateContainer();
    void absorbStatesIntoContainer();
    void redistributeStatesFromContainer();
    void evolveContainerStates();
    
    // System status
    std::string getSystemStatus() const;
    
private:
    std::vector<QuantumTechnology> trackedTechnologies;
    std::vector<WarpTransmission> activeTransmissions;
    std::map<std::string, QuantumStateWarp> warpedStates;
    EnvironmentalConditions currentEnvironment;
    double cosmicReach;
    std::vector<std::string> reactiveDataTraces;
    std::unique_ptr<QuantumStateContainer> stateContainer;
    
    // Helper methods
    void updateSystemStatus();
    double calculateWarpEfficiency() const;
};

#endif // COSMIC_QUANTUM_TRACKING_H