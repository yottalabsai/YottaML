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
            for item in resp.get("data") or []:
                logging.info(
                    f"{item.get('id')} | {item.get('name')} | "
                    f"status={item.get('status')} | workers={item.get('runningWorkers')}/{item.get('totalWorkers')}"
                )
        else:
            logging.warning("Unexpected code=%s message=%s", resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("ClientError: status=%s code=%s message=%s", e.status_code, e.error_code, e.error_message)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
