from realtime_transit.stations.reference import build_reference


def test_build_reference_keeps_stations_with_coordinates():
    stop_points = [
        {"naptanId": "940GZZLUOXC", "commonName": "Oxford Circus", "lat": 51.515, "lon": -0.142},
    ]

    result = build_reference(stop_points)

    assert result == {
        "940GZZLUOXC": {"name": "Oxford Circus", "lat": 51.515, "lon": -0.142},
    }


def test_build_reference_skips_stations_without_coordinates():
    stop_points = [
        {"naptanId": "940GZZLUOXC", "commonName": "Oxford Circus", "lat": 51.515, "lon": -0.142},
        {"naptanId": "940GZZLUABC", "commonName": "No Coordinates"},
    ]

    result = build_reference(stop_points)

    assert list(result.keys()) == ["940GZZLUOXC"]
