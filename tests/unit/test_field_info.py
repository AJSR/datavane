from datavane.models import (
    Candidate,
    FieldInfo,
    InferredStructure,
    InferredType,
)


def test_field_info_initial_state():
    field = FieldInfo(name="age")

    assert field.name == "age"
    assert field.types == set()
    assert field.candidates == {}
    assert field.example is None
    assert field.appearances == 0
    assert field.null_count == 0
    assert field.context_count == 0


def test_update_value():
    field = FieldInfo(name="age")

    field.update(
        25,
        Candidate(
            InferredType.INT,
            {"native"},
        ),
    )

    assert field.types == {InferredType.INT}
    assert field.candidates == {
        InferredType.INT: {"native"},
    }
    assert field.appearances == 1
    assert field.null_count == 0
    assert field.example == 25


def test_update_none():
    field = FieldInfo(name="nickname")

    field.update(
        None,
        Candidate(
            InferredType.UNKNOWN,
            {"null"},
        ),
    )

    assert field.types == set()
    assert field.candidates == {}
    assert field.appearances == 1
    assert field.null_count == 1
    assert field.example is None


def test_update_keeps_first_example():
    field = FieldInfo(name="age")

    field.update(
        25,
        Candidate(
            InferredType.INT,
            {"native"},
        ),
    )
    field.update(
        30,
        Candidate(
            InferredType.INT,
            {"native"},
        ),
    )

    assert field.types == {InferredType.INT}
    assert field.candidates == {
        InferredType.INT: {"native"},
    }
    assert field.appearances == 2
    assert field.null_count == 0
    assert field.example == 25


def test_update_uses_first_non_null_example():
    field = FieldInfo(name="nickname")

    field.update(
        None,
        Candidate(
            InferredType.UNKNOWN,
            {"null"},
        ),
    )
    field.update(
        "Tony",
        Candidate(
            InferredType.STR,
            {"native"},
        ),
    )
    field.update(
        "Juan",
        Candidate(
            InferredType.STR,
            {"native"},
        ),
    )

    assert field.types == {InferredType.STR}
    assert field.candidates == {InferredType.STR: {"native"}}
    assert field.appearances == 3
    assert field.null_count == 1
    assert field.example == "Tony"


def test_update_collects_types():
    field = FieldInfo(name="age")

    field.update(
        10,
        Candidate(
            InferredType.INT,
            {"normal"},
        ),
    )
    field.update(
        "10",
        Candidate(
            InferredType.STR,
            {"native"},
        ),
    )
    field.update(
        10.5,
        Candidate(
            InferredType.FLOAT,
            {"normal"},
        ),
    )

    assert field.types == {
        InferredType.INT,
        InferredType.STR,
        InferredType.FLOAT,
    }
    assert field.candidates == {
        InferredType.INT: {"normal"},
        InferredType.STR: {"native"},
        InferredType.FLOAT: {"normal"},
    }
    assert field.appearances == 3
    assert field.null_count == 0


def test_field_info_initial_candidates():
    field = FieldInfo(name="age")

    assert field.candidates == {}


def test_update_adds_candidate():
    field = FieldInfo(name="age")

    field.update(
        25,
        Candidate(
            InferredType.INT,
            {"native"},
        ),
    )

    assert field.candidates == {
        InferredType.INT: {"native"},
    }


def test_update_accumulates_candidate_evidence():
    field = FieldInfo(name="id")

    field.update(
        "001",
        Candidate(
            InferredType.INT,
            {"leading_zero"},
        ),
    )

    field.update(
        "123",
        Candidate(
            InferredType.INT,
            {"normal"},
        ),
    )

    assert field.candidates == {
        InferredType.INT: {
            "leading_zero",
            "normal",
        },
    }


def test_update_accumulates_different_candidate_types():
    field = FieldInfo(name="value")

    field.update(
        "123",
        Candidate(
            InferredType.INT,
            {"normal"},
        ),
    )

    field.update(
        "1.5",
        Candidate(
            InferredType.FLOAT,
            {"normal"},
        ),
    )

    assert field.candidates == {
        InferredType.INT: {"normal"},
        InferredType.FLOAT: {"normal"},
    }


def test_field_info_update_object_structure():
    field = FieldInfo(name="customer")

    candidate = Candidate(
        structure=InferredStructure.OBJECT,
        evidence={"native"},
    )

    field.update({"id": 1}, candidate)

    assert field.types == set()
    assert field.structures == {InferredStructure.OBJECT}
    assert field.structural_candidates == {InferredStructure.OBJECT: {"native"}}
    assert field.appearances == 1
    assert field.null_count == 0
    assert field.example == {"id": 1}


def test_field_info_update_array_structure():
    field = FieldInfo(name="items")

    candidate = Candidate(
        structure=InferredStructure.ARRAY,
        evidence={"native"},
    )

    field.update([1, 2, 3], candidate)

    assert field.types == set()
    assert field.structures == {InferredStructure.ARRAY}
    assert field.structural_candidates == {InferredStructure.ARRAY: {"native"}}
    assert field.appearances == 1
    assert field.null_count == 0
    assert field.example == [1, 2, 3]


def test_field_info_accumulates_multiple_structures():
    field = FieldInfo(name="value")

    object_candidate = Candidate(
        structure=InferredStructure.OBJECT,
        evidence={"native"},
    )
    array_candidate = Candidate(
        structure=InferredStructure.ARRAY,
        evidence={"native"},
    )

    field.update({"id": 1}, object_candidate)
    field.update([1, 2], array_candidate)

    assert field.types == set()
    assert field.structures == {
        InferredStructure.OBJECT,
        InferredStructure.ARRAY,
    }
    assert field.structural_candidates == {
        InferredStructure.OBJECT: {"native"},
        InferredStructure.ARRAY: {"native"},
    }
    assert field.appearances == 2


def test_field_info_keeps_scalar_type_and_structure_separate():
    field = FieldInfo(name="value")

    field.update(
        42,
        Candidate(
            type=InferredType.INT,
            evidence={"native"},
        ),
    )

    field.update(
        {"value": 42},
        Candidate(
            structure=InferredStructure.OBJECT,
            evidence={"native"},
        ),
    )

    assert field.types == {InferredType.INT}
    assert field.structures == {InferredStructure.OBJECT}

    assert field.candidates == {
        InferredType.INT: {"native"},
    }
    assert field.structural_candidates == {
        InferredStructure.OBJECT: {"native"},
    }

    assert field.appearances == 2
