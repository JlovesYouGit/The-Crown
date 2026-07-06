/*
 * Cortical Mapping Demo for Neural Enhancement System
 * Demonstrates detailed cerebral cortex mapping and layer analysis
 */

#include "NeuralEnhancementSystem.h"
#include <iostream>
#include <string>

int main() {
    std::cout << "🌟 JJ Neural Enhancement System - Cortical Mapping Demo 🌟" << std::endl;
    std::cout << "=====================================================" << std::endl;
    std::cout << "Initializing detailed cerebral cortex mapping system..." << std::endl << std::endl;

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

    // Create 3D brain visualization with detailed cortical mapping
    std::cout << "3. Generating 3D brain visualization with cerebral cortex mapping..." << std::endl;
    Brain3DVisualization brain3D;
    if (Create3DVisualization(&currentState, &brain3D)) {
        std::cout << "✅ 3D brain visualization with cortical mapping generated successfully!" << std::endl;
        std::cout << "   Grid dimensions: " << brain3D.gridWidth << "x" 
                  << brain3D.gridHeight << "x" << brain3D.gridDepth << std::endl;
        std::cout << "   Visualization type: " << brain3D.visualizationType << std::endl;
        std::cout << "   Cortex regions mapped: " << brain3D.cortexRegions.size() << std::endl;
        std::cout << "   Deep structures mapped: " << brain3D.deepStructures.size() << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to generate 3D brain visualization with cortical mapping!" << std::endl << std::endl;
    }

    // Analyze cortical layers
    std::cout << "4. Analyzing cortical layers across cerebral cortex regions..." << std::endl;
    if (AnalyzeCorticalLayers(&currentState, &brain3D)) {
        std::cout << "✅ Cortical layer analysis completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to analyze cortical layers!" << std::endl << std::endl;
    }

    // Display detailed cortex region information
    std::cout << "5. Detailed Cerebral Cortex Region Analysis:" << std::endl;
    std::cout << "===========================================" << std::endl;
    for (const auto& regionPair : brain3D.cortexRegions) {
        const CerebralCortexRegion& region = regionPair.second;
        std::cout << "Region: " << region.name << std::endl;
        std::cout << "   Lobe: " << region.lobe << std::endl;
        std::cout << "   Function: " << region.function << std::endl;
        std::cout << "   Activity Level: " << static_cast<int>(region.activityLevel * 100) << "%" << std::endl;
        std::cout << "   Connectivity: " << static_cast<int>(region.connectivity * 100) << "%" << std::endl;
        std::cout << "   Connected Regions: " << region.connectedRegions.size() << std::endl;
        std::cout << "   Cortical Layers Analyzed: " << region.layerAnalysis.size() << std::endl;
        
        // Display layer information for the first few layers
        for (size_t i = 0; i < std::min(region.layerAnalysis.size(), static_cast<size_t>(3)); i++) {
            const CorticalLayerAnalysis& layer = region.layerAnalysis[i];
            std::cout << "     Layer " << (i+1) << " (" << layer.layerName << "): " 
                      << static_cast<int>(layer.activityLevel * 100) << "% activity" << std::endl;
        }
        if (region.layerAnalysis.size() > 3) {
            std::cout << "     ... and " << (region.layerAnalysis.size() - 3) << " more layers" << std::endl;
        }
        std::cout << std::endl;
    }

    // Display deep brain structure information
    std::cout << "6. Deep Brain Structure Analysis:" << std::endl;
    std::cout << "===============================" << std::endl;
    for (const auto& structurePair : brain3D.deepStructures) {
        const DeepBrainStructure& structure = structurePair.second;
        std::cout << "Structure: " << structure.name << std::endl;
        std::cout << "   Function: " << structure.function << std::endl;
        std::cout << "   Activity Level: " << static_cast<int>(structure.activityLevel * 100) << "%" << std::endl;
        std::cout << "   Connections: " << structure.connections.size() << std::endl << std::endl;
    }

    // Display cortical layer information
    std::cout << "7. Cortical Layer Information:" << std::endl;
    std::cout << "============================" << std::endl;
    for (const std::string& layer : brain3D.corticalLayers) {
        std::cout << "   " << layer << " Layer" << std::endl;
    }
    std::cout << std::endl;

    // Create enhanced brain map
    std::cout << "8. Creating enhanced brain activity map with cortical analysis..." << std::endl;
    std::string brainMap;
    if (CreateBrainMap(&currentState, brainMap)) {
        std::cout << brainMap << std::endl;
    } else {
        std::cerr << "❌ Failed to create brain map!" << std::endl;
    }

    // Display connection status
    std::cout << "9. Checking connection status..." << std::endl;
    ConnectionStatus status = GetConnectionStatus();
    std::cout << "✅ Connection diagnostics completed!" << std::endl << std::endl;

    // Show 3D visualization data summary
    std::cout << "10. 3D Visualization Data Summary:" << std::endl;
    std::cout << "=================================" << std::endl;
    std::cout << "   Prefrontal cortex activity: " << (brain3D.cortexRegions.at("Prefrontal Cortex").activityLevel * 100) << "%" << std::endl;
    std::cout << "   Primary visual cortex activity: " << (brain3D.cortexRegions.at("Primary Visual Cortex").activityLevel * 100) << "%" << std::endl;
    std::cout << "   Hippocampus activity: " << (brain3D.cortexRegions.at("Hippocampus").activityLevel * 100) << "%" << std::endl;
    std::cout << "   Thalamus activity: " << (brain3D.deepStructures.at("Thalamus").activityLevel * 100) << "%" << std::endl << std::endl;

    // Shutdown system
    std::cout << "11. Shutting down cortical mapping system..." << std::endl;
    ShutdownNeuralEnhancementSystem();
    
    std::cout << "🎉 Cortical mapping demo completed successfully!" << std::endl;
    std::cout << "🧠 Detailed cerebral cortex mapping and layer analysis complete!" << std::endl;

    return 0;
}