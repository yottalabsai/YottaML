#!/usr/bin/env python
import logging

from examples.utils.prepare_env import get_api_key
from yotta.elastic import ElasticApi
from yotta.error import ClientError
from yotta.lib.utils import config_logging


def main():
    config_logging(logging, logging.DEBUG)

    api_key = get_api_key()
    client = ElasticApi(api_key, base_url="https://api.dev.yottalabs.ai", debug=True)

    try:
        # Example pod ID to retrieve - replace with your actual pod ID
        deployment_id = 384425425995034706

        resp = client.start_deployment(deployment_id)
        if resp.get("code") == 10000:
            logging.info("Elastic deployment %s started", deployment_id)
        else:
            logging.warning("Unexpected code=%s message=%s", resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("ClientError: status=%s code=%s message=%s", e.status_code, e.error_code, e.error_message)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
