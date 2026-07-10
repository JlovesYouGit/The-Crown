# Quantum Energy Service Hardware Compatibility Checker

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   QUANTUM ENERGY SERVICE HARDWARE COMPATIBILITY CHECK" -ForegroundColor Cyan
Write-Host "   System Hardware Analysis" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[CHECK] Running as Administrator - proceeding with hardware compatibility check" -ForegroundColor Green
Start-Sleep -Seconds 1

# Initialize compatibility score
$compatibilityScore = 0
$totalChecks = 0

Write-Host "[CHECK] Analyzing system hardware..." -ForegroundColor Green
Write-Host ""

# Check CPU information
Write-Host "CPU Information:" -ForegroundColor Cyan
$totalChecks++
try {
    $cpu = Get-WmiObject -Class Win32_Processor
    Write-Host "  Model: $($cpu.Name)" -ForegroundColor Gray
    Write-Host "  Cores: $($cpu.NumberOfCores)" -ForegroundColor Gray
    Write-Host "  Threads: $($cpu.NumberOfLogicalProcessors)" -ForegroundColor Gray
    Write-Host "  Max Clock Speed: $($cpu.MaxClockSpeed) MHz" -ForegroundColor Gray
    Write-Host "  Architecture: $($cpu.Architecture)" -ForegroundColor Gray
    
    # Check for 64-bit architecture
    if ($cpu.Architecture -eq 9) {  # 9 = x64
        Write-Host "  [COMPATIBLE] 64-bit architecture detected" -ForegroundColor Green
        $compatibilityScore++
    } else {
        Write-Host "  [WARNING] 32-bit architecture may limit performance" -ForegroundColor Yellow
    }
    
    # Check for multi-core
    if ($cpu.NumberOfCores -ge 4) {
        Write-Host "  [COMPATIBLE] Multi-core processor detected" -ForegroundColor Green
        $compatibilityScore++
        $totalChecks++
    } else {
        Write-Host "  [WARNING] Single or dual-core processor may limit performance" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Unable to retrieve CPU information" -ForegroundColor Red
}

Write-Host ""

# Check memory information
Write-Host "Memory Information:" -ForegroundColor Cyan
$totalChecks++
try {
    $memory = Get-WmiObject -Class Win32_PhysicalMemory
    $totalMemory = ($memory | Measure-Object -Property Capacity -Sum).Sum / 1GB
    Write-Host "  Total Memory: $($totalMemory.ToString("F1")) GB" -ForegroundColor Gray
    Write-Host "  Memory Speed: $($memory[0].Speed) MHz" -ForegroundColor Gray
    Write-Host "  Memory Type: $($memory[0].SMBIOSMemoryType)" -ForegroundColor Gray
    
    # Check for minimum memory requirement (4GB)
    if ($totalMemory -ge 4) {
        Write-Host "  [COMPATIBLE] Sufficient memory for energy service" -ForegroundColor Green
        $compatibilityScore++
    } else {
        Write-Host "  [WARNING] Insufficient memory (< 4GB) may cause performance issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Unable to retrieve memory information" -ForegroundColor Red
}

Write-Host ""

# Check disk information
Write-Host "Disk Information:" -ForegroundColor Cyan
$totalChecks++
try {
    $disks = Get-WmiObject -Class Win32_LogicalDisk -Filter "DriveType=3"
    foreach ($disk in $disks) {
        $freeSpace = $disk.FreeSpace / 1GB
        $totalSpace = $disk.Size / 1GB
        $usedSpace = $totalSpace - $freeSpace
        $usagePercent = ($usedSpace / $totalSpace) * 100
        
        Write-Host "  Drive $($disk.DeviceID):" -ForegroundColor Gray
        Write-Host "    Total Size: $($totalSpace.ToString("F1")) GB" -ForegroundColor Gray
        Write-Host "    Free Space: $($freeSpace.ToString("F1")) GB" -ForegroundColor Gray
        Write-Host "    Usage: $($usagePercent.ToString("F1"))%" -ForegroundColor Gray
    }
    
    # Check for sufficient free space (at least 1GB)
    $systemDrive = $disks | Where-Object { $_.DeviceID -eq $env:SystemDrive }
    if ($systemDrive -and ($systemDrive.FreeSpace / 1GB) -ge 1) {
        Write-Host "  [COMPATIBLE] Sufficient disk space available" -ForegroundColor Green
        $compatibilityScore++
    } else {
        Write-Host "  [WARNING] Insufficient disk space (< 1GB) may cause issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Unable to retrieve disk information" -ForegroundColor Red
}

Write-Host ""

# Check graphics information
Write-Host "Graphics Information:" -ForegroundColor Cyan
$totalChecks++
try {
    $graphics = Get-WmiObject -Class Win32_VideoController
    foreach ($gpu in $graphics) {
        Write-Host "  Adapter: $($gpu.Name)" -ForegroundColor Gray
        Write-Host "  Video Memory: $(($gpu.AdapterRAM / 1GB).ToString("F1")) GB" -ForegroundColor Gray
        Write-Host "  Driver Version: $($gpu.DriverVersion)" -ForegroundColor Gray
    }
    
    # Check for dedicated graphics (at least 1GB VRAM)
    $dedicatedGPU = $graphics | Where-Object { $_.AdapterRAM -ge 1GB }
    if ($dedicatedGPU) {
        Write-Host "  [COMPATIBLE] Dedicated graphics detected" -ForegroundColor Green
        $compatibilityScore++
    } else {
        Write-Host "  [INFO] Integrated graphics may limit visualization capabilities" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Unable to retrieve graphics information" -ForegroundColor Red
}

Write-Host ""

# Check operating system information
Write-Host "Operating System Information:" -ForegroundColor Cyan
$totalChecks++
try {
    $os = Get-WmiObject -Class Win32_OperatingSystem
    Write-Host "  Version: $($os.Caption)" -ForegroundColor Gray
    Write-Host "  Build: $($os.BuildNumber)" -ForegroundColor Gray
    Write-Host "  Architecture: $($os.OSArchitecture)" -ForegroundColor Gray
    
    # Check for supported OS versions
    if ($os.Caption -match "Windows 10|Windows 11|Windows Server 2016|Windows Server 2019|Windows Server 2022") {
        Write-Host "  [COMPATIBLE] Supported operating system detected" -ForegroundColor Green
        $compatibilityScore++
    } else {
        Write-Host "  [WARNING] Unsupported operating system version" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Unable to retrieve OS information" -ForegroundColor Red
}

Write-Host ""

# Check .NET Framework version
Write-Host ".NET Framework Information:" -ForegroundColor Cyan
$totalChecks++
try {
    $netVersion = Get-ItemProperty "HKLM:SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" -ErrorAction SilentlyContinue
    if ($netVersion) {
        Write-Host "  Version: $($netVersion.Version)" -ForegroundColor Gray
        Write-Host "  Release: $($netVersion.Release)" -ForegroundColor Gray
        
        # Check for .NET Framework 4.8 or higher (release >= 461808)
        if ($netVersion.Release -ge 461808) {
            Write-Host "  [COMPATIBLE] .NET Framework 4.8 or higher detected" -ForegroundColor Green
            $compatibilityScore++
        } else {
            Write-Host "  [WARNING] .NET Framework version may be insufficient" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [ERROR] .NET Framework 4.x not found" -ForegroundColor Red
    }
} catch {
    Write-Host "  [ERROR] Unable to retrieve .NET Framework information" -ForegroundColor Red
}

Write-Host ""

# Check power management capabilities
Write-Host "Power Management Information:" -ForegroundColor Cyan
$totalChecks++
try {
    $powerPlans = powercfg /LIST 2>$null
    if ($powerPlans -match "High performance") {
        Write-Host "  [COMPATIBLE] High performance power plans available" -ForegroundColor Green
        $compatibilityScore++
    } else {
        Write-Host "  [INFO] Limited power plan options available" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Unable to retrieve power management information" -ForegroundColor Red
}

Write-Host ""

# Calculate compatibility percentage
$compatibilityPercentage = [math]::Round(($compatibilityScore / $totalChecks) * 100, 1)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   HARDWARE COMPATIBILITY SUMMARY" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Compatibility Score: $compatibilityScore / $totalChecks ($compatibilityPercentage%)" -ForegroundColor Cyan
Write-Host ""

if ($compatibilityPercentage -ge 80) {
    Write-Host "[SUCCESS] System is highly compatible with Quantum Energy Service!" -ForegroundColor Green
    Write-Host "The system meets or exceeds all major requirements for optimal performance." -ForegroundColor Green
} elseif ($compatibilityPercentage -ge 60) {
    Write-Host "[ACCEPTABLE] System is compatible with Quantum Energy Service." -ForegroundColor Yellow
    Write-Host "Some minor limitations may affect performance." -ForegroundColor Yellow
} else {
    Write-Host "[WARNING] System may have compatibility issues with Quantum Energy Service." -ForegroundColor Red
    Write-Host "Consider upgrading hardware components for optimal performance." -ForegroundColor Red
}

Write-Host ""
Write-Host "Recommended Actions:" -ForegroundColor Cyan
Write-Host "  - Ensure all Windows updates are installed" -ForegroundColor Gray
Write-Host "  - Install latest graphics drivers" -ForegroundColor Gray
Write-Host "  - Configure power settings to High Performance" -ForegroundColor Gray
Write-Host "  - Free up disk space if usage is above 80%" -ForegroundColor Gray
Write-Host ""

Pause