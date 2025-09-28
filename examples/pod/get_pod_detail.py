#!/usr/bin/env python
import argparse
import logging

from examples.utils.prepare_env import get_api_key
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.pod import PodApi


def parse_args():
    parser = argparse.ArgumentParser(description="Get pod detail by ID")
    parser.add_argument("--base-url", type=str, default="http://127.0.0.1:8080",
                        help="Yotta OpenAPI base URL")
    parser.add_argument("--debug", action="store_true", help="Enable HTTP debug logs")
    parser.add_argument("--id", type=int, required=True, help="Pod ID to query")
    return parser.parse_args()


def display_detail(detail: dict):
    if not detail:
        logging.info("No pod detail returned.")
        return
    logging.info("Pod Detail:")
    for k, v in detail.items():
        logging.info("  %-24s: %s", k, v)


def main():
    config_logging(logging, logging.DEBUG)
    args = parse_args()

    api_key = get_api_key()
    client = PodApi(api_key, base_url=args.base_url, debug=args.debug)

    try:
        resp = client.get_pod_detail(args.id)
        if resp.get("code") == 10000:
            logging.info("Successfully retrieved pod detail.")
            display_detail(resp.get("data"))
        else:
            logging.warning("Unexpected response code: %s", resp.get("code"))
            logging.warning("Response message: %s", resp.get("message"))
    except ClientError as error:
        logging.error("Client error. Status: %s, Code: %s, Message: %s",
                      error.status_code, error.error_code, error.error_message)
    except Exception as error:
        logging.error("Unexpected error: %s", str(error))


if __name__ == "__main__":
    main()
