@echo off
REM Test script for Quantum AI FPS Adjustment Features

echo 🌟 Testing AMD Quantum AI FPS Adjustment Features 🌟
echo ===============================================
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

REM Run the AI FPS test
echo Running AI FPS adjustment test...
echo.
Release\TestAI_FPS.exe
if %errorlevel% neq 0 (
    echo ❌ Test failed with error code %errorlevel%!
    echo.
    cd ..
    pause
    exit /b 1
)

echo.
echo ✅ All AI FPS adjustment tests passed!
echo.

cd ..

REM Run the demo application
echo Running AI FPS adjustment demo...
echo.
build\Release\AI_FPS_Demo.exe
if %errorlevel% neq 0 (
    echo ❌ Demo failed with error code %errorlevel%!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ AI FPS adjustment demo completed successfully!
echo.

pause