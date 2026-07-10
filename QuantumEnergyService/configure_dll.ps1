# Quantum Energy Service DLL Configuration Script

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Pause
    Exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   CONFIGURE QUANTUM ENERGY SERVICE DLLs" -ForegroundColor Cyan
Write-Host "   Windows DLL Configuration" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[CONFIG] Running as Administrator - proceeding with DLL configuration" -ForegroundColor Green
Start-Sleep -Seconds 1

# Define required DLLs for energy service
$requiredDlls = @(
    "kernel32.dll",
    "advapi32.dll",
    "ole32.dll",
    "ntdll.dll",
    "powrprof.dll",
    "setupapi.dll",
    "user32.dll",
    "gdi32.dll"
)

Write-Host "[CONFIG] Checking required system DLLs..." -ForegroundColor Green

$dllPath = "C:\Windows\System32"
$missingDlls = @()

foreach ($dll in $requiredDlls) {
    $fullPath = Join-Path $dllPath $dll
    if (Test-Path $fullPath) {
        Write-Host "[OK] Found $dll" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $dll not found" -ForegroundColor Red
        $missingDlls += $dll
    }
}

if ($missingDlls.Count -gt 0) {
    Write-Host ""
    Write-Host "[WARNING] Missing DLLs detected:" -ForegroundColor Yellow
    foreach ($dll in $missingDlls) {
        Write-Host "  - $dll" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Please ensure all required DLLs are present in System32." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[SUCCESS] All required DLLs are present." -ForegroundColor Green
}

Write-Host ""
Write-Host "[CONFIG] Configuring DLL loading policies..." -ForegroundColor Green

# Configure DLL search order (registry settings)
$dllSearchPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager"
if (Test-Path $dllSearchPath) {
    # Get current SafeDllSearchMode value
    $safeDllSearchMode = Get-ItemProperty -Path $dllSearchPath -Name "SafeDllSearchMode" -ErrorAction SilentlyContinue
    if ($safeDllSearchMode -ne $null) {
        Write-Host "[CONFIG] Current SafeDllSearchMode: $($safeDllSearchMode.SafeDllSearchMode)" -ForegroundColor Green
    } else {
        # Set SafeDllSearchMode to 1 (enable safe DLL search mode)
        Set-ItemProperty -Path $dllSearchPath -Name "SafeDllSearchMode" -Value 1 -Type DWord
        Write-Host "[CONFIG] Set SafeDllSearchMode to 1 (enabled)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[CONFIG] Setting up DLL dependency information..." -ForegroundColor Green

# Create DLL directory if it doesn't exist
$serviceDllPath = "C:\QuantumEnergyService\dll"
if (!(Test-Path $serviceDllPath)) {
    New-Item -ItemType Directory -Path $serviceDllPath -Force | Out-Null
    Write-Host "[CONFIG] Created DLL directory: $serviceDllPath" -ForegroundColor Green
}

# Copy required service-specific DLLs (if any)
# In a real implementation, this would copy custom DLLs needed by the service
Write-Host "[CONFIG] No custom DLLs to copy for this service." -ForegroundColor Green

Write-Host ""
Write-Host "[CONFIG] Configuring hardware acceleration DLLs..." -ForegroundColor Green

# Check for graphics driver DLLs
$graphicsDlls = @(
    "opengl32.dll",
    "glu32.dll",
    "d3d11.dll",
    "d3d12.dll",
    "dxgi.dll"
)

foreach ($dll in $graphicsDlls) {
    $fullPath = Join-Path $dllPath $dll
    if (Test-Path $fullPath) {
        Write-Host "[OK] Hardware acceleration DLL: $dll" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Hardware acceleration DLL not found: $dll" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[CONFIG] Setting up DLL registration for energy service..." -ForegroundColor Green

# Register service DLLs if needed
# This would typically involve calling RegSvr32 for COM DLLs
# For our service, we're using .NET which handles registration differently

Write-Host "[CONFIG] No COM DLLs to register for this service." -ForegroundColor Green

Write-Host ""
Write-Host "[CONFIG] Verifying DLL permissions..." -ForegroundColor Green

# Check permissions on critical system DLLs
$criticalDlls = @("kernel32.dll", "advapi32.dll")
foreach ($dll in $criticalDlls) {
    $fullPath = Join-Path $dllPath $dll
    if (Test-Path $fullPath) {
        try {
            $acl = Get-Acl $fullPath
            $accessRules = $acl.Access | Where-Object { $_.IdentityReference -like "*SYSTEM*" -or $_.IdentityReference -like "*Administrators*" }
            if ($accessRules) {
                Write-Host "[OK] Permissions verified for $dll" -ForegroundColor Green
            } else {
                Write-Host "[WARNING] Check permissions for $dll" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "[INFO] Unable to check permissions for $dll" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "[COMPLETE] DLL configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  - Checked $($requiredDlls.Count) required system DLLs" -ForegroundColor Cyan
Write-Host "  - Configured DLL search policies" -ForegroundColor Cyan
Write-Host "  - Verified hardware acceleration support" -ForegroundColor Cyan
Write-Host "  - Set up service-specific DLL environment" -ForegroundColor Cyan
Write-Host ""
Write-Host "The energy service is now configured to use system DLLs efficiently." -ForegroundColor Cyan
Write-Host ""

Pause