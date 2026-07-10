# Quantum Energy Service - F12 Boot Command Cleanup Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   CLEANUP F12 BOOT COMMAND CONFIGURATION" -ForegroundColor Cyan
Write-Host "   Pre-Windows Boot Gateway Removal" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[CLEANUP] Running as Administrator - proceeding with F12 boot command cleanup" -ForegroundColor Green
Start-Sleep -Seconds 1

# Define registry paths
$f12Path = "HKLM:\SYSTEM\CurrentControlSet\Control\F12BootCommand"
$quantumPath = "HKLM:\SOFTWARE\QuantumEnergyService"

Write-Host "[CLEANUP] Removing F12 boot command registry keys..." -ForegroundColor Green

# Remove F12 boot command registry key
if (Test-Path $f12Path) {
    Remove-Item -Path $f12Path -Recurse -Force
    Write-Host "[CLEANUP] Removed F12 boot command registry key: $f12Path" -ForegroundColor Green
}

Write-Host ""
Write-Host "[CLEANUP] Resetting boot manager settings..." -ForegroundColor Green

# Reset boot manager settings
$bootMgrPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Boot"
if (Test-Path $bootMgrPath) {
    Remove-ItemProperty -Path $bootMgrPath -Name "F12BootCommand" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $bootMgrPath -Name "F12BootDelay" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $bootMgrPath -Name "F12BootEnabled" -ErrorAction SilentlyContinue
    Write-Host "[CLEANUP] Reset boot manager settings" -ForegroundColor Green
}

Write-Host ""
Write-Host "[CLEANUP] Removing environment variables..." -ForegroundColor Green

# Remove environment variables
$envPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
Remove-ItemProperty -Path $envPath -Name "QUANTUM_BIOS_GATEWAY" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $envPath -Name "QUANTUM_AUTONOMOUS_MODE" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $envPath -Name "QUANTUM_PREBOOT_CONTROL" -ErrorAction SilentlyContinue

Write-Host "[CLEANUP] Removed pre-boot environment variables" -ForegroundColor Green

Write-Host ""
Write-Host "[CLEANUP] Cleaning Quantum Energy Service registry entries..." -ForegroundColor Green

# Remove Quantum Energy Service registry entries related to F12
if (Test-Path $quantumPath) {
    Remove-ItemProperty -Path $quantumPath -Name "F12BootGateway" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $quantumPath -Name "AutonomousControl" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $quantumPath -Name "BiosIntegration" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $quantumPath -Name "PreBootOptimization" -ErrorAction SilentlyContinue
    
    # Check if the key is empty and remove it if so
    $items = Get-ChildItem -Path $quantumPath -Recurse
    if ($items.Count -eq 0) {
        Remove-Item -Path $quantumPath -Force
        Write-Host "[CLEANUP] Removed Quantum Energy Service registry key: $quantumPath" -ForegroundColor Green
    } else {
        Write-Host "[CLEANUP] Cleaned Quantum Energy Service registry entries" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[COMPLETE] F12 boot command cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Registry keys and values removed:" -ForegroundColor Cyan
Write-Host "  $f12Path" -ForegroundColor Cyan
Write-Host "  Related environment variables" -ForegroundColor Cyan
Write-Host "  Quantum Energy Service F12 configuration" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pre-Windows boot autonomous control has been disabled." -ForegroundColor Yellow
Write-Host ""

Pause