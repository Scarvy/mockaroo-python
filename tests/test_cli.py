# ruff: noqa: D103
"""Unit test for CLI."""

import json
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from mockaroo.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_version(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


def test_cli(runner):
    result = runner.invoke(cli)
    assert result.output
    assert result.exit_code == 0


def test_types(runner):
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
                            "description": "min value",
                            "default": 10,
                        },
                        {
                            "name": "max",
                            "type": "integer",
                            "description": "max value",
                            "default": 20,
                        },
                    ],
                },
                {
                    "name": "Row Number",
                    "type": "integer",
                    "parameters": [],
                },
            ]
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = runner.invoke(cli, ["types"])

        assert result.output
        assert result.exit_code == 0


def test_upload(runner):
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = runner.invoke(
            cli,
            [
                "upload",
                "test",
                "tests/samples/test.csv",
            ],
        )

        assert result.output == "Uploaded!\n"
        assert result.exit_code == 0


def test_delete(runner):
    with patch("builtins.input", return_value="y"), patch(
        "requests.request"
    ) as mock_request:  # noqa: E501
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = runner.invoke(cli, ["delete", "test"])

        assert result.output == "Deleted!\n"
        assert result.exit_code == 0


@pytest.mark.parametrize(
    "params, expected_output",
    [
        (
            {"schema": "Person", "fmt": "json", "count": 1},
            {"id": 1, "first_name": "Stormy", "last_name": "Raithbie"},
        ),
        # (
        #     {"schema": "Person", "fmt": "csv", "count": 1},
        #     b"id,first_name,last_name\n1,Culley,Shawel\n",
        # ),
        # (
        #     {"schema": "Person", "fmt": "txt", "count": 1},
        #     b"id\tfirst_name\tlast_name\n1\tSteven\tFerrarone\n",
        # ),
        # (
        #     {"schema": "Person", "fmt": "xml", "count": 1},
        #     b"<?xml version='1.0' encoding='UTF-8'?>\n<dataset>\n<record><id>1</id><first_name>Brianne</first_name><last_name>Frankcom</last_name></record></dataset>",  # noqa: E501
        # ),
        # (
        #     {"schema": "Person", "fmt": "sql", "count": 1},
        #     b"insert into MOCK_DATA (id, first_name, last_name) values (1, 'Cherlyn', 'Bytheway');\n",  # noqa: E501
        # ),
    ],
)
def test_generate(runner, params, expected_output):
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = expected_output
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = runner.invoke(
            cli,
            [
                "gen",
                params["schema"],
                "--fmt",
                params["fmt"],
                "--count",
                str(params["count"]),
            ],
        )

        if params["fmt"] == "json":
            # Deserialize JSON from output before comparison
            assert json.loads(result.output) == expected_output
        else:
            # Compare text outputs directly
            assert result.output.strip() == expected_output.strip()

        assert result.exit_code == 0
