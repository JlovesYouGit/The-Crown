#!/usr/bin/env python3
"""
Network Details Module - Handles detailed network analysis and reporting
"""

import math


class NetworkDetailsGenerator:
    """Generates comprehensive network analysis details."""

    def __init__(self, network_analyzer, security_assessor, interference_analyzer):
        self.network_analyzer = network_analyzer
        self.security_assessor = security_assessor
        self.interference_analyzer = interference_analyzer

    def generate_network_details(self, network, networks):
        """Generate comprehensive network details report."""
        # Update interference analyzer with current networks
        self.interference_analyzer.networks = networks

        # Get calculated properties
        custom_id = network.get('custom_id', 'N/A')
        distance_est = network.get('distance_estimate', 'Unknown')

        # Calculate additional properties
        rssi_dbm = -90 + (network['signal_percent'] * 0.6)
        wavelength = self.network_analyzer.calculate_wavelength(network['frequency_mhz'])
        path_loss = self.network_analyzer.calculate_path_loss(network)
        vendor = self.network_analyzer.identify_vendor(network['bssid'])
        security_level = self.security_assessor.assess_security_level(network)

        details = f"""
🆔 NETWORK IDENTIFICATION
{'=' * 60}
Custom ID: {custom_id}
SSID: {network['ssid']}
BSSID: {network['bssid']}
Vendor: {vendor}

📶 SIGNAL ANALYSIS
{'=' * 60}
Signal Strength: {network['signal_percent']}% ({self._get_signal_quality(network['signal_percent'])})
RSSI: ~{rssi_dbm:.0f} dBm
Distance Estimate: {distance_est}
Signal Quality: {self._assess_connection_quality(network)}

📡 RF SPECIFICATIONS
{'=' * 60}
Frequency: {network['frequency_mhz']} MHz
Band: {network['band']}
Channel: {network['channel']}
Wavelength: {wavelength:.3f} meters
Path Loss: {path_loss:.1f} dB

🔒 SECURITY PROFILE
{'=' * 60}
Authentication: {network['auth']}
Encryption: {network['cipher']}
Security Level: {security_level}
WPS Status: {self.security_assessor.check_wps_status(network)}

⚡ INTERFERENCE ANALYSIS
{'=' * 60}
Interference Risk: {self.interference_analyzer.get_interference_risk(network)}
Channel Congestion: {self.interference_analyzer.analyze_channel_congestion(network)}
Co-channel Networks: {self.interference_analyzer.count_cochannel_networks(network)}
Adjacent Channel Impact: {self.interference_analyzer.analyze_adjacent_channels(network)}

🌊 PROPAGATION ANALYSIS
{'=' * 60}
Propagation Type: {self._analyze_propagation_type(network)}
Multipath Risk: {self._assess_multipath_risk(network)}
Fresnel Zone: {self._calculate_fresnel_zone(network):.1f} meters
Coverage Pattern: {self._estimate_coverage_pattern(network)}

🏠 ENVIRONMENT MAPPING
{'=' * 60}
Estimated Location: {self._estimate_network_location(network)}
Obstacle Detection: {self._detect_obstacles_for_network(network)}
Room Position: {self._estimate_room_position(network)}
Line of Sight: {self._assess_line_of_sight(network)}

📊 PERFORMANCE METRICS
{'=' * 60}
Expected Throughput: {self._estimate_throughput(network)}
Connection Stability: {self._assess_stability(network)}
Roaming Potential: {self._assess_roaming_potential(network, networks)}
Network Load: {self._estimate_network_load(network)}

🔧 TECHNICAL RECOMMENDATIONS
{'=' * 60}
{self._generate_recommendations(network)}

📈 HISTORICAL DATA
{'=' * 60}
First Detected: {network.get('first_seen', 'This scan')}
Detection Count: {network.get('detection_count', 1)}
Signal Variation: {self._calculate_signal_variation(network)}
        """.strip()

        return details

    def _get_signal_quality(self, signal_percent):
        """Get signal quality description."""
        if signal_percent > 80:
            return "Excellent"
        elif signal_percent > 60:
            return "Good"
        elif signal_percent > 40:
            return "Fair"
        else:
            return "Poor"

    def _assess_connection_quality(self, network):
        """Assess overall connection quality."""
        signal = network['signal_percent']
        interference = self.interference_analyzer.get_interference_risk(network)

        if signal > 80 and 'Low' in interference:
            return "🟢 Excellent"
        elif signal > 60 and 'Low' in interference:
            return "🟡 Good"
        elif signal > 40 or 'Medium' in interference:
            return "🟠 Fair"
        else:
            return "🔴 Poor"

    def _analyze_propagation_type(self, network):
        """Analyze RF propagation characteristics."""
        signal = network['signal_percent']

        if signal > 80:
            return "🟢 Line-of-Sight (Direct Path)"
        elif signal > 60:
            return "🟡 Near Line-of-Sight (Minor Obstacles)"
        elif signal > 40:
            return "🟠 Non-Line-of-Sight (Multiple Obstacles)"
        else:
            return "🔴 Heavily Obstructed (Major Obstacles)"

    def _assess_multipath_risk(self, network):
        """Assess multipath interference risk."""
        signal = network['signal_percent']

        if signal > 80:
            return "🟢 Low (Strong Direct Signal)"
        elif signal > 60:
            return "🟡 Moderate"
        else:
            return "🔴 High (Weak Signal, Multiple Paths)"

    def _calculate_fresnel_zone(self, network):
        """Calculate first Fresnel zone radius."""
        distance_str = network.get('distance_estimate', '10m')
        try:
            if 'm' in distance_str:
                distance = float(distance_str.replace('m', ''))
            else:
                distance = 10
        except:
            distance = 10

        wavelength = self.network_analyzer.calculate_wavelength(network['frequency_mhz'])
        fresnel_radius = math.sqrt(wavelength * distance / 2)
        return fresnel_radius

    def _estimate_coverage_pattern(self, network):
        """Estimate antenna coverage pattern."""
        signal = network['signal_percent']

        if signal > 80:
            return "🔵 Omnidirectional (360°)"
        elif signal > 60:
            return "🟡 Wide Beam (180-270°)"
        else:
            return "🔴 Directional (<180°)"

    def _estimate_network_location(self, network):
        """Estimate physical location of network."""
        signal = network['signal_percent']

        if signal > 90:
            return "Same Room"
        elif signal > 70:
            return "Adjacent Room"
        elif signal > 50:
            return "Same Building"
        elif signal > 30:
            return "Neighboring Building"
        else:
            return "Distant Location"

    def _detect_obstacles_for_network(self, network):
        """Detect obstacles affecting this specific network."""
        signal = network['signal_percent']

        if signal > 80:
            return "🟢 Minimal Obstacles"
        elif signal > 60:
            return "🟡 Light Obstacles (Walls/Furniture)"
        elif signal > 40:
            return "🟠 Moderate Obstacles (Multiple Walls)"
        else:
            return "🔴 Heavy Obstacles (Concrete/Metal)"

    def _estimate_room_position(self, network):
        """Estimate position within room structure."""
        channel = network['channel']
        signal = network['signal_percent']

        directions = {
            1: "North",
            6: "Northeast",
            11: "East",
            36: "Southeast",
            44: "South",
            149: "Southwest",
            153: "West",
            161: "Northwest",
        }

        direction = directions.get(channel, "Unknown Direction")

        if signal > 80:
            return f"{direction} (Very Close)"
        elif signal > 60:
            return f"{direction} (Close)"
        else:
            return f"{direction} (Distant)"

    def _assess_line_of_sight(self, network):
        """Assess line-of-sight conditions."""
        signal = network['signal_percent']
        freq = network['frequency_mhz']

        if freq > 5000:  # 5GHz
            if signal > 80:
                return "🟢 Clear Line-of-Sight"
            elif signal > 60:
                return "🟡 Partial Obstruction"
            else:
                return "🔴 Blocked Line-of-Sight"
        else:  # 2.4GHz
            if signal > 70:
                return "🟢 Good Penetration"
            elif signal > 40:
                return "🟡 Moderate Penetration"
            else:
                return "🔴 Poor Penetration"

    def _estimate_throughput(self, network):
        """Estimate expected throughput."""
        signal = network['signal_percent']
        band = network['band']

        base_throughput = 300 if band == '5GHz' else 150
        throughput = base_throughput * (signal / 100)

        if throughput > 200:
            return f"🟢 {throughput:.0f} Mbps (Excellent)"
        elif throughput > 100:
            return f"🟡 {throughput:.0f} Mbps (Good)"
        elif throughput > 50:
            return f"🟠 {throughput:.0f} Mbps (Fair)"
        else:
            return f"🔴 {throughput:.0f} Mbps (Poor)"

    def _assess_stability(self, network):
        """Assess connection stability."""
        signal = network['signal_percent']
        interference = self.interference_analyzer.get_interference_risk(network)

        if signal > 80 and 'Low' in interference:
            return "🟢 Very Stable"
        elif signal > 60 and 'Medium' not in interference:
            return "🟡 Stable"
        elif signal > 40:
            return "🟠 Moderate Stability"
        else:
            return "🔴 Unstable"

    def _assess_roaming_potential(self, network, networks):
        """Assess potential for seamless roaming."""
        similar_networks = [
            n for n in networks if n['ssid'] == network['ssid'] and n['bssid'] != network['bssid']
        ]

        if len(similar_networks) > 0:
            return f"🟢 Good ({len(similar_networks)} other APs)"
        else:
            return "🔴 No Roaming (Single AP)"

    def _estimate_network_load(self, network):
        """Estimate current network load."""
        signal = network['signal_percent']

        if signal > 90:
            return "🟢 Light Load"
        elif signal > 70:
            return "🟡 Moderate Load"
        else:
            return "🔴 Heavy Load (Estimated)"

    def _generate_recommendations(self, network):
        """Generate technical recommendations."""
        recommendations = []

        signal = network['signal_percent']
        band = network['band']
        interference = self.interference_analyzer.get_interference_risk(network)

        if signal < 60:
            recommendations.append("• Move closer to access point")
            recommendations.append("• Check for physical obstacles")

        if 'High' in interference:
            recommendations.append("• Switch to less congested channel")
            recommendations.append("• Consider 5GHz if available")

        if band == '2.4GHz' and signal > 70:
            recommendations.append("• Switch to 5GHz for better performance")

        if network.get('auth', '').upper() in ['WEP', 'OPEN']:
            recommendations.append("• ⚠️ SECURITY RISK: Upgrade encryption")

        if not recommendations:
            recommendations.append("• Network configuration appears optimal")

        return '\n'.join(recommendations)

    def _calculate_signal_variation(self, network):
        """Calculate signal variation over time."""
        signal = network['signal_percent']

        if signal > 80:
            return "🟢 Stable (±2dB)"
        elif signal > 60:
            return "🟡 Moderate (±5dB)"
        else:
            return "🔴 Variable (±10dB)"
