#!/usr/bin/env python3
"""
Interference Analysis Module - Handles RF interference and channel analysis
"""


class InterferenceAnalyzer:
    """Handles interference analysis and channel congestion assessment."""

    def __init__(self, networks):
        self.networks = networks

    def get_interference_risk(self, network):
        """Assess interference risk."""
        same_channel = [
            n
            for n in self.networks
            if n['channel'] == network['channel'] and n['bssid'] != network['bssid']
        ]

        if len(same_channel) > 0:
            return f"High ({len(same_channel)} other networks on same channel)"

        if network['band'] == '2.4GHz':
            adjacent = [
                n
                for n in self.networks
                if abs(n['channel'] - network['channel']) <= 2 and n['bssid'] != network['bssid']
            ]
            if len(adjacent) > 0:
                return f"Medium ({len(adjacent)} networks on adjacent channels)"

        return "Low"

    def analyze_channel_congestion(self, network):
        """Analyze channel congestion level."""
        channel = network['channel']
        band = network['band']

        same_channel = [n for n in self.networks if n['channel'] == channel and n['band'] == band]

        if len(same_channel) == 1:
            return "🟢 Clear"
        elif len(same_channel) <= 2:
            return "🟡 Light"
        elif len(same_channel) <= 4:
            return "🟠 Moderate"
        else:
            return "🔴 Heavy"

    def count_cochannel_networks(self, network):
        """Count networks on the same channel."""
        same_channel = [
            n
            for n in self.networks
            if n['channel'] == network['channel']
            and n['band'] == network['band']
            and n['bssid'] != network['bssid']
        ]
        return len(same_channel)

    def analyze_adjacent_channels(self, network):
        """Analyze impact from adjacent channels."""
        if network['band'] != '2.4GHz':
            return "🟢 No Impact (5GHz)"

        channel = network['channel']
        adjacent_channels = []

        for n in self.networks:
            if (
                n['band'] == '2.4GHz'
                and n['bssid'] != network['bssid']
                and abs(n['channel'] - channel) <= 4
            ):
                adjacent_channels.append(n)

        if len(adjacent_channels) == 0:
            return "🟢 No Adjacent Interference"
        elif len(adjacent_channels) <= 2:
            return f"🟡 Light ({len(adjacent_channels)} networks)"
        else:
            return f"🔴 Heavy ({len(adjacent_channels)} networks)"
