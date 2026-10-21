import json
from pathlib import Path

from datavane.generator import doc_table


def test_mixed_directory_uses_csv_inference_for_csv_files(tmp_path: Path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "users.json").write_text(
        json.dumps([{"id": 1, "name": "Ana"}]),
        encoding="utf-8",
    )

    (input_dir / "events.csv").write_text(
        "event_date,event_timestamp,score\n"
        "2026-10-15,2026-10-15T09:30:00,42\n"
        "2026-10-16,2026-10-16T18:45:00,27\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "mixed.md"

    doc_table(input_dir, "Mixed dataset", output_path)

    documentation = output_path.read_text(encoding="utf-8")

    assert "| id | int |" in documentation
    assert "| name | str |" in documentation
    assert "| event_date | date |" in documentation
    assert "| event_timestamp | datetime |" in documentation
    assert "| score | int |" in documentation


def test_mixed_directory_distinguishes_missing_fields_from_nulls(
    tmp_path: Path,
):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "metrics.json").write_text(
        json.dumps(
            [
                {"score": 10},
                {"other": "missing score"},
                {"score": None},
            ]
        ),
        encoding="utf-8",
    )

    (input_dir / "events.csv").write_text(
        "label\nA\nB\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "mixed.md"

    doc_table(input_dir, "Mixed dataset", output_path)

    documentation = output_path.read_text(encoding="utf-8")

    score_row = next(
        line for line in documentation.splitlines() if line.startswith("| score |")
    )
    columns = [column.strip() for column in score_row.strip("|").split("|")]

    assert columns[1] == "int"
    assert columns[2] == "10"
    assert columns[3] == "40.0%"
    assert columns[4] == "50.0%"


def test_mixed_directory_documents_conflicting_types(tmp_path: Path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "scores.json").write_text(
        json.dumps([{"score": 42}]),
        encoding="utf-8",
    )

    (input_dir / "scores.csv").write_text(
        "score\nhigh\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "mixed.md"

    doc_table(input_dir, "Mixed dataset", output_path)

    documentation = output_path.read_text(encoding="utf-8")

    score_row = next(
        line for line in documentation.splitlines() if line.startswith("| score |")
    )
    columns = [column.strip() for column in score_row.strip("|").split("|")]

    documented_types = {item.strip() for item in columns[1].split(",")}

    assert documented_types == {"int", "str"}


def test_directory_merges_conflicting_types_from_multiple_csv_files(
    tmp_path: Path,
):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "part1.csv").write_text(
        "value\n10\n",
        encoding="utf-8",
    )

    (input_dir / "part2.csv").write_text(
        "value\nhello\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "combined.csv.md"

    doc_table(input_dir, "Combined CSV", output_path)

    documentation = output_path.read_text(encoding="utf-8")
    value_row = next(
        line for line in documentation.splitlines() if line.startswith("| value |")
    )
    columns = [column.strip() for column in value_row.strip("|").split("|")]

    documented_types = {item.strip() for item in columns[1].split(",")}

    assert documented_types == {"int", "str"}


def test_directory_merges_conflicting_types_from_multiple_json_files(
    tmp_path: Path,
):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "part1.json").write_text(
        json.dumps([{"value": 10}]),
        encoding="utf-8",
    )

    (input_dir / "part2.json").write_text(
        json.dumps([{"value": "hello"}]),
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "combined.json.md"

    doc_table(input_dir, "Combined JSON", output_path)

    documentation = output_path.read_text(encoding="utf-8")
    value_row = next(
        line for line in documentation.splitlines() if line.startswith("| value |")
    )
    columns = [column.strip() for column in value_row.strip("|").split("|")]

    documented_types = {item.strip() for item in columns[1].split(",")}

    assert documented_types == {"int", "str"}


def test_directory_discovers_files_in_nested_directories(
    tmp_path: Path,
):
    input_dir = tmp_path / "data"
    events_dir = input_dir / "events"
    events_dir.mkdir(parents=True)

    (input_dir / "users.json").write_text(
        json.dumps([{"user_id": 1}]),
        encoding="utf-8",
    )

    (events_dir / "scores.csv").write_text(
        "score\n42\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "nested.md"

    doc_table(input_dir, "Nested dataset", output_path)

    documentation = output_path.read_text(encoding="utf-8")

    assert "| user_id | int |" in documentation
    assert "| score | int |" in documentation


def test_directory_ignores_unsupported_files(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text(
        "This file should be ignored.",
        encoding="utf-8",
    )
    (tmp_path / "data.xml").write_text(
        "<data><value>42</value></data>",
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "data_dictionary.md"

    doc_table(tmp_path, "test_table", output_path)

    assert output_path.exists()

    documentation = output_path.read_text(encoding="utf-8")
    assert "This file should be ignored" not in documentation
    assert "<data>" not in documentation


def test_empty_directory_generates_documentation(tmp_path: Path) -> None:
    output_path = tmp_path / "docs" / "data_dictionary.md"

    doc_table(tmp_path, "test_table", output_path)

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").strip()


def test_nested_field_presence_uses_parent_context(
    tmp_path: Path,
) -> None:
    data_path = tmp_path / "data.json"
    data_path.write_text(
        json.dumps(
            [
                {"user": {"name": "Ana", "age": 30}},
                {"user": {"name": "Luis"}},
                {"other": "value"},
            ]
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "data_dictionary.md"

    doc_table(data_path, "users", output_path)

    documentation = output_path.read_text(encoding="utf-8")
    age_row = next(
        line for line in documentation.splitlines() if line.startswith("| user.age |")
    )

    assert "50.0%" in age_row


def test_nested_field_presence_and_nulls_are_independent(
    tmp_path: Path,
) -> None:
    data_path = tmp_path / "data.json"
    data_path.write_text(
        json.dumps(
            [
                {"user": {"age": 30}},
                {"user": {"age": None}},
                {"user": {}},
                {"other": "value"},
            ]
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "data_dictionary.md"

    doc_table(data_path, "users", output_path)

    documentation = output_path.read_text(encoding="utf-8")
    age_row = next(
        line for line in documentation.splitlines() if line.startswith("| user.age |")
    )

    # ? age appears in 2 of 3 user objects
    assert "66.7%" in age_row

    # ? One of the 2 appearances of age is null
    assert "50.0%" in age_row


def test_nested_field_context_is_merged_across_json_files(
    tmp_path: Path,
) -> None:
    first_file = tmp_path / "part1.json"
    first_file.write_text(
        json.dumps(
            [
                {"user": {"name": "Ana", "age": 30}},
                {"user": {"name": "Luis"}},
            ]
        ),
        encoding="utf-8",
    )

    second_file = tmp_path / "part2.json"
    second_file.write_text(
        json.dumps(
            [
                {"user": {"age": 40}},
                {"other": "value"},
            ]
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "data_dictionary.md"

    doc_table(tmp_path, "users", output_path)

    documentation = output_path.read_text(encoding="utf-8")
    age_row = next(
        line for line in documentation.splitlines() if line.startswith("| user.age |")
    )

    # ? user appears in 3 entries, age appears in 2 of the 3 entries
    assert "66.7%" in age_row
