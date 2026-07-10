@echo off
echo Cosmic Qubit Service Status Checker
echo ==================================

echo Checking if service is running...
tasklist | findstr CosmicQubitSimple >nul
if %errorlevel% == 0 (
    echo [RUNNING] Cosmic Qubit Service is active
) else (
    echo [STOPPED] Cosmic Qubit Service is not running
)

echo.
echo Checking data file...
if exist "c:\QuantumEnergyService\qubit_data.txt" (
    echo [OK] Data file exists
    echo.
    echo Last data update:
    type "c:\QuantumEnergyService\qubit_data.txt" | findstr "Last Updated"
) else (
    echo [MISSING] Data file not found
)

echo.
echo To start service: schtasks /run /tn "CosmicQubitService"
echo To stop service: taskkill /f /im CosmicQubitSimple.exe