@echo off
REM AMD Quantum Rendering Background Service Uninstaller
REM Stops and removes the quantum rendering service

echo 🌟 AMD Quantum Rendering Background Service Uninstaller 🌟
echo ==========================================================
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

REM Stop the service
echo Stopping AMD Quantum Rendering Service...
net stop AMDQuantumRenderService
if %errorlevel% equ 0 (
    echo ✅ Service stopped successfully!
) else (
    echo ⚠️  Service was not running or could not be stopped
)

REM Uninstall the service
echo Uninstalling AMD Quantum Rendering Service...
QuantumRenderService.exe -uninstall
if %errorlevel% equ 0 (
    echo ✅ Service uninstalled successfully!
) else (
    echo ❌ Failed to uninstall service
    pause
    exit /b 1
)

echo.
echo 🎉 AMD Quantum Rendering Background Service has been removed!
echo.
echo To reinstall the service, run install_background_service.bat
echo.
pause