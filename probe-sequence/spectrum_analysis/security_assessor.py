#!/usr/bin/env python3
"""
Security Assessment Module - Handles network security analysis
"""


class SecurityAssessor:
    """Handles security assessment and analysis of networks."""

    def assess_security_level(self, network):
        """Assess overall security level of the network."""
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

    def check_wps_status(self, network):
        """Check WPS (WiFi Protected Setup) status."""
        auth = network.get('auth', '').upper()
        if 'WPS' in auth:
            return "🟠 Enabled (Security Risk)"
        else:
            return "🟢 Likely Disabled"

    def generate_security_recommendations(self, network):
        """Generate security-specific recommendations."""
        recommendations = []
        auth = network.get('auth', '').upper()

        if auth in ['WEP', 'OPEN']:
            recommendations.append("• ⚠️ CRITICAL: Upgrade to WPA2/WPA3")
            recommendations.append("• Current encryption is easily compromised")

        if 'WPS' in auth:
            recommendations.append("• Disable WPS to prevent PIN attacks")

        if 'WPA2' in auth and 'WPA3' not in auth:
            recommendations.append("• Consider upgrading to WPA3 if supported")

        return recommendations
