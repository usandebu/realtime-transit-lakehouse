from unittest.mock import Mock

import pytest
import requests

from realtime_transit.extract.errors import ExtractionError
from realtime_transit.extract.tfl import BASE_URL, fetch_arrivals, fetch_stop_points


def test_fetch_arrivals_returns_payload():
    expected_payload = [{"vehicleId": "011", "lineId": "central"}]

    response = Mock()
    response.json.return_value = expected_payload

    session = Mock()
    session.get.return_value = response

    result = fetch_arrivals(["central"], api_key="test-key", session=session)

    assert result == expected_payload

    session.get.assert_called_once_with(
        f"{BASE_URL}/Line/central/Arrivals",
        params={"app_key": "test-key"},
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()


def test_fetch_arrivals_joins_multiple_line_ids():
    response = Mock()
    response.json.return_value = []

    session = Mock()
    session.get.return_value = response

    fetch_arrivals(["central", "victoria"], api_key="test-key", session=session)

    session.get.assert_called_once_with(
        f"{BASE_URL}/Line/central,victoria/Arrivals",
        params={"app_key": "test-key"},
        timeout=10,
    )


def test_fetch_arrivals_rejects_unexpected_structure():
    response = Mock()
    response.json.return_value = {"message": "not a list"}

    session = Mock()
    session.get.return_value = response

    with pytest.raises(ExtractionError, match="Unexpected TfL arrivals response structure"):
        fetch_arrivals(["central"], api_key="test-key", session=session)


def test_fetch_arrivals_wraps_http_errors():
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")

    session = Mock()
    session.get.return_value = response

    with pytest.raises(ExtractionError, match="Failed to fetch TfL arrivals"):
        fetch_arrivals(["central"], api_key="test-key", session=session)


def test_fetch_arrivals_wraps_invalid_json():
    response = Mock()
    response.json.side_effect = ValueError("invalid json")

    session = Mock()
    session.get.return_value = response

    with pytest.raises(ExtractionError, match="TfL arrivals response is not valid JSON"):
        fetch_arrivals(["central"], api_key="test-key", session=session)


def test_fetch_stop_points_returns_stop_points():
    expected_stop_points = [{"naptanId": "940GZZLUOXC", "lat": 51.5, "lon": -0.14}]

    response = Mock()
    response.json.return_value = {"stopPoints": expected_stop_points}

    session = Mock()
    session.get.return_value = response

    result = fetch_stop_points("tube", api_key="test-key", session=session)

    assert result == expected_stop_points

    session.get.assert_called_once_with(
        f"{BASE_URL}/StopPoint/Mode/tube",
        params={"app_key": "test-key"},
        timeout=30,
    )


def test_fetch_stop_points_rejects_unexpected_structure():
    response = Mock()
    response.json.return_value = {"message": "no stop points here"}

    session = Mock()
    session.get.return_value = response

    with pytest.raises(ExtractionError, match="Unexpected TfL stop points response structure"):
        fetch_stop_points("tube", api_key="test-key", session=session)
