from unittest.mock import patch

import pytest

from yotta.error import ClientError
from yotta.credential import CredentialApi


MOCK_EMPTY_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": [],
}

MOCK_LIST_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": [
        {
            "id": "384410568058921807",
            "name": "Test-Credential",
        },
        {
            "id": "361530338086227968",
            "name": "official",
        },
    ],
}


@pytest.fixture
def credential_api():
    """Create a CredentialApi instance with a mock API key"""
    return CredentialApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_get_credentials_empty_list(credential_api):
    """Test getting an empty credential list"""
    with patch.object(credential_api, "http_get", return_value=MOCK_EMPTY_RESPONSE) as mock_get:
        response = credential_api.get_credentials()

        assert response == MOCK_EMPTY_RESPONSE
        mock_get.assert_called_once_with("/openapi/v1/credentials/list", payload={})


def test_get_credentials_list(credential_api):
    """Test getting credential list"""
    with patch.object(credential_api, "http_get", return_value=MOCK_LIST_RESPONSE) as mock_get:
        response = credential_api.get_credentials()

        assert response == MOCK_LIST_RESPONSE
        assert len(response["data"]) == 2
        assert response["data"][0]["id"] == "384410568058921807"
        assert response["data"][0]["name"] == "Test-Credential"
        assert response["data"][1]["id"] == "361530338086227968"
        assert response["data"][1]["name"] == "official"
        mock_get.assert_called_once_with("/openapi/v1/credentials/list", payload={})


def test_get_credentials_with_kwargs(credential_api):
    """Test getting credentials with additional query parameters"""
    with patch.object(credential_api, "http_get", return_value=MOCK_EMPTY_RESPONSE) as mock_get:
        kwargs = {"page": 1, "size": 10}
        response = credential_api.get_credentials(**kwargs)

        assert response == MOCK_EMPTY_RESPONSE
        mock_get.assert_called_once_with("/openapi/v1/credentials/list", payload=kwargs)


def test_get_credentials_client_error(credential_api):
    """Test handling client error when listing credentials"""
    with patch.object(
        credential_api,
        "http_get",
        side_effect=ClientError(
            status_code=401,
            error_code=40001,
            error_message="Invalid API key",
            header={},
            error_data=None,
        ),
    ):
        with pytest.raises(ClientError) as exc_info:
            credential_api.get_credentials()

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == 40001
        assert "Invalid API key" in str(exc_info.value.error_message)


