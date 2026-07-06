"""CLI for spectrum grabber - integrates WiFi scanning with tower location data."""

import argparse
import csv
import sys
from typing import Optional

from .overpass_grabber import (
    DEFAULT_USER_AGENT,
    BBox,
    build_overpass_query,
    create_session,
    fetch_overpass_data,
    geocode_place_to_bbox,
    normalize_elements,
    parse_bbox_string,
    validate_place_query,
)
from .wifi_scanner import WiFiScanError, list_interfaces, scan_wifi_cross_platform


def wifi_to_csv_record(ap, kind="wifi") -> dict[str, Optional[str]]:
    """Convert WiFi AccessPoint to CSV record format."""
    return {
        "kind": kind,
        "id": None,
        "osm_type": None,
        "latitude": "",  # WiFi may not have location
        "longitude": "",
        "name": ap.ssid,
        "operator": None,
        "man_made": None,
        "tower_type": None,
        "height": None,
        "source": "wifi_scan",
        "ssid": ap.ssid,
        "bssid": ap.bssid,
        "channel": str(ap.channel),
        "signal": str(ap.signal_percent),
        "auth": ap.auth,
        "cipher": ap.cipher,
        "band": ap.band,
        "frequency_mhz": str(ap.frequency_mhz),
    }


def tower_to_csv_record(tower_record, kind="tower") -> dict[str, Optional[str]]:
    """Convert tower record to unified CSV format."""
    result = dict(tower_record)
    result["kind"] = kind
    # Add WiFi-specific empty columns
    result.update(
        {
            "ssid": None,
            "bssid": None,
            "channel": None,
            "signal": None,
            "auth": None,
            "cipher": None,
            "band": None,
            "frequency_mhz": None,
        }
    )
    return result


def write_unified_csv(file_path: str, records: list[dict[str, Optional[str]]]) -> None:
    """Write unified records to CSV with stable column order."""
    field_names = [
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

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def create_unified_map(
    map_file_path: str,
    tower_records: list[dict],
    wifi_records: list[dict],
    bbox: Optional[BBox] = None,
    place: Optional[str] = None,
) -> None:
    """Create HTML map with towers + WiFi table, clustering, and layer control."""
    try:
        import folium
        from folium.plugins import MarkerCluster
    except ImportError:
        print(
            "folium not installed. Skipping map generation. Install with 'pip install folium'.",
            file=sys.stderr,
        )
        return

    # Determine map center
    if bbox:
        # Use bbox centroid
        center_lat = (bbox.south + bbox.north) / 2
        center_lon = (bbox.west + bbox.east) / 2
    elif tower_records:
        # Calculate from tower coordinates
        latitudes, longitudes = [], []
        for record in tower_records:
            try:
                lat = float(record.get("latitude", ""))
                lon = float(record.get("longitude", ""))
                latitudes.append(lat)
                longitudes.append(lon)
            except (ValueError, TypeError):
                continue
        if latitudes:
            center_lat = sum(latitudes) / len(latitudes)
            center_lon = sum(longitudes) / len(longitudes)
        else:
            center_lat, center_lon = 39.8283, -98.5795  # US geographic center
    else:
        # Default fallback
        center_lat, center_lon = 39.8283, -98.5795  # US geographic center

    # Create base map
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    # Add tower markers with clustering
    if tower_records:
        tower_cluster = MarkerCluster(name="Cell Towers")
        for record in tower_records:
            try:
                lat = float(record.get("latitude", ""))
                lon = float(record.get("longitude", ""))
            except (ValueError, TypeError):
                continue

            popup_lines = [
                "Type: Tower",
                f"Name: {record.get('name') or 'N/A'}",
                f"Operator: {record.get('operator') or 'N/A'}",
                f"Type: {record.get('man_made') or record.get('tower_type') or 'N/A'}",
                f"Height: {record.get('height') or 'N/A'}",
                f"OSM: {record['osm_type']}/{record['id']}",
            ]
            folium.Marker(
                location=[lat, lon],
                popup="\\n".join(popup_lines),
                icon=folium.Icon(color="blue", icon="signal", prefix="fa"),
            ).add_to(tower_cluster)
        tower_cluster.add_to(fmap)

    # Add WiFi markers only for APs with geolocation
    wifi_with_location = [r for r in wifi_records if r.get("latitude") and r.get("longitude")]
    if wifi_with_location:
        wifi_cluster = MarkerCluster(name="WiFi Access Points")
        for record in wifi_with_location:
            try:
                lat = float(record["latitude"])
                lon = float(record["longitude"])
            except (ValueError, TypeError):
                continue

            popup_lines = [
                "Type: WiFi",
                f"SSID: {record.get('ssid') or 'N/A'}",
                f"BSSID: {record.get('bssid') or 'N/A'}",
                f"Channel: {record.get('channel') or 'N/A'}",
                f"Signal: {record.get('signal') or 'N/A'}%",
                f"Auth: {record.get('auth') or 'N/A'}",
            ]
            folium.Marker(
                location=[lat, lon],
                popup="\\n".join(popup_lines),
                icon=folium.Icon(color="green", icon="wifi", prefix="fa"),
            ).add_to(wifi_cluster)
        wifi_cluster.add_to(fmap)

    # Add layer control
    folium.LayerControl().add_to(fmap)

    # Create WiFi table HTML
    wifi_table_html = ""
    if wifi_records:
        wifi_table_html = f"""
        <div id="wifi-panel" style="position: fixed; top: 10px; right: 10px; width: 400px; background: white;
                                   border: 2px solid #ccc; border-radius: 5px; padding: 10px; z-index: 1000;
                                   max-height: 500px; overflow-y: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
            <div style="cursor: pointer; font-weight: bold; border-bottom: 1px solid #ccc; padding-bottom: 5px;"
                 onclick="toggleWifiTable()">📶 WiFi Access Points ({len(wifi_records)}) - Click to toggle</div>
            <div id="wifi-table" style="display: none; margin-top: 10px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                    <thead>
                        <tr style="background: #f0f0f0;">
                            <th style="border: 1px solid #ccc; padding: 4px;">SSID</th>
                            <th style="border: 1px solid #ccc; padding: 4px;">BSSID</th>
                            <th style="border: 1px solid #ccc; padding: 4px;">Ch</th>
                            <th style="border: 1px solid #ccc; padding: 4px;">Signal</th>
                            <th style="border: 1px solid #ccc; padding: 4px;">Auth</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for record in wifi_records:
            ssid = record.get("ssid", "N/A")[:20]  # Truncate long SSIDs
            bssid = (
                record.get("bssid", "N/A")[-8:] if record.get("bssid") else "N/A"
            )  # Last 8 chars
            channel = record.get("channel", "N/A")
            signal = f"{record.get('signal', 'N/A')}%"
            auth = record.get("auth", "N/A")[:10]  # Truncate long auth types

            wifi_table_html += f"""
                        <tr>
                            <td style="border: 1px solid #ccc; padding: 2px; word-break: break-all;">{ssid}</td>
                            <td style="border: 1px solid #ccc; padding: 2px; font-family: monospace;">{bssid}</td>
                            <td style="border: 1px solid #ccc; padding: 2px; text-align: center;">{channel}</td>
                            <td style="border: 1px solid #ccc; padding: 2px; text-align: center;">{signal}</td>
                            <td style="border: 1px solid #ccc; padding: 2px;">{auth}</td>
                        </tr>
            """

        wifi_table_html += """
                    </tbody>
                </table>
            </div>
        </div>
        <script>
        function toggleWifiTable() {
            var table = document.getElementById('wifi-table');
            if (table.style.display === 'none') {
                table.style.display = 'block';
            } else {
                table.style.display = 'none';
            }
        }
        </script>
        """

    # Save map with custom HTML
    map_html = fmap._repr_html_()

    # Insert WiFi table before closing body tag
    if wifi_table_html:
        map_html = map_html.replace("</body>", wifi_table_html + "</body>")

    with open(map_file_path, "w", encoding="utf-8") as f:
        f.write(map_html)

    print(
        f"Saved enhanced map to {map_file_path} with {len(tower_records)} towers and {len(wifi_records)} WiFi APs"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch communication towers and WiFi access points. "
            "Combines OpenStreetMap tower data with local WiFi scanning."
        )
    )

    # Location options (mutually exclusive)
    location_group = parser.add_mutually_exclusive_group(required=False)
    location_group.add_argument(
        "--place",
        type=str,
        help="Place name for tower search (e.g., 'San Francisco, CA').",
    )
    location_group.add_argument(
        "--bbox",
        type=str,
        help="Bounding box as 'south,west,north,east' for tower search.",
    )

    # WiFi scanning options
    parser.add_argument(
        "--wifi-scan",
        action="store_true",
        help="Include WiFi access point scanning.",
    )
    parser.add_argument(
        "--wifi-interface",
        type=str,
        help="Specific WiFi interface to use (Windows only).",
    )

    # Tower data options
    parser.add_argument(
        "--no-osm",
        action="store_true",
        help="Skip OpenStreetMap tower data collection.",
    )

    # Output options
    parser.add_argument(
        "--out-csv",
        type=str,
        help="CSV file path for unified output.",
    )
    parser.add_argument(
        "--out-html",
        type=str,
        help="HTML map file path (requires folium).",
    )

    # HTTP options
    parser.add_argument(
        "--user-agent",
        type=str,
        default=None,
        help="User-Agent for HTTP requests.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="HTTP retry count (default: 3).",
    )
    parser.add_argument(
        "--backoff",
        type=float,
        default=0.5,
        help="HTTP retry backoff factor (default: 0.5).",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.wifi_scan and not args.place and not args.bbox and args.no_osm:
        parser.error(
            "Must specify either --wifi-scan, location (--place/--bbox), or both. Use --no-osm to skip towers."
        )

    if (args.place or args.bbox) and args.no_osm and not args.wifi_scan:
        parser.error("Location specified but --no-osm set and --wifi-scan not enabled.")

    # Collect data
    tower_records = []
    wifi_records = []
    bbox = None  # Initialize bbox

    # Tower data collection
    if not args.no_osm and (args.place or args.bbox):
        user_agent = args.user_agent or DEFAULT_USER_AGENT
        session = create_session(
            user_agent=user_agent, retries=args.retries, backoff_factor=args.backoff
        )

        if args.place:
            validated_place = validate_place_query(args.place)
            print(f"Geocoding place: {validated_place}")
            bbox = geocode_place_to_bbox(validated_place, session=session)
        else:
            bbox = parse_bbox_string(args.bbox)

        print(f"Using bounding box (south, west, north, east): {bbox}")

        query = build_overpass_query(bbox)
        data = fetch_overpass_data(query, session=session)
        tower_records = normalize_elements(data.get("elements", []))

        print(f"Found {len(tower_records)} tower candidates")

    # WiFi scanning
    if args.wifi_scan:
        try:
            if args.wifi_interface:
                # On Windows, list interfaces first to validate
                try:
                    available_interfaces = list_interfaces()
                    if args.wifi_interface not in available_interfaces:
                        print(
                            f"Warning: Interface '{args.wifi_interface}' not in available interfaces: {available_interfaces}"
                        )
                except Exception:
                    pass  # Continue anyway

            print("Scanning WiFi access points...")
            access_points = scan_wifi_cross_platform(interface=args.wifi_interface, timeout=10.0)
            wifi_records = [wifi_to_csv_record(ap) for ap in access_points]
            print(f"Found {len(wifi_records)} WiFi access points")

        except WiFiScanError as e:
            print(f"WiFi scan failed: {e}", file=sys.stderr)
            if not tower_records:
                sys.exit(1)

    # Prepare unified records
    unified_records = []
    unified_records.extend([tower_to_csv_record(record) for record in tower_records])
    unified_records.extend(wifi_records)

    # Output
    if args.out_csv:
        write_unified_csv(args.out_csv, unified_records)
        print(f"Wrote unified CSV: {args.out_csv}")

    if args.out_html:
        bbox_param = bbox if not args.no_osm and (args.place or args.bbox) else None
        place_param = args.place if args.place else None
        create_unified_map(args.out_html, tower_records, wifi_records, bbox_param, place_param)

    # Console output if no CSV specified
    if not args.out_csv:
        print("\n=== TOWERS ===")
        for record in tower_records[:25]:
            print(
                f"{record['latitude']},{record['longitude']} - "
                f"{record.get('name') or record.get('operator') or 'Unknown'} "
                f"({record.get('man_made') or record.get('tower_type') or 'tower'})"
            )
        if len(tower_records) > 25:
            print(f"... and {len(tower_records) - 25} more towers")

        print("\n=== WIFI ACCESS POINTS ===")
        for record in wifi_records[:25]:
            print(
                f"{record.get('ssid')} [{record.get('bssid')}] - "
                f"Ch{record.get('channel')} {record.get('signal')}% "
                f"({record.get('auth')})"
            )
        if len(wifi_records) > 25:
            print(f"... and {len(wifi_records) - 25} more access points")

    print(f"\nTotal: {len(tower_records)} towers, {len(wifi_records)} WiFi APs")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
