from unittest.mock import patch

import pytest

from yottaml.error import ClientError
from yottaml.credential import CredentialApi


MOCK_EMPTY_RESPONSE = {"code": 10000, "message": "success", "data": []}

MOCK_LIST_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": [
        {"id": "384410568058921807", "name": "Test-Credential", "type": "DOCKER_HUB"},
        {"id": "361530338086227968", "name": "official", "type": "PRIVATE"},
    ],
}


@pytest.fixture
def credential_api():
    return CredentialApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_get_credentials_empty_list(credential_api):
    with patch.object(credential_api, "http_get", return_value=MOCK_EMPTY_RESPONSE) as mock_get:
        response = credential_api.get_credentials()
        assert response == MOCK_EMPTY_RESPONSE
        mock_get.assert_called_once_with("/v2/container-registry-auths", payload={})


def test_get_credentials_list(credential_api):
    with patch.object(credential_api, "http_get", return_value=MOCK_LIST_RESPONSE) as mock_get:
        response = credential_api.get_credentials()
        assert response == MOCK_LIST_RESPONSE
        assert len(response["data"]) == 2
        assert response["data"][0]["id"] == "384410568058921807"
        mock_get.assert_called_once_with("/v2/container-registry-auths", payload={})


def test_get_credentials_with_kwargs(credential_api):
    with patch.object(credential_api, "http_get", return_value=MOCK_EMPTY_RESPONSE) as mock_get:
        kwargs = {"page": 1, "size": 10}
        response = credential_api.get_credentials(**kwargs)
        assert response == MOCK_EMPTY_RESPONSE
        mock_get.assert_called_once_with("/v2/container-registry-auths", payload=kwargs)


def test_get_credentials_client_error(credential_api):
    with patch.object(
        credential_api,
        "http_get",
        side_effect=ClientError(401, 40001, "Invalid API key", {}, None),
    ):
        with pytest.raises(ClientError) as exc_info:
            credential_api.get_credentials()
        assert exc_info.value.status_code == 401
