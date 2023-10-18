# ruff: noqa: D103
"""Subcommands of the main CLI module."""
import click
from click import secho

from ..api.client import Client
from .layout import print_table


@click.command(help="Get Mockaroo data types")
@click.option("--pager", "-P", is_flag=True, default=False, help="Page output.")
def types(pager):
    client = Client()
    types = client.types()

    print_table(data_types=types, page=pager)


@click.command(help="Upload dataset to Mockaroo")
@click.argument("name")
@click.argument("input_file", type=click.Path(exists=True))
def upload(name, input_file):
    client = Client()
    response = client.upload(name=name, path=input_file)
    if response["success"]:
        secho("Uploaded!", fg="bright_green")


@click.command(help="Delete a dataset from Mockaroo")
@click.argument("name")
def delete(name):
    client = Client()
    user_input = input("Are you sure you want to delete? [y/N]")
    if user_input.upper() == "Y":
        response = client.delete(name=name)
        if response["success"]:
            secho("Deleted!", fg="bright_red")
