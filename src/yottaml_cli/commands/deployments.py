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
def deployments():
    """Manage elastic deployments."""


@deployments.command("list")
@click.option("--status", multiple=True, help="Filter by status (repeatable), e.g. RUNNING.")
@click.pass_context
def list_deployments(ctx, status):
    """List elastic deployments."""
    try:
        _out(_client(ctx).get_deployments(status_list=list(status) or None))
    except (ClientError, ServerError) as e:
        _err(e)


@deployments.command("get")
@click.argument("deployment_id")
@click.pass_context
def get_deployment(ctx, deployment_id):
    """Get deployment details."""
    try:
        _out(_client(ctx).get_deployment_detail(deployment_id))
    except (ClientError, ServerError) as e:
        _err(e)


@deployments.command("delete")
@click.argument("deployment_id")
@click.pass_context
def delete_deployment(ctx, deployment_id):
    """Delete a deployment."""
    try:
        _out(_client(ctx).delete_deployment(deployment_id))
    except (ClientError, ServerError) as e:
        _err(e)


@deployments.command("start")
@click.argument("deployment_id")
@click.pass_context
def start_deployment(ctx, deployment_id):
    """Start a deployment."""
    try:
        _out(_client(ctx).start_deployment(deployment_id))
    except (ClientError, ServerError) as e:
        _err(e)


@deployments.command("stop")
@click.argument("deployment_id")
@click.pass_context
def stop_deployment(ctx, deployment_id):
    """Stop a deployment."""
    try:
        _out(_client(ctx).stop_deployment(deployment_id))
    except (ClientError, ServerError) as e:
        _err(e)


@deployments.command("scale")
@click.argument("deployment_id")
@click.option("--workers", required=True, type=int, help="Target worker count.")
@click.pass_context
def scale_deployment(ctx, deployment_id, workers):
    """Scale deployment workers."""
    try:
        _out(_client(ctx).scale_workers(deployment_id, workers))
    except (ClientError, ServerError) as e:
        _err(e)


@deployments.command("workers")
@click.argument("deployment_id")
@click.option("--status", multiple=True, help="Filter workers by status (repeatable).")
@click.pass_context
def list_workers(ctx, deployment_id, status):
    """List workers for a deployment."""
    try:
        _out(_client(ctx).get_workers(deployment_id, status_list=list(status) or None))
    except (ClientError, ServerError) as e:
        _err(e)
