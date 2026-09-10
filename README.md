# Datavane

[![Tests](https://github.com/AJSR/datavane/actions/workflows/tests.yml/badge.svg)](https://github.com/AJSR/datavane/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/datavane.svg)](https://pypi.org/project/datavane/)
[![Python](https://img.shields.io/pypi/pyversions/datavane.svg)](https://pypi.org/project/datavane/)
[![License](https://img.shields.io/github/license/AJSR/datavane.svg)](https://github.com/AJSR/datavane/blob/main/LICENSE)

A Python library for automatically generating documentation from datasets.

Datavane inspects JSON and CSV datasets, infers their structure and generates a Markdown data dictionary containing information about fields, types, examples, presence and null values.

The project is designed primarily for **small data projects and simple data-processing workflows**, but it can also be used as a standalone utility wherever automatic dataset documentation is useful.

[GitHub](https://github.com/AJSR/datavane) · [PyPI](https://pypi.org/project/datavane/)

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

Then import the public API directly:

```python
from datavane import doc_table
```

## Usage

The main public API is `doc_table()`:

```python
from pathlib import Path

from datavane import doc_table

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

Datavane can identify fields such as:

```text
id
name
address
address.city
```

along with their inferred types, examples and statistics.

## Generated documentation

The generated Markdown document contains a dataset summary followed by the inferred schema:

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
datavane/
├── src/
│   └── datavane/
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
├── poetry.lock
├── README.md
└── LICENSE
```

## Development

Datavane uses Poetry for dependency management and packaging.

Install the project and its development dependencies with:

```bash
poetry install
```

Run the test suite with:

```bash
poetry run pytest
```

Run Ruff:

```bash
poetry run ruff check .
poetry run ruff format --check .
```

Build the package with:

```bash
poetry build
```

The project contains both unit and integration tests and uses GitHub Actions for continuous integration.

## Project status

Datavane is currently in an early stage of development.

Version `0.1.0` is the first public release. The current functionality focuses on automatic documentation of small datasets using JSON and CSV files.

The project is intentionally being developed incrementally, with future versions expected to expand its dataset profiling and analysis capabilities.

## Why Datavane?

Datavane started as a project-specific utility for inspecting datasets in a football data project.

As the functionality became more general, the utility was separated from the original project and developed into an independent Python package.

This project is also part of my software and data engineering portfolio, and is an opportunity to apply software engineering practices such as:

* Modular design
* Unit and integration testing
* Continuous integration
* Code quality and formatting
* Python packaging
* Dependency management
* Versioning and releases
* Distribution through PyPI

## License

This project is licensed under the MIT License.
