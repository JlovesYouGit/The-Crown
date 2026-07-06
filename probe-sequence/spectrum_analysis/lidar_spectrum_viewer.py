#!/usr/bin/env python3
"""
Live LIDAR-Style 3D Spectrum Visualizer
Real-time 3D visualization of RF spectrum environment like LIDAR mapping.
"""

import tkinter as tk

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from mpl_toolkits.mplot3d import Axes3D

    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: matplotlib 3D not available: {e}")
    print("Please install with: pip install matplotlib")
    print("Using fallback mode...")
    MATPLOTLIB_AVAILABLE = False

    # Create dummy classes to prevent errors
    class Axes3D:
        pass

    class FigureCanvasTkAgg:
        pass


import json
import os
import sys
import threading
import time

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_wifi_scanner import SpectrumAnalyzer
    from spectrum_grabber.wifi_scanner import WiFiScanError, scan_wifi_cross_platform
except ImportError:
    print("Warning: Could not import spectrum scanning modules")
    scan_wifi_cross_platform = None
    SpectrumAnalyzer = None


class LidarSpectrumViewer:
    """Live LIDAR-style 3D spectrum visualization GUI."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LIDAR-Style Spectrum Viewer - Live 3D RF Environment")
        self.root.geometry("1400x900")
        self.root.configure(bg='black')

        # Data storage
        self.networks = []
        self.scan_history = []
        self.is_scanning = False
        self.scan_thread = None

        # LIDAR-style parameters
        self.scan_angle = 0  # Current scan angle
        self.scan_radius = 100  # Maximum scan radius
        self.point_cloud = []  # LIDAR-style point cloud

        # Colors for different frequency bands
        self.colors = {
            '2.4GHz': '#FF4444',  # Red
            '5GHz': '#4444FF',  # Blue
            '6GHz': '#FF44FF',  # Magenta
            'Unknown': '#FFFFFF',  # White
        }

        self.setup_gui()
        self.setup_3d_plot()

        # Start the update loop
        self.update_display()

    def setup_gui(self):
        """Setup the GUI layout."""
        # Main frame
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel
        control_frame = tk.Frame(main_frame, bg='#1a1a1a', relief=tk.RAISED, bd=2)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        # Title
        title_label = tk.Label(
            control_frame,
            text="🌊 LIDAR-Style Spectrum Viewer",
            font=('Arial', 16, 'bold'),
            fg='#00FF00',
            bg='#1a1a1a',
        )
        title_label.pack(pady=10)

        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#1a1a1a')
        button_frame.pack(pady=5)

        self.scan_button = tk.Button(
            button_frame,
            text="Start LIDAR Scan",
            command=self.toggle_scanning,
            bg='#00AA00',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=15,
        )
        self.scan_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(
            button_frame,
            text="Clear Point Cloud",
            command=self.clear_point_cloud,
            bg='#AA0000',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=15,
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(
            button_frame,
            text="Save Scan",
            command=self.save_scan_data,
            bg='#0000AA',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=15,
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Status and info frame
        info_frame = tk.Frame(main_frame, bg='black')
        info_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        # Left info panel
        left_info = tk.Frame(info_frame, bg='#1a1a1a', relief=tk.RAISED, bd=1)
        left_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(
            left_info, text="📊 Scan Status", font=('Arial', 12, 'bold'), fg='#00FFFF', bg='#1a1a1a'
        ).pack(pady=5)

        self.status_text = tk.Text(
            left_info,
            height=8,
            width=40,
            bg='black',
            fg='#00FF00',
            font=('Courier', 10),
            insertbackground='#00FF00',
        )
        self.status_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Right info panel
        right_info = tk.Frame(info_frame, bg='#1a1a1a', relief=tk.RAISED, bd=1)
        right_info.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(
            right_info,
            text="📡 Network Details",
            font=('Arial', 12, 'bold'),
            fg='#00FFFF',
            bg='#1a1a1a',
        ).pack(pady=5)

        self.network_text = tk.Text(
            right_info,
            height=8,
            width=40,
            bg='black',
            fg='#FFFF00',
            font=('Courier', 10),
            insertbackground='#FFFF00',
        )
        self.network_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # 3D plot frame
        self.plot_frame = tk.Frame(main_frame, bg='black', relief=tk.RAISED, bd=2)
        self.plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def setup_3d_plot(self):
        """Setup the 3D matplotlib plot or fallback display."""
        if not MATPLOTLIB_AVAILABLE:
            # Create fallback display
            self.setup_fallback_display()
            return

        try:
            # Create figure with dark theme
            plt.style.use('dark_background')
            self.fig = plt.figure(figsize=(12, 8), facecolor='black')
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.ax.set_facecolor('black')

            # Setup plot appearance
            self.ax.set_xlabel('Distance East (m)', color='white', fontsize=10)
            self.ax.set_ylabel('Distance North (m)', color='white', fontsize=10)
            self.ax.set_zlabel('Height (m)', color='white', fontsize=10)
            self.ax.set_title(
                'LIDAR-Style RF Spectrum Point Cloud\n🌊 Live 3D Environment Mapping',
                color='#00FFFF',
                fontsize=14,
                fontweight='bold',
            )

            # Set axis colors
            self.ax.xaxis.label.set_color('white')
            self.ax.yaxis.label.set_color('white')
            self.ax.zaxis.label.set_color('white')
            self.ax.tick_params(colors='white')

            # Set limits
            self.ax.set_xlim([-self.scan_radius, self.scan_radius])
            self.ax.set_ylim([-self.scan_radius, self.scan_radius])
            self.ax.set_zlim([-10, 30])

            # Add grid
            self.ax.grid(True, alpha=0.3, color='gray')

            # Embed plot in tkinter
            self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Add toolbar
            toolbar = tk.Frame(self.plot_frame, bg='black')
            toolbar.pack(side=tk.BOTTOM, fill=tk.X)

            # Custom toolbar buttons
            tk.Button(
                toolbar,
                text="Reset View",
                command=self.reset_view,
                bg='#333333',
                fg='white',
                font=('Arial', 10),
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                toolbar,
                text="Top View",
                command=self.top_view,
                bg='#333333',
                fg='white',
                font=('Arial', 10),
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                toolbar,
                text="Side View",
                command=self.side_view,
                bg='#333333',
                fg='white',
                font=('Arial', 10),
            ).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            print(f"Error setting up 3D plot: {e}")
            self.setup_fallback_display()

    def setup_fallback_display(self):
        """Setup fallback display when matplotlib is not available."""
        # Create a simple text-based display
        fallback_label = tk.Label(
            self.plot_frame,
            text="🌊 LIDAR-Style Spectrum Viewer\n\n"
            + "⚠️ 3D Visualization Unavailable\n"
            + "matplotlib not installed\n\n"
            + "Install with: pip install matplotlib\n\n"
            + "📊 Network data will still be displayed\n"
            + "in the panels above",
            font=('Arial', 14),
            fg='#00FFFF',
            bg='black',
            justify=tk.CENTER,
        )
        fallback_label.pack(expand=True, fill=tk.BOTH)

        # Add install button
        install_frame = tk.Frame(self.plot_frame, bg='black')
        install_frame.pack(pady=20)

        tk.Button(
            install_frame,
            text="📥 Install matplotlib",
            command=self.install_matplotlib,
            bg='#0066CC',
            fg='white',
            font=('Arial', 12, 'bold'),
        ).pack()

    def install_matplotlib(self):
        """Attempt to install matplotlib."""
        import subprocess
        import sys

        try:
            self.update_status("📥 Installing matplotlib...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "matplotlib"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.update_status("✅ matplotlib installed successfully!")
                self.update_status("🔄 Please restart the application to use 3D visualization")
            else:
                self.update_status(f"❌ Installation failed: {result.stderr}")
        except Exception as e:
            self.update_status(f"❌ Installation error: {e}")

    def toggle_scanning(self):
        """Toggle LIDAR-style scanning."""
        if not self.is_scanning:
            self.start_scanning()
        else:
            self.stop_scanning()

    def start_scanning(self):
        """Start the LIDAR-style scanning process."""
        self.is_scanning = True
        self.scan_button.config(text="Stop LIDAR Scan", bg='#AA0000')

        # Start scanning thread
        self.scan_thread = threading.Thread(target=self.lidar_scan_loop, daemon=True)
        self.scan_thread.start()

        self.update_status("🚀 LIDAR scan started...\n📡 Sweeping RF spectrum...")

    def stop_scanning(self):
        """Stop the scanning process."""
        self.is_scanning = False
        self.scan_button.config(text="Start LIDAR Scan", bg='#00AA00')
        self.update_status("⏹️ LIDAR scan stopped")

    def lidar_scan_loop(self):
        """Main LIDAR scanning loop - simulates rotating LIDAR sweep."""
        while self.is_scanning:
            try:
                # Perform WiFi scan
                if scan_wifi_cross_platform:
                    networks = scan_wifi_cross_platform()
                    self.process_scan_data(networks)
                else:
                    # Simulate data if modules not available
                    self.simulate_scan_data()

                # Update scan angle (LIDAR rotation simulation)
                self.scan_angle = (self.scan_angle + 15) % 360

                # Wait before next scan
                time.sleep(2)

            except Exception as e:
                self.update_status(f"❌ Scan error: {e}")
                time.sleep(5)

    def process_scan_data(self, networks):
        """Process real scan data into LIDAR-style points."""
        self.networks = []
        new_points = []

        for i, ap in enumerate(networks):
            # Convert to our format
            network = {
                'ssid': ap.ssid,
                'bssid': ap.bssid,
                'signal_percent': ap.signal_percent,
                'frequency_mhz': ap.frequency_mhz,
                'band': ap.band,
                'channel': ap.channel,
                'vendor': getattr(ap, 'vendor', 'Unknown'),
            }
            self.networks.append(network)

            # Create LIDAR-style point
            point = self.create_lidar_point(network, i)
            new_points.append(point)

        # Add to point cloud
        self.point_cloud.extend(new_points)

        # Limit point cloud size (simulate LIDAR memory)
        if len(self.point_cloud) > 1000:
            self.point_cloud = self.point_cloud[-1000:]

        self.update_status(
            f"📡 Scan complete: {len(networks)} networks\n🎯 Point cloud: {len(self.point_cloud)} points"
        )

    def simulate_scan_data(self):
        """Simulate scan data for demo purposes."""
        # Create simulated networks
        simulated_networks = [
            {
                'ssid': 'Home_WiFi_5G',
                'signal_percent': 95,
                'frequency_mhz': 5180,
                'band': '5GHz',
                'channel': 36,
            },
            {
                'ssid': 'Neighbor_2G',
                'signal_percent': 65,
                'frequency_mhz': 2412,
                'band': '2.4GHz',
                'channel': 1,
            },
            {
                'ssid': 'Office_Net',
                'signal_percent': 45,
                'frequency_mhz': 5745,
                'band': '5GHz',
                'channel': 149,
            },
            {
                'ssid': 'Mobile_Hotspot',
                'signal_percent': 30,
                'frequency_mhz': 2462,
                'band': '2.4GHz',
                'channel': 11,
            },
        ]

        self.networks = simulated_networks
        new_points = []

        for i, network in enumerate(simulated_networks):
            point = self.create_lidar_point(network, i)
            new_points.append(point)

        self.point_cloud.extend(new_points)

        if len(self.point_cloud) > 1000:
            self.point_cloud = self.point_cloud[-1000:]

        self.update_status(
            f"📡 Simulated scan: {len(simulated_networks)} networks\n🎯 Point cloud: {len(self.point_cloud)} points"
        )

    def create_lidar_point(self, network, index):
        """Create a LIDAR-style point from network data."""
        # Estimate distance from signal strength
        signal = network['signal_percent']
        if signal >= 90:
            distance = np.random.uniform(5, 15)
        elif signal >= 70:
            distance = np.random.uniform(15, 40)
        elif signal >= 50:
            distance = np.random.uniform(40, 70)
        else:
            distance = np.random.uniform(70, 100)

        # LIDAR-style angular positioning
        angle = (self.scan_angle + index * 45) % 360
        elevation = np.random.uniform(-10, 20)  # Height variation

        # Convert to Cartesian coordinates
        x = distance * np.cos(np.radians(angle))
        y = distance * np.sin(np.radians(angle))
        z = elevation

        return {
            'x': x,
            'y': y,
            'z': z,
            'network': network,
            'timestamp': time.time(),
            'scan_angle': self.scan_angle,
            'distance': distance,
        }

    def update_display(self):
        """Update the 3D display with current point cloud."""
        if hasattr(self, 'ax'):
            # Clear previous plot
            self.ax.clear()

            # Redraw axes and labels
            self.ax.set_xlabel('Distance East (m)', color='white', fontsize=10)
            self.ax.set_ylabel('Distance North (m)', color='white', fontsize=10)
            self.ax.set_zlabel('Height (m)', color='white', fontsize=10)
            self.ax.set_title(
                'LIDAR-Style RF Spectrum Point Cloud\n🌊 Live 3D Environment Mapping',
                color='#00FFFF',
                fontsize=14,
                fontweight='bold',
            )

            # Set limits
            self.ax.set_xlim([-self.scan_radius, self.scan_radius])
            self.ax.set_ylim([-self.scan_radius, self.scan_radius])
            self.ax.set_zlabel([-10, 30])

            # Plot our position
            self.ax.scatter(
                0,
                0,
                0,
                color='gold',
                s=300,
                marker='*',
                label='Scanner Position',
                edgecolors='black',
                linewidth=2,
            )

            # Plot point cloud
            if self.point_cloud:
                # Group points by frequency band
                bands = {'2.4GHz': [], '5GHz': [], '6GHz': [], 'Unknown': []}

                for point in self.point_cloud:
                    band = point['network']['band']
                    bands[band].append(point)

                # Plot each band with different colors
                for band, points in bands.items():
                    if points:
                        xs = [p['x'] for p in points]
                        ys = [p['y'] for p in points]
                        zs = [p['z'] for p in points]
                        signals = [p['network']['signal_percent'] for p in points]

                        # Size based on signal strength
                        sizes = [max(20, s) for s in signals]

                        self.ax.scatter(
                            xs,
                            ys,
                            zs,
                            c=self.colors[band],
                            s=sizes,
                            alpha=0.7,
                            label=f'{band} Networks',
                            edgecolors='white',
                            linewidth=0.5,
                        )

            # Add LIDAR scan line (current scan direction)
            scan_x = self.scan_radius * np.cos(np.radians(self.scan_angle))
            scan_y = self.scan_radius * np.sin(np.radians(self.scan_angle))
            self.ax.plot(
                [0, scan_x],
                [0, scan_y],
                [0, 0],
                color='#00FF00',
                linewidth=3,
                alpha=0.8,
                label='LIDAR Beam',
            )

            # Add grid and styling
            self.ax.grid(True, alpha=0.3, color='gray')
            self.ax.legend(loc='upper left', bbox_to_anchor=(0, 1))

            # Update canvas
            self.canvas.draw()

            # Update network info
            self.update_network_info()

        # Schedule next update
        self.root.after(1000, self.update_display)  # Update every second

    def update_status(self, message):
        """Update status text."""
        if hasattr(self, 'status_text'):
            self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
            self.status_text.see(tk.END)

            # Limit text length
            lines = self.status_text.get("1.0", tk.END).split('\n')
            if len(lines) > 20:
                self.status_text.delete("1.0", "2.0")

    def update_network_info(self):
        """Update network information display."""
        if hasattr(self, 'network_text'):
            self.network_text.delete("1.0", tk.END)

            if self.networks:
                info = "📡 DETECTED NETWORKS:\n\n"
                for i, net in enumerate(self.networks, 1):
                    band_icon = "🔴" if net['band'] == '2.4GHz' else "🔵"
                    info += f"{i}. {net['ssid']} {band_icon}\n"
                    info += f"   Signal: {net['signal_percent']}%\n"
                    info += f"   Channel: {net['channel']} ({net['frequency_mhz']} MHz)\n"
                    info += f"   Band: {net['band']}\n\n"

                info += f"Total Point Cloud: {len(self.point_cloud)} points\n"
                info += f"Scan Angle: {self.scan_angle}°"

                self.network_text.insert("1.0", info)

    def clear_point_cloud(self):
        """Clear the LIDAR point cloud."""
        self.point_cloud = []
        self.update_status("🧹 Point cloud cleared")

    def save_scan_data(self):
        """Save current scan data to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"lidar_scan_{timestamp}.json"

        data = {
            'timestamp': timestamp,
            'networks': self.networks,
            'point_cloud': self.point_cloud,
            'scan_parameters': {
                'scan_radius': self.scan_radius,
                'current_angle': self.scan_angle,
                'total_points': len(self.point_cloud),
            },
        }

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            self.update_status(f"💾 Scan saved: {filename}")
        except Exception as e:
            self.update_status(f"❌ Save error: {e}")

    def reset_view(self):
        """Reset 3D view to default."""
        self.ax.view_init(elev=20, azim=45)
        self.canvas.draw()

    def top_view(self):
        """Set top-down view."""
        self.ax.view_init(elev=90, azim=0)
        self.canvas.draw()

    def side_view(self):
        """Set side view."""
        self.ax.view_init(elev=0, azim=0)
        self.canvas.draw()

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main function to start the LIDAR spectrum viewer."""
    print("🌊 Starting LIDAR-Style Spectrum Viewer...")

    try:
        app = LidarSpectrumViewer()
        app.run()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
