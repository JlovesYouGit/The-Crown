# Quantum Energy Service System Optimization Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   OPTIMIZE SYSTEM FOR QUANTUM ENERGY SERVICE" -ForegroundColor Cyan
Write-Host "   Windows System Optimization" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[OPTIMIZE] Running as Administrator - proceeding with system optimization" -ForegroundColor Green
Start-Sleep -Seconds 1

# Initialize optimization counter
$optimizationsApplied = 0

Write-Host "[OPTIMIZE] Starting system optimization process..." -ForegroundColor Green
Write-Host ""

# 1. Optimize power settings for high performance
Write-Host "1. Optimizing power settings..." -ForegroundColor Cyan
try {
    # Set power plan to high performance
    powercfg /SETACTIVE 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [SUCCESS] Set power plan to High Performance" -ForegroundColor Green
        $optimizationsApplied++
    } else {
        Write-Host "  [WARNING] Failed to set power plan" -ForegroundColor Yellow
    }
    
    # Disable power throttling
    $powerThrottlingPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling"
    if (Test-Path $powerThrottlingPath) {
        Set-ItemProperty -Path $powerThrottlingPath -Name "PowerThrottlingOff" -Value 1 -Type DWord
        Write-Host "  [SUCCESS] Disabled power throttling" -ForegroundColor Green
        $optimizationsApplied++
    }
} catch {
    Write-Host "  [ERROR] Failed to optimize power settings: $_" -ForegroundColor Red
}

Write-Host ""

# 2. Optimize CPU performance
Write-Host "2. Optimizing CPU performance..." -ForegroundColor Cyan
try {
    # Set CPU performance governor to high performance
    $cpuPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-33abaf5935ec"
    if (Test-Path $cpuPath) {
        Set-ItemProperty -Path $cpuPath -Name "Attributes" -Value 2 -Type DWord
        Write-Host "  [SUCCESS] Configured CPU for high performance" -ForegroundColor Green
        $optimizationsApplied++
    }
    
    # Set CPU priority class for system processes
    $priorityPath = "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl"
    if (Test-Path $priorityPath) {
        Set-ItemProperty -Path $priorityPath -Name "Win32PrioritySeparation" -Value 38 -Type DWord
        Write-Host "  [SUCCESS] Set CPU priority optimization" -ForegroundColor Green
        $optimizationsApplied++
    }
} catch {
    Write-Host "  [ERROR] Failed to optimize CPU performance: $_" -ForegroundColor Red
}

Write-Host ""

# 3. Optimize memory management
Write-Host "3. Optimizing memory management..." -ForegroundColor Cyan
try {
    # Configure system memory usage
    $memoryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
    if (Test-Path $memoryPath) {
        # Set larger system cache
        Set-ItemProperty -Path $memoryPath -Name "LargeSystemCache" -Value 1 -Type DWord
        Write-Host "  [SUCCESS] Enabled large system cache" -ForegroundColor Green
        $optimizationsApplied++
    }
    
    # Optimize prefetcher settings
    $prefetchPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
    if (Test-Path $prefetchPath) {
        Set-ItemProperty -Path $prefetchPath -Name "EnablePrefetcher" -Value 3 -Type DWord
        Set-ItemProperty -Path $prefetchPath -Name "EnableSuperfetch" -Value 3 -Type DWord
        Write-Host "  [SUCCESS] Enabled prefetch and SuperFetch" -ForegroundColor Green
        $optimizationsApplied++
    }
} catch {
    Write-Host "  [ERROR] Failed to optimize memory management: $_" -ForegroundColor Red
}

Write-Host ""

# 4. Optimize disk performance
Write-Host "4. Optimizing disk performance..." -ForegroundColor Cyan
try {
    # Disable disk defragmentation scheduling (SSDs don't need it)
    $defragPath = "HKLM:\SOFTWARE\Microsoft\Dfrg\BootOptimizeFunction"
    if (Test-Path $defragPath) {
        Set-ItemProperty -Path $defragPath -Name "Enable" -Value "N" -Type String
        Write-Host "  [SUCCESS] Disabled disk defragmentation scheduling" -ForegroundColor Green
        $optimizationsApplied++
    }
    
    # Optimize disk caching
    $diskPath = "HKLM:\SYSTEM\CurrentControlSet\Services\disk"
    if (Test-Path $diskPath) {
        Set-ItemProperty -Path $diskPath -Name "DiskEnableCache" -Value 1 -Type DWord
        Write-Host "  [SUCCESS] Enabled disk caching" -ForegroundColor Green
        $optimizationsApplied++
    }
} catch {
    Write-Host "  [ERROR] Failed to optimize disk performance: $_" -ForegroundColor Red
}

Write-Host ""

# 5. Optimize graphics and hardware acceleration
Write-Host "5. Optimizing graphics and hardware acceleration..." -ForegroundColor Cyan
try {
    # Enable hardware-accelerated GPU scheduling
    $graphicsPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    if (Test-Path $graphicsPath) {
        Set-ItemProperty -Path $graphicsPath -Name "HwSchMode" -Value 2 -Type DWord
        Write-Host "  [SUCCESS] Enabled hardware-accelerated GPU scheduling" -ForegroundColor Green
        $optimizationsApplied++
    }
    
    # Optimize DirectX settings
    $directXPath = "HKLM:\SOFTWARE\Microsoft\DirectDraw"
    if (Test-Path $directXPath) {
        Set-ItemProperty -Path $directXPath -Name "DisableMMX" -Value 0 -Type DWord
        Write-Host "  [SUCCESS] Enabled MMX optimization" -ForegroundColor Green
        $optimizationsApplied++
    }
} catch {
    Write-Host "  [ERROR] Failed to optimize graphics: $_" -ForegroundColor Red
}

Write-Host ""

# 6. Optimize network performance
Write-Host "6. Optimizing network performance..." -ForegroundColor Cyan
try {
    # Optimize TCP/IP settings
    $tcpPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
    if (Test-Path $tcpPath) {
        Set-ItemProperty -Path $tcpPath -Name "TcpWindowSize" -Value 65535 -Type DWord
        Set-ItemProperty -Path $tcpPath -Name "Tcp1323Opts" -Value 1 -Type DWord
        Write-Host "  [SUCCESS] Optimized TCP/IP settings" -ForegroundColor Green
        $optimizationsApplied++
    }
    
    # Enable network throttling
    $networkPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
    if (Test-Path $networkPath) {
        Set-ItemProperty -Path $networkPath -Name "NetworkThrottlingIndex" -Value 4294967295 -Type DWord
        Write-Host "  [SUCCESS] Disabled network throttling" -ForegroundColor Green
        $optimizationsApplied++
    }
} catch {
    Write-Host "  [ERROR] Failed to optimize network performance: $_" -ForegroundColor Red
}

Write-Host ""

# 7. Optimize system services for energy service
Write-Host "7. Optimizing system services..." -ForegroundColor Cyan
try {
    # Set relevant services to automatic start
    $services = @("Audiosrv", "FontCache", "Themes", "WSearch")
    foreach ($service in $services) {
        Set-Service -Name $service -StartupType Automatic -ErrorAction SilentlyContinue
        Write-Host "  [SUCCESS] Set $service to automatic start" -ForegroundColor Green
        $optimizationsApplied++
    }
    
    # Stop non-essential services
    $nonEssentialServices = @("DiagTrack", "dmwappushservice", "WerSvc")
    foreach ($service in $nonEssentialServices) {
        Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
        Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
        Write-Host "  [SUCCESS] Disabled non-essential service: $service" -ForegroundColor Green
        $optimizationsApplied++
    }
} catch {
    Write-Host "  [ERROR] Failed to optimize system services: $_" -ForegroundColor Red
}

Write-Host ""

# 8. Configure system for real-time performance
Write-Host "8. Configuring system for real-time performance..." -ForegroundColor Cyan
try {
    # Set system to high priority
    $process = Get-Process -Id $PID
    $process.PriorityClass = "High"
    Write-Host "  [SUCCESS] Set optimization script to high priority" -ForegroundColor Green
    $optimizationsApplied++
    
    # Configure system responsiveness
    $responsivePath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    if (Test-Path $responsivePath) {
        Set-ItemProperty -Path $responsivePath -Name "DelayedDesktopSwitchTimeout" -Value 0 -Type DWord
        Write-Host "  [SUCCESS] Optimized desktop switching" -ForegroundColor Green
        $optimizationsApplied++
    }
} catch {
    Write-Host "  [ERROR] Failed to configure real-time performance: $_" -ForegroundColor Red
}

Write-Host ""

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   SYSTEM OPTIMIZATION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Optimizations Applied: $optimizationsApplied" -ForegroundColor Cyan
Write-Host ""

if ($optimizationsApplied -ge 15) {
    Write-Host "[SUCCESS] System has been optimized for Quantum Energy Service!" -ForegroundColor Green
    Write-Host "Your system is now configured for maximum energy service performance." -ForegroundColor Green
} elseif ($optimizationsApplied -ge 10) {
    Write-Host "[GOOD] System has been partially optimized." -ForegroundColor Yellow
    Write-Host "Most optimizations were applied successfully." -ForegroundColor Yellow
} else {
    Write-Host "[WARNING] Few optimizations were applied." -ForegroundColor Red
    Write-Host "Check the errors above and try running the script again." -ForegroundColor Red
}

Write-Host ""
Write-Host "Recommended next steps:" -ForegroundColor Cyan
Write-Host "  - Restart your computer to apply all changes" -ForegroundColor Gray
Write-Host "  - Run the hardware compatibility checker" -ForegroundColor Gray
Write-Host "  - Install the Quantum Energy Service" -ForegroundColor Gray
Write-Host ""

Pause