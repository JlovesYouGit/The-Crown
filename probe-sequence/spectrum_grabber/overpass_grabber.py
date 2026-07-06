import argparse
import csv
import sys
from typing import Any, Optional, TypedDict, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
DEFAULT_USER_AGENT = "spectrum-grabber/1.0 (+https://example.com/contact)"


# Type definitions for OSM/Overpass data structures
class OSMTags(TypedDict, total=False):
    """Common OSM tags for tower/mast elements."""

    name: str
    operator: str
    man_made: str  # 'communications_tower', 'mast', etc.
    height: str
    source: str


class TowerTags(OSMTags, total=False):
    """Extended tags specific to communication towers."""

    tower_type: str  # from 'tower:type'


class OSMCenter(TypedDict):
    """Center coordinates for way elements."""

    lat: float
    lon: float


class OSMNode(TypedDict):
    """OSM node element structure."""

    type: str  # 'node'
    id: int
    lat: float
    lon: float
    tags: TowerTags


class OSMWay(TypedDict):
    """OSM way element structure."""

    type: str  # 'way'
    id: int
    center: OSMCenter
    tags: TowerTags


OSMElement = Union[OSMNode, OSMWay]


class OverpassResponse(TypedDict):
    """Overpass API response structure."""

    version: float
    generator: str
    elements: list[OSMElement]


class NominatimResult(TypedDict):
    """Nominatim geocoding result structure."""

    place_id: int
    licence: str
    osm_type: str
    osm_id: int
    boundingbox: list[str]  # [south, north, west, east] as strings
    lat: str
    lon: str
    display_name: str
    class_: str
    type: str
    importance: float


class TowerRecord(TypedDict):
    """Normalized tower record for CSV output."""

    id: Optional[str]
    osm_type: Optional[str]
    latitude: str
    longitude: str
    name: Optional[str]
    operator: Optional[str]
    man_made: Optional[str]
    tower_type: Optional[str]
    height: Optional[str]
    source: Optional[str]


# Type aliases
BBox = tuple[float, float, float, float]  # (south, west, north, east)
PlaceInput = Union[str, BBox]


class OverpassError(Exception):
    """Raised when the Overpass API returns an error response."""


def create_session(
    user_agent: str, retries: int = 3, backoff_factor: float = 0.5
) -> requests.Session:
    """Create a configured requests session with retry policy and default headers."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": user_agent})
    return session


def safe_float(value: Optional[str]) -> Optional[float]:
    """Convert a possibly-null string to float, returning None if not parseable."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def geocode_place_to_bbox(place_query: str, session: requests.Session) -> BBox:
    """Geocode a place name to a bounding box using Nominatim.

    Returns a tuple: (south, west, north, east)
    """
    params: dict[str, Union[str, int]] = {"q": place_query, "format": "json", "limit": 1}
    response = session.get(
        NOMINATIM_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    results = response.json()
    if not results:
        raise ValueError(f"Could not geocode place: {place_query}")

    bbox_values = results[0].get("boundingbox")
    if not bbox_values or len(bbox_values) != 4:
        raise ValueError(f"Nominatim did not return a valid bounding box for: {place_query}")

    south = float(bbox_values[0])
    north = float(bbox_values[1])
    west = float(bbox_values[2])
    east = float(bbox_values[3])
    return south, west, north, east


def build_overpass_query(bbox: BBox) -> str:
    """Build an Overpass QL query to fetch likely radio/communication towers.

    The query targets common tags used for towers:
    - man_made=communications_tower
    - man_made=mast
    - tower:type=communication
    """
    south, west, north, east = bbox
    query = f"""
    [out:json][timeout:30];
    (
      node["man_made"="communications_tower"]({south},{west},{north},{east});
      way["man_made"="communications_tower"]({south},{west},{north},{east});
      node["man_made"="mast"]({south},{west},{north},{east});
      way["man_made"="mast"]({south},{west},{north},{east});
      node["tower:type"="communication"]({south},{west},{north},{east});
      way["tower:type"="communication"]({south},{west},{north},{east});
    );
    out center tags;
    """.strip()
    return query


def fetch_overpass_data(query: str, session: requests.Session) -> dict[str, Any]:
    """Execute Overpass query and return JSON payload."""
    response = session.post(
        OVERPASS_URL,
        data={"data": query},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=90,
    )
    if response.status_code != 200:
        raise OverpassError(f"Overpass error {response.status_code}: {response.text[:200]}")
    data = response.json()
    if "elements" not in data:
        raise OverpassError("Overpass returned unexpected payload: missing 'elements'")
    return data  # type: ignore[no-any-return]


def normalize_elements(elements: list[dict[str, Any]]) -> list[TowerRecord]:
    """Normalize Overpass elements into a flat list of records with lat/lon and key tags."""
    records: list[dict[str, Optional[str]]] = []
    for element in elements:
        element_type = element.get("type")
        tags = element.get("tags", {}) or {}

        if element_type == "node":
            latitude = element.get("lat")
            longitude = element.get("lon")
        else:
            center = element.get("center") or {}
            latitude = center.get("lat")
            longitude = center.get("lon")

        if latitude is None or longitude is None:
            continue

        record: dict[str, Optional[str]] = {
            "id": str(element.get("id")),
            "osm_type": element_type,
            "latitude": f"{latitude}",
            "longitude": f"{longitude}",
            "name": tags.get("name"),
            "operator": tags.get("operator"),
            "man_made": tags.get("man_made"),
            "tower_type": tags.get("tower:type"),
            "height": tags.get("height"),
            "source": tags.get("source"),
        }
        records.append(record)
    return records


def write_csv(file_path: str, records: list[TowerRecord]) -> None:
    """Write records to CSV with a stable column order."""
    field_names = [
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
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def try_create_map(map_file_path: str, records: list[TowerRecord]) -> None:
    """Create a simple HTML map using folium if installed; otherwise print guidance."""
    try:
        import folium
    except Exception:
        print(
            "folium is not installed. Skipping map generation. Install with 'pip install folium' and re-run.",
            file=sys.stderr,
        )
        return

    if not records:
        print("No records to map.")
        return

    latitudes: list[float] = []
    longitudes: list[float] = []
    for r in records:
        lat = safe_float(r.get("latitude"))
        lon = safe_float(r.get("longitude"))
        if lat is not None and lon is not None:
            latitudes.append(lat)
            longitudes.append(lon)

    if not latitudes or not longitudes:
        print("No valid coordinate data to map.")
        return

    average_latitude = sum(latitudes) / len(latitudes)
    average_longitude = sum(longitudes) / len(longitudes)

    fmap = folium.Map(location=[average_latitude, average_longitude], zoom_start=10)
    for record in records:
        lat = safe_float(record.get("latitude"))
        lon = safe_float(record.get("longitude"))
        if lat is None or lon is None:
            continue
        popup_lines = [
            f"Name: {record.get('name') or 'N/A'}",
            f"Operator: {record.get('operator') or 'N/A'}",
            f"Type: {record.get('man_made') or record.get('tower_type') or 'N/A'}",
            f"Height: {record.get('height') or 'N/A'}",
            f"OSM: {record['osm_type']}/{record['id']}",
        ]
        folium.Marker(
            location=[lat, lon],
            popup="\n".join(popup_lines),
            icon=folium.Icon(color="blue", icon="signal", prefix="fa"),
        ).add_to(fmap)

    fmap.save(map_file_path)
    print(f"Saved map to {map_file_path}")


def validate_bbox(bbox: BBox) -> BBox:
    """Validate bounding box coordinates are within valid ranges."""
    south, west, north, east = bbox

    # Validate latitude bounds
    if not (-90 <= south <= 90) or not (-90 <= north <= 90):
        raise ValueError("Latitude values must be between -90 and 90 degrees")

    # Validate longitude bounds
    if not (-180 <= west <= 180) or not (-180 <= east <= 180):
        raise ValueError("Longitude values must be between -180 and 180 degrees")

    # Validate bbox ordering
    if south >= north:
        raise ValueError("South boundary must be less than north boundary")

    if west >= east:
        raise ValueError("West boundary must be less than east boundary")

    # Warn for very large bounding boxes
    area = (north - south) * (east - west)
    if area > 100:  # ~10 degrees x 10 degrees
        print(
            f"Warning: Large bounding box area ({area:.2f} sq degrees) may result in slow queries",
            file=sys.stderr,
        )

    return bbox


def parse_bbox_string(bbox_string: str) -> BBox:
    """Parse a comma-separated bbox string into a validated float tuple."""
    if not bbox_string or not bbox_string.strip():
        raise ValueError("Bounding box string cannot be empty")

    parts = [p.strip() for p in bbox_string.split(",")]
    if len(parts) != 4:
        raise ValueError("--bbox must be four comma-separated numbers: south,west,north,east")

    try:
        south, west, north, east = map(float, parts)
    except ValueError as e:
        raise ValueError(f"Invalid number in bounding box: {e}")

    bbox = (south, west, north, east)
    return validate_bbox(bbox)


def validate_place_query(place_query: str) -> str:
    """Validate and sanitize place query string."""
    if not place_query or not place_query.strip():
        raise ValueError("Place query cannot be empty")

    cleaned = place_query.strip()
    if len(cleaned) > 200:  # Reasonable limit for place names
        raise ValueError("Place query too long (max 200 characters)")

    # Basic validation for suspicious characters
    if any(char in cleaned for char in ["<", ">", "&", '"', "'"]) and not any(
        char in cleaned for char in [",", " "]
    ):
        print(
            f"Warning: Place query contains special characters: {cleaned[:50]}...", file=sys.stderr
        )

    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch approximate locations of communication towers from OpenStreetMap via Overpass API, "
            "either by place name (geocoded to a bounding box) or by an explicit bounding box."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--place",
        type=str,
        help="Place name to search (e.g., 'San Francisco, CA' or 'Berlin, Germany').",
    )
    group.add_argument(
        "--bbox",
        type=str,
        help="Bounding box as 'south,west,north,east' (e.g., '37.60,-122.55,37.90,-122.30').",
    )
    parser.add_argument(
        "--out-file",
        type=str,
        default=None,
        help="Optional CSV file path to write results.",
    )
    parser.add_argument(
        "--map-file",
        type=str,
        default=None,
        help="Optional HTML map file to write (requires folium).",
    )
    parser.add_argument(
        "--user-agent",
        type=str,
        default=None,
        help=(
            "User-Agent for HTTP requests (include contact per Nominatim policy), "
            "defaults to a generic tool UA."
        ),
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="HTTP retry count for Overpass/Nominatim requests (default: 3).",
    )
    parser.add_argument(
        "--backoff",
        type=float,
        default=0.5,
        help="HTTP retry backoff factor in seconds (default: 0.5).",
    )

    args = parser.parse_args()

    user_agent = args.user_agent or DEFAULT_USER_AGENT
    session = create_session(
        user_agent=user_agent, retries=args.retries, backoff_factor=args.backoff
    )

    if args.place:
        validated_place = validate_place_query(args.place)
        print(f"Geocoding place: {validated_place}")
        bbox = geocode_place_to_bbox(validated_place, session=session)
        bbox = validate_bbox(bbox)  # Validate geocoded bbox too
    else:
        bbox = parse_bbox_string(args.bbox)  # Already validates internally

    print(f"Using bounding box (south, west, north, east): {bbox}")

    query = build_overpass_query(bbox)
    data = fetch_overpass_data(query, session=session)
    records = normalize_elements(data.get("elements", []))

    print(f"Found {len(records)} tower candidates")

    if args.out_file:
        write_csv(args.out_file, records)
        print(f"Wrote CSV: {args.out_file}")

    if args.map_file:
        try_create_map(args.map_file, records)

    if not args.out_file:
        for record in records[:50]:
            print(
                f"{record['latitude']},{record['longitude']} - "
                f"{record.get('name') or record.get('operator') or 'Unknown'} "
                f"({record.get('man_made') or record.get('tower_type') or 'tower'})"
            )
        if len(records) > 50:
            print(f"... and {len(records) - 50} more")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
