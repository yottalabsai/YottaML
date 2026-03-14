import json
import sys

import click

from yottaml.error import ClientError, ServerError
from yottaml.pod import PodApi
from yottaml_cli.formatter import format_output


def _client(ctx):
    return PodApi(
        api_key=ctx.obj["api_key"], base_url=ctx.obj["base_url"], debug=ctx.obj["debug"]
    )


def _out(data, fmt):
    format_output(data, fmt)


def _err(e):
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@click.group()
def pods():
    """Manage pods."""


@pods.command("list")
@click.option("--region", multiple=True, help="Filter by region (repeatable).")
@click.option(
    "--status", multiple=True, type=int, help="Filter by status code (repeatable)."
)
@click.pass_context
def list_pods(ctx, region, status):
    """List pods."""
    try:
        _out(
            _client(ctx).get_pods(
                region_list=list(region) or None, status_list=list(status) or None
            ),
            ctx.obj["format"],
        )
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("get")
@click.argument("pod_id")
@click.pass_context
def get_pod(ctx, pod_id):
    """Get pod details."""
    try:
        _out(_client(ctx).get_pod(pod_id), ctx.obj["format"])
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("create")
@click.option("--image", required=True, help="Container image.")
@click.option("--gpu-type", required=True, help="GPU type, e.g. NVIDIA_RTX_5090.")
@click.option(
    "--gpu-count",
    type=int,
    default=1,
    show_default=True,
    help="Number of GPUs (must be power of 2).",
)
@click.option("--region", multiple=True, help="Acceptable region(s) (repeatable).")
@click.option("--name", default=None, help="Pod name.")
@click.option("--init-cmd", default=None, help="Initialization command.")
@click.option(
    "--container-volume", type=int, default=None, help="Container volume in GB."
)
@click.option(
    "--persistent-volume", type=int, default=None, help="Persistent volume in GB."
)
@click.option(
    "--persistent-mount-path", default=None, help="Persistent volume mount path."
)
@click.option(
    "--image-registry", default=None, help="Docker registry URL for private images."
)
@click.option(
    "--credential-id", default=None, type=int, help="Stored registry credential ID."
)
@click.option(
    "--image-public-type",
    default=None,
    type=click.Choice(["PUBLIC", "PRIVATE"], case_sensitive=True),
    help="Image visibility: PUBLIC or PRIVATE.",
)
@click.option(
    "--resource-type",
    default=None,
    type=click.Choice(["GPU", "CPU"], case_sensitive=True),
    help="Resource type: GPU (default) or CPU.",
)
@click.option(
    "--min-vram", type=int, default=None, help="Minimum single-card VRAM in GB."
)
@click.option(
    "--min-ram", type=int, default=None, help="Minimum single-card RAM in GB."
)
@click.option(
    "--min-vcpu", type=int, default=None, help="Minimum single-card vCPU count."
)
@click.option("--shm", type=int, default=None, help="Shared memory size in GB.")
@click.option(
    "--env",
    multiple=True,
    metavar="KEY=VALUE",
    help="Environment variable (repeatable), e.g. --env FOO=bar.",
)
@click.option(
    "--expose",
    default=None,
    help='JSON array of ports to expose, e.g. \'[{"port":8080,"protocol":"http"}]\'.',
)
@click.pass_context
def create_pod(
    ctx,
    image,
    gpu_type,
    gpu_count,
    region,
    name,
    init_cmd,
    container_volume,
    persistent_volume,
    persistent_mount_path,
    image_registry,
    credential_id,
    image_public_type,
    resource_type,
    min_vram,
    min_ram,
    min_vcpu,
    shm,
    env,
    expose,
):
    """Create a new pod."""
    env_vars = None
    if env:
        env_vars = []
        for item in env:
            if "=" not in item:
                click.echo(
                    f"Error: --env value must be KEY=VALUE, got: {item!r}", err=True
                )
                sys.exit(1)
            k, v = item.split("=", 1)
            env_vars.append({"key": k, "value": v})

    expose_list = None
    if expose is not None:
        try:
            expose_list = json.loads(expose)
        except json.JSONDecodeError as exc:
            click.echo(f"Error: --expose is not valid JSON: {exc}", err=True)
            sys.exit(1)

    try:
        _out(
            _client(ctx).new_pod(
                image=image,
                gpu_type=gpu_type,
                gpu_count=gpu_count,
                regions=list(region) or None,
                name=name,
                initialization_command=init_cmd,
                container_volume_in_gb=container_volume,
                persistent_volume_in_gb=persistent_volume,
                persistent_mount_path=persistent_mount_path,
                image_registry=image_registry,
                container_registry_auth_id=credential_id,
                image_public_type=image_public_type,
                resource_type=resource_type,
                min_single_card_vram_in_gb=min_vram,
                min_single_card_ram_in_gb=min_ram,
                min_single_card_vcpu=min_vcpu,
                shm_in_gb=shm,
                environment_vars=env_vars,
                expose=expose_list,
            ),
            ctx.obj["format"],
        )
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("delete")
@click.argument("pod_id")
@click.pass_context
def delete_pod(ctx, pod_id):
    """Delete a pod."""
    try:
        _out(_client(ctx).delete_pod(pod_id), ctx.obj["format"])
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("pause")
@click.argument("pod_id")
@click.pass_context
def pause_pod(ctx, pod_id):
    """Pause a running pod."""
    try:
        _out(_client(ctx).pause_pod(pod_id), ctx.obj["format"])
    except (ClientError, ServerError) as e:
        _err(e)


@pods.command("resume")
@click.argument("pod_id")
@click.pass_context
def resume_pod(ctx, pod_id):
    """Resume a paused pod."""
    try:
        _out(_client(ctx).resume_pod(pod_id), ctx.obj["format"])
    except (ClientError, ServerError) as e:
        _err(e)
