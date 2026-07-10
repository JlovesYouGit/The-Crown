@echo off
echo Compiling Natural Language Processing Test...
echo ==========================================

"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" Test_NL_Process.cs

if %errorlevel% == 0 (
    echo.
    echo Compilation successful!
    echo Running test...
    echo.
    Test_NL_Process.exe
) else (
    echo.
    echo Compilation failed!
    echo.
)

pause