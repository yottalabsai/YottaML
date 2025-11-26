#!/usr/bin/env python
import logging
import argparse

from examples.utils.prepare_env import get_api_key
from yotta.lib.utils import config_logging
from yotta.error import ClientError
from yotta.elastic import ElasticApi, ElasticEndpointStatusEnum


def parse_args():
    p = argparse.ArgumentParser(description="List elastic deployments with optional status filter")
    p.add_argument(
        "--status",
        dest="statuses",
        action="append",
        default=[],
        help=(
            "Filter by status (repeatable or comma-separated). "
            "Allowed: INITIALIZING,RUNNING,STOPPING,STOPPED,FAILED or alias 'active'. "
            "Example: --status RUNNING --status STOPPED  or  --status active"
        ),
    )
    p.add_argument("--base-url", default="https://api.dev.yottalabs.ai", help="API base URL")
    p.add_argument("--debug", action="store_true", help="Enable HTTP debug logging")
    return p.parse_args()


def flat_split(values):
    out = []
    for v in values or []:
        if v is None:
            continue
        parts = [s.strip() for s in str(v).split(",") if str(s).strip()]
        out.extend(parts)
    return out

def normalize_status(status_tokens):
    """
    Accept tokens like 'running', 'STOPPED', or alias 'active' (expands to INITIALIZING,RUNNING).
    Also supports giving enum names via ElasticEndpointStatusEnum.
    """
    result = []
    for t in status_tokens or []:
        val = str(t).strip()
        if not val:
            continue
        up = val.upper()
        if up == "ACTIVE":
            result.extend(ElasticEndpointStatusEnum.active())
        else:
            result.append(up)
    return result or None

def main():
    config_logging(logging, logging.DEBUG)
    args = parse_args()

    api_key = get_api_key()
    client = ElasticApi(api_key, base_url=args.base_url, debug=args.debug)

    # Support repeated --status and comma-separated forms, plus 'active' alias
    tokens = flat_split(args.statuses)
    status_list = normalize_status(tokens)

    try:
        resp = client.get_endpoints(status_list=status_list)
        if resp.get("code") == 10000:
            logging.info("Fetched deployments successfully")
            display_deployment_list(resp)
        else:
            logging.warning("Unexpected code=%s message=%s", resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("ClientError: status=%s code=%s message=%s", e.status_code, e.error_code, e.error_message)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


def display_deployment_row(item: dict) -> None:
    """
    Display a single elastic deployment in table row format.
    """
    deployment_id = str(item.get("id", ""))
    name = str(item.get("name", ""))
    status = str(item.get("status", ""))
    workers = f"{item.get('runningWorkers')}/{item.get('totalWorkers')}"

    # 这里给每一列固定宽度，后面一列对齐一列
    logging.info(
        f"{deployment_id:<20} | {name:<28} | {status:<10} | {workers:<9}"
    )


def display_deployment_list(resp: dict) -> None:
    """
    Pretty print elastic deployments in a simple table.
    """
    items = resp.get("data") or []
    if not items:
        logging.info("No elastic deployments found.")
        return

    logging.info("\nElastic Deployments:")
    logging.info("-" * 80)
    logging.info(
        f"{'id':<20} | {'name':<28} | {'status':<10} | {'workers':<9}"
    )
    logging.info("-" * 80)

    for item in items:
        display_deployment_row(item)

    logging.info("-" * 80)
    logging.info("Total: %s", len(items))


if __name__ == "__main__":
    main()
