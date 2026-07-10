# Quantum Energy Service Registry Configuration Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   CONFIGURE QUANTUM ENERGY SERVICE REGISTRY" -ForegroundColor Cyan
Write-Host "   Windows Registry Configuration" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[CONFIG] Running as Administrator - proceeding with registry configuration" -ForegroundColor Green
Start-Sleep -Seconds 1

# Define registry paths
$basePath = "HKLM:\SOFTWARE\QuantumEnergyService"
$coolingPath = "$basePath\EnergyCooling"
$hardwarePath = "$basePath\HardwareCommunication"

Write-Host "[CONFIG] Creating registry keys..." -ForegroundColor Green

# Create base registry key
if (!(Test-Path $basePath)) {
    New-Item -Path $basePath -Force | Out-Null
    Write-Host "[CONFIG] Created base registry key: $basePath" -ForegroundColor Green
}

# Create energy cooling registry key
if (!(Test-Path $coolingPath)) {
    New-Item -Path $coolingPath -Force | Out-Null
    Write-Host "[CONFIG] Created energy cooling registry key: $coolingPath" -ForegroundColor Green
}

# Create hardware communication registry key
if (!(Test-Path $hardwarePath)) {
    New-Item -Path $hardwarePath -Force | Out-Null
    Write-Host "[CONFIG] Created hardware communication registry key: $hardwarePath" -ForegroundColor Green
}

Write-Host ""
Write-Host "[CONFIG] Setting registry values..." -ForegroundColor Green

# Set energy cooling configuration values
Set-ItemProperty -Path $coolingPath -Name "PositiveEnergyLevel" -Value "0.0" -Type String
Set-ItemProperty -Path $coolingPath -Name "NegativeEnergyLevel" -Value "0.0" -Type String
Set-ItemProperty -Path $coolingPath -Name "SeparationDistance" -Value "0.5" -Type String
Set-ItemProperty -Path $coolingPath -Name "YinYangBalance" -Value "0.5" -Type String
Set-ItemProperty -Path $coolingPath -Name "GhostParticleDensity" -Value "0.0" -Type String
Set-ItemProperty -Path $coolingPath -Name "ReactionRate" -Value "0" -Type String
Set-ItemProperty -Path $coolingPath -Name "SystemActive" -Value "false" -Type String

Write-Host "[CONFIG] Set energy cooling configuration values" -ForegroundColor Green

# Set hardware communication configuration values
Set-ItemProperty -Path $hardwarePath -Name "CPUMonitoringEnabled" -Value "true" -Type String
Set-ItemProperty -Path $hardwarePath -Name "GPUMonitoringEnabled" -Value "true" -Type String
Set-ItemProperty -Path $hardwarePath -Name "MemoryMonitoringEnabled" -Value "true" -Type String
Set-ItemProperty -Path $hardwarePath -Name "DiskMonitoringEnabled" -Value "true" -Type String
Set-ItemProperty -Path $hardwarePath -Name "PowerManagementEnabled" -Value "true" -Type String
Set-ItemProperty -Path $hardwarePath -Name "HardwareOptimizationLevel" -Value "High" -Type String

Write-Host "[CONFIG] Set hardware communication configuration values" -ForegroundColor Green

# Set service configuration values
Set-ItemProperty -Path $basePath -Name "ServiceVersion" -Value "1.0.0" -Type String
Set-ItemProperty -Path $basePath -Name "InstallationDate" -Value $(Get-Date -Format "yyyy-MM-dd") -Type String
Set-ItemProperty -Path $basePath -Name "LogLevel" -Value "Info" -Type String
Set-ItemProperty -Path $basePath -Name "LogFilePath" -Value "C:\QuantumEnergyService\quantum_energy_service.log" -Type String

Write-Host "[CONFIG] Set service configuration values" -ForegroundColor Green

Write-Host ""
Write-Host "[CONFIG] Setting performance registry tweaks..." -ForegroundColor Green

# Configure system performance for energy service
# Disable power throttling for better performance
$powerThrottlingPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling"
if (Test-Path $powerThrottlingPath) {
    Set-ItemProperty -Path $powerThrottlingPath -Name "PowerThrottlingOff" -Value 1 -Type DWord
    Write-Host "[CONFIG] Disabled power throttling" -ForegroundColor Green
}

# Configure power plan settings for high performance
powercfg /SETACTIVE 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[CONFIG] Set power plan to high performance" -ForegroundColor Green
}

Write-Host ""
Write-Host "[CONFIG] Setting hardware acceleration registry entries..." -ForegroundColor Green

# Configure hardware acceleration settings
$graphicsDriversPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
if (Test-Path $graphicsDriversPath) {
    Set-ItemProperty -Path $graphicsDriversPath -Name "HwSchMode" -Value 2 -Type DWord
    Write-Host "[CONFIG] Enabled hardware scheduled GPU processing" -ForegroundColor Green
}

# Configure CPU performance settings
$cpuPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-33abaf5935ec"
if (Test-Path $cpuPath) {
    Set-ItemProperty -Path $cpuPath -Name "Attributes" -Value 2 -Type DWord
    Write-Host "[CONFIG] Configured CPU performance settings" -ForegroundColor Green
}

Write-Host ""
Write-Host "[COMPLETE] Registry configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Registry keys created:" -ForegroundColor Cyan
Write-Host "  $basePath" -ForegroundColor Cyan
Write-Host "  $coolingPath" -ForegroundColor Cyan
Write-Host "  $hardwarePath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration values set for optimal energy service performance." -ForegroundColor Cyan
Write-Host ""

Pause