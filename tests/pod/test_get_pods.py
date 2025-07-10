from unittest.mock import patch

import pytest

from yotta.error import ClientError
from yotta.pod import PodApi

# Mock response data
MOCK_EMPTY_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": []
}

MOCK_SINGLE_POD_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": [{
        "id": 123456789,
        "podName": "test-pod",
        "status": "RUNNING",
        "gpuType": "NVIDIA_L4_24G",
        "gpuCount": 1,
        "containerVolumeInGb": 20,
        "persistentVolumeInGb": 10,
        "networkUploadMbps": 1000,
        "environmentVars": [{"key": "TEST", "value": "value"}],
        "expose": [{"port": 22, "protocol": "SSH", "healthy": True}],
        "createdAt": "2024-03-14T12:00:00Z"
    }]
}

MOCK_MULTIPLE_PODS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": [
        {
            "id": 123456789,
            "podName": "test-pod-1",
            "status": "RUNNING",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
            "containerVolumeInGb": 20,
            "persistentVolumeInGb": 10,
            "networkUploadMbps": 1000,
            "environmentVars": [],
            "expose": [],
            "createdAt": "2024-03-14T12:00:00Z"
        },
        {
            "id": 987654321,
            "podName": "test-pod-2",
            "status": "INITIALIZE",
            "gpuType": "NVIDIA_A100",
            "gpuCount": 2,
            "containerVolumeInGb": 50,
            "persistentVolumeInGb": 100,
            "networkUploadMbps": 10000,
            "environmentVars": [{"key": "ENV1", "value": "val1"}],
            "expose": [
                {"port": 22, "protocol": "SSH", "healthy": True},
                {"port": 80, "protocol": "HTTP", "healthy": False}
            ],
            "createdAt": "2024-03-14T11:00:00Z"
        }
    ]
}

MOCK_ERROR_RESPONSE = {
    "code": 10001,
    "message": "error message",
    "data": None
}


@pytest.fixture
def pod_api():
    """Create a PodApi instance with a mock API key"""
    return PodApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_get_pods_empty_list(pod_api):
    """Test getting an empty list of pods"""
    with patch.object(pod_api, 'http_get', return_value=MOCK_EMPTY_RESPONSE) as mock_get:
        response = pod_api.get_pods()

        assert response == MOCK_EMPTY_RESPONSE
        mock_get.assert_called_once_with("/openapi/v1/pods/list", payload={})


def test_get_pods_single_pod(pod_api):
    """Test getting a list with a single pod"""
    with patch.object(pod_api, 'http_get', return_value=MOCK_SINGLE_POD_RESPONSE) as mock_get:
        response = pod_api.get_pods()

        assert response == MOCK_SINGLE_POD_RESPONSE
        assert len(response['data']) == 1
        pod = response['data'][0]
        assert pod['id'] == 123456789
        assert pod['podName'] == "test-pod"
        assert pod['status'] == "RUNNING"
        assert pod['gpuType'] == "NVIDIA_L4_24G"
        assert pod['gpuCount'] == 1
        assert len(pod['expose']) == 1
        assert pod['expose'][0]['port'] == 22
        assert pod['expose'][0]['protocol'] == "SSH"
        mock_get.assert_called_once_with("/openapi/v1/pods/list", payload={})


def test_get_pods_multiple_pods(pod_api):
    """Test getting a list with multiple pods"""
    with patch.object(pod_api, 'http_get', return_value=MOCK_MULTIPLE_PODS_RESPONSE) as mock_get:
        response = pod_api.get_pods()

        assert response == MOCK_MULTIPLE_PODS_RESPONSE
        assert len(response['data']) == 2

        # Verify first pod
        pod1 = response['data'][0]
        assert pod1['id'] == 123456789
        assert pod1['podName'] == "test-pod-1"
        assert pod1['status'] == "RUNNING"
        assert pod1['gpuCount'] == 1
        assert len(pod1['environmentVars']) == 0
        assert len(pod1['expose']) == 0

        # Verify second pod
        pod2 = response['data'][1]
        assert pod2['id'] == 987654321
        assert pod2['podName'] == "test-pod-2"
        assert pod2['status'] == "INITIALIZE"
        assert pod2['gpuCount'] == 2
        assert len(pod2['environmentVars']) == 1
        assert len(pod2['expose']) == 2

        mock_get.assert_called_once_with("/openapi/v1/pods/list", payload={})


def test_get_pods_client_error(pod_api):
    """Test handling of client errors"""
    with patch.object(pod_api, 'http_get', side_effect=ClientError(
            status_code=400,
            error_code=40001,
            error_message="Invalid API key",
            header={},
            error_data=None
    )):
        with pytest.raises(ClientError) as exc_info:
            pod_api.get_pods()

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == 40001
        assert "Invalid API key" in str(exc_info.value.error_message)


def test_get_pods_with_kwargs(pod_api):
    """Test getting pods with additional query parameters"""
    with patch.object(pod_api, 'http_get', return_value=MOCK_EMPTY_RESPONSE) as mock_get:
        kwargs = {"status": "RUNNING", "limit": 10}
        response = pod_api.get_pods(**kwargs)

        assert response == MOCK_EMPTY_RESPONSE
        mock_get.assert_called_once_with("/openapi/v1/pods/list", payload=kwargs)


def test_format_size():
    """Test size formatting utility function"""
    from examples.pod.get_pods import format_size

    assert format_size(100) == "100 GB"
    assert format_size(1024) == "1.0 TB"
    assert format_size(2048) == "2.0 TB"
    assert format_size(0) == "0 GB"


def test_format_network_speed():
    """Test network speed formatting utility function"""
    from examples.pod.get_pods import format_network_speed

    assert format_network_speed(100) == "100 Mbps"
    assert format_network_speed(1000) == "1.0 Gbps"
    assert format_network_speed(2500) == "2.5 Gbps"
    assert format_network_speed(0) == "0 Mbps"
