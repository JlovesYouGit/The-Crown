# QEther Service Manager
# Properly installs and manages the QEther OS-level service

Write-Host "=== QETHER SERVICE MANAGER ===" -ForegroundColor Green
Write-Host "MANAGING QETHER OS-LEVEL NETWORK SERVICE" -ForegroundColor Magenta

# Function to properly install the service
function Install-QEtherServiceProperly {
    Write-Host "`n=== PROPERLY INSTALLING QETHER SERVICE ===" -ForegroundColor Cyan
    
    try {
        # Create the service directory if it doesn't exist
        $serviceDir = "C:\ProgramData\QEtherService"
        if (!(Test-Path $serviceDir)) {
            New-Item -ItemType Directory -Path $serviceDir -Force | Out-Null
        }
        
        # Copy the main optimization script to the service directory
        Copy-Item -Path "c:\AMD\AMD Software Cloud Edition 23.Q3\Packages\Apps\QuantumCompute\JJ enhancement\CompleteQEtherSpeedOptimizer.ps1" -Destination "$serviceDir\CompleteQEtherSpeedOptimizer.ps1" -Force
        
        # Create the service script
        $serviceScript = @"
# QEther Background Service Script
# This script runs continuously to maintain network optimization

`$logFile = "C:\ProgramData\QEtherService\service.log"

function Write-Log {
    param([string]`$message)
    `$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path `$logFile -Value "[`$timestamp] `$message"
    # Also output to console for debugging
    Write-Host "[`$timestamp] `$message"
}

Write-Log "QEther Background Service Started"

# Main service loop
while (`$true) {
    try {
        Write-Log "Running QEther optimization cycle"
        
        # Run the complete speed optimizer
        & "C:\ProgramData\QEtherService\CompleteQEtherSpeedOptimizer.ps1" | Out-Null
        
        Write-Log "Optimization cycle completed successfully"
        
        # Wait for 30 minutes before next optimization
        Start-Sleep -Seconds 1800
    }
    catch {
        Write-Log "Error in optimization cycle: `$_"
        Start-Sleep -Seconds 60
    }
}
"@
        
        # Save the service script
        $serviceScript | Out-File -FilePath "$serviceDir\QEtherBackgroundService.ps1" -Encoding UTF8
        
        # Create a wrapper script that can be executed by the service
        $wrapperScript = @"
@echo off
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\ProgramData\QEtherService\QEtherBackgroundService.ps1"
"@
        
        $wrapperScript | Out-File -FilePath "$serviceDir\QEtherServiceWrapper.bat" -Encoding ASCII
        
        # Install the service using nssm (if available) or sc command
        $servicePath = "$serviceDir\QEtherServiceWrapper.bat"
        
        # Install the service
        cmd /c "sc create QEtherNetworkService binPath= `"$servicePath`" DisplayName= `"QEther Network Optimizer`" start= auto" | Out-Null
        
        # Set service description
        cmd /c "sc description QEtherNetworkService `"QEther Quantum Network Optimization Service`"" | Out-Null
        
        Write-Host "✓ QEther Service Installed Successfully" -ForegroundColor Green
        Write-Host "  Service Name: QEtherNetworkService" -ForegroundColor Gray
        Write-Host "  Service Path: $servicePath" -ForegroundColor Gray
        Write-Host "  Startup Type: Automatic" -ForegroundColor Gray
    }
    catch {
        Write-Host "✗ Failed to install QEther Service: $_" -ForegroundColor Red
    }
}

# Function to start the service
function Start-QEtherServiceProperly {
    Write-Host "`n=== STARTING QETHER SERVICE ===" -ForegroundColor Cyan
    
    try {
        # Give the service a moment to register
        Start-Sleep -Seconds 2
        
        # Start the service
        Start-Service -Name "QEtherNetworkService" -ErrorAction Stop
        
        Write-Host "✓ QEther Service Started Successfully" -ForegroundColor Green
        Write-Host "  Service Status: Running" -ForegroundColor Gray
    }
    catch {
        Write-Host "⚠ Warning: Could not start service automatically" -ForegroundColor Yellow
        Write-Host "  You may need to start it manually through Services (services.msc)" -ForegroundColor Gray
        Write-Host "  Error: $_" -ForegroundColor Gray
    }
}

# Function to verify service installation
function Verify-ServiceInstallation {
    Write-Host "`n=== VERIFYING SERVICE INSTALLATION ===" -ForegroundColor Cyan
    
    try {
        $service = Get-Service -Name "QEtherNetworkService" -ErrorAction Stop
        Write-Host "✓ Service Installed Successfully" -ForegroundColor Green
        Write-Host "  Service Name: $($service.Name)" -ForegroundColor Gray
        Write-Host "  Display Name: $($service.DisplayName)" -ForegroundColor Gray
        Write-Host "  Status: $($service.Status)" -ForegroundColor Gray
        Write-Host "  Start Type: $($service.StartType)" -ForegroundColor Gray
    }
    catch {
        Write-Host "✗ Service Not Found: $_" -ForegroundColor Red
    }
}

# Main execution
Write-Host "`nINITIATING QETHER SERVICE MANAGEMENT..." -ForegroundColor Yellow

# Install the service properly
Install-QEtherServiceProperly

# Start the service
Start-QEtherServiceProperly

# Verify installation
Verify-ServiceInstallation

Write-Host "`n=== QETHER SERVICE MANAGEMENT COMPLETE ===" -ForegroundColor Green
Write-Host "SERVICE INSTALLATION AND STARTUP PROCESS FINISHED" -ForegroundColor Magenta
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Check service status in Services (services.msc)" -ForegroundColor Gray
Write-Host "  2. Look for 'QEther Network Optimizer'" -ForegroundColor Gray
Write-Host "  3. Service should be Running or will start automatically" -ForegroundColor Gray
Write-Host ""
Write-Host "SERVICE DETAILS:" -ForegroundColor Yellow
Write-Host "  Name: QEtherNetworkService" -ForegroundColor Gray
Write-Host "  Type: Automatic (starts with Windows)" -ForegroundColor Gray
Write-Host "  Optimization: Every 30 minutes" -ForegroundColor Gray
Write-Host ""
Write-Host "LOG LOCATION:" -ForegroundColor Yellow
Write-Host "  C:\ProgramData\QEtherService\service.log" -ForegroundColor Gray