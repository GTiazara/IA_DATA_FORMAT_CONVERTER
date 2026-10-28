"""Feather (Arrow IPC v2) writer."""

from pathlib import Path
from typing import Any

import pyarrow as pa
from pyarrow import feather

from ia_data_format_converter.errors import InvalidOptionError

COMPRESSIONS = ("lz4", "zstd", "uncompressed")


class FeatherWriter:
    name = "feather"
    extension = ".feather"

    def validate_options(self, compression: str | None = None, **extra: Any) -> dict[str, Any]:
        if extra:
            raise InvalidOptionError(
                f"Unsupported option(s) for feather: {', '.join(sorted(extra))}"
            )
        compression = compression or "lz4"
        if compression not in COMPRESSIONS:
            raise InvalidOptionError(
                f"Invalid compression {compression!r}. Accepted values: {', '.join(COMPRESSIONS)}"
            )
        return {"compression": compression}

    def write(self, table: pa.Table, path: Path, **options: Any) -> None:
        compression = self.validate_options(**options)["compression"]
        feather.write_feather(table, path, compression=compression, version=2)
