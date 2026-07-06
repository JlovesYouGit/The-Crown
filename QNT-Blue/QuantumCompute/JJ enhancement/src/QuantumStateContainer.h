#ifndef QUANTUM_STATE_CONTAINER_H
#define QUANTUM_STATE_CONTAINER_H

#include <vector>
#include <map>
#include <string>
#include <memory>
#include <chrono>

// Forward declarations
template<typename T>
class EVoltreeNode;

struct QuantumState {
    std::string id;
    std::string type;
    double energyLevel;
    std::chrono::steady_clock::time_point creationTime;
    std::vector<double> waveFunction;
    
    QuantumState(const std::string& i, const std::string& t, double energy) 
        : id(i), type(t), energyLevel(energy), creationTime(std::chrono::steady_clock::now()) {}
};

class QuantumStateContainer {
public:
    // Constructor
    QuantumStateContainer();
    
    // State absorption methods
    void absorbState(const QuantumState& state);
    void absorbMultipleStates(const std::vector<QuantumState>& states);
    
    // State redistribution methods
    std::vector<QuantumState> redistributeStates(int count);
    void redistributeToSystem();
    
    // Evolutionary value enhancement
    void evolveStates();
    double calculateEvolutionValue() const;
    
    // Container management
    size_t getStateCount() const;
    bool isEmpty() const;
    void clearContainer();
    
    // Container status
    std::string getStatusReport() const;
    
private:
    std::vector<QuantumState> absorbedStates;
    std::map<std::string, int> stateTypeCount;
    double evolutionFactor;
    std::chrono::steady_clock::time_point lastEvolution;
    
    // Helper methods
    void updateStateTypeCount(const QuantumState& state, bool increment);
    QuantumState enhanceState(const QuantumState& original) const;
    double calculateStateValue(const QuantumState& state) const;
};

#endif // QUANTUM_STATE_CONTAINER_H