import click

from yottaml.__version__ import __version__
from yottaml_cli.commands import credentials, serverless, gpus, pods, tasks
from yottaml_cli.config import configure, load_profile

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="yotta")
@click.option(
    "--api-key",
    envvar="YOTTA_API_KEY",
    default=None,
    help="API key (or set YOTTA_API_KEY).",
)
@click.option(
    "--base-url",
    envvar="YOTTA_BASE_URL",
    default=None,
    help="API base URL (or set YOTTA_BASE_URL).",
)
@click.option(
    "--profile",
    default="default",
    show_default=True,
    help="Config profile from ~/.yotta/config.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    show_default=True,
    help="Output format.",
)
@click.option("--debug", is_flag=True, default=False, help="Enable debug logging.")
@click.pass_context
def cli(ctx, api_key, base_url, profile, output_format, debug):
    """Yotta — YottaML command-line interface."""
    ctx.ensure_object(dict)
    cfg = load_profile(profile)
    ctx.obj["api_key"] = api_key or cfg.get("api_key")
    ctx.obj["base_url"] = base_url or cfg.get("base_url") or "https://api.yottalabs.ai"
    ctx.obj["debug"] = debug
    ctx.obj["format"] = output_format


cli.add_command(configure)
cli.add_command(pods.pods)
cli.add_command(serverless.serverless)
cli.add_command(gpus.gpus)
cli.add_command(credentials.credentials)
cli.add_command(tasks.tasks)
