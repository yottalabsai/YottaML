import json
import sys

import click

from yottaml.error import ClientError, ServerError
from yottaml.pod import PodApi


def _client(ctx):
    return PodApi(api_key=ctx.obj["api_key"], base_url=ctx.obj["base_url"], debug=ctx.obj["debug"])


def _out(data):
    click.echo(json.dumps(data, indent=2))


def _err(e):
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@click.group()
def pods():
    """Manage pods."""


@pods.command("list")
@click.option("--region", multiple=True, help="Filter by region (repeatable).")
@click.option("--status", multiple=True, type=int, help="Filter by status code (repeatable).")
@click.pass_context
def list_pods(ctx, region, status):
    """List pods."""
    try:
        _out(_client(ctx).get_pods(region_list=list(region) or None, status_list=list(status) or None))
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("get")
@click.argument("pod_id")
@click.pass_context
def get_pod(ctx, pod_id):
    """Get pod details."""
    try:
        _out(_client(ctx).get_pod(pod_id))
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("create")
@click.option("--image", required=True, help="Container image.")
@click.option("--gpu-type", required=True, help="GPU type, e.g. NVIDIA_L4_24G.")
@click.option("--gpu-count", type=int, default=1, show_default=True, help="Number of GPUs.")
@click.option("--region", default=None, help="Region.")
@click.option("--name", default=None, help="Pod name.")
@click.option("--cloud-type", default=None, help="Cloud type (SECURE or COMMUNITY).")
@click.option("--init-cmd", default=None, help="Initialization command.")
@click.option("--container-volume", type=int, default=None, help="Container volume in GB.")
@click.option("--persistent-volume", type=int, default=None, help="Persistent volume in GB.")
@click.option("--persistent-mount-path", default=None, help="Persistent volume mount path.")
@click.pass_context
def create_pod(ctx, image, gpu_type, gpu_count, region, name, cloud_type, init_cmd,
               container_volume, persistent_volume, persistent_mount_path):
    """Create a new pod."""
    try:
        _out(_client(ctx).new_pod(
            image=image,
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            region=region,
            pod_name=name,
            cloud_type=cloud_type,
            initialization_command=init_cmd,
            container_volume_in_gb=container_volume,
            persistent_volume_in_gb=persistent_volume,
            persistent_mount_path=persistent_mount_path,
        ))
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("delete")
@click.argument("pod_id")
@click.pass_context
def delete_pod(ctx, pod_id):
    """Delete a pod."""
    try:
        _out(_client(ctx).delete_pod(pod_id))
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("pause")
@click.argument("pod_id")
@click.pass_context
def pause_pod(ctx, pod_id):
    """Pause a running pod."""
    try:
        _out(_client(ctx).pause_pod(pod_id))
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("resume")
@click.argument("pod_id")
@click.pass_context
def resume_pod(ctx, pod_id):
    """Resume a paused pod."""
    try:
        _out(_client(ctx).resume_pod(pod_id))
    except (ClientError, ServerError) as e:
        _err(e)
