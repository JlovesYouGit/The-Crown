@echo off
REM AMD Quantum Rendering Service Manager
REM Manages the background quantum rendering service

echo 🌟 AMD Quantum Rendering Service Manager 🌟
echo ==========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ❌ This script must be run as Administrator
    echo    Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Parse command line arguments
if "%1"=="" goto :show_help
if "%1"=="-install" goto :install_service
if "%1"=="-uninstall" goto :uninstall_service
if "%1"=="-start" goto :start_service
if "%1"=="-stop" goto :stop_service
if "%1"=="-status" goto :service_status
goto :show_help

:show_help
echo Usage: service_manager.bat [option]
echo.
echo Options:
echo   -install    Install and start the quantum rendering service
echo   -uninstall  Stop and uninstall the quantum rendering service
echo   -start      Start the quantum rendering service
echo   -stop       Stop the quantum rendering service
echo   -status     Check the status of the quantum rendering service
echo.
goto :end

:install_service
echo Installing AMD Quantum Rendering Service...
QuantumRenderService.exe -install
if %errorlevel% equ 0 (
    echo ✅ Service installed successfully!
) else (
    echo ❌ Failed to install service
)
goto :end

:uninstall_service
echo Uninstalling AMD Quantum Rendering Service...
QuantumRenderService.exe -uninstall
if %errorlevel% equ 0 (
    echo ✅ Service uninstalled successfully!
) else (
    echo ❌ Failed to uninstall service
)
goto :end

:start_service
echo Starting AMD Quantum Rendering Service...
net start AMDQuantumRenderService
if %errorlevel% equ 0 (
    echo ✅ Service started successfully!
) else (
    echo ❌ Failed to start service
)
goto :end

:stop_service
echo Stopping AMD Quantum Rendering Service...
net stop AMDQuantumRenderService
if %errorlevel% equ 0 (
    echo ✅ Service stopped successfully!
) else (
    echo ❌ Failed to stop service
)
goto :end

:service_status
echo Checking AMD Quantum Rendering Service status...
sc query AMDQuantumRenderService
goto :end

:end
echo.
echo Service management complete!
echo.
pause