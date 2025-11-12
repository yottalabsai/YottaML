#!/usr/bin/env python
import logging
import argparse

from examples.utils.prepare_env import get_api_key
from yotta.lib.utils import config_logging
from yotta.error import ClientError
from yotta.elastic import ElasticApi


def main():
    config_logging(logging, logging.DEBUG)

    parser = argparse.ArgumentParser(description="Scale elastic deployment workers")
    parser.add_argument("id", help="Deployment ID (positive integer)")
    parser.add_argument("workers", type=int, help="Target workers (>= 0)")
    parser.add_argument("--base-url", default="https://api.dev.yottalabs.ai", help="API base URL")
    parser.add_argument("--debug", action="store_true", help="Enable HTTP debug logging")
    args = parser.parse_args()

    api_key = get_api_key()
    client = ElasticApi(api_key, base_url=args.base_url, debug=args.debug)

    try:
        resp = client.scale_workers(args.id, args.workers)
        if resp.get("code") == 10000:
            logging.info("Scale request accepted")
        else:
            logging.warning("Unexpected code=%s message=%s", resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("ClientError: status=%s code=%s message=%s", e.status_code, e.error_code, e.error_message)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
