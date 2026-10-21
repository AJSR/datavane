from pathlib import Path

from datavane.inference.csv_schema import infer_csv_schema
from datavane.inference.schema import infer_schema
from datavane.models import FieldInfo

from .formatting import format_summary, markdown_table
from .io import load_dataset


def _merge_schemas(
    target: dict[str, FieldInfo],
    source: dict[str, FieldInfo],
) -> None:
    """Merges two data dictionaries from different sources.

    Args:
        target (dict[str, FieldInfo]): Data dictionary where schemas will be merged
        source (dict[str, FieldInfo]): Data dictionary that is going to be merged
          with target
    """
    for name, field in source.items():
        if name not in target:
            target[name] = FieldInfo(
                name=field.name,
                types=set(field.types),
                structures=set(field.structures),
                candidates={
                    inferred_type: set(evidence)
                    for inferred_type, evidence in field.candidates.items()
                },
                structural_candidates={
                    structure: set(evidence)
                    for structure, evidence in field.structural_candidates.items()
                },
                example=field.example,
                appearances=field.appearances,
                null_count=field.null_count,
                context_count=field.context_count,
            )
            continue

        existing = target[name]
        existing.types.update(field.types)
        existing.structures.update(field.structures)

        for inferred_type, evidence in field.candidates.items():
            existing.candidates.setdefault(inferred_type, set()).update(evidence)

        for structure, evidence in field.structural_candidates.items():
            existing.structural_candidates.setdefault(structure, set()).update(evidence)

        if existing.example is None:
            existing.example = field.example

        existing.appearances += field.appearances
        existing.null_count += field.null_count
        existing.context_count += field.context_count


def doc_table(path: Path, table_name: str, output_path: Path) -> None:
    """Generate a Markdown data dictionary for a dataset.

    The dataset is loaded from the given path, its schema is inferred,
    and the resulting documentation is written to the specified output
    file.

    Args:
        path (Path): Path to the input dataset or directory containing datasets.
        table_name (str): Name used as the title of the generated documentation.
        output_path (Path): Path where the Markdown documentation will be written.
    """

    data = load_dataset(path)
    total_records = len(data)
    if path.is_file():
        data = load_dataset(path)
        total_records = len(data)

        if path.suffix.lower() == ".csv":
            schema = infer_csv_schema(data)
        else:
            schema = infer_schema(data)

    else:
        json_data = []
        csv_data = []

        for file_path in path.rglob("*"):
            if not file_path.is_file():
                continue

            suffix = file_path.suffix.lower()

            if suffix not in {".json", ".csv"}:
                continue

            file_data = load_dataset(file_path)

            if suffix == ".json":
                json_data.extend(file_data)
            else:
                csv_data.extend(file_data)

        total_records = len(json_data) + len(csv_data)
        schema = {}

        if json_data:
            _merge_schemas(schema, infer_schema(json_data))

        if csv_data:
            _merge_schemas(schema, infer_csv_schema(csv_data))

        # * Root-level fields share the complete dataset as their context.
        for name, field in schema.items():
            if "." not in name:
                field.context_count = total_records

    total_fields = len(schema)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        format_summary(table_name, total_fields, total_records, f)
        markdown_table(schema, f)
