@echo off
REM Simple build script for QuantumMeshBoost DLL
REM Uses absolute paths to avoid CMake path issues

echo 🌟 AMD Quantum Mesh Rendering Boost DLL Simple Build Script 🌟
echo =================================================================
echo.

REM Check if required files exist
echo Checking required files...
if not exist "QuantumMeshBoost.cpp" (
    echo ❌ QuantumMeshBoost.cpp not found!
    pause
    exit /b 1
)

if not exist "QuantumMeshBoost.h" (
    echo ❌ QuantumMeshBoost.h not found!
    pause
    exit /b 1
)

if not exist "..\ggml\build-vs\src\Release\ggml.lib" (
    echo ❌ ggml.lib not found!
    echo    Expected at: ..\ggml\build-vs\src\Release\ggml.lib
    pause
    exit /b 1
)

if not exist "..\ggml\build-vs\src\Release\ggml-base.lib" (
    echo ❌ ggml-base.lib not found!
    echo    Expected at: ..\ggml\build-vs\src\Release\ggml-base.lib
    pause
    exit /b 1
)

if not exist "..\ggml\build-vs\src\Release\ggml-cpu.lib" (
    echo ❌ ggml-cpu.lib not found!
    echo    Expected at: ..\ggml\build-vs\src\Release\ggml-cpu.lib
    pause
    exit /b 1
)

echo ✅ All required files found!
echo.

REM Create output directory
if not exist "Release" mkdir "Release"

REM Compile the DLL
echo Compiling QuantumMeshBoost DLL...
"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe" /LD /EHsc /std:c++17 /DWIN32 /D_WINDOWS /DQUANTUM_MESH_BOOST_EXPORTS /DWIN32_LEAN_AND_MEAN ^
   /I"." /I"..\ggml\include" ^
   /I"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include" ^
   /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\ucrt" ^
   /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\um" ^
   /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\shared" ^
   /Fe"Release\QuantumMeshBoost.dll" ^
   /Fd"Release\QuantumMeshBoost.pdb" ^
   QuantumMeshBoost.cpp ^
   "..\ggml\build-vs\src\Release\ggml.lib" ^
   "..\ggml\build-vs\src\Release\ggml-base.lib" ^
   "..\ggml\build-vs\src\Release\ggml-cpu.lib" ^
   advapi32.lib

if %errorlevel% neq 0 (
    echo ❌ Compilation failed!
    pause
    exit /b 1
)

echo.
echo ✅ QuantumMeshBoost DLL compiled successfully!
echo    Output: Release\QuantumMeshBoost.dll
echo.
echo To run the sample application, execute:
echo    cl /EHsc /std:c++17 /I"." /I"..\ggml\include" SampleApp.cpp Release\QuantumMeshBoost.lib
echo.
pause