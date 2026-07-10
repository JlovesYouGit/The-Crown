# Quantum Energy Service Master Control Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

# Function to display menu
function Show-Menu {
    Clear-Host
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "   QUANTUM ENERGY SERVICE MASTER CONTROL" -ForegroundColor Cyan
    Write-Host "   Integrated Energy Management System" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Main Menu:" -ForegroundColor Yellow
    Write-Host "  1. Install Quantum Energy Services" -ForegroundColor Gray
    Write-Host "  2. Uninstall Quantum Energy Services" -ForegroundColor Gray
    Write-Host "  3. Verify Service Installation" -ForegroundColor Gray
    Write-Host "  4. Start Services" -ForegroundColor Gray
    Write-Host "  5. Stop Services" -ForegroundColor Gray
    Write-Host "  6. Check Hardware Compatibility" -ForegroundColor Gray
    Write-Host "  7. Optimize System for Energy Service" -ForegroundColor Gray
    Write-Host "  8. Configure Registry Settings" -ForegroundColor Gray
    Write-Host "  9. Configure DLL Dependencies" -ForegroundColor Gray
    Write-Host " 10. Cleanup Registry Settings" -ForegroundColor Gray
    Write-Host " 11. View Service Status" -ForegroundColor Gray
    Write-Host " 12. View Service Logs" -ForegroundColor Gray
    Write-Host " 13. Install F12 Boot Command" -ForegroundColor Gray
    Write-Host " 14. Uninstall F12 Boot Command" -ForegroundColor Gray
    Write-Host " 15. Install Invisible BIOS Gateway" -ForegroundColor Gray
    Write-Host " 16. Uninstall Invisible BIOS Gateway" -ForegroundColor Gray
    Write-Host "  0. Exit" -ForegroundColor Gray
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
}

# Function to install services
function Install-Services {
    Write-Host "[INSTALL] Installing Quantum Energy Services..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the installation script
    if (Test-Path "C:\QuantumEnergyService\install_energy_cooling_service.ps1") {
        & "C:\QuantumEnergyService\install_energy_cooling_service.ps1"
    } else {
        Write-Host "[ERROR] Installation script not found!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to uninstall services
function Uninstall-Services {
    Write-Host "[UNINSTALL] Uninstalling Quantum Energy Services..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the uninstallation script
    if (Test-Path "C:\QuantumEnergyService\uninstall_energy_cooling_service.ps1") {
        & "C:\QuantumEnergyService\uninstall_energy_cooling_service.ps1"
    } else {
        Write-Host "[ERROR] Uninstallation script not found!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to verify installation
function Verify-Installation {
    Write-Host "[VERIFY] Verifying service installation..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the verification script
    if (Test-Path "C:\QuantumEnergyService\verify_installation.bat") {
        & "C:\QuantumEnergyService\verify_installation.bat"
    } else {
        Write-Host "[ERROR] Verification script not found!" -ForegroundColor Red
        Write-Host "Press any key to continue..." -ForegroundColor Yellow
        $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Function to start services
function Start-Services {
    Write-Host "[START] Starting Quantum Energy Services..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    try {
        Start-Service -Name "CosmicQubitWindowsService" -ErrorAction SilentlyContinue
        Write-Host "[START] Cosmic Qubit Service started" -ForegroundColor Green
        
        Start-Service -Name "IntegratedEnergyCoolingService" -ErrorAction SilentlyContinue
        Write-Host "[START] Integrated Energy Cooling Service started" -ForegroundColor Green
        
        Start-Service -Name "ArmorBiosOptimizationService" -ErrorAction SilentlyContinue
        Write-Host "[START] Armor BIOS Optimization Service started" -ForegroundColor Green
        
        Start-Service -Name "InvisibleBiosGatewayService" -ErrorAction SilentlyContinue
        Write-Host "[START] Invisible BIOS Gateway Service started" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to start services: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to stop services
function Stop-Services {
    Write-Host "[STOP] Stopping Quantum Energy Services..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    try {
        Stop-Service -Name "InvisibleBiosGatewayService" -Force -ErrorAction SilentlyContinue
        Write-Host "[STOP] Invisible BIOS Gateway Service stopped" -ForegroundColor Green
        
        Stop-Service -Name "ArmorBiosOptimizationService" -Force -ErrorAction SilentlyContinue
        Write-Host "[STOP] Armor BIOS Optimization Service stopped" -ForegroundColor Green
        
        Stop-Service -Name "IntegratedEnergyCoolingService" -Force -ErrorAction SilentlyContinue
        Write-Host "[STOP] Integrated Energy Cooling Service stopped" -ForegroundColor Green
        
        Stop-Service -Name "CosmicQubitWindowsService" -Force -ErrorAction SilentlyContinue
        Write-Host "[STOP] Cosmic Qubit Service stopped" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to stop services: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to check hardware compatibility
function Check-HardwareCompatibility {
    Write-Host "[CHECK] Checking hardware compatibility..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the hardware compatibility script
    if (Test-Path "C:\QuantumEnergyService\check_hardware_compatibility.ps1") {
        & "C:\QuantumEnergyService\check_hardware_compatibility.ps1"
    } else {
        Write-Host "[ERROR] Hardware compatibility script not found!" -ForegroundColor Red
        Write-Host "Press any key to continue..." -ForegroundColor Yellow
        $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Function to optimize system
function Optimize-System {
    Write-Host "[OPTIMIZE] Optimizing system for energy service..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the optimization script
    if (Test-Path "C:\QuantumEnergyService\optimize_system.ps1") {
        & "C:\QuantumEnergyService\optimize_system.ps1"
    } else {
        Write-Host "[ERROR] System optimization script not found!" -ForegroundColor Red
        Write-Host "Press any key to continue..." -ForegroundColor Yellow
        $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Function to configure registry
function Configure-Registry {
    Write-Host "[CONFIG] Configuring registry settings..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the registry configuration script
    if (Test-Path "C:\QuantumEnergyService\configure_registry.ps1") {
        & "C:\QuantumEnergyService\configure_registry.ps1"
    } else {
        Write-Host "[ERROR] Registry configuration script not found!" -ForegroundColor Red
        Write-Host "Press any key to continue..." -ForegroundColor Yellow
        $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Function to configure DLLs
function Configure-DLLs {
    Write-Host "[CONFIG] Configuring DLL dependencies..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the DLL configuration script
    if (Test-Path "C:\QuantumEnergyService\configure_dll.ps1") {
        & "C:\QuantumEnergyService\configure_dll.ps1"
    } else {
        Write-Host "[ERROR] DLL configuration script not found!" -ForegroundColor Red
        Write-Host "Press any key to continue..." -ForegroundColor Yellow
        $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Function to cleanup registry
function Cleanup-Registry {
    Write-Host "[CLEANUP] Cleaning up registry settings..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the registry cleanup script
    if (Test-Path "C:\QuantumEnergyService\cleanup_registry.ps1") {
        & "C:\QuantumEnergyService\cleanup_registry.ps1"
    } else {
        Write-Host "[ERROR] Registry cleanup script not found!" -ForegroundColor Red
        Write-Host "Press any key to continue..." -ForegroundColor Yellow
        $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Function to view service status
function View-ServiceStatus {
    Write-Host "[STATUS] Quantum Energy Service Status" -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $cosmicService = Get-Service -Name "CosmicQubitWindowsService" -ErrorAction SilentlyContinue
        if ($cosmicService) {
            Write-Host "Cosmic Qubit Management Service:" -ForegroundColor Yellow
            Write-Host "  Status: $($cosmicService.Status)" -ForegroundColor Gray
            Write-Host "  Start Type: $($cosmicService.StartType)" -ForegroundColor Gray
        } else {
            Write-Host "Cosmic Qubit Management Service: NOT INSTALLED" -ForegroundColor Red
        }
        
        Write-Host ""
        
        $coolingService = Get-Service -Name "IntegratedEnergyCoolingService" -ErrorAction SilentlyContinue
        if ($coolingService) {
            Write-Host "Integrated Energy Cooling Service:" -ForegroundColor Yellow
            Write-Host "  Status: $($coolingService.Status)" -ForegroundColor Gray
            Write-Host "  Start Type: $($coolingService.StartType)" -ForegroundColor Gray
        } else {
            Write-Host "Integrated Energy Cooling Service: NOT INSTALLED" -ForegroundColor Red
        }
        
        Write-Host ""
        
        $armorService = Get-Service -Name "ArmorBiosOptimizationService" -ErrorAction SilentlyContinue
        if ($armorService) {
            Write-Host "Armor BIOS Optimization Service:" -ForegroundColor Yellow
            Write-Host "  Status: $($armorService.Status)" -ForegroundColor Gray
            Write-Host "  Start Type: $($armorService.StartType)" -ForegroundColor Gray
        } else {
            Write-Host "Armor BIOS Optimization Service: NOT INSTALLED" -ForegroundColor Red
        }
        
        Write-Host ""
        
        $invisibleGatewayService = Get-Service -Name "InvisibleBiosGatewayService" -ErrorAction SilentlyContinue
        if ($invisibleGatewayService) {
            Write-Host "Invisible BIOS Gateway Service:" -ForegroundColor Yellow
            Write-Host "  Status: $($invisibleGatewayService.Status)" -ForegroundColor Gray
            Write-Host "  Start Type: $($invisibleGatewayService.StartType)" -ForegroundColor Gray
        } else {
            Write-Host "Invisible BIOS Gateway Service: NOT INSTALLED" -ForegroundColor Red
        }
    } catch {
        Write-Host "[ERROR] Failed to retrieve service status: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to view service logs
function View-ServiceLogs {
    Write-Host "[LOGS] Quantum Energy Service Logs" -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $logFiles = @(
        "C:\QuantumEnergyService\armor_bios_optimization.log",
        "C:\QuantumEnergyService\energy_cooling_service.log",
        "C:\QuantumEnergyService\cosmic_service.log",
        "C:\QuantumEnergyService\hardware_comm.log",
        "C:\QuantumEnergyService\invisible_bios_gateway.log"
    )
    
    foreach ($logFile in $logFiles) {
        Write-Host "Checking: $logFile" -ForegroundColor Yellow
        if (Test-Path $logFile) {
            Write-Host "  [FOUND] Log file exists" -ForegroundColor Green
            $lines = Get-Content $logFile -Tail 5 -ErrorAction SilentlyContinue
            if ($lines) {
                Write-Host "  Recent entries:" -ForegroundColor Gray
                foreach ($line in $lines) {
                    Write-Host "    $line" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host "  [MISSING] Log file not found" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to install F12 boot command
function Install-F12BootCommand {
    Write-Host "[INSTALL] Installing F12 Boot Command..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the F12 boot command installation script
    if (Test-Path "C:\QuantumEnergyService\install_f12_boot_command.bat") {
        Start-Process -FilePath "C:\QuantumEnergyService\install_f12_boot_command.bat" -Wait
    } else {
        Write-Host "[ERROR] F12 boot command installation script not found!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to uninstall F12 boot command
function Uninstall-F12BootCommand {
    Write-Host "[UNINSTALL] Uninstalling F12 Boot Command..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the F12 boot command uninstallation script
    if (Test-Path "C:\QuantumEnergyService\uninstall_f12_boot_command.bat") {
        Start-Process -FilePath "C:\QuantumEnergyService\uninstall_f12_boot_command.bat" -Wait
    } else {
        Write-Host "[ERROR] F12 boot command uninstallation script not found!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to install invisible BIOS gateway
function Install-InvisibleBiosGateway {
    Write-Host "[INSTALL] Installing Invisible BIOS Gateway..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the invisible BIOS gateway installation script
    if (Test-Path "C:\QuantumEnergyService\install_invisible_gateway_service.bat") {
        Start-Process -FilePath "C:\QuantumEnergyService\install_invisible_gateway_service.bat" -Wait
    } else {
        Write-Host "[ERROR] Invisible BIOS gateway installation script not found!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to uninstall invisible BIOS gateway
function Uninstall-InvisibleBiosGateway {
    Write-Host "[UNINSTALL] Uninstalling Invisible BIOS Gateway..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    
    # Run the invisible BIOS gateway uninstallation script
    if (Test-Path "C:\QuantumEnergyService\uninstall_invisible_gateway_service.bat") {
        Start-Process -FilePath "C:\QuantumEnergyService\uninstall_invisible_gateway_service.bat" -Wait
    } else {
        Write-Host "[ERROR] Invisible BIOS gateway uninstallation script not found!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Main program loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice (0-14)"
    
    switch ($choice) {
        1 { Install-Services }
        2 { Uninstall-Services }
        3 { Verify-Installation }
        4 { Start-Services }
        5 { Stop-Services }
        6 { Check-HardwareCompatibility }
        7 { Optimize-System }
        8 { Configure-Registry }
        9 { Configure-DLLs }
        10 { Cleanup-Registry }
        11 { View-ServiceStatus }
        12 { View-ServiceLogs }
        13 { Install-F12BootCommand }
        14 { Uninstall-F12BootCommand }
        15 { Install-InvisibleBiosGateway }
        16 { Uninstall-InvisibleBiosGateway }
        0 { 
            Write-Host "Exiting Quantum Energy Service Master Control..." -ForegroundColor Green
            Start-Sleep -Seconds 1
        }
        default { 
            Write-Host "Invalid choice. Please enter a number between 0 and 16." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
} while ($choice -ne "0")

Write-Host "Thank you for using Quantum Energy Service!" -ForegroundColor Cyan
Write-Host ""
Pause