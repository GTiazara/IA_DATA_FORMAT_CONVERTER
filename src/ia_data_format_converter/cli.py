"""Command-line interface for ia-convert."""

import argparse
import sys
from collections.abc import Sequence
from typing import Any

from ia_data_format_converter.config import ConfigError, load_config
from ia_data_format_converter.converter import convert
from ia_data_format_converter.errors import ConversionError
from ia_data_format_converter.writers import available_formats

_DEFAULTS: dict[str, Any] = {
    "input": None,
    "output": None,
    "to": None,
    "sep": ",",
    "encoding": "utf-8",
    "compression": None,
    "overwrite": False,
}


def build_parser() -> argparse.ArgumentParser:
    formats = available_formats()
    parser = argparse.ArgumentParser(
        prog="ia-convert",
        description="Convert a tabular CSV file into a binary data format.",
        epilog=f"Available output formats: {', '.join(formats)}",
    )
    # Defaults are None so that values from --config are only overridden when given explicitly.
    parser.add_argument("input", nargs="?", help="input CSV file (header row required)")
    parser.add_argument("--to", choices=formats, help="output format")
    parser.add_argument(
        "-o", "--output", help="output file (default: input path with the format extension)"
    )
    parser.add_argument("--sep", help="CSV field separator (default: ',')")
    parser.add_argument("--encoding", help="CSV file encoding (default: utf-8)")
    parser.add_argument(
        "--compression", help="output compression (feather: lz4 [default], zstd, uncompressed)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=None,
        help="replace the output file if it already exists",
    )
    parser.add_argument("--config", help="YAML file providing default values for these options")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = dict(_DEFAULTS)
    try:
        if args.config:
            settings.update(load_config(args.config))
    except ConfigError as exc:
        print(f"ia-convert: error: {exc}", file=sys.stderr)
        return 1
    settings.update({k: v for k, v in vars(args).items() if k != "config" and v is not None})

    if not settings["input"]:
        parser.error("an input CSV file is required (argument or 'input' in --config)")
    if not settings["to"]:
        parser.error("an output format is required (--to or 'to' in --config)")

    options = {}
    if settings["compression"] is not None:
        options["compression"] = settings["compression"]
    try:
        output = convert(
            settings["input"],
            settings["output"],
            settings["to"],
            sep=settings["sep"],
            encoding=settings["encoding"],
            overwrite=settings["overwrite"],
            **options,
        )
    except (ConversionError, OSError) as exc:
        print(f"ia-convert: error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {output}")
    return 0
