#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import argparse

from examples.utils.prepare_env import get_api_key
from yotta.error import ClientError
from yotta.lib.utils import config_logging, none_to_zero
from yotta.pod import PodApi

# --- Pod status enum (server side) ---
# 0 INITIALIZE, 1 RUNNING, 2 PAUSING, 3 PAUSED, 4 TERMINATING, 5 TERMINATED, 6 FAILED
STATUS_NAME = {
    0: "INITIALIZE",
    1: "RUNNING",
    2: "PAUSING",
    3: "PAUSED",
    4: "TERMINATING",
    5: "TERMINATED",
    6: "FAILED",
}

STATUS_ICON = {
    0: "⚪",  # initialize
    1: "🟢",  # running
    2: "🟡",  # pausing
    3: "🟠",  # paused
    4: "⏳",  # terminating
    5: "⚫",  # terminated
    6: "🔴",  # failed
}


def safe_str(s, maxlen):
    """Safely cast any value to str and clip to max length."""
    if s is None:
        return "-"
    s = str(s)
    return s[:maxlen]


def format_status(status_value):
    """Return icon + name for a numeric status."""
    try:
        sv = int(status_value)
    except Exception:
        sv = -1
    icon = STATUS_ICON.get(sv, "⚪")
    name = STATUS_NAME.get(sv, "UNKNOWN")
    return f"{icon} {name}"


def display_pod_row(pod: dict):
    """Print one row for a pod."""
    pid = pod.get("id")
    name = safe_str(pod.get("podName"), 22)
    gpu_type = safe_str(pod.get("gpuType"), 18)
    gpu_count = none_to_zero(pod.get("gpuCount"), "gpuCount")
    region = safe_str(pod.get("region"), 14)
    status = format_status(pod.get("status"))

    logging.info(
        f"{pid!s:>10} | {name:<22} | {gpu_type:<18} x{int(gpu_count):<2} | {region:<14} | {status}"
    )


def display_pods_list(pods: list[dict]):
    """Render pods as a small table and print summary."""
    if not pods:
        logging.info("No pods found.")
        return

    # Header
    logging.info("")
    logging.info("Pods List")
    logging.info("=" * 100)
    logging.info(
        f"{'ID':>10} | {'Name':<22} | {'GPU Type':<18}   {' ':<2}| {'Region':<14} | {'Status'}"
    )
    logging.info("-" * 100)

    # Sort by createdAt desc if present; fall back to id
    def _sort_key(p):
        return (p.get("createdAt") is not None, p.get("createdAt") or p.get("id") or 0)

    for pod in sorted(pods, key=_sort_key, reverse=True):
        display_pod_row(pod)

    # Summary
    logging.info("-" * 100)
    total = len(pods)
    # Server returns numeric status; treat 1 as RUNNING
    active = sum(1 for p in pods if str(p.get("status")) == "1")
    total_gpus = sum(int(none_to_zero(p.get("gpuCount"), "gpuCount")) for p in pods)
    logging.info(f"Total Pods : {total}")
    logging.info(f"Active Pods: {active}")
    logging.info(f"Total GPUs : {total_gpus}")


def parse_args():
    """CLI filters to match API: region + statusList"""
    parser = argparse.ArgumentParser(
        description="List pods with optional region/status filters."
    )
    parser.add_argument(
        "--region",
        help="Comma separated regions, e.g. sg,us-east-1",
        default=None,
        type=str,
    )
    parser.add_argument(
        "--status",
        help="Comma separated status values (0..6). e.g. 1,3",
        default=None,
        type=str,
    )
    parser.add_argument(
        "--base-url",
        help="API base url",
        default="https://api.dev.yottalabs.ai",
        type=str,
    )
    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Logging
    config_logging(logging, logging.DEBUG if args.debug else logging.INFO)

    # Auth
    api_key = get_api_key()

    # Client
    client = PodApi(api_key, base_url=args.base_url, debug=args.debug)

    # Build filters for SDK
    region_list = args.region.split(",") if args.region else None
    status_list = (
        [int(s.strip()) for s in args.status.split(",") if s.strip().isdigit()]
        if args.status
        else None
    )

    try:
        # Fetch
        resp = client.get_pods(region=region_list, status_list=status_list)

        # Basic check (platform-standard envelope)
        if resp.get("code") == 10000:
            logging.info("Successfully retrieved pods list.")
            pods = resp.get("data") or []
            display_pods_list(pods)
        else:
            logging.warning("Unexpected response code: %s", resp.get("code"))
            logging.warning("Response message: %s", resp.get("message"))

    except ClientError as e:
        logging.error(
            "Client error occurred. Status: %s, Error code: %s, Message: %s",
            getattr(e, "status_code", None),
            getattr(e, "error_code", None),
            getattr(e, "error_message", None),
        )
    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e))


if __name__ == "__main__":
    main()
