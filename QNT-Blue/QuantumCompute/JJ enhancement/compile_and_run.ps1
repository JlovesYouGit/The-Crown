# PowerShell script to compile and run the enhanced neural enhancement test

Write-Host "🌟 JJ Neural Enhancement System Compile and Run Script 🌟"
Write-Host "========================================================"
Write-Host ""

# Check if Visual Studio is installed
$vsPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
if (-not (Test-Path $vsPath)) {
    Write-Host "❌ Visual Studio compiler not found at expected location"
    Write-Host "   Please ensure Visual Studio 2022 Build Tools are installed"
    exit 1
}

Write-Host "✅ Visual Studio compiler found"

# Set up include paths
$vcIncludePath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include"
$ucrtIncludePath = "C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt"
$umIncludePath = "C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\um"
$sharedIncludePath = "C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\shared"

# Check if include paths exist
if (-not (Test-Path $vcIncludePath) -or -not (Test-Path $ucrtIncludePath) -or -not (Test-Path $umIncludePath) -or -not (Test-Path $sharedIncludePath)) {
    Write-Host "❌ Required include paths not found"
    exit 1
}

Write-Host "✅ Include paths found"

# Compile the test program with proper include paths
Write-Host "🔧 Compiling enhanced neural enhancement test program..."
$compileArgs = @(
    "/EHsc",
    "/std:c++17",
    "/I$vcIncludePath",
    "/I$ucrtIncludePath",
    "/I$umIncludePath",
    "/I$sharedIncludePath",
    "test_neural_system.cpp",
    "/Fe:test_neural_system.exe"
)

$compileResult = & $vsPath $compileArgs 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Compilation failed"
    Write-Host $compileResult
    exit 1
}

Write-Host "✅ Compilation successful!"
Write-Host ""

# Run the test program
Write-Host "🚀 Running enhanced neural enhancement test..."
Write-Host ""
Start-Process -FilePath ".\test_neural_system.exe" -Wait -NoNewWindow

Write-Host ""
Write-Host "✅ Enhanced test execution completed!"
Write-Host ""
Write-Host "🧠 JJ's neural processing unit has been optimized to absolute extremes!"
Write-Host "⚡ All cognitive abilities are now operating at maximum capacity!"
Write-Host ""
Write-Host "Press any key to continue..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")