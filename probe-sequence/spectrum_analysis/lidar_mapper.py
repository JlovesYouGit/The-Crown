#!/usr/bin/env python3
"""
LIDAR Mapping Module - Handles environment mapping and visualization
"""

import math
import tkinter as tk


class LidarMapper:
    """Handles LIDAR-style room mapping and environment visualization."""

    def __init__(self):
        self.environment_points = []
        self.wave_reflections = []
        self.room_structure = {}

    def update_environment_mapping(self, networks):
        """Update environment mapping based on RF signal analysis."""
        for network in networks:
            self.analyze_rf_reflections(network)
            self.detect_obstacles(network)

    def analyze_rf_reflections(self, network):
        """Analyze RF wave reflections to map environment."""
        signal = network['signal_percent']

        if signal < 70:
            angle = (network['channel'] * 30) % 360
            distance = 100 - signal

            reflection_point = {
                'angle': angle,
                'distance': distance,
                'strength': signal,
                'frequency': network['frequency_mhz'],
                'type': 'wall' if signal < 40 else 'furniture',
            }

            if not any(abs(r['angle'] - angle) < 15 for r in self.wave_reflections):
                self.wave_reflections.append(reflection_point)

    def detect_obstacles(self, network):
        """Detect obstacles based on signal patterns."""
        signal = network['signal_percent']

        if signal < 50:
            angle = (network['channel'] * 30 + hash(network['bssid']) % 360) % 360
            distance = (100 - signal) * 0.8

            obstacle = {
                'x': distance * math.cos(math.radians(angle)),
                'y': distance * math.sin(math.radians(angle)),
                'type': 'wall' if signal < 30 else 'obstacle',
                'confidence': (100 - signal) / 100,
            }

            if not any(
                abs(o['x'] - obstacle['x']) < 10 and abs(o['y'] - obstacle['y']) < 10
                for o in self.environment_points
            ):
                self.environment_points.append(obstacle)

    def draw_lidar_room_mapping(self, canvas, center_x, center_y, width, height, scale):
        """Draw LIDAR-style room mapping visualization."""
        self.draw_scanning_grid(canvas, center_x, center_y, scale)
        self.draw_scanner_position(canvas, center_x, center_y, scale)
        self.draw_environment_obstacles(canvas, center_x, center_y, scale)
        self.draw_rf_wave_paths(canvas, center_x, center_y, scale)
        self.draw_estimated_room_boundaries(canvas, center_x, center_y, scale)

    def draw_scanning_grid(self, canvas, center_x, center_y, scale):
        """Draw VR-style scanning grid."""
        grid_size = int(30 * scale)
        grid_color = "#1a4d1a"

        for i in range(-10, 11):
            x = center_x + i * grid_size
            y = center_y + i * grid_size

            if 0 <= x <= canvas.winfo_width():
                canvas.create_line(
                    x, 0, x, canvas.winfo_height(), fill=grid_color, width=1, dash=(2, 4)
                )

            if 0 <= y <= canvas.winfo_height():
                canvas.create_line(
                    0, y, canvas.winfo_width(), y, fill=grid_color, width=1, dash=(2, 4)
                )

        for radius in [50, 100, 150]:
            scaled_radius = int(radius * scale)
            canvas.create_oval(
                center_x - scaled_radius,
                center_y - scaled_radius,
                center_x + scaled_radius,
                center_y + scaled_radius,
                outline="#2d5a2d",
                width=1,
                dash=(3, 3),
            )

    def draw_scanner_position(self, canvas, center_x, center_y, scale):
        """Draw our scanner position like VR headset."""
        size = int(12 * scale)

        canvas.create_oval(
            center_x - size,
            center_y - size,
            center_x + size,
            center_y + size,
            fill="#00FF00",
            outline="#FFFFFF",
            width=2,
        )

        canvas.create_line(
            center_x,
            center_y,
            center_x,
            center_y - int(20 * scale),
            fill="#00FF00",
            width=3,
            arrow=tk.LAST,
        )

        canvas.create_text(
            center_x,
            center_y - int(35 * scale),
            text="RF SCANNER",
            fill="#00FF00",
            font=('Arial', int(8 * scale), 'bold'),
        )

    def draw_environment_obstacles(self, canvas, center_x, center_y, scale):
        """Draw detected obstacles and walls."""
        for obstacle in self.environment_points:
            x = center_x + int(obstacle['x'] * scale)
            y = center_y + int(obstacle['y'] * scale)

            if obstacle['type'] == 'wall':
                color = "#FF6666"
                size = int(8 * scale)
            else:
                color = "#FFAA66"
                size = int(6 * scale)

            canvas.create_oval(
                x - size // 2,
                y - size // 2,
                x + size // 2,
                y + size // 2,
                fill=color,
                outline="#FFFFFF",
                width=1,
            )

            confidence_radius = int(obstacle['confidence'] * 15 * scale)
            canvas.create_oval(
                x - confidence_radius,
                y - confidence_radius,
                x + confidence_radius,
                y + confidence_radius,
                outline=color,
                width=1,
                dash=(1, 2),
            )

    def draw_rf_wave_paths(self, canvas, center_x, center_y, scale):
        """Draw RF wave propagation paths."""
        for reflection in self.wave_reflections:
            angle_rad = math.radians(reflection['angle'])
            distance = int(reflection['distance'] * scale)

            end_x = center_x + distance * math.cos(angle_rad)
            end_y = center_y + distance * math.sin(angle_rad)

            color = "#FF4444" if reflection['frequency'] < 2500 else "#4444FF"

            canvas.create_line(center_x, center_y, end_x, end_y, fill=color, width=2, dash=(4, 2))

            canvas.create_oval(
                end_x - 4, end_y - 4, end_x + 4, end_y + 4, fill=color, outline="#FFFFFF", width=1
            )

    def draw_estimated_room_boundaries(self, canvas, center_x, center_y, scale):
        """Draw estimated room boundaries based on RF analysis."""
        if len(self.environment_points) < 3:
            return

        wall_points = [p for p in self.environment_points if p['type'] == 'wall']

        if len(wall_points) >= 3:
            for i in range(len(wall_points)):
                p1 = wall_points[i]
                p2 = wall_points[(i + 1) % len(wall_points)]

                x1 = center_x + int(p1['x'] * scale)
                y1 = center_y + int(p1['y'] * scale)
                x2 = center_x + int(p2['x'] * scale)
                y2 = center_y + int(p2['y'] * scale)

                canvas.create_line(x1, y1, x2, y2, fill="#666666", width=2, dash=(5, 5))
