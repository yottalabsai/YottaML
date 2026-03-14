import sys

import click

from yottaml.credential import CredentialApi
from yottaml.error import ClientError, ServerError
from yottaml_cli.formatter import format_output


def _client(ctx):
    return CredentialApi(
        api_key=ctx.obj["api_key"], base_url=ctx.obj["base_url"], debug=ctx.obj["debug"]
    )


def _out(data, fmt):
    format_output(data, fmt)


def _err(e):
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@click.group()
def credentials():
    """Manage registry credentials."""


@credentials.command("list")
@click.pass_context
def list_credentials(ctx):
    """List credentials."""
    try:
        _out(_client(ctx).get_credentials(), ctx.obj["format"])
    except (ClientError, ServerError) as e:
        _err(e)


@credentials.command("get")
@click.argument("credential_id")
@click.pass_context
def get_credential(ctx, credential_id):
    """Get credential details."""
    try:
        _out(_client(ctx).get_credential(credential_id), ctx.obj["format"])
    except (ClientError, ServerError) as e:
        _err(e)


@credentials.command("create")
@click.option("--name", required=True, help="Credential name.")
@click.option(
    "--type",
    "cred_type",
    required=True,
    help="Registry type (DOCKER_HUB, GCR, ECR, ACR, PRIVATE).",
)
@click.option("--username", required=True, help="Registry username.")
@click.option("--password", required=True, help="Registry password or token.")
@click.pass_context
def create_credential(ctx, name, cred_type, username, password):
    """Create a registry credential."""
    try:
        _out(
            _client(ctx).create_credential(
                name=name, type=cred_type, username=username, password=password
            ),
            ctx.obj["format"],
        )
    except (ClientError, ServerError) as e:
        _err(e)


@credentials.command("update")
@click.argument("credential_id")
@click.option("--name", default=None, help="New credential name.")
@click.option("--username", default=None, help="New registry username.")
@click.option("--password", default=None, help="New registry password or token.")
@click.pass_context
def update_credential(ctx, credential_id, name, username, password):
    """Update a credential (partial update)."""
    updates = {
        k: v
        for k, v in {"name": name, "username": username, "password": password}.items()
        if v is not None
    }
    if not updates:
        click.echo(
            "Error: at least one of --name, --username, --password must be provided.",
            err=True,
        )
        sys.exit(1)
    try:
        _out(
            _client(ctx).update_credential(credential_id, **updates), ctx.obj["format"]
        )
    except (ClientError, ServerError) as e:
        _err(e)


@credentials.command("delete")
@click.argument("credential_id")
@click.pass_context
def delete_credential(ctx, credential_id):
    """Delete a credential."""
    try:
        _out(_client(ctx).delete_credential(credential_id), ctx.obj["format"])
    except (ClientError, ServerError) as e:
        _err(e)
