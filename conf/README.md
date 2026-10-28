# Configuration

YAML files passed to `ia-convert --config FILE` provide default values for the conversion options.
Explicit command-line arguments always take precedence over the file.

| Key           | Type   | Default                         | Description                                   |
|---------------|--------|---------------------------------|-----------------------------------------------|
| `input`       | string | —                               | Input CSV file (header row required)          |
| `output`      | string | input path + format extension   | Output file                                   |
| `to`          | string | —                               | Output format (`feather`)                     |
| `sep`         | string | `,`                             | CSV field separator (single character)        |
| `encoding`    | string | `utf-8`                         | CSV file encoding (e.g. `latin-1`)            |
| `compression` | string | `lz4`                           | Feather compression: `lz4`, `zstd`, `uncompressed` |
| `overwrite`   | bool   | `false`                         | Replace an existing output file               |

Unknown keys or values of the wrong type are rejected with an error naming the setting.

## Path resolution

Relative `input` and `output` paths are resolved against the directory containing the
configuration file, not the current working directory. With `conf/example.yaml`,
`../data/train.csv` points to `data/train.csv` at the repository root.

Do not commit secrets or machine-specific absolute paths in these files.
