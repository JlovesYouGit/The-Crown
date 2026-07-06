#include "QEtherNetwork.h"
#include <iostream>

int main() {
    std::cout << "=== QEther Network Self-Management System Test ===" << std::endl;
    
    // Create QEther Network instance
    QEtherNetwork network;
    
    // Initialize the network
    std::cout << "1. Initializing QEther Network..." << std::endl;
    if (!network.initializeNetwork()) {
        std::cerr << "Failed to initialize network!" << std::endl;
        return -1;
    }
    
    // Configure the network
    std::cout << "2. Configuring QEther Network..." << std::endl;
    QEtherConfig config;
    config.enableGlobalTracing = true;
    config.enableAntiBacktrack = true;
    network.configureQEther(config);
    
    // Check initial nodes
    auto nodes = network.getNetworkNodes();
    std::cout << "3. Initial network has " << nodes.size() << " nodes" << std::endl;
    
    // Enable self-management for all nodes
    std::cout << "4. Enabling self-management for all nodes..." << std::endl;
    for (const auto& node : nodes) {
        network.enableNodeSelfManagement(node.nodeId);
        std::cout << "   Enabled self-management for Node #" << node.nodeId << std::endl;
    }
    
    // Create a new node
    std::cout << "5. Creating a new node..." << std::endl;
    int newNodeId = network.createQEtherNode("Test_Node", "Test_Location", "TEST_REGION");
    if (newNodeId > 0) {
        std::cout << "   Created new Node #" << newNodeId << std::endl;
        network.enableNodeSelfManagement(newNodeId);
        std::cout << "   Enabled self-management for new Node #" << newNodeId << std::endl;
    }
    
    // Perform automatic maintenance
    std::cout << "6. Performing automatic node maintenance..." << std::endl;
    network.performAutomaticNodeMaintenance();
    
    // Check node health
    std::cout << "7. Checking node health..." << std::endl;
    auto updatedNodes = network.getNetworkNodes();
    for (const auto& node : updatedNodes) {
        bool isHealthy = network.isNodeHealthy(node.nodeId);
        std::cout << "   Node #" << node.nodeId << " (" << node.nodeName << "): " 
                  << (isHealthy ? "HEALTHY" : "UNHEALTHY") 
                  << " (Health: " << node.healthStatus << ")" << std::endl;
    }
    
    // Test broken node management
    std::cout << "8. Testing broken node management..." << std::endl;
    network.manageBrokenNodes();
    
    // Final status report
    std::cout << "9. Generating final status report..." << std::endl;
    std::cout << network.getNetworkStatusReport() << std::endl;
    
    std::cout << "=== Test Complete ===" << std::endl;
    return 0;
}