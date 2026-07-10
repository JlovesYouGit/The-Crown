@echo off
:: Background Runner for Unified Cosmic System
:: This script runs the system in the background without console window

echo Starting Unified Cosmic System in background mode...
echo =================================================

:: Hide the window by calling PowerShell with WindowStyle Hidden
powershell -WindowStyle Hidden -Command "Start-Process 'c:\QuantumEnergyService\UnifiedCosmicSystem.exe' -WindowStyle Hidden"

:: Also start the other components
powershell -WindowStyle Hidden -Command "Start-Process 'c:\QuantumEnergyService\MilkyWayCosmicSystem.exe' -WindowStyle Hidden"
powershell -WindowStyle Hidden -Command "Start-Process 'c:\QuantumEnergyService\RealWorldGalacticBridge.exe' -WindowStyle Hidden"

echo System components started in background.
echo All processes are now running without terminal interference.
echo.
echo Log files are being written to:
echo   c:\QuantumEnergyService\milkyway_data\
echo   c:\QuantumEnergyService\reality_bridge\
echo   c:\QuantumEnergyService\unified_cosmos\
echo.
echo To stop the system, use Task Manager to end the processes:
echo   UnifiedCosmicSystem.exe
echo   MilkyWayCosmicSystem.exe
echo   RealWorldGalacticBridge.exe