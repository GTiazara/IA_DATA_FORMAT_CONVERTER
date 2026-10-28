"""Loading and validation of YAML configuration files."""

from pathlib import Path
from typing import Any

import yaml

# Expected type for each allowed configuration key.
_SCHEMA: dict[str, type] = {
    "input": str,
    "output": str,
    "to": str,
    "sep": str,
    "encoding": str,
    "compression": str,
    "overwrite": bool,
}
_PATH_KEYS = ("input", "output")


class ConfigError(Exception):
    """The configuration file is missing or invalid."""


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a YAML configuration file.

    Relative ``input`` and ``output`` paths are resolved against the directory of the file.
    """
    path = Path(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"Cannot read configuration file {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in configuration file {path}: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"Configuration file {path} must contain a mapping of settings")

    config: dict[str, Any] = {}
    for key, value in data.items():
        expected = _SCHEMA.get(key)
        if expected is None:
            raise ConfigError(
                f"Unknown configuration setting {key!r}. Allowed: {', '.join(_SCHEMA)}"
            )
        if not isinstance(value, expected):
            raise ConfigError(
                f"Invalid value for setting {key!r}: expected {expected.__name__}, "
                f"got {type(value).__name__}"
            )
        if key in _PATH_KEYS:
            value = str((path.parent / value).resolve())
        config[key] = value
    return config
