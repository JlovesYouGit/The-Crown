"""Cross-platform WiFi scanner with Windows as primary target and Linux/macOS fallbacks."""

import platform
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class WiFiScanError(Exception):
    """Base exception for WiFi scanning errors."""

    pass


class WLANServiceDisabledError(WiFiScanError):
    """Raised when WLAN service is disabled."""

    pass


class NoWirelessInterfacesError(WiFiScanError):
    """Raised when no wireless interfaces are found."""

    pass


@dataclass
class AccessPoint:
    """WiFi access point information."""

    ssid: str
    bssid: str
    signal_percent: int
    channel: int
    auth: str
    cipher: str
    band: str
    frequency_mhz: int
    seen_at: datetime


def _channel_to_frequency(channel: int) -> int:
    """Convert channel number to frequency in MHz."""
    # 2.4 GHz band (channels 1-14)
    if 1 <= channel <= 14:
        if channel == 14:
            return 2484
        return 2412 + (channel - 1) * 5

    # 5 GHz band (channels 36-165)
    elif 36 <= channel <= 165:
        return 5000 + channel * 5

    # 6 GHz band (channels 1-233, but starting at 5955 MHz)
    elif channel >= 200:  # Approximate 6 GHz detection
        return 5955 + (channel - 1) * 20

    # Fallback for unknown channels
    return 2412


def _get_band_from_frequency(freq_mhz: int) -> str:
    """Determine WiFi band from frequency."""
    if 2400 <= freq_mhz <= 2500:
        return "2.4GHz"
    elif 5000 <= freq_mhz <= 6000:
        return "5GHz"
    elif freq_mhz >= 5900:
        return "6GHz"
    return "Unknown"


def list_interfaces() -> list[str]:
    """List available wireless interfaces."""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except subprocess.CalledProcessError as e:
        if "not running" in e.stderr or "AutoConfig" in e.stderr:
            raise WLANServiceDisabledError("WLAN AutoConfig service is not running") from e
        raise WiFiScanError(f"Failed to list interfaces: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise WiFiScanError("Timeout listing interfaces") from e

    interfaces = []
    lines = result.stdout.split("\n")

    for line in lines:
        line = line.strip()
        if line.startswith("Name") and ":" in line:
            # Extract interface name after the colon
            name = line.split(":", 1)[1].strip()
            if name:
                interfaces.append(name)

    if not interfaces:
        raise NoWirelessInterfacesError("No wireless interfaces found")

    return interfaces


def scan_wifi(interface: Optional[str] = None, timeout: float = 10.0) -> list[AccessPoint]:
    """Scan for WiFi access points."""
    cmd = ["netsh", "wlan", "show", "networks", "mode=bssid"]
    if interface:
        cmd.extend([f'interface="{interface}"'])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
    except subprocess.CalledProcessError as e:
        if "not running" in e.stderr or "AutoConfig" in e.stderr:
            raise WLANServiceDisabledError("WLAN AutoConfig service is not running") from e
        if interface and ("not found" in e.stderr or "does not exist" in e.stderr):
            raise WiFiScanError(f"Interface '{interface}' not found") from e
        raise WiFiScanError(f"Failed to scan WiFi: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise WiFiScanError("Timeout during WiFi scan") from e

    return _parse_netsh_output(result.stdout)


def _parse_netsh_output(output: str) -> list[AccessPoint]:
    """Parse netsh wlan show networks output."""
    access_points = []
    lines = output.split("\n")
    current_ssid = None
    current_bssids = []
    seen_at = datetime.now()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # New SSID block
        if line.startswith("SSID") and ":" in line:
            # Process previous SSID if exists
            if current_ssid and current_bssids:
                for bssid_info in current_bssids:
                    access_points.append(_create_access_point(current_ssid, bssid_info, seen_at))

            # Start new SSID
            current_ssid = line.split(":", 1)[1].strip()
            current_bssids = []

        # BSSID information
        elif line.startswith("BSSID") and ":" in line:
            bssid = line.split(":", 1)[1].strip()
            bssid_info = {"bssid": bssid}

            # Look ahead for related information
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(("SSID", "BSSID")):
                info_line = lines[j].strip()
                if ":" in info_line:
                    key, value = info_line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if "signal" in key:
                        # Extract percentage from signal (e.g., "85%")
                        signal_match = re.search(r"(\d+)%", value)
                        if signal_match:
                            bssid_info["signal"] = int(signal_match.group(1))
                    elif "channel" in key:
                        # Extract channel number
                        channel_match = re.search(r"\d+", value)
                        if channel_match:
                            bssid_info["channel"] = int(channel_match.group())
                    elif "authentication" in key:
                        bssid_info["auth"] = value
                    elif "encryption" in key:
                        bssid_info["cipher"] = value
                j += 1

            current_bssids.append(bssid_info)
            i = j - 1

        i += 1

    # Process final SSID
    if current_ssid and current_bssids:
        for bssid_info in current_bssids:
            access_points.append(_create_access_point(current_ssid, bssid_info, seen_at))

    return access_points


def _create_access_point(ssid: str, bssid_info: dict, seen_at: datetime) -> AccessPoint:
    """Create AccessPoint from parsed information."""
    channel = bssid_info.get("channel", 1)
    frequency = _channel_to_frequency(channel)
    band = _get_band_from_frequency(frequency)

    return AccessPoint(
        ssid=ssid,
        bssid=bssid_info.get("bssid", ""),
        signal_percent=bssid_info.get("signal", 0),
        channel=channel,
        auth=bssid_info.get("auth", "Unknown"),
        cipher=bssid_info.get("cipher", "Unknown"),
        band=band,
        frequency_mhz=frequency,
        seen_at=seen_at,
    )


def _scan_wifi_linux(timeout: float = 10.0) -> list[AccessPoint]:
    """Scan WiFi on Linux using nmcli."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,CHAN,SECURITY", "device", "wifi", "list"],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        raise WiFiScanError("nmcli command not found - NetworkManager not installed")
    except subprocess.CalledProcessError as e:
        raise WiFiScanError(f"nmcli failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise WiFiScanError("Timeout during Linux WiFi scan")

    return _parse_nmcli_output(result.stdout)


def _parse_nmcli_output(output: str) -> list[AccessPoint]:
    """Parse nmcli WiFi scan output."""
    access_points = []
    seen_at = datetime.now()

    for line in output.strip().split("\n"):
        if not line:
            continue

        parts = line.split(":")
        if len(parts) >= 5:
            ssid = parts[0] if parts[0] else "<Hidden>"
            bssid = parts[1]
            try:
                signal = int(parts[2]) if parts[2] else 0
            except ValueError:
                signal = 0

            try:
                channel = int(parts[3]) if parts[3] else 1
            except ValueError:
                channel = 1

            security = parts[4] if parts[4] else "Open"

            frequency = _channel_to_frequency(channel)
            band = _get_band_from_frequency(frequency)

            access_points.append(
                AccessPoint(
                    ssid=ssid,
                    bssid=bssid,
                    signal_percent=signal,
                    channel=channel,
                    auth=security,
                    cipher=security,
                    band=band,
                    frequency_mhz=frequency,
                    seen_at=seen_at,
                )
            )

    return access_points


def _scan_wifi_macos(timeout: float = 10.0) -> list[AccessPoint]:
    """Scan WiFi on macOS using airport utility."""
    airport_path = (
        "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    )

    try:
        result = subprocess.run(
            [airport_path, "-s"], capture_output=True, text=True, check=True, timeout=timeout
        )
    except FileNotFoundError:
        raise WiFiScanError("airport command not found - not available on this macOS system")
    except subprocess.CalledProcessError as e:
        raise WiFiScanError(f"airport scan failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise WiFiScanError("Timeout during macOS WiFi scan")

    return _parse_airport_output(result.stdout)


def _parse_airport_output(output: str) -> list[AccessPoint]:
    """Parse macOS airport scan output."""
    access_points = []
    seen_at = datetime.now()
    lines = output.strip().split("\n")

    # Skip header line
    for line in lines[1:]:
        if not line.strip():
            continue

        # Parse airport output format: SSID BSSID  RSSI CHANNEL(CC) CC SECURITY
        parts = line.split()
        if len(parts) >= 6:
            ssid = parts[0] if parts[0] else "<Hidden>"
            bssid = parts[1]

            try:
                rssi = int(parts[2])  # RSSI in dBm
                # Convert RSSI to percentage (rough approximation)
                signal = max(0, min(100, (rssi + 100) * 2))
            except ValueError:
                signal = 0

            # Extract channel from format like "6(2)"
            channel_info = parts[3]
            try:
                channel = int(channel_info.split("(")[0])
            except (ValueError, IndexError):
                channel = 1

            # Security info is in remaining parts
            security = " ".join(parts[5:]) if len(parts) > 5 else "Open"

            frequency = _channel_to_frequency(channel)
            band = _get_band_from_frequency(frequency)

            access_points.append(
                AccessPoint(
                    ssid=ssid,
                    bssid=bssid,
                    signal_percent=signal,
                    channel=channel,
                    auth=security,
                    cipher=security,
                    band=band,
                    frequency_mhz=frequency,
                    seen_at=seen_at,
                )
            )

    return access_points


def scan_wifi_cross_platform(
    interface: Optional[str] = None, timeout: float = 10.0
) -> list[AccessPoint]:
    """Cross-platform WiFi scanner with OS auto-detection.

    Primary target: Windows (using netsh)
    Fallbacks: Linux (nmcli), macOS (airport)

    Args:
        interface: WiFi interface name (Windows only)
        timeout: Scan timeout in seconds

    Returns:
        List of AccessPoint objects

    Raises:
        WiFiScanError: If scanning fails or platform unsupported
    """
    os_name = platform.system().lower()

    if os_name == "windows":
        try:
            return scan_wifi(interface, timeout)
        except (FileNotFoundError, WiFiScanError) as e:
            raise WiFiScanError(f"Windows WiFi scan failed: {e}")

    elif os_name == "linux":
        if interface:
            print("Warning: Interface selection not supported on Linux - using default")
        try:
            return _scan_wifi_linux(timeout)
        except WiFiScanError as e:
            raise WiFiScanError(f"Linux WiFi scan failed: {e}")

    elif os_name == "darwin":  # macOS
        if interface:
            print("Warning: Interface selection not supported on macOS - using default")
        try:
            return _scan_wifi_macos(timeout)
        except WiFiScanError as e:
            raise WiFiScanError(f"macOS WiFi scan failed: {e}")

    else:
        raise WiFiScanError(
            f"Unsupported operating system: {os_name}. "
            "This tool supports Windows (primary), Linux, and macOS. "
            "WiFi scanning is not available on this platform."
        )
