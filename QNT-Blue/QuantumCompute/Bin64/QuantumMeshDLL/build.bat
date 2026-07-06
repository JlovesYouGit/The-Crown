@echo off
REM AMD Quantum Mesh Rendering Boost DLL Build Script
REM Builds the DLL and sample application using CMake and MSVC

echo 🌟 AMD Quantum Mesh Rendering Boost DLL Build Script 🌟
echo ========================================================
echo.

REM Check if CMake is available
cmake --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CMake not found! Please install CMake and add it to your PATH.
    echo.
    pause
    exit /b 1
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
cmake --build . --config Release --target QuantumMeshBoost
cmake --build . --config Release --target SampleApp
cmake --build . --config Release --target EnhancedSampleApp
cmake --build . --config Release --target TestEnhancedAPI
cmake --build . --config Release --target GrainUpscaleDemo
cmake --build . --config Release --target TestGrainUpscale
cmake --build . --config Release --target QBitStressDemo
cmake --build . --config Release --target TestQBitStress
cmake --build . --config Release --target AdaptiveStressDemo
cmake --build . --config Release --target TestAdaptiveStress
cmake --build . --config Release --target AI_FPS_Demo
cmake --build . --config Release --target TestAI_FPS
cmake --build . --config Release --target VR_FarRendering_Demo
cmake --build . --config Release --target TestVR_FarRendering
cmake --build . --config Release --target TestLightingShadows
cmake --build . --config Release --target TestQuantumStateManipulation
if %errorlevel% neq 0 (
    echo ⚠️ CMake build failed, trying simple build approach...
    cd ..
    call build_simple.bat
    if %errorlevel% neq 0 (
        echo ❌ Simple build also failed!
        echo.
        pause
        exit /b 1
    )
    cd build
)

REM Build the service (if CMakeListsService.txt exists)
if exist ..\CMakeListsService.txt (
    echo Building Quantum Rendering Service...
    cmake --build . --config Release --target QuantumRenderService
    if %errorlevel% equ 0 (
        echo Copying service executable...
        copy /Y Release\QuantumRenderService.exe ..\..
    ) else (
        echo ⚠️  CMake service build failed, trying simple build approach...
        cd ..
        call build_service_simple.bat
        if %errorlevel% neq 0 (
            echo ⚠️  Simple service build also failed, continuing without service...
        ) else (
            echo Copying service executable...
            copy /Y Release\QuantumRenderService.exe ..\..
        )
        cd build
    )
) else (
    echo ⚠️  CMakeListsService.txt not found, skipping service build...
)

REM Copy DLL to the main Bin64 directory
echo Copying DLL to main Bin64 directory...
copy /Y Release\QuantumMeshBoost.dll ..\..
if %errorlevel% neq 0 (
    echo ❌ Failed to copy DLL to main directory!
    echo.
    cd ..
    pause
    exit /b 1
)

REM Copy DLL to the main Bin64 directory
echo Copying DLL to main Bin64 directory...
if exist "Release\QuantumMeshBoost.dll" (
    copy /Y Release\QuantumMeshBoost.dll ..\..
    copy /Y Release\ggml-base.dll ..\..
    copy /Y Release\ggml-cpu.dll ..\..
    copy /Y Release\ggml.dll ..\..
) else (
    copy /Y ..\Release\QuantumMeshBoost.dll ..\..
    copy /Y ..\ggml\build-vs\bin\Release\ggml-base.dll ..\..
    copy /Y ..\ggml\build-vs\bin\Release\ggml-cpu.dll ..\..
    copy /Y ..\ggml\build-vs\bin\Release\ggml.dll ..\..
)
if %errorlevel% neq 0 (
    echo ❌ Failed to copy DLLs to main directory!
    echo.
    cd ..
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo    QuantumMeshBoost.dll and dependencies have been created and copied to the Bin64 directory.
echo.
echo To run the sample application, execute:
echo    Release\SampleApp.exe
echo    Release\TestLightingShadows.exe
echo    Release\TestQuantumStateManipulation.exe
echo.
echo To install the background service (optional), run install_background_service.bat as Administrator
echo.
cd ..
pause