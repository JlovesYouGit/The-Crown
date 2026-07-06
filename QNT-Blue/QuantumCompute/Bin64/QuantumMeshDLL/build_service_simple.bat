@echo off
REM Simple build script for Quantum Rendering Service
REM Uses absolute paths to avoid CMake path issues

echo 🌟 AMD Quantum Rendering Service Simple Build Script 🌟
echo =======================================================
echo.

REM Check if required files exist
echo Checking required files...
if not exist "QuantumRenderService.cpp" (
    echo ❌ QuantumRenderService.cpp not found!
    pause
    exit /b 1
)

if not exist "Release\QuantumMeshBoost.lib" (
    echo ❌ QuantumMeshBoost.lib not found!
    echo    Please build the QuantumMeshBoost DLL first.
    pause
    exit /b 1
)

if not exist "..\ggml\build-vs\src\Release\ggml.lib" (
    echo ❌ ggml.lib not found!
    echo    Expected at: ..\ggml\build-vs\src\Release\ggml.lib
    pause
    exit /b 1
)

echo ✅ All required files found!
echo.

REM Compile the service
echo Compiling Quantum Rendering Service...
"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe" /EHsc /std:c++17 /DWIN32 /D_WINDOWS /DWIN32_LEAN_AND_MEAN ^
   /I"." /I"..\ggml\include" ^
   /I"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include" ^
   /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\ucrt" ^
   /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\um" ^
   /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\shared" ^
   /Fe"Release\QuantumRenderService.exe" ^
   /Fd"Release\QuantumRenderService.pdb" ^
   QuantumRenderService.cpp ^
   "Release\QuantumMeshBoost.lib" ^
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
echo ✅ Quantum Rendering Service compiled successfully!
echo    Output: Release\QuantumRenderService.exe
echo.
echo To install the service, run install_background_service.bat as Administrator
echo.
pause