import json
import os
import time
import uuid
from datetime import UTC, datetime

import boto3
from confluent_kafka import Consumer
from dotenv import load_dotenv

from realtime_transit.streaming.topics import VEHICLE_POSITIONS

FLUSH_INTERVAL_SECONDS = 30
S3_PREFIX = "landing/vehicle_positions"


def build_s3_key(now: datetime) -> str:
    """Build a Hive-partitioned S3 key: prefix/year=Y/month=M/day=D/file.json"""
    timestamp = now.strftime("%Y%m%dT%H%M%S%f")
    unique_suffix = uuid.uuid4().hex[:8]
    return (
        f"{S3_PREFIX}/year={now:%Y}/month={now:%m}/day={now:%d}/"
        f"{timestamp}_{unique_suffix}.json"
    )


def records_to_ndjson(records: list[dict]) -> str:
    """Serialize records as newline-delimited JSON (one JSON object per line)."""
    return "\n".join(json.dumps(record) for record in records)


def flush_batch(s3_client, bucket: str, records: list[dict]) -> None:
    if not records:
        return

    key = build_s3_key(datetime.now(UTC))
    body = records_to_ndjson(records).encode("utf-8")
    s3_client.put_object(Bucket=bucket, Key=key, Body=body)
    print(f"Wrote {len(records)} records to s3://{bucket}/{key}")


def main() -> None:
    load_dotenv()
    bucket = os.environ["LANDING_BUCKET_NAME"]

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ["PIPELINE_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["PIPELINE_AWS_SECRET_ACCESS_KEY"],
    )

    consumer = Consumer(
        {
            "bootstrap.servers": "localhost:9092",
            "group.id": "transit-s3-sink",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([VEHICLE_POSITIONS])

    print(
        f"Sinking '{VEHICLE_POSITIONS}' to s3://{bucket}/{S3_PREFIX} "
        f"every {FLUSH_INTERVAL_SECONDS}s. Ctrl+C to stop."
    )

    batch: list[dict] = []
    last_flush = time.monotonic()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is not None:
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                else:
                    batch.append(json.loads(msg.value()))

            if time.monotonic() - last_flush >= FLUSH_INTERVAL_SECONDS:
                flush_batch(s3_client, bucket, batch)
                consumer.commit()
                batch = []
                last_flush = time.monotonic()
    except KeyboardInterrupt:
        print("Stopping S3 sink...")
        flush_batch(s3_client, bucket, batch)
        consumer.commit()
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
