from unittest.mock import patch

import pytest

from yotta.error import ClientError
from yotta.credential import CredentialApi


MOCK_DETAIL_RESPONSE = {
    "code": 10000,
    "message": "success",
    "data": {
        "id": "384403563726401853",
        "name": "Test-Credential",
    },
}


def test_get_credential_detail_success():
    client = CredentialApi("dummy", base_url="http://127.0.0.1:8080")

    with patch.object(client, "http_get", return_value=MOCK_DETAIL_RESPONSE) as mock_get:
        resp = client.get_credential("384403563726401853")
        mock_get.assert_called_once_with("/openapi/v1/credentials/384403563726401853")
        assert resp["code"] == 10000
        assert resp["data"]["id"] == "384403563726401853"
        assert resp["data"]["name"] == "Test-Credential"


def test_get_credential_detail_invalid_id():
    client = CredentialApi("dummy", base_url="http://127.0.0.1:8080")

    with pytest.raises(ValueError):
        client.get_credential(0)

    with pytest.raises(ValueError):
        client.get_credential(-5)


def test_get_credential_detail_http_error():
    """Test handling of HTTP error when fetching credential detail"""
    client = CredentialApi("dummy", base_url="http://127.0.0.1:8080")

    with patch.object(client, "http_get", side_effect=ClientError(404, 40400, "Not Found", {}, None)):
        with pytest.raises(ClientError) as exc_info:
            client.get_credential("999999")

        assert exc_info.value.status_code == 404
        assert exc_info.value.error_code == 40400
        assert "Not Found" in str(exc_info.value.error_message)


