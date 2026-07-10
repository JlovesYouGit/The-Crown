# Install Cosmic Qubit Windows Service
Write-Host "Installing Cosmic Qubit Windows Service..."

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator"
    exit 1
}

try {
    # Install the service using InstallUtil
    & "C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe" "c:\QuantumEnergyService\CosmicQubitService.exe"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Service installed successfully"
        
        # Start the service
        Write-Host "Starting the service..."
        Start-Service CosmicQubitWindowsService
        Write-Host "Service started successfully"
    } else {
        Write-Host "Service installation failed with exit code: $LASTEXITCODE"
    }
} catch {
    Write-Host "Error installing service: $_"
}

Write-Host "Installation process completed"