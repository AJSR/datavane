from datavane.inference.csv_inference import (
    detect_bool,
    detect_candidates,
    detect_float,
    detect_int,
    is_null_value,
    normalize_value,
)
from datavane.models import Candidate, InferredType


def test_normalize_value_strips_whitespace():
    assert normalize_value(" 42 ") == "42"


def test_normalize_value_strips_whitespace_from_text():
    assert normalize_value("  hello  ") == "hello"


def test_normalize_value_keeps_internal_whitespace():
    assert normalize_value("hello world") == "hello world"


def test_normalize_value_empty_string():
    assert normalize_value("") == ""


def test_normalize_value_whitespace_only():
    assert normalize_value("   ") == ""


def test_normalize_value_none():
    assert normalize_value(None) is None


def test_normalize_value_does_not_convert_numeric_strings():
    assert normalize_value("42") == "42"
    assert isinstance(normalize_value("42"), str)


def test_normalize_value_does_not_convert_boolean_strings():
    assert normalize_value("true") == "true"
    assert isinstance(normalize_value("true"), str)


def test_is_null_value_none():
    assert is_null_value(None) is True


def test_is_null_value_empty_string():
    assert is_null_value("") is True


def test_is_null_value_whitespace():
    assert is_null_value(normalize_value("   ")) is True


def test_is_null_value_non_empty_string():
    assert is_null_value("hello") is False


def test_is_null_value_numeric_string():
    assert is_null_value("42") is False


def test_is_null_value_null_literal():
    assert is_null_value("null") is True


def test_is_null_value_na_literal():
    assert is_null_value("NA") is False


def test_is_null_value_null_case_insensitive():
    assert is_null_value("NULL") is True
    assert is_null_value("Null") is True
    assert is_null_value("nUlL") is True


def test_is_null_value_whitespace_is_handled_by_normalization():
    value = normalize_value("   null   ")

    assert is_null_value(value) is True


def test_detect_int():
    assert detect_int("123")
    assert detect_int("+123")
    assert detect_int("-123")

    assert not detect_int("++123")
    assert not detect_int("--123")
    assert not detect_int("1+3")
    assert not detect_int("123abc")


def test_detect_bool():
    assert detect_bool("true")
    assert detect_bool("TRUE")
    assert detect_bool("False")

    assert not detect_bool("true123")
    assert not detect_bool("nottrue")
    assert not detect_bool("1")


def test_detect_float_decimal():
    assert detect_float("1.5")
    assert detect_float("3.14")
    assert detect_float("0.5")


def test_detect_float_decimal_with_sign():
    assert detect_float("+1.5")
    assert detect_float("-1.5")


def test_detect_float_scientific_notation():
    assert detect_float("1e3")
    assert detect_float("1E3")
    assert detect_float("1e-3")
    assert detect_float("1E-3")
    assert detect_float("1e+3")
    assert detect_float("1E+3")


def test_detect_float_decimal_scientific_notation():
    assert detect_float("1.5e3")
    assert detect_float("1.5E3")
    assert detect_float("1.5e-3")
    assert detect_float("1.5E-3")
    assert detect_float("1.5e+3")
    assert detect_float("1.5E+3")


def test_detect_float_decimal_scientific_notation_with_sign():
    assert detect_float("+1.5e3")
    assert detect_float("-1.5e3")
    assert detect_float("+1.5e-3")
    assert detect_float("-1.5e-3")
    assert detect_float("+1.5e+3")
    assert detect_float("-1.5e+3")


def test_detect_float_rejects_integers():
    assert not detect_float("1")
    assert not detect_float("42")
    assert not detect_float("-42")
    assert not detect_float("+42")


def test_detect_float_rejects_invalid_decimal_formats():
    assert not detect_float("1..5")
    assert not detect_float("1.2.3")


def test_detect_float_rejects_invalid_exponents():
    assert not detect_float("1e")
    assert not detect_float("1e+")
    assert not detect_float("1e-")
    assert not detect_float("1.5e")
    assert not detect_float("1.5e+")
    assert not detect_float("1.5e-")


def test_detect_float_rejects_multiple_signs():
    assert not detect_float("++1.5")
    assert not detect_float("--1.5")
    assert not detect_float("+-1.5")
    assert not detect_float("-+1.5")


def test_detect_float_rejects_signs_in_middle():
    assert not detect_float("1+2.5")
    assert not detect_float("1-2.5")
    assert not detect_float("1.5+2")
    assert not detect_float("1.5-2")


def test_detect_float_rejects_text():
    assert not detect_float("abc")
    assert not detect_float("abc1.5")
    assert not detect_float("1.5abc")
    assert not detect_float("hello1e3")


def test_detect_float_rejects_whitespace():
    assert not detect_float(" 1.5")
    assert not detect_float("1.5 ")
    assert not detect_float(" 1.5 ")


def test_detect_float_rejects_empty_value():
    assert not detect_float("")


def test_detect_candidates_bool():
    assert detect_candidates("true") == Candidate(type=InferredType.BOOL)


def test_detect_candidates_bool_case_insensitive():
    assert detect_candidates("TRUE") == Candidate(type=InferredType.BOOL)


def test_detect_candidates_false():
    assert detect_candidates("false") == Candidate(type=InferredType.BOOL)


def test_detect_candidates_int():
    assert detect_candidates("123") == Candidate(
        InferredType.INT,
        {"normal"},
    )


def test_detect_candidates_negative_int():
    assert detect_candidates("-123") == Candidate(
        InferredType.INT,
        {"normal"},
    )


def test_detect_candidates_positive_int():
    assert detect_candidates("+123") == Candidate(
        InferredType.INT,
        {"normal"},
    )


def test_detect_candidates_int_leading_zero():
    assert detect_candidates("00123") == Candidate(
        InferredType.INT,
        {"normal", "leading_zero"},
    )


def test_detect_candidates_float():
    assert detect_candidates("123.45") == Candidate(
        InferredType.FLOAT,
        {"normal"},
    )


def test_detect_candidates_negative_float():
    assert detect_candidates("-123.45") == Candidate(
        InferredType.FLOAT,
        {"normal"},
    )


def test_detect_candidates_float_without_leading_integer():
    assert detect_candidates(".45") == Candidate(
        InferredType.FLOAT,
        {"normal"},
    )


def test_detect_candidates_negative_float_without_leading_integer():
    assert detect_candidates("-.45") == Candidate(
        InferredType.FLOAT,
        {"normal"},
    )


def test_detect_candidates_float_leading_zero():
    assert detect_candidates("001.45") == Candidate(
        InferredType.FLOAT,
        {"normal", "leading_zero"},
    )


def test_detect_candidates_scientific_notation():
    assert detect_candidates("1e3") == Candidate(
        InferredType.FLOAT,
        {"scientific notation"},
    )


def test_detect_candidates_decimal_scientific_notation():
    assert detect_candidates("1.5e3") == Candidate(
        InferredType.FLOAT,
        {"scientific notation"},
    )


def test_detect_candidates_negative_scientific_notation():
    assert detect_candidates("-1.5e-3") == Candidate(
        InferredType.FLOAT,
        {"scientific notation"},
    )


def test_detect_candidates_leading_zero_scientific_notation():
    assert detect_candidates("001.5e3") == Candidate(
        InferredType.FLOAT,
        {"leading_zero", "scientific notation"},
    )


def test_detect_candidates_string():
    assert detect_candidates("hello") == Candidate(type=InferredType.STR)


def test_detect_candidates_numeric_string():
    assert detect_candidates("123abc") == Candidate(type=InferredType.STR)
