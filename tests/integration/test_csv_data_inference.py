from pathlib import Path

from datavane import doc_table


def test_csv_dates_are_documented_as_date_and_datetime(tmp_path: Path):
    csv_path = tmp_path / "events.csv"
    output_path = tmp_path / "docs" / "events.md"

    csv_path.write_text(
        "event_date,event_timestamp,score\n"
        "2026-10-15,2026-10-15T09:30:00,42\n"
        "2026-10-16,2026-10-16T18:45:00,27\n",
        encoding="utf-8",
    )

    doc_table(csv_path, "Events", output_path)

    documentation = output_path.read_text(encoding="utf-8")

    assert "| event_date | date |" in documentation
    assert "| event_timestamp | datetime |" in documentation
    assert "| score | int |" in documentation
