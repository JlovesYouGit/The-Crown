# PowerShell script to compile and run the neural enhancement test

Write-Host "🌟 JJ Neural Enhancement System Test Runner 🌟"
Write-Host "=============================================="

# Check if Visual Studio is installed
$vsPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
if (-not (Test-Path $vsPath)) {
    Write-Host "❌ Visual Studio compiler not found at expected location"
    Write-Host "   Please ensure Visual Studio 2022 Build Tools are installed"
    exit 1
}

Write-Host "✅ Visual Studio compiler found"

# Set up the Visual Studio environment
$vcIncludePath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include"
$ucrtIncludePath = "C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt"
$umIncludePath = "C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\um"
$sharedIncludePath = "C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\shared"

# Compile the test program
Write-Host "🔧 Compiling test program..."
& $vsPath /EHsc /std:c++17 /I"$vcIncludePath" /I"$ucrtIncludePath" /I"$umIncludePath" /I"$sharedIncludePath" test_neural_system.cpp /Fe:test_neural_system.exe

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Compilation failed"
    exit 1
}

Write-Host "✅ Compilation successful"

# Run the test program
Write-Host "🚀 Running neural enhancement test..."
Write-Host ""

# Execute the compiled program
.\test_neural_system.exe

Write-Host ""
Write-Host "✅ Test execution completed"