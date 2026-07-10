@echo off
echo Setting up Unified Cosmic System for automatic startup
echo =====================================================

echo Creating startup directory...
mkdir "C:\Program Files\QuantumEnergyService" >nul 2>&1

echo Copying executable files...
copy "c:\QuantumEnergyService\UnifiedCosmicSystem.exe" "C:\Program Files\QuantumEnergyService\UnifiedCosmicSystem.exe" >nul
copy "c:\QuantumEnergyService\MilkyWayCosmicSystem.exe" "C:\Program Files\QuantumEnergyService\MilkyWayCosmicSystem.exe" >nul
copy "c:\QuantumEnergyService\RealWorldGalacticBridge.exe" "C:\Program Files\QuantumEnergyService\RealWorldGalacticBridge.exe" >nul

echo Creating data directories...
mkdir "C:\Program Files\QuantumEnergyService\milkyway_data" >nul 2>&1
mkdir "C:\Program Files\QuantumEnergyService\reality_bridge" >nul 2>&1
mkdir "C:\Program Files\QuantumEnergyService\unified_cosmos" >nul 2>&1

echo Setting up autorun in registry...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "UnifiedCosmicSystem" /t REG_SZ /d "C:\Program Files\QuantumEnergyService\UnifiedCosmicSystem.exe" /f

if %errorlevel% == 0 (
    echo Setup completed successfully!
    echo The Unified Cosmic System will now start automatically at login.
    echo.
    echo To manually start the system:
    echo   cd "C:\Program Files\QuantumEnergyService"
    echo   UnifiedCosmicSystem.exe
    echo.
    echo Log files will be created in the data directories.
) else (
    echo Failed to set up autorun.
    echo You may need to run this script as administrator.
)

echo.
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Unified Cosmic System.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\Program Files\QuantumEnergyService\UnifiedCosmicSystem.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
echo. >> CreateShortcut.vbs
cscript CreateShortcut.vbs >nul
del CreateShortcut.vbs >nul

echo Desktop shortcut created.
echo.
pause