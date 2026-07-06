@echo off
REM JJ Neural Enhancement System Build Script
REM Builds the neural enhancement library and demo application

echo 🌟 JJ Neural Enhancement System Build Script 🌟
echo ==============================================
echo.

REM Check if CMake is available
cmake --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CMake not found! Please install CMake and add it to your PATH.
    echo.
    pause
    exit /b 1
)

REM Clean previous build if it exists
echo Cleaning previous build...
if exist build (
    rmdir /s /q build
    if %errorlevel% neq 0 (
        echo ⚠️  Warning: Could not clean previous build directory
    )
)

REM Create build directory
echo Creating build directory...
if not exist build mkdir build
cd build

REM Generate build files with CMake
echo Generating build files with CMake...
cmake .. -G "Visual Studio 17 2022"
if %errorlevel% neq 0 (
    echo ❌ CMake configuration failed!
    echo.
    cd ..
    pause
    exit /b 1
)

REM Build the project
echo Building the project...
cmake --build . --config Release --target NeuralEnhancement
if %errorlevel% neq 0 (
    echo ❌ Neural Enhancement library build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release --target NeuralEnhancementDemo
if %errorlevel% neq 0 (
    echo ❌ Neural Enhancement Demo build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release --target ExtremeOptimizationDemo
if %errorlevel% neq 0 (
    echo ❌ Extreme Optimization Demo build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release --target BodyMappingDemo
if %errorlevel% neq 0 (
    echo ❌ Body Mapping Demo build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release --target VisualizationDemo
if %errorlevel% neq 0 (
    echo ❌ Visualization Demo build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release --target NeuralIntegrationDemo
if %errorlevel% neq 0 (
    echo ❌ Neural Integration Demo build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release --target GenomicEnhancementDemo
if %errorlevel% neq 0 (
    echo ❌ Genomic Enhancement Demo build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release --target BiologicalIntegrationDemo
if %errorlevel% neq 0 (
    echo ❌ Biological Integration Demo build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release --target RealityManipulationDemo
if %errorlevel% neq 0 (
    echo ❌ Reality Manipulation Demo build failed!
    echo.
    cd ..
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo    NeuralEnhancement.dll and all demo applications have been created.
echo.
echo To run the demo applications, execute any of:
echo    Release\NeuralEnhancementDemo.exe
echo    Release\ExtremeOptimizationDemo.exe
echo    Release\BodyMappingDemo.exe
echo    Release\VisualizationDemo.exe
echo    Release\NeuralIntegrationDemo.exe
echo    Release\GenomicEnhancementDemo.exe
echo    Release\BiologicalIntegrationDemo.exe
echo    Release\RealityManipulationDemo.exe
echo.
cd ..
pause