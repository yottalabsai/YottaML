from unittest.mock import patch

import pytest

from yotta.error import ClientError, ParameterRequiredError
from yotta.credential import CredentialApi


MOCK_SUCCESS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": "384401988287099196",
}

MOCK_ERROR_RESPONSE = {
    "code": 20001,
    "message": "Create credential failed",
    "data": None,
}


@pytest.fixture
def credential_api():
    """Create a CredentialApi instance with a mock API key"""
    return CredentialApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_create_credential_success(credential_api):
    """Test successful credential creation"""
    with patch.object(credential_api, "http_post", return_value=MOCK_SUCCESS_RESPONSE) as mock_post:
        response = credential_api.create_credential(
            name="Test-Credential",
            username="Test-Credential-username",
            token="Test-Credential-token",
        )

        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once_with(
            "/openapi/v1/credentials/create",
            {
                "name": "Test-Credential",
                "username": "Test-Credential-username",
                "token": "Test-Credential-token",
            },
        )


def test_create_credential_missing_parameters(credential_api):
    """Test missing required parameters raise ParameterRequiredError"""
    with pytest.raises(ParameterRequiredError):
        credential_api.create_credential(name=None, username="user", token="token")

    with pytest.raises(ParameterRequiredError):
        credential_api.create_credential(name="name", username=None, token="token")

    with pytest.raises(ParameterRequiredError):
        credential_api.create_credential(name="name", username="user", token=None)


def test_create_credential_client_error(credential_api):
    """Test handling of client error during creation"""
    with patch.object(
        credential_api,
        "http_post",
        side_effect=ClientError(
            status_code=400,
            error_code=20001,
            error_message="Create credential failed",
            header={},
            error_data=None,
        ),
    ):
        with pytest.raises(ClientError) as exc_info:
            credential_api.create_credential(
                name="Test-Credential",
                username="Test-Credential-username",
                token="Test-Credential-token",
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == 20001
        assert "Create credential failed" in str(exc_info.value.error_message)


