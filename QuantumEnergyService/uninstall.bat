@echo off
set SERVICE_NAME=QuantumEnergyService

echo Uninstalling Quantum Energy Service...

REM Check if service exists
sc query %SERVICE_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo Service %SERVICE_NAME% is not installed.
    pause
    exit /b 1
)

REM Stop the service
echo Stopping service...
sc stop %SERVICE_NAME%

timeout /t 3 /nobreak >nul

REM Delete the service
echo Deleting service...
sc delete %SERVICE_NAME%

if %errorlevel% neq 0 (
    echo Error uninstalling service.
    pause
    exit /b 1
)

echo Service uninstalled successfully!

pause