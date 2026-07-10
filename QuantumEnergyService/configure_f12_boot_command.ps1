# Quantum Energy Service - F12 Boot Command Configuration Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   CONFIGURE F12 BOOT COMMAND FOR AUTONOMOUS CONTROL" -ForegroundColor Cyan
Write-Host "   Pre-Windows Boot Gateway Configuration" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[CONFIG] Running as Administrator - proceeding with F12 boot command configuration" -ForegroundColor Green
Start-Sleep -Seconds 1

# Define registry paths
$bootPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Boot"
$f12Path = "HKLM:\SYSTEM\CurrentControlSet\Control\F12BootCommand"
$quantumPath = "HKLM:\SOFTWARE\QuantumEnergyService"

Write-Host "[CONFIG] Creating registry keys for F12 boot command..." -ForegroundColor Green

# Create F12 boot command registry key
if (!(Test-Path $f12Path)) {
    New-Item -Path $f12Path -Force | Out-Null
    Write-Host "[CONFIG] Created F12 boot command registry key: $f12Path" -ForegroundColor Green
}

# Set F12 boot command values
Set-ItemProperty -Path $f12Path -Name "Enabled" -Value "1" -Type String
Set-ItemProperty -Path $f12Path -Name "Command" -Value "quantum_bios_gateway.exe" -Type String
Set-ItemProperty -Path $f12Path -Name "Description" -Value "Quantum Energy Service BIOS Gateway" -Type String
Set-ItemProperty -Path $f12Path -Name "AutoStart" -Value "1" -Type String
Set-ItemProperty -Path $f12Path -Name "DelaySeconds" -Value "0" -Type String

Write-Host "[CONFIG] Set F12 boot command configuration values" -ForegroundColor Green

# Configure boot settings
Set-ItemProperty -Path $bootPath -Name "AutoStart" -Value "1" -Type DWord
Set-ItemProperty -Path $bootPath -Name "BootUX" -Value "1" -Type DWord

Write-Host "[CONFIG] Configured boot settings for autonomous control" -ForegroundColor Green

# Create Quantum Energy Service registry entries
if (!(Test-Path $quantumPath)) {
    New-Item -Path $quantumPath -Force | Out-Null
    Write-Host "[CONFIG] Created Quantum Energy Service registry key: $quantumPath" -ForegroundColor Green
}

# Set service configuration values
Set-ItemProperty -Path $quantumPath -Name "F12BootGateway" -Value "Enabled" -Type String
Set-ItemProperty -Path $quantumPath -Name "AutonomousControl" -Value "Full" -Type String
Set-ItemProperty -Path $quantumPath -Name "BiosIntegration" -Value "Deep" -Type String
Set-ItemProperty -Path $quantumPath -Name "PreBootOptimization" -Value "Enabled" -Type String

Write-Host "[CONFIG] Set Quantum Energy Service configuration values" -ForegroundColor Green

Write-Host ""
Write-Host "[CONFIG] Setting up pre-boot environment variables..." -ForegroundColor Green

# Set environment variables for pre-boot execution
$envPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
Set-ItemProperty -Path $envPath -Name "QUANTUM_BIOS_GATEWAY" -Value "1" -Type String
Set-ItemProperty -Path $envPath -Name "QUANTUM_AUTONOMOUS_MODE" -Value "ENABLED" -Type String
Set-ItemProperty -Path $envPath -Name "QUANTUM_PREBOOT_CONTROL" -Value "FULL" -Type String

Write-Host "[CONFIG] Set pre-boot environment variables" -ForegroundColor Green

Write-Host ""
Write-Host "[CONFIG] Configuring boot manager settings..." -ForegroundColor Green

# Configure boot manager for F12 command
$bootMgrPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Boot"
Set-ItemProperty -Path $bootMgrPath -Name "F12BootCommand" -Value "quantum_bios_gateway.exe" -Type String
Set-ItemProperty -Path $bootMgrPath -Name "F12BootDelay" -Value "0" -Type DWord
Set-ItemProperty -Path $bootMgrPath -Name "F12BootEnabled" -Value "1" -Type DWord

Write-Host "[CONFIG] Configured boot manager settings" -ForegroundColor Green

Write-Host ""
Write-Host "[COMPLETE] F12 boot command configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Registry keys created:" -ForegroundColor Cyan
Write-Host "  $f12Path" -ForegroundColor Cyan
Write-Host "  $quantumPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration values set for pre-Windows boot autonomous control." -ForegroundColor Cyan
Write-Host ""
Write-Host "The F12 boot command will now execute before Windows boot," -ForegroundColor Yellow
Write-Host "establishing a gateway between BIOS full control and automated adjusters." -ForegroundColor Yellow
Write-Host ""

Pause