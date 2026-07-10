@echo off
echo Real World to Galactic Bridge Status
echo =================================

echo Checking if bridge is running...
tasklist | findstr RealWorldGalacticBridge >nul
if %errorlevel% == 0 (
    echo [RUNNING] Real World to Galactic Bridge is active
) else (
    echo [STOPPED] Real World to Galactic Bridge is not running
)

echo.
echo Checking bridge directory...
if exist "c:\QuantumEnergyService\reality_bridge" (
    echo [OK] Bridge directory exists
    echo.
    echo Recent sync files:
    dir "c:\QuantumEnergyService\reality_bridge" /b | findstr .dat
) else (
    echo [MISSING] Bridge directory not found
)

echo.
echo To start bridge: c:\QuantumEnergyService\run_reality_bridge.bat
echo To stop bridge: taskkill /f /im RealWorldGalacticBridge.exe