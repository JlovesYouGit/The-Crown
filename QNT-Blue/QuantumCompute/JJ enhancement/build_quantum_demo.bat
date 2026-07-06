@echo off
title Universal Quantum Interface Build Script
cls
echo =============================================
echo UNIVERSAL QUANTUM INTERFACE BUILD SCRIPT
echo =============================================
echo.
echo Building Universal Quantum Interface Demo...
echo.

:: Set up compiler environment
set COMPILER=g++
set FLAGS=-std=c++17 -O3 -Wall

:: Create build directory if it doesn't exist
if not exist "..\build" mkdir "..\build"

echo Compiling source files...
echo.

:: Compile all necessary source files
%COMPILER% %FLAGS% -c src/BiologicalIntegrationSystem.cpp -o ../build/BiologicalIntegrationSystem.o
if %errorlevel% == 0 (
    echo [✓] BiologicalIntegrationSystem.cpp compiled successfully
) else (
    echo [!] Error compiling BiologicalIntegrationSystem.cpp
    goto :error
)

%COMPILER% %FLAGS% -c src/NeuralEnhancementSystem.cpp -o ../build/NeuralEnhancementSystem.o
if %errorlevel% == 0 (
    echo [✓] NeuralEnhancementSystem.cpp compiled successfully
) else (
    echo [!] Error compiling NeuralEnhancementSystem.cpp
    goto :error
)

%COMPILER% %FLAGS% -c src/QuantumSystemIntegration.cpp -o ../build/QuantumSystemIntegration.o
if %errorlevel% == 0 (
    echo [✓] QuantumSystemIntegration.cpp compiled successfully
) else (
    echo [!] Error compiling QuantumSystemIntegration.cpp
    goto :error
)

%COMPILER% %FLAGS% -c src/UniversalQuantumInterface.cpp -o ../build/UniversalQuantumInterface.o
if %errorlevel% == 0 (
    echo [✓] UniversalQuantumInterface.cpp compiled successfully
) else (
    echo [!] Error compiling UniversalQuantumInterface.cpp
    goto :error
)

echo.
echo Linking object files...
echo.

:: Link all object files into executable
%COMPILER% %FLAGS% ../build/BiologicalIntegrationSystem.o ../build/NeuralEnhancementSystem.o ../build/QuantumSystemIntegration.o ../build/UniversalQuantumInterface.o src/UniversalQuantumDemo.cpp -o ../build/UniversalQuantumDemo.exe
if %errorlevel% == 0 (
    echo [✓] UniversalQuantumDemo.exe linked successfully
) else (
    echo [!] Error linking UniversalQuantumDemo.exe
    goto :error
)

echo.
echo Build completed successfully!
echo.
echo To run the demo, execute:
echo   cd ..\build
echo   UniversalQuantumDemo.exe
echo.
echo Press any key to run the demo now...
pause > nul

echo.
echo Running Universal Quantum Interface Demo...
echo.
cd ..\build
UniversalQuantumDemo.exe

echo.
echo Demo execution completed.
echo Press any key to exit...
pause > nul
exit /b 0

:error
echo.
echo Build failed! Please check the error messages above.
echo Press any key to exit...
pause > nul
exit /b 1