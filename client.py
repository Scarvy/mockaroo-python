import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.mockaroo.com"
TYPE_ENDPOINT = "/api/types/"
UPLOAD_DATASET_ENDPOINT = "/api/datasets/"
GENERATE_DATASET_ENDPOINT = "/api/generate"

# TODO fix generate dataset from schema func not returning anything


def _get_mockaroo(url: str) -> dict:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def get_api_key():
    try:
        return os.environ["API_KEY"]
    except:
        raise KeyError("API Key does not exist.")


def get_types(api_key: str) -> dict:
    return _get_mockaroo(f"{BASE_URL}{TYPE_ENDPOINT}?key={api_key}")


def upload_dataset(api_key: str, name: str, path: str) -> dict:
    url = f"{BASE_URL}{UPLOAD_DATASET_ENDPOINT}{name}?key={api_key}"
    with open(path, "rb") as f:
        files = {"file": f}
        resp = requests.post(url, files=files, headers={"content-type": "text/csv"})
    return resp.json()


def delete_dataset(api_key: str, name: str):
    url = f"{BASE_URL}{UPLOAD_DATASET_ENDPOINT}{name}?key={api_key}"
    resp = requests.delete(url)
    return resp.json()


def generate_dataset_from_schema(
    api_key: str,
    dataset_format: str,
    schema_name: str,
):
    # url = f"{BASE_URL}{GENERATE_DATASET_ENDPOINT}.{dataset_format}?key={api_key}"
    # resp = requests.post(url, params={"schema": schema_name})
    # return resp
    ...


if __name__ == "__main__":
    api_key = get_api_key()

    types = get_types(api_key=api_key)
    print(types)

    result = upload_dataset(api_key=api_key, name="test_dataset", path="test.csv")
    print(result)

    result = delete_dataset(api_key=api_key, name="test_dataset")
    print(result)

    # result = generate_dataset_from_schema(
    #     api_key=api_key, dataset_format="csv", schema_name="Person"
    # )
