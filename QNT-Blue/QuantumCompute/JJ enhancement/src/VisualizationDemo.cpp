/*
 * Visualization Demo for Neural Enhancement System
 * Demonstrates 3D and 4D brain visualization capabilities
 */

#include "NeuralEnhancementSystem.h"
#include <iostream>
#include <string>

int main() {
    std::cout << "🌟 JJ Neural Enhancement System - Visualization Demo 🌟" << std::endl;
    std::cout << "=====================================================" << std::endl;
    std::cout << "Initializing advanced 3D/4D brain visualization system..." << std::endl << std::endl;

    // Initialize the neural enhancement system
    if (!InitializeNeuralEnhancementSystem()) {
        std::cerr << "❌ Failed to initialize neural enhancement system!" << std::endl;
        return -1;
    }

    // Create neural state
    NeuralState currentState;
    BrainwaveData waves;
    
    // Measure brainwaves
    std::cout << "1. Measuring brainwaves via EEG interface..." << std::endl;
    if (!MeasureBrainwaves(&currentState, &waves)) {
        std::cerr << "❌ Failed to measure brainwaves!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }
    std::cout << "✅ Brainwave measurement completed successfully!" << std::endl << std::endl;

    // Analyze neural state
    std::cout << "2. Analyzing neural coherence and focus..." << std::endl;
    if (!AnalyzeNeuralState(&currentState)) {
        std::cerr << "❌ Failed to analyze neural state!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }
    std::cout << "✅ Neural state analysis completed successfully!" << std::endl << std::endl;

    // Create 3D brain visualization
    std::cout << "3. Generating 3D brain visualization..." << std::endl;
    Brain3DVisualization brain3D;
    if (Create3DVisualization(&currentState, &brain3D)) {
        std::cout << "✅ 3D brain visualization generated successfully!" << std::endl;
        std::cout << "   Grid dimensions: " << brain3D.gridWidth << "x" 
                  << brain3D.gridHeight << "x" << brain3D.gridDepth << std::endl;
        std::cout << "   Visualization type: " << brain3D.visualizationType << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to generate 3D brain visualization!" << std::endl << std::endl;
    }

    // Create 4D brain visualization
    std::cout << "4. Generating 4D brain visualization (3D + time)..." << std::endl;
    Brain4DVisualization brain4D;
    if (Create4DVisualization(&currentState, &brain4D, 5)) { // 5 time steps
        std::cout << "✅ 4D brain visualization generated successfully!" << std::endl;
        std::cout << "   Time steps: " << brain4D.timeSeries.size() << std::endl;
        std::cout << "   Time resolution: " << brain4D.timeResolution << " seconds" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to generate 4D brain visualization!" << std::endl << std::endl;
    }

    // Create enhanced brain map
    std::cout << "5. Creating enhanced brain activity map..." << std::endl;
    std::string brainMap;
    if (CreateBrainMap(&currentState, brainMap)) {
        std::cout << brainMap << std::endl;
    } else {
        std::cerr << "❌ Failed to create brain map!" << std::endl;
    }

    // Display connection status
    std::cout << "6. Checking connection status..." << std::endl;
    ConnectionStatus status = GetConnectionStatus();
    std::cout << "✅ Connection diagnostics completed!" << std::endl << std::endl;

    // Show 3D visualization data summary
    std::cout << "7. 3D Visualization Data Summary:" << std::endl;
    std::cout << "   Frontal lobe activity (executive functions): " << (brain3D.brainActivityGrid[1][5][5] * 100) << "%" << std::endl;
    std::cout << "   Parietal lobe activity (sensory processing): " << (brain3D.brainActivityGrid[5][8][5] * 100) << "%" << std::endl;
    std::cout << "   Temporal lobe activity (memory/auditory): " << (brain3D.brainActivityGrid[5][1][5] * 100) << "%" << std::endl;
    std::cout << "   Occipital lobe activity (visual processing): " << (brain3D.brainActivityGrid[8][5][5] * 100) << "%" << std::endl << std::endl;

    // Show 4D visualization data summary
    std::cout << "8. 4D Visualization Data Summary:" << std::endl;
    if (!brain4D.timeSeries.empty()) {
        std::cout << "   First time step frontal activity: " << (brain4D.timeSeries[0].brainActivityGrid[1][5][5] * 100) << "%" << std::endl;
        std::cout << "   Last time step frontal activity: " << (brain4D.timeSeries.back().brainActivityGrid[1][5][5] * 100) << "%" << std::endl;
        std::cout << "   Activity variation over time: " << 
            abs((brain4D.timeSeries.back().brainActivityGrid[1][5][5] - brain4D.timeSeries[0].brainActivityGrid[1][5][5]) * 100) << "%" << std::endl;
    }
    std::cout << std::endl;

    // Shutdown system
    std::cout << "9. Shutting down visualization system..." << std::endl;
    ShutdownNeuralEnhancementSystem();
    
    std::cout << "🎉 Visualization demo completed successfully!" << std::endl;
    std::cout << "🧠 The future of brain-computer visualization is here!" << std::endl;

    return 0;
}