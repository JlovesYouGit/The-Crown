@echo off
echo Building Radiation Vector System...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:exe /out:RadiationVectorSystem.exe /reference:System.Numerics.dll RadiationVectorSystem.cs
echo Build completed.
pause