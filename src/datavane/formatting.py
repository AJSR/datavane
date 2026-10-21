from .models import FieldInfo, InferredType

MAX_DICT_FIELDS = 5
MAX_LIST_FIELDS = 3
MAX_STRING_LENGTH = 80


def format_types(types: set[InferredType]) -> str:
    """Format a set of types as a sorted, comma-separated string.

    Args:
        types: Set containing the inferred types of a field.

    Returns:
        str: A comma-separated string containing the types in sorted order.
    """

    return ", ".join(sorted(type_.value for type_ in types))


def format_field_types(field: FieldInfo) -> str:
    """Format a field's scalar types and JSON structures."""
    types = {type_.value for type_ in field.types}
    types.update(structure.value for structure in field.structures)
    return ", ".join(sorted(types))


def format_presence(field: FieldInfo) -> str:
    """Calculate field presence as a percentage of its parent contexts."""
    if field.context_count == 0:
        return "N/A"

    percentage = (field.appearances / field.context_count) * 100
    return f"{round(percentage, 1)}%"


def format_nulls(field: FieldInfo) -> str:
    """Calculate null values as a percentage of field appearances."""
    if field.appearances == 0:
        return "N/A"

    percentage = (field.null_count / field.appearances) * 100
    return f"{round(percentage, 1)}%"


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
    file.write(f"| Records | {total_records} | \n")
    file.write(f"| Fields  | {total_fields} | \n")


def markdown_row(field: FieldInfo) -> str:
    """Format a field as a Markdown table row."""
    return (
        f"| {field.name} | "
        f"{format_field_types(field)} | "
        f"{format_example(field.example)} | "
        f"{format_presence(field)} | "
        f"{format_nulls(field)} |\n"
    )


def markdown_table(fields_dict: dict[str, FieldInfo], file) -> None:
    """Write the dataset schema as a Markdown table.

    Args:
        fields_dict (dict[str, FieldInfo]): Mapping of field names
        to their inferred information.
        total_records (int): Total number of records in the dataset.
        file: File-like object where the Markdown output is written.
    """

    file.write("## Schema \n")
    file.write("| Field | Type | Example | Presence (%) | Nulls (%) |\n")
    file.write("|-------|------|---------|--------------|-----------|\n")
    file.write(
        "\nPresence is the percentage of parent contexts in which a field appears. "
        "Nulls is the percentage of observed field values that are null."
        " Percentages are shown as N/A when their denominator is zero.\n\n"
    )
    file.writelines(markdown_row(field) for field in fields_dict.values())


def test_format_presence_with_zero_context() -> None:
    # ? A field without context doesn't have presence percentage
    assert format_presence(0, 0) == "N/A"


def test_format_nulls_with_zero_appearances() -> None:
    # ? With no appearances, there isn't a null percentage
    assert format_nulls(0, 0) == "N/A"
