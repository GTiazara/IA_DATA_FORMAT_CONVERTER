from pathlib import Path

import pyarrow as pa
import pytest
from pyarrow import feather

from ia_data_format_converter.errors import InvalidOptionError, UnknownFormatError
from ia_data_format_converter.writers import available_formats, get_writer


@pytest.fixture
def table() -> pa.Table:
    return pa.table({"x": [1, 2, None], "y": ["a", "b", "c"]})


def test_available_formats_contains_feather():
    assert "feather" in available_formats()


def test_unknown_format_lists_available():
    with pytest.raises(UnknownFormatError, match="parquet.*feather"):
        get_writer("parquet")


@pytest.mark.parametrize("compression", [None, "lz4", "zstd", "uncompressed"])
def test_feather_roundtrip(tmp_path: Path, table: pa.Table, compression: str | None):
    path = tmp_path / "out.feather"
    options = {} if compression is None else {"compression": compression}

    get_writer("feather").write(table, path, **options)

    assert feather.read_table(path).equals(table)


def test_feather_default_compression_is_lz4():
    assert get_writer("feather").validate_options() == {"compression": "lz4"}


def test_feather_invalid_compression(tmp_path: Path, table: pa.Table):
    path = tmp_path / "out.feather"
    with pytest.raises(InvalidOptionError, match="gzip.*lz4, zstd, uncompressed"):
        get_writer("feather").write(table, path, compression="gzip")
    assert not path.exists()
