@echo off
cls
title Uninstall F12 Boot Command

echo ========================================================
echo    UNINSTALL F12 BOOT COMMAND
echo    Pre-Windows Boot Gateway Removal
echo ========================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [ERROR] This script must be run as Administrator
    echo [ERROR] Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [UNINSTALL] Running as Administrator - proceeding with F12 boot command removal
echo.
timeout /t 1 /nobreak >nul

echo [UNINSTALL] Removing F12 boot command registry entries...
timeout /t 1 /nobreak >nul

REM Remove F12 boot command configuration using PowerShell
powershell -ExecutionPolicy Bypass -File "C:\QuantumEnergyService\cleanup_f12_boot_command.ps1"

if %errorLevel% EQU 0 (
    echo [SUCCESS] F12 boot command registry entries removed successfully
) else (
    echo [ERROR] Failed to remove F12 boot command registry entries
    pause
    exit /b 1
)

echo.
echo [UNINSTALL] Removing Quantum BIOS Gateway executable...
timeout /t 1 /nobreak >nul

REM Remove executable from system directory
del /F /Q "C:\Windows\System32\quantum_bios_gateway.exe" >nul 2>&1

if %errorLevel% EQU 0 (
    echo [SUCCESS] Quantum BIOS Gateway executable removed
) else (
    echo [INFO] Quantum BIOS Gateway executable not found or already removed
)

echo.
echo [UNINSTALL] Verifying removal...
timeout /t 1 /nobreak >nul

REM Verify the removal
if exist "C:\Windows\System32\quantum_bios_gateway.exe" (
    echo [WARNING] Quantum BIOS Gateway executable still exists
) else (
    echo [VERIFY] Quantum BIOS Gateway executable removed successfully
)

REM Check registry
reg query "HKLM\SYSTEM\CurrentControlSet\Control\F12BootCommand" >nul 2>&1
if %errorLevel% EQU 0 (
    echo [WARNING] F12 boot command registry entries still exist
) else (
    echo [VERIFY] F12 boot command registry entries removed successfully
)

echo.
echo [UNINSTALL] F12 boot command removal complete!
echo.
echo The F12 boot command has been removed from your system.
echo Pre-Windows boot autonomous control has been disabled.
echo.
pause