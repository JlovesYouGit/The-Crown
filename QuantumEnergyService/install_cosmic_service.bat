@echo off
echo Installing Unified Cosmic Service
echo ===============================

echo Stopping any existing service...
net stop UnifiedCosmicService >nul 2>&1

echo Installing service...
copy "c:\QuantumEnergyService\UnifiedCosmicService.exe" "C:\Program Files\UnifiedCosmicService.exe"

echo Creating Windows service...
sc create UnifiedCosmicService binPath= "C:\Program Files\UnifiedCosmicService.exe" DisplayName= "Unified Cosmic Service" start= auto

if %errorlevel% == 0 (
    echo Service installed successfully!
    
    echo Setting service description...
    sc description UnifiedCosmicService "Bridges real world with galactic model for continuous cosmic computation"
    
    echo Starting service...
    net start UnifiedCosmicService
    
    if %errorlevel% == 0 (
        echo Unified Cosmic Service is now running automatically!
        echo It will start automatically at system boot.
    ) else (
        echo Failed to start service. Check Windows Event Log for details.
    )
) else (
    echo Failed to install service.
    echo Error code: %errorlevel%
)

echo.
echo Log files will be created at:
echo   c:\QuantumEnergyService\unified_cosmic_service.log
echo   c:\QuantumEnergyService\unified_cosmic_operations.log
echo.
echo To manually start: net start UnifiedCosmicService
echo To stop: net stop UnifiedCosmicService
echo To uninstall: sc delete UnifiedCosmicService
echo.
pause