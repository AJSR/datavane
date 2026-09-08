from pathlib import Path

import pytest

from datavane.io import load_csv, load_dataset, load_json

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def sample_csv_path():
    return FIXTURES_DIR / "sample.csv"


@pytest.fixture
def sample_json_path():
    return FIXTURES_DIR / "sample.json"


def test_load_csv(sample_csv_path):
    data = load_csv(sample_csv_path)
    assert isinstance(data, list)
    assert len(data) == 8
    for el in data:
        assert isinstance(el, dict)
        for v in el.values():
            assert isinstance(v, str)


def test_load_json(sample_json_path):
    data = load_json(sample_json_path)
    assert isinstance(data, list)
    assert len(data) == 8

    for element in data:
        assert isinstance(element, dict)

    assert isinstance(data[0]["id"], int)
    assert isinstance(data[0]["name"], str)
    assert data[3]["city"] is None
    assert data[4]["age"] is None
    assert data[4]["email"] is None


def test_load_dataset_csv(sample_csv_path):
    data = load_dataset(sample_csv_path)

    assert isinstance(data, list)
    assert len(data) == 8
    assert all(isinstance(element, dict) for element in data)


def test_load_dataset_directory(tmp_path):
    json_path = tmp_path / "sample.json"
    csv_dir = tmp_path / "nested"
    csv_dir.mkdir()
    csv_path = csv_dir / "sample.csv"

    json_path.write_text(
        (FIXTURES_DIR / "sample.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    csv_path.write_text(
        (FIXTURES_DIR / "sample.csv").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    data = load_dataset(tmp_path)

    assert isinstance(data, list)
    assert len(data) == 16
    assert all(isinstance(element, dict) for element in data)
