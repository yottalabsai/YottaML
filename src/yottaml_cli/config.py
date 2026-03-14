import configparser
import os
from pathlib import Path

import click

_CONFIG_DIR = Path.home() / ".yotta"
_CONFIG_FILE = _CONFIG_DIR / "config"


def load_profile(profile: str = "default") -> dict:
    """Load config values for a profile from ~/.yotta/config.

    Returns an empty dict if the file or profile section does not exist.
    """
    if not _CONFIG_FILE.exists():
        return {}
    config = configparser.ConfigParser()
    config.read(_CONFIG_FILE)
    if profile not in config:
        return {}
    return dict(config[profile])


def save_profile(profile: str, values: dict) -> None:
    """Write config values for a profile to ~/.yotta/config."""
    _CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    if _CONFIG_FILE.exists():
        config.read(_CONFIG_FILE)
    if profile not in config:
        config[profile] = {}
    config[profile].update({k: v for k, v in values.items() if v})
    with open(_CONFIG_FILE, "w") as fh:
        config.write(fh)
    os.chmod(_CONFIG_FILE, 0o600)


@click.command("configure")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
def configure(profile):
    """Configure API credentials for a profile."""
    existing = load_profile(profile)
    click.echo(f"Configuring profile [{profile}] in {_CONFIG_FILE}\n")

    api_key = click.prompt(
        "API key",
        default=existing.get("api_key", ""),
        hide_input=True,
        show_default=False,
        prompt_suffix=" (hidden): ",
    )
    base_url = click.prompt(
        "Base URL",
        default=existing.get("base_url", "https://api.yottalabs.ai"),
    )

    save_profile(profile, {"api_key": api_key, "base_url": base_url})
    click.echo(f"\nSaved to {_CONFIG_FILE}")
