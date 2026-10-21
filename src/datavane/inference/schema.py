from datavane.models import FieldInfo

from .json_inference import candidate_from_json_value


def process_object(
    obj: dict | list,
    fields: dict[str, FieldInfo],
    prefix: str = "",
    context_counts: dict[str, int] | None = None,
) -> None:
    # todo Needs doccomment
    """Recursively process objects and lists to infer field information."""
    if context_counts is None:
        context_counts = {}

    if isinstance(obj, dict):
        context_counts[prefix] = context_counts.get(prefix, 0) + 1

        for field, value in obj.items():
            if prefix:
                field_name = f"{prefix}.{field}"
            else:
                field_name = field

            if field_name not in fields:
                fields[field_name] = FieldInfo(name=field_name)

            fields[field_name].update(
                value,
                candidate_from_json_value(value),
            )

            if isinstance(value, (dict, list)):
                process_object(
                    value,
                    fields,
                    field_name,
                    context_counts,
                )

    elif isinstance(obj, list):
        for entry in obj:
            if isinstance(entry, dict):
                process_object(
                    entry,
                    fields,
                    prefix + "[]",
                    context_counts,
                )


def infer_schema(data: list[dict]) -> dict[str, FieldInfo]:
    # todo Needs doccomment
    """Infer field types, structures, and occurrence statistics."""
    fields: dict[str, FieldInfo] = {}
    context_counts: dict[str, int] = {}

    for entry in data:
        process_object(
            entry,
            fields,
            context_counts=context_counts,
        )

    for field_name, field_info in fields.items():
        parent_prefix = field_name.rpartition(".")[0]
        field_info.context_count = context_counts.get(parent_prefix, 0)

    return dict(sorted(fields.items()))
