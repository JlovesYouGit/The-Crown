@echo off
cls
title Install F12 Boot Command

echo ========================================================
echo    INSTALL F12 BOOT COMMAND
echo    Pre-Windows Boot Gateway Installation
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

echo [INSTALL] Running as Administrator - proceeding with F12 boot command installation
echo.
timeout /t 1 /nobreak >nul

echo [INSTALL] Building Quantum BIOS Gateway...
timeout /t 1 /nobreak >nul

REM Navigate to the project directory
cd /d "C:\QuantumEnergyService"

REM Build the gateway if needed
if not exist "C:\QuantumEnergyService\bin\Release\QuantumBiosGateway.exe" (
    echo [BUILD] Building Quantum BIOS Gateway...
    if exist "build_bios_gateway.bat" (
        call build_bios_gateway.bat
    ) else (
        echo [WARNING] Build script not found, attempting direct build...
        if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe" (
            "C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe" "QuantumBiosGateway.csproj" /p:Configuration=Release
        )
    )
)

echo.
echo [INSTALL] Copying executable to system directory...
timeout /t 1 /nobreak >nul

REM Copy executable to system directory
copy /Y "C:\QuantumEnergyService\bin\Release\QuantumBiosGateway.exe" "C:\Windows\System32\quantum_bios_gateway.exe"

if %errorLevel% EQU 0 (
    echo [SUCCESS] Executable copied to system directory
) else (
    echo [ERROR] Failed to copy executable to system directory
    pause
    exit /b 1
)

echo.
echo [INSTALL] Configuring F12 boot command in registry...
timeout /t 1 /nobreak >nul

REM Configure F12 boot command using PowerShell
powershell -ExecutionPolicy Bypass -File "C:\QuantumEnergyService\configure_f12_boot_command.ps1"

if %errorLevel% EQU 0 (
    echo [SUCCESS] F12 boot command configured successfully
) else (
    echo [ERROR] Failed to configure F12 boot command
    pause
    exit /b 1
)

echo.
echo [INSTALL] Verifying installation...
timeout /t 1 /nobreak >nul

REM Verify the installation
if exist "C:\Windows\System32\quantum_bios_gateway.exe" (
    echo [VERIFY] Quantum BIOS Gateway executable found
) else (
    echo [WARNING] Quantum BIOS Gateway executable not found in system directory
)

REM Check registry
reg query "HKLM\SYSTEM\CurrentControlSet\Control\F12BootCommand" >nul 2>&1
if %errorLevel% EQU 0 (
    echo [VERIFY] F12 boot command registry entries found
) else (
    echo [WARNING] F12 boot command registry entries not found
)

echo.
echo [INSTALL] F12 boot command installation complete!
echo.
echo The F12 boot command will now execute before Windows boot,
echo establishing a gateway between BIOS full control and automated adjusters.
echo.
echo To test the installation:
echo   1. Reboot your computer
echo   2. Press F12 during boot to activate the gateway
echo   3. Check C:\QuantumEnergyService\quantum_bios_gateway.log for logs
echo.
pause