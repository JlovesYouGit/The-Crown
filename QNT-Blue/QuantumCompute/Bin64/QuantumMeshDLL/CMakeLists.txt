# AMD Quantum Mesh Rendering Boost DLL CMakeLists.txt
# Provides optimized mesh rendering capabilities using quantum computing

cmake_minimum_required(VERSION 3.10)

# Project information
project(QuantumMeshBoostDLL VERSION 1.0.0 DESCRIPTION "AMD Quantum Mesh Rendering Boost DLL")

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set the library name
set(LIBRARY_NAME QuantumMeshBoost)

# Add the library as a shared library (DLL on Windows)
add_library(${LIBRARY_NAME} SHARED
    QuantumMeshBoost.cpp
    QuantumMeshBoost.h
)

# Set preprocessor definitions for Windows DLL export
if(WIN32)
    target_compile_definitions(${LIBRARY_NAME} PRIVATE QUANTUM_MESH_BOOST_EXPORTS WIN32_LEAN_AND_MEAN)
endif()

# Set target properties
set_target_properties(${LIBRARY_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    PUBLIC_HEADER QuantumMeshBoost.h
)

# Set additional properties for Windows
target_compile_definitions(${LIBRARY_NAME} PRIVATE WIN32_LEAN_AND_MEAN)

# Include directories
target_include_directories(${LIBRARY_NAME} PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../../ggml/include
)

# Add Windows SDK include directories
target_include_directories(${LIBRARY_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link libraries (if needed)
target_link_libraries(${LIBRARY_NAME} PRIVATE
    "C:/AMD/AMD Software Cloud Edition 23.Q3/Packages/Apps/QuantumCompute/Bin64/ggml/build-vs/src/Release/ggml.lib"
    "C:/AMD/AMD Software Cloud Edition 23.Q3/Packages/Apps/QuantumCompute/Bin64/ggml/build-vs/src/Release/ggml-base.lib"
    "C:/AMD/AMD Software Cloud Edition 23.Q3/Packages/Apps/QuantumCompute/Bin64/ggml/build-vs/src/Release/ggml-cpu.lib"
)

# Add Windows libraries for service support
target_link_libraries(${LIBRARY_NAME} PRIVATE advapi32)

# Installation rules
install(TARGETS ${LIBRARY_NAME}
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)

# Install service files
install(FILES service_manager.bat DESTINATION bin)
install(FILES QuantumRenderService.cpp DESTINATION src)

# Create enhanced sample application
add_executable(EnhancedSampleApp EnhancedSampleApp.cpp)
target_link_libraries(EnhancedSampleApp PRIVATE ${LIBRARY_NAME})
target_include_directories(EnhancedSampleApp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create enhanced API test
add_executable(TestEnhancedAPI test_enhanced_api.cpp)
target_link_libraries(TestEnhancedAPI PRIVATE ${LIBRARY_NAME})
target_include_directories(TestEnhancedAPI PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create grain & upscaling demo application
add_executable(GrainUpscaleDemo GrainUpscaleDemo.cpp)
target_link_libraries(GrainUpscaleDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(GrainUpscaleDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create grain & upscaling test application
add_executable(TestGrainUpscale test_grain_upscale.cpp)
target_link_libraries(TestGrainUpscale PRIVATE ${LIBRARY_NAME})
target_include_directories(TestGrainUpscale PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create qbit stress management demo application
add_executable(QBitStressDemo QBitStressDemo.cpp)
target_link_libraries(QBitStressDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(QBitStressDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create qbit stress management test application
add_executable(TestQBitStress test_qbit_stress.cpp)
target_link_libraries(TestQBitStress PRIVATE ${LIBRARY_NAME})
target_include_directories(TestQBitStress PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create adaptive stress management demo application
add_executable(AdaptiveStressDemo AdaptiveStressDemo.cpp)
target_link_libraries(AdaptiveStressDemo PRIVATE ${LIBRARY_NAME})
target_include_directories(AdaptiveStressDemo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create adaptive stress management test application
add_executable(TestAdaptiveStress test_adaptive_stress.cpp)
target_link_libraries(TestAdaptiveStress PRIVATE ${LIBRARY_NAME})
target_include_directories(TestAdaptiveStress PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create AI FPS adjustment demo application
add_executable(AI_FPS_Demo AI_FPS_Demo.cpp)
target_link_libraries(AI_FPS_Demo PRIVATE ${LIBRARY_NAME})
target_include_directories(AI_FPS_Demo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create AI FPS adjustment test application
add_executable(TestAI_FPS test_ai_fps.cpp)
target_link_libraries(TestAI_FPS PRIVATE ${LIBRARY_NAME})
target_include_directories(TestAI_FPS PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create VR and far rendering demo application
add_executable(VR_FarRendering_Demo VR_FarRendering_Demo.cpp)
target_link_libraries(VR_FarRendering_Demo PRIVATE ${LIBRARY_NAME})
target_include_directories(VR_FarRendering_Demo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create VR and far rendering test application
add_executable(TestVR_FarRendering test_vr_far_rendering.cpp)
target_link_libraries(TestVR_FarRendering PRIVATE ${LIBRARY_NAME})
target_include_directories(TestVR_FarRendering PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create lighting and shadow enhancement test application
add_executable(TestLightingShadows test_lighting_shadows.cpp)
target_link_libraries(TestLightingShadows PRIVATE ${LIBRARY_NAME})
target_include_directories(TestLightingShadows PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create quantum state manipulation test application
add_executable(TestQuantumStateManipulation test_quantum_state_manipulation.cpp)
target_link_libraries(TestQuantumStateManipulation PRIVATE ${LIBRARY_NAME})
target_include_directories(TestQuantumStateManipulation PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Create a .def file for Windows DLL exports (optional)
if(WIN32)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/QuantumMeshBoost.def.in"
        "${CMAKE_CURRENT_BINARY_DIR}/QuantumMeshBoost.def"
    )
    target_sources(${LIBRARY_NAME} PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/QuantumMeshBoost.def")
endif()

# Include subdirectory for service application
# add_subdirectory(. ${CMAKE_BINARY_DIR}/Service)