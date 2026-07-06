# AMD Quantum Compiler VR Compatibility Demo CMakeLists.txt

cmake_minimum_required(VERSION 3.10)
project(AMDQuantumVRDemo)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the SDK directory to include paths
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../SDK)

# Create the VR compatibility demo executable
add_executable(vr_compatibility_demo vr_compatibility_demo.cpp)

# Link with the quantum compiler library (assuming it's built as a library)
# In a real implementation, this would link with the actual quantum compiler library
# target_link_libraries(vr_compatibility_demo quantum_compiler)

# For now, we'll just compile the necessary SDK files directly
set(SDK_SOURCES 
    ${CMAKE_CURRENT_SOURCE_DIR}/../SDK/quantum_compiler.cpp
)

# Add the SDK sources to the executable
target_sources(vr_compatibility_demo PRIVATE ${SDK_SOURCES})

# Compiler-specific options
if(MSVC)
    target_compile_options(vr_compatibility_demo PRIVATE /W4)
else()
    target_compile_options(vr_compatibility_demo PRIVATE -Wall -Wextra -pedantic)
endif()

# Installation rules
install(TARGETS vr_compatibility_demo
    RUNTIME DESTINATION bin
)

# Install the sample source file as documentation
install(FILES vr_compatibility_demo.cpp
    DESTINATION share/doc/amd-quantum-vr-demo
)