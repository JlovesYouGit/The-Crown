@echo off
REM AMD Quantum Compiler VR Compatibility Demo Build Script

echo AMD Quantum Compiler VR Compatibility Demo Build Script
echo ======================================================

REM Check if cmake is available
cmake --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: CMake is not installed or not in PATH
    echo Please install CMake 3.10 or higher
    pause
    exit /b 1
)

REM Create build directory
echo Creating build directory...
if not exist build mkdir build
cd build

REM Generate build files
echo Generating build files...
cmake .. -G "Visual Studio 17 2022"

if %errorlevel% neq 0 (
    echo Error: Failed to generate build files
    cd ..
    pause
    exit /b 1
)

REM Build the project
echo Building the project...
cmake --build . --config Release

if %errorlevel% neq 0 (
    echo Error: Failed to build the project
    cd ..
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable location: build\Release\vr_compatibility_demo.exe
echo.
echo To run the demo, execute:
echo   cd build\Release
echo   vr_compatibility_demo.exe
echo.

cd ..
pause