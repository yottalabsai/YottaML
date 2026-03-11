from unittest.mock import patch

import pytest

from yottaml.elastic import ElasticApi


MOCK_WORKERS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": [
        {
            "id": "384428779525529885",
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
            "status": "INITIALIZE",
        },
        {
            "id": "384427270809247899",
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
            "status": "TERMINATED",
        },
    ],
}


@pytest.fixture
def elastic_api():
    return ElasticApi("key", base_url="https://api.dev.yottalabs.ai")


@patch.object(ElasticApi, "http_get")
def test_get_workers_with_status_list(mock_get, elastic_api):
    mock_get.return_value = MOCK_WORKERS_RESPONSE

    resp = elastic_api.get_workers(
        deployment_id=384414489660887859,
        status_list=["INITIALIZE", "RUNNING"],
    )

    mock_get.assert_called_once()
    path = mock_get.call_args[0][0]
    payload = mock_get.call_args[1].get("payload")

    assert path == "/v2/serverless/384414489660887859/workers"
    assert payload["statusList"] == "INITIALIZE,RUNNING"
    assert resp["code"] == 10000
    assert len(resp["data"]) == 2


@patch.object(ElasticApi, "http_get")
def test_get_workers_without_status_list(mock_get, elastic_api):
    mock_get.return_value = MOCK_WORKERS_RESPONSE

    resp = elastic_api.get_workers(deployment_id=384414489660887859)

    mock_get.assert_called_once()
    path = mock_get.call_args[0][0]
    payload = mock_get.call_args[1].get("payload")

    assert path == "/v2/serverless/384414489660887859/workers"
    assert "statusList" not in payload
    assert resp["code"] == 10000


