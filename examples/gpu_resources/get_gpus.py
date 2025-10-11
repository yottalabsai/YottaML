#!/usr/bin/env python
import json
import logging
from examples.utils.prepare_env import get_api_key
from yotta.lib.utils import config_logging
from yotta.gpu import GpuApi
from yotta.error import ClientError


def main():
    config_logging(logging, logging.INFO)
    api_key = get_api_key()
    client = GpuApi(api_key, base_url="https://api.dev.yottalabs.ai")

    # 必填参数 minSingleCardVram 与 maxSingleCardVram
    payload = {
        "regions": [],
        "minSingleCardVramInGb": 1,
        "maxSingleCardVramInGb": 300,
        "minSingleCardRamInGb": 1,
        "maxSingleCardRamInGb": 300
    }

    try:
        resp = client.get_gpus(payload)
        if resp.get("code") == 10000:
            logging.info("[GPU LIST] total: %d", len(resp.get("data", [])))
            data = resp.get("data", [])
            logging.info("[GPU LIST] total: %d", len(data))
            logging.info(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            logging.warning("[GPU LIST] unexpected code: %s %s",
                            resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("[GPU LIST] client error: %s %s", e.error_code, e.error_message)
    except Exception as e:
        logging.exception("[GPU LIST] unexpected: %s", e)


if __name__ == "__main__":
    main()
