from unittest.mock import patch

import pytest

from yotta.elastic import ElasticApi
from yotta.error import ClientError, ParameterRequiredError

MOCK_UPDATE_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": {
        "id": "384414489660887859",
        "name": "Llama-3.2-3B",
        "image": "vllm/vllm-openai:latest",
        "status": "STOPPED",
    },
}


@pytest.fixture
def elastic_api():
    return ElasticApi("key", base_url="https://api.dev.yottalabs.ai")


@patch.object(ElasticApi, "http_post")
def test_update_deployment_success(mock_post, elastic_api):
    mock_post.return_value = MOCK_UPDATE_RESPONSE

    resources = [
        {
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
        }
    ]

    resp = elastic_api.update_deployment(
        deployment_id=384414489660887859,
        name="Llama-3.2-3B3",
        resources=resources,
        min_single_card_vram_in_gb=12,
        min_single_card_vcpu=10,
        min_single_card_ram_in_gb=14,
        workers=1,
        container_volume_in_gb=20,
        initialization_command="echo update",
        environment_vars=[{"key": "CUDA_VISIBLE_DEVICES", "value": "1"}],
        expose={"port": 8000, "protocol": "http"},
    )

    mock_post.assert_called_once()
    path, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
    payload = kwargs.get("payload", {})

    assert path == "/openapi/v1/elastic/deploy/384414489660887859/update"
    assert payload["name"] == "Llama-3.2-3B3"
    assert payload["resources"] == resources
    assert payload["workers"] == 1
    assert payload["containerVolumeInGb"] == 20
    assert resp == MOCK_UPDATE_RESPONSE


def test_update_deployment_missing_required(elastic_api):
    resources = [
        {
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
        }
    ]

    with pytest.raises(ParameterRequiredError):
        elastic_api.update_deployment(
            deployment_id=384414489660887859,
            name=None,
            resources=resources,
            workers=1,
            container_volume_in_gb=120,
        )

    with pytest.raises(ParameterRequiredError):
        elastic_api.update_deployment(
            deployment_id=384414489660887859,
            name="name",
            resources=None,
            workers=1,
            container_volume_in_gb=120,
        )

    with pytest.raises(ParameterRequiredError):
        elastic_api.update_deployment(
            deployment_id=384414489660887859,
            name="name",
            resources=resources,
            workers=None,
            container_volume_in_gb=120,
        )

    with pytest.raises(ParameterRequiredError):
        elastic_api.update_deployment(
            deployment_id=384414489660887859,
            name="name",
            resources=resources,
            workers=1,
            container_volume_in_gb=None,
        )


def test_update_deployment_invalid_workers(elastic_api):
    resources = [
        {
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
        }
    ]

    with pytest.raises(ValueError):
        elastic_api.update_deployment(
            deployment_id=384414489660887859,
            name="n",
            resources=resources,
            workers=0,
            container_volume_in_gb=120,
        )


def test_update_deployment_client_error(elastic_api):
    resources = [
        {
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
        }
    ]

    with patch.object(
            elastic_api,
            "http_post",
            side_effect=ClientError(
                status_code=400,
                error_code=20002,
                error_message="Update elastic deployment failed",
                header={},
                error_data=None,
            ),
    ):
        with pytest.raises(ClientError) as exc_info:
            elastic_api.update_deployment(
                deployment_id=384414489660887859,
                name="n",
                resources=resources,
                workers=1,
                container_volume_in_gb=120,
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == 20002
        assert "Update elastic deployment failed" in str(exc_info.value.error_message)
