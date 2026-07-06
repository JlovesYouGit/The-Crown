# Enhanced Live Spectrum Viewer Launcher (PowerShell)
# Stable Windows-style launcher mirroring the simple viewer setup

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Enhanced RF Spectrum Analyzer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting enhanced spectrum viewer..." -ForegroundColor Green
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
Write-Host "🌊 Launching Enhanced Live Spectrum Viewer..." -ForegroundColor Cyan
Write-Host "" 
Write-Host "🎮 Features:" -ForegroundColor White
Write-Host "  • Advanced WiFi analysis (interference, security, history)" -ForegroundColor Gray
Write-Host "  • Multiple visualization modes" -ForegroundColor Gray
Write-Host "  • Export/Import of scan data" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C or close window to exit" -ForegroundColor Yellow
Write-Host ""

try {
    python enhanced_live_viewer.py
    Write-Host ""
    Write-Host "✅ Enhanced Spectrum Viewer closed normally" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ Application encountered an error" -ForegroundColor Red
    Write-Host "This might be due to missing tkinter or permissions" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
