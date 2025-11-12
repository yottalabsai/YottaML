import pytest
from unittest.mock import patch
from yotta.elastic import ElasticApi


@patch.object(ElasticApi, "http_get")
def test_get_endpoints_with_status(mock_get):
    mock_get.return_value = {"code": 10000, "message": "success", "data": []}
    api = ElasticApi("test-key", base_url="https://api.dev.yottalabs.ai")

    result = api.get_endpoints(status_list=["running", "STOPPED"])
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    path = args[0]
    payload = kwargs.get("payload")

    assert path == "/openapi/v1/elastic/deploy/list"
    assert "statusList" in payload
    assert payload["statusList"] == "RUNNING,STOPPED"
    assert result["code"] == 10000


@patch.object(ElasticApi, "http_get")
def test_get_endpoints_empty_status(mock_get):
    mock_get.return_value = {"code": 10000, "message": "ok", "data": []}
    api = ElasticApi("test-key")
    api.get_endpoints(status_list=[])
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    payload = kwargs.get("payload")
    assert "statusList" not in payload


@patch.object(ElasticApi, "http_get")
def test_get_endpoints_alias_active(mock_get):
    """
    When caller expands 'active' to INITIALIZING,RUNNING (examples side),
    client should receive normalized upper-case CSV in payload.
    """
    mock_get.return_value = {"code": 10000, "message": "success", "data": []}
    api = ElasticApi("test-key")

    # emulate examples/get_endpoints.py normalization result
    result = api.get_endpoints(status_list=["INITIALIZING", "RUNNING"])
    args, kwargs = mock_get.call_args
    payload = kwargs.get("payload")
    assert payload["statusList"] == "INITIALIZING,RUNNING"
