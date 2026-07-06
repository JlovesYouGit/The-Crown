@echo off
REM AMD Quantum Mesh Rendering Boost DLL Installation Verification Script
REM Verifies that all required components are properly installed

echo 🌟 AMD Quantum Mesh Rendering Boost DLL Installation Verification 🌟
echo =====================================================================
echo.

echo Checking required components...
echo.

REM Check if the main DLL exists
echo 1. Checking QuantumMeshBoost.dll...
if exist "QuantumMeshBoost.dll" (
    echo    ✅ QuantumMeshBoost.dll found
) else (
    echo    ❌ QuantumMeshBoost.dll not found
)

REM Check if GGML DLLs exist
echo 2. Checking GGML dependencies...
if exist "ggml.dll" (
    echo    ✅ ggml.dll found
) else (
    echo    ❌ ggml.dll not found
)

if exist "ggml-base.dll" (
    echo    ✅ ggml-base.dll found
) else (
    echo    ❌ ggml-base.dll not found
)

if exist "ggml-cpu.dll" (
    echo    ✅ ggml-cpu.dll found
) else (
    echo    ❌ ggml-cpu.dll not found
)

REM Check if the model exists
echo 3. Checking lightweight AI model...
if exist "..\Models\quantum_render_optimization.gguf" (
    echo    ✅ quantum_render_optimization.gguf found
) else (
    echo    ❌ quantum_render_optimization.gguf not found
)

REM Check if header files exist
echo 4. Checking header files...
if exist "QuantumMeshBoost.h" (
    echo    ✅ QuantumMeshBoost.h found
) else (
    echo    ❌ QuantumMeshBoost.h not found
)

if exist "..\ggml\include\ggml.h" (
    echo    ✅ ggml.h found
) else (
    echo    ❌ ggml.h not found
)

if exist "..\ggml\include\gguf.h" (
    echo    ✅ gguf.h found
) else (
    echo    ❌ gguf.h not found
)

echo.
echo 5. Checking build tools...
cmake --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ CMake found
) else (
    echo    ❌ CMake not found
)

echo.
echo Verification complete!
echo.
echo If all components are marked with ✅, the system is ready for use.
echo If any components are marked with ❌, please check the installation.
echo.
pause