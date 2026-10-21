import csv
import json

import pytest

from datavane.generator import doc_table


def test_doc_table_raises_for_nonexistent_path(tmp_path) -> None:
    input_path = tmp_path / "does_not_exist.json"
    output_path = tmp_path / "docs" / "data_dictionary.md"

    with pytest.raises(FileNotFoundError):
        doc_table(input_path, "test_table", output_path)

    assert not output_path.exists()


def test_doc_table_rejects_unsupported_file_extension(
    tmp_path,
) -> None:
    input_path = tmp_path / "data.txt"
    input_path.write_text("This is not JSON or CSV.", encoding="utf-8")

    output_path = tmp_path / "docs" / "data_dictionary.md"

    with pytest.raises(ValueError, match=r"File extension must be \.csv or \.json"):
        doc_table(input_path, "test_table", output_path)

    assert not output_path.exists()


def test_doc_table_rejects_invalid_json(
    tmp_path,
) -> None:
    input_path = tmp_path / "invalid.json"
    input_path.write_text(
        '{"user": "Ana", invalid}',
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "data_dictionary.md"

    with pytest.raises(json.JSONDecodeError):
        doc_table(input_path, "test_table", output_path)

    assert not output_path.exists()


def test_doc_table_rejects_malformed_csv(tmp_path) -> None:
    input_path = tmp_path / "invalid.csv"
    input_path.write_text(
        'id,name\n1,"Ana\n2,"Luis"\n',
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "data_dictionary.md"

    with pytest.raises(csv.Error):
        doc_table(input_path, "test_table", output_path)

    assert not output_path.exists()


def test_doc_table_rejects_csv_rows_with_missing_columns(tmp_path) -> None:
    input_path = tmp_path / "missing_columns.csv"
    input_path.write_text(
        "id,name\n1,Ana\n2\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "data_dictionary.md"

    with pytest.raises(ValueError, match="column"):
        doc_table(input_path, "test_table", output_path)

    assert not output_path.exists()


def test_doc_table_rejects_csv_rows_with_extra_columns(tmp_path) -> None:
    input_path = tmp_path / "extra_columns.csv"
    input_path.write_text(
        "id,name\n1,Ana,unexpected\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "data_dictionary.md"

    with pytest.raises(ValueError, match="column"):
        doc_table(input_path, "test_table", output_path)

    assert not output_path.exists()
