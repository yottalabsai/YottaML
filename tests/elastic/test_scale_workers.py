import pytest
from unittest.mock import patch
from yotta.elastic import ElasticApi


@patch.object(ElasticApi, "http_post")
def test_scale_workers_success(mock_post):
    mock_post.return_value = {"code": 10000, "message": "success", "data": None}

    api = ElasticApi("k")
    resp = api.scale_workers(123456, 2)

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    path = args[0]
    payload = kwargs.get("payload")

    assert path == "/openapi/v1/elastic/deploy/123456/workers"
    assert payload["workers"] == 2
    assert resp["code"] == 10000


@patch.object(ElasticApi, "http_post")
def test_scale_workers_invalid_worker_count(mock_post):
    api = ElasticApi("k")
    with pytest.raises(ValueError):
        api.scale_workers(1, -3)  # 不允许负数
