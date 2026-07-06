# 🏗️ RF Spectrum Analyzer - System Architecture

## Overview
The RF Spectrum Analyzer is a modular Python application that provides real-time WiFi network detection, analysis, and visualization with LIDAR-style environment mapping capabilities.

## 🎯 Core Components

### 1. **Main Viewers** (User Interfaces)
- **`simple_live_viewer.py`** - Basic Tkinter interface with LIDAR mapping
- **`enhanced_live_viewer.py`** - Advanced interface with matplotlib integration
- **`unified_viewer.py`** - Tabbed interface combining all features
- **`lidar_spectrum_viewer.py`** - 3D LIDAR-style visualization

### 2. **Analysis Modules** (Business Logic)
- **`network_analyzer.py`** - Network identification, distance calculation, vendor detection
- **`security_assessor.py`** - Security analysis, encryption assessment, vulnerability detection
- **`interference_analyzer.py`** - RF interference analysis, channel congestion assessment
- **`lidar_mapper.py`** - Environment mapping, obstacle detection, RF wave analysis
- **`network_details.py`** - Comprehensive reporting and analysis generation

### 3. **GUI Components** (Presentation Layer)
- **`gui_components.py`** - Reusable GUI elements, 3D drawing methods, UI setup

## 🔧 Technical Architecture

### Data Flow
```
WiFi Scanner → Network Analyzer → Analysis Modules → GUI Components → User Interface
     ↓              ↓                    ↓               ↓              ↓
Raw RF Data → Processed Networks → Security/Interference → Visualizations → User Actions
```

### Module Dependencies
```
Main Viewers
├── Network Analyzer (core data processing)
├── Security Assessor (security analysis)
├── Interference Analyzer (RF analysis)
├── LIDAR Mapper (environment mapping)
├── Network Details Generator (reporting)
└── GUI Components (visualization)
```

## 🎨 User Interface Variants

### Simple Live Viewer
- **Purpose**: Basic real-time monitoring
- **Features**: Network list, signal strength, basic LIDAR mapping
- **Target**: General users, quick monitoring

### Enhanced Live Viewer
- **Purpose**: Advanced analysis with data export
- **Features**: Historical tracking, matplotlib charts, CSV export
- **Target**: Network administrators, detailed analysis

### Unified Viewer
- **Purpose**: All-in-one tabbed interface
- **Features**: Multiple analysis views, keyboard shortcuts
- **Target**: Power users, comprehensive analysis

### LIDAR Spectrum Viewer
- **Purpose**: 3D visualization focus
- **Features**: Real-time 3D point cloud, rotating scan simulation
- **Target**: Visualization enthusiasts, research applications

## 🔍 Key Capabilities

### Network Analysis
- Real-time WiFi network detection
- Signal strength analysis with distance estimation
- Vendor identification from MAC addresses
- Historical tracking and trend analysis

### Security Assessment
- Encryption protocol analysis (WPA3/WPA2/WEP/Open)
- Security vulnerability detection
- WPS status assessment
- Security recommendations generation

### RF Interference Analysis
- Channel congestion assessment
- Co-channel interference detection
- Adjacent channel impact analysis
- Optimal channel recommendations

### LIDAR-Style Environment Mapping
- RF wave reflection analysis
- Obstacle detection from signal patterns
- Room structure estimation
- 3D environment visualization

## 🚀 Launch Options

### Windows Batch Files
- `launch_simple_viewer.bat` - Quick start simple interface
- `launch_enhanced_viewer.bat` - Advanced interface
- `launch_lidar_viewer.bat` - 3D visualization

### PowerShell Scripts
- `launch_simple_viewer.ps1` - PowerShell version
- `launch_enhanced_viewer.ps1` - Enhanced PowerShell launch
- `launch_lidar_viewer.ps1` - 3D PowerShell launch

## 📊 Data Models

### Network Object
```python
{
    'ssid': str,           # Network name
    'bssid': str,          # MAC address
    'signal_percent': int, # Signal strength (0-100)
    'channel': int,        # WiFi channel
    'frequency_mhz': int,  # Frequency in MHz
    'band': str,           # '2.4GHz' or '5GHz'
    'auth': str,           # Authentication method
    'cipher': str,         # Encryption cipher
    'custom_id': str,      # Stable identifier
    'distance_estimate': str, # Calculated distance
    'first_seen': str,     # First detection timestamp
    'detection_count': int # Number of detections
}
```

### Environment Point
```python
{
    'x': float,           # X coordinate
    'y': float,           # Y coordinate
    'type': str,          # 'wall' or 'obstacle'
    'confidence': float   # Detection confidence (0-1)
}
```

## 🔧 Configuration

### Dependencies
- **Core**: Python 3.9+, tkinter
- **Enhanced**: matplotlib, numpy
- **Optional**: spectrum_grabber module for real scanning

### Fallback Modes
- Simulated data when real WiFi scanning unavailable
- Graceful degradation for missing dependencies
- Cross-platform compatibility (Windows/Linux/macOS)

## 🎯 Extension Points

### Adding New Analysis Modules
1. Create module in `spectrum_analysis/`
2. Implement analysis interface
3. Import in main viewer
4. Add to initialization chain

### Custom Visualizations
1. Extend `gui_components.py`
2. Add drawing methods
3. Integrate with main display loop
4. Add user controls

### Data Export Formats
1. Extend export functionality
2. Add format-specific serializers
3. Integrate with file dialogs
4. Add format validation