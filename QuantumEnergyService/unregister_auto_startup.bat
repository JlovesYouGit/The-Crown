@echo off
cls
title Unregister Quantum Service Auto-Startup

echo ========================================================
echo    UNREGISTER QUANTUM SERVICE AUTO-STARTUP
echo    Windows Registry Configuration
echo ========================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [ERROR] This script must be run as Administrator
    echo [ERROR] Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [REGISTRY] Running as Administrator - proceeding with unregistration
echo.
timeout /t 1 /nobreak >nul

echo [REGISTRY] Removing quantum service from Windows startup...
timeout /t 1 /nobreak >nul

REM Create the registry entry to remove the key
echo Windows Registry Editor Version 5.00 > temp_registry.reg
echo. >> temp_registry.reg
echo [HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run] >> temp_registry.reg
echo "QuantumCommunicationService"=- >> temp_registry.reg

REM Import the registry file
reg import temp_registry.reg

REM Clean up temporary file
del temp_registry.reg

echo.
echo [REGISTRY] Quantum service unregistered from auto-startup
echo.
echo The service will no longer automatically start with Windows.
echo.
echo To reinstall, run 'register_auto_startup.bat'
echo.
pause