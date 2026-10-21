from datavane.inference.json_inference import candidate_from_json_value
from datavane.models import Candidate, InferredType


def test_json_bool_candidate():
    assert candidate_from_json_value(True) == Candidate(
        InferredType.BOOL,
        {"native"},
    )


def test_json_int_candidate():
    assert candidate_from_json_value(123) == Candidate(
        InferredType.INT,
        {"native"},
    )


def test_json_float_candidate():
    assert candidate_from_json_value(1.5) == Candidate(
        InferredType.FLOAT,
        {"native"},
    )


def test_json_string_candidate():
    assert candidate_from_json_value("hello") == Candidate(
        InferredType.STR,
        {"native"},
    )


def test_json_null_candidate():
    assert candidate_from_json_value(None) == Candidate(
        InferredType.UNKNOWN,
        {"null"},
    )


def test_json_false_candidate():
    assert candidate_from_json_value(False) == Candidate(
        InferredType.BOOL,
        {"native"},
    )
