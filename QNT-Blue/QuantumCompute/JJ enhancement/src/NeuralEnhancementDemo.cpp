/*
 * Neural Enhancement System Demo Application
 * Demonstrates the JJ USB Transmission Neural Enhancement Features
 */

#include "NeuralEnhancementSystem.h"
#include <iostream>
#include <string>

int main() {
    std::cout << "🌟 JJ Neural Enhancement System Demo 🌟" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Connecting to JJ USB transmission interface..." << std::endl;
    std::cout << "Establishing quantum link with neural headset..." << std::endl << std::endl;

    // Initialize the neural enhancement system
    if (!InitializeNeuralEnhancementSystem()) {
        std::cerr << "❌ Failed to initialize neural enhancement system!" << std::endl;
        return -1;
    }
    std::cout << "✅ Neural enhancement system initialized successfully!" << std::endl << std::endl;

    // Check connection status
    std::cout << "1. Checking device connection status..." << std::endl;
    ConnectionStatus connectionStatus = GetConnectionStatus();
    std::cout << std::endl;

    // Create neural state and brainwave data structures
    NeuralState currentState;
    BrainwaveData currentWaves;
    
    // Measure brainwaves
    std::cout << "2. Measuring brainwaves via EEG interface..." << std::endl;
    if (MeasureBrainwaves(&currentState, &currentWaves)) {
        std::cout << "✅ Brainwave measurement completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to measure brainwaves!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }

    // Analyze neural state
    std::cout << "3. Analyzing neural coherence and focus..." << std::endl;
    if (AnalyzeNeuralState(&currentState)) {
        std::cout << "✅ Neural state analysis completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to analyze neural state!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }

    // Create brain map
    std::cout << "4. Creating brain activity map..." << std::endl;
    std::string brainMap;
    if (CreateBrainMap(&currentState, brainMap)) {
        std::cout << "✅ Brain map generated successfully!" << std::endl;
        std::cout << brainMap << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to create brain map!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }

    // Initialize user statistics
    std::cout << "5. Initializing user statistics..." << std::endl;
    UserStats userStats;
    if (InitializeUserStats(&userStats)) {
        std::cout << "✅ User statistics initialized successfully!" << std::endl;
        std::cout << "   Starting Level: " << userStats.level << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to initialize user statistics!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }

    // Initialize and enhance neural schema
    std::cout << "6. Initializing neural schema with systematic neuron indexing..." << std::endl;
    if (InitializeNeuralSchema(&userStats.cognitiveSchema)) {
        std::cout << "✅ Neural schema initialized successfully!" << std::endl;
        
        // Enhance the neural schema
        std::cout << "7. Enhancing neural schema based on user stats..." << std::endl;
        if (EnhanceNeuralSchema(&userStats.cognitiveSchema, &userStats)) {
            std::cout << "✅ Neural schema enhanced successfully!" << std::endl;
            
            // Apply the neural schema to user stats
            std::cout << "8. Applying neural schema to user stats..." << std::endl;
            if (ApplyNeuralSchema(&userStats, &userStats.cognitiveSchema)) {
                std::cout << "✅ Neural schema applied successfully!" << std::endl << std::endl;
            } else {
                std::cerr << "❌ Failed to apply neural schema!" << std::endl;
            }
        } else {
            std::cerr << "❌ Failed to enhance neural schema!" << std::endl;
        }
    } else {
        std::cerr << "❌ Failed to initialize neural schema!" << std::endl;
    }
    std::cout << std::endl;

    // Award experience points
    std::cout << "9. Awarding experience points for neural performance..." << std::endl;
    int xpGained = AwardExperiencePoints(&currentState, &userStats);
    if (xpGained > 0) {
        std::cout << "✅ Experience points awarded successfully!" << std::endl;
        
        // Check for level up
        if (LevelUpUser(&userStats)) {
            std::cout << "🎉 Congratulations on your level up!" << std::endl;
        }
        std::cout << std::endl;
    } else {
        std::cerr << "❌ Failed to award experience points!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }

    // Initialize skill tree
    std::cout << "10. Initializing neural enhancement skill tree..." << std::endl;
    SkillTree skillTree;
    if (InitializeSkillTree(&skillTree)) {
        std::cout << "✅ Skill tree initialized successfully!" << std::endl;
        std::cout << "   Available skill points: " << skillTree.availablePoints << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to initialize skill tree!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }

    // Unlock a skill
    std::cout << "11. Unlocking Neural Sensitivity skill..." << std::endl;
    if (UnlockSkill(&skillTree, &userStats, "Neural Sensitivity")) {
        std::cout << "✅ Neural Sensitivity skill unlocked successfully!" << std::endl;
        std::cout << "   Updated Intelligence: " << userStats.intelligence << std::endl;
        std::cout << "   Updated Perception: " << userStats.perception << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to unlock Neural Sensitivity skill!" << std::endl;
        ShutdownNeuralEnhancementSystem();
        return -1;
    }

    // Enhance brain hemispheres
    std::cout << "12. Enhancing brain hemispheres..." << std::endl;
    HemisphereEnhancement hemisphereEnhancement;
    if (EnhanceHemispheres(&hemisphereEnhancement, &userStats)) {
        std::cout << "✅ Brain hemisphere enhancement completed!" << std::endl << std::endl;
    } else {
        std::cout << "⚠️ Brain hemisphere enhancement not available at current level." << std::endl << std::endl;
    }

    // Upload enhancement to processor
    std::cout << "13. Uploading neural enhancement to core processor..." << std::endl;
    UploadParameters uploadParams;
    ProcessorMetrics processorMetrics;
    processorMetrics.volumeCapacity = 100.0;
    processorMetrics.evolutionaryState = 1;
    processorMetrics.stateName = "Baseline Human";
    
    if (UploadEnhancementToProcessor(&userStats, &uploadParams, &processorMetrics)) {
        std::cout << "✅ Neural enhancement uploaded successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to upload neural enhancement!" << std::endl << std::endl;
    }

    // Evolve processor to next state
    std::cout << "14. Evolving processor to enhanced state..." << std::endl;
    if (EvolveProcessor(&processorMetrics, 2)) {
        std::cout << "✅ Processor evolution completed successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to evolve processor!" << std::endl << std::endl;
    }

    // Display final processor capabilities
    std::cout << "15. Retrieving final processor capabilities..." << std::endl;
    if (GetProcessorCapabilities(&processorMetrics)) {
        std::cout << "✅ Processor capabilities retrieved successfully!" << std::endl << std::endl;
    } else {
        std::cerr << "❌ Failed to retrieve processor capabilities!" << std::endl << std::endl;
    }

    // Display final user stats
    std::cout << "Final User Statistics:" << std::endl;
    std::cout << "=====================" << std::endl;
    std::cout << "Level: " << userStats.level << std::endl;
    std::cout << "Experience Points: " << userStats.experiencePoints << std::endl;
    std::cout << "Intelligence: " << userStats.intelligence << std::endl;
    std::cout << "Perception: " << userStats.perception << std::endl;
    std::cout << "Focus: " << userStats.focus << std::endl;
    std::cout << "Creativity: " << userStats.creativity << std::endl;
    std::cout << "Memory: " << userStats.memory << std::endl;
    std::cout << "Processing Speed: " << userStats.processingSpeed << std::endl;
    std::cout << "Neural Plasticity: " << userStats.neuralPlasticity << std::endl;
    std::cout << "Qbit Energy: " << userStats.qbitEnergy << std::endl << std::endl;

    // Display neural schema information
    std::cout << "Neural Schema Information:" << std::endl;
    std::cout << "========================" << std::endl;
    std::cout << "Schema ID: " << userStats.cognitiveSchema.schemaID << std::endl;
    std::cout << "Coherence: " << static_cast<int>(userStats.cognitiveSchema.coherence * 100) << "%" << std::endl;
    std::cout << "Complexity: " << static_cast<int>(userStats.cognitiveSchema.complexity * 100) << "%" << std::endl;
    std::cout << "Neuron Types Indexed: " << userStats.cognitiveSchema.neuronTypes.size() << std::endl;
    std::cout << "Enhanced Functions: " << userStats.cognitiveSchema.enhancedFunctions.size() << std::endl;
    for (const std::string& function : userStats.cognitiveSchema.enhancedFunctions) {
        std::cout << "  - " << function << std::endl;
    }
    std::cout << std::endl;

    // Shutdown the system
    std::cout << "16. Shutting down neural enhancement system..." << std::endl;
    ShutdownNeuralEnhancementSystem();
    
    std::cout << "🎉 Demo completed successfully!" << std::endl;
    std::cout << "Thank you for using the JJ Neural Enhancement System!" << std::endl;

    return 0;
}