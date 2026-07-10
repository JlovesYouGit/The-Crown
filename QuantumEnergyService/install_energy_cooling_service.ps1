# Integrated Energy Cooling Service Installation Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   INSTALL INTEGRATED ENERGY COOLING SERVICE" -ForegroundColor Cyan
Write-Host "   Windows Service Installation" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INSTALL] Running as Administrator - proceeding with installation" -ForegroundColor Green
Start-Sleep -Seconds 1

# Build the project
Write-Host "[BUILD] Building the Quantum Energy Service project..." -ForegroundColor Green
try {
    # Navigate to the project directory
    Set-Location -Path "C:\QuantumEnergyService"
    
    # Build the project using MSBuild
    & "C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe" "QuantumEnergyService.csproj" /p:Configuration=Release
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[BUILD] Project built successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to build project" -ForegroundColor Red
        Pause
        Exit 1
    }
} catch {
    Write-Host "[WARNING] MSBuild not found or failed, continuing with installation..." -ForegroundColor Yellow
}

Start-Sleep -Seconds 1

# Install the service
Write-Host "[INSTALL] Installing Integrated Energy Cooling Service..." -ForegroundColor Green
try {
    # Use InstallUtil to install the service
    $installUtilPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe"
    & $installUtilPath "C:\QuantumEnergyService\bin\Release\QuantumEnergyService.exe"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[INSTALL] Service installed successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to install service" -ForegroundColor Red
        Pause
        Exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to install service: $_" -ForegroundColor Red
    Pause
    Exit 1
}

Start-Sleep -Seconds 1

# Start the service
Write-Host "[START] Starting Integrated Energy Cooling Service..." -ForegroundColor Green
try {
    Start-Service -Name "IntegratedEnergyCoolingService" -ErrorAction Stop
    Write-Host "[START] Service started successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to start service: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[COMPLETE] Integrated Energy Cooling Service installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Service Details:" -ForegroundColor Cyan
Write-Host "  Name: IntegratedEnergyCoolingService" -ForegroundColor Cyan
Write-Host "  Display Name: Integrated Energy Cooling Service" -ForegroundColor Cyan
Write-Host "  Status: Running" -ForegroundColor Cyan
Write-Host ""
Write-Host "To check service status:" -ForegroundColor Yellow
Write-Host "  Open Services.msc" -ForegroundColor Yellow
Write-Host "  Or run: Get-Service IntegratedEnergyCoolingService" -ForegroundColor Yellow
Write-Host ""

Pause