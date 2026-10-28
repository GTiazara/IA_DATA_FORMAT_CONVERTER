from pathlib import Path

import pyarrow as pa
import pytest

from ia_data_format_converter.errors import (
    ConversionError,
    InputFileError,
    InvalidOptionError,
    OutputExistsError,
    UnknownFormatError,
)
from ia_data_format_converter.readers import read_csv


def test_errors_share_base_class():
    for exc in (InputFileError, InvalidOptionError, OutputExistsError, UnknownFormatError):
        assert issubclass(exc, ConversionError)


def test_infers_column_types_and_nulls(sample_csv: Path):
    table = read_csv(sample_csv)

    assert table.column_names == ["id", "score", "label"]
    assert table.num_rows == 3
    assert pa.types.is_integer(table.schema.field("id").type)
    assert pa.types.is_floating(table.schema.field("score").type)
    assert pa.types.is_string(table.schema.field("label").type)
    assert table.column("score").to_pylist() == [0.5, 1.25, None]


def test_semicolon_separator(tmp_path: Path):
    path = tmp_path / "semi.csv"
    path.write_text("a;b\n1;x\n2;y\n", encoding="utf-8")

    table = read_csv(path, sep=";")

    assert table.column_names == ["a", "b"]
    assert table.column("b").to_pylist() == ["x", "y"]


def test_latin1_encoding(tmp_path: Path):
    path = tmp_path / "latin.csv"
    path.write_bytes("ville\nBézier\nÉvry\n".encode("latin-1"))

    table = read_csv(path, encoding="latin-1")

    assert table.column("ville").to_pylist() == ["Bézier", "Évry"]


def test_missing_file(tmp_path: Path):
    with pytest.raises(InputFileError, match="missing.csv"):
        read_csv(tmp_path / "missing.csv")


def test_empty_file(tmp_path: Path):
    path = tmp_path / "empty.csv"
    path.touch()
    with pytest.raises(InputFileError, match="empty"):
        read_csv(path)


def test_inconsistent_field_count(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text("a,b\n1,2\n3,4,5\n", encoding="utf-8")
    with pytest.raises(InputFileError):
        read_csv(path)


def test_unknown_encoding(sample_csv: Path):
    with pytest.raises(InvalidOptionError, match="encoding"):
        read_csv(sample_csv, encoding="not-an-encoding")
