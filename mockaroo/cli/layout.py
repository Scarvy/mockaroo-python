"""Provides code to display rich rendered layouts."""
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


def table_layout(data_types: List[Dict[str, Any]]) -> None:
    """Displays Mockaroo data types in a table format using rich.

    Args:
        data_types (List[Dict[str, Any]]): List of data types.
    """
    table = Table(leading=1, highlight=True, title="Mockaroo 🦘 Datatypes")

    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Parameters")

    for d in data_types:
        name = Text(d["name"], style="bold #19857b")
        data_type = Text(d["type"], style="bold #52a552") if d["type"] else Text("")
        params = d.get("parameters", "")
        if params:
            result = []
            for count, param in enumerate(params, start=1):
                formatted_str = \
                    f"{count}.) [#90caf9]Name[/#90caf9]: {param['name']}"\
                    "[#90caf9]Type[/#90caf9]: {param['type']} "\
                    "[#90caf9]Description[/#90caf9]: '{param['description']}' "\
                    "[#90caf9]Default[/#90caf9]: {param['default']}\n"
                result.append(formatted_str)

            result_str = "\n".join(result)
        else:
            result_str = "None"

        table.add_row(name, data_type, result_str)

    console.print(table)


def print_table(
    data_types: List[Dict[str, Any]],
    page: bool = False,
) -> None:
    """Print the Mockaroo Datatype Table.

    Args:
        data_types (Dict[str, Any]): List of data types.
        page (bool, optional): Pagination. Defaults to False.
    """
    if page:
        with console.pager(styles=True):
            table_layout(data_types=data_types)
        return
    table_layout(data_types=data_types)
