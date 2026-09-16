import json
import os
import time
from datetime import UTC, datetime

from confluent_kafka import Producer
from dotenv import load_dotenv

from realtime_transit.extract.errors import ExtractionError
from realtime_transit.extract.tfl import fetch_arrivals
from realtime_transit.transform.canonical import to_canonical

LINES = ["central", "victoria", "bakerloo"]
TOPIC = "transit.vehicle_positions"
POLL_INTERVAL_SECONDS = 30


def delivery_report(err, msg) -> None:
    if err is not None:
        print(f"Delivery failed for {msg.key()}: {err}")


def produce_arrivals(producer: Producer, api_key: str) -> None:
    arrivals = fetch_arrivals(LINES, api_key)
    for arrival in arrivals:
        record = to_canonical(arrival)
        producer.produce(
            TOPIC,
            key=record["vehicle_id"],
            value=json.dumps(record),
            callback=delivery_report,
        )
    producer.flush()
    print(f"[{datetime.now(UTC).isoformat()}] Produced {len(arrivals)} records")


def main() -> None:
    load_dotenv()
    api_key = os.environ["TFL_API_KEY"]
    producer = Producer({"bootstrap.servers": "localhost:9092"})

    print(f"Polling TfL Arrivals for lines {LINES} every {POLL_INTERVAL_SECONDS}s. Ctrl+C to stop.")
    try:
        while True:
            try:
                produce_arrivals(producer, api_key)
            except ExtractionError as error:
                print(f"Skipping this poll cycle: {error}")
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Stopping producer...")
        producer.flush()


if __name__ == "__main__":
    main()
