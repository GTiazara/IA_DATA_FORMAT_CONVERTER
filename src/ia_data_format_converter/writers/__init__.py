"""Registry of output format writers."""

from pathlib import Path
from typing import Any, Protocol

import pyarrow as pa

from ia_data_format_converter.errors import UnknownFormatError
from ia_data_format_converter.writers.feather import FeatherWriter


class Writer(Protocol):
    name: str
    extension: str

    def validate_options(self, **options: Any) -> dict[str, Any]:
        """Return normalized options or raise InvalidOptionError."""
        ...

    def write(self, table: pa.Table, path: Path, **options: Any) -> None: ...


_REGISTRY: dict[str, Writer] = {writer.name: writer for writer in (FeatherWriter(),)}


def available_formats() -> list[str]:
    """Return the names of the registered output formats."""
    return sorted(_REGISTRY)


def get_writer(name: str) -> Writer:
    """Return the writer registered under ``name``."""
    try:
        return _REGISTRY[name]
    except KeyError:
        raise UnknownFormatError(
            f"Unknown output format {name!r}. Available formats: {', '.join(available_formats())}"
        ) from None
