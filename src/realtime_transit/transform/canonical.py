def to_canonical(arrival: dict) -> dict:
    """Map a raw TfL Arrivals record to the canonical vehicle-position schema."""
    return {
        "vehicle_id": arrival["vehicleId"],
        "feed_source": "tfl",
        "line": arrival["lineId"],
        "naptan_id": arrival["naptanId"],
        "lat": None,
        "lon": None,
        "timestamp": arrival["timestamp"],
        "status": "active",
        "trip_id": None,
    }
