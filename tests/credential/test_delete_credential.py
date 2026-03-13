from unittest.mock import patch

import pytest

from yottaml.error import ClientError, ParameterRequiredError
from yottaml.credential import CredentialApi


MOCK_SUCCESS_RESPONSE = {"code": 10000, "message": "success", "data": None}


@pytest.fixture
def credential_api():
    return CredentialApi(
        api_key="test_api_key", base_url="https://api.test.yottalabs.ai"
    )


def test_delete_credential_success(credential_api):
    credential_id = "384410568058921807"
    with patch.object(
        credential_api, "http_delete", return_value=MOCK_SUCCESS_RESPONSE
    ) as mock_delete:
        response = credential_api.delete_credential(credential_id=credential_id)
        assert response == MOCK_SUCCESS_RESPONSE
        mock_delete.assert_called_once_with(
            f"/v2/container-registry-auths/{credential_id}", payload=None
        )


def test_delete_credential_missing_id(credential_api):
    with pytest.raises(ParameterRequiredError):
        credential_api.delete_credential(credential_id=None)
    with pytest.raises(ParameterRequiredError):
        credential_api.delete_credential(credential_id="")


def test_delete_credential_invalid_id_type(credential_api):
    for invalid_id in ["abc", "123abc", "cred-123", -123, 0, 1.5, True]:
        with pytest.raises(ValueError):
            credential_api.delete_credential(credential_id=invalid_id)


def test_delete_credential_client_error(credential_api):
    credential_id = "384410568058921807"
    with patch.object(
        credential_api,
        "http_delete",
        side_effect=ClientError(
            200, 25002, "Credential is in use and cannot be deleted.", {}, None
        ),
    ):
        with pytest.raises(ClientError) as exc_info:
            credential_api.delete_credential(credential_id=credential_id)
        assert exc_info.value.error_code == 25002
