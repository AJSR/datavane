from datavane.models import Candidate, FieldInfo, InferredType

from .csv_inference import (
    detect_candidates,
    is_null_value,
    normalize_value,
)


def infer_csv_schema(
    data: list[dict[str, str | None]],
) -> dict[str, FieldInfo]:
    """Infer field types and occurrence statistics from CSV records."""
    fields: dict[str, FieldInfo] = {}

    for record in data:
        for field_name, raw_value in record.items():
            if field_name not in fields:
                fields[field_name] = FieldInfo(name=field_name)

            value = normalize_value(raw_value)

            if is_null_value(value):
                fields[field_name].update(
                    None,
                    Candidate(type=InferredType.UNKNOWN),
                )
                continue

            candidate = detect_candidates(value)
            fields[field_name].update(value, candidate)

    total_records = len(data)

    for field_info in fields.values():
        field_info.context_count = total_records

    return dict(sorted(fields.items()))
