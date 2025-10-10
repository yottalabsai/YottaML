#!/usr/bin/env python
import logging
from examples.utils.prepare_env import get_api_key
from yotta.lib.utils import config_logging
from yotta.gpu_resource import GpuResourceApi
from yotta.error import ClientError


def main():
    config_logging(logging, logging.INFO)
    api_key = get_api_key()
    client = GpuResourceApi(api_key, base_url="https://api.dev.yottalabs.ai")

    # 必填参数 minSingleCardVram 与 maxSingleCardVram
    payload = {
        "region": "us-east-1",
        "page": 1,
        "size": 5,
        "sortBy": "price",
        "sortOrder": "asc",
        "minSingleCardVramInGb": 0,
        "maxSingleCardVramInGb": 1536
    }

    try:
        resp = client.get_gpus(payload)
        if resp.get("code") == 10000:
            logging.info("[GPU LIST] total: %d", len(resp.get("data", [])))
            for item in resp.get("data", []):
                gpu_type = item.get("gpuType", "Unknown")
                memory = item.get("memory") or 0  # 避免 None
                price = item.get("price") or "N/A"  # 避免 None
                logging.info(" - %-15s %4dGB  $%s/hr", gpu_type, memory, price)
        else:
            logging.warning("[GPU LIST] unexpected code: %s %s",
                            resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("[GPU LIST] client error: %s %s", e.error_code, e.error_message)
    except Exception as e:
        logging.exception("[GPU LIST] unexpected: %s", e)


if __name__ == "__main__":
    main()
