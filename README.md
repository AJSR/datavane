# datavane

A Python library for automatically generating documentation from datasets.

`datavane` inspects JSON and CSV datasets, infers their structure and generates a Markdown data dictionary containing information about fields, types, examples, presence and null values.

## Features

* Support for JSON and CSV files.
* Recursive processing of nested dictionaries and lists.
* Automatic field type inference.
* Field path notation for nested structures.
* Example values for detected fields.
* Field presence and null-value statistics.
* Recursive discovery of JSON and CSV files inside directories.
* Markdown documentation generation.
* No external runtime dependencies.

## Installation

Install Datavane from PyPI:

```bash
pip install datavane
```

Once installed, you can import it directly in your Python project:

```python
from datavane import doc_table
```


## Usage

The main public API is `doc_table()`:

```python
from pathlib import Path

from data_dictionary import doc_table

doc_table(
    Path("data/matches.json"),
    "Matches",
    Path("docs/matches.md"),
)
```

The function accepts either a JSON/CSV file or a directory containing supported datasets.

For example, given a dataset containing:

```json
{
    "id": 1,
    "name": "Juan",
    "address": {
        "city": "Málaga"
    }
}
```

the generated documentation can identify fields such as:

```text
id
name
address
address.city
```

along with their inferred types, examples and statistics.

## Generated documentation

The generated Markdown document contains a summary followed by the inferred schema:

```markdown
# Matches

> Data dictionary generated automatically by `datavane`.

## Dataset summary

| Property | Value |
|----------|-------|
| Records  | 100   |
| Fields   | 8     |

## Schema

| Field | Type | Example | Presence | Nulls |
|---|---|---|---|---|
| id | int | 1 | 100.0% | 0.0% |
| name | str | John | 100.0% | 0.0% |
| address.city | str | Madrid | 98.0% | 0.0% |
```

## Project structure

```text
data-dictionary/
├── src/
│   └── data_dictionary/
│       ├── __init__.py
│       ├── models.py
│       ├── inference.py
│       ├── formatting.py
│       ├── io.py
│       └── generator.py
├── tests/
│   ├── fixtures/
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── README.md
└── LICENSE
```

## Development

Create a virtual environment and install the project in editable mode:

```bash
python -m venv .venv
python -m pip install -e .
```

Run the test suite with:

```bash
pytest
```

The project contains both unit and integration tests.

## Status

This project is currently in early development. The public API and internal implementation may change as the library evolves.

## License

This project is licensed under the MIT License.
