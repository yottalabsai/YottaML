import json

import click
from tabulate import tabulate


def format_output(response: dict, fmt: str) -> None:
    """Render an API response in the requested format (table or json)."""
    if fmt == "json":
        click.echo(json.dumps(response, indent=2))
        return

    # Table format
    data = response.get("data")

    if data is None or data == "" or data == []:
        click.echo(response.get("message", "OK"))
        return

    if isinstance(data, list):
        headers = list(data[0].keys())
        rows = [[_fmt_cell(item.get(h)) for h in headers] for item in data]
        click.echo(tabulate(rows, headers=headers, tablefmt="simple"))
    elif isinstance(data, dict):
        rows = [[k, _fmt_cell(v)] for k, v in data.items()]
        click.echo(tabulate(rows, headers=["Field", "Value"], tablefmt="simple"))
    else:
        # Scalar (e.g. a returned ID)
        click.echo(data)


def _fmt_cell(value) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"))
    if value is None:
        return ""
    return str(value)
