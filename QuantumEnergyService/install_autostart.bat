@echo off
echo Installing Cosmic Qubit Service Autostart
echo ========================================

echo Adding service to Windows startup...

REM Copy the service executable to a permanent location
copy "c:\QuantumEnergyService\CosmicQubitSimple.exe" "C:\Program Files\"

REM Create a scheduled task to run at startup
schtasks /create /tn "CosmicQubitService" /tr "C:\Program Files\CosmicQubitSimple.exe" /sc onstart /ru SYSTEM /f

if %errorlevel% == 0 (
    echo Service installed successfully!
    echo The Cosmic Qubit Service will now start automatically at system boot
) else (
    echo Failed to install service as scheduled task
    echo Error code: %errorlevel%
)

echo.
echo To manually start the service: schtasks /run /tn "CosmicQubitService"
echo To stop the service: taskkill /f /im CosmicQubitSimple.exe
echo To remove the service: schtasks /delete /tn "CosmicQubitService" /f
echo.
pause