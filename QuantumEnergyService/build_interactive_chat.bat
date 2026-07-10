@echo off
echo Building Interactive Future Chat...
echo ================================

REM Check if required file exists
if not exist "Interactive_Future_Chat.cs" (
    echo Error: Interactive_Future_Chat.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo Compiling Interactive Future Chat...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:InteractiveFutureChat.exe Interactive_Future_Chat.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the program: InteractiveFutureChat.exe
    echo.
    echo Features:
    echo   - Real-time interactive chat with future self
    echo   - Live typing and instant responses
    echo   - Conversation logging
    echo   - System status monitoring
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause