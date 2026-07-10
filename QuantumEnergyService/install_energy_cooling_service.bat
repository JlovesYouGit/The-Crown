@echo off
cls
title Install Integrated Energy Cooling Service

echo ========================================================
echo    INSTALL INTEGRATED ENERGY COOLING SERVICE
echo    Windows Service Installation
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

echo [INSTALL] Running as Administrator - proceeding with installation
echo.
timeout /t 1 /nobreak >nul

echo [INSTALL] Building the Quantum Energy Service project...
timeout /t 1 /nobreak >nul

REM Navigate to the project directory
cd /d "C:\QuantumEnergyService"

REM Build the project using MSBuild if available
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe" (
    echo [BUILD] Using MSBuild to build project...
    "C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe" "QuantumEnergyService.csproj" /p:Configuration=Release
    if %errorLevel% EQU 0 (
        echo [BUILD] Project built successfully
    ) else (
        echo [WARNING] Failed to build project, continuing with installation...
    )
) else (
    echo [INFO] MSBuild not found, skipping build step...
)

echo.
echo [INSTALL] Installing Integrated Energy Cooling Service...
timeout /t 1 /nobreak >nul

REM Install the service using InstallUtil
if exist "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe" (
    echo [INSTALL] Using InstallUtil to install service...
    "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe" "C:\QuantumEnergyService\bin\Release\QuantumEnergyService.exe"
    if %errorLevel% EQU 0 (
        echo [INSTALL] Service installed successfully
    ) else (
        echo [ERROR] Failed to install service
        pause
        exit /b 1
    )
) else (
    echo [ERROR] InstallUtil not found. Please ensure .NET Framework 4.8 is installed.
    pause
    exit /b 1
)

echo.
echo [START] Starting Integrated Energy Cooling Service...
timeout /t 1 /nobreak >nul

REM Start the service
net start IntegratedEnergyCoolingService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [START] Service started successfully
) else (
    echo [WARNING] Failed to start service. You may need to start it manually.
)

echo.
echo [INSTALL] Service installation complete!
echo.
echo Service Details:
echo   Name: IntegratedEnergyCoolingService
echo   Display Name: Integrated Energy Cooling Service
echo.
echo To check service status:
echo   Open Services.msc
echo   Or run: sc query IntegratedEnergyCoolingService
echo.
pause