#!/usr/bin/env python3
"""
GUI Components Module - Handles GUI setup and drawing methods
"""

import math
import tkinter as tk
from tkinter import scrolledtext


class SpectrumGUI:
    """Handles GUI components and drawing methods."""

    def __init__(self, parent):
        self.parent = parent

    def setup_gui(self):
        """Setup the main GUI."""
        # Title
        title_frame = tk.Frame(self.parent.root, bg='#1a1a1a')
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        title_label = tk.Label(
            title_frame,
            text="🌊 Live RF Spectrum Viewer",
            font=('Arial', 20, 'bold'),
            fg='#00FFFF',
            bg='#1a1a1a',
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Real-time WiFi Network Detection & Analysis",
            font=('Arial', 12),
            fg='#CCCCCC',
            bg='#1a1a1a',
        )
        subtitle_label.pack()

        # Control panel
        control_frame = tk.Frame(self.parent.root, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Status indicators
        status_frame = tk.Frame(control_frame, bg='#2a2a2a')
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        self.parent.status_label = tk.Label(
            status_frame,
            text="🔴 Initializing...",
            font=('Arial', 12, 'bold'),
            fg='#FF4444',
            bg='#2a2a2a',
        )
        self.parent.status_label.pack(side=tk.LEFT)

        self.parent.scan_count_label = tk.Label(
            status_frame, text="Scans: 0", font=('Arial', 12), fg='#CCCCCC', bg='#2a2a2a'
        )
        self.parent.scan_count_label.pack(side=tk.RIGHT)

        # Main content area
        content_frame = tk.Frame(self.parent.root, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Left panel - Network list
        left_frame = tk.Frame(content_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(
            left_frame,
            text="📡 Detected Networks",
            font=('Arial', 14, 'bold'),
            fg='#00FFFF',
            bg='#2a2a2a',
        ).pack(pady=10)

        # Network listbox with scrollbar
        list_frame = tk.Frame(left_frame, bg='#2a2a2a')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.parent.network_listbox = tk.Listbox(
            list_frame, bg='black', fg='#00FF00', font=('Courier', 11), selectbackground='#444444'
        )
        scrollbar = tk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.parent.network_listbox.yview
        )
        self.parent.network_listbox.configure(yscrollcommand=scrollbar.set)

        self.parent.network_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right panel - Spectrum visualization
        right_frame = tk.Frame(content_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(
            right_frame,
            text="📊 Spectrum Map",
            font=('Arial', 14, 'bold'),
            fg='#00FFFF',
            bg='#2a2a2a',
        ).pack(pady=10)

        # Canvas controls frame
        canvas_controls = tk.Frame(right_frame, bg='#2a2a2a')
        canvas_controls.pack(fill=tk.X, padx=10, pady=(0, 5))

        # Zoom controls
        tk.Label(
            canvas_controls, text="🔍 Zoom:", fg='#CCCCCC', bg='#2a2a2a', font=('Arial', 10)
        ).pack(side=tk.LEFT)

        zoom_out_btn = tk.Button(
            canvas_controls,
            text="−",
            command=self.parent.zoom_out,
            bg='#444444',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=3,
        )
        zoom_out_btn.pack(side=tk.LEFT, padx=(5, 2))

        self.parent.zoom_label = tk.Label(
            canvas_controls, text="100%", fg='#00FFFF', bg='#2a2a2a', font=('Arial', 10), width=6
        )
        self.parent.zoom_label.pack(side=tk.LEFT, padx=2)

        zoom_in_btn = tk.Button(
            canvas_controls,
            text="+",
            command=self.parent.zoom_in,
            bg='#444444',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=3,
        )
        zoom_in_btn.pack(side=tk.LEFT, padx=(2, 10))

        # Reset view button
        reset_btn = tk.Button(
            canvas_controls,
            text="🎯 Reset View",
            command=self.parent.reset_view,
            bg='#006600',
            fg='white',
            font=('Arial', 10),
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        # Mapping mode toggle
        self.parent.mapping_mode = tk.BooleanVar(value=True)
        mapping_check = tk.Checkbutton(
            canvas_controls,
            text="🗺️ Room Mapping",
            variable=self.parent.mapping_mode,
            command=self.parent.toggle_mapping_mode,
            fg='#CCCCCC',
            bg='#2a2a2a',
            selectcolor='#444444',
            font=('Arial', 10),
        )
        mapping_check.pack(side=tk.RIGHT, padx=5)

        # Canvas for spectrum visualization
        self.parent.canvas = tk.Canvas(right_frame, bg='black', width=600, height=500)
        self.parent.canvas.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

        # Bind mouse events for pan and zoom
        self.parent.canvas.bind("<Button-1>", self.parent.on_canvas_click)
        self.parent.canvas.bind("<B1-Motion>", self.parent.on_canvas_drag)
        self.parent.canvas.bind("<MouseWheel>", self.parent.on_canvas_scroll)
        self.parent.canvas.bind("<Button-3>", self.parent.on_canvas_right_click)

        # Bottom panel - Details
        bottom_frame = tk.Frame(self.parent.root, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            bottom_frame,
            text="📋 Network Details",
            font=('Arial', 12, 'bold'),
            fg='#00FFFF',
            bg='#2a2a2a',
        ).pack(pady=(10, 5))

        self.parent.details_text = scrolledtext.ScrolledText(
            bottom_frame,
            height=8,
            bg='black',
            fg='#FFFF00',
            font=('Courier', 10),
            insertbackground='#FFFF00',
        )
        self.parent.details_text.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Bind listbox selection
        self.parent.network_listbox.bind('<<ListboxSelect>>', self.parent.on_network_select)
        self.parent.network_listbox.bind('<Button-1>', self.parent.on_network_click)

        # Initialize with welcome message
        self.parent.details_text.insert(
            1.0,
            """
🌊 RF SPECTRUM LIDAR ROOM MAPPER
===============================

Welcome to the Live RF Spectrum Viewer!

📡 INSTRUCTIONS:
• Networks will appear automatically in the left panel
• Click on any network to see detailed analysis
• Use zoom controls to explore the spectrum map
• Toggle between LIDAR mapping and traditional view

🎮 CONTROLS:
• Left click: Select network for details
• Mouse wheel: Zoom in/out on spectrum map
• Drag: Pan around the environment
• Right click: Clear mapping data

⚡ FEATURES:
• Real-time network detection
• Physics-based distance calculations
• Security analysis and recommendations
• RF propagation modeling
• LIDAR-style environment mapping

Click on a network in the list above to see comprehensive analysis!
        """,
        )

    def draw_3d_environment(self, canvas, center_x, center_y, max_radius, width, height):
        """Draw the 3D environment base."""
        grid_color = "#333333"

        # Perspective grid lines
        for i in range(-3, 4):
            y_near = center_y + i * 20
            y_far = center_y + i * 10
            x_left_near = center_x - max_radius
            x_right_near = center_x + max_radius
            x_left_far = center_x - max_radius // 2
            x_right_far = center_x + max_radius // 2

            canvas.create_line(x_left_near, y_near, x_left_far, y_far, fill=grid_color, width=1)
            canvas.create_line(x_right_near, y_near, x_right_far, y_far, fill=grid_color, width=1)

        # Vertical grid lines (perspective)
        for i in range(-3, 4):
            x_near = center_x + i * 30
            x_far = center_x + i * 15
            y_near = center_y + max_radius // 2
            y_far = center_y - max_radius // 3

            canvas.create_line(x_near, y_near, x_far, y_far, fill=grid_color, width=1)

        # Draw horizon line
        horizon_y = center_y - max_radius // 3
        canvas.create_line(0, horizon_y, width, horizon_y, fill="#444444", width=2, dash=(5, 5))

        # Draw our position (center)
        canvas.create_oval(
            center_x - 8,
            center_y - 8,
            center_x + 8,
            center_y + 8,
            fill="#FFD700",
            outline="#FFF",
            width=2,
        )
        canvas.create_text(
            center_x, center_y - 20, text="YOU", fill="#FFD700", font=('Arial', 10, 'bold')
        )

        # Draw range circles
        for radius in [max_radius // 3, max_radius * 2 // 3, max_radius]:
            canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline="#444444",
                width=1,
                dash=(3, 3),
            )

    def draw_network_in_3d(self, canvas, network, index, center_x, center_y, max_radius):
        """Draw a network positioned in 3D space."""
        signal = network['signal_percent']

        # Distance from signal strength
        if signal > 80:
            distance = max_radius * 0.3
        elif signal > 60:
            distance = max_radius * 0.5
        elif signal > 40:
            distance = max_radius * 0.7
        else:
            distance = max_radius * 0.9

        # Angle based on channel and index
        angle = (network['channel'] * 30 + index * 45) % 360
        angle_rad = math.radians(angle)

        # Calculate 3D position
        x = center_x + distance * math.cos(angle_rad)
        y = center_y + distance * math.sin(angle_rad) * 0.6

        # Height based on frequency
        if network['band'] == '5GHz':
            height_offset = -15
            color = "#4444FF"
            band_symbol = "5G"
        else:
            height_offset = 5
            color = "#FF4444"
            band_symbol = "2G"

        y += height_offset

        # Draw network tower/building representation
        tower_height = signal // 4
        base_size = max(8, signal // 10)

        canvas.create_rectangle(
            x - base_size // 2,
            y,
            x + base_size // 2,
            y + tower_height,
            fill=color,
            outline="#FFF",
            width=1,
        )

        # Draw signal waves
        for wave in range(1, 4):
            wave_radius = base_size + wave * 8
            wave_color = color if wave == 1 else "#666666"
            canvas.create_oval(
                x - wave_radius,
                y - wave_radius // 2,
                x + wave_radius,
                y + wave_radius // 2,
                outline=wave_color,
                width=1,
                dash=(2, 4),
            )

        # Draw network info
        info_y = y - tower_height - 5
        ssid_short = network['ssid'][:8] + "..." if len(network['ssid']) > 8 else network['ssid']

        canvas.create_text(x, info_y, text=ssid_short, fill="#FFF", font=('Arial', 8, 'bold'))
        canvas.create_text(
            x, info_y - 12, text=f"{signal}% {band_symbol}", fill=color, font=('Arial', 7)
        )
        canvas.create_text(
            x, info_y - 22, text=f"Ch{network['channel']}", fill="#CCCCCC", font=('Arial', 6)
        )

        # Draw connection line for strong signals
        if signal > 60:
            canvas.create_line(
                center_x,
                center_y,
                x,
                y + tower_height // 2,
                fill=color,
                width=1,
                dash=(2, 2),
                stipple="gray25",
            )

    def draw_3d_legend(self, canvas, width, height):
        """Draw legend and compass for 3D view."""
        # Compass
        compass_x = width - 60
        compass_y = 60
        compass_size = 40

        canvas.create_oval(
            compass_x - compass_size // 2,
            compass_y - compass_size // 2,
            compass_x + compass_size // 2,
            compass_y + compass_size // 2,
            outline="#666666",
            width=2,
        )

        directions = [
            ("N", 0, -compass_size // 2 + 5),
            ("E", compass_size // 2 - 5, 0),
            ("S", 0, compass_size // 2 - 5),
            ("W", -compass_size // 2 + 5, 0),
        ]

        for direction, dx, dy in directions:
            canvas.create_text(
                compass_x + dx,
                compass_y + dy,
                text=direction,
                fill="#FFF",
                font=('Arial', 10, 'bold'),
            )

        canvas.create_line(
            compass_x,
            compass_y,
            compass_x,
            compass_y - compass_size // 3,
            fill="#FF0000",
            width=3,
            arrow=tk.LAST,
        )

        # Legend
        legend_x = 20
        legend_y = height - 100

        canvas.create_rectangle(
            legend_x - 5,
            legend_y - 5,
            legend_x + 150,
            legend_y + 80,
            fill="#000000",
            outline="#666666",
            width=1,
        )

        canvas.create_text(
            legend_x + 70,
            legend_y + 5,
            text="3D Spectrum Map",
            fill="#00FFFF",
            font=('Arial', 10, 'bold'),
        )

        legend_items = [
            ("🔴 2.4GHz Networks", "#FF4444"),
            ("🔵 5GHz Networks", "#4444FF"),
            ("⭐ Your Position", "#FFD700"),
            ("📶 Signal Strength = Distance", "#CCCCCC"),
        ]

        for i, (text, color) in enumerate(legend_items):
            y_pos = legend_y + 20 + i * 12
            canvas.create_text(
                legend_x + 5, y_pos, text=text, anchor="w", fill=color, font=('Arial', 8)
            )

        canvas.create_text(
            legend_x + 70,
            legend_y + 70,
            text="Rings: Close → Medium → Far",
            fill="#666666",
            font=('Arial', 7),
        )

    def draw_mapping_ui(
        self, canvas, width, height, zoom_level, environment_points, wave_reflections, mapping_mode
    ):
        """Draw mapping UI elements."""
        # Zoom indicator
        zoom_text = f"Zoom: {int(zoom_level * 100)}%"
        canvas.create_text(width - 80, 20, text=zoom_text, fill="#00FFFF", font=('Arial', 10))

        # Mapping stats
        stats_text = f"Obstacles: {len(environment_points)}\nReflections: {len(wave_reflections)}"
        canvas.create_text(
            20, height - 40, text=stats_text, anchor="w", fill="#CCCCCC", font=('Arial', 9)
        )

        # Mode indicator
        mode_text = "🗺️ LIDAR Mapping Mode" if mapping_mode else "📊 Traditional View"
        canvas.create_text(
            width // 2, 20, text=mode_text, fill="#00FFFF", font=('Arial', 12, 'bold')
        )
