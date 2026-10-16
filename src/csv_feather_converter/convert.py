"""Module for converting files between CSV and Feather formats."""
import logging
from pathlib import Path
from typing import Optional

import pyarrow.csv as pacsv
import pyarrow.feather as feather

logger = logging.getLogger(__name__)

CSV_EXTENSIONS = {".csv", ".txt", ".tsv"}
FEATHER_EXTENSIONS = {".feather", ".arrow", ".ftr"}


def infer_direction(input_file: str, output_file: str) -> str:
    """
    Infer conversion direction from file extensions.

    Returns:
        "csv2feather" or "feather2csv"
    """
    in_ext = Path(input_file).suffix.lower()
    out_ext = Path(output_file).suffix.lower()

    if in_ext in CSV_EXTENSIONS and out_ext in FEATHER_EXTENSIONS:
        return "csv2feather"
    if in_ext in FEATHER_EXTENSIONS and out_ext in CSV_EXTENSIONS:
        return "feather2csv"
    raise ValueError(
        f"Cannot infer direction from extensions '{in_ext}' -> '{out_ext}'. "
        "Set 'direction' to 'csv2feather' or 'feather2csv' in the config."
    )


def csv_to_feather(
    input_file: str,
    output_file: str,
    delimiter: str = ",",
    encoding: str = "utf8",
    compression: Optional[str] = "zstd",
):
    """
    Convert a CSV file to Feather (Arrow IPC) format.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output Feather file
        delimiter: CSV field delimiter
        encoding: CSV file encoding
        compression: Feather compression ("zstd", "lz4" or "uncompressed")
    """
    table = pacsv.read_csv(
        input_file,
        read_options=pacsv.ReadOptions(encoding=encoding),
        parse_options=pacsv.ParseOptions(delimiter=delimiter),
    )
    logger.info(f"Read {table.num_rows} rows x {table.num_columns} columns from {input_file}")

    feather.write_feather(table, output_file, compression=compression)
    logger.info(f"Wrote Feather file: {output_file}")


def feather_to_csv(
    input_file: str,
    output_file: str,
    delimiter: str = ",",
    include_header: bool = True,
):
    """
    Convert a Feather (Arrow IPC) file to CSV format (UTF-8).

    Args:
        input_file: Path to input Feather file
        output_file: Path to output CSV file
        delimiter: CSV field delimiter
        include_header: Write column names as first line
    """
    table = feather.read_table(input_file)
    logger.info(f"Read {table.num_rows} rows x {table.num_columns} columns from {input_file}")

    pacsv.write_csv(
        table,
        output_file,
        write_options=pacsv.WriteOptions(delimiter=delimiter, include_header=include_header),
    )
    logger.info(f"Wrote CSV file: {output_file}")


def convert(
    input_file: str,
    output_file: str,
    direction: Optional[str] = None,
    delimiter: str = ",",
    encoding: str = "utf8",
    compression: Optional[str] = "zstd",
    include_header: bool = True,
):
    """
    Convert between CSV and Feather. Direction is inferred from extensions if not given.
    """
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    if direction is None:
        direction = infer_direction(input_file, output_file)

    logger.info(f"Converting ({direction}): {input_file} -> {output_file}")

    if direction == "csv2feather":
        csv_to_feather(input_file, output_file, delimiter, encoding, compression)
    elif direction == "feather2csv":
        feather_to_csv(input_file, output_file, delimiter, include_header)
    else:
        raise ValueError(f"Unknown direction '{direction}'. Use 'csv2feather' or 'feather2csv'.")
