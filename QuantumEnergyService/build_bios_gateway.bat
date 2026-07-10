@echo off
cls
title Build Quantum BIOS Gateway

echo ========================================================
echo    BUILD QUANTUM BIOS GATEWAY
echo    Pre-Windows Boot Gateway Compilation
echo ========================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [WARNING] Not running as Administrator
    echo [INFO] Build may fail without admin privileges
    echo.
)

echo [BUILD] Starting Quantum BIOS Gateway build process...
echo.
timeout /t 1 /nobreak >nul

REM Navigate to the project directory
cd /d "C:\QuantumEnergyService"

echo [BUILD] Checking for MSBuild...
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe" (
    echo [FOUND] MSBuild located
    set MSBUILD_PATH="C:\Program Files\Microsoft Visual Studio\2022\Community\Msbuild\Current\Bin\MSBuild.exe"
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Msbuild\Current\Bin\MSBuild.exe" (
    echo [FOUND] MSBuild BuildTools located
    set MSBUILD_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Msbuild\Current\Bin\MSBuild.exe"
) else (
    echo [ERROR] MSBuild not found
    echo [INFO] Please install Visual Studio or Build Tools
    pause
    exit /b 1
)

echo.
echo [BUILD] Compiling Quantum BIOS Gateway...
timeout /t 1 /nobreak >nul

REM Build the project using MSBuild
%MSBUILD_PATH% "QuantumBiosGateway.csproj" /p:Configuration=Release

if %errorLevel% EQU 0 (
    echo [SUCCESS] Quantum BIOS Gateway compiled successfully
) else (
    echo [ERROR] Failed to compile Quantum BIOS Gateway
    pause
    exit /b 1
)

echo.
echo [BUILD] Creating output directory if needed...
if not exist "C:\QuantumEnergyService\bin\Release" (
    mkdir "C:\QuantumEnergyService\bin\Release"
)

echo.
echo [BUILD] Copying executable to system directory...
copy /Y "C:\QuantumEnergyService\bin\Release\QuantumBiosGateway.exe" "C:\Windows\System32\quantum_bios_gateway.exe"

if %errorLevel% EQU 0 (
    echo [SUCCESS] Executable copied to system directory
) else (
    echo [WARNING] Failed to copy executable to system directory
    echo [INFO] You may need to run as Administrator
)

echo.
echo [BUILD] Quantum BIOS Gateway build complete!
echo.
echo Output files:
echo   - C:\QuantumEnergyService\bin\Release\QuantumBiosGateway.exe
echo   - C:\Windows\System32\quantum_bios_gateway.exe
echo.
pause