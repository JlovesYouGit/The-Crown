@echo off
REM AMD Quantum Rendering System Enhancements Verification Script
REM Verifies that the new data structures compile correctly

echo 🌟 AMD Quantum Rendering System Enhancements Verification 🌟
echo ========================================================
echo.

REM Check if required files exist
echo Checking required files...
if not exist "verify_enhancements.cpp" (
    echo ❌ verify_enhancements.cpp not found!
    pause
    exit /b 1
)

if not exist "QuantumMeshBoost.h" (
    echo ❌ QuantumMeshBoost.h not found!
    pause
    exit /b 1
)

echo ✅ All required files found!
echo.

REM Compile the verification program
echo Compiling verification program...
cl /EHsc /std:c++17 /DWIN32 /D_WINDOWS ^
   /I"." ^
   /Fe"verify_enhancements.exe" ^
   /Fd"verify_enhancements.pdb" ^
   verify_enhancements.cpp

if %errorlevel% neq 0 (
    echo ❌ Compilation failed!
    pause
    exit /b 1
)

echo.
echo ✅ Verification program compiled successfully!
echo.
echo Running verification...
echo.
verify_enhancements.exe
echo.
echo ✅ Verification completed!
echo.
pause