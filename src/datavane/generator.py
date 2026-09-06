from pathlib import Path

from .formatting import format_summary, markdown_table
from .inference import infer_schema
from .io import load_dataset


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
    schema = infer_schema(data)
    total_fields = len(schema)
    with open(output_path, "w", encoding="utf-8") as f:
        format_summary(table_name, total_fields, total_records, f)
        markdown_table(schema, total_records, f)
