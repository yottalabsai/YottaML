from yottaml import API
from yottaml.lib.utils import (
    check_required_parameter,
    check_required_parameters,
    check_is_positive_int,
)


class CredentialApi(API):
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    def create_credential(self, name: str, type: str, username: str, password: str):
        """Create Credential

        POST /v2/container-registry-auths

        Args:
            name (str): Credential name.
            type (str): Registry type. One of DOCKER_HUB, GCR, ECR, ACR, PRIVATE.
            username (str): Registry username.
            password (str): Registry password or token.

        Returns:
            Json: Response containing the created credential.
        """
        check_required_parameters(
            [
                [name, "name"],
                [type, "type"],
                [username, "username"],
                [password, "password"],
            ]
        )

        payload = {
            "name": name,
            "type": type,
            "username": username,
            "password": password,
        }

        return self.http_post("/v2/container-registry-auths", payload)

    def get_credentials(self, **kwargs):
        """Get all credentials

        GET /v2/container-registry-auths

        Args:
            **kwargs: Additional query parameters, will be passed directly into query string.

        Returns:
            Json: List of credentials.
        """
        payload = {**kwargs}
        return self.http_get("/v2/container-registry-auths", payload=payload)

    def get_credential(self, credential_id: str):
        """Get a specific credential by ID

        GET /v2/container-registry-auths/{id}

        Args:
            credential_id (str): ID of the credential to retrieve. Must be a positive integer.

        Returns:
            Json: Credential detail payload.

        Raises:
            ValueError: If credential_id is not a positive integer.
        """
        check_required_parameter(credential_id, "credential_id")
        check_is_positive_int(credential_id, "credential_id")

        return self.http_get(f"/v2/container-registry-auths/{credential_id}")

    def update_credential(self, credential_id: str, **kwargs):
        """Update a specific credential by ID (partial update)

        PATCH /v2/container-registry-auths/{id}

        Args:
            credential_id (str): ID of the credential to update. Must be a positive integer.
            **kwargs: Fields to update (name, username, password).

        Returns:
            Json: Updated credential payload.

        Raises:
            ValueError: If credential_id is not a positive integer.
        """
        check_required_parameter(credential_id, "credential_id")
        check_is_positive_int(credential_id, "credential_id")

        return self.http_patch(
            f"/v2/container-registry-auths/{credential_id}", payload=kwargs
        )

    def delete_credential(self, credential_id: str):
        """Delete a specific credential by ID

        DELETE /v2/container-registry-auths/{id}

        Args:
            credential_id (str): ID of the credential to delete. Must be a positive integer.

        Returns:
            Json: Response indicating success or failure of deletion.

        Raises:
            ValueError: If credential_id is not a valid positive integer.
        """
        check_required_parameter(credential_id, "credential_id")
        check_is_positive_int(credential_id, "credential_id")

        return self.http_delete(
            f"/v2/container-registry-auths/{credential_id}", payload=None
        )
