import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()

TYPE_ENDPOINT = "/api/types/"
UPLOAD_ENDPOINT = "/api/datasets/"
GENERATE_ENDPOINT = "/api/generate"

# TODO handle different data output


class MockarooError(Exception):
    pass


class ApiKeyNotFound(MockarooError):
    def __init__(self):
        self.msg = "API key is required. Export API_KEY=mockaroo_api_key"

    def __call__(self):
        print(self.msg)


class InvalidApiKeyError(MockarooError):
    pass


class UsageLimitExceededError(MockarooError):
    pass


class Client:
    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = "api.mockaroo.com",
        secure: bool = True,
        port: Optional[int] = None,
    ) -> None:
        if not api_key:
            self.api_key = os.environ["API_KEY"]
        else:
            raise ApiKeyNotFound()
        self.host: str = host
        self.secure: bool = secure
        self.port: Optional[int] = port

    def _convert_error(self, response_data: Dict[str, Any]) -> None:
        error = response_data.get("error")
        if error == "Invalid API Key":
            raise InvalidApiKeyError()
        elif "limited" in error:
            raise UsageLimitExceededError()
        else:
            raise MockarooError(error)

    def _validate_fields(self, fields: Optional[List[Dict[str, Any]]]) -> None:
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
        base_url: str = f"{'https' if self.secure else 'http'}://{self.host}"
        if self.port:
            base_url += f":{self.port}"

        params: Dict[str, Union[str, int, bool]] = {
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

        return f"{base_url}/api/generate.{fmt}?{urlencode(params)}"

    def types(self) -> dict:
        url = f"https://{self.host}{TYPE_ENDPOINT}?key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code != 200:
            self._convert_error(response.json())

        return response.json()

    def upload(self, name: str, path: str) -> dict:
        url = f"https://{self.host}{UPLOAD_ENDPOINT}{name}?key={self.api_key}"
        with open(path, "rb") as f:
            files = {"file": f}
            resp = requests.post(url, files=files, headers={"content-type": "text/csv"})
        return resp.json()

    def delete(self, name: str):
        url = f"https://{self.host}{UPLOAD_ENDPOINT}{name}?key={self.api_key}"
        resp = requests.delete(url)
        return resp.json()

    def generate(
        self,
        count: int = 1,
        fmt: str = "json",
        schema: Optional[str] = None,
        header: bool = True,
        array: bool = False,
        fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        self._validate_fields(fields)
        url = self._get_url(count, fmt, schema, header, array)
        response = requests.post(url, json=fields)
        response.raise_for_status()

        if response.status_code != 200:
            self._convert_error(response.json())

        if fmt == "json":
            return response.json()
        return response
