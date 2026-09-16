from realtime_transit.transform.canonical import to_canonical


def test_to_canonical_maps_tfl_fields():
    arrival = {
        "vehicleId": "011",
        "lineId": "central",
        "lineName": "Central",
        "naptanId": "940GZZLUOXC",
        "timestamp": "2026-09-16T18:36:06.4189329Z",
    }

    result = to_canonical(arrival)

    assert result == {
        "vehicle_id": "011",
        "feed_source": "tfl",
        "line": "central",
        "naptan_id": "940GZZLUOXC",
        "lat": None,
        "lon": None,
        "timestamp": "2026-09-16T18:36:06.4189329Z",
        "status": "active",
        "trip_id": None,
    }


def test_to_canonical_does_not_resolve_coordinates():
    arrival = {
        "vehicleId": "011",
        "lineId": "central",
        "naptanId": "940GZZLUOXC",
        "timestamp": "2026-09-16T18:36:06.4189329Z",
    }

    result = to_canonical(arrival)

    assert result["lat"] is None
    assert result["lon"] is None
