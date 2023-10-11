"""Provides code to interact with the Mockaroo API"""
import warnings
import os
from typing import Any, Dict, List, Optional, Union, ByteString
from urllib.parse import urlencode, quote

import requests
from dotenv import load_dotenv

from .constants import (
    TYPE_ENDPOINT,
    UPLOAD_ENDPOINT,
    GENERATE_ENDPOINT,
    HTTP_GET,
    HTTP_POST,
    HTTP_DELETE,
)
from .exceptions import (
    MockarooError,
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
        self._api_key = api_key
        self.host: str = host
        self.secure: bool = secure
        self.port: Optional[int] = port

    @property
    def api_key(self):
        if not self._api_key:
            self._api_key = os.environ.get("API_KEY")
            if not self._api_key:
                warnings.warn(
                    "API key is not provided. Set API_KEY `export API_KEY=your_api_key`."
                )
        return self._api_key

    def _convert_error(self, response_data: Dict[str, Any]) -> None:
        """Convert API errors into appropriate exceptions."""
        error = response_data.get("error", "Unknown error")
        exception_mapping = {
            "Invalid API Key": InvalidApiKeyError,
            "Usage Limit Exceeded": UsageLimitExceededError,
        }
        exception_cls = exception_mapping.get(error, MockarooError)
        raise exception_cls(error)

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
        params["count"] = params.get("count")

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
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        if response.status_code != 200:
            self._convert_error(response.json())
        return response

    def types(self) -> Dict[str, Any]:
        """Retrieve the types supported by the Mockaroo API.

        Returns:
            dict: A dictionary containing types supported by Mockaroo API.
        """
        url = self._get_url(TYPE_ENDPOINT)
        return self._http_request(HTTP_GET, url=url).json()

    def upload(self, name: str, path: str) -> Dict[str, Any]:
        """Upload a dataset to Mockaroo.

        Args:
            name (str): Name of the dataset to upload.
            path (str): File path of the dataset to upload.

        Returns:
            dict: Dictionary containing upload status and other metadata.
        """
        url = self._get_url(UPLOAD_ENDPOINT, name=name)
        with open(path, "rb") as f:
            files = {"file": f}
            return self._http_request(
                HTTP_POST,
                url=url,
                files=files,
                headers={"content-type": "text/csv"},
            ).json()

    def delete(self, name: str) -> Dict[str, Any]:
        """Delete a dataset from Mockaroo.

        Args:
            name (str): Name of the dataset to delete.

        Returns:
            dict: Dictionary containing delete status and other metadata.
        """
        url = self._get_url(UPLOAD_ENDPOINT, name=name)
        return self._http_request(HTTP_DELETE, url=url).json()

    def generate(
        self,
        **kwargs,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], ByteString]:
        """Generate mock data using the Mockaroo API.

        Keyword Args:
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
            [{'id': 1, 'transactionType': 'credit'}, {'id': 2, 'transactionType': 'debit'}]
        """
        schema = kwargs.get("schema")
        fields = kwargs.get("fields")

        if (schema is None and fields is None) or (
            schema is not None and fields is not None
        ):
            warnings.warn(
                "You should specify either 'schema' or 'fields', but not both. `schema` will override any values passed to `fields`."
            )

        if fields:
            self._validate_fields(fields)

        fields = kwargs.pop("fields", None)  # Remove fields from keyword args

        url = self._get_url(GENERATE_ENDPOINT, **kwargs)
        response = self._http_request(HTTP_POST, url=url, json=fields)

        return (
            response.json()
            if kwargs.get("fields", "json") == "json"
            else response.content
        )
