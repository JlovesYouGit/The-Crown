@echo off
cls
title Register Quantum Service Auto-Startup

echo ========================================================
echo    REGISTER QUANTUM SERVICE AUTO-STARTUP
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

echo [REGISTRY] Running as Administrator - proceeding with registration
echo.
timeout /t 1 /nobreak >nul

echo [REGISTRY] Adding quantum service to Windows startup...
timeout /t 1 /nobreak >nul

REM Create the registry entry for auto-startup
echo Windows Registry Editor Version 5.00 > temp_registry.reg
echo. >> temp_registry.reg
echo [HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run] >> temp_registry.reg
echo "QuantumCommunicationService"="\"%~dp0auto_launch_accelerated_service.bat\"" >> temp_registry.reg

REM Import the registry file
reg import temp_registry.reg

REM Clean up temporary file
del temp_registry.reg

echo.
echo [REGISTRY] Quantum service registered for auto-startup
echo.
echo The service will now automatically start with:
echo   - Hardware acceleration enabled
echo   - Hybrid CPU/GPU targeting
echo   - Windows DLL optimization
echo   - Background operation
echo.
echo To uninstall, run 'unregister_auto_startup.bat'
echo.
pause