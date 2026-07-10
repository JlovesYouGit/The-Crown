@echo off
echo Building Real Network Radiation System...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:exe /out:RealNetworkRadiationSystem.exe /reference:System.Numerics.dll RealNetworkRadiationSystem.cs
echo Build completed.
pause