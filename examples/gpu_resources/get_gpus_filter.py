#!/usr/bin/env python
import logging
from examples.utils.prepare_env import get_api_key
from yotta.lib.utils import config_logging
from yotta.gpu_resource import GpuResourceApi
from yotta.error import ClientError

def pick(d, *keys, default=None):
    """从字典 d 中按顺序取第一个存在且非 None 的键"""
    for k in keys:
        if d is not None and d.get(k) is not None:
            return d.get(k)
    return default

def main():
    config_logging(logging, logging.DEBUG)
    api_key = get_api_key()
    client = GpuResourceApi(api_key, base_url="https://api.dev.yottalabs.ai")

    payload = {
        "region": "us-east-1",
        "gpuBrand": "NVIDIA",
        "gpuType": "RTX_4090_24G",
        "gpuCount": 1,
        "minMemory": 24,
        "maxMemory": 80
    }

    try:
        resp = client.get_gpus_filter(payload)
    except ClientError as e:
        logging.error("[GPU TYPE FILTER] client error: %s %s", e.error_code, e.error_message)
        return

    code = resp.get("code")
    data = resp.get("data")

    if code != 10000:
        logging.warning("[GPU TYPE FILTER] code=%s msg=%s", code, resp.get("message"))
        return

    if not data:
        logging.info("[GPU TYPE FILTER] 没有匹配到符合条件的 GPU（data 为空）")
        return

    # 字段回退：兼容不同命名
    gpu_type = pick(data, "gpuType", "type", "gpu_type", default="Unknown")
    memory   = pick(data, "memory", "memoryInGb", "vram", default=0)
    price    = pick(data, "unitPrice", "pricePerHour", "price", default="N/A")

    # 统一打印
    try:
        logging.info("[GPU TYPE FILTER] 推荐型号: %s (%sGB), price=%s/hr", gpu_type, memory, price)
    except Exception:
        # 万一依旧出现非预期类型
        logging.info("[GPU TYPE FILTER] 原始返回: %s", str(resp)[:800])

if __name__ == "__main__":
    main()
