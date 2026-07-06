#!/usr/bin/env python3
"""
Enhanced Live Spectrum Viewer - Advanced RF Analysis
Integrates advanced spectrum analysis, historical tracking, and data export capabilities.
"""

import csv
import ctypes
import json
import os
import sys
import threading
import time
import tkinter as tk
from collections import defaultdict, deque
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_wifi_scanner import SpectrumAnalyzer, enhanced_wifi_scan
    from spectrum_grabber.wifi_scanner import WiFiScanError, scan_wifi_cross_platform
except ImportError:
    scan_wifi_cross_platform = None
    WiFiScanError = Exception
    SpectrumAnalyzer = None
    enhanced_wifi_scan = None

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class EnhancedLiveViewer:
    """Enhanced live spectrum viewer with advanced analysis capabilities."""

    def __init__(self):
        # Windows app integration before creating Tk root
        self._set_windows_app_integration()

        self.root = tk.Tk()
        self.root.title("🌊 Enhanced RF Spectrum Analyzer")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#1a1a1a')
        # Native app polish
        try:
            self.root.state('zoomed')  # Maximize on Windows
        except Exception:
            pass
        self.root.option_add('*tearOff', False)

        # App-wide theme state and style
        self.current_theme = 'dark'
        self.setup_style()
        self.setup_menubar()

        # Initialize data structures
        self.networks = []
        self.network_history = defaultdict(list)  # Track changes over time
        self.scan_count = 0
        self.is_scanning = False
        self.scan_thread = None
        # Stable ID and per-BSSID history registry
        self.network_registry = {}  # bssid -> {first_seen, last_seen, detection_count, stable_id}

        # Advanced analysis data
        self.spectrum_analyzer = SpectrumAnalyzer() if SpectrumAnalyzer else None
        self.interference_map = {}
        self.channel_optimization = {}
        self.security_assessment = {}

        # Historical data
        self.history_window = 24  # hours
        self.export_data = []

        # Visualization settings
        self.view_mode = tk.StringVar(value="spectrum")
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = 5.0  # seconds

        self.setup_gui()
        self.start_auto_scan()

    def setup_style(self):
        """Configure ttk style for dark/light themes."""
        style = ttk.Style(self.root)
        # Use a theme that allows color overrides
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        if self.current_theme == 'dark':
            self.apply_dark_theme(style)
        else:
            self.apply_light_theme(style)

    def apply_dark_theme(self, style: ttk.Style):
        """Apply a dark theme palette."""
        bg = '#1a1a1a'
        panel = '#2a2a2a'
        fg = '#e6e6e6'
        self.root.configure(bg=bg)
        style.configure('.', background=panel, foreground=fg, fieldbackground=panel)
        style.configure('TFrame', background=panel)
        style.configure('TLabel', background=panel, foreground=fg)
        style.configure('TButton', background=panel, foreground=fg)
        style.configure('TNotebook', background=bg)
        style.configure('TNotebook.Tab', background=panel, foreground=fg)
        style.map('TButton', background=[('active', '#3a3a3a')])

    def apply_light_theme(self, style: ttk.Style):
        """Apply a light theme palette."""
        bg = '#f5f5f5'
        panel = '#ffffff'
        fg = '#222222'
        self.root.configure(bg=bg)
        style.configure('.', background=panel, foreground=fg, fieldbackground=panel)
        style.configure('TFrame', background=panel)
        style.configure('TLabel', background=panel, foreground=fg)
        style.configure('TButton', background=panel, foreground=fg)
        style.configure('TNotebook', background=bg)
        style.configure('TNotebook.Tab', background=panel, foreground=fg)

    def setup_menubar(self):
        """Create application menubar with File/View/Help."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export...", command=self.export_scan_data)
        file_menu.add_command(label="Import...", command=self.import_scan_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def toggle_theme(self):
        """Switch between dark and light themes."""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.setup_style()
        # Force refresh of views to redraw with new palette
        self.update_visualizations()

    def show_about(self):
        """Display About dialog."""
        messagebox.showinfo(
            "About",
            "Enhanced RF Spectrum Analyzer\n"
            "Real-time WiFi analysis with interference, security, and history views.",
        )

    def open_settings(self):
        """Open a basic settings dialog."""
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("420x220")
        frm = ttk.Frame(win, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Auto-refresh interval (seconds):").pack(anchor='w')
        var = tk.DoubleVar(value=self.refresh_interval)
        spin = ttk.Spinbox(frm, from_=1, to=60, textvariable=var, width=8)
        spin.pack(anchor='w', pady=(0, 10))

        def save():
            try:
                self.refresh_interval = float(var.get())
                win.destroy()
            except Exception:
                win.destroy()

        ttk.Button(frm, text="Save", command=save).pack(anchor='e')

    def import_scan_data(self):
        """Import scan data from JSON/CSV exports."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            if filename.endswith('.json'):
                with open(filename, encoding='utf-8') as f:
                    data = json.load(f)
                # Support both export format and raw list
                networks = data.get('networks') if isinstance(data, dict) else data
            else:
                networks = []
                with open(filename, encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Normalize numeric fields
                        for k in ['signal_percent', 'channel', 'frequency_mhz']:
                            if k in row and row[k] not in (None, ''):
                                try:
                                    row[k] = int(float(row[k]))
                                except Exception:
                                    pass
                        networks.append(row)
            # Apply imported data
            self.networks = []
            for net in networks:
                # Minimal normalized mapping
                network = {
                    'ssid': net.get('ssid', 'Unknown'),
                    'bssid': net.get('bssid', ''),
                    'signal_percent': int(net.get('signal_percent', 0) or 0),
                    'channel': int(net.get('channel', 0) or 0),
                    'frequency_mhz': int(net.get('frequency_mhz', 0) or 0),
                    'band': net.get('band', 'Unknown'),
                    'auth': net.get('auth', 'Unknown'),
                    'cipher': net.get('cipher', 'Unknown'),
                    'timestamp': net.get('timestamp', datetime.now().isoformat()),
                }
                self.networks.append(network)
                self.update_network_history(network)
            self.update_display()
            messagebox.showinfo(
                "Import",
                f"Imported {len(self.networks)} networks from {os.path.basename(filename)}",
            )
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {e}")

    def setup_topbar(self, parent_root: tk.Tk):
        """Top toolbar with common actions for an app-like feel."""
        bar = ttk.Frame(parent_root)
        bar.pack(fill=tk.X, padx=8, pady=(6, 4))
        title = ttk.Label(bar, text="🌊 Enhanced RF Spectrum Analyzer", font=('Arial', 14, 'bold'))
        title.pack(side=tk.LEFT)
        btns = ttk.Frame(bar)
        btns.pack(side=tk.RIGHT)
        ttk.Button(btns, text="Start/Stop Scan", command=self.toggle_scanning).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns, text="Enhanced Scan", command=self.start_enhanced_scan).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns, text="Export", command=self.export_scan_data).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Settings", command=self.open_settings).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Theme", command=self.toggle_theme).pack(side=tk.LEFT, padx=4)

    def setup_sidebar(self, parent):
        """Left navigation sidebar with quick view switching."""
        sidebar = ttk.Frame(parent)
        sidebar.pack(fill=tk.X, padx=5, pady=(5, 8))
        ttk.Label(sidebar, text="Navigation", font=('Arial', 11, 'bold')).pack(
            anchor='w', pady=(0, 4)
        )
        ttk.Button(
            sidebar, text="Spectrum", command=lambda: self.notebook.select(self.spectrum_frame)
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            sidebar,
            text="Interference",
            command=lambda: self.notebook.select(self.interference_frame),
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            sidebar, text="Security", command=lambda: self.notebook.select(self.security_frame)
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            sidebar, text="Historical", command=lambda: self.notebook.select(self.historical_frame)
        ).pack(fill=tk.X, pady=2)

    def setup_gui(self):
        """Setup the enhanced GUI with multiple panels."""
        # Top toolbar
        self.setup_topbar(self.root)
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - Control and Analysis
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)

        # Right panel - Visualization
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=2)

        # Sidebar-like nav on left
        self.setup_sidebar(left_panel)
        self.setup_control_panel(left_panel)
        self.setup_analysis_panel(left_panel)
        self.setup_visualization_panel(right_panel)
        self.setup_status_bar()

    def setup_control_panel(self, parent):
        """Setup the control panel with advanced options."""
        control_frame = ttk.LabelFrame(parent, text="🎛️ Control Panel", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Scan controls
        scan_frame = ttk.Frame(control_frame)
        scan_frame.pack(fill=tk.X, pady=5)

        self.scan_button = ttk.Button(
            scan_frame, text="🔄 Start Scan", command=self.toggle_scanning
        )
        self.scan_button.pack(side=tk.LEFT, padx=5)

        self.enhanced_scan_btn = ttk.Button(
            scan_frame, text="🚀 Enhanced Scan", command=self.start_enhanced_scan
        )
        self.enhanced_scan_btn.pack(side=tk.LEFT, padx=5)

        # View mode selector
        view_frame = ttk.Frame(control_frame)
        view_frame.pack(fill=tk.X, pady=5)

        ttk.Label(view_frame, text="View Mode:").pack(side=tk.LEFT)
        view_combo = ttk.Combobox(
            view_frame,
            textvariable=self.view_mode,
            values=["spectrum", "interference", "security", "historical"],
            state="readonly",
            width=15,
        )
        view_combo.pack(side=tk.LEFT, padx=5)
        view_combo.bind('<<ComboboxSelected>>', self.on_view_mode_change)

        # Auto-refresh toggle
        refresh_frame = ttk.Frame(control_frame)
        refresh_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(refresh_frame, text="Auto-refresh", variable=self.auto_refresh).pack(
            side=tk.LEFT
        )

        ttk.Label(refresh_frame, text="Interval:").pack(side=tk.LEFT, padx=(10, 0))
        interval_spin = ttk.Spinbox(
            refresh_frame,
            from_=1,
            to=60,
            textvariable=tk.DoubleVar(value=self.refresh_interval),
            width=5,
            command=self.update_refresh_interval,
        )
        interval_spin.pack(side=tk.LEFT, padx=5)

    def setup_analysis_panel(self, parent):
        """Setup the analysis panel with detailed network information."""
        analysis_frame = ttk.LabelFrame(parent, text="📊 Network Analysis", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Network list with enhanced details
        list_frame = ttk.Frame(analysis_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Network listbox
        self.network_listbox = tk.Listbox(
            list_frame, bg='black', fg='#00FF00', font=('Courier', 10), selectbackground='#444444'
        )
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.network_listbox.yview
        )
        self.network_listbox.configure(yscrollcommand=scrollbar.set)

        self.network_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection events
        self.network_listbox.bind('<<ListboxSelect>>', self.on_network_select)
        self.network_listbox.bind('<Double-Button-1>', self.on_network_double_click)

        # Analysis buttons
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="📈 Export Data", command=self.export_scan_data).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            button_frame, text="🔍 Interference Analysis", command=self.show_interference_analysis
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame, text="📊 Channel Optimization", command=self.show_channel_optimization
        ).pack(side=tk.LEFT, padx=5)

    def setup_visualization_panel(self, parent):
        """Setup the visualization panel with multiple view options."""
        viz_frame = ttk.LabelFrame(parent, text="🎨 Visualization", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True)

        # View selector tabs
        self.notebook = ttk.Notebook(viz_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Spectrum view tab
        self.spectrum_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.spectrum_frame, text="📡 Spectrum")
        self.setup_spectrum_view()

        # Interference view tab
        self.interference_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.interference_frame, text="⚠️ Interference")
        self.setup_interference_view()

        # Security view tab
        self.security_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.security_frame, text="🔒 Security")
        self.setup_security_view()

        # Historical view tab
        self.historical_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.historical_frame, text="📈 Historical")
        self.setup_historical_view()

    def setup_spectrum_view(self):
        """Setup the spectrum visualization view."""
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure
            self.spectrum_fig = Figure(figsize=(8, 6), facecolor='black')
            self.spectrum_ax = self.spectrum_fig.add_subplot(111, facecolor='black')
            self.spectrum_canvas = FigureCanvasTkAgg(self.spectrum_fig, self.spectrum_frame)
            self.spectrum_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # Fallback to canvas
            self.spectrum_canvas = tk.Canvas(self.spectrum_frame, bg='black', width=600, height=400)
            self.spectrum_canvas.pack(fill=tk.BOTH, expand=True)

    def setup_interference_view(self):
        """Setup the interference analysis view."""
        self.interference_canvas = tk.Canvas(
            self.interference_frame, bg='black', width=600, height=400
        )
        self.interference_canvas.pack(fill=tk.BOTH, expand=True)

    def setup_security_view(self):
        """Setup the security assessment view."""
        self.security_canvas = tk.Canvas(self.security_frame, bg='black', width=600, height=400)
        self.security_canvas.pack(fill=tk.BOTH, expand=True)

    def setup_historical_view(self):
        """Setup the historical data view."""
        self.historical_canvas = tk.Canvas(self.historical_frame, bg='black', width=600, height=400)
        self.historical_canvas.pack(fill=tk.BOTH, expand=True)

    def setup_status_bar(self):
        """Setup the status bar with real-time information."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

        # Scan count and time
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(side=tk.RIGHT)

        self.scan_count_label = ttk.Label(info_frame, text="Scans: 0")
        self.scan_count_label.pack(side=tk.RIGHT, padx=5)

        self.time_label = ttk.Label(info_frame, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)

    def start_auto_scan(self):
        """Start automatic scanning in background."""
        self.is_scanning = True
        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()
        self.update_status("🟡 Starting scan...")

    def scan_loop(self):
        """Main scanning loop with enhanced capabilities."""
        while self.is_scanning:
            try:
                self.update_status("🟡 Scanning...")

                # Use enhanced scanner if available
                if enhanced_wifi_scan and self.spectrum_analyzer:
                    networks = enhanced_wifi_scan(extended_range=True, multiple_scans=2)
                    self.process_enhanced_networks(networks)
                elif scan_wifi_cross_platform:
                    networks = scan_wifi_cross_platform()
                    self.process_basic_networks(networks)
                else:
                    self.simulate_networks()

                self.scan_count += 1
                self.update_display()
                self.update_status(f"🟢 Active - Found {len(self.networks)} networks")

                # Update time
                self.root.after(
                    0, lambda: self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
                )

                time.sleep(self.refresh_interval)

            except Exception as e:
                self.update_status(f"🔴 Error: {str(e)[:50]}...")
                time.sleep(5)

    def process_enhanced_networks(self, networks):
        """Process networks from enhanced scanner."""
        self.networks = []
        current_time = datetime.now()

        for net in networks:
            network_data = {
                'ssid': net.ssid,
                'bssid': net.bssid,
                'signal_percent': net.signal_percent,
                'channel': net.channel,
                'frequency_mhz': net.frequency_mhz,
                'band': net.band,
                'auth': net.auth,
                'cipher': net.cipher,
                'rssi_dbm': getattr(net, 'rssi_dbm', None),
                'noise_floor': getattr(net, 'noise_floor', None),
                'snr': getattr(net, 'snr', None),
                'vendor': getattr(net, 'vendor', None),
                'timestamp': current_time,
            }

            self.networks.append(network_data)
            self.update_network_history(network_data)
        # Attach stable IDs and maintain per-BSSID history
        self._enrich_with_history(self.networks)

    def process_basic_networks(self, networks):
        """Process networks from basic scanner."""
        self.networks = []
        current_time = datetime.now()

        for net in networks:
            network_data = {
                'ssid': net.ssid,
                'bssid': net.bssid,
                'signal_percent': net.signal_percent,
                'channel': net.channel,
                'frequency_mhz': net.frequency_mhz,
                'band': net.band,
                'auth': net.auth,
                'cipher': net.cipher,
                'timestamp': current_time,
            }

            self.networks.append(network_data)
            self.update_network_history(network_data)
        # Attach stable IDs and maintain per-BSSID history
        self._enrich_with_history(self.networks)

    def update_network_history(self, network):
        """Update historical data for a network."""
        bssid = network['bssid']
        if bssid not in self.network_history:
            self.network_history[bssid] = deque(maxlen=100)  # Keep last 100 scans

        self.network_history[bssid].append(network.copy())

    def get_stable_id(self, network: dict) -> str:
        """Return a stable human-friendly ID derived from BSSID/band/channel."""
        bssid = network.get('bssid') or ''
        suffix = ''.join(bssid.split(':')[-3:]) or 'UNKNOWN'
        band = network.get('band')
        band_code = '2' if band == '2.4GHz' else '5' if band == '5GHz' else '6'
        ch = int(network.get('channel') or 0)
        return f"{band_code}{ch:02d}-{suffix.upper()}"

    def _enrich_with_history(self, networks: list) -> None:
        """Populate networks with stable IDs and maintain per-BSSID history summary."""
        now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for net in networks:
            bssid = net.get('bssid')
            if not bssid:
                net['custom_id'] = self.get_stable_id(net)
                continue
            entry = self.network_registry.get(bssid)
            if entry is None:
                entry = {
                    'first_seen': now_ts,
                    'last_seen': now_ts,
                    'detection_count': 1,
                    'stable_id': self.get_stable_id(net),
                }
                self.network_registry[bssid] = entry
            else:
                entry['last_seen'] = now_ts
                entry['detection_count'] += 1
                entry['stable_id'] = self.get_stable_id(net)
            net['custom_id'] = entry['stable_id']
            net['first_seen'] = entry['first_seen']
            net['last_seen'] = entry['last_seen']
            net['detection_count'] = entry['detection_count']

    def update_display(self):
        """Update all display elements."""
        self.root.after(0, self._update_display_safe)

    def _update_display_safe(self):
        """Thread-safe display update."""
        # Update network list
        self.network_listbox.delete(0, tk.END)

        # Sort by signal strength
        sorted_networks = sorted(self.networks, key=lambda x: x['signal_percent'], reverse=True)

        for _i, net in enumerate(sorted_networks):
            # Create enhanced display text
            band_icon = "🔴" if net['band'] == '2.4GHz' else "🔵" if net['band'] == '5GHz' else "🟣"
            signal_bars = "█" * (net['signal_percent'] // 20) + "░" * (
                5 - net['signal_percent'] // 20
            )

            # Enhanced format with stable ID
            custom_id = net.get('custom_id') or self.get_stable_id(net)
            display_text = f"[{custom_id}] {band_icon} {net['ssid'][:20]:20} {signal_bars} {net['signal_percent']:3d}% Ch{net['channel']:2d} {net['band']}"
            self.network_listbox.insert(tk.END, display_text)

        # Update scan count
        self.scan_count_label.config(text=f"Scans: {self.scan_count}")

        # Update visualizations
        self.update_visualizations()

    def update_visualizations(self):
        """Update all visualization views."""
        if self.view_mode.get() == "spectrum":
            self.update_spectrum_view()
        elif self.view_mode.get() == "interference":
            self.update_interference_view()
        elif self.view_mode.get() == "security":
            self.update_security_view()
        elif self.view_mode.get() == "historical":
            self.update_historical_view()

    def update_spectrum_view(self):
        """Update the spectrum visualization."""
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'spectrum_ax'):
            self.spectrum_ax.clear()
            self.spectrum_ax.set_facecolor('black')

            if self.networks:
                # Create spectrum plot
                channels = [net['channel'] for net in self.networks]
                signals = [net['signal_percent'] for net in self.networks]
                colors = ['red' if net['band'] == '2.4GHz' else 'blue' for net in self.networks]

                self.spectrum_ax.scatter(channels, signals, c=colors, s=100, alpha=0.7)
                self.spectrum_ax.set_xlabel('Channel', color='white')
                self.spectrum_ax.set_ylabel('Signal Strength (%)', color='white')
                self.spectrum_ax.set_title('WiFi Spectrum Analysis', color='white')
                self.spectrum_ax.grid(True, alpha=0.3)
                self.spectrum_ax.tick_params(colors='white')

                # Set axis colors
                self.spectrum_ax.spines['bottom'].set_color('white')
                self.spectrum_ax.spines['top'].set_color('white')
                self.spectrum_ax.spines['left'].set_color('white')
                self.spectrum_ax.spines['right'].set_color('white')

            self.spectrum_canvas.draw()
        else:
            # Fallback canvas update
            self.spectrum_canvas.delete("all")
            if self.networks:
                # Simple bar chart
                bar_width = 600 // len(self.networks)
                for i, net in enumerate(self.networks):
                    x = i * bar_width + 50
                    height = (net['signal_percent'] / 100) * 300
                    color = '#FF4444' if net['band'] == '2.4GHz' else '#4444FF'

                    self.spectrum_canvas.create_rectangle(
                        x, 350 - height, x + bar_width - 10, 350, fill=color, outline='white'
                    )
                    self.spectrum_canvas.create_text(
                        x + bar_width // 2, 370, text=f"Ch{net['channel']}", fill='white'
                    )

    def update_interference_view(self):
        """Update the interference analysis view."""
        self.interference_canvas.delete("all")

        if not self.networks:
            return

        # Analyze channel interference
        channel_usage = defaultdict(list)
        for net in self.networks:
            channel_usage[net['channel']].append(net)

        # Draw interference map
        y_offset = 50
        for _channel, networks in sorted(channel_usage.items()):
            x = 50
            for net in networks:
                color = '#FF4444' if net['band'] == '2.4GHz' else '#4444FF'
                size = max(20, net['signal_percent'] // 5)

                self.interference_canvas.create_oval(
                    x, y_offset, x + size, y_offset + size, fill=color, outline='white'
                )
                self.interference_canvas.create_text(
                    x + size // 2,
                    y_offset + size + 15,
                    text=net['ssid'][:10],
                    fill='white',
                    font=('Arial', 8),
                )
                x += size + 10

            y_offset += 80

    def update_security_view(self):
        """Update the security assessment view."""
        self.security_canvas.delete("all")

        if not self.networks:
            return

        # Security analysis
        security_levels = {'Excellent': 0, 'Good': 0, 'Fair': 0, 'Poor': 0, 'Critical': 0}

        for net in self.networks:
            level = self.assess_security_level(net)
            if 'Excellent' in level:
                security_levels['Excellent'] += 1
            elif 'Good' in level:
                security_levels['Good'] += 1
            elif 'Fair' in level:
                security_levels['Fair'] += 1
            elif 'Poor' in level:
                security_levels['Poor'] += 1
            else:
                security_levels['Critical'] += 1

        # Draw security pie chart
        total = len(self.networks)
        if total > 0:
            colors = ['#00FF00', '#FFFF00', '#FFAA00', '#FF6600', '#FF0000']
            y_offset = 100

            for i, (level, count) in enumerate(security_levels.items()):
                if count > 0:
                    percentage = (count / total) * 100
                    self.security_canvas.create_rectangle(
                        50,
                        y_offset,
                        50 + percentage * 3,
                        y_offset + 30,
                        fill=colors[i],
                        outline='white',
                    )
                    self.security_canvas.create_text(
                        60,
                        y_offset + 15,
                        text=f"{level}: {count} ({percentage:.1f}%)",
                        anchor='w',
                        fill='black',
                        font=('Arial', 10, 'bold'),
                    )
                    y_offset += 40

    def update_historical_view(self):
        """Update the historical data view."""
        self.historical_canvas.delete("all")

        if not self.network_history:
            return

        # Show network stability over time
        y_offset = 50
        for _bssid, history in list(self.network_history.items())[:10]:  # Show first 10
            if len(history) > 1:
                # Plot signal strength over time
                signals = [h['signal_percent'] for h in history]
                x_points = [50 + i * 20 for i in range(len(signals))]
                y_points = [350 - (s / 100) * 250 for s in signals]

                # Draw line
                for i in range(len(x_points) - 1):
                    self.historical_canvas.create_line(
                        x_points[i],
                        y_points[i],
                        x_points[i + 1],
                        y_points[i + 1],
                        fill='#00FF00',
                        width=2,
                    )

                # Label
                ssid = history[-1]['ssid'][:15]
                self.historical_canvas.create_text(
                    x_points[0], y_offset, text=ssid, fill='white', font=('Arial', 8)
                )
                y_offset += 30

    def assess_security_level(self, network):
        """Assess security level of a network."""
        auth = network.get('auth', 'Unknown').upper()
        cipher = network.get('cipher', 'Unknown').upper()

        if 'WPA3' in auth:
            return "🟢 Excellent (WPA3)"
        elif 'WPA2' in auth and 'AES' in cipher:
            return "🟡 Good (WPA2-AES)"
        elif 'WPA2' in auth:
            return "🟡 Good (WPA2)"
        elif 'WPA' in auth:
            return "🟠 Fair (WPA - Outdated)"
        elif 'WEP' in auth:
            return "🔴 Poor (WEP - Insecure)"
        elif 'OPEN' in auth or auth == 'Unknown':
            return "🔴 Critical (Open Network)"
        else:
            return f"🟡 Moderate ({auth})"

    def toggle_scanning(self):
        """Toggle scanning on/off."""
        if self.is_scanning:
            self.is_scanning = False
            self.scan_button.config(text="🔄 Start Scan")
            self.update_status("⏸️ Scanning paused")
        else:
            self.is_scanning = True
            self.scan_button.config(text="⏸️ Stop Scan")
            self.start_auto_scan()

    def start_enhanced_scan(self):
        """Start an enhanced scan with multiple passes."""
        if self.spectrum_analyzer:
            self.update_status("🚀 Starting enhanced scan...")
            # This would trigger a more comprehensive scan
            threading.Thread(target=self._enhanced_scan_worker, daemon=True).start()
        else:
            messagebox.showwarning("Enhanced Scanner", "Enhanced scanner not available")

    def _enhanced_scan_worker(self):
        """Worker thread for enhanced scanning."""
        try:
            if enhanced_wifi_scan:
                networks = enhanced_wifi_scan(extended_range=True, multiple_scans=3, scan_delay=1.0)
                self.root.after(0, lambda: self.process_enhanced_networks(networks))
                self.root.after(0, lambda: self.update_status("🚀 Enhanced scan completed"))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.update_status(f"🔴 Enhanced scan error: {error_msg}"))

    def export_scan_data(self):
        """Export scan data to CSV/JSON."""
        if not self.networks:
            messagebox.showinfo("Export", "No data to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")],
        )

        if filename:
            try:
                if filename.endswith('.csv'):
                    self._export_to_csv(filename)
                elif filename.endswith('.json'):
                    self._export_to_json(filename)
                else:
                    self._export_to_csv(filename + '.csv')

                messagebox.showinfo("Export", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def _export_to_csv(self, filename):
        """Export data to CSV format."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if self.networks:
                fieldnames = self.networks[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.networks)

    def _export_to_json(self, filename):
        """Export data to JSON format."""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'scan_count': self.scan_count,
            'networks': self.networks,
            'history_summary': {
                bssid: len(history) for bssid, history in self.network_history.items()
            },
        }

        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, default=str)

    def show_interference_analysis(self):
        """Show detailed interference analysis."""
        if not self.networks:
            messagebox.showinfo("Analysis", "No networks to analyze")
            return

        # Create interference analysis window
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Interference Analysis")
        analysis_window.geometry("800x600")

        # Analyze channel usage
        channel_usage = defaultdict(list)
        for net in self.networks:
            channel_usage[net['channel']].append(net)

        # Create analysis text
        analysis_text = scrolledtext.ScrolledText(analysis_window, height=30)
        analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        analysis_text.insert(tk.END, "📊 INTERFERENCE ANALYSIS REPORT\n")
        analysis_text.insert(tk.END, "=" * 50 + "\n\n")

        for channel, networks in sorted(channel_usage.items()):
            analysis_text.insert(tk.END, f"Channel {channel}:\n")
            analysis_text.insert(tk.END, f"  Networks: {len(networks)}\n")

            if len(networks) > 1:
                analysis_text.insert(tk.END, "  ⚠️ INTERFERENCE DETECTED!\n")
                analysis_text.insert(tk.END, "  Recommendations:\n")
                analysis_text.insert(tk.END, "    • Switch to less congested channel\n")
                analysis_text.insert(tk.END, "    • Consider 5GHz if available\n")
                analysis_text.insert(tk.END, "    • Adjust transmit power\n")
            else:
                analysis_text.insert(tk.END, "  ✅ No interference detected\n")

            analysis_text.insert(tk.END, "\n")

    def show_channel_optimization(self):
        """Show channel optimization recommendations."""
        if not self.networks:
            messagebox.showinfo("Optimization", "No networks to optimize")
            return

        # Create optimization window
        opt_window = tk.Toplevel(self.root)
        opt_window.title("Channel Optimization")
        opt_window.geometry("700x500")

        opt_text = scrolledtext.ScrolledText(opt_window, height=25)
        opt_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        opt_text.insert(tk.END, "🎯 CHANNEL OPTIMIZATION RECOMMENDATIONS\n")
        opt_text.insert(tk.END, "=" * 50 + "\n\n")

        # Analyze current usage
        channel_usage = defaultdict(list)
        for net in self.networks:
            channel_usage[net['channel']].append(net)

        # Find optimal channels
        optimal_24 = [1, 6, 11]  # Non-overlapping 2.4GHz channels
        optimal_5 = [36, 44, 52, 60, 100, 108, 116, 124, 132, 140, 148, 156, 164]

        opt_text.insert(tk.END, "📡 2.4GHz Band Analysis:\n")
        for channel in optimal_24:
            if channel in channel_usage:
                opt_text.insert(
                    tk.END, f"  Channel {channel}: {len(channel_usage[channel])} networks\n"
                )
            else:
                opt_text.insert(tk.END, f"  Channel {channel}: ✅ Available (Recommended)\n")

        opt_text.insert(tk.END, "\n📡 5GHz Band Analysis:\n")
        for channel in optimal_5[:8]:  # Show first 8 channels
            if channel in channel_usage:
                opt_text.insert(
                    tk.END, f"  Channel {channel}: {len(channel_usage[channel])} networks\n"
                )
            else:
                opt_text.insert(tk.END, f"  Channel {channel}: ✅ Available (Recommended)\n")

    def on_network_select(self, event):
        """Handle network selection."""
        selection = self.network_listbox.curselection()
        if selection:
            index = selection[0]
            sorted_networks = sorted(self.networks, key=lambda x: x['signal_percent'], reverse=True)
            if index < len(sorted_networks):
                network = sorted_networks[index]
                self.show_network_details(network)

    def on_network_double_click(self, event):
        """Handle network double-click for detailed view."""
        selection = self.network_listbox.curselection()
        if selection:
            index = selection[0]
            sorted_networks = sorted(self.networks, key=lambda x: x['signal_percent'], reverse=True)
            if index < len(sorted_networks):
                network = sorted_networks[index]
                self.show_detailed_network_view(network)

    def show_network_details(self, network):
        """Show basic network details in status bar."""
        details = f"📡 {network['ssid']} | Signal: {network['signal_percent']}% | Channel: {network['channel']} | {network['band']}"
        self.update_status(details)

    def show_detailed_network_view(self, network):
        """Show detailed network information in a new window."""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Network Details: {network['ssid']}")
        detail_window.geometry("600x400")

        detail_text = scrolledtext.ScrolledText(detail_window, height=20)
        detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format detailed information
        details = f"""
🔍 NETWORK DETAILS
{'=' * 50}

📡 BASIC INFORMATION
SSID: {network['ssid']}
BSSID: {network['bssid']}
Band: {network['band']}
Channel: {network['channel']}
Frequency: {network['frequency_mhz']} MHz

📶 SIGNAL ANALYSIS
Signal Strength: {network['signal_percent']}%
RSSI: ~{-90 + (network['signal_percent'] * 0.6):.0f} dBm
Distance Estimate: {self.estimate_distance(network['signal_percent'])}

🔒 SECURITY
Authentication: {network['auth']}
Encryption: {network['cipher']}
Security Level: {self.assess_security_level(network)}

📊 INTERFERENCE ANALYSIS
Channel Congestion: {self.analyze_channel_congestion(network)}
Co-channel Networks: {self.count_cochannel_networks(network)}

🌊 PROPAGATION
Line of Sight: {self.assess_line_of_sight(network)}
Expected Throughput: {self.estimate_throughput(network)}

💡 RECOMMENDATIONS
{self.generate_recommendations(network)}
        """

        detail_text.insert(tk.END, details)

    def estimate_distance(self, signal_percent):
        """Estimate distance from signal strength."""
        if signal_percent > 80:
            return "Very Close (<10m)"
        elif signal_percent > 60:
            return "Close (10-30m)"
        elif signal_percent > 40:
            return "Medium (30-70m)"
        else:
            return "Far (>70m)"

    def analyze_channel_congestion(self, network):
        """Analyze channel congestion."""
        same_channel = [
            n
            for n in self.networks
            if n['channel'] == network['channel'] and n['bssid'] != network['bssid']
        ]
        if len(same_channel) == 0:
            return "🟢 Clear"
        elif len(same_channel) <= 2:
            return "🟡 Light"
        else:
            return "🔴 Heavy"

    def count_cochannel_networks(self, network):
        """Count networks on same channel."""
        same_channel = [
            n
            for n in self.networks
            if n['channel'] == network['channel'] and n['bssid'] != network['bssid']
        ]
        return len(same_channel)

    def assess_line_of_sight(self, network):
        """Assess line-of-sight conditions."""
        signal = network['signal_percent']
        if signal > 80:
            return "🟢 Clear Line-of-Sight"
        elif signal > 60:
            return "🟡 Partial Obstruction"
        else:
            return "🔴 Blocked Line-of-Sight"

    def estimate_throughput(self, network):
        """Estimate expected throughput."""
        signal = network['signal_percent']
        band = network['band']

        base_throughput = 300 if band == '5GHz' else 150
        throughput = base_throughput * (signal / 100)

        if throughput > 200:
            return f"🟢 {throughput:.0f} Mbps (Excellent)"
        elif throughput > 100:
            return f"🟡 {throughput:.0f} Mbps (Good)"
        else:
            return f"🔴 {throughput:.0f} Mbps (Fair)"

    def generate_recommendations(self, network):
        """Generate recommendations for network optimization."""
        recommendations = []
        signal = network['signal_percent']

        if signal < 60:
            recommendations.append("• Move closer to access point")
            recommendations.append("• Check for physical obstacles")

        if self.count_cochannel_networks(network) > 0:
            recommendations.append("• Switch to less congested channel")
            recommendations.append("• Consider 5GHz if available")

        if network.get('auth', '').upper() in ['WEP', 'OPEN']:
            recommendations.append("• ⚠️ SECURITY RISK: Upgrade encryption")

        if not recommendations:
            recommendations.append("• Network configuration appears optimal")

        return '\n'.join(recommendations)

    def on_view_mode_change(self, event):
        """Handle view mode change."""
        self.update_visualizations()

    def update_refresh_interval(self):
        """Update the refresh interval."""
        try:
            self.refresh_interval = float(self.root.focus_get().get())
        except:
            pass

    def update_status(self, message):
        """Update status bar message."""
        self.status_label.config(text=message)

    def simulate_networks(self):
        """Simulate network data for demo purposes."""
        import random

        base_networks = [
            {'ssid': 'Home_WiFi_5G', 'channel': 36, 'band': '5GHz'},
            {'ssid': 'Neighbor_2G', 'channel': 1, 'band': '2.4GHz'},
            {'ssid': 'Office_Network', 'channel': 149, 'band': '5GHz'},
            {'ssid': 'Mobile_Hotspot', 'channel': 11, 'band': '2.4GHz'},
            {'ssid': 'Guest_Network', 'channel': 6, 'band': '2.4GHz'},
        ]

        self.networks = []
        current_time = datetime.now()

        for net in base_networks:
            if random.random() > 0.3:
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
                    'timestamp': current_time,
                }
                self.networks.append(network)
                self.update_network_history(network)

    def run(self):
        """Start the application."""
        self.root.mainloop()

    def _set_windows_app_integration(self):
        """Enable DPI awareness and AppUserModelID on Windows for a native look."""
        if sys.platform.startswith('win'):
            try:
                # DPI awareness for crisp UI on high DPI displays
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
            try:
                # Set AppUserModelID for proper taskbar grouping/icon
                app_id = 'RFAnalyzer.EnhancedViewer'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            except Exception:
                pass


def main():
    """Main function."""
    print("🌊 Starting Enhanced Live Spectrum Viewer...")

    try:
        app = EnhancedLiveViewer()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
