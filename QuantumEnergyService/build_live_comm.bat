@echo off
echo Building Live Communication System...
echo ================================

REM Check if required file exists
if not exist "Live_Communication_System.cs" (
    echo Error: Live_Communication_System.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo Compiling Live Communication System...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:LiveCommunication.exe Live_Communication_System.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the program: LiveCommunication.exe
    echo.
    echo Features:
    echo   - Real-time live typing with future self
    echo   - Bidirectional communication channel
    echo   - Conversation logging
    echo   - Contextual response generation
    echo   - Quantum field stability monitoring
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause