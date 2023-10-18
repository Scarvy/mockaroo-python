"""The main CLI module of the Mockaroo APIs."""
import rich_click as click
from rich_click.cli import patch

patch()

from .cli import commands  # noqa: E402

help_config = click.RichHelpConfiguration(
    show_arguments=True, group_arguments_options=True, use_rich_markup=True
)


@click.rich_config(help_config=help_config)
@click.group(help="Interact with the Mockaroo APIs 🦘 + 🐍")
def cli():  # noqa: D103 
    pass # pragma: no cover


# Commands
cli.add_command(commands.types)  # Get available Mockaroo data types
cli.add_command(commands.upload)  # Upload dataset to Mockaroo
cli.add_command(commands.delete)  # Delete a dataset from Mockaroo

if __name__ == "__main__": # pragma: no cover
    cli()
