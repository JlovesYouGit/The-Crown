@echo off
REM AMD Quantum Compute Installation Script
REM This script integrates the quantum compilation system with AMD Software

echo AMD Quantum Compute Installation
echo ================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as administrator
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Check for AMD software installation
if not exist "%ProgramFiles%\AMD" (
    echo ERROR: AMD software not found
    echo Please install AMD Software before installing Quantum Compute
    echo.
    pause
    exit /b 1
)

REM Create installation directories
echo Creating installation directories...
mkdir "%ProgramFiles%\AMD\QuantumCompute" >nul 2>&1
mkdir "%ProgramFiles%\AMD\QuantumCompute\bin" >nul 2>&1
mkdir "%ProgramFiles%\AMD\QuantumCompute\lib" >nul 2>&1
mkdir "%ProgramFiles%\AMD\QuantumCompute\include" >nul 2>&1
mkdir "%ProgramFiles%\AMD\QuantumCompute\samples" >nul 2>&1

REM Copy files
echo Copying files...
copy /Y "quantum_compiler.dll" "%ProgramFiles%\AMD\QuantumCompute\bin\" >nul 2>&1
copy /Y "quantum_runtime.dll" "%ProgramFiles%\AMD\QuantumCompute\bin\" >nul 2>&1
copy /Y "quantum_compiler.h" "%ProgramFiles%\AMD\QuantumCompute\include\" >nul 2>&1
copy /Y "quantum_optimizer.qs" "%ProgramFiles%\AMD\QuantumCompute\samples\" >nul 2>&1
copy /Y "quantum_integration.py" "%ProgramFiles%\AMD\QuantumCompute\samples\" >nul 2>&1

REM Register quantum service
echo Registering quantum service...
sc create "AMDQuantumService" binPath= "%ProgramFiles%\AMD\QuantumCompute\bin\quantum_service.exe" start= auto >nul 2>&1
sc description "AMDQuantumService" "AMD Quantum Compute Service" >nul 2>&1

REM Start the service
sc start "AMDQuantumService" >nul 2>&1

REM Add to PATH
echo Updating system PATH...
setx PATH "%PATH%;%ProgramFiles%\AMD\QuantumCompute\bin" /M >nul 2>&1

REM Register with AMD software
echo Registering with AMD software...
reg add "HKLM\SOFTWARE\AMD\QuantumCompute" /v "Version" /t REG_SZ /d "1.0.0001" /f >nul 2>&1
reg add "HKLM\SOFTWARE\AMD\QuantumCompute" /v "InstallPath" /t REG_SZ /d "%ProgramFiles%\AMD\QuantumCompute" /f >nul 2>&1

echo.
echo Installation completed successfully!
echo.
echo Please restart your computer to complete the installation.
echo.
pause