from dataclasses import dataclass, field


@dataclass
class FieldInfo:
    """Store inferred information and statistics for a dataset field."""

    name: str
    types: set[str] = field(default_factory=set)
    example: object | None = None
    appearances: int = 0
    null_count: int = 0
    context_count: int = 0

    def update(self, new_value, value_type) -> None:
        """Update the field information with a new observed value.

        The value type and appearance count are always updated. Null values
        increment the null counter, while the first non-null value is stored
        as the field example.

        Args:
            new_value: Value observed for the field.
            value_type: Inferred type of the observed value.
        """
        self.types.add(value_type)
        self.appearances += 1

        if new_value is None:
            self.null_count += 1
            return
        
        if self.example is None:
            self.example = new_value
