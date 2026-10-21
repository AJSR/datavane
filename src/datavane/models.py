from dataclasses import dataclass, field
from enum import Enum


class InferredType(Enum):
    """Types that can be inferred from textual data."""

    UNKNOWN = "unknown"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    DATE = "date"
    DATETIME = "datetime"
    STR = "str"


class InferredStructure(Enum):
    OBJECT = "object"
    ARRAY = "array"


class InferenceCertainty(Enum):
    """Confidence levels for an inferred type."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class InferenceResult:
    # todo Update docstring
    """Store the result of inferring a type from textual data."""

    type: InferredType
    certainty: InferenceCertainty
    evidence: dict[str, object] = field(default_factory=dict)


@dataclass
class Candidate:
    type: InferredType | None = None
    evidence: set[str] = field(default_factory=set)
    structure: InferredStructure | None = None


@dataclass
class FieldInfo:
    # todo Update docstring
    """Store inferred information and statistics for a dataset field."""

    name: str
    types: set[InferredType] = field(default_factory=set)
    structures: set[InferredStructure] = field(default_factory=set)
    candidates: dict[InferredType, set[str]] = field(default_factory=dict)
    structural_candidates: dict[InferredStructure, set[str]] = field(
        default_factory=dict
    )
    example: object | None = None
    appearances: int = 0
    null_count: int = 0
    context_count: int = 0

    def update(self, new_value, candidate: Candidate) -> None:
        # todo Update documentation
        """Update the field information with a new observed value.

        The value type and appearance count are always updated. Null values
        increment the null counter, while the first non-null value is stored
        as the field example.

        Args:
            new_value: Value observed for the field.
            value_type: Inferred type of the observed value.
        """
        if candidate.type is not None and candidate.type != InferredType.UNKNOWN:
            self.types.add(candidate.type)
            self.candidates.setdefault(candidate.type, set()).update(candidate.evidence)

        if candidate.structure is not None:
            self.structures.add(candidate.structure)
            self.structural_candidates.setdefault(candidate.structure, set()).update(
                candidate.evidence
            )

        self.appearances += 1

        if new_value is None:
            self.null_count += 1
            return

        if self.example is None:
            self.example = new_value
