# Quantum Energy Service Uninstallation Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator" -ForegroundColor Red
    exit 1
}

# Define service parameters
$serviceName = "QuantumEnergyService"

# Check if service exists
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if (-not $service) {
    Write-Host "Service $serviceName is not installed." -ForegroundColor Yellow
    exit 1
}

# Stop the service
Write-Host "Stopping service..." -ForegroundColor Yellow
Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue

# Wait a moment for the service to stop
Start-Sleep -Seconds 2

# Remove the service
Write-Host "Removing service..." -ForegroundColor Yellow
$serviceToRemove = Get-WmiObject -Class Win32_Service -Filter "Name='$serviceName'"
if ($serviceToRemove) {
    $result = $serviceToRemove.Delete()
    if ($result.ReturnValue -eq 0) {
        Write-Host "Service removed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error removing service. Return code: $($result.ReturnValue)" -ForegroundColor Red
    }
} else {
    Write-Host "Service not found in WMI." -ForegroundColor Yellow
}

Write-Host "Service uninstallation completed!" -ForegroundColor Green