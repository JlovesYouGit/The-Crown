"""Integration tests with mocked external services using responses library."""

from datetime import datetime
from unittest.mock import patch

import pytest
import responses

from spectrum_grabber.overpass_grabber import (
    build_overpass_query,
    create_session,
    fetch_overpass_data,
    geocode_place_to_bbox,
    normalize_elements,
)
from spectrum_grabber.wifi_scanner import AccessPoint


class TestOverpassIntegration:
    """Integration tests for Overpass API with mocked responses."""

    @responses.activate
    def test_full_overpass_workflow_success(self):
        """Test complete workflow from geocoding to data fetching."""
        # Mock Nominatim geocoding response
        responses.add(
            responses.GET,
            "https://nominatim.openstreetmap.org/search",
            json=[
                {
                    "boundingbox": ["37.7", "37.8", "-122.5", "-122.4"],
                    "lat": "37.75",
                    "lon": "-122.45",
                    "display_name": "San Francisco, CA, USA",
                }
            ],
            status=200,
        )

        # Mock Overpass API response
        responses.add(
            responses.POST,
            "https://overpass-api.de/api/interpreter",
            json={
                "version": 0.6,
                "generator": "Overpass API",
                "elements": [
                    {
                        "type": "node",
                        "id": 123456,
                        "lat": 37.7749,
                        "lon": -122.4194,
                        "tags": {
                            "name": "Sutro Tower",
                            "man_made": "communications_tower",
                            "height": "298",
                            "operator": "Sutro Tower Inc.",
                        },
                    },
                    {
                        "type": "way",
                        "id": 789012,
                        "center": {"lat": 37.7849, "lon": -122.4094},
                        "tags": {
                            "tower:type": "communication",
                            "man_made": "mast",
                            "operator": "Cellular Corp",
                        },
                    },
                ],
            },
            status=200,
        )

        # Execute workflow
        session = create_session("test-agent/1.0")

        # Step 1: Geocode place
        bbox = geocode_place_to_bbox("San Francisco, CA", session)
        assert bbox == (37.7, -122.5, 37.8, -122.4)

        # Step 2: Build and execute Overpass query
        query = build_overpass_query(bbox)
        data = fetch_overpass_data(query, session)

        # Step 3: Normalize results
        records = normalize_elements(data["elements"])

        # Verify results
        assert len(records) == 2

        # Check node record
        node_record = next(r for r in records if r["id"] == "123456")
        assert node_record["osm_type"] == "node"
        assert node_record["latitude"] == "37.7749"
        assert node_record["longitude"] == "-122.4194"
        assert node_record["name"] == "Sutro Tower"
        assert node_record["man_made"] == "communications_tower"
        assert node_record["height"] == "298"
        assert node_record["operator"] == "Sutro Tower Inc."

        # Check way record
        way_record = next(r for r in records if r["id"] == "789012")
        assert way_record["osm_type"] == "way"
        assert way_record["latitude"] == "37.7849"
        assert way_record["longitude"] == "-122.4094"
        assert way_record["tower_type"] == "communication"
        assert way_record["man_made"] == "mast"
        assert way_record["operator"] == "Cellular Corp"

    @responses.activate
    def test_overpass_rate_limiting_retry(self):
        """Test handling of rate limiting with retry logic."""
        # First request returns 429 (rate limited)
        responses.add(
            responses.POST,
            "https://overpass-api.de/api/interpreter",
            body="Rate limit exceeded",
            status=429,
        )

        # Second request succeeds
        responses.add(
            responses.POST,
            "https://overpass-api.de/api/interpreter",
            json={"version": 0.6, "generator": "Overpass API", "elements": []},
            status=200,
        )

        session = create_session("test-agent/1.0", retries=2, backoff_factor=0.1)
        query = build_overpass_query((37.7, -122.5, 37.8, -122.4))

        # This should succeed after retry
        data = fetch_overpass_data(query, session)
        assert "elements" in data
        assert len(responses.calls) == 2  # Verify retry occurred

    @responses.activate
    def test_nominatim_rate_limiting_retry(self):
        """Test Nominatim rate limiting and retry."""
        # First request returns 429
        responses.add(
            responses.GET,
            "https://nominatim.openstreetmap.org/search",
            body="Rate limit exceeded",
            status=429,
        )

        # Second request succeeds
        responses.add(
            responses.GET,
            "https://nominatim.openstreetmap.org/search",
            json=[
                {
                    "boundingbox": ["37.7", "37.8", "-122.5", "-122.4"],
                    "lat": "37.75",
                    "lon": "-122.45",
                }
            ],
            status=200,
        )

        session = create_session("test-agent/1.0", retries=2, backoff_factor=0.1)

        # Should succeed after retry
        bbox = geocode_place_to_bbox("San Francisco", session)
        assert bbox == (37.7, -122.5, 37.8, -122.4)
        assert len(responses.calls) == 2

    @responses.activate
    def test_overpass_server_error_handling(self):
        """Test handling of server errors from Overpass API."""
        responses.add(
            responses.POST,
            "https://overpass-api.de/api/interpreter",
            body="Internal server error",
            status=503,
        )

        session = create_session("test-agent/1.0")
        query = build_overpass_query((37.7, -122.5, 37.8, -122.4))

        from spectrum_grabber.overpass_grabber import OverpassError

        with pytest.raises(OverpassError, match="Overpass error 503"):
            fetch_overpass_data(query, session)

    @responses.activate
    def test_nominatim_no_results(self):
        """Test handling when Nominatim returns no results."""
        responses.add(
            responses.GET, "https://nominatim.openstreetmap.org/search", json=[], status=200
        )

        session = create_session("test-agent/1.0")

        with pytest.raises(ValueError, match="Could not geocode place"):
            geocode_place_to_bbox("NonExistentPlace", session)

    @responses.activate
    def test_overpass_malformed_response(self):
        """Test handling of malformed Overpass response."""
        responses.add(
            responses.POST,
            "https://overpass-api.de/api/interpreter",
            json={
                "version": 0.6,
                "generator": "Overpass API",
                # Missing "elements" key
            },
            status=200,
        )

        session = create_session("test-agent/1.0")
        query = build_overpass_query((37.7, -122.5, 37.8, -122.4))

        from spectrum_grabber.overpass_grabber import OverpassError

        with pytest.raises(OverpassError, match="missing 'elements'"):
            fetch_overpass_data(query, session)


class TestCLIIntegration:
    """Integration tests for CLI with mocked external services."""

    @responses.activate
    @patch("spectrum_grabber.cli.scan_wifi_cross_platform")
    def test_cli_full_workflow_with_wifi_scan(self, mock_wifi_scan, tmp_path, capsys):
        """Test complete CLI workflow with WiFi scanning."""
        # Mock WiFi scan results
        mock_access_points = [
            AccessPoint(
                ssid="TestNetwork",
                bssid="00:11:22:33:44:55",
                signal_percent=85,
                channel=6,
                auth="WPA2-Personal",
                cipher="CCMP",
                band="2.4GHz",
                frequency_mhz=2437,
                seen_at=datetime.now(),
            ),
            AccessPoint(
                ssid="OpenWiFi",
                bssid="aa:bb:cc:dd:ee:ff",
                signal_percent=60,
                channel=11,
                auth="Open",
                cipher="None",
                band="2.4GHz",
                frequency_mhz=2462,
                seen_at=datetime.now(),
            ),
        ]
        mock_wifi_scan.return_value = mock_access_points

        # Mock Nominatim response
        responses.add(
            responses.GET,
            "https://nominatim.openstreetmap.org/search",
            json=[
                {
                    "boundingbox": ["37.7", "37.8", "-122.5", "-122.4"],
                    "lat": "37.75",
                    "lon": "-122.45",
                }
            ],
            status=200,
        )

        # Mock Overpass response
        responses.add(
            responses.POST,
            "https://overpass-api.de/api/interpreter",
            json={
                "version": 0.6,
                "generator": "Overpass API",
                "elements": [
                    {
                        "type": "node",
                        "id": 123456,
                        "lat": 37.7749,
                        "lon": -122.4194,
                        "tags": {"name": "Test Tower", "man_made": "communications_tower"},
                    }
                ],
            },
            status=200,
        )

        # Create output files
        csv_file = tmp_path / "output.csv"
        html_file = tmp_path / "map.html"

        # Mock sys.argv for CLI
        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "spectrum-grabber",
                "--place",
                "San Francisco, CA",
                "--wifi-scan",
                "--out-csv",
                str(csv_file),
                "--out-html",
                str(html_file),
            ]

            # Execute CLI
            from spectrum_grabber.cli import main

            main()

        finally:
            sys.argv = original_argv

        # Verify outputs
        assert csv_file.exists()
        assert html_file.exists()

        # Check console output
        captured = capsys.readouterr()
        assert "Found 1 tower candidates" in captured.out
        assert "Found 2 WiFi access points" in captured.out
        assert "Total: 1 towers, 2 WiFi APs" in captured.out

        # Verify CSV content
        import csv as csv_module

        with open(csv_file, encoding="utf-8") as f:
            reader = csv_module.DictReader(f)
            rows = list(reader)

        # Should have 1 tower + 2 WiFi records
        assert len(rows) == 3

        tower_row = next(r for r in rows if r["kind"] == "tower")
        assert tower_row["name"] == "Test Tower"

        wifi_rows = [r for r in rows if r["kind"] == "wifi"]
        assert len(wifi_rows) == 2
        assert any(r["ssid"] == "TestNetwork" for r in wifi_rows)
        assert any(r["ssid"] == "OpenWiFi" for r in wifi_rows)

    @patch("spectrum_grabber.cli.scan_wifi_cross_platform")
    def test_cli_wifi_only_mode(self, mock_wifi_scan, tmp_path, capsys):
        """Test CLI with WiFi scanning only (no OSM data)."""
        mock_access_points = [
            AccessPoint(
                ssid="WiFiOnly",
                bssid="11:22:33:44:55:66",
                signal_percent=70,
                channel=1,
                auth="WPA3-Personal",
                cipher="CCMP",
                band="2.4GHz",
                frequency_mhz=2412,
                seen_at=datetime.now(),
            )
        ]
        mock_wifi_scan.return_value = mock_access_points

        csv_file = tmp_path / "wifi_only.csv"

        import sys

        original_argv = sys.argv
        try:
            sys.argv = ["spectrum-grabber", "--wifi-scan", "--out-csv", str(csv_file)]

            from spectrum_grabber.cli import main

            main()

        finally:
            sys.argv = original_argv

        # Verify output
        assert csv_file.exists()

        captured = capsys.readouterr()
        assert "Found 1 WiFi access points" in captured.out
        assert "Total: 0 towers, 1 WiFi APs" in captured.out

        # Check CSV
        import csv as csv_module

        with open(csv_file, encoding="utf-8") as f:
            reader = csv_module.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["kind"] == "wifi"
        assert rows[0]["ssid"] == "WiFiOnly"

    @patch("spectrum_grabber.cli.scan_wifi_cross_platform")
    def test_cli_wifi_scan_error_with_tower_fallback(self, mock_wifi_scan, tmp_path, capsys):
        """Test CLI when WiFi scan fails but tower data succeeds."""
        # Mock WiFi scan failure
        from spectrum_grabber.wifi_scanner import WiFiScanError

        mock_wifi_scan.side_effect = WiFiScanError("WLAN service not running")

        # Mock successful tower data
        responses.add(
            responses.GET,
            "https://nominatim.openstreetmap.org/search",
            json=[
                {
                    "boundingbox": ["37.7", "37.8", "-122.5", "-122.4"],
                }
            ],
            status=200,
        )

        responses.add(
            responses.POST,
            "https://overpass-api.de/api/interpreter",
            json={
                "version": 0.6,
                "generator": "Overpass API",
                "elements": [
                    {
                        "type": "node",
                        "id": 99999,
                        "lat": 37.77,
                        "lon": -122.42,
                        "tags": {"name": "Fallback Tower", "man_made": "mast"},
                    }
                ],
            },
            status=200,
        )

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "spectrum-grabber",
                "--place",
                "San Francisco",
                "--wifi-scan",  # This will fail
            ]

            # Should not exit with error since tower data succeeds
            from spectrum_grabber.cli import main

            main()

        finally:
            sys.argv = original_argv

        captured = capsys.readouterr()
        assert "WiFi scan failed" in captured.err
        assert "Found 1 tower candidates" in captured.out
        assert "Total: 1 towers, 0 WiFi APs" in captured.out

    @patch("spectrum_grabber.cli.scan_wifi_cross_platform")
    def test_cli_wifi_scan_error_no_towers_exits(self, mock_wifi_scan, capsys):
        """Test CLI exits when WiFi scan fails and no tower data requested."""
        from spectrum_grabber.wifi_scanner import WiFiScanError

        mock_wifi_scan.side_effect = WiFiScanError("No wireless adapters")

        import sys

        original_argv = sys.argv
        try:
            sys.argv = ["spectrum-grabber", "--wifi-scan"]  # Only WiFi, no towers

            from spectrum_grabber.cli import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

        finally:
            sys.argv = original_argv

        captured = capsys.readouterr()
        assert "WiFi scan failed" in captured.err


class TestEndToEndWithFixtures:
    """End-to-end tests using fixture data."""

    def create_mock_wifi_scanner(self, fixture_output: str):
        """Create a mock WiFi scanner that returns fixture output."""

        def mock_scan_wifi(interface=None, timeout=10.0):
            from spectrum_grabber.wifi_scanner import _parse_netsh_output

            return _parse_netsh_output(fixture_output)

        return mock_scan_wifi

    @responses.activate
    def test_e2e_with_complex_wifi_fixture(self, tmp_path):
        """End-to-end test with complex WiFi fixture data."""
        # Complex netsh fixture with various network types
        netsh_fixture = """
SSID 1 : CorporateNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Enterprise
    Encryption              : AES
    BSSID 1                 : 00:1a:2b:3c:4d:01
         Signal             : 95%
         Radio type         : 802.11ac
         Channel            : 36
    BSSID 2                 : 00:1a:2b:3c:4d:02
         Signal             : 80%
         Radio type         : 802.11ac
         Channel            : 149

SSID 2 : PublicWiFi
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    BSSID 1                 : aa:bb:cc:dd:ee:ff
         Signal             : 65%
         Radio type         : 802.11n
         Channel            : 6

SSID 3 :
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 11:22:33:44:55:66
         Signal             : 45%
         Radio type         : 802.11g
         Channel            : 11
"""

        # Mock external services
        responses.add(
            responses.GET,
            "https://nominatim.openstreetmap.org/search",
            json=[
                {
                    "boundingbox": ["40.7", "40.8", "-74.1", "-74.0"],
                }
            ],
            status=200,
        )

        responses.add(
            responses.POST,
            "https://overpass-api.de/api/interpreter",
            json={
                "version": 0.6,
                "generator": "Overpass API",
                "elements": [
                    {
                        "type": "node",
                        "id": 1001,
                        "lat": 40.7589,
                        "lon": -74.0495,
                        "tags": {
                            "name": "Empire State Building Antenna",
                            "man_made": "communications_tower",
                            "height": "443",
                            "operator": "Various broadcasters",
                        },
                    },
                    {
                        "type": "way",
                        "id": 2002,
                        "center": {"lat": 40.7505, "lon": -74.0409},
                        "tags": {
                            "tower:type": "communication",
                            "man_made": "mast",
                            "operator": "Verizon",
                        },
                    },
                ],
            },
            status=200,
        )

        # Mock WiFi scanning with fixture
        with patch(
            "spectrum_grabber.cli.scan_wifi_cross_platform",
            self.create_mock_wifi_scanner(netsh_fixture),
        ):
            csv_file = tmp_path / "e2e_test.csv"

            import sys

            original_argv = sys.argv
            try:
                sys.argv = [
                    "spectrum-grabber",
                    "--place",
                    "New York City",
                    "--wifi-scan",
                    "--out-csv",
                    str(csv_file),
                ]

                from spectrum_grabber.cli import main

                main()

            finally:
                sys.argv = original_argv

        # Verify comprehensive output
        assert csv_file.exists()

        import csv as csv_module

        with open(csv_file, encoding="utf-8") as f:
            reader = csv_module.DictReader(f)
            rows = list(reader)

        # Should have 2 towers + 4 WiFi entries (2 BSSIDs for CorporateNetwork + 1 each for others)
        assert len(rows) == 6

        # Verify tower data
        tower_rows = [r for r in rows if r["kind"] == "tower"]
        assert len(tower_rows) == 2

        empire_tower = next(r for r in tower_rows if "Empire State" in r["name"])
        assert empire_tower["height"] == "443"
        assert empire_tower["man_made"] == "communications_tower"

        # Verify WiFi data
        wifi_rows = [r for r in rows if r["kind"] == "wifi"]
        assert len(wifi_rows) == 4

        # Check corporate network (2 BSSIDs)
        corp_rows = [r for r in wifi_rows if r["ssid"] == "CorporateNetwork"]
        assert len(corp_rows) == 2
        assert all(r["auth"] == "WPA2-Enterprise" for r in corp_rows)
        assert all(r["cipher"] == "AES" for r in corp_rows)

        # Check different channels for corporate BSSIDs
        channels = {r["channel"] for r in corp_rows}
        assert channels == {"36", "149"}

        # Check public WiFi
        public_rows = [r for r in wifi_rows if r["ssid"] == "PublicWiFi"]
        assert len(public_rows) == 1
        assert public_rows[0]["auth"] == "Open"
        assert public_rows[0]["cipher"] == "None"

        # Check hidden network
        hidden_rows = [r for r in wifi_rows if r["ssid"] == ""]
        assert len(hidden_rows) == 1
        assert hidden_rows[0]["auth"] == "WPA2-Personal"
