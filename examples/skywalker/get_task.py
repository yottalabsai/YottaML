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
    Parse CLI arguments for fetching a single task detail.
    """
    parser = argparse.ArgumentParser(
        description="Get Skywalker task detail by userTaskId or internal task id"
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("YOTTA_BASE_URL", "https://api.dev.yottalabs.ai"),
        help="API base URL (default: https://api.dev.yottalabs.ai)",
    )
    parser.add_argument(
        "--task-id",
        default=os.getenv("YOTTA_TASK_ID", "task_20251111_001"),
        help="Task ID (userTaskId or internal id), default from env YOTTA_TASK_ID",
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

    logging.info("Querying task detail...")
    logging.info("Base URL    : %s", base_url)
    logging.info("Endpoint ID : %s", endpoint_id)
    logging.info("Task ID     : %s", args.task_id)

    api = SkywalkerTaskApi(api_key=api_key, base_url=base_url, debug=args.debug)

    try:
        resp = api.get_task(
            endpoint_id=endpoint_id,
            task_id=args.task_id,
        )
        logging.info("Request finished. Raw response:")
        print(json.dumps(resp, indent=2, ensure_ascii=False))

        data = resp.get("data") or {}
        logging.info("Task status     : %s", data.get("status"))
        logging.info("Worker URL      : %s", data.get("workerUrl"))
        logging.info("Notify URL      : %s", data.get("notifyUrl"))
        logging.info("Result send stat: %s", data.get("resultSendStatus"))
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
