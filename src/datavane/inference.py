from .models import FieldInfo


def infer_type(value) -> str:
    """Infer the type of a value, including nested lists.

    Lists are represented using the inferred types of their elements.
    Empty lists are represented simply as ``list``.

    Args:
        value: Value whose type should be inferred.

    Returns:
        str: A string representing the inferred type.
    """

    if value is None:
        return "null"

    if isinstance(value, list):
        if not value:
            return "list"

        element_types = set()

        for element in value:
            element_types.add(infer_type(element))

        return f"list[{', '.join(sorted(element_types))}]"

    return type(value).__name__


def process_object(
    obj: dict | list,
    fields: dict[str, FieldInfo],
    prefix: str = "",
    context_count: int = 1,
) -> None:
    """Recursively process a dictionary or list to infer field information.

    Nested fields are represented using dot notation, while fields inside
    lists are marked with ``[]``. Field statistics are updated as values
    are encountered.

    Args:
        obj (dict | list): Dictionary or list to process.
        fields (dict[str, FieldInfo]): Mapping of field paths to their corresponding 
        ``FieldInfo``.
        prefix (str, optional): Path prefix used for nested fields. Defaults to "".
        context_count (int, optional): Number of records represented by the current 
        context. Defaults to 1.
    """

    if isinstance(obj, dict):
        for field, value in obj.items():
            if prefix:
                field_name = f"{prefix}.{field}"
            else:
                field_name = field

            if field_name not in fields:
                fields[field_name] = FieldInfo(
                    name=field_name, context_count=context_count
                )

            fields[field_name].update(value, infer_type(value))

            if isinstance(value, (dict, list)):
                process_object(value, fields, field_name, context_count=1)

    elif isinstance(obj, list):
        for entry in obj:
            if isinstance(entry, dict):
                process_object(entry, fields, prefix + "[]", context_count=len(obj))


def infer_schema(data: list[dict]) -> dict[str, FieldInfo]:
    """Infer the schema of a dataset.

    Each record is recursively processed to collect information about
    its fields, including their types, examples, appearances, nulls,
    and contextual occurrence counts.

    Args:
        data (list[dict]): Dataset represented as a list of dictionaries.

    Returns:
        dict[str, FieldInfo]: A dictionary mapping field paths to their inferred
        ``FieldInfo``.
    """

    fields: dict[str, FieldInfo] = {}
    for entry in data:
        process_object(entry, fields, context_count=len(data))

    return dict(sorted(fields.items()))
