@echo off
set SERVICE_NAME=QuantumEnergyService
set SERVICE_DISPLAY_NAME=Quantum Energy Management Service
set SERVICE_DESCRIPTION=Manages CPU/GPU energy consumption using quantized wave transmission states (QWTS)
set EXECUTABLE_PATH=%~dp0bin\Release\net8.0\QuantumEnergyService.exe

echo Installing Quantum Energy Service...

REM Check if service already exists
sc query %SERVICE_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    echo Stopping existing service...
    sc stop %SERVICE_NAME%
    
    echo Uninstalling existing service...
    sc delete %SERVICE_NAME%
    
    timeout /t 5 /nobreak >nul
)

REM Check if executable exists
if not exist "%EXECUTABLE_PATH%" (
    echo Error: Service executable not found at %EXECUTABLE_PATH%
    echo Please build the project first using build.bat
    pause
    exit /b 1
)

REM Install the service
echo Installing new service...
sc create %SERVICE_NAME% binPath="%EXECUTABLE_PATH%" DisplayName="%SERVICE_DISPLAY_NAME%" start=auto
sc description %SERVICE_NAME% "%SERVICE_DESCRIPTION%"

if %errorlevel% neq 0 (
    echo Error installing service.
    pause
    exit /b 1
)

REM Set service to restart on failure
sc failure %SERVICE_NAME% reset=86400 actions=restart/5000/restart/10000/restart/30000

echo Starting service...
sc start %SERVICE_NAME%

if %errorlevel% neq 0 (
    echo Warning: Could not start service automatically. Please start it manually from Services.msc
)

echo Service installation completed!
echo Service Name: %SERVICE_NAME%
echo Display Name: %SERVICE_DISPLAY_NAME%

pause