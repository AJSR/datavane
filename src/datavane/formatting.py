from .models import FieldInfo

MAX_DICT_FIELDS = 5
MAX_LIST_FIELDS = 3
MAX_STRING_LENGTH = 80


def format_types(types: set[str]) -> str:
    """Format a set of types as a sorted, comma-separated string.

    Args:
        types (set[str]): Set containing the inferred types of a field.

    Returns:
        str: A comma-separated string containing the types in sorted order.
    """

    return ", ".join(sorted(types))


def format_presence(field: FieldInfo, total_records: int) -> str:
    """Calculate and format the percentage of records containing a field.

    Args:
        field (FieldInfo): Field information containing the number of appearances.
        total_records (int): Total number of records in the dataset.

    Returns:
        str: The field presence as a percentage string.
    """

    return str(round((field.appearances / total_records) * 100, 1)) + "%"


def format_nulls(field: FieldInfo, total_records: int) -> str:
    """Calculate and format the percentage of null values for a field.

    Args:
        field (FieldInfo): Field information containing the number of null values.
        total_records (int): Total number of records in the dataset.

    Returns:
        str: The null value percentage as a string.
    """

    return str(round((field.null_count / total_records) * 100, 1)) + "%"


def format_example(example) -> str:
    """Format an example value for inclusion in the Markdown output.

    Strings longer than ``MAX_STRING_LENGTH`` are truncated. Dictionaries
    and lists are recursively formatted and limited to the configured
    number of elements.

    Args:
        example: Example value to format.

    Returns:
        str: A string representation suitable for the generated documentation.
    """

    if example is None:
        return "null"

    if isinstance(example, str):
        if len(example) > MAX_STRING_LENGTH:
            return example[:MAX_STRING_LENGTH] + "..."
        return example

    if isinstance(example, dict):
        examples_list = []

        for i, (key, value) in enumerate(example.items()):
            if i >= MAX_DICT_FIELDS:
                examples_list.append("...")
                break

            examples_list.append(f"{key}: {format_example(value)}")

        return "{ " + ", ".join(examples_list) + " }"

    if isinstance(example, list):
        examples_list = []

        for i, entry in enumerate(example):
            if i >= MAX_LIST_FIELDS:
                examples_list.append("...")
                break

            examples_list.append(format_example(entry))

        return "[ " + ", ".join(examples_list) + " ]"

    return str(example)


def format_summary(
    table_name: str, total_fields: int, total_records: int, file
) -> None:
    """Write the dataset summary section to a file.

    Args:
        table_name (str): Name of the dataset or table being documented.
        total_fields (int): Number of fields detected in the dataset.
        total_records (int): Number of records in the dataset.
        file: File-like object where the Markdown output is written.
    """

    file.write(f"# {table_name} \n")
    file.write("> Data dictionary generated automatically by `datavane` \n")
    file.write("## Dataset summary \n")
    file.write("| Property | Value | \n")
    file.write("|----------|-------| \n")
    file.write(f"| Records | {total_records}| \n")
    file.write(f"| Fields  | {total_fields} | \n")


def markdown_row(field: FieldInfo, total_records: int) -> str:
    """Format a field as a Markdown table row.

    Args:
        field (FieldInfo): Field information to format.
        total_records (int): Total number of records in the dataset.

    Returns:
        str: A Markdown table row containing the field's type, example, presence,
          and null percentage.
    """

    return (
        f"| {field.name} | "
        f"{format_types(field.types)} | "
        f"{format_example(field.example)} | "
        f"{format_presence(field, total_records)} | "
        f"{format_nulls(field, total_records)} |\n"
    )


def markdown_table(fields_dict: dict[str, FieldInfo], total_records: int, file) -> None:
    """Write the dataset schema as a Markdown table.

    Args:
        fields_dict (dict[str, FieldInfo]): Mapping of field names
        to their inferred information.
        total_records (int): Total number of records in the dataset.
        file: File-like object where the Markdown output is written.
    """

    file.write("## Schema \n")
    file.write("| Field | Type | Example | Presence | Nulls | \n")
    file.write("|-------|------|---------| -------- | ----- |\n")
    file.writelines(
        markdown_row(field, total_records) for field in fields_dict.values()
    )
