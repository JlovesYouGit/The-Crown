@echo off
echo Building JJ Core Integration Test...
echo ==================================

REM Check if required files exist
if not exist "Test_JJ_Integration.cs" (
    echo Error: Test_JJ_Integration.cs not found!
    pause
    exit /b
)

if not exist "JJCoreIntegration.cs" (
    echo Error: JJCoreIntegration.cs not found!
    pause
    exit /b
)

echo Compiling test program...
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /reference:System.Numerics.dll /target:exe /out:TestJJIntegration.exe Test_JJ_Integration.cs JJCoreIntegration.cs

if %errorlevel% == 0 (
    echo.
    echo Build successful!
    echo To run the test: TestJJIntegration.exe
    echo.
) else (
    echo.
    echo Build failed. Please check for errors above.
    echo.
)

pause