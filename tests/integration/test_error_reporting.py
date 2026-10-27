import json

import pytest

from datavane import doc_table


def create_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_report_includes_details_of_failed_file(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    create_json(input_dir / "valid.json", [{"id": 1}])
    (input_dir / "invalid.json").write_text(
        "{invalid json",
        encoding="utf-8",
    )

    output_path = tmp_path / "output.md"

    doc_table(input_dir, "Test", output_path, on_error="continue")

    report = output_path.read_text(encoding="utf-8")
    assert "invalid.json" in report
    assert "JSONDecodeError" in report
    assert "Failed files" in report


def test_report_includes_details_of_every_failed_file(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "invalid1.json").write_text(
        "{invalid json",
        encoding="utf-8",
    )
    (input_dir / "invalid2.json").write_text(
        "[invalid json",
        encoding="utf-8",
    )

    output_path = tmp_path / "output.md"

    doc_table(input_dir, "Test", output_path, on_error="continue")

    report = output_path.read_text(encoding="utf-8")

    assert "invalid1.json" in report
    assert "invalid2.json" in report
    assert report.count("JSONDecodeError") >= 2


def test_unsupported_files_are_listed_without_read_errors(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    create_json(input_dir / "valid.json", [{"id": 1}])
    (input_dir / "notes.txt").write_text(
        "This file is not supported",
        encoding="utf-8",
    )

    output_path = tmp_path / "output.md"

    doc_table(input_dir, "Test", output_path, on_error="continue")

    report = output_path.read_text(encoding="utf-8")

    assert "notes.txt" in report
    assert "Unsupported files" in report

    unsupported_files_section = report.split("### Unsupported files", maxsplit=1)[
        1
    ].split("## Dataset summary", maxsplit=1)[0]

    assert "notes.txt" in unsupported_files_section
    assert "### Failed files" not in report


def test_failed_file_details_include_error_message(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    invalid_path = input_dir / "invalid.json"
    invalid_path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError) as exc_info:
        json.loads(invalid_path.read_text(encoding="utf-8"))

    expected_message = str(exc_info.value)

    output_path = tmp_path / "output.md"

    doc_table(input_dir, "Test", output_path, on_error="continue")

    report = output_path.read_text(encoding="utf-8")

    assert "invalid.json" in report
    assert expected_message in report


def test_all_files_fail_generates_report_with_all_errors(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "invalid1.json").write_text(
        "{invalid json",
        encoding="utf-8",
    )
    (input_dir / "invalid2.json").write_text(
        "[invalid json",
        encoding="utf-8",
    )

    output_path = tmp_path / "output.md"

    doc_table(input_dir, "Test", output_path, on_error="continue")

    assert output_path.exists()

    report = output_path.read_text(encoding="utf-8")

    assert "invalid1.json" in report
    assert "invalid2.json" in report
    assert report.count("JSONDecodeError") >= 2


def test_empty_directory_generates_empty_report(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    output_path = tmp_path / "output.md"

    doc_table(input_dir, "Test", output_path, on_error="continue")

    assert output_path.exists()

    report = output_path.read_text(encoding="utf-8")

    assert "Records" in report
    assert "| 0 |" in report
    assert "JSONDecodeError" not in report


def test_raise_does_not_create_new_report(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "invalid.json").write_text(
        "{invalid json",
        encoding="utf-8",
    )

    output_path = tmp_path / "output.md"

    with pytest.raises(json.JSONDecodeError):
        doc_table(input_dir, "Test", output_path, on_error="raise")

    assert not output_path.exists()
