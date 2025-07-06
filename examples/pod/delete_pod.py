#!/usr/bin/env python

import logging

from examples.utils.prepare_env import get_api_key
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.pod import PodApi


def main():
    # Configure logging to show debug information
    config_logging(logging, logging.DEBUG)

    # Get API key from environment
    api_key = get_api_key()

    # Initialize client with test environment
    client = PodApi(api_key, base_url="https://api.dev.yottalabs.ai")

    try:
        # Example pod ID to delete - replace with your actual pod ID
        pod_id = 331864222263676928

        # Delete the pod
        response = client.delete_pod(pod_id=pod_id)

        # Check response
        if response['code'] == 10000:
            logging.info(f"Successfully deleted pod {pod_id}")
            logging.info(f"Response message: {response['message']}")
        else:
            logging.warning(f"Unexpected response code: {response['code']}")
            logging.warning(f"Response message: {response['message']}")

    except ClientError as error:
        # Handle client-side errors (4XX status codes)
        logging.error(
            "Client error occurred. Status: %s, Error code: %s, Message: %s",
            error.status_code, error.error_code, error.error_message
        )
    except Exception as error:
        # Handle other unexpected errors
        logging.error("An unexpected error occurred: %s", str(error))


if __name__ == "__main__":
    main()
