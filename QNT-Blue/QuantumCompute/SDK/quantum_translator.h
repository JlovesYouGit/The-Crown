/*
 * AMD Quantum-Classical Translator Header
 * Translates classical computations to quantum operations
 */

#ifndef AMD_QUANTUM_TRANSLATOR_H
#define AMD_QUANTUM_TRANSLATOR_H

#include <string>
#include <vector>
#include <memory>

namespace amd {
namespace quantum {

    // Translation modes
    enum class TranslationMode {
        AUTO_DETECT = 0,
        CLASSICAL_TO_QUANTUM = 1,
        QUANTUM_TO_CLASSICAL = 2,
        HYBRID = 3
    };

    // Computation types
    enum class ComputationType {
        ARITHMETIC = 0,
        LOGICAL = 1,
        SEARCH = 2,
        OPTIMIZATION = 3,
        SIMULATION = 4,
        MESH_RENDERING = 5
    };

    // Translation result
    struct TranslationResult {
        bool success;
        std::string quantum_code;
        std::string error_message;
        double translation_time;
        ComputationType detected_type;
        bool quantum_accelerated;
        int mesh_count;
        double fps_improvement_factor;
        int tracked_axes;
        double movement_precision;
    };

    // Quantum translator interface
    class QuantumTranslator {
    public:
        QuantumTranslator();
        ~QuantumTranslator();

        // Set translation mode
        void setTranslationMode(TranslationMode mode);

        // Translate classical code to quantum operations
        TranslationResult translateToQuantum(const std::string& classical_code);

        // Optimize classical code using quantum principles
        TranslationResult optimizeWithQuantum(const std::string& classical_code);

        // Optimize mesh rendering using quantum parallelism
        TranslationResult optimizeMeshRendering(const std::string& rendering_code);

        // Track objects in all axes and movements
        TranslationResult trackObjectsInAxes(const std::string& tracking_code);

        // Check if computation can benefit from quantum acceleration
        bool canQuantumAccelerate(const std::string& classical_code);

        // Get translator version
        std::string getVersion() const;

    private:
        TranslationMode translation_mode_;
        std::string version_;
        
        // Helper functions
        ComputationType detectComputationType(const std::string& code);
        std::string generateQuantumCode(const std::string& classical_code, ComputationType type);
        bool validateQuantumCode(const std::string& quantum_code);
    };

    // Factory function for creating quantum translator instances
    std::unique_ptr<QuantumTranslator> createQuantumTranslator();

} // namespace quantum
} // namespace amd

#endif // AMD_QUANTUM_TRANSLATOR_H