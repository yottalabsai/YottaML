#!/usr/bin/env python
import logging
import argparse

from examples.utils.prepare_env import get_api_key
from yotta.lib.utils import config_logging
from yotta.error import ClientError
from yotta.elastic import ElasticApi


def parse_args():
    p = argparse.ArgumentParser(description="List workers of an elastic deployment")
    p.add_argument("id", help="Deployment ID (positive integer)")
    p.add_argument(
        "--status",
        dest="statuses",
        action="append",
        default=[],
        help="Filter by worker status (repeatable or comma-separated), e.g. --status INITIALIZE --status RUNNING",
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


def main():
    config_logging(logging, logging.DEBUG)
    args = parse_args()

    api_key = get_api_key()
    client = ElasticApi(api_key, base_url=args.base_url, debug=args.debug)

    status_tokens = flat_split(args.statuses)
    status_list = [s.upper() for s in status_tokens] or None

    try:
        resp = client.get_workers(
            deployment_id=args.id,
            status_list=status_list,
        )
        if resp.get("code") == 10000:
            workers = resp.get("data") or []
            logging.info("Total workers: %s", len(workers))
            for w in workers:
                logging.info(
                    "id=%s region=%s gpuType=%s gpuCount=%s status=%s",
                    w.get("id"),
                    w.get("region"),
                    w.get("gpuType"),
                    w.get("gpuCount"),
                    w.get("status"),
                )
        else:
            logging.warning("Unexpected code=%s message=%s", resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("ClientError: status=%s code=%s message=%s", e.status_code, e.error_code, e.error_message)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()


