import pytest
from unittest.mock import patch
from yotta.elastic import ElasticApi

# ------------------------------------------------------
# Mock dataset used to validate returned `data` field
# ------------------------------------------------------
MOCK_DATA = [
    {
        "id": "381105364051694317",
        "name": "jobs_test_queue_new2",
        "status": "RUNNING",
        "runningWorkers": 3,
        "totalWorkers": 5,
    },
    {
        "id": "381105364051694318",
        "name": "jobs_test_queue_new3",
        "status": "STOPPED",
        "runningWorkers": 0,
        "totalWorkers": 2,
    },
]


# ======================================================
# Test 1 — Valid status list: RUNNING + STOPPED
# Ensures:
#   - statusList is normalized and passed correctly
#   - http_get is invoked with correct path and payload
#   - returned data fields are preserved and accessible
# ======================================================
@patch.object(ElasticApi, "http_get")
def test_get_endpoints_with_status(mock_get):
    mock_get.return_value = {"code": 10000, "message": "success", "data": MOCK_DATA}

    api = ElasticApi("test-key", base_url="https://api.dev.yottalabs.ai")
    result = api.get_endpoints(status_list=["RUNNING", "STOPPED"])

    # Ensure one HTTP GET call occurred
    mock_get.assert_called_once()

    path = mock_get.call_args[0][0]
    payload = mock_get.call_args[1].get("payload")

    # Verify correct endpoint path
    assert path == "/openapi/v1/elastic/deploy/list"

    # Verify payload contains normalized CSV status list
    assert payload["statusList"] == "RUNNING,STOPPED"

    # Verify returned result content
    assert result["code"] == 10000
    assert len(result["data"]) == 2
    assert result["data"][0]["name"] == "jobs_test_queue_new2"


# ======================================================
# Test 2 — Passing an empty list should NOT send `statusList`
# Ensures:
#   - The client omits the parameter entirely
#   - Backend receives a clean query without `statusList`
# ======================================================
@patch.object(ElasticApi, "http_get")
def test_get_endpoints_empty_status(mock_get):
    mock_get.return_value = {"code": 10000, "message": "ok", "data": []}

    api = ElasticApi("test-key")
    api.get_endpoints(status_list=[])

    _, kwargs = mock_get.call_args
    payload = kwargs.get("payload")

    # statusList should not appear in payload
    assert "statusList" not in payload


# ======================================================
# Test 3 — The example script expands alias 'active'
# to INITIALIZING,RUNNING before calling this method.
#
# This test ensures:
#   - The client receives normalized tokens
#   - The payload uses plain comma-separated uppercase values
# ======================================================
@patch.object(ElasticApi, "http_get")
def test_get_endpoints_alias_active(mock_get):
    mock_get.return_value = {"code": 10000, "message": "success", "data": []}

    api = ElasticApi("test-key")

    # Example script would already expand 'active'
    result = api.get_endpoints(status_list=["INITIALIZING", "RUNNING"])

    payload = mock_get.call_args[1].get("payload")

    assert payload["statusList"] == "INITIALIZING,RUNNING"
    assert result["code"] == 10000


# ======================================================
# Test 4 — Verify returned `data` structure is preserved
# Ensures:
#   - get_endpoints returns the backend `data` field verbatim
#   - no unexpected mutation or filtering occurs on the client side
# ======================================================
@patch.object(ElasticApi, "http_get")
def test_get_endpoints_result_data_integrity(mock_get):
    mock_get.return_value = {"code": 10000, "message": "success", "data": MOCK_DATA}

    api = ElasticApi("key")
    resp = api.get_endpoints(status_list=["RUNNING"])

    # Validate structure integrity
    assert isinstance(resp["data"], list)
    assert resp["data"][0]["id"] == MOCK_DATA[0]["id"]
    assert resp["data"][1]["status"] == "STOPPED"
    assert resp["data"][1]["runningWorkers"] == 0
    assert resp["data"][1]["totalWorkers"] == 2
