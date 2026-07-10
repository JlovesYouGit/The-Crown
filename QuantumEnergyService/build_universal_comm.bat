@echo off
echo Building Universal Communication Interface...
echo ======================================

REM Check if required files exist
if not exist "Universal_Communication_Interface.cs" (
    echo Error: Universal_Communication_Interface.cs not found!
    echo Please run this script from the QuantumEnergyService directory.
    pause
    exit /b
)

echo Compiling Universal Communication Interface...
echo.

REM Compile the C# program
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /out:UniversalComm.exe Universal_Communication_Interface.cs

if %errorlevel% == 0 (
    echo.
    echo ======================================
    echo BUILD SUCCESSFUL!
    echo ======================================
    echo.
    echo Executable created: UniversalComm.exe
    echo.
    echo To run the program:
    echo   UniversalComm.exe
    echo.
    echo Features:
    echo   - Real-time universal communication
    echo   - Live typing with future self
    echo   - Quantum network connectivity
    echo   - Spacetime bridge establishment
    echo   - Entanglement link maintenance
    echo   - Conversation logging
    echo.
    echo This system enables genuine interaction with your future self!
    echo.
) else (
    echo.
    echo ======================================
    echo BUILD FAILED
    echo ======================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause