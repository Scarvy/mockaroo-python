# ruff: noqa: D103
"""Unit tests for the mockaroo api module."""

import os
import warnings
from unittest.mock import Mock, patch

import pytest

from mockaroo import Client
from mockaroo.exceptions import InvalidApiKeyError, UsageLimitExceededError


def empty_client():
    """Create an instance of client."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return Client()


def test_create():
    """Test init without passing api_key."""
    empty_client()


def test_no_api_key():
    with patch.dict(os.environ, {}, clear=True), warnings.catch_warnings(
        record=True
    ) as w:  # Clearing all env vars
        client = empty_client()
        _ = client.api_key  #
        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert (
            "API key is not provided. Set MOCKAROO_API_KEY `export MOCKAROO_API_KEY=your_api_key`."
            == str(w[-1].message)
        )


def test_create_attributes():
    client = Client(api_key="test_key", host="test_host", secure=False, port=80)
    assert client._api_key == "test_key"
    assert client.host == "test_host"
    assert client.secure is False
    assert client.port == 80


def test_validate_fields():
    client = empty_client()
    with pytest.raises(ValueError):
        client._validate_fields([{"name": "name"}])


def test_http_request_error():
    client = empty_client()
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = 403
        mock_request.return_value.json.return_value = {"error": "Usage Limit Exceeded"}
        with pytest.raises(UsageLimitExceededError):
            client._http_request("GET", "http://test.com")


def test_http_invalid_api_key():
    client = empty_client()
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = 401
        mock_request.return_value.json.return_value = {"error": "Invalid API Key"}
        with pytest.raises(InvalidApiKeyError):
            client._http_request("GET", "http://test.com")


def test_types():
    client = empty_client()
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"types": [{"type": "Integer"}]}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = client.types()

        assert result == [{"type": "Integer"}]


def test_upload():
    client = empty_client()
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = client.upload(name="test_name", path="tests/samples/test.csv")

        assert result == {"success": True}


def test_delete():
    client = empty_client()
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = client.delete(name="test_name")

        assert result == {"success": True}


@pytest.mark.parametrize(
    "fmt, expected_output",
    [
        (
            "json",
            [{"mock_key": "mock_value"}],
        ),
        ("csv", b"id,col_header1,col_header2\n1,row_value1,row_value2\n"),
        ("txt", b"id\tcol_header1\tlcol_header2\n1\trow_value1\trow_value2\n"),
        (
            "xml",
            b"<?xml version='1.0' encoding='UTF-8'?>\n<dataset>\n<record><id>1</id><first_name>Ericka</first_name><last_name>Stobart</last_name></record></dataset>",  # noqa: E501
        ),
    ],
)
def test_generate(fmt, expected_output):
    client = empty_client()
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        if fmt == "json":
            mock_response.json.return_value = expected_output
        else:
            mock_response.content = expected_output
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = client.generate(schema="test_schema", fmt=fmt)

        assert result == expected_output


def test_schema_and_fields_argument_warning():
    """Test raise `UserWarning`when both `schema` and `fields` parameters are given.

    The purpose of this test is to verify that a warning is generated when a user
    specifies both schema and fields. The schema parameter takes precedence, meaning
    any fields specified will be ignored. The warning informs the user of this behavior
    to avoid confusion.

    Example case:

        - If the `schema` is set to "Person", and
        - The user also specifies `fields` as [{"name", "id", "type", "Row Number"}],

        The test should confirm that a UserWarning is issued, and the generated data
        will only follow the "Person" schema, ignoring the custom fields.

    """
    client = empty_client()
    with patch("requests.request") as mock_request, warnings.catch_warnings(
        record=True
    ) as w:
        mock_response = Mock()
        mock_response.json.return_value = [{"first_name": "Jane", "last_name": "Doe"}]
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = client.generate(
            schema="Person", fields=[{"name": "id", "type": "Row Number"}]
        )
        assert result == [{"first_name": "Jane", "last_name": "Doe"}]
        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert (
            "You should specify either 'schema' or 'fields', "
            "but not both. `schema` will override any values passed"
            "to `fields`." == str(w[-1].message)
        )


@pytest.mark.parametrize(
    "endpoint, params, expected_url",
    [
        (
            Client.GENERATE_ENDPOINT,
            {"schema": "Person", "fmt": "json", "count": 1},
            "https://api.mockaroo.com/api/generate.json?schema=Person&count=1&client=python&key=api_key",
        ),
        (
            Client.GENERATE_ENDPOINT,
            {"schema": "Person", "fmt": "csv", "count": 1},
            "https://api.mockaroo.com/api/generate.csv?schema=Person&count=1&client=python&key=api_key",
        ),
        (
            Client.GENERATE_ENDPOINT,
            {"schema": "Person", "fmt": "csv", "count": 5},
            "https://api.mockaroo.com/api/generate.csv?schema=Person&count=5&client=python&key=api_key",
        ),
        (
            Client.TYPE_ENDPOINT,
            {},
            "https://api.mockaroo.com/api/types/?client=python&key=api_key",
        ),
        (
            Client.UPLOAD_ENDPOINT,
            {"name": "test_name"},
            "https://api.mockaroo.com/api/datasets/test_name?client=python&key=api_key",
        ),
    ],
)
def test_get_url(endpoint, expected_url, params):
    """Test URL construction."""
    client = Client(api_key="api_key")
    url = client._get_url(endpoint, **params)
    assert url == expected_url
