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
        credential_id = "384499613536751775"

        response = client.delete_credential(credential_id)

        if response.get("code") == 10000:
            logging.info("Successfully deleted credential %s", credential_id)
            logging.info("Response message: %s", response.get("message"))
        elif response.get("code") == 25002:
            logging.warning("Credential %s is in use and cannot be deleted.", credential_id)
            logging.warning("Response message: %s", response.get("message"))
            data = response.get("data") or {}
            pod_list = data.get("podList") or []
            elastic_list = data.get("elasticList") or []
            logging.warning("Pods using this credential: %s", pod_list)
            logging.warning("Elastic deployments using this credential: %s", elastic_list)
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


