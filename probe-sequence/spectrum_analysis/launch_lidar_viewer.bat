@echo off
echo.
echo ========================================
echo   LIDAR-Style Spectrum Viewer Launcher
echo ========================================
echo.
echo Starting 3D RF Environment Mapping...
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
    echo Warning: Virtual environment not found, using system Python
)

REM Install required packages if needed
echo Checking dependencies...
python -c "import tkinter, matplotlib, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install matplotlib numpy
)

REM Launch the LIDAR viewer
echo.
echo 🌊 Launching LIDAR-Style Spectrum Viewer...
echo.
echo Controls:
echo - Click "Start LIDAR Scan" to begin real-time scanning
echo - Use mouse to rotate 3D view
echo - "Clear Point Cloud" to reset the visualization
echo - "Save Scan" to export data
echo.
echo Press Ctrl+C or close window to exit
echo.

python lidar_spectrum_viewer.py

if errorlevel 1 (
    echo.
    echo ❌ Application encountered an error
    echo Check the console output above for details
    pause
)

echo.
echo LIDAR Spectrum Viewer closed
pause