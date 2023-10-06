# Mockaroo API Python Library 🐍 + 🦘

Python Library for the [Mockaroo APIs](https://mockaroo.com/docs).

## Usage

```python
from mockaroo import Client

client = Client(api_key=your_api_key_here)

# Get mockaroo data types
types = client.types()

# upload dataset to mockaroo website
client.upload(name="name_of_dataset", path"/path/to/my_file.csv")

# delete dataset from mockaroo website
client.delete(name="name_of_dataset")

# generate datasets
data = client.generate(schema="name_of_schema")  # Default:
```

## Generate Dataset

```python
from mockaroo import Client
client = Client()
data = client.generate(schema="Person")
print(data)
{'id': 1, 'first_name': 'Patrizius', 'last_name': 'Van'}
```
