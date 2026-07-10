@echo off
echo Building Enhanced Q Terminal...
echo ================================

REM Copy the enhanced version to the main file
copy QTerminalEnhanced.cs QTerminal.cs

REM Compile using .NET Framework compiler
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:QTerminalEnhanced.exe QTerminal.cs

if %errorlevel% == 0 (
    echo.
    echo Enhanced Q Terminal build successful!
    echo To run: QTerminalEnhanced.exe
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause