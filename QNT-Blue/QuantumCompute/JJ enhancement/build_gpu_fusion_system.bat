@echo off
echo Building Advanced GPU Compute-Graphics Fusion System...
echo ====================================================

REM Set up environment
setlocal
set SRC_DIR=src
set BUILD_DIR=build
set OUTPUT_DIR=output

REM Create build directory if it doesn't exist
if not exist %BUILD_DIR% mkdir %BUILD_DIR%
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Compiling GPU Compute-Graphics Fusion System...
echo.

REM Compile the GPU fusion system
g++ -std=c++14 -I%SRC_DIR% -o %BUILD_DIR%\gpu_fusion_demo.exe ^
    %SRC_DIR%\GPUFusionDemo.cpp ^
    %SRC_DIR%\GPUComputeGraphicsFusion.cpp

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Compilation successful!
    echo Moving executable to output directory...
    move %BUILD_DIR%\gpu_fusion_demo.exe %OUTPUT_DIR%\gpu_fusion_demo.exe >nul
    echo.
    echo ====================================================
    echo GPU Compute-Graphics Fusion System Build Complete
    echo Executable: %OUTPUT_DIR%\gpu_fusion_demo.exe
    echo ====================================================
    echo To run the demonstration, execute:
    echo   %OUTPUT_DIR%\gpu_fusion_demo.exe
    echo.
) else (
    echo.
    echo ====================================================
    echo Compilation failed!
    echo Please check for errors above.
    echo ====================================================
)

pause