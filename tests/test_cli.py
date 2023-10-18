# ruff: noqa: D103
"""Unit test for CLI."""
import pytest
import warnings

from unittest.mock import patch, Mock

from click.testing import CliRunner

from mockaroo.__main__ import cli
from mockaroo.cli.commands import types, upload, delete
from mockaroo.api.client import Client

@pytest.fixture
def runner():
    return CliRunner()

def empty_client():
    """Create an instance of client."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return Client()

def test_cli(runner):
    result = runner.invoke(cli)
    assert result.output
    assert result.exit_code == 0


def test_types_command(runner):
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {
            "types": [
                {
                    "name": "Words", 
                    "type": "string", 
                    "parameters": [
                        {
                            "name": "min",
                            "type": "integer", 
                            "description": 
                            "min value", 
                            "default": 10,
                        },
                        {
                            "name": "max",
                            "type": "integer", 
                            "description": 
                            "max value", 
                            "default": 20,
                        },
                    ],
                },
                {
                    "name": "Row Number", 
                    "type": "integer", 
                    "parameters": [],
                }
            ]
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response
    
        result = runner.invoke(types)
    
        assert result.output
        assert result.exit_code == 0


def test_successful_upload_command(runner):
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_request.return_value = mock_response
    
        result = runner.invoke(upload, ["test", "tests/samples/test.csv"])
    
        assert result.output == "Uploaded!\n"
        assert result.exit_code == 0


def test_delete_command(runner):
    with patch("builtins.input", return_value="y"), patch("requests.request") as mock_request:  # noqa: E501
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_request.return_value = mock_response
    
        result = runner.invoke(delete, ["test"])
    
        assert result.output == "Deleted!\n"
        assert result.exit_code == 0