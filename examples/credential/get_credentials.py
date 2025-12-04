#!/usr/bin/env python

import logging

from examples.utils.prepare_env import get_api_key
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.credential import CredentialApi


def display_credentials_list(credentials):
    """Display credentials in a simple table"""
    if not credentials:
        logging.info("No credentials found.")
        return

    logging.info("\nCredentials List:")
    logging.info("=" * 60)
    logging.info("  ID                  | Name")
    logging.info("-" * 60)

    for cred in credentials:
        logging.info(
            f" {str(cred.get('id','')):20} | "
            f"{str(cred.get('name',''))[:30]:<30}"
        )

    logging.info("-" * 60)
    logging.info("Total Credentials: %s", len(credentials))


def main():
    config_logging(logging, logging.DEBUG)

    api_key = get_api_key()
    client = CredentialApi(api_key, base_url="https://api.dev.yottalabs.ai", debug=True)

    try:
        response = client.get_credentials()

        if response.get("code") == 10000:
            logging.info("Successfully retrieved credentials list")
            logging.info("Response message: %s", response.get("message"))
            display_credentials_list(response.get("data") or [])
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


