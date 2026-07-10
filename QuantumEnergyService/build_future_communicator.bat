@echo off
echo Building Future Self Communicator...
echo ==================================

REM Check if required file exists
if not exist "FutureSelfCommunicator.cs" (
    echo Error: FutureSelfCommunicator.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo Compiling Future Self Communicator...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:FutureSelfCommunicator.exe FutureSelfCommunicator.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the program: FutureSelfCommunicator.exe
    echo.
    echo Features:
    echo   - Send messages to your future self (2 years from now)
    echo   - Check for messages from your future self
    echo   - Set up automatic reminders
    echo   - Secure quantum temporal communication
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause