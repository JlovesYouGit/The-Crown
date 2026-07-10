# Quantum Energy Service Installation Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator" -ForegroundColor Red
    exit 1
}

# Define service parameters
$serviceName = "QuantumEnergyService"
$serviceDisplayName = "Quantum Energy Management Service"
$serviceDescription = "Manages CPU/GPU energy consumption using quantized wave transmission states (QWTS)"
$executablePath = "$PSScriptRoot\bin\Release\net8.0-windows\QuantumEnergyService.exe"

# Check if executable exists
if (-not (Test-Path $executablePath)) {
    Write-Host "Error: Service executable not found at $executablePath" -ForegroundColor Red
    Write-Host "Please build the project first using: dotnet build --configuration Release" -ForegroundColor Yellow
    exit 1
}

# Stop and remove existing service if it exists
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Stopping existing service..." -ForegroundColor Yellow
    Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
    
    Write-Host "Removing existing service..." -ForegroundColor Yellow
    $serviceToRemove = Get-WmiObject -Class Win32_Service -Filter "Name='$serviceName'"
    if ($serviceToRemove) {
        $serviceToRemove.Delete()
    }
    
    Start-Sleep -Seconds 3
}

# Create the new service
Write-Host "Creating new service..." -ForegroundColor Green
New-Service -Name $serviceName -BinaryPathName $executablePath -DisplayName $serviceDisplayName -StartupType Automatic -Description $serviceDescription

# Set service to restart on failure
sc.exe failure $serviceName reset= 86400 actions= restart/5000/restart/10000/restart/30000 | Out-Null

# Start the service
Write-Host "Starting service..." -ForegroundColor Green
Start-Service -Name $serviceName

Write-Host "Service installation completed successfully!" -ForegroundColor Green
Write-Host "Service Name: $serviceName" -ForegroundColor Cyan
Write-Host "Display Name: $serviceDisplayName" -ForegroundColor Cyan