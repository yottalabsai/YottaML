#!/usr/bin/env python
import os
import json
import logging
import argparse

from examples.utils.prepare_env import get_api_key, get_endpoint_id
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.skywalker import SkywalkerTaskApi


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments for querying processing task count.
    """
    parser = argparse.ArgumentParser(
        description="Get processing (queued + running) task count for an endpoint"
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("YOTTA_BASE_URL", "https://api.dev.yottalabs.ai"),
        help="API base URL (default: https://api.dev.yottalabs.ai)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable HTTP debug logging",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config_logging(logging, logging.DEBUG if args.debug else logging.INFO)

    api_key = get_api_key()
    endpoint_id = get_endpoint_id()
    base_url = args.base_url

    logging.info("Querying processing task count...")
    logging.info("Base URL    : %s", base_url)
    logging.info("Endpoint ID : %s", endpoint_id)

    api = SkywalkerTaskApi(api_key=api_key, base_url=base_url, debug=args.debug)

    try:
        resp = api.get_processing_count(endpoint_id=endpoint_id)
        logging.info("Request finished. Raw response:")
        print(json.dumps(resp, indent=2, ensure_ascii=False))

        data = resp.get("data") or {}
        count = data.get("processingCount")
        logging.info("Processing task count: %s", count)
    except ClientError as error:
        logging.error(
            "Client error occurred. Status: %s, Error code: %s, Message: %s",
            error.status_code,
            error.error_code,
            error.error_message,
        )
    except Exception as error:
        logging.error("Unexpected error occurred: %s", str(error))


if __name__ == "__main__":
    main()
