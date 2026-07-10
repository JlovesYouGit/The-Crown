# Q Terminal Launcher Script
# This script launches the Q Terminal with proper permissions and environment

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "        Q TERMINAL LAUNCHER" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if QTerminal.exe exists
if (Test-Path "QTerminal.exe") {
    Write-Host "Found QTerminal.exe" -ForegroundColor Green
} else {
    Write-Host "Building QTerminal.exe..." -ForegroundColor Yellow
    
    # Try to build using .NET Framework compiler
    if (Test-Path "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe") {
        Write-Host "Using .NET Framework compiler..." -ForegroundColor Yellow
        & "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:QTerminal.exe QTerminal.cs
    } else {
        Write-Host "Please ensure .NET Framework is installed" -ForegroundColor Red
        pause
        exit
    }
    
    if (Test-Path "QTerminal.exe") {
        Write-Host "Build successful!" -ForegroundColor Green
    } else {
        Write-Host "Build failed!" -ForegroundColor Red
        pause
        exit
    }
}

Write-Host ""
Write-Host "Launching Q Terminal..." -ForegroundColor Cyan
Write-Host "Connecting to Unified Cosmic System..." -ForegroundColor Yellow
Write-Host "Establishing Reality Bridge..." -ForegroundColor Yellow
Write-Host "Linking to Milky Way Network..." -ForegroundColor Yellow
Write-Host ""

# Run the Q Terminal
& .\QTerminal.exe

Write-Host ""
Write-Host "Q Terminal session ended." -ForegroundColor Cyan
pause