import requests

from realtime_transit.extract.errors import ExtractionError
from realtime_transit.extract.http import build_retry_session

BASE_URL = "https://api.tfl.gov.uk"


def fetch_arrivals(
    line_ids: list[str],
    api_key: str,
    session: requests.Session | None = None,
) -> list[dict]:
    if session is not None:
        return _fetch_arrivals(line_ids, api_key, session)

    with build_retry_session() as client:
        return _fetch_arrivals(line_ids, api_key, client)


def _fetch_arrivals(
    line_ids: list[str],
    api_key: str,
    client: requests.Session,
) -> list[dict]:
    url = f"{BASE_URL}/Line/{','.join(line_ids)}/Arrivals"

    try:
        response = client.get(url, params={"app_key": api_key}, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        raise ExtractionError("Failed to fetch TfL arrivals") from error
    except ValueError as error:
        raise ExtractionError("TfL arrivals response is not valid JSON") from error

    if not isinstance(payload, list):
        raise ExtractionError("Unexpected TfL arrivals response structure")

    return payload


def fetch_stop_points(
    modes: str,
    api_key: str,
    session: requests.Session | None = None,
) -> list[dict]:
    if session is not None:
        return _fetch_stop_points(modes, api_key, session)

    with build_retry_session() as client:
        return _fetch_stop_points(modes, api_key, client)


def _fetch_stop_points(
    modes: str,
    api_key: str,
    client: requests.Session,
) -> list[dict]:
    url = f"{BASE_URL}/StopPoint/Mode/{modes}"

    try:
        response = client.get(url, params={"app_key": api_key}, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        raise ExtractionError("Failed to fetch TfL stop points") from error
    except ValueError as error:
        raise ExtractionError("TfL stop points response is not valid JSON") from error

    if "stopPoints" not in payload:
        raise ExtractionError("Unexpected TfL stop points response structure")

    return payload["stopPoints"]
