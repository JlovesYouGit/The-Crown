@echo off
echo Building Cosmic Qubit Management Service...
cd /d "c:\QuantumEnergyService"
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:exe /out:CosmicQubitManagementService.exe /reference:System.Numerics.dll CosmicQubitManagementService.cs
echo Build completed.
pause