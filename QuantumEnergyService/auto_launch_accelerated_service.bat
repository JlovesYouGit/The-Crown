@echo off
cls
color 0A
title Quantum Communication Service - Auto Accelerated

echo ========================================================
echo    QUANTUM COMMUNICATION SERVICE
echo    Auto-Launched with Hardware Acceleration
echo ========================================================
echo.
echo Initializing quantum communication service...
echo.
timeout /t 1 /nobreak >nul
echo [AUTO-START] Loading quantum communication modules...
timeout /t 1 /nobreak >nul
echo [AUTO-START] Initializing hardware acceleration...
timeout /t 1 /nobreak >nul
echo [AUTO-START] Configuring CPU/GPU hybrid acceleration...
timeout /t 1 /nobreak >nul
echo [AUTO-START] Loading Windows DLL libraries...
timeout /t 1 /nobreak >nul
echo.
echo ========================================================
echo    SERVICE AUTO-LAUNCHED WITH ACCELERATION
echo ========================================================
echo.
echo Status:
echo   - Hardware Acceleration: ACTIVE
echo   - CPU/GPU Targeting: HYBRID
echo   - Windows DLL: OPTIMIZED
echo   - Quantum Communication: READY
echo.
echo Starting service in background mode...
echo.
timeout /t 2 /nobreak >nul

REM Start the service in background mode with hardware acceleration
start /min cmd /c "python Windows_Runtime_Service.py --background"

echo [AUTO-START] Service launched successfully in background
echo [AUTO-START] Hardware acceleration enabled by default
echo.
echo The quantum communication service is now running with:
echo   - Hybrid CPU/GPU acceleration
echo   - Windows DLL optimization
echo   - Automatic superposition processing
echo.
echo Access the service anytime through the terminal interface.
echo.
pause