# Integrated Energy Cooling Service Uninstallation Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   UNINSTALL INTEGRATED ENERGY COOLING SERVICE" -ForegroundColor Cyan
Write-Host "   Windows Service Removal" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[UNINSTALL] Running as Administrator - proceeding with uninstallation" -ForegroundColor Green
Start-Sleep -Seconds 1

# Stop the service if it's running
Write-Host "[STOP] Stopping Integrated Energy Cooling Service..." -ForegroundColor Green
try {
    Stop-Service -Name "IntegratedEnergyCoolingService" -Force -ErrorAction SilentlyContinue
    Write-Host "[STOP] Service stopped successfully" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Service was not running or not found" -ForegroundColor Yellow
}

Start-Sleep -Seconds 1

# Uninstall the service
Write-Host "[UNINSTALL] Removing Integrated Energy Cooling Service..." -ForegroundColor Green
try {
    # Use InstallUtil to uninstall the service
    $installUtilPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe"
    & $installUtilPath /u "C:\QuantumEnergyService\bin\Release\QuantumEnergyService.exe"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[UNINSTALL] Service uninstalled successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to uninstall service" -ForegroundColor Red
        Pause
        Exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to uninstall service: $_" -ForegroundColor Red
    Pause
    Exit 1
}

Write-Host ""
Write-Host "[COMPLETE] Integrated Energy Cooling Service uninstallation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "The service has been removed from your system." -ForegroundColor Cyan
Write-Host ""

Pause