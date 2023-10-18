# ruff: noqa: D103
"""Unit tests for layout module."""
import pytest  # noqa: F401

from mockaroo.cli.layout import print_table

def test_pager_layout():
    data_types = [{"name": "Words", "type": "string", "parameters": None}]
    assert print_table(data_types=data_types, page=True) is None
