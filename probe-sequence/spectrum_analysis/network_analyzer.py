#!/usr/bin/env python3
"""
Network Analysis Module - Handles network data analysis and calculations
"""

import math
import time


class NetworkAnalyzer:
    """Handles network analysis, calculations, and assessments."""

    def __init__(self):
        self.network_registry = {}  # bssid -> {first_seen, last_seen, detection_count, stable_id}

    def get_stable_id(self, network: dict) -> str:
        """Return a stable human-friendly ID derived from BSSID/band/channel."""
        bssid = network.get('bssid') or ''
        # Use last 3 bytes of MAC as suffix
        suffix = ''.join(bssid.split(':')[-3:]) or 'UNKNOWN'
        band_code = (
            '2'
            if network.get('band') == '2.4GHz'
            else '5'
            if network.get('band') == '5GHz'
            else '6'
        )
        ch = int(network.get('channel') or 0)
        return f"{band_code}{ch:02d}-{suffix.upper()}"

    def enrich_with_history(self, networks: list) -> None:
        """Populate networks with stable IDs and maintain per-BSSID history."""
        now_ts = time.strftime('%Y-%m-%d %H:%M:%S')
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
            # Copy registry fields onto network for display
            net['custom_id'] = entry['stable_id']
            net['first_seen'] = entry['first_seen']
            net['last_seen'] = entry['last_seen']
            net['detection_count'] = entry['detection_count']

    def calculate_network_distance(self, signal_percent, frequency_mhz):
        """Calculate estimated distance based on signal strength and frequency."""
        rssi_dbm = -90 + (signal_percent * 0.6)
        tx_power = 20
        path_loss = tx_power - rssi_dbm
        frequency_ghz = frequency_mhz / 1000

        try:
            distance_m = 10 ** ((path_loss - 20 * math.log10(frequency_ghz) - 32.44) / 20)

            if distance_m < 1:
                return f"{distance_m * 100:.0f}cm"
            elif distance_m < 10:
                return f"{distance_m:.1f}m"
            elif distance_m < 100:
                return f"{distance_m:.0f}m"
            else:
                return f"{distance_m / 1000:.1f}km"
        except:
            if signal_percent > 80:
                return "<5m"
            elif signal_percent > 60:
                return "5-20m"
            elif signal_percent > 40:
                return "20-50m"
            else:
                return ">50m"

    def calculate_wavelength(self, frequency_mhz):
        """Calculate wavelength from frequency."""
        c = 3e8  # Speed of light
        return c / (frequency_mhz * 1e6)

    def calculate_path_loss(self, network):
        """Calculate estimated path loss."""
        network['frequency_mhz'] / 1000
        signal_dbm = -90 + (network['signal_percent'] * 0.6)
        tx_power = 20
        return tx_power - signal_dbm

    def identify_vendor(self, bssid):
        """Identify network vendor from BSSID/MAC address."""
        if not bssid or len(bssid) < 8:
            return "Unknown"

        oui_db = {
            'c8:70:23': 'Netgear',
            '80:69:1a': 'Linksys/Cisco',
            '00:1b:63': 'Apple',
            '00:26:bb': 'Apple',
            'ac:87:a3': 'Apple',
            '00:50:56': 'VMware',
            '08:00:27': 'Oracle VirtualBox',
            '00:0c:29': 'VMware',
            '00:15:5d': 'Microsoft Hyper-V',
            'fc:73:fb': 'Claro/ISP Router',
            '00:24:a5': 'Buffalo',
            '00:22:6b': 'D-Link',
            '00:1f:3f': 'TP-Link',
            '00:14:d1': 'TRENDnet',
        }

        oui = bssid[:8].lower()
        return oui_db.get(oui, f"Unknown ({oui.upper()})")
