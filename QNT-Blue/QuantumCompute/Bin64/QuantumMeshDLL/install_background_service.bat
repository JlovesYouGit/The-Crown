@echo off
REM AMD Quantum Rendering Background Service Installer
REM Automatically installs and starts the quantum rendering service

echo 🌟 AMD Quantum Rendering Background Service Installer 🌟
echo ========================================================
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

REM Check if required files exist
echo Checking required files...
if not exist "QuantumRenderService.exe" (
    echo ❌ QuantumRenderService.exe not found!
    echo    Please build the service first.
    echo.
    pause
    exit /b 1
)

if not exist "..\Models\quantum_render_optimization.gguf" (
    echo ❌ quantum_render_optimization.gguf not found!
    echo    Please download the model first.
    echo.
    pause
    exit /b 1
)

echo ✅ All required files found!
echo.

REM Stop service if it's already running
echo Stopping existing service (if any)...
net stop AMDQuantumRenderService >nul 2>&1

REM Uninstall existing service
echo Uninstalling existing service (if any)...
QuantumRenderService.exe -uninstall >nul 2>&1

REM Install the service
echo Installing AMD Quantum Rendering Service...
QuantumRenderService.exe -install
if %errorlevel% equ 0 (
    echo ✅ Service installed successfully!
) else (
    echo ❌ Failed to install service
    pause
    exit /b 1
)

REM Start the service
echo Starting AMD Quantum Rendering Service...
net start AMDQuantumRenderService
if %errorlevel% equ 0 (
    echo ✅ Service started successfully!
) else (
    echo ❌ Failed to start service
    pause
    exit /b 1
)

REM Check service status
echo.
echo Service Status:
sc query AMDQuantumRenderService

echo.
echo 🎉 AMD Quantum Rendering Background Service is now running!
echo.
echo The service will automatically:
echo   • Run quantum mesh rendering optimizations
echo   • Process frames with lightweight AI models
echo   • Interpolate to 60fps output
echo   • Manage Q-bit compressed memory
echo   • Run continuously in the background
echo.
echo To manage the service:
echo   • service_manager.bat -install    : Install the service
echo   • service_manager.bat -uninstall  : Uninstall the service
echo   • service_manager.bat -start      : Start the service
echo   • service_manager.bat -stop       : Stop the service
echo   • service_manager.bat -status     : Check service status
echo.
echo The service will automatically start when Windows boots.
echo.
pause