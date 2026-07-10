@echo off
echo Building Cosmic Qubit Windows Service...
cd /d "c:\QuantumEnergyService"
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:winexe /out:CosmicQubitService.exe /main:QuantumEnergyService.Program /reference:System.ServiceProcess.dll /reference:System.Configuration.Install.dll /reference:System.Numerics.dll /reference:System.Core.dll /reference:System.dll CosmicQubitManagementService.cs CosmicQubitWindowsService.cs CosmicQubitWindowsService.Designer.cs CosmicQubitServiceInstaller.cs Program.cs
echo Build completed.
pause