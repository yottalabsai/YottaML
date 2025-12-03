#!/usr/bin/env python
import argparse
import logging

from examples.utils.prepare_env import get_api_key
from yotta.elastic import ElasticApi
from yotta.error import ClientError
from yotta.lib.utils import config_logging


def main():
    config_logging(logging, logging.DEBUG)

    api_key = get_api_key()
    client = ElasticApi(api_key, base_url="https://api.dev.yottalabs.ai", debug=True)

    resources = [
        {
            "region": "us-west-1",
            "gpuType": "NVIDIA_L4_24G",
            "gpuCount": 1,
        }
    ]

    try:
        # Example pod ID to retrieve - replace with your actual pod ID
        deployment_id = 384425425995034706

        resp = client.update_deployment(
            deployment_id=deployment_id,
            name="Llama-3.2-3B3",
            resources=resources,
            min_single_card_vram_in_gb=12,
            min_single_card_vcpu=10,
            min_single_card_ram_in_gb=14,
            workers=1,
            container_volume_in_gb=20,
            initialization_command=(
                "vllm serve meta-llama/Llama-3.2-3B-Instruct "
                "--served-model-name meta-llama/Llama-3.2-3B-Instruct  "
                "--max-model-len 20480 --port 8000 --dtype half "
                "--gpu-memory-utilization 0.90 --tensor-parallel-size 1 "
                "--chat-template /vllm-workspace/examples/tool_chat_template_llama3.2_json.jinja"
            ),
            environment_vars=[
                {"key": "HUGGING_FACE_HUB_TOKEN", "value": "YOUR_HF_TOKEN"},
                {"key": "VLLM_PORT", "value": "8000"},
                {"key": "CUDA_VISIBLE_DEVICES", "value": "1"},
            ],
            expose={"port": 8000, "protocol": "http"},
        )

        if resp.get("code") == 10000:
            logging.info("Elastic deployment updated successfully")
            detail = resp.get("data") or {}
            logging.info("Deployment detail:")
            for k, v in detail.items():
                logging.info(f"{k:25}: {v}")
        else:
            logging.warning("Unexpected code=%s message=%s", resp.get("code"), resp.get("message"))
    except ClientError as e:
        logging.error("ClientError: status=%s code=%s message=%s", e.status_code, e.error_code, e.error_message)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
