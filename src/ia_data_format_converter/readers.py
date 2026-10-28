"""Readers turning input files into Arrow tables."""

from pathlib import Path

import pyarrow as pa
from pyarrow import csv

from ia_data_format_converter.errors import InputFileError, InvalidOptionError


def read_csv(path: str | Path, sep: str = ",", encoding: str = "utf-8") -> pa.Table:
    """Read a CSV file with a header row into an Arrow table with inferred column types."""
    path = Path(path)
    if len(sep) != 1:
        raise InvalidOptionError(f"Separator must be a single character, got {sep!r}")
    if not path.is_file():
        raise InputFileError(f"Input file not found: {path}")
    if path.stat().st_size == 0:
        raise InputFileError(f"Input file is empty: {path}")

    try:
        return csv.read_csv(
            path,
            read_options=csv.ReadOptions(encoding=encoding),
            parse_options=csv.ParseOptions(delimiter=sep),
        )
    except LookupError as exc:
        raise InvalidOptionError(f"Unknown encoding: {encoding!r}") from exc
    except (pa.ArrowInvalid, UnicodeDecodeError) as exc:
        raise InputFileError(f"Cannot read CSV file {path}: {exc}") from exc
