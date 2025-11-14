#!/usr/bin/env python
import os
import json
import time
import logging
import argparse

from examples.utils.prepare_env import get_api_key, get_endpoint_id
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.skywalker import SkywalkerTaskApi


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments for creating a Skywalker task.
    """
    parser = argparse.ArgumentParser(
        description="Create a Skywalker task and submit it to elastic queue"
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("YOTTA_BASE_URL", "https://api.dev.yottalabs.ai"),
        help="API base URL (default: https://api.dev.yottalabs.ai)",
    )
    parser.add_argument(
        "--user-task-id",
        default=f"task_{int(time.time())}",
        help="Custom userTaskId (default: task_<timestamp>)",
    )
    parser.add_argument(
        "--model",
        default="meta-llama/Llama-3.2-3B-Instruct",
        help="Model name in taskData (default: meta-llama/Llama-3.2-3B-Instruct)",
    )
    parser.add_argument(
        "--notify-url",
        default="http://your-callback-url/notify",
        help="Callback URL when task is finished",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable HTTP debug logging",
    )
    return parser.parse_args()


def build_sample_payload(model: str) -> dict:
    """
    Build a sample OpenAI-like chat completion payload.
    """
    return {
        "temperature": 0.5,
        "top_p": 0.9,
        "max_tokens": 256,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.2,
        "repetition_penalty": 1.2,
        "model": model,
        "messages": [
            {"role": "assistant", "content": "what can i help you?"},
            {"role": "user", "content": "Hello"},
        ],
        "stream": False,
    }


def pretty_print_resp(resp: dict) -> None:
    """
    Pretty print JSON response to stdout.
    """
    print(json.dumps(resp, indent=2, ensure_ascii=False))


def main():
    # basic logging
    args = parse_args()
    config_logging(logging, logging.DEBUG if args.debug else logging.INFO)

    api_key = get_api_key()
    endpoint_id = get_endpoint_id()
    base_url = args.base_url

    logging.info("Creating Skywalker task...")
    logging.info("Base URL     : %s", base_url)
    logging.info("Endpoint ID  : %s", endpoint_id)
    logging.info("User Task ID : %s", args.user_task_id)

    api = SkywalkerTaskApi(api_key=api_key, base_url=base_url, debug=args.debug)

    payload = build_sample_payload(args.model)

    try:
        resp = api.create_task(
            endpoint_id=endpoint_id,
            user_task_id=args.user_task_id,
            worker_port=8000,
            process_uri="/v1/chat/completions",
            notify_url=args.notify_url,
            notify_auth_key="key",
            task_data=payload,
            header={
                "Authorization": "Bearer your-worker-token",
                "X-Custom-Header": "custom-value",
                "X-Request-ID": "test-request-123",
            },
        )
        logging.info("Task created successfully.")
        pretty_print_resp(resp)
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
