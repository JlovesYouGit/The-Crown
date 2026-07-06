# Simple Live Spectrum Viewer Launcher (PowerShell)
# Stable version without complex 3D plotting

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Simple Live Spectrum Viewer" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting stable WiFi spectrum viewer..." -ForegroundColor Green
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
    Write-Host "Using system Python..." -ForegroundColor Yellow
}

# Launch the application
Write-Host ""
Write-Host "🌊 Launching Simple Live Spectrum Viewer..." -ForegroundColor Cyan
Write-Host ""
Write-Host "🎮 Features:" -ForegroundColor White
Write-Host "  • Real-time WiFi network detection" -ForegroundColor Gray
Write-Host "  • Live spectrum visualization" -ForegroundColor Gray
Write-Host "  • Network details and analysis" -ForegroundColor Gray
Write-Host "  • Stable, lightweight interface" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Usage:" -ForegroundColor White
Write-Host "  • Networks appear automatically in the list" -ForegroundColor Gray
Write-Host "  • Click on any network to see detailed information" -ForegroundColor Gray
Write-Host "  • Spectrum bars show signal strength visually" -ForegroundColor Gray
Write-Host "  • Red = 2.4GHz, Blue = 5GHz networks" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C or close window to exit" -ForegroundColor Yellow
Write-Host ""

try {
    python simple_live_viewer.py
    Write-Host ""
    Write-Host "✅ Simple Spectrum Viewer closed normally" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ Application encountered an error" -ForegroundColor Red
    Write-Host "This might be due to missing tkinter or permissions" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"