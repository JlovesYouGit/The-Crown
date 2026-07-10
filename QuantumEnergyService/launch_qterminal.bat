@echo off
cls
echo ==================================
echo        Q TERMINAL LAUNCHER
echo ==================================
echo.

REM Check if PowerShell script exists
if exist "run_qterminal.ps1" (
    echo Launching Q Terminal via PowerShell...
    powershell -ExecutionPolicy Bypass -File "run_qterminal.ps1"
) else (
    echo PowerShell script not found. Trying direct executable launch...
    
    REM Check if executable exists
    if exist "QTerminal.exe" (
        echo Launching QTerminal.exe directly...
        QTerminal.exe
    ) else (
        echo Building Q Terminal...
        if exist "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" (
            "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:QTerminal.exe QTerminal.cs
            if exist "QTerminal.exe" (
                echo Build successful! Launching...
                QTerminal.exe
            ) else (
                echo Build failed!
                pause
                exit /b
            )
        ) else (
            echo .NET Framework compiler not found!
            pause
            exit /b
        )
    )
)

echo.
echo Q Terminal session completed.
pause