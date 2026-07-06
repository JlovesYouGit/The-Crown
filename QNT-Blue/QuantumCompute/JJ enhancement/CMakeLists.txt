# JJ Neural Enhancement System CMakeLists.txt
# CMake configuration for the neural enhancement system

cmake_minimum_required(VERSION 3.10)

# Project information
project(JJNeuralEnhancement VERSION 1.0.0 DESCRIPTION "JJ USB Transmission Neural Enhancement System")

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set the library name
set(LIBRARY_NAME NeuralEnhancement)

# Add the library as a static library
add_library(${LIBRARY_NAME} STATIC
    src/NeuralEnhancementSystem.cpp
    src/NeuralEnhancementSystem.h
    src/NeuralIntegrationSystem.cpp
    src/NeuralOptimizationExtremes.cpp
    src/NeuralOptimizationExtremes.h
    src/BodyMappingSystem.cpp
    src/BodyMappingSystem.h
    src/GenomicEnhancementSystem.cpp
    src/GenomicEnhancementSystem.h
    src/FinancialModelingSystem.cpp
    src/FinancialModelingSystem.h
    # Exclude problematic files that cause compilation errors
    # src/BiologicalIntegrationSystem.cpp
    # src/BiologicalIntegrationSystem.h
    # src/RealityManipulationSystem.cpp
    # src/RealityManipulationSystem.h
)

# Set target properties
set_target_properties(${LIBRARY_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    PUBLIC_HEADER src/NeuralEnhancementSystem.h
)

# Include directories
target_include_directories(${LIBRARY_NAME} PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Create demo applications
add_executable(NeuralEnhancementDemo src/NeuralEnhancementDemo.cpp)
target_link_libraries(NeuralEnhancementDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(NeuralEnhancementDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

add_executable(ExtremeOptimizationDemo src/ExtremeOptimizationDemo.cpp)
target_link_libraries(ExtremeOptimizationDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(ExtremeOptimizationDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

add_executable(BodyMappingDemo src/BodyMappingDemo.cpp)
target_link_libraries(BodyMappingDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(BodyMappingDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New visualization demo
add_executable(VisualizationDemo src/VisualizationDemo.cpp)
target_link_libraries(VisualizationDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(VisualizationDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New neural integration demo
add_executable(NeuralIntegrationDemo src/NeuralIntegrationDemo.cpp)
target_link_libraries(NeuralIntegrationDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(NeuralIntegrationDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New genomic enhancement demo
add_executable(GenomicEnhancementDemo src/GenomicEnhancementDemo.cpp)
target_link_libraries(GenomicEnhancementDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(GenomicEnhancementDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New coherent learning demo
add_executable(CoherentLearningDemo src/CoherentLearningDemo.cpp)
target_link_libraries(CoherentLearningDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(CoherentLearningDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New genius memory demo
add_executable(GeniusMemoryDemo src/GeniusMemoryDemo.cpp)
target_link_libraries(GeniusMemoryDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(GeniusMemoryDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New continuous evolution demo
add_executable(ContinuousEvolutionDemo src/ContinuousEvolutionDemo.cpp)
target_link_libraries(ContinuousEvolutionDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(ContinuousEvolutionDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New brain simulation demo
add_executable(BrainSimulationDemo src/BrainSimulationDemo.cpp)
target_link_libraries(BrainSimulationDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(BrainSimulationDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New comprehensive testing demo
add_executable(ComprehensiveTestingDemo src/ComprehensiveTestingDemo.cpp)
target_link_libraries(ComprehensiveTestingDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(ComprehensiveTestingDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New financial modeling demo
add_executable(FinancialModelingDemo src/FinancialModelingDemo.cpp)
target_link_libraries(FinancialModelingDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(FinancialModelingDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New quantum mining demo
add_executable(QuantumMiningDemo src/QuantumMiningDemo.cpp)
target_link_libraries(QuantumMiningDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(QuantumMiningDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# New reality overlap demo
add_executable(RealityOverlapDemo src/RealityOverlapDemo.cpp)
target_link_libraries(RealityOverlapDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(RealityOverlapDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Installation rules
install(TARGETS ${LIBRARY_NAME}
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)

install(TARGETS NeuralEnhancementDemo ExtremeOptimizationDemo BodyMappingDemo VisualizationDemo NeuralIntegrationDemo GenomicEnhancementDemo CoherentLearningDemo GeniusMemoryDemo ContinuousEvolutionDemo BrainSimulationDemo ComprehensiveTestingDemo FinancialModelingDemo QuantumMiningDemo RealityOverlapDemo
    RUNTIME DESTINATION bin
)