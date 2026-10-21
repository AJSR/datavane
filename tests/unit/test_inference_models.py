from datavane.models import (
    InferenceCertainty,
    InferenceResult,
    InferredType,
)


def test_inferred_type_values():
    assert InferredType.UNKNOWN.value == "unknown"
    assert InferredType.BOOL.value == "bool"
    assert InferredType.INT.value == "int"
    assert InferredType.FLOAT.value == "float"
    assert InferredType.DATE.value == "date"
    assert InferredType.DATETIME.value == "datetime"
    assert InferredType.STR.value == "str"


def test_inference_certainty_values():
    assert InferenceCertainty.NONE.value == "none"
    assert InferenceCertainty.LOW.value == "low"
    assert InferenceCertainty.MEDIUM.value == "medium"
    assert InferenceCertainty.HIGH.value == "high"


def test_inference_result_initial_state():
    result = InferenceResult(
        type=InferredType.INT,
        certainty=InferenceCertainty.HIGH,
    )

    assert result.type is InferredType.INT
    assert result.certainty is InferenceCertainty.HIGH
    assert result.evidence == {}


def test_inference_result_stores_evidence():
    evidence = {
        "total_values": 100,
        "integer_values": 98,
        "null_values": 2,
    }

    result = InferenceResult(
        type=InferredType.INT,
        certainty=InferenceCertainty.HIGH,
        evidence=evidence,
    )

    assert result.evidence == evidence
