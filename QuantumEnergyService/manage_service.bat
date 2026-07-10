@echo off
echo Cosmic Qubit Service Manager
echo ==========================

if "%1" == "" goto help
if "%1" == "start" goto start
if "%1" == "stop" goto stop
if "%1" == "status" goto status
if "%1" == "install" goto install
if "%1" == "uninstall" goto uninstall
goto help

:start
echo Starting Cosmic Qubit Service...
c:\QuantumEnergyService\CosmicQubitSimple.exe
goto end

:stop
echo Stopping Cosmic Qubit Service...
taskkill /f /im CosmicQubitSimple.exe
goto end

:status
echo Checking service status...
tasklist | findstr CosmicQubitSimple.exe
if %errorlevel% == 0 (
    echo Service is running
) else (
    echo Service is not running
)
goto end

:install
echo Installing service...
copy c:\QuantumEnergyService\CosmicQubitSimple.exe "C:\Program Files\"
echo Service installed to "C:\Program Files\CosmicQubitSimple.exe"
goto end

:uninstall
echo Uninstalling service...
del "C:\Program Files\CosmicQubitSimple.exe"
echo Service uninstalled
goto end

:help
echo Usage: manage_service.bat [start^|stop^|status^|install^|uninstall]
echo.
echo start     - Start the cosmic qubit service
echo stop      - Stop the cosmic qubit service
echo status    - Check if service is running
echo install   - Install service to Program Files
echo uninstall - Remove service from Program Files

:end
echo.
echo Operation completed.