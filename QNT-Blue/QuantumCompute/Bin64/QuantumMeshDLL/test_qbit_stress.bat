@echo off
REM Test script for Quantum QBit Stress Management Features

echo 🌟 Testing AMD Quantum QBit Stress Management Features 🌟
echo =======================================================
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

REM Run the qbit stress test
echo Running qbit stress management test...
echo.
Release\TestQBitStress.exe
if %errorlevel% neq 0 (
    echo ❌ Test failed with error code %errorlevel%!
    echo.
    cd ..
    pause
    exit /b 1
)

echo.
echo ✅ All qbit stress management tests passed!
echo.

cd ..

REM Run the demo application
echo Running qbit stress management demo...
echo.
build\Release\QBitStressDemo.exe
if %errorlevel% neq 0 (
    echo ❌ Demo failed with error code %errorlevel%!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ QBit stress management demo completed successfully!
echo.

pause