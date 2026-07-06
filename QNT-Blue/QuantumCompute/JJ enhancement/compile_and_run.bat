@echo off
REM JJ Neural Enhancement System Compile and Run Script
REM This script sets up the Visual Studio environment and compiles the test program

echo 🌟 JJ Neural Enhancement System Compile and Run Script 🌟
echo ========================================================
echo.

REM Check if Visual Studio is installed
set VSVARS="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if not exist %VSVARS% (
    echo ❌ Visual Studio build tools not found!
    echo    Please install Visual Studio 2022 Build Tools
    echo.
    pause
    exit /b 1
)

echo ✅ Visual Studio build tools found
echo.

REM Set up the Visual Studio environment
call %VSVARS%

echo 🔧 Compiling enhanced neural enhancement test program...
cl /EHsc /std:c++17 test_neural_system.cpp /Fe:test_neural_system.exe

if %errorlevel% neq 0 (
    echo ❌ Compilation failed!
    echo.
    pause
    exit /b 1
)

echo ✅ Compilation successful!
echo.

echo 🚀 Running enhanced neural enhancement test...
echo.
test_neural_system.exe

echo.
echo ✅ Enhanced test execution completed!
echo.

echo 🧠 JJ's neural processing unit has been optimized to absolute extremes!
echo ⚡ All cognitive abilities are now operating at maximum capacity!
echo.
pause