# AMD Quantum Compilation System CMake Configuration
cmake_minimum_required(VERSION 3.20)
project(AMDQuantumCompiler VERSION 1.0.0001 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Check for quantum computing support
option(ENABLE_QUANTUM "Enable quantum computing support" ON)

# Compiler-specific settings
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -pedantic)
endif()

# Source files
set(SOURCES
    quantum_compiler.cpp
    quantum_translator.cpp
)

# Header files
set(HEADERS
    quantum_compiler.h
    quantum_translator.h
)

# Create the library
add_library(amd_quantum_compiler ${SOURCES} ${HEADERS})

# Set include directories
target_include_directories(amd_quantum_compiler PUBLIC 
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link libraries
if(ENABLE_QUANTUM)
    # In a real implementation, we would link against AMD's quantum SDK
    # target_link_libraries(amd_quantum_compiler PRIVATE amd_quantum_sdk)
endif()

# Create a simple test executable
add_executable(quantum_compiler_test test_main.cpp)
target_link_libraries(quantum_compiler_test PRIVATE amd_quantum_compiler)

# Create translator demo executable
add_executable(quantum_translator_demo translator_demo.cpp)
target_link_libraries(quantum_translator_demo PRIVATE amd_quantum_compiler)

# Add subdirectory for Quantum Mesh DLL
add_subdirectory(../Bin64/QuantumMeshDLL ${CMAKE_BINARY_DIR}/QuantumMeshDLL)

# Installation rules
install(TARGETS amd_quantum_compiler
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES ${HEADERS} DESTINATION include/amd/quantum)

# Install translator demo
install(TARGETS quantum_translator_demo RUNTIME DESTINATION bin)

# Package configuration
set(CPACK_PACKAGE_NAME "AMDQuantumCompiler")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION "Quantum-enhanced compilation system with classical-quantum translation for AMD processors")
set(CPACK_PACKAGE_CONTACT "AMD Quantum Team <quantum.support@amd.com>")
include(CPack)