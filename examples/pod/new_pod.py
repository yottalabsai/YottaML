#!/usr/bin/env python

import logging

from examples.utils.prepare_env import get_api_key
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.pod import PodApi


def create_sample_pod(client, config):
    """Create a pod with the given configuration

    Args:
        client: The API client instance
        config (dict): Pod configuration dictionary
    """
    try:
        # Create the pod
        response = client.new_pod(**config)

        # Check response
        if response['code'] == 10000:
            logging.info(f"Successfully created pod")
            logging.info(f"Response message: {response['message']}")
            logging.info(f"New Pod ID: {response['data']}")
            return response['data']
        else:
            logging.warning(f"Unexpected response code: {response['code']}")
            logging.warning(f"Response message: {response['message']}")
            return None

    except ClientError as error:
        # Handle client-side errors (4XX status codes)
        logging.error(
            "Client error occurred. Status: %s, Error code: %s, Message: %s",
            error.status_code, error.error_code, error.error_message
        )
        return None
    except Exception as error:
        # Handle other unexpected errors
        logging.error("An unexpected error occurred: %s", str(error))
        return None


def main():
    # Configure logging to show debug information
    config_logging(logging, logging.DEBUG)

    # Get API key from environment
    api_key = get_api_key()

    # Initialize client with test environment
    client = PodApi(api_key, base_url="https://api.dev.yottalabs.ai")

    # Example 1: Basic GPU Pod with SSH
    basic_config = {
        "image": "yottalabsai/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04-2025050802",
        "gpu_type": "NVIDIA_L4_24G",
        "pod_name": "Test_from_SDK",
        "gpu_count": 1,
        "expose": [
            {
                "port": 22,
                "protocol": "SSH"
            }
        ]
    }

    logging.info("\nCreating basic GPU pod with SSH...")
    basic_pod_id = create_sample_pod(client, basic_config)

    # Print summary of created pods
    logging.info("\nSummary of Created Pods:")
    logging.info("=" * 50)
    if basic_pod_id:
        logging.info(f"Basic GPU Pod ID: {basic_pod_id}")


if __name__ == "__main__":
    main()
