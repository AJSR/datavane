import json
from csv import DictReader
from pathlib import Path

SUPPORTED_EXTENSIONS = {".json", ".csv"}


def load_csv(file_path: Path) -> list[dict]:
    """Load records from a CSV file.

    The first row of the CSV file is used as the field names.

    Args:
        file_path (Path): Path to the CSV file.

    Returns:
        list[dict]: A list of dictionaries containing the CSV records.
    """
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = DictReader(csvfile)
        return list(reader)


def load_json(file_path: Path) -> list[dict]:
    """Load records from a JSON file.

    Args:
        file_path (Path): Path to the JSON file.

    Returns:
        list[dict]: The records contained in the JSON file.
    """
    with open(file_path, encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)

    return data


def load_dataset(path: Path) -> list[dict]:
    """Load a dataset from a file or directory.

    JSON and CSV files are supported. When a directory is provided,
    supported files are searched recursively and their records are
    combined into a single dataset.

    Args:
        path (Path): Path to a JSON/CSV file or a directory containing them.

    Raises:
        ValueError: If a file has an unsupported extension.
        FileNotFoundError: If the provided path does not exist or is neither a file 
        nor a directory.

    Returns:
        list[dict]: A list of dictionaries containing the dataset records.
    """

    if path.is_file():
        if path.suffix.lower() == ".json":
            return load_json(path)
        elif path.suffix.lower() == ".csv":
            return load_csv(path)
        else:
            raise ValueError(
                f"File path {path} not supported. File extension must be .csv or .json"
            )
    elif path.is_dir():
        data = []
        for file in path.rglob("*"):
            if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            if file.suffix.lower() == ".json":
                data.extend(load_json(file))
            elif file.suffix.lower() == ".csv":
                data.extend(load_csv(file))
        return data
    else:
        raise FileNotFoundError(f"The path {path} doesn't exist")
