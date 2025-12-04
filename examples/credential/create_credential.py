#!/usr/bin/env python

import logging

from examples.utils.prepare_env import get_api_key
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.credential import CredentialApi


def main():
    # Configure logging to show debug information
    config_logging(logging, logging.DEBUG)

    # Get API key from environment
    api_key = get_api_key()

    # Initialize client with test environment
    client = CredentialApi(api_key, base_url="https://api.dev.yottalabs.ai", debug=True)

    try:
        # Example credential data
        name = "Test-Credential"
        username = "Test-Credential-username"
        token = "Test-Credential-token"

        # Create credential
        response = client.create_credential(name=name, username=username, token=token)

        if response.get("code") == 10000:
            logging.info("Successfully created credential")
            logging.info("Response message: %s", response.get("message"))
            logging.info("New Credential ID: %s", response.get("data"))
        else:
            logging.warning("Unexpected response code: %s", response.get("code"))
            logging.warning("Response message: %s", response.get("message"))

    except ClientError as error:
        logging.error(
            "Client error occurred. Status: %s, Error code: %s, Message: %s",
            error.status_code,
            error.error_code,
            error.error_message,
        )
    except Exception as error:
        logging.error("An unexpected error occurred: %s", str(error))


if __name__ == "__main__":
    main()


