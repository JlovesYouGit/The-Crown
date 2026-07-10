# Quantum Energy Service Registry Cleanup Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   CLEANUP QUANTUM ENERGY SERVICE REGISTRY" -ForegroundColor Cyan
Write-Host "   Windows Registry Cleanup" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[CLEANUP] Running as Administrator - proceeding with registry cleanup" -ForegroundColor Green
Start-Sleep -Seconds 1

# Define registry paths
$basePath = "HKLM:\SOFTWARE\QuantumEnergyService"
$coolingPath = "$basePath\EnergyCooling"
$hardwarePath = "$basePath\HardwareCommunication"

Write-Host "[CLEANUP] Removing registry keys..." -ForegroundColor Green

# Remove hardware communication registry key
if (Test-Path $hardwarePath) {
    Remove-Item -Path $hardwarePath -Recurse -Force
    Write-Host "[CLEANUP] Removed hardware communication registry key: $hardwarePath" -ForegroundColor Green
}

# Remove energy cooling registry key
if (Test-Path $coolingPath) {
    Remove-Item -Path $coolingPath -Recurse -Force
    Write-Host "[CLEANUP] Removed energy cooling registry key: $coolingPath" -ForegroundColor Green
}

# Remove base registry key if empty
if (Test-Path $basePath) {
    $items = Get-ChildItem -Path $basePath -Recurse
    if ($items.Count -eq 0) {
        Remove-Item -Path $basePath -Force
        Write-Host "[CLEANUP] Removed base registry key: $basePath" -ForegroundColor Green
    } else {
        Write-Host "[CLEANUP] Base registry key still has items, not removing: $basePath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[CLEANUP] Resetting performance registry tweaks..." -ForegroundColor Green

# Reset power throttling setting
$powerThrottlingPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling"
if (Test-Path $powerThrottlingPath) {
    Set-ItemProperty -Path $powerThrottlingPath -Name "PowerThrottlingOff" -Value 0 -Type DWord
    Write-Host "[CLEANUP] Reset power throttling setting" -ForegroundColor Green
}

Write-Host ""
Write-Host "[COMPLETE] Registry cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Registry keys removed:" -ForegroundColor Cyan
Write-Host "  $coolingPath" -ForegroundColor Cyan
Write-Host "  $hardwarePath" -ForegroundColor Cyan
Write-Host "  $basePath (if empty)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Performance settings reset to defaults." -ForegroundColor Cyan
Write-Host ""

Pause