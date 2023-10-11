"""Unit tests for the mockaroo package."""
import pytest
import warnings

from unittest.mock import patch, Mock

from mockaroo import Client, InvalidApiKeyError, UsageLimitExceededError
from mockaroo.constants import GENERATE_ENDPOINT, UPLOAD_ENDPOINT, TYPE_ENDPOINT


def empty_client():
    """Create an instance of client"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return Client()


def test_create():
    """Test init without passing api_key"""
    empty_client()


def test_create_attributes():
    """Test init with attributes"""
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
        mock_response.json.return_value = {"type": "Integer"}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = client.types()

        assert result == {"type": "Integer"}


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


def test_generate():
    client = empty_client()
    with patch("requests.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = [{"mock_key": "mock_value"}]
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = client.generate(schema="Person", count=1, fmt="json")

        assert result == [{"mock_key": "mock_value"}]


@pytest.mark.parametrize(
    "endpoint, params, expected_url",
    [
        (
            GENERATE_ENDPOINT,
            {"count": 5, "fmt": "json"},
            "https://api.mockaroo.com/api/generate.json?count=5&client=python&key=api_key",
        ),
        (
            TYPE_ENDPOINT,
            {},
            "https://api.mockaroo.com/api/types/?client=python&key=api_key&count=None",
        ),
        (
            UPLOAD_ENDPOINT,
            {"name": "test_name"},
            "https://api.mockaroo.com/api/datasets/test_name?client=python&key=api_key&count=None",
        ),
    ],
)
def test_get_url(endpoint, expected_url, params):
    client = Client(api_key="api_key")
    url = client._get_url(endpoint, **params)
    assert url == expected_url
