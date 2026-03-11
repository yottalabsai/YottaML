import pytest
from unittest.mock import patch
from yottaml.elastic import ElasticApi


@patch.object(ElasticApi, "http_put")
def test_scale_workers_success(mock_put):
    mock_put.return_value = {"code": 10000, "message": "success", "data": None}

    api = ElasticApi("k")
    resp = api.scale_workers(123456, 2)

    mock_put.assert_called_once()
    args, kwargs = mock_put.call_args
    path = args[0]
    payload = kwargs.get("payload")

    assert path == "/v2/serverless/123456/workers"
    assert payload["count"] == 2
    assert resp["code"] == 10000


@patch.object(ElasticApi, "http_put")
def test_scale_workers_invalid_worker_count(mock_put):
    api = ElasticApi("k")
    with pytest.raises(ValueError):
        api.scale_workers(1, -3)  # 不允许负数
