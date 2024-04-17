import json

import rich_click as click

from mockaroo import Client

from .layout import print_table


@click.group()
@click.version_option()
def cli():
    "A client wrapper for the Mockaroo API"


@cli.command(name="types")
@click.option("--pager", "-P", is_flag=True, default=False, help="Page output.")
def get_mockaroo_types(pager):
    """Get a list of supported Mockaroo data types."""
    client = Client()
    types = client.types()

    print_table(data_types=types, page=pager)


@cli.command(name="upload")
@click.argument("name")
@click.argument("input_file", type=click.Path(exists=True))
def upload(name, input_file):
    """Upload a file to Mockaroo."""
    client = Client()
    response = client.upload(name=name, path=input_file)
    if response["success"]:
        click.secho("Uploaded!", fg="bright_green")


@cli.command(name="delete")
@click.argument("name")
def delete(name):
    """Delete a dataset on Mockaroo."""
    client = Client()
    user_input = input("Are you sure you want to delete? [y/N]")
    if user_input.upper() == "Y":
        response = client.delete(name=name)
        if response["success"]:
            click.secho("Deleted!", fg="bright_red")


@cli.command(name="gen")
@click.argument("schema")
@click.option(
    "--fmt",
    "-f",
    type=click.Choice(("json", "csv", "txt", "xml", "sql"), case_sensitive=False),
    default="json",
    help="Set dataset format.",
)
@click.option(
    "--count",
    "-n",
    default=3,
    help="Number of results.",
)
def generate(schema, fmt, count):
    """Generate mock data using the Mockaroo API."""
    client = Client()
    result = client.generate(schema=schema, fmt=fmt, count=count)
    if fmt == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(result)
