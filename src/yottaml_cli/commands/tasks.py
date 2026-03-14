import json
import sys

import click

from yottaml.error import ClientError, ServerError
from yottaml.skywalker import SkywalkerTaskApi
from yottaml_cli.formatter import format_output


def _client(ctx):
    return SkywalkerTaskApi(
        api_key=ctx.obj["api_key"], base_url=ctx.obj["base_url"], debug=ctx.obj["debug"]
    )


def _out(data, fmt):
    format_output(data, fmt)


def _err(e):
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@click.group()
def tasks():
    """Manage Skywalker tasks."""


@tasks.command("list")
@click.option("--endpoint-id", required=True, type=int, help="Serverless endpoint ID.")
@click.option(
    "--status",
    default=None,
    help="Filter by status (PROCESSING|DELIVERED|SUCCESS|FAILED).",
)
@click.option("--page", type=int, default=1, show_default=True, help="Page number.")
@click.option(
    "--page-size", type=int, default=10, show_default=True, help="Results per page."
)
@click.pass_context
def list_tasks(ctx, endpoint_id, status, page, page_size):
    """List tasks for an endpoint."""
    try:
        _out(
            _client(ctx).list_tasks(
                endpoint_id=endpoint_id, status=status, page=page, page_size=page_size
            ),
            ctx.obj["format"],
        )
    except (ClientError, ServerError) as e:
        _err(e)


@tasks.command("get")
@click.option("--endpoint-id", required=True, type=int, help="Serverless endpoint ID.")
@click.argument("task_id")
@click.pass_context
def get_task(ctx, endpoint_id, task_id):
    """Get task details."""
    try:
        _out(
            _client(ctx).get_task(endpoint_id=endpoint_id, task_id=task_id),
            ctx.obj["format"],
        )
    except (ClientError, ServerError) as e:
        _err(e)


@tasks.command("count")
@click.option("--endpoint-id", required=True, type=int, help="Serverless endpoint ID.")
@click.pass_context
def processing_count(ctx, endpoint_id):
    """Get number of queued and processing tasks."""
    try:
        _out(
            _client(ctx).get_processing_count(endpoint_id=endpoint_id),
            ctx.obj["format"],
        )
    except (ClientError, ServerError) as e:
        _err(e)


@tasks.command("create")
@click.option("--endpoint-id", required=True, type=int, help="Serverless endpoint ID.")
@click.option(
    "--task-id",
    default=None,
    help="User-defined task ID (alphanumeric + underscore, max 255).",
)
@click.option("--worker-port", required=True, type=int, help="Worker port (1-65535).")
@click.option("--process-uri", required=True, help="Worker URI path, e.g. /process.")
@click.option(
    "--input", "input_data", required=True, help="Task input as a JSON string."
)
@click.option("--webhook", default=None, help="Webhook URL for task completion.")
@click.option("--webhook-auth-key", default=None, help="Auth key for the webhook URL.")
@click.pass_context
def create_task(
    ctx,
    endpoint_id,
    task_id,
    worker_port,
    process_uri,
    input_data,
    webhook,
    webhook_auth_key,
):
    """Submit a task to an endpoint."""
    try:
        parsed_input = json.loads(input_data)
    except json.JSONDecodeError as e:
        click.echo(f"Error: --input is not valid JSON: {e}", err=True)
        sys.exit(1)
    try:
        _out(
            _client(ctx).create_task(
                endpoint_id=endpoint_id,
                task_id=task_id,
                worker_port=worker_port,
                process_uri=process_uri,
                input=parsed_input,
                webhook=webhook,
                webhook_auth_key=webhook_auth_key,
            ),
            ctx.obj["format"],
        )
    except (ClientError, ServerError) as e:
        _err(e)
