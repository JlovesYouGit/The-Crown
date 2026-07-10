# Quantum Energy Service Monitor

 param([int]$RefreshInterval = 5)

Write-Host "Quantum Energy Service Monitor" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "Refresh interval: $RefreshInterval seconds" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to exit" -ForegroundColor Gray
Write-Host ""

while ($true) {
    # Get service status
    $service = Get-Service -Name "QuantumEnergyService" -ErrorAction SilentlyContinue
    if ($service) {
        $statusColor = if ($service.Status -eq "Running") { "Green" } else { "Red" }
        Write-Host "Service Status: $($service.Status)" -ForegroundColor $statusColor
    } else {
        Write-Host "Service Status: Not Installed" -ForegroundColor Red
    }
    
    # Get recent log entries
    Write-Host "`nRecent Log Entries:" -ForegroundColor Cyan
    Write-Host "------------------" -ForegroundColor Cyan
    
    $logs = Get-EventLog -LogName Application -Source "QuantumEnergyService" -Newest 5 -ErrorAction SilentlyContinue
    if ($logs) {
        $logs | ForEach-Object {
            $time = $_.TimeGenerated.ToString("HH:mm:ss")
            $message = $_.Message
            Write-Host "[$time] $message" -ForegroundColor White
        }
    } else {
        Write-Host "No logs found" -ForegroundColor Gray
    }
    
    Write-Host "`nLast updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ("-" * 50) -ForegroundColor DarkGray
    
    Start-Sleep -Seconds $RefreshInterval
    Clear-Host
    Write-Host "Quantum Energy Service Monitor" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    Write-Host "Refresh interval: $RefreshInterval seconds" -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Gray
    Write-Host ""
}