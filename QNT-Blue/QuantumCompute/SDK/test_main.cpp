/*
 * AMD Quantum Compiler Test Application
 * Simple test to validate the quantum compiler implementation
 */

#include "quantum_compiler.h"
#include <iostream>
#include <string>

int main() {
    std::cout << "AMD Quantum Compiler Test\n";
    std::cout << "========================\n";

    // Create quantum compiler instance
    auto compiler = amd::quantum::createQuantumCompiler();
    
    // Check version
    std::cout << "Compiler Version: " << compiler->getVersion() << std::endl;
    
    // Check quantum support
    std::cout << "Quantum Support: " << (compiler->isQuantumSupported() ? "Yes" : "No") << std::endl;
    
    // Set optimization level
    compiler->setOptimizationLevel(amd::quantum::OptimizationLevel::QUANTUM_ENHANCED);
    
    // Simple test code
    std::string test_code = R"(
        int main() {
            int a = 5;
            int b = 10;
            int c = a + b;
            return c;
        }
    )";
    
    // Compile the code
    auto result = compiler->compile(test_code, "test_output.bin");
    
    // Display results
    std::cout << "\nCompilation Results:\n";
    std::cout << "  Success: " << (result.success ? "Yes" : "No") << std::endl;
    std::cout << "  Output File: " << result.output_binary << std::endl;
    std::cout << "  Compilation Time: " << result.compilation_time << " seconds" << std::endl;
    std::cout << "  Optimized Instructions: " << result.optimized_instructions << std::endl;
    
    if (!result.error_message.empty()) {
        std::cout << "  Error: " << result.error_message << std::endl;
    }
    
    std::cout << "\nTest completed successfully!\n";
    
    return 0;
}