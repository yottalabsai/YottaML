from unittest.mock import patch

import pytest

from yottaml.error import ClientError
from yottaml.pod import PodApi


MOCK_EMPTY_RESPONSE = {"code": 10000, "message": "success", "data": []}

MOCK_SINGLE_POD_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": [{
        "id": 123456789,
        "name": "test-pod",
        "status": "RUNNING",
        "gpuType": "RTX_4090_24G",
        "gpuCount": 1,
        "expose": [{"port": 22, "protocol": "SSH", "healthy": True}],
    }]
}

MOCK_MULTIPLE_PODS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": [
        {"id": 123456789, "name": "test-pod-1", "status": "RUNNING", "gpuCount": 1, "environmentVars": [], "expose": []},
        {"id": 987654321, "name": "test-pod-2", "status": "INITIALIZING", "gpuCount": 2,
         "environmentVars": [{"key": "ENV1", "value": "val1"}],
         "expose": [{"port": 22, "protocol": "SSH"}, {"port": 80, "protocol": "HTTP"}]},
    ]
}


@pytest.fixture
def pod_api():
    return PodApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_get_pods_empty_list(pod_api):
    with patch.object(pod_api, 'http_get', return_value=MOCK_EMPTY_RESPONSE) as mock_get:
        response = pod_api.get_pods()
        assert response == MOCK_EMPTY_RESPONSE
        mock_get.assert_called_once_with("/v2/pods", payload={})


def test_get_pods_single_pod(pod_api):
    with patch.object(pod_api, 'http_get', return_value=MOCK_SINGLE_POD_RESPONSE) as mock_get:
        response = pod_api.get_pods()
        assert len(response['data']) == 1
        assert response['data'][0]['name'] == "test-pod"
        mock_get.assert_called_once_with("/v2/pods", payload={})


def test_get_pods_multiple_pods(pod_api):
    with patch.object(pod_api, 'http_get', return_value=MOCK_MULTIPLE_PODS_RESPONSE) as mock_get:
        response = pod_api.get_pods()
        assert len(response['data']) == 2
        mock_get.assert_called_once_with("/v2/pods", payload={})


def test_get_pods_client_error(pod_api):
    with patch.object(pod_api, 'http_get', side_effect=ClientError(400, 40001, "Invalid API key", {}, None)):
        with pytest.raises(ClientError) as exc_info:
            pod_api.get_pods()
        assert exc_info.value.status_code == 400


def test_get_pods_with_kwargs(pod_api):
    with patch.object(pod_api, 'http_get', return_value=MOCK_EMPTY_RESPONSE) as mock_get:
        kwargs = {"status": "RUNNING"}
        pod_api.get_pods(**kwargs)
        mock_get.assert_called_once_with("/v2/pods", payload=kwargs)


def test_format_size():
    from examples.pod.get_pods import format_size
    assert format_size(100) == "100 GB"
    assert format_size(1024) == "1.0 TB"
    assert format_size(0) == "0 GB"


def test_format_network_speed():
    from examples.pod.get_pods import format_network_speed
    assert format_network_speed(100) == "100 Mbps"
    assert format_network_speed(1000) == "1.0 Gbps"
    assert format_network_speed(0) == "0 Mbps"
