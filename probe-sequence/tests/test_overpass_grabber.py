import pytest

from spectrum_grabber.overpass_grabber import (
    build_overpass_query,
    normalize_elements,
    parse_bbox_string,
    validate_bbox,
    validate_place_query,
)


def test_parse_bbox_string_ok() -> None:
    bbox = parse_bbox_string("10.0, -20.0, 30.0, 40.0")
    assert bbox == (10.0, -20.0, 30.0, 40.0)


def test_parse_bbox_string_bad() -> None:
    with pytest.raises(ValueError):
        parse_bbox_string("10,20,30")


def test_build_overpass_query_contains_bbox() -> None:
    q = build_overpass_query((1.0, 2.0, 3.0, 4.0))
    assert "1.0,2.0,3.0,4.0" in q
    assert 'man_made"="communications_tower' in q


def test_normalize_elements_node_and_way() -> None:
    from typing import Any

    elements: list[dict[str, Any]] = [
        {
            "type": "node",
            "id": 1,
            "lat": 10.1,
            "lon": 20.2,
            "tags": {"name": "Tower A", "man_made": "mast", "height": "30"},
        },
        {
            "type": "way",
            "id": 2,
            "center": {"lat": 11.1, "lon": 21.2},
            "tags": {"tower:type": "communication", "operator": "OpX"},
        },
    ]
    records = normalize_elements(elements)
    assert len(records) == 2
    assert records[0]["latitude"] == "10.1"
    assert records[0]["man_made"] == "mast"
    assert records[1]["tower_type"] == "communication"


def test_validate_bbox_valid() -> None:
    """Test validation of valid bounding box."""
    bbox = (37.7, -122.5, 37.8, -122.4)
    validated = validate_bbox(bbox)
    assert validated == bbox


def test_validate_bbox_invalid_lat() -> None:
    """Test validation fails for invalid latitude."""
    with pytest.raises(ValueError, match="Latitude values must be between"):
        validate_bbox((95.0, -122.5, 37.8, -122.4))


def test_validate_bbox_invalid_order() -> None:
    """Test validation fails for invalid coordinate ordering."""
    with pytest.raises(ValueError, match="South boundary must be less than north"):
        validate_bbox((37.8, -122.5, 37.7, -122.4))


def test_validate_place_query_valid() -> None:
    """Test validation of valid place query."""
    query = "San Francisco, CA"
    validated = validate_place_query(query)
    assert validated == query


def test_validate_place_query_empty() -> None:
    """Test validation fails for empty place query."""
    with pytest.raises(ValueError, match="Place query cannot be empty"):
        validate_place_query("")


def test_validate_place_query_too_long() -> None:
    """Test validation fails for overly long place query."""
    long_query = "A" * 250
    with pytest.raises(ValueError, match="Place query too long"):
        validate_place_query(long_query)


def test_parse_bbox_string_validation() -> None:
    """Test that parse_bbox_string includes validation."""
    # Should work for valid bbox
    bbox = parse_bbox_string("37.7,-122.5,37.8,-122.4")
    assert bbox == (37.7, -122.5, 37.8, -122.4)

    # Should fail for invalid bbox ordering
    with pytest.raises(ValueError):
        parse_bbox_string("37.8,-122.5,37.7,-122.4")
