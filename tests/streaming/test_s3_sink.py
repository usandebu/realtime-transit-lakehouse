from datetime import UTC, datetime
from unittest.mock import Mock

from realtime_transit.streaming.s3_sink import (
    build_s3_key,
    flush_batch,
    records_to_ndjson,
)


def test_build_s3_key_uses_hive_style_partitioning():
    now = datetime(2026, 9, 17, 14, 30, 0, 123456, tzinfo=UTC)

    key = build_s3_key(now)

    assert key.startswith("landing/vehicle_positions/year=2026/month=09/day=17/")
    assert key.endswith(".json")


def test_build_s3_key_is_unique_across_calls():
    now = datetime(2026, 9, 17, 14, 30, 0, 123456, tzinfo=UTC)

    first_key = build_s3_key(now)
    second_key = build_s3_key(now)

    assert first_key != second_key


def test_records_to_ndjson_writes_one_json_object_per_line():
    records = [{"vehicle_id": "1"}, {"vehicle_id": "2"}]

    result = records_to_ndjson(records)

    assert result == '{"vehicle_id": "1"}\n{"vehicle_id": "2"}'


def test_flush_batch_skips_empty_batch():
    s3_client = Mock()

    flush_batch(s3_client, bucket="test-bucket", records=[])

    s3_client.put_object.assert_not_called()


def test_flush_batch_writes_records_to_s3():
    s3_client = Mock()
    records = [{"vehicle_id": "1"}]

    flush_batch(s3_client, bucket="test-bucket", records=records)

    s3_client.put_object.assert_called_once()
    call = s3_client.put_object.call_args
    assert call.kwargs["Bucket"] == "test-bucket"
    assert call.kwargs["Key"].startswith("landing/vehicle_positions/year=")
    assert call.kwargs["Body"] == b'{"vehicle_id": "1"}'
