@echo off
REM Enhanced Live Spectrum Viewer Launch Script (Windows)

REM Change to the directory of this script
cd /d "%~dp0"

echo.
echo ========================================
echo   Enhanced RF Spectrum Analyzer
echo ========================================
echo.

REM Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ Python not found. Please install Python 3.9+ and add to PATH
  pause
  exit /b 1
)

echo Using Python:
python --version

REM Try to use pythonw for a windowed app (no console)
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
  set LAUNCHER=pythonw
) else (
  set LAUNCHER=python
)

echo.
echo 🚀 Launching Enhanced Viewer...
%LAUNCHER% enhanced_live_viewer.py

echo.
echo ✅ Enhanced Viewer closed
pause
