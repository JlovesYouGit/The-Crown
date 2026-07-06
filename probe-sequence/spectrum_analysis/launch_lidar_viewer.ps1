# LIDAR-Style Spectrum Viewer Launcher (PowerShell)
# Run this script to start the 3D RF environment mapping tool

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LIDAR-Style Spectrum Viewer Launcher" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting 3D RF Environment Mapping..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for virtual environment
if (Test-Path "..\.venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    & "..\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  Warning: Virtual environment not found, using system Python" -ForegroundColor Yellow
}

# Check dependencies
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import tkinter, matplotlib, numpy" 2>$null
    Write-Host "✅ All dependencies available" -ForegroundColor Green
} catch {
    Write-Host "📥 Installing required packages..." -ForegroundColor Yellow
    pip install matplotlib numpy
}

# Launch the application
Write-Host ""
Write-Host "🌊 Launching LIDAR-Style Spectrum Viewer..." -ForegroundColor Cyan
Write-Host ""
Write-Host "🎮 Controls:" -ForegroundColor White
Write-Host "  • Click 'Start LIDAR Scan' to begin real-time scanning" -ForegroundColor Gray
Write-Host "  • Use mouse to rotate 3D view" -ForegroundColor Gray
Write-Host "  • 'Clear Point Cloud' to reset visualization" -ForegroundColor Gray
Write-Host "  • 'Save Scan' to export data" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C or close window to exit" -ForegroundColor Yellow
Write-Host ""

try {
    python lidar_spectrum_viewer.py
    Write-Host ""
    Write-Host "✅ LIDAR Spectrum Viewer closed normally" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ Application encountered an error" -ForegroundColor Red
    Write-Host "Check the console output above for details" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"