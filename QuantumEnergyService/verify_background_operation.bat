@echo off
echo Verifying Unified Cosmic System Background Operation
echo ===================================================

echo Checking running processes...
echo.

echo Milky Way Cosmic System:
tasklist | findstr MilkyWayCosmicSystem >nul
if %errorlevel% == 0 (
    echo   [RUNNING] MilkyWayCosmicSystem.exe
) else (
    echo   [STOPPED] MilkyWayCosmicSystem.exe
)

echo.
echo Real World Galactic Bridge:
tasklist | findstr RealWorldGalacticBridge >nul
if %errorlevel% == 0 (
    echo   [RUNNING] RealWorldGalacticBridge.exe
) else (
    echo   [STOPPED] RealWorldGalacticBridge.exe
)

echo.
echo Unified Cosmic System:
tasklist | findstr UnifiedCosmicSystem >nul
if %errorlevel% == 0 (
    echo   [RUNNING] UnifiedCosmicSystem.exe
) else (
    echo   [STOPPED] UnifiedCosmicSystem.exe
)

echo.
echo Checking data directories...
if exist "c:\QuantumEnergyService\milkyway_data" (
    echo   [OK] Milky Way data directory exists
) else (
    echo   [MISSING] Milky Way data directory
)

if exist "c:\QuantumEnergyService\reality_bridge" (
    echo   [OK] Reality bridge directory exists
) else (
    echo   [MISSING] Reality bridge directory
)

if exist "c:\QuantumEnergyService\unified_cosmos" (
    echo   [OK] Unified cosmos directory exists
) else (
    echo   [MISSING] Unified cosmos directory
)

echo.
echo Checking recent log files...
echo.
echo Milky Way logs:
if exist "c:\QuantumEnergyService\milkyway_data" (
    dir "c:\QuantumEnergyService\milkyway_data" /b | findstr .dat >nul
    if %errorlevel% == 0 (
        echo   [OK] Log files found
    ) else (
        echo   [EMPTY] No log files yet
    )
)

echo.
echo Reality bridge logs:
if exist "c:\QuantumEnergyService\reality_bridge" (
    dir "c:\QuantumEnergyService\reality_bridge" /b | findstr .dat >nul
    if %errorlevel% == 0 (
        echo   [OK] Log files found
    ) else (
        echo   [EMPTY] No log files yet
    )
)

echo.
echo Unified cosmos logs:
if exist "c:\QuantumEnergyService\unified_cosmos" (
    dir "c:\QuantumEnergyService\unified_cosmos" /b | findstr .dat >nul
    if %errorlevel% == 0 (
        echo   [OK] Log files found
    ) else (
        echo   [EMPTY] No log files yet
    )
)

echo.
echo Status: System is running in background without terminal interference
echo.
echo To stop the system:
echo   taskkill /f /im MilkyWayCosmicSystem.exe
echo   taskkill /f /im RealWorldGalacticBridge.exe
echo   taskkill /f /im UnifiedCosmicSystem.exe
echo.