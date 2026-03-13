import json
import sys

import click

from yottaml.elastic import ElasticApi
from yottaml.error import ClientError, ServerError


def _client(ctx):
    return ElasticApi(api_key=ctx.obj["api_key"], base_url=ctx.obj["base_url"], debug=ctx.obj["debug"])


def _out(data):
    click.echo(json.dumps(data, indent=2))


def _err(e):
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@click.group()
def serverless():
    """Manage serverless deployments."""


@serverless.command("create")
@click.option("--name", required=True, help="Endpoint name (max 20 chars).")
@click.option("--image", required=True, help="Container image.")
@click.option(
    "--resources",
    required=True,
    help='JSON array of resource objects, e.g. \'[{"region":"us-east-3","gpuType":"NVIDIA_RTX_A6000","gpuCount":1}]\'.',
)
@click.option("--workers", required=True, type=int, help="Initial worker count.")
@click.option(
    "--service-mode",
    required=True,
    type=click.Choice(["ALB", "QUEUE", "CUSTOM"], case_sensitive=True),
    help="Service mode: ALB, QUEUE, or CUSTOM.",
)
@click.option("--volume", required=True, type=int, help="Container volume in GB (min 20).")
@click.option("--image-registry", default=None, help="Image registry URL.")
@click.option("--credential-id", default=None, type=int, help="Container registry credential ID.")
@click.option("--init-cmd", default=None, help="Initialization command.")
@click.option(
    "--env",
    multiple=True,
    metavar="KEY=VALUE",
    help="Environment variable (repeatable), e.g. --env FOO=bar.",
)
@click.option("--expose-port", default=None, type=int, help="Port to expose.")
@click.option("--expose-protocol", default=None, help="Expose protocol (e.g. HTTP).")
@click.option("--webhook", default=None, help="Webhook URL for worker status notifications.")
@click.pass_context
def create_deployment(
    ctx,
    name,
    image,
    resources,
    workers,
    service_mode,
    volume,
    image_registry,
    credential_id,
    init_cmd,
    env,
    expose_port,
    expose_protocol,
    webhook,
):
    """Create a new serverless deployment."""
    try:
        resources_list = json.loads(resources)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: --resources is not valid JSON: {exc}", err=True)
        sys.exit(1)

    env_vars = None
    if env:
        env_vars = []
        for item in env:
            if "=" not in item:
                click.echo(f"Error: --env value must be KEY=VALUE, got: {item!r}", err=True)
                sys.exit(1)
            k, v = item.split("=", 1)
            env_vars.append({"name": k, "value": v})

    expose = None
    if expose_port is not None:
        expose = {"port": expose_port}
        if expose_protocol:
            expose["protocol"] = expose_protocol

    try:
        _out(
            _client(ctx).create_deployment(
                name=name,
                image=image,
                resources=resources_list,
                workers=workers,
                service_mode=service_mode,
                container_volume_in_gb=volume,
                image_registry=image_registry,
                credential_id=credential_id,
                initialization_command=init_cmd,
                environment_vars=env_vars,
                expose=expose,
                webhook=webhook,
            )
        )
    except (ClientError, ServerError) as e:
        _err(e)


@serverless.command("list")
@click.option("--status", multiple=True, help="Filter by status (repeatable), e.g. RUNNING.")
@click.pass_context
def list_deployments(ctx, status):
    """List serverless deployments."""
    try:
        _out(_client(ctx).get_deployments(status_list=list(status) or None))
    except (ClientError, ServerError) as e:
        _err(e)


@serverless.command("get")
@click.argument("deployment_id")
@click.pass_context
def get_deployment(ctx, deployment_id):
    """Get deployment details."""
    try:
        _out(_client(ctx).get_deployment_detail(deployment_id))
    except (ClientError, ServerError) as e:
        _err(e)


@serverless.command("delete")
@click.argument("deployment_id")
@click.pass_context
def delete_deployment(ctx, deployment_id):
    """Delete a deployment."""
    try:
        _out(_client(ctx).delete_deployment(deployment_id))
    except (ClientError, ServerError) as e:
        _err(e)


@serverless.command("start")
@click.argument("deployment_id")
@click.pass_context
def start_deployment(ctx, deployment_id):
    """Start a deployment."""
    try:
        _out(_client(ctx).start_deployment(deployment_id))
    except (ClientError, ServerError) as e:
        _err(e)


@serverless.command("stop")
@click.argument("deployment_id")
@click.pass_context
def stop_deployment(ctx, deployment_id):
    """Stop a deployment."""
    try:
        _out(_client(ctx).stop_deployment(deployment_id))
    except (ClientError, ServerError) as e:
        _err(e)


@serverless.command("scale")
@click.argument("deployment_id")
@click.option("--workers", required=True, type=int, help="Target worker count.")
@click.pass_context
def scale_deployment(ctx, deployment_id, workers):
    """Scale deployment workers."""
    try:
        _out(_client(ctx).scale_workers(deployment_id, workers))
    except (ClientError, ServerError) as e:
        _err(e)


@serverless.command("workers")
@click.argument("deployment_id")
@click.option("--status", multiple=True, help="Filter workers by status (repeatable).")
@click.pass_context
def list_workers(ctx, deployment_id, status):
    """List workers for a deployment."""
    try:
        _out(_client(ctx).get_workers(deployment_id, status_list=list(status) or None))
    except (ClientError, ServerError) as e:
        _err(e)
