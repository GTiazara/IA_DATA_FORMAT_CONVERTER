# IA_DATA_FORMAT_CONVERTER

## Modules

### `csv-feather-convert`

Converts CSV -> Feather and Feather -> CSV (direction inferred from extensions or set with `direction`).

```bash
pip install -e .
csv-feather-convert config_csv_to_feather_example.yaml
csv-feather-convert config_feather_to_csv_example.yaml
```

Container: `make build`, then `make run-exec-csv-to-feather` / `make run-exec-feather-to-csv`.
