import click

from yottaml_cli.commands import credentials, serverless, gpus, pods, tasks

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--api-key",
    envvar="YOTTA_API_KEY",
    default=None,
    help="API key (or set YOTTA_API_KEY).",
)
@click.option(
    "--base-url",
    envvar="YOTTA_BASE_URL",
    default="https://api.yottalabs.ai",
    show_default=True,
    help="API base URL.",
)
@click.option("--debug", is_flag=True, default=False, help="Enable debug logging.")
@click.pass_context
def cli(ctx, api_key, base_url, debug):
    """Yotta — YottaML command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["base_url"] = base_url
    ctx.obj["debug"] = debug


cli.add_command(pods.pods)
cli.add_command(serverless.serverless)
cli.add_command(gpus.gpus)
cli.add_command(credentials.credentials)
cli.add_command(tasks.tasks)
