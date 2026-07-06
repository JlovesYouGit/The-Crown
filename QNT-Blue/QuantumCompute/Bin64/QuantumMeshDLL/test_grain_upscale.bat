@echo off
REM Test script for Quantum Grain & Upscaling Features

echo 🌟 Testing AMD Quantum Grain & Upscaling Features 🌟
echo ==================================================
echo.

REM Check if build directory exists
if not exist build (
    echo ❌ Build directory not found!
    echo Please run build.bat first.
    echo.
    pause
    exit /b 1
)

cd build

REM Run the grain & upscaling test
echo Running grain & upscaling test...
echo.
Release\TestGrainUpscale.exe
if %errorlevel% neq 0 (
    echo ❌ Test failed with error code %errorlevel%!
    echo.
    cd ..
    pause
    exit /b 1
)

echo.
echo ✅ All grain & upscaling tests passed!
echo.

cd ..

REM Run the demo application
echo Running grain & upscaling demo...
echo.
build\Release\GrainUpscaleDemo.exe
if %errorlevel% neq 0 (
    echo ❌ Demo failed with error code %errorlevel%!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Grain & upscaling demo completed successfully!
echo.

pause