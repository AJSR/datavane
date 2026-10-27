import json
import logging

import pytest

from datavane import doc_table


def create_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_continue_logs_failed_file(tmp_path, caplog):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "invalid.json").write_text(
        "{invalid json",
        encoding="utf-8",
    )
    create_json(input_dir / "valid.json", [{"id": 1}])

    output_path = tmp_path / "output.md"

    with caplog.at_level(logging.ERROR):
        doc_table(input_dir, "Test", output_path, on_error="continue")

    error_records = [
        record for record in caplog.records if record.levelno >= logging.ERROR
    ]

    assert any("invalid.json" in record.getMessage() for record in error_records)
    assert any(
        record.exc_info and record.exc_info[0] is json.JSONDecodeError
        for record in error_records
    )


def test_raise_logs_error_before_propagating(tmp_path, caplog):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "invalid.json").write_text(
        "{invalid json",
        encoding="utf-8",
    )

    output_path = tmp_path / "output.md"

    with caplog.at_level(logging.ERROR):
        with pytest.raises(json.JSONDecodeError):
            doc_table(input_dir, "Test", output_path, on_error="raise")

    assert any(
        "invalid.json" in record.getMessage()
        for record in caplog.records
        if record.levelno >= logging.ERROR
    )
    assert not output_path.exists()


def test_unsupported_file_is_logged_without_error(
    tmp_path,
    caplog,
):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    create_json(input_dir / "valid.json", [{"id": 1}])
    (input_dir / "notes.txt").write_text(
        "Unsupported file",
        encoding="utf-8",
    )

    output_path = tmp_path / "output.md"

    with caplog.at_level(logging.INFO):
        doc_table(input_dir, "Test", output_path, on_error="continue")

    info_records = [
        record for record in caplog.records if record.levelno == logging.INFO
    ]

    assert any("notes.txt" in record.getMessage() for record in info_records)
    assert not any(
        "notes.txt" in record.getMessage() and record.levelno >= logging.ERROR
        for record in caplog.records
    )
