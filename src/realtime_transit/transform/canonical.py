def to_canonical(arrival: dict) -> dict:
    """Map a raw TfL Arrivals record to the pipeline's canonical vehicle-position schema.

    lat/lon are intentionally left unresolved here: joining naptan_id against the
    stations reference table is a Silver-layer concern (Spark broadcast join), not
    something Bronze should do — Bronze must stay a faithful, join-free copy of the
    source event.
    """
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
