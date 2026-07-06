@echo off
title Quantum Computing Registry Setup
cls
echo ========================================
echo QUANTUM COMPUTING SYSTEM REGISTRY SETUP
echo ========================================
echo.
echo This script will implement quantum computing capabilities
echo at the Windows system level with secure stability for 
echo hypercompute and qubit control.
echo.

echo Setting execution policy...
powershell Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force > nul

echo.
echo Running quantum computing registry setup...
echo This may take a few moments and will request administrator privileges...
echo.
powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"C:\AMD\AMD Software Cloud Edition 23.Q3\Packages\Apps\QuantumCompute\JJ enhancement\quantum_registry_setup.ps1\"' -Verb RunAs"

echo.
echo Quantum computing registry setup initiated.
echo Please respond to the administrator privilege request if prompted.
echo.
echo After completion, please restart your computer for all changes to take effect.
echo.
echo Press any key to exit...
pause > nul