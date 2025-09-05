from unittest.mock import patch

import pytest

from yotta.error import ClientError, ParameterRequiredError
from yotta.pod import PodApi

# Mock response data
MOCK_SUCCESS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": True
}

@pytest.fixture
def pod_api():
    """Create a PodApi instance with a mock API key"""
    return PodApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_resume_pod_success(pod_api):
    """Test successful pod resume"""
    pod_id = 123456789

    with patch.object(pod_api, 'http_post', return_value=MOCK_SUCCESS_RESPONSE) as mock_post:
        response = pod_api.resume_pod(pod_id=pod_id)

        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once_with(f"/openapi/v1/pods/resume/{pod_id}", payload=None)


def test_resume_pod_success_with_string_id(pod_api):
    """Test successful pod resume with string ID that can be converted to int"""
    pod_id = "123456789"

    with patch.object(pod_api, 'http_post', return_value=MOCK_SUCCESS_RESPONSE) as mock_post:
        response = pod_api.resume_pod(pod_id=pod_id)

        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once_with(f"/openapi/v1/pods/resume/{int(pod_id)}", payload=None)


def test_resume_pod_missing_id(pod_api):
    """Test that resuming a pod without an ID raises an error"""
    with pytest.raises(ParameterRequiredError) as exc_info:
        pod_api.resume_pod(pod_id=None)
    assert "pod_id" in str(exc_info.value)

    with pytest.raises(ParameterRequiredError) as exc_info:
        pod_api.resume_pod(pod_id="")
    assert "pod_id" in str(exc_info.value)


def test_resume_pod_invalid_id_type(pod_api):
    """Test that resuming a pod with invalid ID type raises an error"""
    invalid_ids_valueerror = [
        "abc", "123abc", "pod-123", -123, 0, 1.5, True
    ]
    for invalid_id in invalid_ids_valueerror:
        with pytest.raises(ValueError) as exc_info:
            pod_api.resume_pod(pod_id=invalid_id)
        assert "pod_id" in str(exc_info.value)

    for invalid_id in [[], {}]:
        with pytest.raises(ParameterRequiredError) as exc_info:
            pod_api.resume_pod(pod_id=invalid_id)
        assert "pod_id" in str(exc_info.value)


def test_resume_pod_not_found(pod_api):
    """Test handling of pod not found error on resume"""
    pod_id = 999999999

    with patch.object(pod_api, 'http_post', side_effect=ClientError(
        status_code=200,
        error_code=12000,
        error_message="Pod not exist",
        header={},
        error_data=None
    )):
        with pytest.raises(ClientError) as exc_info:
            pod_api.resume_pod(pod_id=pod_id)

        assert exc_info.value.status_code == 200
        assert exc_info.value.error_code == 12000
        assert "Pod not exist" in str(exc_info.value.error_message)


def test_resume_pod_unauthorized(pod_api):
    """Test handling of unauthorized resume attempt"""
    pod_id = 123456789

    with patch.object(pod_api, 'http_post', side_effect=ClientError(
        status_code=200,
        error_code=10004,
        error_message="no permissions",
        header={},
        error_data=None
    )):
        with pytest.raises(ClientError) as exc_info:
            pod_api.resume_pod(pod_id=pod_id)

        assert exc_info.value.status_code == 200
        assert exc_info.value.error_code == 10004
        assert "no permissions" in str(exc_info.value.error_message)


def test_resume_pod_server_error(pod_api):
    """Test handling of server errors during resume"""
    pod_id = 123456789

    with patch.object(pod_api, 'http_post', side_effect=Exception("Internal server error")):
        with pytest.raises(Exception) as exc_info:
            pod_api.resume_pod(pod_id=pod_id)

        assert "Internal server error" in str(exc_info.value)
