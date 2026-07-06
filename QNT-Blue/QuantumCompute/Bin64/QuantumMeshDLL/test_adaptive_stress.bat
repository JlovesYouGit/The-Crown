@echo off
REM Test script for Quantum Adaptive Stress Management Features

echo 🌟 Testing AMD Quantum Adaptive Stress Management Features 🌟
echo =========================================================
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

REM Run the adaptive stress test
echo Running adaptive stress management test...
echo.
Release\TestAdaptiveStress.exe
if %errorlevel% neq 0 (
    echo ❌ Test failed with error code %errorlevel%!
    echo.
    cd ..
    pause
    exit /b 1
)

echo.
echo ✅ All adaptive stress management tests passed!
echo.

cd ..

REM Run the demo application
echo Running adaptive stress management demo...
echo.
build\Release\AdaptiveStressDemo.exe
if %errorlevel% neq 0 (
    echo ❌ Demo failed with error code %errorlevel%!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Adaptive stress management demo completed successfully!
echo.

pause