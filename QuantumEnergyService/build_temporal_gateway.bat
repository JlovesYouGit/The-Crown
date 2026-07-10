@echo off
echo Building Temporal Gateway System...
echo ================================

REM Check if required file exists
if not exist "TemporalGateway.cs" (
    echo Error: TemporalGateway.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo Compiling Temporal Gateway...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:TemporalGateway.exe TemporalGateway.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the program: TemporalGateway.exe
    echo.
    echo Features:
    echo   - Establish temporal gateways to any future date
    echo   - Bypass normal time flow restrictions
    echo   - Send/receive messages through time
    echo   - Quantum field stabilization
    echo   - Temporal paradox protection management
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause