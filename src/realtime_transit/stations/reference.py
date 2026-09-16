def build_reference(stop_points: list[dict]) -> dict:
    return {
        sp["naptanId"]: {
            "name": sp.get("commonName"),
            "lat": sp.get("lat"),
            "lon": sp.get("lon"),
        }
        for sp in stop_points
        if sp.get("lat") is not None and sp.get("lon") is not None
    }
