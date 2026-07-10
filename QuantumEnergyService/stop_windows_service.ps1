# Stop Cosmic Qubit Windows Service
Write-Host "Stopping Cosmic Qubit Windows Service..."

try {
    # Stop the service
    Write-Host "Stopping service..."
    Stop-Service -Name "CosmicQubitWindowsService" -Force
    
    # Check if service is stopped
    $service = Get-Service -Name "CosmicQubitWindowsService"
    if ($service.Status -eq "Stopped") {
        Write-Host "Service stopped successfully"
    } else {
        Write-Host "Service failed to stop. Status: $($service.Status)"
    }
} catch {
    Write-Host "Error: $_"
}

Write-Host "Stop process completed"