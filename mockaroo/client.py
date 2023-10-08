"""Provides code to interact with the Mockaroo API"""

import os
from typing import Any, Dict, List, Optional, Union, ByteString
from urllib.parse import urlencode

import requests
from requests import Response
from dotenv import load_dotenv

from .constants import TYPE_ENDPOINT, UPLOAD_ENDPOINT, GENERATE_ENDPOINT
from .exceptions import (
    MockarooError,
    ApiKeyNotFound,
    InvalidApiKeyError,
    UsageLimitExceededError,
)

load_dotenv()


class Client:
    """Client for interacting with the Mockaroo API.

    Attributes:
        api_key (Optional[str]): API key for Mockaroo API.
        host (str): Hostname of the API. Default: api.mockaroo.com
        secure (bool): Whether to use HTTPS. Default: True
        port (Optional[int]): Port number to connect to. Default: None
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = "api.mockaroo.com",
        secure: bool = True,
        port: Optional[int] = None,
    ) -> None:
        self.api_key = api_key if api_key else os.environ.get("API_KEY")
        if not self.api_key:
            raise ApiKeyNotFound()
        self.host: str = host
        self.secure: bool = secure
        self.port: Optional[int] = port

    def _convert_error(self, response_data: Dict[str, Any]) -> None:
        """Convert API errors into appropriate exceptions."""
        error = response_data.get("error")
        if error is None:
            raise MockarooError("Unknown error")

        if error == "Invalid API Key":
            raise InvalidApiKeyError()
        elif "limited" in error:
            raise UsageLimitExceededError()
        else:
            raise MockarooError(error)

    def _validate_fields(self, fields: Optional[List[Dict[str, Any]]]) -> None:
        """Validate that each field has 'name' and 'type' keys.

        Args:
            fields (Optional[List[Dict[str, Any]]]): A list of dictionaries representing the fields for data generation. Each dictionary must have a 'name' and 'type'.

        Raises:
            ValueError: Raised if any dictionary in the fields list lacks a 'name' or 'type' key.
        """
        if not fields:
            return
        if not all("name" in field and "type" in field for field in fields):
            raise ValueError("Each field must have a 'name' and 'type'")

    def _get_url(
        self,
        count: int,
        fmt: str,
        schema: Optional[str] = None,
        header: Optional[bool] = None,
        array: Optional[bool] = None,
    ) -> str:
        """Construct the API URL.

        Args:
            count (int): Number of records to generate.
            fmt (str): Format of the generated data (e.g., "json").
            schema (Optional[str], optional): Predefined schema to use.
            header (Optional[bool], optional): Whether to include header.
            array (Optional[bool], optional): Whether the output should be an array.

        Returns:
            str: Fully constructed URL for API request.
        """
        base_url: str = f"{'https' if self.secure else 'http'}://{self.host}"
        if self.port:
            base_url += f":{self.port}"

        params: Dict[str, Union[str, int, bool, None]] = {
            "client": "python",
            "key": self.api_key,
            "count": count,
            "format": fmt,
        }
        if schema:
            params["schema"] = schema
        if header:
            params["header"] = header
        if array:
            params["array"] = array

        return f"{base_url}{GENERATE_ENDPOINT}.{fmt}?{urlencode(params)}"

    def _http_get(self, url: str) -> Response:
        """Perform an HTTP GET request and handle errors.

        Args:
            url (str): The URL to send the GET request to.

        Returns:
            Response: `Response` object containing API reply.
        """
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code != 200:
            self._convert_error(response.json())
        return response

    def _http_post(
        self,
        url: str,
        json_data: Optional[List[Dict[str, Any]]] = None,
        files: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Response:
        """Perform an HTTP POST request and handle errors.

        Args:
            url (str): The URL to send the POST request to.
            json_data (Optional[Dict], optional): JSON payload for the request.
            files (Optional[Dict], optional): Files to upload.
            headers (Optional[Dict], optional): HTTP headers for the request.

        Returns:
            Response: `Response` object containing API reply.
        """
        response = requests.post(url, json=json_data, files=files, headers=headers)
        response.raise_for_status()

        if response.status_code != 200:
            self._convert_error(response.json())
        return response

    def _http_delete(self, url: str) -> Response:
        """Perform an HTTP DELETE request and handle errors.

        Args:
            url (str): The URL to send the DELETE request to.

        Returns:
            Response: `Response` object containing API reply.
        """
        response = requests.delete(url)
        response.raise_for_status()

        if response.status_code != 200:
            self._convert_error(response.json())
        return response

    def types(self) -> dict:
        """Retrieve the types supported by the Mockaroo API.

        Returns:
            dict: A dictionary containing types supported by Mockaroo API.
        """
        url = f"https://{self.host}{TYPE_ENDPOINT}?key={self.api_key}"
        resp = self._http_get(url=url)
        return resp.json()

    def upload(self, name: str, path: str) -> dict:
        """Upload a dataset to Mockaroo.

        Args:
            name (str): Name of the dataset to upload.
            path (str): File path of the dataset to upload.

        Returns:
            dict: Dictionary containing upload status and other metadata.
        """
        url = f"https://{self.host}{UPLOAD_ENDPOINT}{name}?key={self.api_key}"
        with open(path, "rb") as f:
            files = {"file": f}
            resp = self._http_post(
                url=url, files=files, headers={"content-type": "text/csv"}
            )
        return resp.json()

    def delete(self, name: str) -> dict:
        """Delete a dataset from Mockaroo.

        Args:
            name (str): Name of the dataset to delete.

        Returns:
            dict: Dictionary containing delete status and other metadata.
        """
        url = f"https://{self.host}{UPLOAD_ENDPOINT}{name}?key={self.api_key}"
        resp = self._http_delete(url=url)
        return resp.json()

    def generate(
        self,
        count: int = 1,
        fmt: str = "json",
        schema: Optional[str] = None,
        header: bool = True,
        array: bool = False,
        fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], ByteString]:
        """Generate mock data using the Mockaroo API.

        Args:
            count (int, optional): Number of records to generate.
            fmt (str, optional): Output format of the generated data.
            schema (Optional[str], optional): Predefined schema to use.
            header (bool, optional): Whether to include header.
            array (bool, optional): Whether the output should be an array.
            fields (Optional[List[Dict[str, Any]]], optional): List of dictionaries specifying the fields for data generation.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]], ByteString]: The generated mock data in the specified format.
        """
        self._validate_fields(fields)
        url = self._get_url(count, fmt, schema, header, array)

        response = self._http_post(url=url, json_data=fields)
        response.raise_for_status()

        if response.status_code != 200:
            self._convert_error(response.json())

        return response.json() if fmt == "json" else response.content
