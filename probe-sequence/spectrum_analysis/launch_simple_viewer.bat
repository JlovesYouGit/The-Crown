@echo off
echo.
echo ========================================
echo   Simple Live Spectrum Viewer
echo ========================================
echo.
echo Starting stable WiFi spectrum viewer...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "..\\.venv\\Scripts\\activate.bat" (
    echo Activating virtual environment...
    call "..\\.venv\\Scripts\\activate.bat"
) else (
    echo Using system Python...
)

REM Launch the simple viewer
echo.
echo 🌊 Launching Simple Live Spectrum Viewer...
echo.
echo Features:
echo - Real-time WiFi network detection
echo - Live spectrum visualization
echo - Network details and analysis
echo - Stable, lightweight interface
echo.
echo Click on networks in the list to see details!
echo Press Ctrl+C or close window to exit
echo.

python simple_live_viewer.py

if errorlevel 1 (
    echo.
    echo ❌ Application encountered an error
    echo This might be due to missing tkinter or permissions
    pause
)

echo.
echo Simple Spectrum Viewer closed
pause