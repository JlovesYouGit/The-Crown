"""Unit tests for CSV and HTML writers with schema validation and file creation."""

import csv
from unittest.mock import MagicMock, patch

import pytest

from spectrum_grabber.cli import (
    create_unified_map,
    tower_to_csv_record,
    wifi_to_csv_record,
    write_unified_csv,
)
from spectrum_grabber.overpass_grabber import TowerRecord, try_create_map, write_csv


class TestCSVWriter:
    """Test CSV writing functionality with schema validation."""

    @pytest.fixture
    def sample_tower_records(self) -> list[TowerRecord]:
        """Sample tower records for testing."""
        return [
            {
                "id": "123456",
                "osm_type": "node",
                "latitude": "37.7749",
                "longitude": "-122.4194",
                "name": "Sutro Tower",
                "operator": "Broadcast Corp",
                "man_made": "communications_tower",
                "tower_type": "communication",
                "height": "298m",
                "source": "osm",
            },
            {
                "id": "789012",
                "osm_type": "way",
                "latitude": "37.7849",
                "longitude": "-122.4094",
                "name": None,
                "operator": "Cellular Co",
                "man_made": "mast",
                "tower_type": None,
                "height": None,
                "source": None,
            },
        ]

    def test_write_csv_basic(self, tmp_path, sample_tower_records):
        """Test basic CSV writing with tower records."""
        csv_file = tmp_path / "test_towers.csv"

        write_csv(str(csv_file), sample_tower_records)

        # Verify file exists and has correct content
        assert csv_file.exists()

        # Read and verify content
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2

        # Check first row
        assert rows[0]["id"] == "123456"
        assert rows[0]["osm_type"] == "node"
        assert rows[0]["latitude"] == "37.7749"
        assert rows[0]["longitude"] == "-122.4194"
        assert rows[0]["name"] == "Sutro Tower"
        assert rows[0]["operator"] == "Broadcast Corp"
        assert rows[0]["man_made"] == "communications_tower"
        assert rows[0]["tower_type"] == "communication"
        assert rows[0]["height"] == "298m"
        assert rows[0]["source"] == "osm"

        # Check second row (with None values)
        assert rows[1]["id"] == "789012"
        assert rows[1]["name"] == ""  # None becomes empty string
        assert rows[1]["tower_type"] == ""
        assert rows[1]["height"] == ""
        assert rows[1]["source"] == ""

    def test_write_csv_field_order(self, tmp_path, sample_tower_records):
        """Test that CSV fields are written in correct order."""
        csv_file = tmp_path / "test_order.csv"

        write_csv(str(csv_file), sample_tower_records)

        with open(csv_file, encoding="utf-8") as f:
            first_line = f.readline().strip()

        expected_headers = [
            "id",
            "osm_type",
            "latitude",
            "longitude",
            "name",
            "operator",
            "man_made",
            "tower_type",
            "height",
            "source",
        ]
        assert first_line == ",".join(expected_headers)

    def test_write_csv_empty_records(self, tmp_path):
        """Test writing empty records list."""
        csv_file = tmp_path / "test_empty.csv"

        write_csv(str(csv_file), [])

        assert csv_file.exists()

        with open(csv_file, encoding="utf-8") as f:
            content = f.read()

        # Should contain only header row
        lines = content.strip().split("\n")
        assert len(lines) == 1
        assert "id,osm_type,latitude" in lines[0]

    def test_write_csv_unicode_content(self, tmp_path):
        """Test writing CSV with Unicode characters."""
        unicode_records = [
            {
                "id": "1",
                "osm_type": "node",
                "latitude": "48.8566",
                "longitude": "2.3522",
                "name": "Tour Eiffel (émetteur)",
                "operator": "Société française",
                "man_made": "communications_tower",
                "tower_type": "communication",
                "height": "324m",
                "source": "openstreetmap",
            }
        ]

        csv_file = tmp_path / "test_unicode.csv"
        write_csv(str(csv_file), unicode_records)

        # Read back and verify Unicode is preserved
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["name"] == "Tour Eiffel (émetteur)"
        assert rows[0]["operator"] == "Société française"

    def test_write_csv_file_permissions_error(self, tmp_path, sample_tower_records):
        """Test handling of file permission errors."""
        csv_file = tmp_path / "readonly_dir" / "test.csv"

        # Create directory but make it read-only
        readonly_dir = tmp_path / "readonly_dir"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        # This should raise a permission error
        with pytest.raises(PermissionError):
            write_csv(str(csv_file), sample_tower_records)

    @patch("builtins.open", side_effect=OSError("Disk full"))
    def test_write_csv_io_error(self, mock_open_func, sample_tower_records):
        """Test handling of I/O errors during writing."""
        with pytest.raises(IOError, match="Disk full"):
            write_csv("test.csv", sample_tower_records)


class TestUnifiedCSVWriter:
    """Test unified CSV writer from CLI module."""

    @pytest.fixture
    def sample_wifi_record(self):
        """Sample WiFi record."""
        from datetime import datetime

        from spectrum_grabber.wifi_scanner import AccessPoint

        ap = AccessPoint(
            ssid="TestNetwork",
            bssid="00:11:22:33:44:55",
            signal_percent=85,
            channel=6,
            auth="WPA2-Personal",
            cipher="CCMP",
            band="2.4GHz",
            frequency_mhz=2437,
            seen_at=datetime.now(),
        )
        return wifi_to_csv_record(ap)

    @pytest.fixture
    def sample_tower_unified_record(self):
        """Sample tower record in unified format."""
        tower_record = {
            "id": "123456",
            "osm_type": "node",
            "latitude": "37.7749",
            "longitude": "-122.4194",
            "name": "Test Tower",
            "operator": "Test Corp",
            "man_made": "communications_tower",
            "tower_type": "communication",
            "height": "100m",
            "source": "osm",
        }
        return tower_to_csv_record(tower_record)

    def test_wifi_to_csv_record_conversion(self, sample_wifi_record):
        """Test WiFi access point to CSV record conversion."""
        record = sample_wifi_record

        assert record["kind"] == "wifi"
        assert record["name"] == "TestNetwork"
        assert record["ssid"] == "TestNetwork"
        assert record["bssid"] == "00:11:22:33:44:55"
        assert record["channel"] == "6"
        assert record["signal"] == "85"
        assert record["auth"] == "WPA2-Personal"
        assert record["cipher"] == "CCMP"
        assert record["band"] == "2.4GHz"
        assert record["frequency_mhz"] == "2437"
        assert record["source"] == "wifi_scan"

        # Tower fields should be None/empty
        assert record["id"] is None
        assert record["osm_type"] is None
        assert record["man_made"] is None
        assert record["tower_type"] is None
        assert record["height"] is None

    def test_tower_to_csv_record_conversion(self, sample_tower_unified_record):
        """Test tower record to unified CSV format conversion."""
        record = sample_tower_unified_record

        assert record["kind"] == "tower"
        assert record["id"] == "123456"
        assert record["osm_type"] == "node"
        assert record["name"] == "Test Tower"
        assert record["latitude"] == "37.7749"
        assert record["longitude"] == "-122.4194"
        assert record["man_made"] == "communications_tower"
        assert record["tower_type"] == "communication"

        # WiFi fields should be None
        assert record["ssid"] is None
        assert record["bssid"] is None
        assert record["channel"] is None
        assert record["signal"] is None
        assert record["auth"] is None
        assert record["cipher"] is None
        assert record["band"] is None
        assert record["frequency_mhz"] is None

    def test_write_unified_csv(self, tmp_path, sample_wifi_record, sample_tower_unified_record):
        """Test writing unified CSV with mixed record types."""
        csv_file = tmp_path / "test_unified.csv"

        records = [sample_tower_unified_record, sample_wifi_record]
        write_unified_csv(str(csv_file), records)

        assert csv_file.exists()

        # Read and verify content
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2

        # Tower record
        tower_row = rows[0]
        assert tower_row["kind"] == "tower"
        assert tower_row["name"] == "Test Tower"
        assert tower_row["ssid"] == ""  # Should be empty

        # WiFi record
        wifi_row = rows[1]
        assert wifi_row["kind"] == "wifi"
        assert wifi_row["ssid"] == "TestNetwork"
        assert wifi_row["man_made"] == ""  # Should be empty

    def test_unified_csv_field_order(self, tmp_path, sample_wifi_record):
        """Test that unified CSV has correct field order."""
        csv_file = tmp_path / "test_field_order.csv"

        write_unified_csv(str(csv_file), [sample_wifi_record])

        with open(csv_file, encoding="utf-8") as f:
            first_line = f.readline().strip()

        expected_headers = [
            "kind",
            "id",
            "osm_type",
            "latitude",
            "longitude",
            "name",
            "operator",
            "man_made",
            "tower_type",
            "height",
            "source",
            "ssid",
            "bssid",
            "channel",
            "signal",
            "auth",
            "cipher",
            "band",
            "frequency_mhz",
        ]
        assert first_line == ",".join(expected_headers)


class TestHTMLMapWriter:
    """Test HTML map generation functionality."""

    @pytest.fixture
    def sample_tower_records_for_map(self):
        """Sample tower records with valid coordinates."""
        return [
            {
                "id": "123456",
                "osm_type": "node",
                "latitude": "37.7749",
                "longitude": "-122.4194",
                "name": "Sutro Tower",
                "operator": "Broadcast Corp",
                "man_made": "communications_tower",
                "tower_type": "communication",
                "height": "298m",
                "source": "osm",
            },
            {
                "id": "789012",
                "osm_type": "way",
                "latitude": "37.7849",
                "longitude": "-122.4094",
                "name": "Cell Tower",
                "operator": "Mobile Co",
                "man_made": "mast",
                "tower_type": "cellular",
                "height": "50m",
                "source": "osm",
            },
        ]

    @pytest.fixture
    def sample_wifi_records_for_map(self):
        """Sample WiFi records."""
        return [
            {
                "kind": "wifi",
                "ssid": "TestNetwork",
                "bssid": "00:11:22:33:44:55",
                "channel": "6",
                "signal": "85",
                "auth": "WPA2-Personal",
                "cipher": "CCMP",
                "latitude": "",  # No location
                "longitude": "",
            },
            {
                "kind": "wifi",
                "ssid": "PublicWiFi",
                "bssid": "aa:bb:cc:dd:ee:ff",
                "channel": "11",
                "signal": "60",
                "auth": "Open",
                "cipher": "None",
                "latitude": "37.7750",  # Has location
                "longitude": "-122.4180",
            },
        ]

    @patch("spectrum_grabber.overpass_grabber.folium")
    def test_try_create_map_success(self, mock_folium, tmp_path, sample_tower_records_for_map):
        """Test successful map creation with folium available."""
        map_file = tmp_path / "test_map.html"

        # Mock folium components
        mock_map = MagicMock()
        mock_folium.Map.return_value = mock_map
        mock_marker = MagicMock()
        mock_folium.Marker.return_value = mock_marker
        mock_icon = MagicMock()
        mock_folium.Icon.return_value = mock_icon

        try_create_map(str(map_file), sample_tower_records_for_map)

        # Verify folium.Map was called with calculated center
        mock_folium.Map.assert_called_once()
        map_args = mock_folium.Map.call_args
        location = map_args[1]["location"]

        # Should be average of the two tower coordinates
        expected_lat = (37.7749 + 37.7849) / 2
        expected_lon = (-122.4194 + -122.4094) / 2
        assert abs(location[0] - expected_lat) < 0.001
        assert abs(location[1] - expected_lon) < 0.001
        assert map_args[1]["zoom_start"] == 10

        # Verify markers were created
        assert mock_folium.Marker.call_count == 2

        # Verify map was saved
        mock_map.save.assert_called_once_with(str(map_file))

    @patch(
        "spectrum_grabber.overpass_grabber.folium",
        side_effect=ImportError("No module named 'folium'"),
    )
    def test_try_create_map_no_folium(
        self, mock_folium, tmp_path, sample_tower_records_for_map, capsys
    ):
        """Test map creation when folium is not installed."""
        map_file = tmp_path / "test_map.html"

        try_create_map(str(map_file), sample_tower_records_for_map)

        captured = capsys.readouterr()
        assert "folium is not installed" in captured.err
        assert not map_file.exists()

    def test_try_create_map_empty_records(self, tmp_path, capsys):
        """Test map creation with empty records."""
        map_file = tmp_path / "test_empty_map.html"

        with patch("spectrum_grabber.overpass_grabber.folium"):
            try_create_map(str(map_file), [])

        captured = capsys.readouterr()
        assert "No records to map" in captured.out

    def test_try_create_map_invalid_coordinates(self, tmp_path, capsys):
        """Test map creation with invalid coordinates."""
        invalid_records = [
            {
                "id": "1",
                "osm_type": "node",
                "latitude": "invalid",
                "longitude": "also_invalid",
                "name": "Bad Tower",
                "operator": None,
                "man_made": "mast",
                "tower_type": None,
                "height": None,
                "source": None,
            }
        ]

        map_file = tmp_path / "test_invalid_map.html"

        with patch("spectrum_grabber.overpass_grabber.folium"):
            try_create_map(str(map_file), invalid_records)

        captured = capsys.readouterr()
        assert "No valid coordinate data to map" in captured.out

    @patch("spectrum_grabber.cli.folium")
    def test_create_unified_map_with_clusters(
        self, mock_folium, tmp_path, sample_tower_records_for_map, sample_wifi_records_for_map
    ):
        """Test unified map creation with clustering and layer control."""
        map_file = tmp_path / "test_unified_map.html"

        # Mock folium components including MarkerCluster
        mock_map = MagicMock()
        mock_folium.Map.return_value = mock_map
        mock_cluster = MagicMock()
        mock_folium.plugins.MarkerCluster.return_value = mock_cluster
        mock_layer_control = MagicMock()
        mock_folium.LayerControl.return_value = mock_layer_control

        # Mock _repr_html_ to return basic HTML
        mock_map._repr_html_.return_value = "<html><body></body></html>"

        create_unified_map(str(map_file), sample_tower_records_for_map, sample_wifi_records_for_map)

        # Verify clustering was used
        assert mock_folium.plugins.MarkerCluster.call_count == 2  # One for towers, one for WiFi

        # Verify layer control was added
        mock_folium.LayerControl.assert_called_once()
        mock_layer_control.add_to.assert_called_once_with(mock_map)

        # Verify file was written
        assert map_file.exists()

    @patch("spectrum_grabber.cli.folium", side_effect=ImportError("No module"))
    def test_create_unified_map_no_folium(self, mock_folium, tmp_path, capsys):
        """Test unified map creation without folium."""
        map_file = tmp_path / "test_no_folium.html"

        create_unified_map(str(map_file), [], [])

        captured = capsys.readouterr()
        assert "folium not installed" in captured.err
        assert not map_file.exists()

    @patch("spectrum_grabber.cli.folium")
    def test_create_unified_map_wifi_table_generation(
        self, mock_folium, tmp_path, sample_wifi_records_for_map
    ):
        """Test that WiFi table is properly generated in HTML."""
        map_file = tmp_path / "test_wifi_table.html"

        # Mock folium components
        mock_map = MagicMock()
        mock_folium.Map.return_value = mock_map
        mock_cluster = MagicMock()
        mock_folium.plugins.MarkerCluster.return_value = mock_cluster
        mock_layer_control = MagicMock()
        mock_folium.LayerControl.return_value = mock_layer_control

        # Mock _repr_html_ to return basic HTML structure
        mock_map._repr_html_.return_value = "<html><body><p>Map content</p></body></html>"

        create_unified_map(str(map_file), [], sample_wifi_records_for_map)

        # Read the generated file and check for WiFi table
        with open(map_file, encoding="utf-8") as f:
            html_content = f.read()

        # Should contain WiFi table elements
        assert "WiFi Access Points" in html_content
        assert "TestNetwork" in html_content
        assert "PublicWiFi" in html_content
        assert "toggleWifiTable" in html_content  # JavaScript function
        assert "<table" in html_content
        assert "SSID" in html_content
        assert "BSSID" in html_content

    def test_create_unified_map_bbox_centering(self, tmp_path):
        """Test map centering using bounding box."""
        map_file = tmp_path / "test_bbox_center.html"
        bbox = (37.7, -122.5, 37.8, -122.4)  # (south, west, north, east)

        with patch("spectrum_grabber.cli.folium") as mock_folium:
            mock_map = MagicMock()
            mock_folium.Map.return_value = mock_map
            mock_folium.plugins.MarkerCluster.return_value = MagicMock()
            mock_folium.LayerControl.return_value = MagicMock()
            mock_map._repr_html_.return_value = "<html><body></body></html>"

            create_unified_map(str(map_file), [], [], bbox=bbox)

            # Verify map center is calculated from bbox
            map_args = mock_folium.Map.call_args
            location = map_args[1]["location"]

            expected_lat = (37.7 + 37.8) / 2
            expected_lon = (-122.5 + -122.4) / 2
            assert abs(location[0] - expected_lat) < 0.001
            assert abs(location[1] - expected_lon) < 0.001

    def test_create_unified_map_default_center(self, tmp_path):
        """Test map centering with no data or bbox (uses default center)."""
        map_file = tmp_path / "test_default_center.html"

        with patch("spectrum_grabber.cli.folium") as mock_folium:
            mock_map = MagicMock()
            mock_folium.Map.return_value = mock_map
            mock_folium.plugins.MarkerCluster.return_value = MagicMock()
            mock_folium.LayerControl.return_value = MagicMock()
            mock_map._repr_html_.return_value = "<html><body></body></html>"

            create_unified_map(str(map_file), [], [])

            # Should use US geographic center as default
            map_args = mock_folium.Map.call_args
            location = map_args[1]["location"]

            assert location[0] == 39.8283  # US center lat
            assert location[1] == -98.5795  # US center lon
