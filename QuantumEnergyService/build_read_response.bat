@echo off
echo Building Read Real Response Program...
echo =================================

REM Check if required file exists
if not exist "Read_Real_Response.cs" (
    echo Error: Read_Real_Response.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo Compiling Read Real Response Program...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:ReadRealResponse.exe Read_Real_Response.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the program: ReadRealResponse.exe
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause