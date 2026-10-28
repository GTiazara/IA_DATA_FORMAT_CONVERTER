from pathlib import Path

import pytest
from pyarrow import csv, feather

from ia_data_format_converter import (
    InputFileError,
    InvalidOptionError,
    OutputExistsError,
    UnknownFormatError,
    convert,
)


def test_convert_csv_to_feather(sample_csv: Path, tmp_path: Path):
    output = convert(sample_csv, tmp_path / "out.feather", "feather")

    result = feather.read_table(output)
    assert result.column_names == ["id", "score", "label"]
    assert result.num_rows == 3
    assert result.equals(csv.read_csv(sample_csv))


def test_default_output_path(sample_csv: Path):
    output = convert(sample_csv, None, "feather")
    assert output == sample_csv.with_suffix(".feather")
    assert output.exists()


def test_existing_output_is_kept(sample_csv: Path, tmp_path: Path):
    output = tmp_path / "out.feather"
    output.write_bytes(b"original")

    with pytest.raises(OutputExistsError):
        convert(sample_csv, output, "feather")
    assert output.read_bytes() == b"original"


def test_overwrite_replaces_output(sample_csv: Path, tmp_path: Path):
    output = tmp_path / "out.feather"
    output.write_bytes(b"original")

    convert(sample_csv, output, "feather", overwrite=True)

    assert feather.read_table(output).num_rows == 3


def test_unknown_format_creates_nothing(sample_csv: Path, tmp_path: Path):
    output = tmp_path / "out.parquet"
    with pytest.raises(UnknownFormatError):
        convert(sample_csv, output, "parquet")
    assert list(tmp_path.iterdir()) == [sample_csv]


def test_invalid_compression_creates_nothing(sample_csv: Path, tmp_path: Path):
    with pytest.raises(InvalidOptionError):
        convert(sample_csv, tmp_path / "out.feather", "feather", compression="gzip")
    assert list(tmp_path.iterdir()) == [sample_csv]


def test_malformed_csv_leaves_no_output(tmp_path: Path):
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b\n1,2\n3,4,5\n", encoding="utf-8")

    with pytest.raises(InputFileError):
        convert(bad, tmp_path / "out.feather", "feather")
    assert list(tmp_path.iterdir()) == [bad]


def test_zstd_compression(sample_csv: Path, tmp_path: Path):
    output = convert(sample_csv, tmp_path / "out.feather", "feather", compression="zstd")
    assert feather.read_table(output).num_rows == 3
