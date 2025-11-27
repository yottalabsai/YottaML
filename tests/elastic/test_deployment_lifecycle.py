from unittest.mock import patch

import pytest

from yotta.elastic import ElasticApi
from yotta.error import ClientError, ParameterRequiredError


@pytest.fixture
def elastic_api():
    return ElasticApi("key", base_url="https://api.dev.yottalabs.ai")


@patch.object(ElasticApi, "http_post")
def test_stop_deployment_success(mock_post, elastic_api):
    mock_post.return_value = {"code": 10000, "message": "success", "data": "384425425995034706"}

    resp = elastic_api.stop_deployment(384414489660887859)

    mock_post.assert_called_once_with(
        "/openapi/v1/elastic/deploy/384414489660887859/stop",
        payload=None,
    )
    assert resp["code"] == 10000


@patch.object(ElasticApi, "http_post")
def test_start_deployment_success(mock_post, elastic_api):
    mock_post.return_value = {"code": 10000, "message": "success", "data": "384425425995034706"}

    resp = elastic_api.start_deployment(384414489660887859)

    mock_post.assert_called_once_with(
        "/openapi/v1/elastic/deploy/384414489660887859/start",
        payload=None,
    )
    assert resp["code"] == 10000


@patch.object(ElasticApi, "http_delete")
def test_delete_deployment_success(mock_delete, elastic_api):
    mock_delete.return_value = {"code": 10000, "message": "success", "data": None}

    resp = elastic_api.delete_deployment(384414489660887859)

    mock_delete.assert_called_once_with(
        "/openapi/v1/elastic/deploy/384414489660887859",
        payload=None,
    )
    assert resp["code"] == 10000


@patch.object(ElasticApi, "http_delete")
def test_delete_deployment_failed_action_not_allowed(mock_delete, elastic_api):
    mock_delete.return_value = {"code": 24002, "message": "Elastic action not allowed", "data": None}

    resp = elastic_api.delete_deployment(384414489660887859)

    mock_delete.assert_called_once_with(
        "/openapi/v1/elastic/deploy/384414489660887859",
        payload=None,
    )
    assert resp["code"] == 24002
    assert resp["message"] == "Elastic action not allowed"


def test_stop_start_delete_invalid_id(elastic_api):
    for invalid in [0, -1]:
        with pytest.raises(ValueError):
            elastic_api.stop_deployment(invalid)
        with pytest.raises(ValueError):
            elastic_api.start_deployment(invalid)
        with pytest.raises(ValueError):
            elastic_api.delete_deployment(invalid)

    with pytest.raises(ParameterRequiredError):
        elastic_api.stop_deployment(None)
    with pytest.raises(ParameterRequiredError):
        elastic_api.start_deployment(None)
    with pytest.raises(ParameterRequiredError):
        elastic_api.delete_deployment(None)


def test_delete_deployment_client_error(elastic_api):
    with patch.object(
        elastic_api,
        "http_delete",
        side_effect=ClientError(
            status_code=200,
            error_code=24002,
            error_message="Elastic action not allowed",
            header={},
            error_data=None,
        ),
    ):
        with pytest.raises(ClientError) as exc_info:
            elastic_api.delete_deployment(384414489660887859)

        assert exc_info.value.status_code == 200
        assert exc_info.value.error_code == 24002
        assert "Elastic action not allowed" in str(exc_info.value.error_message)


