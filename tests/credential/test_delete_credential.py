from unittest.mock import patch

import pytest

from yotta.error import ClientError, ParameterRequiredError
from yotta.credential import CredentialApi


MOCK_SUCCESS_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": None,
}

MOCK_IN_USE_RESPONSE = {
  "code": 25002,
  "message": "Credential is in use and cannot be deleted.",
  "data": [
    {
      "type": "POD",
      "id": "384409266431202134",
      "name": "Jupyter"
    }
  ]
}


@pytest.fixture
def credential_api():
    """Create a CredentialApi instance with a mock API key"""
    return CredentialApi(api_key="test_api_key", base_url="https://api.test.yottalabs.ai")


def test_delete_credential_success(credential_api):
    """Test successful credential deletion"""
    credential_id = "384410568058921807"

    with patch.object(credential_api, "http_delete", return_value=MOCK_SUCCESS_RESPONSE) as mock_delete:
        response = credential_api.delete_credential(credential_id=credential_id)

        assert response == MOCK_SUCCESS_RESPONSE
        mock_delete.assert_called_once_with(f"/openapi/v1/credentials/{credential_id}", payload=None)


def test_delete_credential_in_use(credential_api):
    """Test deleting a credential that is in use returns error payload"""
    credential_id = "384410568058921807"

    with patch.object(credential_api, "http_delete", return_value=MOCK_IN_USE_RESPONSE) as mock_delete:
        response = credential_api.delete_credential(credential_id=credential_id)

        assert response == MOCK_IN_USE_RESPONSE
        mock_delete.assert_called_once_with(f"/openapi/v1/credentials/{credential_id}", payload=None)


def test_delete_credential_missing_id(credential_api):
    """Test that deleting a credential without an ID raises an error"""
    with pytest.raises(ParameterRequiredError):
        credential_api.delete_credential(credential_id=None)

    with pytest.raises(ParameterRequiredError):
        credential_api.delete_credential(credential_id="")


def test_delete_credential_invalid_id_type(credential_api):
    """Test that deleting a credential with invalid ID type raises an error"""
    invalid_ids = [
        "abc",
        "123abc",
        "cred-123",
        -123,
        0,
        1.5,
        True,
    ]

    for invalid_id in invalid_ids:
        with pytest.raises(ValueError):
            credential_api.delete_credential(credential_id=invalid_id)


def test_delete_credential_client_error(credential_api):
    """Test handling of client error during deletion"""
    credential_id = "384410568058921807"

    with patch.object(
        credential_api,
        "http_delete",
        side_effect=ClientError(
            status_code=200,
            error_code=25002,
            error_message="Credential is in use and cannot be deleted.",
            header={},
            error_data=None,
        ),
    ):
        with pytest.raises(ClientError) as exc_info:
            credential_api.delete_credential(credential_id=credential_id)

        assert exc_info.value.status_code == 200
        assert exc_info.value.error_code == 25002
        assert "Credential is in use and cannot be deleted." in str(exc_info.value.error_message)


