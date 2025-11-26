#!/usr/bin/env python
import logging
import argparse

from examples.utils.prepare_env import get_api_key
from yotta.lib.utils import config_logging
from yotta.error import ClientError
from yotta.elastic import ElasticApi


def parse_args():
    p = argparse.ArgumentParser(description="Delete an elastic deployment")
    p.add_argument("id", help="Deployment ID (positive integer)")
    p.add_argument("--base-url", default="https://api.dev.yottalabs.ai", help="API base URL")
    p.add_argument("--debug", action="store_true", help="Enable HTTP debug logging")
    return p.parse_args()


def main():
    config_logging(logging, logging.DEBUG)
    args = parse_args()

    api_key = get_api_key()
    client = ElasticApi(api_key, base_url=args.base_url, debug=args.debug)

    try:
        resp = client.delete_deployment(args.id)
        if resp.get("code") == 10000:
            logging.info("Elastic deployment %s deleted", args.id)
        elif resp.get("code") == 24002:
            logging.warning("Elastic action not allowed for deployment %s", args.id)
            logging.warning("message=%s", resp.get("message"))
        else:
            logging.warning("Unexpected code=%s message=%s", resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("ClientError: status=%s code=%s message=%s", e.status_code, e.error_code, e.error_message)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()


