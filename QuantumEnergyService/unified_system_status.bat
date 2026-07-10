@echo off
echo Unified Cosmic System Status
echo =========================

echo Checking system components...

echo.
echo [MILKY WAY COSMIC SYSTEM]
tasklist | findstr MilkyWayCosmicSystem >nul
if %errorlevel% == 0 (
    echo   Status: [RUNNING]
) else (
    echo   Status: [STOPPED]
)

echo.
echo [REALITY BRIDGE]
tasklist | findstr RealWorldGalacticBridge >nul
if %errorlevel% == 0 (
    echo   Status: [RUNNING]
) else (
    echo   Status: [STOPPED]
)

echo.
echo [UNIFIED SYSTEM]
tasklist | findstr UnifiedCosmicSystem >nul
if %errorlevel% == 0 (
    echo   Status: [RUNNING]
) else (
    echo   Status: [STOPPED]
)

echo.
echo Checking data directories...
if exist "c:\QuantumEnergyService\milkyway_data" (
    echo   Milky Way Data: [OK]
) else (
    echo   Milky Way Data: [MISSING]
)

if exist "c:\QuantumEnergyService\reality_bridge" (
    echo   Reality Bridge Data: [OK]
) else (
    echo   Reality Bridge Data: [MISSING]
)

if exist "c:\QuantumEnergyService\unified_cosmos" (
    echo   Unified Cosmos Data: [OK]
) else (
    echo   Unified Cosmos Data: [MISSING]
)

echo.
echo To start unified system: c:\QuantumEnergyService\run_unified_system.bat
echo To stop all systems:
echo   taskkill /f /im UnifiedCosmicSystem.exe
echo   taskkill /f /im MilkyWayCosmicSystem.exe
echo   taskkill /f /im RealWorldGalacticBridge.exe