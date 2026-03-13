from unittest.mock import patch

import pytest

from yottaml.error import ClientError, ParameterRequiredError
from yottaml.pod import PodApi

VALID_CONFIG = {
    "image": "pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime",
    "gpu_type": "RTX_4090_24G",
    "name": "test_pod",
    "gpu_count": 1,
    "expose": [{"port": 22, "protocol": "SSH"}],
}

MOCK_SUCCESS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": {"id": 789, "name": "test_pod", "status": "RUNNING"},
}


@pytest.fixture
def pod_api():
    return PodApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_new_pod_minimal_config(pod_api):
    with patch.object(
        pod_api, "http_post", return_value=MOCK_SUCCESS_RESPONSE
    ) as mock_post:
        response = pod_api.new_pod(
            image=VALID_CONFIG["image"], gpu_type=VALID_CONFIG["gpu_type"], gpu_count=1
        )
        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once()
        payload = mock_post.call_args[0][1]
        assert payload["image"] == VALID_CONFIG["image"]
        assert payload["gpuType"] == VALID_CONFIG["gpu_type"]


def test_new_pod_full_config(pod_api):
    full_config = {
        **VALID_CONFIG,
        "regions": ["us-west-1"],
        "image_public_type": "PUBLIC",
        "resource_type": "GPU",
        "min_single_card_vram_in_gb": 24,
        "min_single_card_ram_in_gb": 20,
        "container_volume_in_gb": 20,
        "persistent_volume_in_gb": 10,
        "persistent_mount_path": "/data",
        "initialization_command": "echo 'init'",
        "environment_vars": [{"key": "TEST", "value": "value"}],
    }

    with patch.object(
        pod_api, "http_post", return_value=MOCK_SUCCESS_RESPONSE
    ) as mock_post:
        response = pod_api.new_pod(**full_config)
        assert response == MOCK_SUCCESS_RESPONSE
        payload = mock_post.call_args[0][1]
        assert payload["name"] == full_config["name"]
        assert payload["regions"] == full_config["regions"]
        assert payload["image"] == full_config["image"]
        assert payload["imagePublicType"] == full_config["image_public_type"]
        assert payload["resourceType"] == full_config["resource_type"]
        assert payload["gpuType"] == full_config["gpu_type"]
        assert payload["gpuCount"] == full_config["gpu_count"]
        assert (
            payload["minSingleCardVramInGb"]
            == full_config["min_single_card_vram_in_gb"]
        )
        assert (
            payload["minSingleCardRamInGb"] == full_config["min_single_card_ram_in_gb"]
        )
        assert payload["containerVolumeInGb"] == full_config["container_volume_in_gb"]
        assert payload["persistentVolumeInGb"] == full_config["persistent_volume_in_gb"]
        assert payload["persistentMountPath"] == full_config["persistent_mount_path"]
        assert payload["initializationCommand"] == full_config["initialization_command"]
        assert payload["environmentVars"] == full_config["environment_vars"]
        assert payload["expose"] == full_config["expose"]


def test_new_pod_missing_required_params(pod_api):
    with pytest.raises(ParameterRequiredError) as exc_info:
        pod_api.new_pod(image=None, gpu_type=None)
    assert "image" in str(exc_info.value)

    with pytest.raises(ParameterRequiredError) as exc_info:
        pod_api.new_pod(image=VALID_CONFIG["image"], gpu_type=None)
    assert "gpu_type" in str(exc_info.value)


def test_new_pod_client_error(pod_api):
    with patch.object(
        pod_api,
        "http_post",
        side_effect=ClientError(400, 10001, "Invalid parameters", {}, None),
    ):
        with pytest.raises(ClientError) as exc_info:
            pod_api.new_pod(**VALID_CONFIG)
        assert exc_info.value.status_code == 400
        assert "Invalid parameters" in str(exc_info.value.error_message)


def test_new_pod_with_registry_credentials(pod_api):
    config = {**VALID_CONFIG, "container_registry_auth_id": 12345}
    with patch.object(
        pod_api, "http_post", return_value=MOCK_SUCCESS_RESPONSE
    ) as mock_post:
        response = pod_api.new_pod(**config)
        assert response == MOCK_SUCCESS_RESPONSE
        payload = mock_post.call_args[0][1]
        assert (
            payload["containerRegistryAuthId"] == config["container_registry_auth_id"]
        )


def test_new_pod_with_exposed_ports(pod_api):
    config = {
        **VALID_CONFIG,
        "expose": [
            {"port": 22, "protocol": "SSH"},
            {"port": 80, "protocol": "HTTP"},
            {"port": 443, "protocol": "HTTPS"},
        ],
    }
    with patch.object(
        pod_api, "http_post", return_value=MOCK_SUCCESS_RESPONSE
    ) as mock_post:
        response = pod_api.new_pod(**config)
        assert response == MOCK_SUCCESS_RESPONSE
        payload = mock_post.call_args[0][1]
        assert len(payload["expose"]) == 3
