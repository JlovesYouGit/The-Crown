# 🌊 LIDAR-Style Spectrum Viewer

A real-time 3D visualization tool that maps RF spectrum environment like LIDAR mapping, providing live visualization of WiFi networks and electromagnetic spectrum.

## Features

### 🎯 LIDAR-Style Visualization
- **Real-time 3D point cloud** of detected WiFi networks
- **Rotating scan beam** simulation like physical LIDAR
- **Distance estimation** based on signal strength
- **Color-coded frequency bands** (2.4GHz red, 5GHz blue)
- **Live updating** point cloud with scan history

### 📊 Advanced Analysis
- **Signal strength mapping** with physics-based distance calculation
- **Interference pattern detection** between networks
- **Channel utilization analysis** across frequency bands
- **Network vendor identification** from MAC addresses
- **Temporal tracking** of network changes over time

### 🖥️ Interactive GUI
- **3D rotatable view** with mouse controls
- **Real-time status updates** and network information
- **Multiple view modes** (top-down, side view, perspective)
- **Data export functionality** for further analysis
- **Professional dark theme** optimized for RF analysis

## Quick Start

### Windows Users
1. **Double-click** `launch_lidar_viewer.bat` 
2. **Or run** `launch_lidar_viewer.ps1` in PowerShell

### Manual Launch
```bash
cd spectrum_analysis
python lidar_spectrum_viewer.py
```

## System Requirements

- **Python 3.9+** with tkinter support
- **WiFi adapter** for real-time scanning
- **Windows/Linux/macOS** (Windows optimized)

### Dependencies
- `matplotlib` - 3D plotting and visualization
- `numpy` - Mathematical calculations
- `tkinter` - GUI framework (usually included with Python)

## How It Works

### LIDAR Simulation
The viewer simulates a rotating LIDAR scanner that:
1. **Sweeps 360°** around your position
2. **Detects WiFi networks** at each angle
3. **Maps signal strength** to distance
4. **Creates 3D points** representing network locations
5. **Builds point cloud** over time like real LIDAR

### RF Physics
- **Free Space Path Loss** calculations for distance estimation
- **Wavelength analysis** for different frequency bands
- **Signal attenuation modeling** through obstacles
- **Interference pattern detection** between overlapping channels

## Controls

### Main Interface
- **🚀 Start LIDAR Scan** - Begin real-time spectrum scanning
- **⏹️ Stop LIDAR Scan** - Pause the scanning process
- **🧹 Clear Point Cloud** - Reset the visualization
- **💾 Save Scan** - Export current data to JSON

### 3D View Controls
- **Mouse drag** - Rotate 3D view
- **Mouse wheel** - Zoom in/out
- **Reset View** - Return to default perspective
- **Top View** - Bird's eye view of networks
- **Side View** - Profile view of height distribution

## Output Data

### Real-time Display
- **📊 Scan Status** - Current scanning progress and statistics
- **📡 Network Details** - Live information about detected networks
- **🎯 Point Cloud Stats** - Total points and scan coverage

### Saved Data
Exported JSON files contain:
- **Network information** (SSID, signal strength, frequency)
- **3D point cloud data** with timestamps
- **Scan parameters** and metadata
- **Analysis results** and statistics

## Technical Details

### Scanning Process
1. **WiFi adapter query** using system commands
2. **Signal strength analysis** and vendor identification
3. **3D coordinate calculation** from RF measurements
4. **Point cloud generation** with temporal tracking
5. **Real-time visualization** update

### Visualization Engine
- **Matplotlib 3D** rendering with hardware acceleration
- **Tkinter GUI** for cross-platform compatibility
- **Threading** for non-blocking real-time updates
- **Memory management** for long-running scans

## Use Cases

### Professional Applications
- **RF site surveys** and spectrum analysis
- **Network planning** and optimization
- **Interference troubleshooting** and mitigation
- **Security assessments** and rogue AP detection

### Educational/Research
- **Electromagnetic wave visualization** and physics education
- **Spectrum utilization studies** and research
- **Network topology mapping** and analysis
- **RF propagation modeling** and validation

## Troubleshooting

### Common Issues
- **No networks detected**: Check WiFi adapter and permissions
- **GUI not starting**: Ensure tkinter is installed (`python -m tkinter`)
- **3D view problems**: Update matplotlib (`pip install --upgrade matplotlib`)
- **Scanning errors**: Run as administrator on Windows

### Performance Tips
- **Close other WiFi tools** to avoid conflicts
- **Limit point cloud size** for better performance
- **Use wired connection** for internet while scanning
- **Clear point cloud periodically** during long scans

## Advanced Features

### Customization
- Modify `scan_radius` for different coverage areas
- Adjust `update_interval` for scan frequency
- Change `colors` dictionary for custom band colors
- Edit `point_cloud_limit` for memory management

### Integration
- Import scan data into GIS software
- Export to CSV for spreadsheet analysis
- Connect to external RF measurement equipment
- Integrate with network management systems

---

**🌊 Experience the invisible world of RF spectrum like never before!**

*This tool transforms your computer into a sophisticated RF spectrum analyzer with LIDAR-style visualization capabilities.*