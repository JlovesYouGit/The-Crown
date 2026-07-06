@echo off
REM AMD Quantum Rendering Service Build Script
REM Builds the Windows service for background quantum rendering

echo 🌟 AMD Quantum Rendering Service Build Script 🌟
echo ===============================================
echo.

REM Check if running in the correct directory
if not exist "QuantumRenderService.cpp" (
    echo ❌ QuantumRenderService.cpp not found!
    echo    Please run this script from the QuantumMeshDLL directory.
    echo.
    pause
    exit /b 1
)

REM Create build directory
echo Creating build directory...
if not exist "build-service" mkdir "build-service"
cd "build-service"

REM Run CMake to generate build files
echo Generating build files with CMake...
cmake -G "Visual Studio 17 2022" -A x64 .. -DCMAKE_BUILD_TYPE=Release
if %errorlevel% neq 0 (
    echo ❌ CMake failed to generate build files
    cd ..
    pause
    exit /b 1
)

REM Build the service
echo Building the service...
cmake --build . --config Release
if %errorlevel% neq 0 (
    echo ❌ Build failed
    cd ..
    pause
    exit /b 1
)

REM Copy the executable to the main directory
echo Copying service executable...
copy "Release\QuantumRenderService.exe" "..\"
if %errorlevel% neq 0 (
    echo ❌ Failed to copy executable
    cd ..
    pause
    exit /b 1
)

REM Copy configuration file if it doesn't exist
if not exist "..\config.ini" (
    echo Copying configuration file...
    copy "..\config.ini.example" "..\config.ini" >nul 2>&1
)

cd ..

echo.
echo ✅ AMD Quantum Rendering Service built successfully!
echo.
echo To install the service:
echo   1. Run install_background_service.bat as Administrator
echo.
pause