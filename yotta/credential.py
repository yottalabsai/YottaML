from yotta import API
from yotta.lib.utils import check_required_parameter, check_required_parameters, check_is_positive_int


class CredentialApi(API):
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    def create_credential(self, name: str, username: str, token: str):
        """Create Credential

        POST /openapi/v1/credentials/create

        Args:
            name (str): Credential name.
            username (str): Credential username.
            token (str): Credential token/secret.

        Returns:
            Json: Response containing the created credential ID.
        """
        check_required_parameters([
            [name, "name"],
            [username, "username"],
            [token, "token"],
        ])

        payload = {
            "name": name,
            "username": username,
            "token": token,
        }

        url_path = "/openapi/v1/credentials/create"
        return self.http_post(url_path, payload)

    def get_credentials(self, **kwargs):
        """Get all credentials

        GET /openapi/v1/credentials/list

        Args:
            **kwargs: Additional query parameters, will be passed directly into query string.

        Returns:
            Json: List of credentials.
        """
        payload = {**kwargs}
        url_path = "/openapi/v1/credentials/list"
        return self.http_get(url_path, payload=payload)

    def get_credential(self, credential_id: str):
        """Get a specific credential by ID

        GET /openapi/v1/credentials/{credential_id}

        Args:
            credential_id (str): ID of the credential to retrieve detail. Must be a positive integer.

        Returns:
            Json: Credential detail payload.

        Raises:
            ValueError: If credential_id is not a positive integer.
        """
        check_required_parameter(credential_id, "credential_id")
        check_is_positive_int(credential_id, "credential_id")

        url_path = f"/openapi/v1/credentials/{credential_id}"
        return self.http_get(url_path)

    def delete_credential(self, credential_id: str):
        """Delete a specific credential by ID

        DELETE /openapi/v1/credentials/{credential_id}

        Args:
            credential_id (str): ID of the credential to delete. Must be a positive integer.

        Returns:
            Json: Response indicating success or failure of deletion.

        Raises:
            ValueError: If credential_id is not a valid positive integer.
        """
        check_required_parameter(credential_id, "credential_id")
        check_is_positive_int(credential_id, "credential_id")

        url_path = f"/openapi/v1/credentials/{credential_id}"
        return self.http_delete(url_path, payload=None)


