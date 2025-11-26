import pytest
from unittest.mock import patch
from yotta.elastic import ElasticApi
from yotta.error import ParameterRequiredError


# ----------------------------------------
# Test: valid deployment ID
# ----------------------------------------
@patch.object(ElasticApi, "http_get")
def test_get_deployment_valid(mock_get):
    mock_get.return_value = {
        "code": 10000,
        "message": "success",
        "data": {"id": 123, "status": "RUNNING"}
    }

    api = ElasticApi("key")
    result = api.get_endpoint(123)

    # verify request path
    mock_get.assert_called_once_with("/openapi/v1/elastic/deploy/123")

    # verify returned structure
    assert result["code"] == 10000
    assert "data" in result
    assert result["data"]["id"] == 123
    assert result["data"]["status"] == "RUNNING"


# ----------------------------------------
# Test: deployment_id is non-numeric → error
# ----------------------------------------
def test_get_deployment_invalid_id_type():
    api = ElasticApi("key")
    with pytest.raises(ValueError):
        api.get_endpoint("abc")    # must be numeric


# ----------------------------------------
# Test: deployment_id is negative → error
# ----------------------------------------
def test_get_deployment_negative_id():
    api = ElasticApi("key")
    with pytest.raises(ValueError):
        api.get_endpoint(-5)


# ----------------------------------------
# Test: deployment_id is missing (None) → error
# ----------------------------------------
def test_get_deployment_none_id():
    api = ElasticApi("key")
    with pytest.raises(ParameterRequiredError):
        api.get_endpoint(None)


# ----------------------------------------
# Test: get_endpoint should forward raw http_get response without modification
# ----------------------------------------
@patch.object(ElasticApi, "http_get")
def test_get_deployment_response_passthrough(mock_get):
    expected = {
        "code": 12345,
        "message": "custom",
        "data": {"id": 999, "extra": "field"}
    }
    mock_get.return_value = expected

    api = ElasticApi("key")
    result = api.get_endpoint(999)

    assert result is expected  # same object
    assert result["data"]["extra"] == "field"
