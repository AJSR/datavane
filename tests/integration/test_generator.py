from pathlib import Path

from datavane.generator import doc_table

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_doc_table(tmp_path):
    input_path = FIXTURES_DIR / "sample.json"
    output_path = tmp_path / "output.md"

    doc_table(
        input_path,
        "Users",
        output_path,
    )

    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "# Users" in content
    assert "> Data dictionary generated automatically by `datavane`" in content

    assert "## Dataset summary" in content
    assert "Records" in content
    assert "8" in content
    assert "Fields" in content
    assert "6" in content

    assert "## Schema" in content

    assert "| id |" in content
    assert "| name |" in content
    assert "| age |" in content
    assert "| city |" in content
    assert "| email |" in content
    assert "| registration_date |" in content

    assert "Ana García" in content


def test_doc_table_overwrites_existing_file(tmp_path):
    input_path = FIXTURES_DIR / "sample.json"
    output_path = tmp_path / "output.md"

    doc_table(
        input_path,
        "Users",
        output_path,
    )

    first_content = output_path.read_text(encoding="utf-8")

    doc_table(
        input_path,
        "Users",
        output_path,
    )

    second_content = output_path.read_text(encoding="utf-8")

    assert first_content == second_content


def test_doc_table_csv(tmp_path):
    input_path = FIXTURES_DIR / "sample.csv"
    output_path = tmp_path / "output.md"

    doc_table(
        input_path,
        "Users",
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")

    assert "# Users" in content
    assert "## Dataset summary" in content
    assert "Records" in content
    assert "8" in content
    assert "Ana García" in content


def test_doc_table_directory(tmp_path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()

    (input_dir / "sample.json").write_text(
        (FIXTURES_DIR / "sample.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    (input_dir / "sample.csv").write_text(
        (FIXTURES_DIR / "sample.csv").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    output_path = tmp_path / "output.md"

    doc_table(
        input_dir,
        "Users",
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")

    assert "# Users" in content
    assert "## Dataset summary" in content
    assert "Records" in content


def test_doc_table_creates_missing_output_directories(tmp_path):
    input_path = FIXTURES_DIR / "formatting_sample.json"
    output_path = tmp_path / "reports" / "nested" / "output.md"

    assert not output_path.parent.exists()

    doc_table(
        input_path,
        "Formatting sample",
        output_path,
    )

    assert output_path.exists()
    assert output_path.is_file()

    content = output_path.read_text(encoding="utf-8")
    assert "# Formatting sample" in content
