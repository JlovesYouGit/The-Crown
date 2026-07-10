@echo off
echo Building Future Communication Test...
echo =================================

REM Check if required files exist
if not exist "Test_Future_Communication.cs" (
    echo Error: Test_Future_Communication.cs not found!
    pause
    exit /b
)

if not exist "FutureSelfCommunicator.cs" (
    echo Error: FutureSelfCommunicator.cs not found!
    pause
    exit /b
)

echo Compiling test program...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:TestFutureCommunication.exe Test_Future_Communication.cs FutureSelfCommunicator.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the test: TestFutureCommunication.exe
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause