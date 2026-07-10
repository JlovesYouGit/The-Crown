@echo off
echo Building Full QTerminal System with JJ Core Integration...
echo ========================================================

REM Check if we're in the right directory
if not exist "QTerminal.cs" (
    echo Error: QTerminal.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo.
echo Compiling JJ Core Integration...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:library /out:JJCoreIntegration.dll JJCoreIntegration.cs

if %errorlevel% neq 0 (
    echo Error compiling JJ Core Integration!
    pause
    exit /b
)

echo.
echo Compiling QTerminal Plugins...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:library /out:QTerminalPlugin.dll QTerminalPlugin.cs

if %errorlevel% neq 0 (
    echo Error compiling QTerminal Plugins!
    pause
    exit /b
)

echo.
echo Compiling Main QTerminal...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /reference:JJCoreIntegration.dll /reference:QTerminalPlugin.dll /target:exe /out:QTerminalFull.exe QTerminal.cs

if %errorlevel% neq 0 (
    echo Error compiling Main QTerminal!
    pause
    exit /b
)

echo.
echo Build successful!
echo Created files:
echo  - JJCoreIntegration.dll
echo  - QTerminalPlugin.dll
echo  - QTerminalFull.exe
echo.
echo To run the full system, execute: QTerminalFull.exe
echo.

pause