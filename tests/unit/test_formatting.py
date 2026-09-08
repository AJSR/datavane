from io import StringIO

from datavane import formatting
from datavane.models import FieldInfo


def test_format_types():
    assert formatting.format_types({"int", "str", "float"}) == "float, int, str"


def test_format_single_type():
    assert formatting.format_types({"int"}) == "int"


def test_format_types_empty():
    assert formatting.format_types(set()) == ""


def test_format_presence_all_records():
    field = FieldInfo(name="name", appearances=8, context_count=8)

    assert formatting.format_presence(field, 8) == "100.0%"


def test_format_presence_half_records():
    field = FieldInfo(name="name", appearances=4, context_count=8)

    assert formatting.format_presence(field, 8) == "50.0%"


def test_format_presence_no_records():
    field = FieldInfo(name="name", appearances=0, context_count=8)

    assert formatting.format_presence(field, 8) == "0.0%"


def test_format_presence_decimal():
    field = FieldInfo(name="name", appearances=1, context_count=3)

    assert formatting.format_presence(field, 3) == "33.3%"


def test_format_nulls_no_nulls():
    field = FieldInfo(name="name", appearances=8, null_count=0, context_count=8)

    assert formatting.format_nulls(field, 8) == "0.0%"


def test_format_nulls_all_nulls():
    field = FieldInfo(name="name", appearances=8, null_count=8, context_count=8)

    assert formatting.format_nulls(field, 8) == "100.0%"


def test_format_nulls_half_nulls():
    field = FieldInfo(name="name", appearances=8, null_count=4, context_count=8)

    assert formatting.format_nulls(field, 8) == "50.0%"


def test_format_nulls_decimal():
    field = FieldInfo(name="name", appearances=8, null_count=1, context_count=8)

    assert formatting.format_nulls(field, 8) == "12.5%"


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
        types={"int"},
        example=1,
        appearances=8,
        null_count=0,
        context_count=8,
    )

    result = formatting.markdown_row(field, 8)

    expected = "| id | int | 1 | 100.0% | 0.0% |\n"

    assert result == expected


def test_markdown_row_with_nulls():
    field = FieldInfo(
        name="name",
        types={"str", "null"},
        example="Ana",
        appearances=8,
        null_count=2,
        context_count=8,
    )

    result = formatting.markdown_row(field, 8)

    expected = "| name | null, str | Ana | 100.0% | 25.0% |\n"

    assert result == expected


def test_markdown_table():
    fields = {
        "id": FieldInfo(
            name="id",
            types={"int"},
            example=1,
            appearances=8,
            null_count=0,
            context_count=8,
        ),
        "name": FieldInfo(
            name="name",
            types={"str"},
            example="Ana",
            appearances=8,
            null_count=0,
            context_count=8,
        ),
    }

    file = StringIO()

    formatting.markdown_table(fields, 8, file)

    result = file.getvalue()

    expected = (
        "## Schema \n"
        "| Field | Type | Example | Presence | Nulls | \n"
        "|-------|------|---------| -------- | ----- |\n"
        "| id | int | 1 | 100.0% | 0.0% |\n"
        "| name | str | Ana | 100.0% | 0.0% |\n"
    )

    assert result == expected


def test_markdown_table_preserves_field_order():
    fields = {
        "name": FieldInfo(
            name="name",
            types={"str"},
            example="Ana",
            appearances=8,
            null_count=0,
            context_count=8,
        ),
        "id": FieldInfo(
            name="id",
            types={"int"},
            example=1,
            appearances=8,
            null_count=0,
            context_count=8,
        ),
    }

    file = StringIO()

    formatting.markdown_table(fields, 8, file)

    result = file.getvalue()

    assert result.index("| name |") < result.index("| id |")


def test_format_summary():
    file = StringIO()

    formatting.format_summary(
        "Users",
        6,
        8,
        file,
    )

    result = file.getvalue()

    expected = (
        "# Users \n"
        "> Data dictionary generated automatically by `datavane` \n"
        "## Dataset summary \n"
        "| Property | Value | \n"
        "|----------|-------| \n"
        "| Records | 8| \n"
        "| Fields  | 6 | \n"
    )

    assert result == expected
