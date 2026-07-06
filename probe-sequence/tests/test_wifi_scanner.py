"""Unit tests for WiFi scanner with Windows netsh fixture outputs."""

import subprocess
from datetime import datetime
from unittest.mock import patch

import pytest

from spectrum_grabber.wifi_scanner import (
    NoWirelessInterfacesError,
    WiFiScanError,
    WLANServiceDisabledError,
    _channel_to_frequency,
    _create_access_point,
    _get_band_from_frequency,
    _parse_netsh_output,
    list_interfaces,
    scan_wifi,
)


class TestChannelFrequencyConversion:
    """Test channel to frequency conversion and band detection."""

    def test_channel_to_frequency_2_4ghz(self):
        """Test 2.4GHz channel frequency conversion."""
        assert _channel_to_frequency(1) == 2412
        assert _channel_to_frequency(6) == 2437
        assert _channel_to_frequency(11) == 2462
        assert _channel_to_frequency(14) == 2484

    def test_channel_to_frequency_5ghz(self):
        """Test 5GHz channel frequency conversion."""
        assert _channel_to_frequency(36) == 5180
        assert _channel_to_frequency(40) == 5200
        assert _channel_to_frequency(149) == 5745
        assert _channel_to_frequency(165) == 5825

    def test_channel_to_frequency_6ghz(self):
        """Test 6GHz channel frequency approximation."""
        assert _channel_to_frequency(200) == 5975
        assert _channel_to_frequency(233) == 6635

    def test_channel_to_frequency_unknown(self):
        """Test unknown channel fallback."""
        assert _channel_to_frequency(-1) == 2412
        assert _channel_to_frequency(300) == 5975  # 6GHz range

    def test_get_band_from_frequency(self):
        """Test band detection from frequency."""
        assert _get_band_from_frequency(2412) == "2.4GHz"
        assert _get_band_from_frequency(2484) == "2.4GHz"
        assert _get_band_from_frequency(5180) == "5GHz"
        assert _get_band_from_frequency(5825) == "5GHz"
        assert _get_band_from_frequency(5955) == "6GHz"
        assert _get_band_from_frequency(6635) == "6GHz"
        assert _get_band_from_frequency(1000) == "Unknown"


class TestNetshOutputParsing:
    """Test parsing of Windows netsh wlan show networks output."""

    @pytest.fixture
    def netsh_basic_output(self):
        """Basic netsh output with one SSID and one BSSID."""
        return """
Interface name : Wi-Fi
There are 2 profiles on interface Wi-Fi.

The following networks are available:

SSID 1 : MyNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 00:11:22:33:44:55
         Signal             : 85%
         Radio type         : 802.11n
         Channel            : 6
         Basic rates (Mbps) : 1 2 5.5 11
         Other rates (Mbps) : 6 9 12 18 24 36 48 54

Interface name : Wi-Fi 2
There are 3 profiles on interface Wi-Fi 2.
"""

    @pytest.fixture
    def netsh_multiple_bssids_output(self):
        """Netsh output with multiple BSSIDs for same SSID."""
        return """
SSID 1 : CorporateWiFi
    Network type            : Infrastructure
    Authentication          : WPA2-Enterprise
    Encryption              : CCMP
    BSSID 1                 : aa:bb:cc:dd:ee:01
         Signal             : 75%
         Radio type         : 802.11ac
         Channel            : 36
         Basic rates (Mbps) : 6 12 24
         Other rates (Mbps) : 9 18 36 48 54 108 144 162
    BSSID 2                 : aa:bb:cc:dd:ee:02
         Signal             : 60%
         Radio type         : 802.11ac
         Channel            : 149
         Basic rates (Mbps) : 6 12 24
         Other rates (Mbps) : 9 18 36 48 54 108 144 162
    BSSID 3                 : aa:bb:cc:dd:ee:03
         Signal             : 45%
         Radio type         : 802.11n
         Channel            : 11
         Basic rates (Mbps) : 1 2 5.5 11
"""

    @pytest.fixture
    def netsh_hidden_ssid_output(self):
        """Netsh output with hidden SSID."""
        return """
SSID 1 :
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 11:22:33:44:55:66
         Signal             : 50%
         Radio type         : 802.11n
         Channel            : 1
         Basic rates (Mbps) : 1 2 5.5 11

SSID 2 : OpenNetwork
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    BSSID 1                 : 77:88:99:aa:bb:cc
         Signal             : 30%
         Radio type         : 802.11g
         Channel            : 11
"""

    @pytest.fixture
    def netsh_unusual_auth_cipher_output(self):
        """Netsh output with unusual authentication and cipher combinations."""
        return """
SSID 1 : WEPNetwork
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : WEP
    BSSID 1                 : 12:34:56:78:9a:bc
         Signal             : 25%
         Radio type         : 802.11g
         Channel            : 3

SSID 2 : MixedSecurity
    Network type            : Infrastructure
    Authentication          : WPA-Personal
    Encryption              : TKIP
    BSSID 1                 : de:ad:be:ef:ca:fe
         Signal             : 70%
         Radio type         : 802.11n
         Channel            : 8

SSID 3 : EnterpriseAES
    Network type            : Infrastructure
    Authentication          : WPA2-Enterprise
    Encryption              : AES
    BSSID 1                 : f0:0d:ca:fe:ba:be
         Signal             : 95%
         Radio type         : 802.11ac
         Channel            : 44
"""

    def test_parse_basic_network(self, netsh_basic_output):
        """Test parsing basic network output."""
        access_points = _parse_netsh_output(netsh_basic_output)

        assert len(access_points) == 1
        ap = access_points[0]

        assert ap.ssid == "MyNetwork"
        assert ap.bssid == "00:11:22:33:44:55"
        assert ap.signal_percent == 85
        assert ap.channel == 6
        assert ap.auth == "WPA2-Personal"
        assert ap.cipher == "CCMP"
        assert ap.band == "2.4GHz"
        assert ap.frequency_mhz == 2437
        assert isinstance(ap.seen_at, datetime)

    def test_parse_multiple_bssids(self, netsh_multiple_bssids_output):
        """Test parsing network with multiple BSSIDs."""
        access_points = _parse_netsh_output(netsh_multiple_bssids_output)

        assert len(access_points) == 3

        # All should have same SSID but different BSSIDs
        ssids = {ap.ssid for ap in access_points}
        assert ssids == {"CorporateWiFi"}

        bssids = {ap.bssid for ap in access_points}
        assert bssids == {"aa:bb:cc:dd:ee:01", "aa:bb:cc:dd:ee:02", "aa:bb:cc:dd:ee:03"}

        # Check specific properties
        ap1 = next(ap for ap in access_points if ap.bssid == "aa:bb:cc:dd:ee:01")
        assert ap1.channel == 36
        assert ap1.band == "5GHz"
        assert ap1.signal_percent == 75

        ap2 = next(ap for ap in access_points if ap.bssid == "aa:bb:cc:dd:ee:02")
        assert ap2.channel == 149
        assert ap2.band == "5GHz"

        ap3 = next(ap for ap in access_points if ap.bssid == "aa:bb:cc:dd:ee:03")
        assert ap3.channel == 11
        assert ap3.band == "2.4GHz"

    def test_parse_hidden_ssid(self, netsh_hidden_ssid_output):
        """Test parsing hidden SSID and open network."""
        access_points = _parse_netsh_output(netsh_hidden_ssid_output)

        assert len(access_points) == 2

        # Find hidden and open networks
        hidden_ap = next(ap for ap in access_points if ap.bssid == "11:22:33:44:55:66")
        open_ap = next(ap for ap in access_points if ap.bssid == "77:88:99:aa:bb:cc")

        # Hidden SSID should be empty string (not normalized yet)
        assert hidden_ap.ssid == ""
        assert hidden_ap.auth == "WPA2-Personal"
        assert hidden_ap.cipher == "CCMP"

        # Open network
        assert open_ap.ssid == "OpenNetwork"
        assert open_ap.auth == "Open"
        assert open_ap.cipher == "None"
        assert open_ap.signal_percent == 30

    def test_parse_unusual_auth_cipher(self, netsh_unusual_auth_cipher_output):
        """Test parsing unusual authentication and cipher combinations."""
        access_points = _parse_netsh_output(netsh_unusual_auth_cipher_output)

        assert len(access_points) == 3

        # WEP network
        wep_ap = next(ap for ap in access_points if ap.ssid == "WEPNetwork")
        assert wep_ap.auth == "Open"
        assert wep_ap.cipher == "WEP"
        assert wep_ap.signal_percent == 25

        # WPA/TKIP network
        mixed_ap = next(ap for ap in access_points if ap.ssid == "MixedSecurity")
        assert mixed_ap.auth == "WPA-Personal"
        assert mixed_ap.cipher == "TKIP"
        assert mixed_ap.signal_percent == 70

        # Enterprise AES network
        enterprise_ap = next(ap for ap in access_points if ap.ssid == "EnterpriseAES")
        assert enterprise_ap.auth == "WPA2-Enterprise"
        assert enterprise_ap.cipher == "AES"
        assert enterprise_ap.signal_percent == 95
        assert enterprise_ap.channel == 44
        assert enterprise_ap.band == "5GHz"

    def test_parse_empty_output(self):
        """Test parsing empty or no-network output."""
        access_points = _parse_netsh_output("")
        assert len(access_points) == 0

        access_points = _parse_netsh_output("There are no wireless profiles.")
        assert len(access_points) == 0

    def test_parse_malformed_output(self):
        """Test parsing malformed output gracefully."""
        malformed_output = """
SSID 1 : IncompleteNetwork
    Network type            : Infrastructure
    BSSID 1                 : incomplete:data
         Signal             : invalid%
         Channel            : not_a_number
"""
        access_points = _parse_netsh_output(malformed_output)

        # Should still create an access point with defaults for missing/invalid data
        assert len(access_points) == 1
        ap = access_points[0]
        assert ap.ssid == "IncompleteNetwork"
        assert ap.bssid == "incomplete:data"
        assert ap.signal_percent == 0  # Default for invalid signal
        assert ap.channel == 1  # Default for invalid channel
        assert ap.auth == "Unknown"  # Default for missing auth
        assert ap.cipher == "Unknown"  # Default for missing cipher


class TestListInterfaces:
    """Test listing WiFi interfaces."""

    @pytest.fixture
    def interfaces_output(self):
        """Sample netsh wlan show interfaces output."""
        return """
There is 1 interface on the system:

    Name                   : Wi-Fi
    Description            : Intel(R) Wi-Fi 6 AX200 160MHz
    GUID                   : 12345678-1234-5678-9abc-123456789abc
    Physical address       : 00:11:22:33:44:55
    State                  : connected
    SSID                   : MyHomeNetwork
    BSSID                  : aa:bb:cc:dd:ee:ff
    Network type           : Infrastructure
    Radio type             : 802.11ac
    Authentication         : WPA2-Personal
    Cipher                 : CCMP
    Connection mode        : Auto Connect
    Channel                : 6
    Receive rate (Mbps)    : 866
    Transmit rate (Mbps)   : 866
    Signal                 : 85%
    Profile                : MyHomeNetwork

    Hosted network status  : Not available
"""

    @pytest.fixture
    def multiple_interfaces_output(self):
        """Sample output with multiple interfaces."""
        return """
There are 2 interfaces on the system:

    Name                   : Wi-Fi
    Description            : Intel(R) Wi-Fi 6 AX200 160MHz
    GUID                   : 12345678-1234-5678-9abc-123456789abc
    Physical address       : 00:11:22:33:44:55
    State                  : connected

    Name                   : Wi-Fi 2
    Description            : Realtek RTL8822BE 802.11ac PCIe Adapter
    GUID                   : 87654321-4321-8765-cba9-987654321abc
    Physical address       : ff:ee:dd:cc:bb:aa
    State                  : disconnected
"""

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_list_interfaces_success(self, mock_run, interfaces_output):
        """Test successful interface listing."""
        mock_run.return_value.stdout = interfaces_output

        interfaces = list_interfaces()

        assert len(interfaces) == 1
        assert interfaces[0] == "Wi-Fi"
        mock_run.assert_called_once_with(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_list_multiple_interfaces(self, mock_run, multiple_interfaces_output):
        """Test listing multiple interfaces."""
        mock_run.return_value.stdout = multiple_interfaces_output

        interfaces = list_interfaces()

        assert len(interfaces) == 2
        assert "Wi-Fi" in interfaces
        assert "Wi-Fi 2" in interfaces

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_list_interfaces_wlan_service_disabled(self, mock_run):
        """Test handling of disabled WLAN AutoConfig service."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "netsh", stderr="The WLAN AutoConfig service is not running"
        )

        with pytest.raises(
            WLANServiceDisabledError, match="WLAN AutoConfig service is not running"
        ):
            list_interfaces()

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_list_interfaces_no_interfaces(self, mock_run):
        """Test handling when no wireless interfaces are found."""
        mock_run.return_value.stdout = "There are no wireless interfaces on the system."

        with pytest.raises(NoWirelessInterfacesError, match="No wireless interfaces found"):
            list_interfaces()

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_list_interfaces_timeout(self, mock_run):
        """Test handling of command timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("netsh", 10)

        with pytest.raises(WiFiScanError, match="Timeout listing interfaces"):
            list_interfaces()


class TestScanWiFi:
    """Test WiFi scanning functionality."""

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_scan_wifi_success(self, mock_run, netsh_basic_output):
        """Test successful WiFi scan."""
        mock_run.return_value.stdout = netsh_basic_output

        access_points = scan_wifi()

        assert len(access_points) == 1
        assert access_points[0].ssid == "MyNetwork"
        mock_run.assert_called_once_with(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10.0,
        )

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_scan_wifi_with_interface(self, mock_run):
        """Test WiFi scan with specific interface."""
        mock_run.return_value.stdout = ""

        scan_wifi(interface="Wi-Fi 2", timeout=15.0)

        mock_run.assert_called_once_with(
            ["netsh", "wlan", "show", "networks", "mode=bssid", 'interface="Wi-Fi 2"'],
            capture_output=True,
            text=True,
            check=True,
            timeout=15.0,
        )

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_scan_wifi_interface_not_found(self, mock_run):
        """Test handling of interface not found error."""
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "netsh", stderr="The specified interface does not exist"
        )

        with pytest.raises(WiFiScanError, match="Interface 'NonExistent' not found"):
            scan_wifi(interface="NonExistent")

    @patch("spectrum_grabber.wifi_scanner.subprocess.run")
    def test_scan_wifi_wlan_service_disabled(self, mock_run):
        """Test handling of disabled WLAN service during scan."""
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "netsh", stderr="AutoConfig service not running"
        )

        with pytest.raises(WLANServiceDisabledError):
            scan_wifi()


class TestAccessPointCreation:
    """Test AccessPoint object creation from parsed data."""

    def test_create_access_point_complete(self):
        """Test creating access point with complete information."""
        bssid_info = {
            "bssid": "00:11:22:33:44:55",
            "signal": 85,
            "channel": 6,
            "auth": "WPA2-Personal",
            "cipher": "CCMP",
        }

        ap = _create_access_point("TestNetwork", bssid_info, datetime.now())

        assert ap.ssid == "TestNetwork"
        assert ap.bssid == "00:11:22:33:44:55"
        assert ap.signal_percent == 85
        assert ap.channel == 6
        assert ap.auth == "WPA2-Personal"
        assert ap.cipher == "CCMP"
        assert ap.band == "2.4GHz"
        assert ap.frequency_mhz == 2437

    def test_create_access_point_minimal(self):
        """Test creating access point with minimal information."""
        bssid_info = {"bssid": "aa:bb:cc:dd:ee:ff"}

        ap = _create_access_point("MinimalNetwork", bssid_info, datetime.now())

        assert ap.ssid == "MinimalNetwork"
        assert ap.bssid == "aa:bb:cc:dd:ee:ff"
        assert ap.signal_percent == 0  # Default
        assert ap.channel == 1  # Default
        assert ap.auth == "Unknown"  # Default
        assert ap.cipher == "Unknown"  # Default
        assert ap.band == "2.4GHz"  # Default for channel 1
        assert ap.frequency_mhz == 2412  # Default for channel 1

    def test_create_access_point_5ghz(self):
        """Test creating 5GHz access point."""
        bssid_info = {
            "bssid": "ff:ee:dd:cc:bb:aa",
            "signal": 60,
            "channel": 149,
            "auth": "WPA3-Personal",
            "cipher": "CCMP",
        }

        ap = _create_access_point("5GHzNetwork", bssid_info, datetime.now())

        assert ap.channel == 149
        assert ap.band == "5GHz"
        assert ap.frequency_mhz == 5745
