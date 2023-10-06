import pytest

from pathlib import Path
from unittest.mock import patch, Mock
from mockaroo.client import (
    Client,
    ApiKeyNotFound,
)


def test_init():
    with patch.dict("os.environ", {"API_KEY": "test_api_key"}):
        client = Client()
        assert client.api_key == "test_api_key"


def test_no_api_key():
    with pytest.raises(ApiKeyNotFound):
        Client(api_key="some_key")


@patch("requests.get")
def test_types(mocked_get):
    mocked_get.return_value = Mock(status_code=200, json=lambda: {"type1": "desc1"})
    client = Client()
    types = client.types()
    assert types == {"type1": "desc1"}


@patch("requests.post")
def test_upload(mocked_post):
    mocked_post.return_value = Mock(status_code=200, json=lambda: {"success": True})
    client = Client()
    result = client.upload("name", Path("tests/samples/test.csv"))
    assert result == {"success": True}


@patch("requests.delete")
def test_delete(mocked_delete):
    mocked_delete.return_value = Mock(status_code=200, json=lambda: {"success": True})
    client = Client()
    result = client.delete("name")
    assert result == {"success": True}


@patch("requests.post")
def test_generate(mocked_post):
    mocked_post.return_value = Mock(status_code=200, json=lambda: [{"id": 1}])
    client = Client()
    data = client.generate(count=1, fields=[{"name": "id", "type": "Number"}])
    assert data == [{"id": 1}]
