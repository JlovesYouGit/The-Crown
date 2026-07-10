@echo off
echo Milky Way Cosmic System Status
echo =============================

echo Checking if system is running...
tasklist | findstr MilkyWayCosmicSystem >nul
if %errorlevel% == 0 (
    echo [RUNNING] Milky Way Cosmic System is active
) else (
    echo [STOPPED] Milky Way Cosmic System is not running
)

echo.
echo Checking data directory...
if exist "c:\QuantumEnergyService\milkyway_data" (
    echo [OK] Data directory exists
    echo.
    echo Data files:
    dir "c:\QuantumEnergyService\milkyway_data" /b
) else (
    echo [MISSING] Data directory not found
)

echo.
echo To start system: c:\QuantumEnergyService\run_milkyway_system.bat
echo To stop system: taskkill /f /im MilkyWayCosmicSystem.exe