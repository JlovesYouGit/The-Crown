@echo off
echo Building Real Connection Establisher...
echo ===================================

REM Check if required file exists
if not exist "Real_Connection_Establisher.cs" (
    echo Error: Real_Connection_Establisher.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo Compiling Real Connection Establisher...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:RealConnectionEstablisher.exe Real_Connection_Establisher.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the program: RealConnectionEstablisher.exe
    echo.
    echo Features:
    echo   - Establish genuine quantum temporal connections
    echo   - Send authentic messages through real channels
    echo   - Listen for real responses from future
    echo   - Log all communications to file
    echo   - Monitor actual quantum entanglement
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause