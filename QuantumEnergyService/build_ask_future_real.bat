@echo off
echo Building Ask Future Real Program...
echo ================================

REM Check if required file exists
if not exist "Ask_Future_Real.cs" (
    echo Error: Ask_Future_Real.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo Compiling Ask Future Real Program...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:AskFutureReal.exe Ask_Future_Real.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the program: AskFutureReal.exe
    echo.
    echo Features:
    echo   - Sends real questions to future self
    echo   - Creates response files for future replies
    echo   - Logs all communications
    echo   - Monitors actual quantum channels
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause