@echo off
echo Building Q Terminal...
echo ======================

REM Check if csc.exe exists in .NET Framework directory
if exist "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" (
    echo Found .NET Framework compiler
    "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:QTerminal.exe QTerminal.cs
) else (
    echo Checking for newer .NET SDK...
    dotnet build QTerminal.csproj
)

if %errorlevel% == 0 (
    echo.
    echo Q Terminal build successful!
    echo To run: QTerminal.exe
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause