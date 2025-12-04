#!/usr/bin/env python
import argparse
import json
import logging
import os

from examples.utils.prepare_env import get_api_key, get_endpoint_id
from yotta.error import ClientError
from yotta.lib.utils import config_logging
from yotta.skywalker import SkywalkerTaskApi, TaskStatus


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments for listing tasks with pagination.
    """
    parser = argparse.ArgumentParser(
        description="List Skywalker tasks for an endpoint with optional status filter"
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("YOTTA_BASE_URL", "https://api.dev.yottalabs.ai"),
        help="API base URL (default: https://api.dev.yottalabs.ai)",
    )
    parser.add_argument(
        "--status",
        default=None,
        help=(
            "Task status filter: 0,1,2,3 or name "
            "(PROCESSING,DELIVERED,SUCCESS,FAILED). Default: all"
        ),
    )
    parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page number (default: 1)",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=5,
        help="Page size (default: 5)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable HTTP debug logging",
    )
    return parser.parse_args()


def parse_status_arg(status_arg: str = None):
    """
    Parse --status argument into TaskStatus or int or None.
    Accepts:
      - None               -> None
      - '0','1','2','3'    -> int
      - 'processing' ...   -> TaskStatus enum
    """
    if status_arg is None:
        return None

    s = status_arg.strip()
    if not s:
        return None

    # numeric form
    if s.isdigit():
        return int(s)

    # enum name form
    try:
        return TaskStatus[s.upper()]
    except KeyError:
        raise SystemExit(
            "Invalid --status value. Use 0..3 or one of: "
            "PROCESSING, DELIVERED, SUCCESS, FAILED"
        )


def display_task_row(item: dict) -> None:
    """
    Display a single task row in short table format.
    """
    user_task_id = str(item.get("userTaskId", ""))[:30]
    status = str(item.get("status", ""))
    created_at = str(item.get("createdAt", ""))
    notify_url = str(item.get("notifyUrl", ""))

    logging.info(
        f"{user_task_id:<32} | {status:<10} | {created_at:<23} | {notify_url}"
    )


def display_task_list(resp: dict) -> None:
    """
    Pretty print items + simple table + pagination.
    """
    data = resp.get("data") or {}
    items = data.get("items") or []
    pagination = data.get("pagination") or {}

    if not items:
        logging.info("No tasks found.")
        return

    logging.info("\nTasks:")
    logging.info("-" * 120)
    logging.info(
        f"{'userTaskId':<32} | {'status':<10} | {'createdAt':<23} | {'notifyUrl'}"
    )
    logging.info("-" * 120)

    for item in items:
        display_task_row(item)

    logging.info("-" * 120)
    logging.info(
        "Page: %s / %s, PageSize: %s, Total: %s",
        pagination.get("page"),
        pagination.get("totalPages"),
        pagination.get("pageSize"),
        pagination.get("totalCount"),
    )


def main():
    args = parse_args()
    config_logging(logging, logging.DEBUG if args.debug else logging.INFO)

    api_key = get_api_key()
    endpoint_id = get_endpoint_id()
    base_url = args.base_url

    status_filter = parse_status_arg(args.status)

    logging.info("Listing tasks...")
    logging.info("Base URL    : %s", base_url)
    logging.info("Endpoint ID : %s", endpoint_id)
    logging.info("Status      : %s", status_filter)
    logging.info("Page        : %s", args.page)
    logging.info("PageSize    : %s", args.page_size)

    api = SkywalkerTaskApi(api_key=api_key, base_url=base_url, debug=args.debug)

    try:
        resp = api.list_tasks(
            endpoint_id=endpoint_id,
            status=status_filter,
            page=args.page,
            page_size=args.page_size,
        )

        logging.info("Request finished. Raw response:")
        print(json.dumps(resp, indent=2, ensure_ascii=False))

        display_task_list(resp)
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
