@echo off
echo Building Quantum Energy Service...

REM Check if dotnet is available
where dotnet >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: .NET SDK not found. Please install .NET 8.0 SDK.
    pause
    exit /b 1
)

REM Restore packages
echo Restoring NuGet packages...
dotnet restore
if %errorlevel% neq 0 (
    echo Error restoring packages.
    pause
    exit /b 1
)

REM Build the project
echo Building project...
dotnet build --configuration Release
if %errorlevel% neq 0 (
    echo Error building project.
    pause
    exit /b 1
)

echo Build completed successfully!
echo Output location: bin\Release\net8.0\QuantumEnergyService.exe

pause