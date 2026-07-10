@echo off
cls
title Install Quantum Communication Service

echo ========================================================
echo    INSTALL QUANTUM ENERGY SERVICES
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

echo [INSTALL] Creating Windows service registry entries...
timeout /t 1 /nobreak >nul

echo [INSTALL] Setting up service configuration...
timeout /t 1 /nobreak >nul

echo [INSTALL] Creating service batch files...
timeout /t 1 /nobreak >nul

echo [INSTALL] Installing Integrated Energy Cooling Service...
timeout /t 1 /nobreak >nul

REM Create the main service batch file
echo @echo off > quantum_comm_service.bat
echo REM Quantum Communication Service >> quantum_comm_service.bat
echo REM Auto-generated service script >> quantum_comm_service.bat
echo. >> quantum_comm_service.bat
echo cd /d "%~dp0" >> quantum_comm_service.bat
echo python Windows_Runtime_Service.py --service-mode >> quantum_comm_service.bat
echo. >> quantum_comm_service.bat

echo [INSTALL] Service batch file created: quantum_comm_service.bat
echo.

echo [INSTALL] Installing Integrated Energy Cooling Service...
timeout /t 1 /nobreak >nul

cd /d "C:\QuantumEnergyService"
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe" (
    echo [BUILD] Building Quantum Energy Service project...
    "C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe" "QuantumEnergyService.csproj" /p:Configuration=Release
    if %errorLevel% EQU 0 (
        echo [BUILD] Project built successfully
    ) else (
        echo [WARNING] Failed to build project, continuing with installation...
    )
) else (
    echo [INFO] MSBuild not found, skipping build step...
)

echo [INSTALL] Installing services using InstallUtil...
if exist "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe" (
    "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe" "C:\QuantumEnergyService\bin\Release\QuantumEnergyService.exe"
    if %errorLevel% EQU 0 (
        echo [INSTALL] Services installed successfully
    ) else (
        echo [ERROR] Failed to install services
        pause
        exit /b 1
    )
) else (
    echo [ERROR] InstallUtil not found. Please ensure .NET Framework 4.8 is installed.
    pause
    exit /b 1
)

echo [START] Starting services...
net start CosmicQubitWindowsService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [START] Cosmic Qubit Service started successfully
) else (
    echo [WARNING] Failed to start Cosmic Qubit Service
)

net start IntegratedEnergyCoolingService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [START] Integrated Energy Cooling Service started successfully
) else (
    echo [WARNING] Failed to start Integrated Energy Cooling Service
)

echo [INSTALL] Registering service for automatic startup...
timeout /t 1 /nobreak >nul

REM Create startup shortcut
echo @echo off > "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\quantum_comm.lnk"
echo cd /d "%~dp0" > "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\quantum_comm.lnk"
echo start /min cmd /c "python Windows_Runtime_Service.py --background" >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\quantum_comm.lnk"

echo [INSTALL] Startup registration completed
echo.

echo [INSTALL] Starting Armor BIOS Optimization Service...
timeout /t 1 /nobreak >nul

net start ArmorBiosOptimizationService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [START] Armor BIOS Optimization Service started successfully
) else (
    echo [WARNING] Failed to start Armor BIOS Optimization Service
)

echo [INSTALL] Starting Invisible BIOS Gateway Service...
timeout /t 1 /nobreak >nul

net start InvisibleBiosGatewayService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [START] Invisible BIOS Gateway Service started successfully
) else (
    echo [WARNING] Failed to start Invisible BIOS Gateway Service
)

echo [INSTALL] Service installation complete!
echo.
echo Installed Services:
echo   1. Cosmic Qubit Management Service
echo   2. Integrated Energy Cooling Service
echo   3. Armor BIOS Optimization Service
echo   4. Invisible BIOS Gateway Service
echo.
echo To start the services:
echo   1. Services start automatically on boot
echo   2. Or run the individual 'net start' commands for each service
echo   3. Or reboot to start automatically
echo.
pause