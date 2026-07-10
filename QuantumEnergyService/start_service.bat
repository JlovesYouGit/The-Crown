@echo off
echo Starting Cosmic Qubit Service...
echo ==============================
echo This will start the service in the background

REM Start the service in the background
START /B c:\QuantumEnergyService\CosmicQubitSimple.exe

echo Service started successfully!
echo The service is now running in the background
echo.
echo To stop the service, run: taskkill /f /im CosmicQubitSimple.exe
echo To check if it's running: tasklist ^| findstr CosmicQubitSimple
echo.
echo Log files are located at: c:\QuantumEnergyService\