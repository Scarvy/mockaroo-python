# Mockaroo API Python Library 🐍 + 🦘

A Python library for the [Mockaroo APIs](https://mockaroo.com/docs). Use this library to generate mock data for testing, simulations, and more.

## Installation

**Install from PyPl**:

```bash
pip install mockaroo-python
```

**Install from the GitHub Repository**:

```bash
pip install git+https://github.com/Scarvy/mockaroo-python.git
```

**Install from Local Source**:

1. Clone the repository:

```bash
git clone https://github.com/Scarvy/mockaroo-python.git
```

2. Navigate to the cloned directory:

```bash
cd mockaroo-python
```

3. Install the package:

```bash
pip install .
```

## Prerequisites

To use this library, you'll need an API key from [Mockaroo website](www.mockaroo.com).

## Usage

Use the library in your script or in the command-line.

**Python Script:**

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

**Command-Line Interface:**

```bash
Usage: python -m mockaroo [OPTIONS] COMMAND [ARGS]...                               
                                                                                     
Interact with the Mockaroo APIs 🦘 + 🐍                                             
                                                                                     
╭─ Options ────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                          │
╰──────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────╮
│ delete          Delete a dataset from Mockaroo                                   │
│ types           Get Mockaroo data types                                          │
│ upload          Upload dataset to Mockaroo                                       │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

```bash
 Usage: python -m mockaroo types [OPTIONS]                                                           
                                                                                                     
 Get Mockaroo data types                                                                             
                                                                                                     
╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│ --pager  -P    Page output.                                                       │
│ --help         Show this message and exit.                                        │
╰───────────────────────────────────────────────────────────────────────────────────╯
```

```bash
 Usage: python -m mockaroo upload [OPTIONS] NAME INPUT_FILE                                   
                                                                                              
 Upload dataset to Mockaroo                                                                   
                                                                                              
╭─ Options ────────────────────────────────────────────────────────────────────────╮
│ *  NAME          TEXT  [required]                                                │
│ *  INPUT_FILE    PATH  [required]                                                │
│    --help              Show this message and exit.                               │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

```bash
 Usage: python -m mockaroo delete [OPTIONS] NAME                                                 
                                                                                                 
 Delete a dataset from Mockaroo                                                                  
                                                                                                 
╭─ Options ────────────────────────────────────────────────────────────────────────╮
│ *  NAME      TEXT  [required]                                                    │
│    --help          Show this message and exit.                                   │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

## Generate Dataset

### Using Predefined Schemas

To generate data based on a schema you've created on Mockaroo's website, specify the schema name as an argument.

**Example:**

```python
from mockaroo import Client
client = Client()
data = client.generate(schema="Person")
print(data)
{'id': 1, 'first_name': 'Patrizius', 'last_name': 'Van'}
```

### Using Custom Fields

Pass a list of field definitions to generate data with custom fields. For a full list of available types, see the, see [API Reference](https://www.mockaroo.com/docs#Types).

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

### Mockaroo Types

![table_layout](/images/table_layout.svg)
