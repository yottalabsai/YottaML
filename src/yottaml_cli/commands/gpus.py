import json
import sys

import click

from yottaml.error import ClientError, ServerError
from yottaml.gpu import GpuApi


def _client(ctx):
    return GpuApi(
        api_key=ctx.obj["api_key"], base_url=ctx.obj["base_url"], debug=ctx.obj["debug"]
    )


def _out(data):
    click.echo(json.dumps(data, indent=2))


def _err(e):
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@click.group()
def gpus():
    """Query GPU availability."""


@gpus.command("list")
@click.pass_context
def list_gpus(ctx):
    """List available GPU types."""
    try:
        _out(_client(ctx).get_gpus())
    except (ClientError, ServerError) as e:
        _err(e)
