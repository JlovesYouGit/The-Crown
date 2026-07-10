@echo off
echo Building Earth-Linked Node System...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:exe /out:EarthLinkedNodeSystem.exe /reference:System.Numerics.dll EarthLinkedNodeSystem.cs
echo Build completed.
pause