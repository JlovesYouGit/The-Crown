#include "QuantumStateContainer.h"
#include <algorithm>
#include <random>
#include <iostream>
#include <sstream>
#include <iomanip>

QuantumStateContainer::QuantumStateContainer() : evolutionFactor(1.0), lastEvolution(std::chrono::steady_clock::now()) {}

void QuantumStateContainer::absorbState(const QuantumState& state) {
    absorbedStates.push_back(state);
    updateStateTypeCount(state, true);
}

void QuantumStateContainer::absorbMultipleStates(const std::vector<QuantumState>& states) {
    for (const auto& state : states) {
        absorbState(state);
    }
}

std::vector<QuantumState> QuantumStateContainer::redistributeStates(int count) {
    std::vector<QuantumState> redistributed;
    
    // Sort states by energy level (highest first)
    std::sort(absorbedStates.begin(), absorbedStates.end(), 
              [](const QuantumState& a, const QuantumState& b) {
                  return a.energyLevel > b.energyLevel;
              });
    
    // Take the requested count or all states if count exceeds available
    int actualCount = std::min(count, static_cast<int>(absorbedStates.size()));
    for (int i = 0; i < actualCount; ++i) {
        redistributed.push_back(enhanceState(absorbedStates[i]));
    }
    
    // Remove redistributed states from container
    absorbedStates.erase(absorbedStates.begin(), absorbedStates.begin() + actualCount);
    
    return redistributed;
}

void QuantumStateContainer::redistributeToSystem() {
    // In a real implementation, this would interface with the cosmic quantum system
    // For now, we'll just clear the container as if states were distributed
    absorbedStates.clear();
    stateTypeCount.clear();
}

void QuantumStateContainer::evolveStates() {
    // Apply evolution factor to all states
    for (auto& state : absorbedStates) {
        state.energyLevel *= (1.0 + evolutionFactor * 0.1);
        
        // Add some randomness to wave function
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis(-0.1, 0.1);
        
        for (auto& waveValue : state.waveFunction) {
            waveValue += dis(gen);
        }
    }
    
    // Increase evolution factor over time
    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - lastEvolution).count();
    evolutionFactor += duration * 0.01; // Evolve faster over time
    lastEvolution = now;
}

double QuantumStateContainer::calculateEvolutionValue() const {
    double totalValue = 0.0;
    for (const auto& state : absorbedStates) {
        totalValue += calculateStateValue(state);
    }
    return totalValue * evolutionFactor;
}

size_t QuantumStateContainer::getStateCount() const {
    return absorbedStates.size();
}

bool QuantumStateContainer::isEmpty() const {
    return absorbedStates.empty();
}

void QuantumStateContainer::clearContainer() {
    absorbedStates.clear();
    stateTypeCount.clear();
    evolutionFactor = 1.0;
}

std::string QuantumStateContainer::getStatusReport() const {
    std::ostringstream oss;
    oss << "Quantum State Container Status:\n";
    oss << "  States Contained: " << getStateCount() << "\n";
    oss << "  Evolution Factor: " << std::fixed << std::setprecision(2) << evolutionFactor << "\n";
    oss << "  Evolution Value: " << std::fixed << std::setprecision(2) << calculateEvolutionValue() << "\n";
    oss << "  State Types:\n";
    
    for (const auto& pair : stateTypeCount) {
        oss << "    " << pair.first << ": " << pair.second << "\n";
    }
    
    return oss.str();
}

void QuantumStateContainer::updateStateTypeCount(const QuantumState& state, bool increment) {
    if (increment) {
        stateTypeCount[state.type]++;
    } else {
        auto it = stateTypeCount.find(state.type);
        if (it != stateTypeCount.end()) {
            it->second--;
            if (it->second <= 0) {
                stateTypeCount.erase(it);
            }
        }
    }
}

QuantumState QuantumStateContainer::enhanceState(const QuantumState& original) const {
    QuantumState enhanced = original;
    enhanced.energyLevel *= (1.0 + evolutionFactor * 0.05); // Enhanced by evolution factor
    
    // Add enhancement to wave function
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 0.1 * evolutionFactor);
    
    for (auto& waveValue : enhanced.waveFunction) {
        waveValue += dis(gen);
    }
    
    return enhanced;
}

double QuantumStateContainer::calculateStateValue(const QuantumState& state) const {
    // Simple valuation based on energy level and wave function complexity
    double value = state.energyLevel;
    
    // Add value based on wave function
    for (const auto& waveValue : state.waveFunction) {
        value += std::abs(waveValue) * 0.1;
    }
    
    return value;
}