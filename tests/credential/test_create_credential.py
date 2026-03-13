from unittest.mock import patch

import pytest

from yottaml.error import ClientError, ParameterRequiredError
from yottaml.credential import CredentialApi


MOCK_SUCCESS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": {"id": 123, "name": "my-docker-registry", "type": "DOCKER_HUB"},
}


@pytest.fixture
def credential_api():
    return CredentialApi(
        api_key="test_api_key", base_url="https://api.test.yottalabs.ai"
    )


def test_create_credential_success(credential_api):
    with patch.object(
        credential_api, "http_post", return_value=MOCK_SUCCESS_RESPONSE
    ) as mock_post:
        response = credential_api.create_credential(
            name="Test-Credential",
            type="DOCKER_HUB",
            username="Test-Credential-username",
            password="Test-Credential-password",
        )

        assert response == MOCK_SUCCESS_RESPONSE
        mock_post.assert_called_once_with(
            "/v2/container-registry-auths",
            {
                "name": "Test-Credential",
                "type": "DOCKER_HUB",
                "username": "Test-Credential-username",
                "password": "Test-Credential-password",
            },
        )


def test_create_credential_missing_parameters(credential_api):
    with pytest.raises(ParameterRequiredError):
        credential_api.create_credential(
            name=None, type="DOCKER_HUB", username="user", password="pass"
        )
    with pytest.raises(ParameterRequiredError):
        credential_api.create_credential(
            name="name", type=None, username="user", password="pass"
        )
    with pytest.raises(ParameterRequiredError):
        credential_api.create_credential(
            name="name", type="DOCKER_HUB", username=None, password="pass"
        )
    with pytest.raises(ParameterRequiredError):
        credential_api.create_credential(
            name="name", type="DOCKER_HUB", username="user", password=None
        )


def test_create_credential_client_error(credential_api):
    with patch.object(
        credential_api,
        "http_post",
        side_effect=ClientError(400, 20001, "Create credential failed", {}, None),
    ):
        with pytest.raises(ClientError) as exc_info:
            credential_api.create_credential(
                name="Test-Credential",
                type="DOCKER_HUB",
                username="user",
                password="pass",
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == 20001
        assert "Create credential failed" in str(exc_info.value.error_message)
