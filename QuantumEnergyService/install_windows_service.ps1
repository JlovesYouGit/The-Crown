# Install and start Cosmic Qubit Windows Service
Write-Host "Installing Cosmic Qubit Windows Service..."

try {
    # Stop service if it's already running
    $service = Get-Service -Name "CosmicQubitWindowsService" -ErrorAction SilentlyContinue
    if ($service -ne $null) {
        Write-Host "Stopping existing service..."
        Stop-Service -Name "CosmicQubitWindowsService" -Force
        Start-Sleep -Seconds 2
    }
    
    # Install the service using InstallUtil
    Write-Host "Installing service..."
    & "C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe" "c:\QuantumEnergyService\CosmicQubitService.exe"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Service installed successfully"
        
        # Start the service
        Write-Host "Starting the service..."
        Start-Service -Name "CosmicQubitWindowsService"
        
        # Check if service is running
        $service = Get-Service -Name "CosmicQubitWindowsService"
        if ($service.Status -eq "Running") {
            Write-Host "Service is running successfully"
        } else {
            Write-Host "Service failed to start. Status: $($service.Status)"
        }
    } else {
        Write-Host "Service installation failed with exit code: $LASTEXITCODE"
    }
} catch {
    Write-Host "Error: $_"
}

Write-Host "Installation process completed"