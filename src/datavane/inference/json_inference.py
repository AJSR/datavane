from datavane.models import Candidate, InferredStructure, InferredType


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


def candidate_from_json_value(val):
    """Creates a candidate object for val with the inferred type and evidence.

    Args:
        val: Original string from json data

    Returns:
        (Candidate): Returns a Candidate object with type and evidence inferred
          from listed patterns.
    """
    if val is None:
        return Candidate(type=InferredType.UNKNOWN, evidence={"null"})

    if isinstance(val, dict):
        return Candidate(structure=InferredStructure.OBJECT, evidence={"native"})

    if isinstance(val, list):
        return Candidate(structure=InferredStructure.ARRAY, evidence={"native"})

    if isinstance(val, bool):
        return Candidate(type=InferredType.BOOL, evidence={"native"})

    if isinstance(val, int):
        return Candidate(type=InferredType.INT, evidence={"native"})

    if isinstance(val, float):
        return Candidate(type=InferredType.FLOAT, evidence={"native"})

    if isinstance(val, str):
        return Candidate(type=InferredType.STR, evidence={"native"})
