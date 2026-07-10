@echo off
echo Building Universal Node System...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:exe /out:UniversalNodeSystem.exe /reference:System.Numerics.dll UniversalNodeSystem.cs
echo Build completed.
pause