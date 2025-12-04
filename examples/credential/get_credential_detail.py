#!/usr/bin/env python

import logging

from examples.utils.prepare_env import get_api_key
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.credential import CredentialApi


def main():
    config_logging(logging, logging.DEBUG)

    api_key = get_api_key()
    client = CredentialApi(api_key, base_url="https://api.dev.yottalabs.ai", debug=True)

    try:
        # Example credential ID - replace with your actual credential ID
        credential_id = "384410568058921807"

        response = client.get_credential(credential_id)

        if response.get("code") == 10000:
            logging.info("Successfully retrieved credential %s detail", credential_id)
            logging.info("Response message: %s", response.get("message"))

            detail = response.get("data") or {}
            for k, v in detail.items():
                logging.info("%-20s: %s", k, v)
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


