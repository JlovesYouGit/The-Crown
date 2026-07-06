#!/usr/bin/env python3
"""
Unified Spectrum Viewer (Desktop, not Web)
- Single Tkinter application with tabs for Spectrum, Interference, Security, and LIDAR-like map
- Background scanning with simulated fallback if scanner modules are unavailable
- Keyboard shortcuts and export capability
"""

import json
import os
import sys
import threading
import time
import tkinter as tk
from collections import defaultdict, deque
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

# Optional imports (graceful fallback to simulation)
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from spectrum_grabber.wifi_scanner import scan_wifi_cross_platform  # type: ignore
except Exception:
    scan_wifi_cross_platform = None


class UnifiedSpectrumViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(" Unified Spectrum Viewer")
        self.root.geometry("1400x900")
        try:
            self.root.state('zoomed')
        except Exception:
            pass

        self.networks = []
        self.network_history = defaultdict(lambda: deque(maxlen=120))
        self.network_registry = {}
        self.is_scanning = False
        self.scan_thread = None
        self.scan_count = 0
        self.refresh_interval = 3.0
        self.current_theme = 'dark'
        # Intent-driven UX mode
        self.intent_mode = tk.StringVar(value='General Monitoring')

        self._build_ui()
        self._bind_shortcuts()

    # ---------- UI ----------
    def _build_ui(self):
        self._apply_theme()
        self._build_menubar()
        self._build_toolbar()

        container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(container)
        right = ttk.Frame(container)
        container.add(left, weight=1)
        container.add(right, weight=3)

        # Left: network list + details
        self._build_left_panel(left)
        # Right: tabs for visualizations
        self._build_right_panel(right)
        # Status bar
        self._build_status_bar()

    def _apply_theme(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        if self.current_theme == 'dark':
            bg = '#1a1a1a'
            panel = '#2a2a2a'
            fg = '#e6e6e6'
            accent = '#00FFFF'
        else:
            bg = '#f5f5f5'
            panel = '#ffffff'
            fg = '#222222'
            accent = '#005f87'
        self.root.configure(bg=bg)
        style.configure('.', background=panel, foreground=fg, fieldbackground=panel)
        style.configure('TFrame', background=panel)
        style.configure('TLabel', background=panel, foreground=fg)
        style.configure('TButton', background=panel, foreground=fg)
        style.configure('TNotebook', background=bg)
        style.configure('TNotebook.Tab', background=panel, foreground=fg)
        self.palette = {
            'bg': bg,
            'panel': panel,
            'fg': fg,
            'accent': accent,
            'band_24': '#FF4444',
            'band_5': '#4444FF',
            'band_6': '#FF44FF',
        }

    def _build_menubar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export...", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="About",
            command=lambda: messagebox.showinfo(
                "About", "Unified Spectrum Viewer\nNative desktop app (Tkinter)"
            ),
        )
        menubar.add_cascade(label="Help", menu=help_menu)

    def _build_toolbar(self):
        bar = ttk.Frame(self.root)
        bar.pack(fill=tk.X, padx=8, pady=(6, 4))
        ttk.Button(bar, text=" Start Scan", command=self.toggle_scanning).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text=" Export", command=self.export_data).pack(side=tk.LEFT, padx=4)
        ttk.Label(bar, text="Interval (s):").pack(side=tk.LEFT, padx=(12, 4))
        self.interval_var = tk.DoubleVar(value=self.refresh_interval)
        ttk.Spinbox(
            bar,
            from_=1,
            to=60,
            width=6,
            textvariable=self.interval_var,
            command=self._update_interval,
        ).pack(side=tk.LEFT)

        # Intent selector
        ttk.Label(bar, text="  Intent:").pack(side=tk.LEFT, padx=(16, 4))
        self.intent_combo = ttk.Combobox(
            bar,
            state="readonly",
            width=22,
            textvariable=self.intent_mode,
            values=(
                'General Monitoring',
                'Interference Mitigation',
                'Security Audit',
                'Site Survey / Mapping',
            ),
        )
        self.intent_combo.pack(side=tk.LEFT)
        self.intent_combo.bind('<<ComboboxSelected>>', self._on_intent_changed)

    def _build_left_panel(self, parent):
        # Analysis panel with list and details
        panel = ttk.Frame(parent)
        panel.pack(fill=tk.BOTH, expand=True)

        ttk.Label(panel, text=" Detected Networks", font=('Segoe UI', 12, 'bold')).pack(
            anchor='w', padx=6, pady=(4, 2)
        )
        list_frame = ttk.Frame(panel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.network_listbox = tk.Listbox(
            list_frame, bg='black', fg='#00FF00', font=('Consolas', 10), selectbackground='#444444'
        )
        yscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.network_listbox.yview)
        self.network_listbox.configure(yscrollcommand=yscroll.set)
        self.network_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.network_listbox.bind('<<ListboxSelect>>', self._on_select_network)

        # Details
        self.detail_text = tk.Text(
            panel,
            height=10,
            bg='black',
            fg='#FFFF00',
            font=('Consolas', 10),
            insertbackground='#FFFF00',
        )
        self.detail_text.pack(fill=tk.X, padx=6, pady=(0, 6))

    def _build_right_panel(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Spectrum tab
        self.spectrum_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.spectrum_tab, text=" Spectrum")
        self.spectrum_canvas = tk.Canvas(self.spectrum_tab, bg='black')
        self.spectrum_canvas.pack(fill=tk.BOTH, expand=True)

        # Interference tab
        self.interf_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.interf_tab, text=" Interference")
        self.interf_canvas = tk.Canvas(self.interf_tab, bg='black')
        self.interf_canvas.pack(fill=tk.BOTH, expand=True)

        # Security tab
        self.security_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.security_tab, text=" Security")
        self.security_canvas = tk.Canvas(self.security_tab, bg='black')
        self.security_canvas.pack(fill=tk.BOTH, expand=True)

        # LIDAR Map tab (2D approximation)
        self.lidar_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.lidar_tab, text=" LIDAR Map")
        self.lidar_canvas = tk.Canvas(self.lidar_tab, bg='black')
        self.lidar_canvas.pack(fill=tk.BOTH, expand=True)

    def _build_status_bar(self):
        bar = ttk.Frame(self.root)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = ttk.Label(bar, text="Ready", anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        right = ttk.Frame(bar)
        right.pack(side=tk.RIGHT)
        self.scan_count_label = ttk.Label(right, text="Scans: 0")
        self.scan_count_label.pack(side=tk.RIGHT, padx=6)
        self.time_label = ttk.Label(right, text="")
        self.time_label.pack(side=tk.RIGHT, padx=6)

    def _bind_shortcuts(self):
        self.root.bind('<space>', lambda e: self.toggle_scanning())
        self.root.bind('<Control-s>', lambda e: self.export_data())
        self.root.bind('<Control-1>', lambda e: self.notebook.select(self.spectrum_tab))
        self.root.bind('<Control-2>', lambda e: self.notebook.select(self.interf_tab))
        self.root.bind('<Control-3>', lambda e: self.notebook.select(self.security_tab))
        self.root.bind('<Control-4>', lambda e: self.notebook.select(self.lidar_tab))
        # Quick intent switches
        self.root.bind('<Alt-1>', lambda e: self._set_intent('General Monitoring'))
        self.root.bind('<Alt-2>', lambda e: self._set_intent('Interference Mitigation'))
        self.root.bind('<Alt-3>', lambda e: self._set_intent('Security Audit'))
        self.root.bind('<Alt-4>', lambda e: self._set_intent('Site Survey / Mapping'))

    # ---------- Scanning ----------
    def toggle_scanning(self):
        if self.is_scanning:
            self.is_scanning = False
            self._set_status(" Scanning paused")
        else:
            self.is_scanning = True
            if not self.scan_thread or not self.scan_thread.is_alive():
                self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
                self.scan_thread.start()
            self._set_status(" Scanning...")

    def _update_interval(self):
        try:
            self.refresh_interval = float(self.interval_var.get())
        except Exception:
            pass

    # ---------- Intent handling ----------
    def _set_intent(self, intent_label: str):
        try:
            self.intent_mode.set(intent_label)
            if hasattr(self, 'intent_combo'):
                self.intent_combo.set(intent_label)
        except Exception:
            pass
        self._on_intent_changed()

    def _on_intent_changed(self, event=None):
        """Apply intent-driven UI behavior: switch tabs, tweak interval, update status."""
        intent = self.intent_mode.get()
        # Switch to the most relevant tab for the selected intent
        if intent == 'Interference Mitigation':
            try:
                self.notebook.select(self.interf_tab)
            except Exception:
                pass
            self._set_status(' Intent: Interference Mitigation — focus on congested channels')
        elif intent == 'Security Audit':
            try:
                self.notebook.select(self.security_tab)
            except Exception:
                pass
            self._set_status(' Intent: Security Audit — assess auth/cipher posture')
        elif intent == 'Site Survey / Mapping':
            try:
                self.notebook.select(self.lidar_tab)
            except Exception:
                pass
            self._set_status(' Intent: Site Survey — spatial mapping and coverage')
        else:
            try:
                self.notebook.select(self.spectrum_tab)
            except Exception:
                pass
            self._set_status(' Intent: General Monitoring — overall spectrum health')

        # Adjust default interval subtly based on intent (non-destructive)
        try:
            if intent in ('Interference Mitigation', 'Site Survey / Mapping'):
                # Faster refresh for dynamic tasks
                self.refresh_interval = max(1.0, float(self.interval_var.get()))
            else:
                # Slightly slower for audits/monitoring to reduce noise
                self.refresh_interval = max(2.0, float(self.interval_var.get()))
            self.interval_var.set(self.refresh_interval)
        except Exception:
            pass

    def _scan_loop(self):
        while self.is_scanning:
            try:
                networks = self._scan_networks()
                self._process_networks(networks)
                self.scan_count += 1
                self.root.after(0, self._update_display)
                self.root.after(
                    0, lambda: self.scan_count_label.config(text=f"Scans: {self.scan_count}")
                )
                self.root.after(
                    0, lambda: self.time_label.config(text=datetime.now().strftime('%H:%M:%S'))
                )
                time.sleep(self.refresh_interval)
            except Exception as e:
                self._set_status(f" Error: {e}")
                time.sleep(5)

    def _scan_networks(self):
        if scan_wifi_cross_platform:
            try:
                aps = scan_wifi_cross_platform()
                nets = []
                for ap in aps:
                    nets.append(
                        {
                            'ssid': ap.ssid,
                            'bssid': ap.bssid,
                            'signal_percent': int(ap.signal_percent),
                            'channel': int(ap.channel),
                            'frequency_mhz': int(ap.frequency_mhz),
                            'band': ap.band,
                            'auth': getattr(ap, 'auth', 'Unknown'),
                            'cipher': getattr(ap, 'cipher', 'Unknown'),
                        }
                    )
                return nets
            except Exception:
                pass
        # Fallback simulation
        import random

        base = [
            {'ssid': 'Home_WiFi_5G', 'channel': 36, 'band': '5GHz'},
            {'ssid': 'Neighbor_2G', 'channel': 1, 'band': '2.4GHz'},
            {'ssid': 'Office_Network', 'channel': 149, 'band': '5GHz'},
            {'ssid': 'Mobile_Hotspot', 'channel': 11, 'band': '2.4GHz'},
            {'ssid': 'Guest_Network', 'channel': 6, 'band': '2.4GHz'},
        ]
        nets = []
        for b in base:
            if random.random() > 0.25:
                freq = (
                    2412 + (b['channel'] - 1) * 5
                    if b['band'] == '2.4GHz'
                    else 5000 + b['channel'] * 5
                )
                nets.append(
                    {
                        'ssid': b['ssid'],
                        'bssid': f"aa:bb:cc:dd:ee:{random.randint(10, 99)}",
                        'signal_percent': random.randint(30, 100),
                        'channel': b['channel'],
                        'frequency_mhz': freq,
                        'band': b['band'],
                        'auth': 'WPA2',
                        'cipher': 'AES',
                    }
                )
        return nets

    def _process_networks(self, networks):
        self.networks = networks
        now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for net in self.networks:
            bssid = net.get('bssid') or ''
            if bssid not in self.network_registry:
                self.network_registry[bssid] = {
                    'first_seen': now_ts,
                    'last_seen': now_ts,
                    'detection_count': 1,
                    'stable_id': self._stable_id(net),
                }
            else:
                r = self.network_registry[bssid]
                r['last_seen'] = now_ts
                r['detection_count'] += 1
                r['stable_id'] = self._stable_id(net)
            # attach view helpers
            reg = self.network_registry[bssid]
            net['custom_id'] = reg['stable_id']
            net['first_seen'] = reg['first_seen']
            net['last_seen'] = reg['last_seen']
            net['detection_count'] = reg['detection_count']
            self.network_history[bssid].append({**net, 'ts': now_ts})

    def _stable_id(self, net):
        bssid = net.get('bssid') or '00:00:00:00:00:00'
        suffix = ''.join(bssid.split(':')[-3:]) or 'UNKNOWN'
        band_code = (
            '2' if net.get('band') == '2.4GHz' else '5' if net.get('band') == '5GHz' else '6'
        )
        ch = int(net.get('channel') or 0)
        return f"{band_code}{ch:02d}-{suffix.upper()}"

    # ---------- Display ----------
    def _update_display(self):
        # List
        self.network_listbox.delete(0, tk.END)
        sorted_nets = sorted(self.networks, key=lambda n: n['signal_percent'], reverse=True)
        for net in sorted_nets:
            bars = "" * (net['signal_percent'] // 20) + "" * (5 - net['signal_percent'] // 20)
            band_icon = '' if net['band'] == '2.4GHz' else '' if net['band'] == '5GHz' else ''
            self.network_listbox.insert(
                tk.END,
                f"[{net['custom_id']}] {band_icon} {net['ssid'][:18]:18} {bars} {net['signal_percent']:3d}% Ch{net['channel']:2d}",
            )
        # Canvases
        self._draw_spectrum()
        self._draw_interference()
        self._draw_security()
        self._draw_lidar_map()
        # Intent-specific overlays/messages (lightweight)
        self._draw_intent_overlays()

    def _on_select_network(self, event):
        sel = self.network_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        sorted_nets = sorted(self.networks, key=lambda n: n['signal_percent'], reverse=True)
        if index >= len(sorted_nets):
            return
        net = sorted_nets[index]
        self._show_network_details(net)

    def _show_network_details(self, net):
        details = [
            f" {net.get('custom_id', 'N/A')} | {net['ssid']}",
            f"BSSID: {net.get('bssid', '')}",
            f"Band/Ch: {net['band']} / {net['channel']}  ({net['frequency_mhz']} MHz)",
            f"Signal: {net['signal_percent']}%  RSSI{-90 + net['signal_percent'] * 0.6:.0f} dBm",
            f"Auth: {net['auth']}  Cipher: {net['cipher']}",
            f"First Seen: {net.get('first_seen', '')}  Last Seen: {net.get('last_seen', '')}",
            f"Detections: {net.get('detection_count', 1)}",
        ]
        self.detail_text.delete('1.0', tk.END)
        self.detail_text.insert('1.0', "\n".join(details))

    # ---------- Drawing ----------
    def _draw_spectrum(self):
        c = self.spectrum_canvas
        c.delete('all')
        width = max(600, c.winfo_width())
        height = max(400, c.winfo_height())
        if not self.networks:
            c.create_text(
                width // 2, height // 2, text="No data", fill='#666666', font=('Segoe UI', 14)
            )
            return
        margin = 50
        chart_w = width - margin * 2
        chart_h = height - margin * 2
        nets = sorted(self.networks, key=lambda n: n['channel'])
        n = len(nets)
        bar_w = max(12, chart_w // max(1, n) - 6)
        for i, net in enumerate(nets):
            x = margin + i * (bar_w + 6)
            h = int((net['signal_percent'] / 100) * chart_h)
            y0 = height - margin - h
            y1 = height - margin
            color = (
                self.palette['band_24']
                if net['band'] == '2.4GHz'
                else self.palette['band_5']
                if net['band'] == '5GHz'
                else self.palette['band_6']
            )
            c.create_rectangle(x, y0, x + bar_w, y1, fill=color, outline='white')
            c.create_text(
                x + bar_w // 2,
                y1 + 12,
                text=f"Ch{net['channel']}",
                fill='white',
                font=('Segoe UI', 9),
            )

    def _draw_interference(self):
        c = self.interf_canvas
        c.delete('all')
        width = max(600, c.winfo_width())
        y = 40
        if not self.networks:
            c.create_text(width // 2, y, text="No data", fill='#666666', font=('Segoe UI', 14))
            return
        usage = defaultdict(list)
        for net in self.networks:
            usage[net['channel']].append(net)
        for ch, nets in sorted(usage.items()):
            x = 50
            c.create_text(
                10,
                y + 20,
                text=f"Ch {ch}",
                fill='#C8CDD7',
                anchor='w',
                font=('Segoe UI', 10, 'bold'),
            )
            for net in nets:
                size = max(18, net['signal_percent'] // 3)
                color = (
                    self.palette['band_24'] if net['band'] == '2.4GHz' else self.palette['band_5']
                )
                c.create_oval(x, y, x + size, y + size, fill=color, outline='white')
                c.create_text(
                    x + size // 2,
                    y + size + 10,
                    text=net['ssid'][:10],
                    fill='white',
                    font=('Segoe UI', 8),
                )
                x += size + 10
            y += 70

        # Intent cue
        if self.intent_mode.get() == 'Interference Mitigation':
            c.create_text(
                width - 10,
                14,
                text='Intent: Interference',
                fill='#00FFFF',
                anchor='e',
                font=('Segoe UI', 10, 'bold'),
            )

    def _draw_security(self):
        c = self.security_canvas
        c.delete('all')
        width = max(600, c.winfo_width())
        y = 40
        if not self.networks:
            c.create_text(width // 2, y, text="No data", fill='#666666', font=('Segoe UI', 14))
            return
        buckets = {'Excellent': 0, 'Good': 0, 'Fair': 0, 'Poor': 0, 'Critical': 0}
        for net in self.networks:
            level = self._security_level(net)
            if 'Excellent' in level:
                buckets['Excellent'] += 1
            elif 'Good' in level and 'Moderate' not in level:
                buckets['Good'] += 1
            elif 'Fair' in level:
                buckets['Fair'] += 1
            elif 'Poor' in level:
                buckets['Poor'] += 1
            else:
                buckets['Critical'] += 1
        colors = {
            'Excellent': '#00FF00',
            'Good': '#FFFF00',
            'Fair': '#FFAA00',
            'Poor': '#FF6600',
            'Critical': '#FF0000',
        }
        x = 50
        for level, count in buckets.items():
            w = int((count / max(1, len(self.networks))) * (width - 100))
            c.create_rectangle(x, y, x + w, y + 30, fill=colors[level], outline='white')
            c.create_text(
                x + 6,
                y + 15,
                text=f"{level}: {count}",
                anchor='w',
                fill='black',
                font=('Segoe UI', 10, 'bold'),
            )
            y += 40

        # Intent cue
        if self.intent_mode.get() == 'Security Audit':
            c.create_text(
                width - 10,
                14,
                text='Intent: Security Audit',
                fill='#00FFFF',
                anchor='e',
                font=('Segoe UI', 10, 'bold'),
            )

    def _draw_lidar_map(self):
        c = self.lidar_canvas
        c.delete('all')
        width = max(600, c.winfo_width())
        height = max(400, c.winfo_height())
        cx, cy = width // 2, height // 2
        # center point
        c.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill='gold', outline='white')
        c.create_text(cx, cy - 14, text='YOU', fill='gold', font=('Segoe UI', 9, 'bold'))
        if not self.networks:
            c.create_text(
                cx, cy + 10, text='Waiting for scans...', fill='#666666', font=('Segoe UI', 12)
            )
            return
        import math

        for i, net in enumerate(self.networks):
            # pseudo-distance inversely related to signal
            distance = max(20, int((100 - net['signal_percent']) * 2))
            angle = (net['channel'] * 30 + i * 37) % 360
            rad = math.radians(angle)
            x = cx + int(distance * math.cos(rad))
            y = cy + int(distance * math.sin(rad))
            color = self.palette['band_24'] if net['band'] == '2.4GHz' else self.palette['band_5']
            r = max(3, net['signal_percent'] // 20)
            c.create_oval(x - r, y - r, x + r, y + r, fill=color, outline='white')
            if net['signal_percent'] > 60:
                c.create_text(x, y - 12, text=net['ssid'][:10], fill='white', font=('Segoe UI', 8))

        # Intent cue
        if self.intent_mode.get() == 'Site Survey / Mapping':
            c.create_text(
                width - 10,
                14,
                text='Intent: Site Survey',
                fill='#00FFFF',
                anchor='e',
                font=('Segoe UI', 10, 'bold'),
            )

    def _draw_intent_overlays(self):
        """Lightweight overlays on the spectrum canvas and status to reflect intent."""
        # Spectrum: show a small header when in General Monitoring
        if self.intent_mode.get() == 'General Monitoring':
            c = self.spectrum_canvas
            c.delete('intent_label')
            width = max(600, c.winfo_width())
            c.create_text(
                width - 10,
                14,
                text='Intent: Monitoring',
                fill='#00FFFF',
                anchor='e',
                font=('Segoe UI', 10, 'bold'),
                tags=('intent_label',),
            )

    # ---------- Utils ----------
    def _security_level(self, network):
        auth = (network.get('auth') or 'Unknown').upper()
        cipher = (network.get('cipher') or 'Unknown').upper()
        if 'WPA3' in auth:
            return ' Excellent (WPA3)'
        if 'WPA2' in auth and 'AES' in cipher:
            return ' Good (WPA2-AES)'
        if 'WPA2' in auth:
            return ' Good (WPA2)'
        if 'WPA' in auth:
            return ' Fair (WPA)'
        if 'WEP' in auth:
            return ' Poor (WEP)'
        if 'OPEN' in auth or auth == 'UNKNOWN':
            return ' Critical (Open)'
        return f' Moderate ({auth})'

    def _set_status(self, msg):
        self.status_label.config(text=msg)

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self._apply_theme()
        self._update_display()

    def export_data(self):
        if not self.networks:
            messagebox.showinfo("Export", "No data to export")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension='.json', filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        if not filename:
            return
        try:
            if filename.endswith('.csv'):
                import csv

                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = list(self.networks[0].keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.networks)
            else:
                payload = {
                    'export_timestamp': datetime.now().isoformat(),
                    'scan_count': self.scan_count,
                    'networks': self.networks,
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=2)
            messagebox.showinfo("Export", f"Data exported to {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def run(self):
        # initial draw
        self._update_display()
        self.root.mainloop()


def main():
    app = UnifiedSpectrumViewer()
    app.run()


if __name__ == '__main__':
    main()
