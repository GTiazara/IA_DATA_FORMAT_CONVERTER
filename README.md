# IA_DATA_FORMAT_CONVERTER

Command-line tool and Python library that converts tabular CSV data (e.g. datasets used for
machine learning or other AI tasks) into binary formats that load faster and keep column types.

Supported output formats:

| Format    | Extension  | Status    |
|-----------|------------|-----------|
| `feather` | `.feather` | available |
| Apache Parquet, Zarr, SQLite, ... | | planned |

## Requirements

- Python >= 3.11
- [Poetry](https://python-poetry.org/) >= 2.0

## Installation

```bash
make install        # or: poetry install
```

## Usage

```bash
poetry run ia-convert INPUT.csv --to feather [-o OUTPUT] [options]
```

| Option              | Default                              | Description                                       |
|---------------------|--------------------------------------|---------------------------------------------------|
| `INPUT`             | —                                    | Input CSV file with a header row                  |
| `--to FORMAT`       | —                                    | Output format (`feather`)                         |
| `-o, --output PATH` | input path with the format extension | Output file                                       |
| `--sep CHAR`        | `,`                                  | CSV field separator                               |
| `--encoding NAME`   | `utf-8`                              | CSV file encoding (e.g. `latin-1`)                |
| `--compression C`   | `lz4`                                | Feather compression: `lz4`, `zstd`, `uncompressed`|
| `--overwrite`       | off                                  | Replace an existing output file                   |
| `--config FILE`     | —                                    | YAML file providing default values for the options|

Examples:

```bash
poetry run ia-convert data/train.csv --to feather                  # writes data/train.feather
poetry run ia-convert data/train.csv --to feather -o out/train.feather --compression zstd
poetry run ia-convert data/eu.csv --to feather --sep ";" --encoding latin-1
poetry run ia-convert --config conf/example.yaml
poetry run ia-convert --config conf/conf.yaml
make run ARGS="--config conf/example.yaml"
```

### Inputs and outputs

- **Input**: a CSV file with a header row. Column types (integer, float, boolean, string,
  date/time) are inferred; empty cells become null values. The whole file is loaded in memory.
- **Output**: a Feather (Arrow IPC v2) file readable with `pyarrow.feather.read_table`,
  `pandas.read_feather` or `polars.read_ipc`.
- An existing output file is never replaced unless `--overwrite` is given. Output is written
  atomically: a failed conversion leaves no partial file.
- On error, a message is printed on stderr and the command exits with a non-zero status.

### Configuration

See [conf/README.md](conf/README.md), [conf/example.yaml](conf/example.yaml), and
[conf/conf.yaml](conf/conf.yaml). Run your own configuration with
`poetry run ia-convert --config conf/conf.yaml`; ensure its input and output paths match your
environment. Command-line arguments override values from the configuration file; relative paths
in the file are resolved against the file's directory.

### Python API

```python
from ia_data_format_converter import available_formats, convert

convert("data/train.csv", "data/train.feather", "feather", compression="zstd")
```

## Adding an output format

Each output format is a *writer* in `src/ia_data_format_converter/writers/`, exposing `name`,
`extension`, `validate_options(**options)` and `write(table, path, **options)` where `table` is
a `pyarrow.Table`. To add a format (Parquet, Zarr, SQLite, ...):

1. Create `writers/<format>.py` implementing the writer.
2. Register an instance in `_REGISTRY` in `writers/__init__.py`.
3. Add tests in `tests/test_writers.py`.

The CLI picks up the new format automatically.

## Development

```bash
make test           # run tests
make lint           # ruff check
make format-check   # ruff format --check
make check          # lint + tests
```
