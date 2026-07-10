@echo off
cls
title Uninstall Armor BIOS Optimization Service

echo ========================================================
echo    UNINSTALL ARMOR BIOS OPTIMIZATION SERVICE
echo    Windows Service Removal
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

echo [UNINSTALL] Running as Administrator - proceeding with uninstallation
echo.
timeout /t 1 /nobreak >nul

echo [STOP] Stopping Armor BIOS Optimization Service...
timeout /t 1 /nobreak >nul

REM Stop the service if it's running
net stop ArmorBiosOptimizationService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [STOP] Service stopped successfully
) else (
    echo [INFO] Service was not running or not found
)

echo.
echo [UNINSTALL] Removing Armor BIOS Optimization Service...
timeout /t 1 /nobreak >nul

REM Uninstall the service using InstallUtil
if exist "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe" (
    echo [UNINSTALL] Using InstallUtil to uninstall service...
    "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe" /u "C:\QuantumEnergyService\bin\Release\QuantumEnergyService.exe"
    if %errorLevel% EQU 0 (
        echo [UNINSTALL] Service uninstalled successfully
    ) else (
        echo [ERROR] Failed to uninstall service
        pause
        exit /b 1
    )
) else (
    echo [ERROR] InstallUtil not found. Cannot uninstall service.
    pause
    exit /b 1
)

echo.
echo [UNINSTALL] Armor BIOS Optimization Service uninstallation complete!
echo.
echo The service has been removed from your system.
echo.
pause