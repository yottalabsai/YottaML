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

    # Support repeated --status and comma-separated forms, plus 'active' alias
    status_list = ["INITIALIZING", "RUNNING", "STOPPING", "STOPPED", "FAILED"]

    try:
        resp = client.get_deployments(status_list=status_list)
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
