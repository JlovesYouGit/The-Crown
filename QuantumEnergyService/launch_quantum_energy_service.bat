@echo off
cls
title Launch Quantum Energy Service Control Panel

echo ========================================================
echo    LAUNCH QUANTUM ENERGY SERVICE CONTROL PANEL
echo    Integrated Energy Management System
echo ========================================================
echo.

echo [LAUNCH] Starting Quantum Energy Service Master Control...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [WARNING] Not running as Administrator
    echo [INFO] Some functions may be limited without admin privileges
    echo.
)

REM Check if PowerShell script exists
if exist "C:\QuantumEnergyService\master_control.ps1" (
    echo [LAUNCH] Opening Master Control Panel...
    timeout /t 2 /nobreak >nul
    powershell -ExecutionPolicy Bypass -File "C:\QuantumEnergyService\master_control.ps1"
) else (
    echo [ERROR] Master control script not found!
    echo Please ensure all files are in place.
    echo.
    pause
    exit /b 1
)

echo.
echo [COMPLETE] Quantum Energy Service Control Panel closed.
echo.
pause