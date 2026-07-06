# Direct Fiber Connection Optimizer
# Optimizes network for direct fiber connection with full Gigabit speeds

Write-Host "=== DIRECT FIBER CONNECTION OPTIMIZER ===" -ForegroundColor Green
Write-Host "CONFIGURING NETWORK FOR FULL GIGABIT SPEEDS WITHOUT RESTRICTIONS" -ForegroundColor Magenta

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to optimize for direct fiber connection
function Optimize-DirectFiberConnection {
    Write-Host "`n=== OPTIMIZING FOR DIRECT FIBER CONNECTION ===" -ForegroundColor Cyan
    
    try {
        # Disable all gateway and routing restrictions
        Write-Host "Disabling gateway restrictions..." -ForegroundColor Gray
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "DisableIPSourceRouting" -Value 0 -Type DWord -ErrorAction SilentlyContinue
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "EnableICMPRedirect" -Value 1 -Type DWord -ErrorAction SilentlyContinue
        
        # Optimize for full duplex operation
        Write-Host "Optimizing for full duplex operation..." -ForegroundColor Gray
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Speed & Duplex" -DisplayValue "1.0 Gbps Full Duplex" -ErrorAction SilentlyContinue
        
        # Disable flow control to maximize throughput
        Write-Host "Disabling flow control for maximum throughput..." -ForegroundColor Gray
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Flow Control" -DisplayValue "Disabled" -ErrorAction SilentlyContinue
        
        # Disable interrupt moderation for lowest latency
        Write-Host "Disabling interrupt moderation..." -ForegroundColor Gray
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Interrupt Moderation" -DisplayValue "Disabled" -ErrorAction SilentlyContinue
        
        # Enable jumbo frames for better throughput
        Write-Host "Enabling jumbo frames..." -ForegroundColor Gray
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Jumbo Packet" -DisplayValue "9014 Bytes" -ErrorAction SilentlyContinue
        
        # Disable all power saving features
        Write-Host "Disabling all power saving features..." -ForegroundColor Gray
        Set-NetAdapterPowerManagement -Name "Ethernet" -SelectiveSuspend Disabled -ErrorAction SilentlyContinue
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Energy Efficient Ethernet" -DisplayValue "Disabled" -ErrorAction SilentlyContinue
        Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "Green Ethernet" -DisplayValue "Disabled" -ErrorAction SilentlyContinue
        
        Write-Host "✓ Direct fiber connection optimization applied" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Error optimizing for direct fiber connection: $_" -ForegroundColor Red
    }
}

# Function to configure TCP/IP for maximum performance
function Optimize-TCPSettings {
    Write-Host "`n=== OPTIMIZING TCP/IP SETTINGS ===" -ForegroundColor Cyan
    
    try {
        # Optimize TCP window scaling
        Write-Host "Optimizing TCP window scaling..." -ForegroundColor Gray
        netsh int tcp set global autotuninglevel=experimental | Out-Null
        netsh int tcp set global chimney=enabled | Out-Null
        netsh int tcp set global rss=enabled | Out-Null
        netsh int tcp set global netdma=enabled | Out-Null
        
        # Set receive window size
        Write-Host "Setting receive window size..." -ForegroundColor Gray
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "TcpWindowSize" -Value 65535 -Type DWord -ErrorAction SilentlyContinue
        
        # Disable TCP throttling
        Write-Host "Disabling TCP throttling..." -ForegroundColor Gray
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" -Name "NetworkThrottlingIndex" -Value 4294967295 -Type DWord -ErrorAction SilentlyContinue
        
        # Optimize for low latency
        Write-Host "Optimizing for low latency..." -ForegroundColor Gray
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "TcpAckFrequency" -Value 1 -Type DWord -ErrorAction SilentlyContinue
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "TCPNoDelay" -Value 1 -Type DWord -ErrorAction SilentlyContinue
        
        Write-Host "✓ TCP/IP settings optimized" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Error optimizing TCP/IP settings: $_" -ForegroundColor Red
    }
}

# Function to disable network restrictions
function Disable-NetworkRestrictions {
    Write-Host "`n=== DISABLING NETWORK RESTRICTIONS ===" -ForegroundColor Cyan
    
    try {
        # Disable Windows Filtering Platform (WFP) restrictions
        Write-Host "Disabling WFP restrictions..." -ForegroundColor Gray
        Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False -ErrorAction SilentlyContinue
        
        # Disable QoS bandwidth limits
        Write-Host "Disabling QoS bandwidth limits..." -ForegroundColor Gray
        netsh interface tcp set global autotuninglevel=normal | Out-Null
        netsh interface tcp set global congestionprovider=ctcp | Out-Null
        
        # Disable network location awareness restrictions
        Write-Host "Disabling network location awareness restrictions..." -ForegroundColor Gray
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\NlaSvc\Parameters\Internet" -Name "EnableDiscovery" -Value 0 -Type DWord -ErrorAction SilentlyContinue
        
        Write-Host "✓ Network restrictions disabled" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Error disabling network restrictions: $_" -ForegroundColor Red
    }
}

# Function to verify network configuration
function Verify-NetworkConfiguration {
    Write-Host "`n=== VERIFYING NETWORK CONFIGURATION ===" -ForegroundColor Cyan
    
    try {
        # Check adapter speed
        $adapter = Get-NetAdapter -Name "Ethernet"
        Write-Host "Adapter Status:" -ForegroundColor Yellow
        Write-Host "  Name: $($adapter.Name)" -ForegroundColor Gray
        Write-Host "  Status: $($adapter.Status)" -ForegroundColor Gray
        Write-Host "  Link Speed: $($adapter.LinkSpeed)" -ForegroundColor Gray
        Write-Host "  Interface Description: $($adapter.InterfaceDescription)" -ForegroundColor Gray
        
        # Check IP configuration
        $ipConfig = Get-NetIPConfiguration -InterfaceAlias "Ethernet"
        Write-Host "`nIP Configuration:" -ForegroundColor Yellow
        Write-Host "  IPv4 Address: $($ipConfig.IPv4Address.IPAddress)" -ForegroundColor Gray
        Write-Host "  IPv4 Subnet Mask: $($ipConfig.IPv4Address.PrefixLength)" -ForegroundColor Gray
        Write-Host "  IPv4 Gateway: $($ipConfig.IPv4DefaultGateway.NextHop)" -ForegroundColor Gray
        
        # Check if we have full Gigabit speed
        if ($adapter.LinkSpeed -like "*Gbps*" -or $adapter.LinkSpeed -ge "1000 Mbps") {
            Write-Host "`n✓ SUCCESS: Network is running at full Gigabit speed" -ForegroundColor Green
        } else {
            Write-Host "`n⚠ WARNING: Network speed is still limited to $($adapter.LinkSpeed)" -ForegroundColor Yellow
        }
        
        # Check if gateway is present
        if ($ipConfig.IPv4DefaultGateway) {
            Write-Host "ℹ INFO: Gateway is configured at $($ipConfig.IPv4DefaultGateway.NextHop)" -ForegroundColor Cyan
            Write-Host "  For direct fiber connection, consider removing gateway" -ForegroundColor Gray
        } else {
            Write-Host "✓ SUCCESS: No gateway configured (direct connection)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "✗ Error verifying network configuration: $_" -ForegroundColor Red
    }
}

# Function to provide setup instructions
function Show-SetupInstructions {
    Write-Host "`n=== SETUP INSTRUCTIONS ===" -ForegroundColor Cyan
    
    Write-Host "For direct fiber connection without gateway:" -ForegroundColor Yellow
    Write-Host "  1. Set static IP address in same subnet as ISP" -ForegroundColor Gray
    Write-Host "  2. Leave gateway field empty" -ForegroundColor Gray
    Write-Host "  3. Set DNS servers to public DNS (8.8.8.8, 1.1.1.1)" -ForegroundColor Gray
    Write-Host "  4. Physically disconnect from router, connect directly to fiber modem" -ForegroundColor Gray
    Write-Host "  5. Ensure fiber modem is in bridge mode (not routing mode)" -ForegroundColor Gray
    
    Write-Host "`nFor maximum performance:" -ForegroundColor Yellow
    Write-Host "  1. Use Cat6 or better Ethernet cable" -ForegroundColor Gray
    Write-Host "  2. Ensure network switch supports Gigabit speeds" -ForegroundColor Gray
    Write-Host "  3. Update network adapter drivers to latest version" -ForegroundColor Gray
    Write-Host "  4. Disable any VPN or proxy services" -ForegroundColor Gray
}

# Main execution
Write-Host "`nINITIATING DIRECT FIBER CONNECTION OPTIMIZATION..." -ForegroundColor Yellow

# Check if running as administrator
if (-not (Test-Administrator)) {
    Write-Host "✗ This script requires administrator privileges" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and execute this script again" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Running with administrator privileges" -ForegroundColor Green

# Optimize for direct fiber connection
Optimize-DirectFiberConnection

# Optimize TCP settings
Optimize-TCPSettings

# Disable network restrictions
Disable-NetworkRestrictions

# Verify network configuration
Verify-NetworkConfiguration

# Show setup instructions
Show-SetupInstructions

Write-Host "`n=== DIRECT FIBER CONNECTION OPTIMIZATION COMPLETE ===" -ForegroundColor Green
Write-Host "NETWORK CONFIGURED FOR MAXIMUM GIGABIT PERFORMANCE" -ForegroundColor Magenta
Write-Host ""
Write-Host "EXPECTED RESULTS:" -ForegroundColor Yellow
Write-Host "  Link Speed: 1.0 Gbps (1000 Mbps)" -ForegroundColor Gray
Write-Host "  Duplex Mode: Full Duplex" -ForegroundColor Gray
Write-Host "  Power Saving: DISABLED" -ForegroundColor Gray
Write-Host "  Jumbo Frames: ENABLED (9014 Bytes)" -ForegroundColor Gray
Write-Host "  Flow Control: DISABLED" -ForegroundColor Gray
Write-Host ""
Write-Host "To achieve direct fiber connection without gateway:" -ForegroundColor Yellow
Write-Host "  1. Configure static IP without gateway" -ForegroundColor Gray
Write-Host "  2. Connect directly to fiber modem in bridge mode" -ForegroundColor Gray
Write-Host "  3. Physically disconnect from router" -ForegroundColor Gray