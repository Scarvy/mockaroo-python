"""Provides code to interact with the Mockaroo API."""

import os
import warnings
from typing import Any, ByteString, Dict, List, Optional, Union
from urllib.parse import quote, urlencode

import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException

from .exceptions import (
    InvalidApiKeyError,
    MockarooError,
    UsageLimitExceededError,
)

load_dotenv()


class Client:
    """Client for interacting with the Mockaroo API.

    Attributes:
        api_key (Optional[str]): API key for the Mockaroo API.
        host (str): Hostname of the API. Default: api.mockaroo.com
        secure (bool): Whether to use HTTPS. Default: True
        port (Optional[int]): Port number to connect to. Default: None.

    """

    TYPE_ENDPOINT = "/api/types/"
    UPLOAD_ENDPOINT = "/api/datasets/"
    GENERATE_ENDPOINT = "/api/generate"

    HTTP_GET = "GET"
    HTTP_POST = "POST"
    HTTP_DELETE = "DELETE"

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = "api.mockaroo.com",
        secure: bool = True,
        port: Optional[int] = None,
    ) -> None:
        """Initializes the instance based on predefined arguments.

        Args:
            api_key (Optional[str], optional): API key for Mockaroo API.
            host (str): Hostname of the API. Default: api.mockaroo.com
            secure (bool): Whether to use HTTPS. Default: True
            port (Optional[int], optional): Port number to connect to. Default: None.
        """
        self._api_key = api_key
        self.host: str = host
        self.secure: bool = secure
        self.port: Optional[int] = port

        self.last_request: Optional[Dict[str, Any]] = None

    @property
    def api_key(self):
        """Set API key."""
        if not self._api_key:
            self._api_key = os.environ.get("MOCKAROO_API_KEY")
            if not self._api_key:
                warnings.warn(
                    "API key is not provided. "
                    "Set MOCKAROO_API_KEY `export MOCKAROO_API_KEY=your_api_key`."
                )
        return self._api_key

    def _convert_error(self, response_data: Dict[str, Any]) -> None:
        """Convert API errors into appropriate exceptions.

        Args:
            response_data (Dict[str, Any]): A request response error message.

        Raises:
            exception_cls: A Mockaroo exception.
        """
        error = response_data.get("error", "Unknown error")
        exception_mapping = {
            "Invalid API Key": InvalidApiKeyError,
            "Usage Limit Exceeded": UsageLimitExceededError,
        }
        exception_cls = exception_mapping.get(error, MockarooError)
        raise exception_cls(error)

    def _validate_fields(self, fields: List[Dict[str, Any]]) -> None:
        """Validate that each field has 'name' and 'type' keys.

        Args:
            fields (List[Dict[str, Any]]): A list of dictionaries
            representing the fields for data generation.

        Raises:
            ValueError: If any dictionary lacks a 'name' or 'type' key.
        """
        for idx, field in enumerate(fields):
            if not all(k in field for k in ["name", "type"]):
                raise ValueError(f"Field at index {idx} must have a 'name' and 'type'")

    def _get_url(  # noqa: D417
        self,
        endpoint: str,
        **params,
    ) -> str:
        """Construct the API URL.

        Args:
            endpoint (str): Mockaroo API endpoint to use.

        Keyword Args:
            count (int): Number of records to generate. Defaults to 1.
            fmt (str): Format of the generated data. Defaults to "json".
            schema (str): Predefined schema to use.
            name (str): Name for the dataset to use.
            header (str): Whether to include header.
            array (str): Whether the output should be an array.

        Returns:
            str: Fully constructed URL for API request.
        """
        scheme = "https" if self.secure else "http"
        base_url: str = f"{scheme}://{self.host}"

        if self.port:
            base_url += f":{self.port}"

        params["client"] = "python"
        params["key"] = self.api_key

        # for generate requests. Add format type to URL.
        fmt = params.pop("fmt", None)
        if fmt:
            endpoint = f"{endpoint}.{fmt}"  # Example: api/generate.json?

        # name of dataset to upload (POST) or DELETE.
        name = params.pop("name", None)
        if name:
            endpoint = (
                f"{endpoint}{quote(name)}"  # Example: api/upload/name%20of%20dataset?
            )

        return f"{base_url}{endpoint}?{urlencode(params)}"

    def _http_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Perform an HTTP request and return a requests.Response object.

        Args:
            method (str): The HTTP method to use (e.g., 'GET', 'POST').
            url (str): The URL to which the request is sent.
            **kwargs: Additional keyword arguments to pass to `requests.request`.

        Returns:
            requests.Response: The response object containing details of the HTTP response.

        Raises:
            Exception: If the HTTP request fails for any reason or if the status code is not 200.

        Side Effects:
            Updates the `last_request` instance variable with details about the request and its outcome.
        """  # noqa: E501
        self.last_request = {
            "method": method,
            "url": url,
            "request": kwargs,
            "error": None,
        }
        try:
            resp = requests.request(method, url, **kwargs)
            self.last_request["response"] = resp.text
        except RequestException as e:
            self.last_request["error"] = str(e)
            raise

        if resp.status_code != 200:
            self._convert_error(resp.json())
        return resp

    def types(self) -> List[Dict[str, Any]]:
        """Retrieve the types supported by the Mockaroo API.

        Returns:
            dict: A list of dictionaries containing types supported by Mockaroo.
        """
        url = self._get_url(self.TYPE_ENDPOINT)
        json_resp = self._http_request(self.HTTP_GET, url=url).json()
        return json_resp["types"]

    def upload(self, name: str, path: str) -> Dict[str, Any]:
        """Upload a dataset to Mockaroo.

        Args:
            name (str): Name of the dataset to upload.
            path (str): File path of the dataset to upload.

        Returns:
            dict: Dictionary containing upload status and other metadata.
        """
        url = self._get_url(self.UPLOAD_ENDPOINT, name=name)
        with open(path, "rb") as f:
            file_content = f.read()
            return self._http_request(
                self.HTTP_POST,
                url=url,
                headers={"content-type": "text/csv"},
                data=file_content,
            ).json()

    def delete(self, name: str) -> Dict[str, Any]:
        """Delete a dataset from Mockaroo.

        Args:
            name (str): Name of the dataset to delete.

        Returns:
            dict: Dictionary containing delete status and other metadata.
        """
        url = self._get_url(self.UPLOAD_ENDPOINT, name=name)
        return self._http_request(self.HTTP_DELETE, url=url).json()

    def generate(  # noqa: D417
        self,
        **kwargs,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], ByteString]:
        """Generate mock data using the Mockaroo API.

        Args:
            array (bool, optional): Control JSON output type based on 'count'. Defaults to false.
            bom (bool, optional): Include BOM when format is csv, txt, or custom. Defaults to false.
            background (bool, optional): Whether to generate data in the background. Defaults to false.
            callback (str, optional): Javascript function for JSONP response.
            count (int, optional): Number of records to generate. Defaults to 1.
            delimiter (str, optional): Column separator when format is custom.
            fields (List[Dict[str, Any]], optional): Field specifications as JSON array.
            fmt (str, optional): Output format of the generated data. Defaults to "json".
            include_nulls (bool, optional): Include keys with null values in JSON. Defaults to true.
            include_header (bool, optional): Include header row for CSV. Defaults to true.
            line_ending (str, optional): "unix" or "windows" when format is custom.
            quote_char (str, optional): Character for enclosing values, used when format is custom.
            record_element (str, optional): Element name for each record when format is XML.
            root_element (str, optional): Root element name when format is XML.
            schema (str, optional): Name of a saved schema to use.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]], ByteString]: The generated mock data in the specified format.

        Usage:
            >>> from mockaroo import Client
            >>> client = Client()
            >>> data = client.generate(schema="Person") Default: count=1
            >>> data
            {'id': 1, 'first_name': 'Sidnee', 'last_name': 'Attow'}

            >>> from mockaroo import Client
            >>> client = Client()
            >>> data = client.generate(
                    count=2,
                    fields=[
                        {
                            "name": "id",
                            "type": "Row Number"
                        },
                        {
                            "name":"transactionType",
                            "type": "Custom List",
                            "values": ["credit","debit"]
                        }
                    ]
                )
            >>> data
            [
                {'id': 1, 'transactionType': 'credit'},
                {'id': 2, 'transactionType': 'debit'}
            ]
        """  # noqa: E501
        schema = kwargs.get("schema")
        fields = kwargs.get("fields")

        if (schema is None and fields is None) or (
            schema is not None and fields is not None
        ):
            warnings.warn(
                "You should specify either 'schema' or 'fields', "
                "but not both. `schema` will override any values passed"
                "to `fields`."
            )

        if fields:
            self._validate_fields(fields)

        fields = kwargs.pop("fields", None)  # Remove fields from keyword args

        url = self._get_url(self.GENERATE_ENDPOINT, **kwargs)
        response = self._http_request(self.HTTP_POST, url=url, json=fields)

        return (
            response.json() if kwargs.get("fmt", "json") == "json" else response.content
        )
