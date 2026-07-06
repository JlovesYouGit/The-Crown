@echo off
REM Test script for Quantum VR and Far Rendering Features

echo 🌟 Testing AMD Quantum VR and Far Rendering Features 🌟
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

REM Run the VR and far rendering test
echo Running VR and far rendering test...
echo.
Release\TestVR_FarRendering.exe
if %errorlevel% neq 0 (
    echo ❌ Test failed with error code %errorlevel%!
    echo.
    cd ..
    pause
    exit /b 1
)

echo.
echo ✅ All VR and far rendering tests passed!
echo.

cd ..

REM Run the demo application
echo Running VR and far rendering demo...
echo.
build\Release\VR_FarRendering_Demo.exe
if %errorlevel% neq 0 (
    echo ❌ Demo failed with error code %errorlevel%!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ VR and far rendering demo completed successfully!
echo.

pause