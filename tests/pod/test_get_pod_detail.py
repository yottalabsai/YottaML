from unittest.mock import patch

import pytest

from yotta.error import ClientError
from yotta.pod import PodApi


MOCK_DETAIL_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": {
        "id": 123,
        "podName": "demo-pod",
        "status": "RUNNING",
        "region": "us-west-2",
        "gpuType": "NVIDIA-H100",
        "gpuCount": 2
    }
}


def test_get_pod_detail_success():
    client = PodApi("dummy", base_url="http://127.0.0.1:8080")

    with patch.object(client, "http_get", return_value=MOCK_DETAIL_RESPONSE) as mock_get:
        resp = client.get_pod_detail(123)
        mock_get.assert_called_once_with("/openapi/v1/pods/detail", payload={"id": 123})
        assert resp["code"] == 10000
        assert resp["data"]["id"] == 123
        assert resp["data"]["podName"] == "demo-pod"


def test_get_pod_detail_invalid_id():
    client = PodApi("dummy", base_url="http://127.0.0.1:8080")

    with pytest.raises(ValueError):
        client.get_pod_detail(0)

    with pytest.raises(ValueError):
        client.get_pod_detail(-5)


def test_get_pod_detail_http_error():
    """Test handling of HTTP 404 error when fetching pod detail"""
    client = PodApi("dummy", base_url="http://127.0.0.1:8080")

    # Patch the http_get method to simulate a 404 Not Found response
    # The ClientError constructor requires: (status_code, error_code, error_message, headers, data)
    with patch.object(client, "http_get", side_effect=ClientError(404, 40400, "Not Found", {}, None)):
        try:
            # This call should raise a ClientError due to the patched side effect
            client.get_pod_detail(999999)
            # If no exception is raised, the test should fail
            assert False, "Expected ClientError was not raised"
        except ClientError as e:
            # Print exception details for debugging purposes
            print(f"Caught ClientError: status={e.status_code}, code={e.error_code}, message={e.error_message}")

            # Assert the error properties to make sure the exception is as expected
            assert e.status_code == 404
            assert e.error_code == 40400
            assert "Not Found" in str(e.error_message)