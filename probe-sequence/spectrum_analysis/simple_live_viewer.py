#!/usr/bin/env python3
"""
Simple Live Spectrum Viewer - Stable Windows App
Real-time WiFi spectrum visualization without complex 3D plotting.
"""

import math
import os
import sys
import threading
import time
import tkinter as tk

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from spectrum_grabber.wifi_scanner import WiFiScanError, scan_wifi_cross_platform
except ImportError:
    scan_wifi_cross_platform = None
    WiFiScanError = Exception

# Import our modular components
from .gui_components import SpectrumGUI
from .interference_analyzer import InterferenceAnalyzer
from .lidar_mapper import LidarMapper
from .network_analyzer import NetworkAnalyzer
from .network_details import NetworkDetailsGenerator
from .security_assessor import SecurityAssessor


class SimpleLiveViewer:
    """Simple live spectrum viewer with LIDAR-style room mapping."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌊 RF Spectrum LIDAR Room Mapper")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')

        # Data
        self.networks = []
        self.is_scanning = False
        self.scan_count = 0

        # Initialize analysis modules
        self.network_analyzer = NetworkAnalyzer()
        self.security_assessor = SecurityAssessor()
        self.lidar_mapper = LidarMapper()

        # Initialize interference analyzer (will be updated with networks)
        self.interference_analyzer = InterferenceAnalyzer([])

        # Initialize details generator
        self.details_generator = NetworkDetailsGenerator(
            self.network_analyzer, self.security_assessor, self.interference_analyzer
        )

        # Initialize GUI components
        self.gui = SpectrumGUI(self)

        # Zoom and pan controls
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        # Colors for bands
        self.band_colors = {'2.4GHz': '#FF4444', '5GHz': '#4444FF', '6GHz': '#FF44FF'}

        self.gui.setup_gui()
        self.start_auto_scan()

    def start_auto_scan(self):
        """Start automatic scanning in background."""
        self.is_scanning = True
        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()

    def scan_loop(self):
        """Main scanning loop."""
        while self.is_scanning:
            try:
                self.update_status("🟡 Scanning...", "#FFFF00")

                if scan_wifi_cross_platform:
                    # Real scan
                    access_points = scan_wifi_cross_platform()
                    self.networks = []
                    for ap in access_points:
                        network = {
                            'ssid': ap.ssid,
                            'bssid': ap.bssid,
                            'signal_percent': ap.signal_percent,
                            'channel': ap.channel,
                            'frequency_mhz': ap.frequency_mhz,
                            'band': ap.band,
                            'auth': ap.auth,
                            'cipher': ap.cipher,
                        }
                        self.networks.append(network)
                    # Enrich with stable ID and history
                    self.network_analyzer.enrich_with_history(self.networks)
                else:
                    # Simulate data for demo
                    self.simulate_networks()
                    # Enrich simulated networks too
                    self.network_analyzer.enrich_with_history(self.networks)

                self.scan_count += 1
                self.update_display()
                self.update_status(f"🟢 Active - Found {len(self.networks)} networks", "#00FF00")

                time.sleep(3)  # Scan every 3 seconds

            except Exception as e:
                self.update_status(f"🔴 Error: {str(e)[:50]}...", "#FF4444")
                time.sleep(5)

    def simulate_networks(self):
        """Simulate network data for demo."""
        import random

        base_networks = [
            {'ssid': 'Home_WiFi_5G', 'channel': 36, 'band': '5GHz'},
            {'ssid': 'Neighbor_2G', 'channel': 1, 'band': '2.4GHz'},
            {'ssid': 'Office_Network', 'channel': 149, 'band': '5GHz'},
            {'ssid': 'Mobile_Hotspot', 'channel': 11, 'band': '2.4GHz'},
            {'ssid': 'Guest_Network', 'channel': 6, 'band': '2.4GHz'},
        ]

        self.networks = []
        for net in base_networks:
            if random.random() > 0.3:  # Sometimes networks disappear
                network = {
                    'ssid': net['ssid'],
                    'bssid': f"aa:bb:cc:dd:ee:{random.randint(10, 99)}",
                    'signal_percent': random.randint(30, 100),
                    'channel': net['channel'],
                    'frequency_mhz': 2412 + (net['channel'] - 1) * 5
                    if net['band'] == '2.4GHz'
                    else 5000 + net['channel'] * 5,
                    'band': net['band'],
                    'auth': 'WPA2',
                    'cipher': 'AES',
                }
                self.networks.append(network)

    def update_display(self):
        """Update all display elements."""
        self.root.after(0, self._update_display_safe)

    def _update_display_safe(self):
        """Thread-safe display update."""
        # Update network list
        self.network_listbox.delete(0, tk.END)

        # Sort by signal strength
        sorted_networks = sorted(self.networks, key=lambda x: x['signal_percent'], reverse=True)

        # Assign stable IDs and calculate distances
        for _i, net in enumerate(sorted_networks):
            # Use stable custom ID based on BSSID/band/channel
            custom_id = net.get('custom_id') or self.get_stable_id(net)
            net['custom_id'] = custom_id

            # Calculate distance estimate
            distance = self.network_analyzer.calculate_network_distance(
                net['signal_percent'], net['frequency_mhz']
            )
            net['distance_estimate'] = distance

            # Create display text with ID and distance
            "🔴" if net['band'] == '2.4GHz' else "🔵" if net['band'] == '5GHz' else "🟣"
            signal_bars = "█" * (net['signal_percent'] // 20) + "░" * (
                5 - net['signal_percent'] // 20
            )

            # Format: [ID] SSID | Signal | Distance | Channel
            display_text = f"[{custom_id}] {net['ssid'][:15]:15} {signal_bars} {net['signal_percent']:3d}% {distance:>6} Ch{net['channel']:2d}"
            self.network_listbox.insert(tk.END, display_text)

        # Update spectrum visualization
        self.draw_spectrum()

        # Update scan count
        self.scan_count_label.config(text=f"Scans: {self.scan_count}")

    def get_stable_id(self, network: dict) -> str:
        """Return a stable human-friendly ID derived from BSSID/band/channel."""
        return self.network_analyzer.get_stable_id(network)

    def draw_spectrum(self):
        """Draw LIDAR-style room mapping visualization."""
        self.canvas.delete("all")

        # Get canvas dimensions
        width = self.canvas.winfo_width() or 600
        height = self.canvas.winfo_height() or 500

        # Apply zoom and pan transformations
        center_x = (width // 2) + self.pan_x
        center_y = (height // 2) + self.pan_y

        if not self.networks:
            self.canvas.create_text(
                center_x,
                center_y,
                text="🔍 Scanning for networks...\nMove around to map environment",
                fill="#666666",
                font=('Arial', 14),
                justify=tk.CENTER,
            )
            return

        # Update environment mapping based on RF signals
        self.lidar_mapper.update_environment_mapping(self.networks)

        if self.mapping_mode.get():
            # LIDAR-style room mapping mode
            self.lidar_mapper.draw_lidar_room_mapping(
                self.canvas, center_x, center_y, width, height, self.zoom_level
            )
            self.draw_lidar_network_points(center_x, center_y, self.zoom_level)
        else:
            # Traditional spectrum view
            self.draw_traditional_spectrum(center_x, center_y, width, height)

        # Draw UI elements
        self.gui.draw_mapping_ui(
            self.canvas,
            width,
            height,
            self.zoom_level,
            self.lidar_mapper.environment_points,
            self.lidar_mapper.wave_reflections,
            self.mapping_mode.get(),
        )

    def on_network_select(self, event):
        """Handle network selection in listbox."""
        selection = self.network_listbox.curselection()
        if selection:
            index = selection[0]
            # Get the sorted networks (same order as displayed)
            sorted_networks = sorted(self.networks, key=lambda x: x['signal_percent'], reverse=True)

            if index < len(sorted_networks):
                network = sorted_networks[index]

                # Ensure network has all required properties
                if 'custom_id' not in network:
                    network['custom_id'] = self.network_analyzer.get_stable_id(network)
                if 'distance_estimate' not in network:
                    network['distance_estimate'] = self.network_analyzer.calculate_network_distance(
                        network['signal_percent'], network['frequency_mhz']
                    )

                # Show details
                self.show_network_details(network)

                # Debug output
                print(f"Selected network: {network['ssid']} (Index: {index})")
            else:
                print(f"Index {index} out of range for {len(sorted_networks)} networks")

    def on_network_click(self, event):
        """Handle direct click on network listbox."""
        # Get the clicked item index
        index = self.network_listbox.nearest(event.y)
        if index >= 0:
            # Select the item
            self.network_listbox.selection_clear(0, tk.END)
            self.network_listbox.selection_set(index)
            self.network_listbox.activate(index)

            # Trigger the selection handler
            sorted_networks = sorted(self.networks, key=lambda x: x['signal_percent'], reverse=True)
            if index < len(sorted_networks):
                network = sorted_networks[index]

                # Ensure network has all required properties
                if 'custom_id' not in network:
                    network['custom_id'] = self.network_analyzer.get_stable_id(network)
                if 'distance_estimate' not in network:
                    network['distance_estimate'] = self.network_analyzer.calculate_network_distance(
                        network['signal_percent'], network['frequency_mhz']
                    )

                # Show details immediately
                self.show_network_details(network)
                print(f"Direct click on network: {network['ssid']}")

    def show_network_details(self, network):
        """Show comprehensive information about selected network."""
        details = self.details_generator.generate_network_details(network, self.networks)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)

    def update_status(self, message, color):
        """Update status label."""
        self.root.after(0, lambda: self.status_label.config(text=message, fg=color))

    def draw_lidar_room_mapping(self, center_x, center_y, width, height):
        """Draw LIDAR-style room mapping visualization."""
        # Scale factor for zoom
        scale = self.zoom_level

        # Draw scanning grid (like VR room setup)
        self.draw_scanning_grid(center_x, center_y, scale)

        # Draw our position
        self.draw_scanner_position(center_x, center_y, scale)

        # Draw detected obstacles and walls
        self.draw_environment_obstacles(center_x, center_y, scale)

        # Draw RF wave propagation paths
        self.draw_rf_wave_paths(center_x, center_y, scale)

        # Draw network positions with LIDAR-style points
        self.draw_lidar_network_points(center_x, center_y, scale)

        # Draw room boundaries (estimated)
        self.draw_estimated_room_boundaries(center_x, center_y, scale)

    def draw_scanning_grid(self, center_x, center_y, scale):
        """Draw VR-style scanning grid."""
        grid_size = int(30 * scale)
        grid_color = "#1a4d1a"  # Dark green like VR setup

        # Draw grid lines
        for i in range(-10, 11):
            x = center_x + i * grid_size
            y = center_y + i * grid_size

            # Vertical lines
            if 0 <= x <= self.canvas.winfo_width():
                self.canvas.create_line(
                    x, 0, x, self.canvas.winfo_height(), fill=grid_color, width=1, dash=(2, 4)
                )

            # Horizontal lines
            if 0 <= y <= self.canvas.winfo_height():
                self.canvas.create_line(
                    0, y, self.canvas.winfo_width(), y, fill=grid_color, width=1, dash=(2, 4)
                )

        # Draw range circles
        for radius in [50, 100, 150]:
            scaled_radius = int(radius * scale)
            self.canvas.create_oval(
                center_x - scaled_radius,
                center_y - scaled_radius,
                center_x + scaled_radius,
                center_y + scaled_radius,
                outline="#2d5a2d",
                width=1,
                dash=(3, 3),
            )

    def draw_scanner_position(self, center_x, center_y, scale):
        """Draw our scanner position like VR headset."""
        size = int(12 * scale)

        # Scanner body (like VR headset)
        self.canvas.create_oval(
            center_x - size,
            center_y - size,
            center_x + size,
            center_y + size,
            fill="#00FF00",
            outline="#FFFFFF",
            width=2,
        )

        # Scanner direction indicator
        self.canvas.create_line(
            center_x,
            center_y,
            center_x,
            center_y - int(20 * scale),
            fill="#00FF00",
            width=3,
            arrow=tk.LAST,
        )

        # Scanner label
        self.canvas.create_text(
            center_x,
            center_y - int(35 * scale),
            text="RF SCANNER",
            fill="#00FF00",
            font=('Arial', int(8 * scale), 'bold'),
        )

    def draw_environment_obstacles(self, center_x, center_y, scale):
        """Draw detected obstacles and walls."""
        for obstacle in self.environment_points:
            x = center_x + int(obstacle['x'] * scale)
            y = center_y + int(obstacle['y'] * scale)

            # Color based on obstacle type
            if obstacle['type'] == 'wall':
                color = "#FF6666"  # Red for walls
                size = int(8 * scale)
            else:
                color = "#FFAA66"  # Orange for furniture
                size = int(6 * scale)

            # Draw obstacle point
            self.canvas.create_oval(
                x - size // 2,
                y - size // 2,
                x + size // 2,
                y + size // 2,
                fill=color,
                outline="#FFFFFF",
                width=1,
            )

            # Confidence indicator
            confidence_radius = int(obstacle['confidence'] * 15 * scale)
            self.canvas.create_oval(
                x - confidence_radius,
                y - confidence_radius,
                x + confidence_radius,
                y + confidence_radius,
                outline=color,
                width=1,
                dash=(1, 2),
            )

    def draw_rf_wave_paths(self, center_x, center_y, scale):
        """Draw RF wave propagation paths."""
        for reflection in self.wave_reflections:
            angle_rad = math.radians(reflection['angle'])
            distance = int(reflection['distance'] * scale)

            end_x = center_x + distance * math.cos(angle_rad)
            end_y = center_y + distance * math.sin(angle_rad)

            # Wave path color based on frequency
            if reflection['frequency'] < 2500:
                color = "#FF4444"  # Red for 2.4GHz
            else:
                color = "#4444FF"  # Blue for 5GHz

            # Draw wave path
            self.canvas.create_line(
                center_x, center_y, end_x, end_y, fill=color, width=2, dash=(4, 2)
            )

            # Draw reflection point
            self.canvas.create_oval(
                end_x - 4, end_y - 4, end_x + 4, end_y + 4, fill=color, outline="#FFFFFF", width=1
            )

    def draw_lidar_network_points(self, center_x, center_y, scale):
        """Draw networks as LIDAR-style point cloud."""
        for i, network in enumerate(self.networks):
            signal = network['signal_percent']

            # Position based on signal strength and channel
            angle = (network['channel'] * 30 + i * 45) % 360
            angle_rad = math.radians(angle)

            # Distance inversely related to signal strength
            distance = int((100 - signal + 20) * scale)

            x = center_x + distance * math.cos(angle_rad)
            y = center_y + distance * math.sin(angle_rad)

            # Color and size based on band and signal
            if network['band'] == '2.4GHz':
                color = "#FF4444"
            else:
                color = "#4444FF"

            point_size = max(3, int(signal / 20 * scale))

            # Draw network point
            self.canvas.create_oval(
                x - point_size,
                y - point_size,
                x + point_size,
                y + point_size,
                fill=color,
                outline="#FFFFFF",
                width=1,
            )

            # Draw signal strength indicator
            for ring in range(1, 4):
                ring_radius = point_size + ring * int(3 * scale)
                alpha = max(0.1, (signal - ring * 20) / 100)
                if alpha > 0:
                    self.canvas.create_oval(
                        x - ring_radius,
                        y - ring_radius,
                        x + ring_radius,
                        y + ring_radius,
                        outline=color,
                        width=1,
                        dash=(1, 3),
                    )

            # Network label for strong signals
            if signal > 60:
                label_y = y - int(15 * scale)
                self.canvas.create_text(
                    x,
                    label_y,
                    text=network['ssid'][:8],
                    fill="#FFFFFF",
                    font=('Arial', int(7 * scale)),
                )

    def draw_estimated_room_boundaries(self, center_x, center_y, scale):
        """Draw estimated room boundaries based on RF analysis."""
        if len(self.environment_points) < 3:
            return

        # Simple room boundary estimation
        wall_points = [p for p in self.environment_points if p['type'] == 'wall']

        if len(wall_points) >= 3:
            # Draw estimated walls
            for i in range(len(wall_points)):
                p1 = wall_points[i]
                p2 = wall_points[(i + 1) % len(wall_points)]

                x1 = center_x + int(p1['x'] * scale)
                y1 = center_y + int(p1['y'] * scale)
                x2 = center_x + int(p2['x'] * scale)
                y2 = center_y + int(p2['y'] * scale)

                self.canvas.create_line(x1, y1, x2, y2, fill="#666666", width=2, dash=(5, 5))

    def draw_traditional_spectrum(self, center_x, center_y, width, height):
        """Draw traditional spectrum view."""
        max_radius = int(min(width, height) // 3 * self.zoom_level)
        self.gui.draw_3d_environment(self.canvas, center_x, center_y, max_radius, width, height)

        for i, net in enumerate(self.networks):
            self.gui.draw_network_in_3d(self.canvas, net, i, center_x, center_y, max_radius)

        self.gui.draw_3d_legend(self.canvas, width, height)

    def draw_mapping_ui(self, width, height):
        """Draw mapping UI elements."""
        # Zoom indicator
        zoom_text = f"Zoom: {int(self.zoom_level * 100)}%"
        self.canvas.create_text(width - 80, 20, text=zoom_text, fill="#00FFFF", font=('Arial', 10))

        # Mapping stats
        stats_text = (
            f"Obstacles: {len(self.environment_points)}\nReflections: {len(self.wave_reflections)}"
        )
        self.canvas.create_text(
            20, height - 40, text=stats_text, anchor="w", fill="#CCCCCC", font=('Arial', 9)
        )

        # Mode indicator
        mode_text = "🗺️ LIDAR Mapping Mode" if self.mapping_mode.get() else "📊 Traditional View"
        self.canvas.create_text(
            width // 2, 20, text=mode_text, fill="#00FFFF", font=('Arial', 12, 'bold')
        )

    # Mouse and zoom control methods
    def zoom_in(self):
        """Zoom in the view."""
        self.zoom_level = min(3.0, self.zoom_level * 1.2)
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.draw_spectrum()

    def zoom_out(self):
        """Zoom out the view."""
        self.zoom_level = max(0.3, self.zoom_level / 1.2)
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.draw_spectrum()

    def reset_view(self):
        """Reset zoom and pan to default."""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.zoom_label.config(text="100%")
        self.draw_spectrum()

    def toggle_mapping_mode(self):
        """Toggle between LIDAR mapping and traditional view."""
        self.draw_spectrum()

    def on_canvas_click(self, event):
        """Handle canvas click for panning."""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def on_canvas_drag(self, event):
        """Handle canvas drag for panning."""
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y

        self.pan_x += dx
        self.pan_y += dy

        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        self.draw_spectrum()

    def on_canvas_scroll(self, event):
        """Handle mouse wheel for zooming."""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def on_canvas_right_click(self, event):
        """Handle right click for context menu."""
        # Clear environment mapping
        self.environment_points.clear()
        self.wave_reflections.clear()
        self.draw_spectrum()

    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main function."""
    print("🌊 Starting Simple Live Spectrum Viewer...")

    try:
        app = SimpleLiveViewer()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
