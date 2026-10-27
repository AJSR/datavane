import json

import pytest

from datavane.generator import doc_table


def create_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_single_invalid_json_raises_error(tmp_path):
    input_path = tmp_path / "invalid.json"
    output_path = tmp_path / "output.md"
    input_path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        doc_table(input_path, "Test", output_path, on_error="continue")


def test_directory_raise_stops_at_first_error(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    create_json(input_dir / "valid.json", [{"id": 1}])
    (input_dir / "invalid.json").write_text("{invalid json", encoding="utf-8")

    output_path = tmp_path / "output.md"

    with pytest.raises(json.JSONDecodeError):
        doc_table(input_dir, "Test", output_path, on_error="raise")


def test_directory_continue_generates_partial_report(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    create_json(input_dir / "valid.json", [{"id": 1}])
    (input_dir / "invalid.json").write_text("{invalid json", encoding="utf-8")

    output_path = tmp_path / "output.md"

    doc_table(input_dir, "Test", output_path, on_error="continue")

    assert output_path.exists()

    report = output_path.read_text(encoding="utf-8")

    assert "id" in report
    assert "invalid.json" in report
    assert "partial" in report.lower() or "parcial" in report.lower()
