from datavane.generator import _merge_schemas
from datavane.inference.csv_schema import infer_csv_schema
from datavane.inference.schema import infer_schema
from datavane.models import FieldInfo, InferredType


def test_merge_schemas_preserves_conflicting_types():
    json_schema = infer_schema([{"score": 42}])
    csv_schema = infer_csv_schema([{"score": "high"}])

    merged = {}
    _merge_schemas(merged, json_schema)
    _merge_schemas(merged, csv_schema)

    field = merged["score"]

    assert field.types == {InferredType.INT, InferredType.STR}
    assert set(field.candidates) == {InferredType.INT, InferredType.STR}
    assert field.appearances == 2
    assert field.null_count == 0
    assert field.example == 42


def test_merge_schemas_combines_appearances_and_nulls():
    json_schema = infer_schema(
        [
            {"score": 42},
            {"score": None},
        ]
    )
    csv_schema = infer_csv_schema(
        [
            {"score": "high"},
        ]
    )

    merged = {}
    _merge_schemas(merged, json_schema)
    _merge_schemas(merged, csv_schema)

    field = merged["score"]

    assert field.appearances == 3
    assert field.null_count == 1
    assert field.context_count == 3
    assert field.example == 42


def test_merge_schemas_does_not_share_new_field_objects() -> None:
    source_field = FieldInfo(name="score")
    source_field.types.add("int")
    source_field.candidates["int"] = {"42"}
    source_field.appearances = 1

    source = {"score": source_field}
    target = {}

    _merge_schemas(target, source)

    target_field = target["score"]
    target_field.types.add("str")
    target_field.candidates["str"] = {"high"}
    target_field.appearances += 1

    assert source_field.types == {"int"}
    assert source_field.candidates == {"int": {"42"}}
    assert source_field.appearances == 1


def test_merge_schemas_accumulates_existing_field_information() -> None:
    target_field = FieldInfo(name="score")
    target_field.types.add("int")
    target_field.structures.add("scalar")
    target_field.candidates["int"] = {"42"}
    target_field.structural_candidates["scalar"] = {"42"}
    target_field.example = 42
    target_field.appearances = 2
    target_field.null_count = 1
    target_field.context_count = 3

    source_field = FieldInfo(name="score")
    source_field.types.add("str")
    source_field.structures.add("scalar")
    source_field.candidates["str"] = {"high"}
    source_field.structural_candidates["scalar"] = {"high"}
    source_field.example = "high"
    source_field.appearances = 4
    source_field.null_count = 2
    source_field.context_count = 5

    target = {"score": target_field}
    source = {"score": source_field}

    _merge_schemas(target, source)

    merged = target["score"]

    assert merged.types == {"int", "str"}
    assert merged.structures == {"scalar"}
    assert merged.candidates == {
        "int": {"42"},
        "str": {"high"},
    }
    assert merged.structural_candidates == {
        "scalar": {"42", "high"},
    }
    assert merged.example == 42
    assert merged.appearances == 6
    assert merged.null_count == 3
    assert merged.context_count == 8

    # ? Merge must modify the original schema
    assert source_field.types == {"str"}
    assert source_field.appearances == 4
    assert source_field.null_count == 2
    assert source_field.context_count == 5


def test_merge_schemas_preserves_different_structures() -> None:
    target_field = FieldInfo(name="value")
    target_field.types.add("int")
    target_field.structures.add("scalar")
    target_field.candidates["int"] = {"42"}
    target_field.structural_candidates["scalar"] = {"42"}
    target_field.example = 42
    target_field.appearances = 2
    target_field.context_count = 2

    source_field = FieldInfo(name="value")
    source_field.types.add("list[int]")
    source_field.structures.add("list")
    source_field.candidates["list[int]"] = {"[1, 2]"}
    source_field.structural_candidates["list"] = {"[1, 2]"}
    source_field.example = [1, 2]
    source_field.appearances = 3
    source_field.context_count = 3

    target = {"value": target_field}
    source = {"value": source_field}

    _merge_schemas(target, source)

    merged = target["value"]

    assert merged.types == {"int", "list[int]"}
    assert merged.structures == {"scalar", "list"}
    assert merged.candidates == {
        "int": {"42"},
        "list[int]": {"[1, 2]"},
    }
    assert merged.structural_candidates == {
        "scalar": {"42"},
        "list": {"[1, 2]"},
    }
    assert merged.example == 42
    assert merged.appearances == 5
    assert merged.context_count == 5

    # ? Original information form both schemas must be preserved
    assert target_field.types == {"int", "list[int]"}
    assert source_field.types == {"list[int]"}
    assert source_field.structures == {"list"}
