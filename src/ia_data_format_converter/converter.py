"""Conversion orchestration."""

import os
import tempfile
from pathlib import Path
from typing import Any

from ia_data_format_converter.errors import OutputExistsError
from ia_data_format_converter.readers import read_csv
from ia_data_format_converter.writers import get_writer


def default_output_path(input_path: str | Path, fmt: str) -> Path:
    """Return the input path with the extension of the target format."""
    return Path(input_path).with_suffix(get_writer(fmt).extension)


def convert(
    input_path: str | Path,
    output_path: str | Path | None,
    fmt: str,
    *,
    sep: str = ",",
    encoding: str = "utf-8",
    overwrite: bool = False,
    **options: Any,
) -> Path:
    """Convert a CSV file to ``fmt`` and return the written output path.

    The output is written atomically: on failure no partial file is left behind.
    """
    writer = get_writer(fmt)
    options = writer.validate_options(**options)
    output = Path(output_path) if output_path is not None else default_output_path(input_path, fmt)
    if output.exists() and not overwrite:
        raise OutputExistsError(f"Output file already exists: {output} (use overwrite to replace)")

    table = read_csv(input_path, sep=sep, encoding=encoding)

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        writer.write(table, tmp_path, **options)
        os.replace(tmp_path, output)
    finally:
        tmp_path.unlink(missing_ok=True)
    return output
