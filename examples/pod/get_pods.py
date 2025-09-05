#!/usr/bin/env python
import logging
import argparse

from examples.utils.prepare_env import get_api_key
from yotta.error import ClientError
from yotta.lib.utils import config_logging, none_to_zero
from yotta.pod import PodApi


def format_size(size_in_gb):
    """Format size to appropriate unit"""
    if size_in_gb >= 1024:
        return f"{size_in_gb / 1024:.1f} TB"
    return f"{size_in_gb} GB"


def format_network_speed(speed_mbps):
    """Format network speed to appropriate unit"""
    if float(speed_mbps) >= 1000:
        return f"{float(speed_mbps) / 1000:.1f} Gbps"
    return f"{speed_mbps} Mbps"


def display_pod_summary(pod):
    """Display a single line summary of pod information"""
    raw_status = pod.get('status')

    # 端口健康统计（容错）
    expose = pod.get('expose') or []
    active_ports = sum(1 for p in expose if isinstance(p, dict) and p.get('healthy'))
    total_ports = len(expose)

    logging.info(
        f" {str(pod.get('id','')):10} | "
        f"{str(pod.get('podName',''))[:20]:<20} | "
        f"{str(pod.get('gpuType',''))[:15]:<15} x{none_to_zero(pod.get('gpuCount'),'gpuCount'):<2} | "
        f"{raw_status}"
    )


def display_pods_list(pods):
    """Display a list of pods in a table format"""
    if not pods:
        logging.info("No pods found.")
        return

    logging.info("\nPods List:")
    logging.info("=" * 100)
    logging.info("  ID                | Name                 | GPU Type            | Status")
    logging.info("-" * 100)

    sorted_pods = sorted(pods, key=lambda x: x.get('createdAt', 0), reverse=True)
    for pod in sorted_pods:
        display_pod_summary(pod)

    logging.info("-" * 100)
    logging.info(f"Total Pods: {len(pods)}")

    # 统计：活跃与总 GPU
    def is_running(p):
        try:
            return p.get('status') == "RUNNING"
        except Exception:
            return False

    active_pods = sum(1 for p in pods if is_running(p))
    total_gpus = sum(none_to_zero(p.get('gpuCount'), 'gpuCount') for p in pods)
    logging.info(f"Active Pods: {active_pods}")
    logging.info(f"Total GPUs: {total_gpus}")


def parse_args():
    parser = argparse.ArgumentParser(description="List pods with optional region/status filters")
    # 多值支持：--region ap-southeast-1 --region us-west-1
    # 或者：--region ap-southeast-1,us-west-1
    parser.add_argument(
        "--region", dest="regions", action="append", default=[],
        help="Region filter (repeatable or comma-separated), e.g. --region ap-southeast-1 --region us-west-1"
    )
    parser.add_argument(
        "--status", dest="statuses", action="append", default=[],
        help="Status filter as integers (repeatable or comma-separated), e.g. --status 1 --status 4 or --status 1,4"
    )
    parser.add_argument(
        "--base-url", default="https://api.dev.yottalabs.ai",
        help="API base URL (default: https://api.dev.yottalabs.ai)"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable HTTP debug logging"
    )
    return parser.parse_args()


def flat_split(values):
    """Support both repeated flags and comma-separated lists"""
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

    # 环境变量/准备脚本里读取 API Key
    api_key = get_api_key()

    client = PodApi(api_key, base_url=args.base_url, debug=args.debug)

    # 处理 regionList/statusList
    region_list = flat_split(args.regions) or None
    status_strs = flat_split(args.statuses) or []
    try:
        status_list = [int(s) for s in status_strs] if status_strs else None
    except ValueError:
        raise SystemExit("Invalid --status value(s): must be integers, e.g. 1 or 1,4")

    try:
        # 关键：把可选的 regionList/statusList 作为查询参数传入
        response = client.get_pods(
            **({"regionList": region_list} if region_list else {}),
            **({"statusList": status_list} if status_list else {})
        )

        if response.get('code') == 10000:
            logging.info("Successfully retrieved pods list")
            logging.info(f"Response message: {response.get('message')}")
            display_pods_list(response.get('data') or [])
        else:
            logging.warning(f"Unexpected response code: {response.get('code')}")
            logging.warning(f"Response message: {response.get('message')}")
    except ClientError as error:
        logging.error(
            "Client error occurred. Status: %s, Error code: %s, Message: %s",
            error.status_code, error.error_code, error.error_message
        )
    except Exception as error:
        logging.error("An unexpected error occurred: %s", str(error))


if __name__ == "__main__":
    main()
