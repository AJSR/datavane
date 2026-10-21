import pytest

from datavane.inference.csv_inference import detect_candidates
from datavane.models import InferredType


@pytest.mark.parametrize(
    "value",
    [
        "2026-10-15",
        "2024-02-29",
        "2000-01-01",
        "1999-12-31",
    ],
)
def test_detect_iso_dates(value):
    candidate = detect_candidates(value)

    assert candidate.type == InferredType.DATE


@pytest.mark.parametrize(
    "value",
    [
        "2026-02-30",
        "2026-13-01",
        "2026-00-10",
        "2026-01-00",
        "15-10-2026",
        "10/15/2026",
        "",
        "not-a-date",
    ],
)
def test_invalid_or_unsupported_dates_are_strings(value):
    candidate = detect_candidates(value)

    assert candidate.type == InferredType.STR


@pytest.mark.parametrize(
    "value",
    [
        "2026-10-15T09:30:00",
        "2026-10-15T09:30:00.123456",
        "2026-10-15 09:30:00",
        "2024-02-29T23:59:59",
    ],
)
def test_detect_iso_datetimes(value):
    candidate = detect_candidates(value)

    assert candidate.type == InferredType.DATETIME


@pytest.mark.parametrize(
    "value",
    [
        "2026-10-15T25:30:00",
        "2026-10-15T09:60:00",
        "2026-10-15T09:30:60",
        "2026-02-30T09:30:00",
        "2026-10-15Tnot-a-time",
    ],
)
def test_invalid_datetimes_are_strings(value):
    candidate = detect_candidates(value)

    assert candidate.type == InferredType.STR


@pytest.mark.parametrize(
    ("value", "expected_type"),
    [
        ("2026-10-15", InferredType.DATE),
        ("2026-10-15T09:30:00", InferredType.DATETIME),
    ],
)
def test_date_and_datetime_are_distinguished(value, expected_type):
    candidate = detect_candidates(value)

    assert candidate.type == expected_type


@pytest.mark.parametrize(
    "value",
    [
        "15/10/2026",
        "10/15/2026",
        "01/02/2026",
        "2026/10/15",
    ],
)
def test_ambiguous_date_formats_are_strings(value):
    candidate = detect_candidates(value)

    assert candidate.type == InferredType.STR


@pytest.mark.parametrize(
    "value",
    [
        "2026-10-15",
        "2026-10-15T09:30:00",
    ],
)
def test_date_candidates_have_no_unexpected_structure(value):
    candidate = detect_candidates(value)

    assert candidate.structure is None
