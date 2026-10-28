from io import StringIO
from pathlib import Path

import pytest

from datavane import formatting
from datavane.models import (
    FieldInfo,
    FileError,
    InferredStructure,
    InferredType,
    ProcessingSummary,
)


def test_format_types():
    assert (
        formatting.format_types(
            {InferredType.INT, InferredType.STR, InferredType.FLOAT}
        )
        == "float, int, str"
    )


def test_format_single_type():
    assert formatting.format_types({InferredType.INT}) == "int"


def test_format_types_empty():
    assert formatting.format_types(set()) == ""


def test_format_presence_all_records():
    field = FieldInfo(name="name", appearances=8, context_count=8)

    assert formatting.format_presence(field) == "100.0%"


def test_format_presence_half_records():
    field = FieldInfo(name="name", appearances=4, context_count=8)

    assert formatting.format_presence(field) == "50.0%"


def test_format_presence_no_records():
    field = FieldInfo(name="name", appearances=0, context_count=8)

    assert formatting.format_presence(field) == "0.0%"


def test_format_presence_decimal():
    field = FieldInfo(name="name", appearances=1, context_count=3)

    assert formatting.format_presence(field) == "33.3%"


def test_format_nulls_no_nulls():
    field = FieldInfo(name="name", appearances=8, null_count=0, context_count=8)

    assert formatting.format_nulls(field) == "0.0%"


def test_format_nulls_all_nulls():
    field = FieldInfo(name="name", appearances=8, null_count=8, context_count=8)

    assert formatting.format_nulls(field) == "100.0%"


def test_format_nulls_half_nulls():
    field = FieldInfo(name="name", appearances=8, null_count=4, context_count=8)

    assert formatting.format_nulls(field) == "50.0%"


def test_format_nulls_decimal():
    field = FieldInfo(name="name", appearances=8, null_count=1, context_count=8)

    assert formatting.format_nulls(field) == "12.5%"


def test_format_example_none():
    assert formatting.format_example(None) == "null"


def test_format_example_string():
    assert formatting.format_example("Juan Gámez") == "Juan Gámez"


def test_format_example_long_string():
    value = "a" * 100

    result = formatting.format_example(value)

    assert result.endswith("...")
    assert len(result) == formatting.MAX_STRING_LENGTH + 3


def test_format_example_dict():
    value = {
        "id": 1,
        "name": "Juan",
        "age": 33,
    }

    result = formatting.format_example(value)

    assert "id" in result
    assert "name" in result
    assert "age" in result


def test_format_example_large_dict():
    value = {
        "field1": 1,
        "field2": 2,
        "field3": 3,
        "field4": 4,
        "field5": 5,
        "field6": 6,
        "field7": 7,
    }

    result = formatting.format_example(value)

    assert "field1" in result
    assert "field5" in result
    assert "field6" not in result


def test_format_example_list():
    value = ["a", "b", "c"]

    result = formatting.format_example(value)

    assert "a" in result
    assert "b" in result
    assert "c" in result


def test_format_example_large_list():
    value = ["a", "b", "c", "d", "e"]

    result = formatting.format_example(value)

    assert "a" in result
    assert "b" in result
    assert "c" in result
    assert "d" not in result
    assert "e" not in result


def test_markdown_row():
    field = FieldInfo(
        name="id",
        types={InferredType.INT},
        example=1,
        appearances=8,
        null_count=0,
        context_count=8,
    )

    result = formatting.markdown_row(field)

    expected = "| id | int | 1 | 100.0% | 0.0% |\n"

    assert result == expected


def test_markdown_row_with_nulls():
    field = FieldInfo(
        name="name",
        types={InferredType.STR, InferredType.UNKNOWN},
        example="Ana",
        appearances=8,
        null_count=2,
        context_count=8,
    )

    result = formatting.markdown_row(field)

    expected = "| name | str, unknown | Ana | 100.0% | 25.0% |\n"

    assert result == expected


def test_markdown_table():
    fields = {
        "id": FieldInfo(
            name="id",
            types={InferredType.INT},
            example=1,
            appearances=8,
            null_count=0,
            context_count=8,
        ),
        "name": FieldInfo(
            name="name",
            types={InferredType.STR},
            example="Ana",
            appearances=8,
            null_count=0,
            context_count=8,
        ),
    }

    file = StringIO()

    formatting.markdown_table(fields, file)

    result = file.getvalue()

    expected = (
        "## Schema \n"
        "| Field | Type | Example | Presence (%) | Nulls (%) |\n"
        "|-------|------|---------|--------------|-----------|\n"
        "\n"
        "Presence is the percentage of parent contexts in which a field "
        "appears. Nulls is the percentage of observed field values that "
        "are null. Percentages are shown as N/A when their denominator is zero.\n\n"
        "| id | int | 1 | 100.0% | 0.0% |\n"
        "| name | str | Ana | 100.0% | 0.0% |\n"
    )

    assert result == expected


def test_markdown_table_preserves_field_order():
    fields = {
        "name": FieldInfo(
            name="name",
            types={InferredType.STR},
            example="Ana",
            appearances=8,
            null_count=0,
            context_count=8,
        ),
        "id": FieldInfo(
            name="id",
            types={InferredType.INT},
            example=1,
            appearances=8,
            null_count=0,
            context_count=8,
        ),
    }

    file = StringIO()

    formatting.markdown_table(fields, file)

    result = file.getvalue()

    assert result.index("| name |") < result.index("| id |")


@pytest.mark.parametrize(
    (
        "partial",
        "unsupported_files",
        "failed_files",
        "processed_files",
        "expected_sections",
    ),
    [
        (
            False,
            [],
            [],
            2,
            [
                "- No unsupported files.\n",
            ],
        ),
        (
            False,
            ["notes.txt"],
            [],
            2,
            [
                "- Unsupported files: 1\n",
                "### Unsupported files\n",
                "- `notes.txt`\n",
            ],
        ),
        (
            True,
            [],
            [
                FileError(
                    Path("invalid.json"),
                    "JSONDecodeError",
                    "Invalid JSON",
                )
            ],
            1,
            [
                "> This documentation is from a partial set of files "
                "due to the presence of invalid or unsupported files.\n\n",
                "- Failed files: 1\n\n",
                "### Failed files\n",
                "- `invalid.json`\n",
                "Error type: JSONDecodeError\n",
                "Error message: Invalid JSON\n",
            ],
        ),
        (
            True,
            ["notes.txt"],
            [
                FileError(
                    Path("invalid.json"),
                    "JSONDecodeError",
                    "Invalid JSON",
                )
            ],
            1,
            [
                "- Unsupported files: 1\n",
                "### Unsupported files\n",
                "- `notes.txt`\n",
                "### Failed files\n",
                "- `invalid.json`\n",
            ],
        ),
    ],
)
def test_format_summary(
    partial,
    unsupported_files,
    failed_files,
    processed_files,
    expected_sections,
):
    file = StringIO()
    summary = ProcessingSummary(
        supported_files=2,
        unsupported_files=unsupported_files,
        processed_files=processed_files,
        failed_files=failed_files,
        partial=partial,
    )

    formatting.format_summary(
        "Users",
        6,
        8,
        file,
        summary,
    )

    result = file.getvalue()

    assert result.startswith("# Users \n")
    assert "> Data dictionary generated automatically by `datavane`\n\n" in result
    assert "## Processing Summary\n" in result
    assert "- Files found: " in result
    assert "- Supported files: 2\n" in result
    assert f"- Successfully processed: {processed_files}\n" in result
    assert "## Dataset summary\n" in result
    assert "| Records | 8 |\n" in result
    assert "| Fields  | 6 |\n" in result

    if partial:
        assert (
            "> This documentation is from a partial set of files "
            "due to the presence of invalid or unsupported files.\n\n"
            "> Data dictionary generated automatically by `datavane`\n\n"
        ) in result

    for section in expected_sections:
        assert section in result

    if not failed_files:
        assert "### Failed files\n" not in result

    if not unsupported_files:
        assert "### Unsupported files\n" not in result


def test_format_presence_uses_context_count():
    field = FieldInfo(
        name="items[].id",
        appearances=2,
        context_count=3,
    )

    assert formatting.format_presence(field) == "66.7%"


def test_format_presence_with_zero_context_count():
    field = FieldInfo(
        name="items[].id",
        appearances=0,
        context_count=0,
    )

    assert formatting.format_presence(field) == "N/A"


def test_format_nulls_uses_field_appearances():
    field = FieldInfo(
        name="items[].id",
        appearances=4,
        null_count=1,
        context_count=5,
    )

    assert formatting.format_nulls(field) == "25.0%"


def test_format_nulls_with_zero_appearances():
    field = FieldInfo(
        name="items[].id",
        appearances=0,
        null_count=0,
        context_count=0,
    )

    assert formatting.format_nulls(field) == "N/A"


def test_format_field_types_scalar_and_structure():
    field = FieldInfo(
        name="profile",
        types={InferredType.STR},
        structures={InferredStructure.OBJECT},
    )

    assert formatting.format_field_types(field) == "object, str"


def test_format_field_types_array():
    field = FieldInfo(
        name="orders",
        structures={InferredStructure.ARRAY},
    )

    assert formatting.format_field_types(field) == "array"


def test_format_field_types_empty():
    field = FieldInfo(name="unknown_field")

    assert formatting.format_field_types(field) == ""
