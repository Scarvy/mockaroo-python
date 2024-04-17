# mockaroo-python

[![PyPI](https://img.shields.io/pypi/v/mockaroo-python.svg)](https://pypi.org/project/mockaroo-python/)
[![Changelog](https://img.shields.io/github/v/release/Scarvy/mockaroo-python?include_prereleases&label=changelog)](https://github.com/Scarvy/mockaroo-python/releases)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

A Python wrapper for the Mockaroo API 🦘 + 🐍.

## Installation

Install this tool using `pip`:

    pip install mockaroo-python

## Prerequisites

To use this library, you'll need an API key from the [Mockaroo website](https://www.mockaroo.com/docs#Gaining_Access).

Set your key as an environment variable:

```bash
export MOCKAROO_API_KEY=<api_key>
```

or pass it to the `Client` class as an argument:

```python
client = Client(api_key="api_key")
```

## Usage

Use the library in your Python script or from the command-line.

**Command-Line**:

For help, run:

```bash
mockaroo --help
```

You can also use:

```bash
python -m mockaroo --help
```

Generate a dataset:

```bash
mockaroo gen Person # your own schema in Mockaroo

[
    {
        "id": 1,
        "first_name": "Burch",
        "last_name": "Minichi"
    },
    {
        "id": 2,
        "first_name": "Val",
        "last_name": "Curzon"
    },
    {
        "id": 3,
        "first_name": "Poppy",
        "last_name": "Pallant"
    }
]
```

Write data to a file format (JSON, CSV, TXT, XML, or SQL):

```bash
mockaroo gen Person --count 5 >> people.json
```

Upload a file to Mockaroo:

```bash
mockaroo upload customers customers.csv
```

Delete a file:

```bash
mockaroo delete customers
```

Check the available Mockaroo types:

```bash
mockaroo types
```

**Python Script**:

```python
from mockaroo import Client

# Initialize the client with your API key
client = Client(api_key="your_api_key_here")
# Or set an enviornment variable. `export API_KEY=your_api_key_here`
client = Client()

# Fetch available types from Mockaroo
types = client.types()

# Upload a dataset ('csv' or 'txt') to Mockaroo
client.upload(name="name_of_dataset", path="/path/to/file.csv")

# Remove a dataset from Mockaroo
client.delete(name="name_of_dataset")

# Generate data using a predefined schema
data = client.generate(schema="name_of_schema")

# Alternatively, specify fields to generate custom data
data = client.generate(
    fields=[
        {"name": "city", "type": "City"},
        {"name": "street_name", "type": "Street Name"}
    ]
)
```

## Ways to Generate Mockaroo Datasets

### Using Predefined Schemas

To generate data based on a schema you've created, specify the schema name as an argument.

**Example:**

```python
from mockaroo import Client

client = Client()

data = client.generate(schema="Person")

print(data)
{'id': 1, 'first_name': 'Patrizius', 'last_name': 'Van'}
```

### Using Custom Fields

Pass a list of field definitions to generate mock data with custom fields. For a full list of available types, see the [Official API Reference Page](https://www.mockaroo.com/docs#Types).

**Example**:

```python
result = client.generate(
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
print(result)
[{'id': 1, 'transactionType': 'credit'}, {'id': 2, 'transactionType': 'debit'}]
```

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd mockaroo-python
    poetry install

Now install the dependencies and test dependencies:

    poetry install --with dev

To run the tests:

    pytest
