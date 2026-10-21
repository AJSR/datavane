from datavane.models import Candidate, InferredType


def test_candidate_initial_state():
    candidate = Candidate(type=InferredType.INT)

    assert candidate.type == InferredType.INT
    assert candidate.evidence == set()


def test_candidate_with_evidence():
    candidate = Candidate(
        type=InferredType.INT,
        evidence={"normal"},
    )

    assert candidate.type == InferredType.INT
    assert candidate.evidence == {"normal"}


def test_candidate_with_multiple_evidences():
    candidate = Candidate(
        type=InferredType.FLOAT,
        evidence={"normal", "leading_zero"},
    )

    assert candidate.type == InferredType.FLOAT
    assert candidate.evidence == {"normal", "leading_zero"}


def test_candidates_with_same_data_are_equal():
    candidate1 = Candidate(
        type=InferredType.INT,
        evidence={"normal"},
    )

    candidate2 = Candidate(
        type=InferredType.INT,
        evidence={"normal"},
    )

    assert candidate1 == candidate2


def test_candidates_with_different_types_are_not_equal():
    candidate1 = Candidate(
        type=InferredType.INT,
        evidence={"normal"},
    )

    candidate2 = Candidate(
        type=InferredType.FLOAT,
        evidence={"normal"},
    )

    assert candidate1 != candidate2


def test_candidates_with_different_evidence_are_not_equal():
    candidate1 = Candidate(
        type=InferredType.INT,
        evidence={"normal"},
    )

    candidate2 = Candidate(
        type=InferredType.INT,
        evidence={"leading_zero"},
    )

    assert candidate1 != candidate2
