@echo off
cls
title Verify Quantum Energy Service Installation

echo ========================================================
echo    VERIFY QUANTUM ENERGY SERVICE INSTALLATION
echo    Windows Service Verification
echo ========================================================
echo.

echo [VERIFY] Checking if services are installed...
echo.

echo Checking Cosmic Qubit Management Service...
sc query CosmicQubitWindowsService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [OK] Cosmic Qubit Management Service is installed
) else (
    echo [ERROR] Cosmic Qubit Management Service is not installed
)

echo.
echo Checking Integrated Energy Cooling Service...
sc query IntegratedEnergyCoolingService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [OK] Integrated Energy Cooling Service is installed
) else (
    echo [ERROR] Integrated Energy Cooling Service is not installed
)

echo.
echo Checking Armor BIOS Optimization Service...
sc query ArmorBiosOptimizationService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [OK] Armor BIOS Optimization Service is installed
) else (
    echo [ERROR] Armor BIOS Optimization Service is not installed
)

echo.
echo Checking Invisible BIOS Gateway Service...
sc query InvisibleBiosGatewayService >nul 2>&1
if %errorLevel% EQU 0 (
    echo [OK] Invisible BIOS Gateway Service is installed
) else (
    echo [ERROR] Invisible BIOS Gateway Service is not installed
)

echo.
echo [VERIFY] Checking service statuses...
echo.

echo Cosmic Qubit Management Service status:
sc query CosmicQubitWindowsService | findstr STATE

echo.
echo Integrated Energy Cooling Service status:
sc query IntegratedEnergyCoolingService | findstr STATE

echo.
echo Armor BIOS Optimization Service status:
sc query ArmorBiosOptimizationService | findstr STATE

echo.
echo Invisible BIOS Gateway Service status:
sc query InvisibleBiosGatewayService | findstr STATE

echo.
echo [VERIFY] Checking required files...
echo.

if exist "C:\QuantumEnergyService\bin\Release\QuantumEnergyService.exe" (
    echo [OK] QuantumEnergyService.exe found
) else (
    echo [ERROR] QuantumEnergyService.exe not found
)

if exist "C:\QuantumEnergyService\ENERGY_COOLING_SERVICE_README.md" (
    echo [OK] Energy Cooling Service documentation found
) else (
    echo [ERROR] Energy Cooling Service documentation not found
)

if exist "C:\QuantumEnergyService\SYSTEM_INTEGRATION_SUMMARY.md" (
    echo [OK] System integration summary found
) else (
    echo [ERROR] System integration summary not found
)

echo.
echo [COMPLETE] Verification complete!
echo.
echo For detailed service information, please check:
echo   - C:\QuantumEnergyService\ENERGY_COOLING_SERVICE_README.md
echo   - C:\QuantumEnergyService\SYSTEM_INTEGRATION_SUMMARY.md
echo   - Windows Event Viewer for service logs
echo.
pause