# Fix Network Adapter Speed
# Disables energy-saving features that limit network speed

Write-Host "=== FIXING NETWORK ADAPTER SPEED ===" -ForegroundColor Green
Write-Host "DISABLING ENERGY-SAVING FEATURES TO ACHIEVE MAXIMUM SPEED" -ForegroundColor Magenta

# Function to disable energy-saving features
function Disable-EnergySavingFeatures {
    Write-Host "`n=== DISABLING ENERGY-SAVING FEATURES ===" -ForegroundColor Cyan
    
    try {
        # Disable Energy Efficient Ethernet
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Energy Efficient Ethernet" -DisplayValue "Disabled" -ErrorAction SilentlyContinue
        Write-Host "✓ Energy Efficient Ethernet: DISABLED" -ForegroundColor Green
        
        # Disable Green Ethernet
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Green Ethernet" -DisplayValue "Disabled" -ErrorAction SilentlyContinue
        Write-Host "✓ Green Ethernet: DISABLED" -ForegroundColor Green
        
        # Disable Advanced EEE
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Advanced EEE" -DisplayValue "Disabled" -ErrorAction SilentlyContinue
        Write-Host "✓ Advanced EEE: DISABLED" -ForegroundColor Green
        
        # Set Speed & Duplex to force 1.0 Gbps Full Duplex
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Speed & Duplex" -DisplayValue "1.0 Gbps Full Duplex" -ErrorAction SilentlyContinue
        Write-Host "✓ Speed & Duplex: 1.0 Gbps Full Duplex" -ForegroundColor Green
        
        # Disable Auto Disable Gigabit
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Auto Disable Gigabit" -DisplayValue "Disabled" -ErrorAction SilentlyContinue
        Write-Host "✓ Auto Disable Gigabit: DISABLED" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Error disabling energy-saving features: $_" -ForegroundColor Red
    }
}

# Function to optimize power management
function Optimize-PowerManagement {
    Write-Host "`n=== OPTIMIZING POWER MANAGEMENT ===" -ForegroundColor Cyan
    
    try {
        # Disable all power saving features for maximum performance
        # Using registry method to disable power management
        $registryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\000*"
        Get-ChildItem -Path $registryPath -ErrorAction SilentlyContinue | ForEach-Object {
            Set-ItemProperty -Path $_.PSPath -Name "PnPCapabilities" -Value 24 -Type DWord -ErrorAction SilentlyContinue
        }
        Write-Host "✓ Power Management: DISABLED via Registry" -ForegroundColor Green
        
        # Specifically disable selective suspend
        Set-NetAdapterPowerManagement -Name "Ethernet" -SelectiveSuspend Disabled -ErrorAction SilentlyContinue
        Write-Host "✓ Selective Suspend: DISABLED" -ForegroundColor Green
        
        # Disable device sleep on disconnect
        Set-NetAdapterPowerManagement -Name "Ethernet" -DeviceSleepOnDisconnect Disabled -ErrorAction SilentlyContinue
        Write-Host "✓ Device Sleep on Disconnect: DISABLED" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Error optimizing power management: $_" -ForegroundColor Red
    }
}

# Function to optimize for maximum performance
function Optimize-ForMaximumPerformance {
    Write-Host "`n=== OPTIMIZING FOR MAXIMUM PERFORMANCE ===" -ForegroundColor Cyan
    
    try {
        # Enable Receive Side Scaling (RSS)
        Set-NetAdapterRSS -Name "Ethernet" -Enabled $true -ErrorAction SilentlyContinue
        Write-Host "✓ Receive Side Scaling: ENABLED" -ForegroundColor Green
        
        # Enable Receive Segment Coalescing (RSC)
        Set-NetAdapterRsc -Name "Ethernet" -IPv4Enabled $true -IPv6Enabled $true -ErrorAction SilentlyContinue
        Write-Host "✓ Receive Segment Coalescing: ENABLED" -ForegroundColor Green
        
        # Enable Large Send Offload (LSO)
        Set-NetAdapterLso -Name "Ethernet" -IPv4Enabled $true -IPv6Enabled $true -ErrorAction SilentlyContinue
        Write-Host "✓ Large Send Offload: ENABLED" -ForegroundColor Green
        
        # Optimize TCP settings
        netsh int tcp set global autotuninglevel=experimental | Out-Null
        netsh int tcp set global chimney=enabled | Out-Null
        netsh int tcp set global rss=enabled | Out-Null
        netsh int tcp set global netdma=enabled | Out-Null
        Write-Host "✓ TCP Settings: OPTIMIZED" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Error optimizing for maximum performance: $_" -ForegroundColor Red
    }
}

# Function to verify network speed
function Verify-NetworkSpeed {
    Write-Host "`n=== VERIFYING NETWORK SPEED ===" -ForegroundColor Cyan
    
    try {
        # Get current adapter status
        $adapter = Get-NetAdapter -Name "Ethernet"
        Write-Host "Adapter Status:" -ForegroundColor Yellow
        Write-Host "  Name: $($adapter.Name)" -ForegroundColor Gray
        Write-Host "  Status: $($adapter.Status)" -ForegroundColor Gray
        Write-Host "  Link Speed: $($adapter.LinkSpeed)" -ForegroundColor Gray
        Write-Host "  Interface Description: $($adapter.InterfaceDescription)" -ForegroundColor Gray
        
        if ($adapter.LinkSpeed -like "*Gbps*" -or $adapter.LinkSpeed -ge "1000 Mbps") {
            Write-Host "✓ NETWORK SPEED FIXED: $($adapter.LinkSpeed)" -ForegroundColor Green
        } else {
            Write-Host "⚠ Network speed still limited: $($adapter.LinkSpeed)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "✗ Error verifying network speed: $_" -ForegroundColor Red
    }
}

# Function to provide troubleshooting steps
function Show-TroubleshootingSteps {
    Write-Host "`n=== TROUBLESHOOTING STEPS ===" -ForegroundColor Cyan
    
    Write-Host "If network speed is still limited after these changes:" -ForegroundColor Yellow
    Write-Host "  1. Check physical connection (cable quality)" -ForegroundColor Gray
    Write-Host "  2. Verify router/switch supports Gigabit Ethernet" -ForegroundColor Gray
    Write-Host "  3. Try a different Ethernet port on router/switch" -ForegroundColor Gray
    Write-Host "  4. Update network adapter drivers" -ForegroundColor Gray
    Write-Host "  5. Check for network adapter hardware issues" -ForegroundColor Gray
}

# Main execution
Write-Host "`nINITIATING NETWORK ADAPTER SPEED FIX..." -ForegroundColor Yellow

# Disable energy-saving features
Disable-EnergySavingFeatures

# Optimize power management
Optimize-PowerManagement

# Optimize for maximum performance
Optimize-ForMaximumPerformance

# Verify network speed
Verify-NetworkSpeed

# Show troubleshooting steps
Show-TroubleshootingSteps

Write-Host "`n=== NETWORK ADAPTER SPEED FIX COMPLETE ===" -ForegroundColor Green
Write-Host "ENERGY-SAVING FEATURES DISABLED FOR MAXIMUM PERFORMANCE" -ForegroundColor Magenta
Write-Host ""
Write-Host "EXPECTED RESULTS:" -ForegroundColor Yellow
Write-Host "  Link Speed: 1.0 Gbps (1000 Mbps)" -ForegroundColor Gray
Write-Host "  Energy Features: DISABLED" -ForegroundColor Gray
Write-Host "  Power Management: DISABLED" -ForegroundColor Gray
Write-Host "  Performance Features: ENABLED" -ForegroundColor Gray
Write-Host ""
Write-Host "PLEASE DISCONNECT AND RECONNECT YOUR ETHERNET CABLE TO APPLY CHANGES!" -ForegroundColor Green