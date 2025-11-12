import pytest
from unittest.mock import patch
from yotta.elastic import ElasticApi


@patch.object(ElasticApi, "http_get")
def test_get_endpoint_valid(mock_get):
    mock_get.return_value = {"code": 10000, "message": "success", "data": {"id": "123"}}

    api = ElasticApi("key")
    result = api.get_endpoint(123)

    mock_get.assert_called_once_with("/openapi/v1/elastic/deploy/123")
    assert result["code"] == 10000


@patch.object(ElasticApi, "http_get")
def test_get_endpoint_invalid_id(mock_get):
    api = ElasticApi("key")
    with pytest.raises(ValueError):
        api.get_endpoint("abc")  # 非数字 ID 不允许
