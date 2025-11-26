from unittest.mock import patch

import pytest

from yotta.elastic import ElasticApi
from yotta.error import ClientError, ParameterRequiredError


MOCK_CREATE_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": "384425425995034706",
}


@pytest.fixture
def elastic_api():
    return ElasticApi("key", base_url="https://api.dev.yottalabs.ai")


@patch.object(ElasticApi, "http_post")
def test_create_deployment_success(mock_post, elastic_api):
    mock_post.return_value = MOCK_CREATE_RESPONSE

    resources = [
        {
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
        }
    ]

    resp = elastic_api.create_deployment(
        name="Llama-3.2-3B",
        image="vllm/vllm-openai:latest",
        image_registry="https://index.docker.io/v1",
        resources=resources,
        min_single_card_vram_in_gb=6,
        min_single_card_vcpu=2,
        min_single_card_ram_in_gb=4,
        workers=1,
        service_mode="ALB",
        credential_id=361530338086227968,
        container_volume_in_gb=20,
        initialization_command="vllm serve meta-llama/Llama-3.2-3B-Instruct --served-model-name meta-llama/Llama-3.2-3B-Instruct  --max-model-len 20480 --port 8000 --dtype half --gpu-memory-utilization 0.90 --tensor-parallel-size 1 --chat-template /vllm-workspace/examples/tool_chat_template_llama3.2_json.jinja",
        environment_vars=[{"key": "VLLM_PORT", "value": "8000"}],
        expose=[{"port": 8000, "protocol": "HTTP"}],
    )

    mock_post.assert_called_once()
    path, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
    payload = kwargs.get("payload", {})

    assert path == "/openapi/v1/elastic/deploy/create"
    assert payload["name"] == "Llama-3.2-3B"
    assert payload["image"] == "vllm/vllm-openai:latest"
    assert payload["imageRegistry"] == "https://index.docker.io/v1"
    assert payload["resources"] == resources
    assert payload["workers"] == 1
    assert payload["serviceMode"] == "ALB"
    assert payload["credentialId"] == 361530338086227968
    assert resp == MOCK_CREATE_RESPONSE


def test_create_deployment_missing_required(elastic_api):
    resources = [
        {
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
        }
    ]

    with pytest.raises(ParameterRequiredError):
        elastic_api.create_deployment(
            name=None,
            image="img",
            image_registry="reg",
            resources=resources,
            workers=1,
            service_mode="ALB",
            credential_id=1,
        )

    with pytest.raises(ParameterRequiredError):
        elastic_api.create_deployment(
            name="n",
            image=None,
            image_registry="reg",
            resources=resources,
            workers=1,
            service_mode="ALB",
            credential_id=1,
        )

    with pytest.raises(ParameterRequiredError):
        elastic_api.create_deployment(
            name="n",
            image="img",
            image_registry=None,
            resources=resources,
            workers=1,
            service_mode="ALB",
            credential_id=1,
        )


def test_create_deployment_invalid_workers(elastic_api):
    resources = [
        {
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
        }
    ]

    with pytest.raises(ValueError):
        elastic_api.create_deployment(
            name="n",
            image="img",
            image_registry="reg",
            resources=resources,
            workers=0,
            service_mode="ALB",
            credential_id=1,
        )


def test_create_deployment_client_error(elastic_api):
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
            error_code=20001,
            error_message="Create elastic deployment failed",
            header={},
            error_data=None,
        ),
    ):
        with pytest.raises(ClientError) as exc_info:
            elastic_api.create_deployment(
                name="n",
                image="img",
                image_registry="reg",
                resources=resources,
                workers=1,
                service_mode="ALB",
                credential_id=1,
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == 20001
        assert "Create elastic deployment failed" in str(exc_info.value.error_message)


