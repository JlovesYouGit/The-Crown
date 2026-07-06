@echo off
echo Building Advanced Display Port Optimization System...
echo ====================================================

REM Set up environment
setlocal
set SRC_DIR=src
set BUILD_DIR=build
set OUTPUT_DIR=output

REM Create build directory if it doesn't exist
if not exist %BUILD_DIR% mkdir %BUILD_DIR%
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Compiling Display Port Optimization System...
echo.

REM Compile the display port optimization system
g++ -std=c++14 -I%SRC_DIR% -o %BUILD_DIR%\display_port_demo.exe ^
    %SRC_DIR%\DisplayPortDemo.cpp ^
    %SRC_DIR%\DisplayPortOptimizer.cpp

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Compilation successful!
    echo Moving executable to output directory...
    move %BUILD_DIR%\display_port_demo.exe %OUTPUT_DIR%\display_port_demo.exe >nul
    echo.
    echo ====================================================
    echo Display Port Optimization System Build Complete
    echo Executable: %OUTPUT_DIR%\display_port_demo.exe
    echo ====================================================
    echo To run the demonstration, execute:
    echo   %OUTPUT_DIR%\display_port_demo.exe
    echo.
) else (
    echo.
    echo ====================================================
    echo Compilation failed!
    echo Please check for errors above.
    echo ====================================================
)

pause