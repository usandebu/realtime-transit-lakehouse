import json
import os
from pathlib import Path

from dotenv import load_dotenv

from realtime_transit.extract.tfl import fetch_stop_points
from realtime_transit.stations.reference import build_reference

MODES = "tube"
OUTPUT_PATH = Path(__file__).parents[3] / "data" / "stations.json"


def main() -> None:
    load_dotenv()
    api_key = os.environ["TFL_API_KEY"]

    stop_points = fetch_stop_points(MODES, api_key)
    reference = build_reference(stop_points)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(reference, indent=2))
    print(f"Saved {len(reference)} stations to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
