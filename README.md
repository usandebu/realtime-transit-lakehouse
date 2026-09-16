# realtime-transit-lakehouse

> **Work in progress.** This project is a work in progress.

Streaming pipeline that ingests live vehicle positions from two European public transport networks (Transport for London and Berlin's VBB) in two different formats (JSON and GTFS-Realtime/protobuf), normalizes them into a common canonical schema, and processes them with Spark Structured Streaming on a Delta Lake medallion architecture (Bronze/Silver/Gold).

## Status

**Phase 1 complete:** TfL producer → Kafka → consumer, validated end-to-end.

- [x] Kafka (KRaft) running locally in Docker
- [x] TfL Unified API producer (polls live arrivals, normalizes to canonical schema)
- [x] Simple consumer for pipeline validation
- [x] Stations reference builder (naptanId → lat/lon lookup table)
- [x] Tests, linting (ruff), CI (GitHub Actions)
- [ ] Spark Structured Streaming + Delta Lake (Bronze/Silver)
- [ ] VBB Berlin (GTFS-Realtime/protobuf) source
- [ ] Gold layer + Grafana dashboard
- [ ] Power BI, Terraform, AWS deployment

## Why this project

Public transport data is real, live, and high-volume — no synthetic datasets. Combining TfL (JSON) and VBB (GTFS-Realtime/protobuf) demonstrates handling both a conventional REST API and the transport industry's de facto binary streaming standard within the same canonical pipeline.

## Architecture (target)

```text
TfL (JSON) + VBB (protobuf) -> canonical schema -> Kafka (local Docker)
  -> Spark Structured Streaming (watermarking, dedupe) -> Delta Lake (Bronze/Silver/Gold)
  -> Grafana (operations) + Power BI (business)
```

## Tech stack

- **Streaming:** Kafka (KRaft mode), Docker Compose
- **Processing:** PySpark / Spark Structured Streaming (planned)
- **Storage:** Delta Lake on AWS S3, Databricks
- **Orchestration:** Airflow (self-hosted in Docker)
- **Language/tooling:** Python, `uv`, `ruff`, `pytest`
- **CI:** GitHub Actions

## Design decisions

- **Bronze stays join-free.** The TfL producer normalizes fields into the canonical schema but does _not_ resolve `naptan_id` into `lat`/`lon` — that lookup is a join against a reference dataset, and joins belong in Silver (Spark broadcast join), not Bronze.
- **`line` uses `lineId`**, not `lineName` — a stable machine key, not a display string.
- **Local Kafka and Airflow, not MSK/MWAA.** This project runs on a tight AWS budget; managed streaming/orchestration services would burn it in hours.

## Running locally

```bash
docker compose up -d              # start Kafka
uv sync --dev                     # install dependencies
uv run python -m realtime_transit.stations.build       # build stations reference table
uv run python -m realtime_transit.streaming.consumer   # terminal 1
uv run python -m realtime_transit.streaming.producer   # terminal 2
```

Requires a free TfL API key (`TFL_API_KEY` in `.env`) from https://api-portal.tfl.gov.uk/.

## Testing & CI

```bash
uv run ruff check src tests
uv run pytest -q tests
```

Both run automatically on every push to `main` and on every pull request.
