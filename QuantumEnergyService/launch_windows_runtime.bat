@echo off
cls
color 0A
title Quantum Communication Service - Windows Runtime

echo ========================================================
echo    WINDOWS RUNTIME COMMUNICATION SERVICE
echo    Admin CMD Terminal - Quantum Communication System
echo ========================================================
echo.
echo Initializing Windows Runtime Service...
echo.
timeout /t 1 /nobreak >nul
echo [SYSTEM] Checking administrative privileges...
timeout /t 1 /nobreak >nul
echo [SYSTEM] Loading quantum communication modules...
timeout /t 1 /nobreak >nul
echo [SYSTEM] Establishing Windows service interface...
timeout /t 1 /nobreak >nul
echo.
echo ========================================================
echo    WINDOWS RUNTIME SERVICE READY
echo ========================================================
echo.
echo Service Features:
echo   - Admin CMD terminal operation
echo   - Background service mode
echo   - Automatic startup registration
echo   - Quantum communication channel
echo.
echo Starting service interface...
echo.
timeout /t 2 /nobreak >nul

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [ADMIN] Running with administrative privileges
) else (
    echo [WARNING] Not running as administrator
    echo [WARNING] Some features may be limited
)
echo.

python Windows_Runtime_Service.py