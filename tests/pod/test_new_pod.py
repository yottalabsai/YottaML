from unittest.mock import patch

import pytest

from yotta.error import ClientError, ParameterRequiredError
from yotta.pod import PodApi

# Test data
VALID_CONFIG = {
    "image": "yottalabsai/pytorch:2.8.0",
    "gpu_type": "NVIDIA_L4_24G",
    "pod_name": "test_pod",
    "gpu_count": 1,
    "expose": [
        {"port": 22, "protocol": "SSH"}
    ]
}

MOCK_SUCCESS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": 123456789  # Pod ID
}

MOCK_ERROR_RESPONSE = {
    "code": 40001,
    "message": "error message",
    "data": None
}


@pytest.fixture
def pod_api():
    """Create a PodApi instance with a mock API key"""
    return PodApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_new_pod_minimal_config(pod_api):
    """Test creating a pod with minimal required configuration"""
    with patch.object(pod_api, 'http_post', return_value=MOCK_SUCCESS_RESPONSE) as mock_post:
        response = pod_api.new_pod(
            image=VALID_CONFIG["image"],
            gpu_type=VALID_CONFIG["gpu_type"],
            gpu_count=1,
        )

        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once()

        # Verify payload contains required fields
        call_args = mock_post.call_args[0]
        payload = call_args[1]
        assert payload["image"] == VALID_CONFIG["image"]
        assert payload["gpuType"] == VALID_CONFIG["gpu_type"]


def test_new_pod_full_config(pod_api):
    """Test creating a pod with all optional parameters"""
    full_config = {
        **VALID_CONFIG,
        "region": "us-west-1",
        "cloud_type": "SECURE",
        "official_image": "OFFICIAL",
        "image_public_type": "PUBLIC",
        "resource_type": "GPU",
        "container_volume_in_gb": 20,
        "persistent_volume_in_gb": 10,
        "persistent_mount_path": "/data",
        "initialization_command": "echo 'init'",
        "environment_vars": [{"key": "TEST", "value": "value"}]
    }

    with patch.object(pod_api, 'http_post', return_value=MOCK_SUCCESS_RESPONSE) as mock_post:
        response = pod_api.new_pod(**full_config)

        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once()

        # Verify all fields are in payload
        call_args = mock_post.call_args[0]
        payload = call_args[1]
        assert payload["region"] == full_config["region"]
        assert payload["cloudType"] == full_config["cloud_type"]
        assert payload["podName"] == full_config["pod_name"]
        assert payload["image"] == full_config["image"]
        assert payload["officialImage"] == full_config["official_image"]
        assert payload["imagePublicType"] == full_config["image_public_type"]
        assert payload["resourceType"] == full_config["resource_type"]
        assert payload["gpuType"] == full_config["gpu_type"]
        assert payload["gpuCount"] == full_config["gpu_count"]
        assert payload["containerVolumeInGb"] == full_config["container_volume_in_gb"]
        assert payload["persistentVolumeInGb"] == full_config["persistent_volume_in_gb"]
        assert payload["persistentMountPath"] == full_config["persistent_mount_path"]
        assert payload["initializationCommand"] == full_config["initialization_command"]
        assert payload["environmentVars"] == full_config["environment_vars"]
        assert payload["expose"] == full_config["expose"]


def test_new_pod_missing_required_params(pod_api):
    """Test that creating a pod without required parameters raises an error"""
    with pytest.raises(ParameterRequiredError) as exc_info:
        pod_api.new_pod(image=None, gpu_type=None)
    assert "image" in str(exc_info.value)

    with pytest.raises(ParameterRequiredError) as exc_info:
        pod_api.new_pod(image=VALID_CONFIG["image"], gpu_type=None)
    assert "gpu_type" in str(exc_info.value)


def test_new_pod_client_error(pod_api):
    """Test handling of client errors"""
    with patch.object(pod_api, 'http_post', side_effect=ClientError(
            status_code=400,
            error_code=10001,
            error_message="Invalid parameters",
            header={},
            error_data=None
    )):
        with pytest.raises(ClientError) as exc_info:
            pod_api.new_pod(**VALID_CONFIG)

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == 10001
        assert "Invalid parameters" in str(exc_info.value.error_message)


def test_new_pod_with_registry_credentials(pod_api):
    """Test creating a pod with private registry credentials"""
    config = {
        **VALID_CONFIG,
        "image_registry_username": "user",
        "image_registry_token": "token"
    }

    with patch.object(pod_api, 'http_post', return_value=MOCK_SUCCESS_RESPONSE) as mock_post:
        response = pod_api.new_pod(**config)

        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once()

        # Verify registry credentials are in payload
        call_args = mock_post.call_args[0]
        payload = call_args[1]
        assert payload["imageRegistryUsername"] == config["image_registry_username"]
        assert payload["imageRegistryToken"] == config["image_registry_token"]


def test_new_pod_with_exposed_ports(pod_api):
    """Test creating a pod with various exposed ports"""
    config = {
        **VALID_CONFIG,
        "expose": [
            {"port": 22, "protocol": "SSH"},
            {"port": 80, "protocol": "HTTP"},
            {"port": 443, "protocol": "HTTPS"}
        ]
    }

    with patch.object(pod_api, 'http_post', return_value=MOCK_SUCCESS_RESPONSE) as mock_post:
        response = pod_api.new_pod(**config)

        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once()

        # Verify exposed ports are in payload
        call_args = mock_post.call_args[0]
        payload = call_args[1]
        assert payload["expose"] == config["expose"]
        assert len(payload["expose"]) == 3
