from pathlib import Path

import pytest
from pyarrow import feather

from ia_data_format_converter.cli import main


def test_convert_success(sample_csv: Path, tmp_path: Path, capsys):
    output = tmp_path / "out.feather"

    assert main([str(sample_csv), "--to", "feather", "-o", str(output)]) == 0
    assert feather.read_table(output).num_rows == 3
    assert str(output) in capsys.readouterr().out


def test_help_lists_formats(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "feather" in capsys.readouterr().out


def test_implicit_output(sample_csv: Path):
    assert main([str(sample_csv), "--to", "feather"]) == 0
    assert sample_csv.with_suffix(".feather").exists()


def test_overwrite_refused(sample_csv: Path, tmp_path: Path, capsys):
    output = tmp_path / "out.feather"
    output.write_bytes(b"original")

    assert main([str(sample_csv), "--to", "feather", "-o", str(output)]) != 0
    assert "already exists" in capsys.readouterr().err
    assert output.read_bytes() == b"original"


def test_overwrite_allowed(sample_csv: Path, tmp_path: Path):
    output = tmp_path / "out.feather"
    output.write_bytes(b"original")

    assert main([str(sample_csv), "--to", "feather", "-o", str(output), "--overwrite"]) == 0
    assert feather.read_table(output).num_rows == 3


def test_missing_input(tmp_path: Path, capsys):
    missing = tmp_path / "missing.csv"

    assert main([str(missing), "--to", "feather"]) != 0
    err = capsys.readouterr().err
    assert "missing.csv" in err
    assert "Traceback" not in err


def test_unknown_format(sample_csv: Path, capsys):
    with pytest.raises(SystemExit) as exc:
        main([str(sample_csv), "--to", "zarr"])
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "zarr" in err
    assert "feather" in err


def test_unknown_format_from_config(sample_csv: Path, tmp_path: Path, capsys):
    conf = tmp_path / "c.yaml"
    conf.write_text("to: zarr\n")

    assert main([str(sample_csv), "--config", str(conf)]) != 0
    err = capsys.readouterr().err
    assert "zarr" in err
    assert "feather" in err


def test_sep_and_compression_from_config(tmp_path: Path, monkeypatch):
    (tmp_path / "data.csv").write_text("a;b\n1;x\n", encoding="utf-8")
    conf = tmp_path / "c.yaml"
    conf.write_text("input: data.csv\nto: feather\nsep: ';'\ncompression: zstd\n")
    calls = {}

    import ia_data_format_converter.cli as cli

    real_convert = cli.convert

    def spy(*args, **kwargs):
        calls.update(kwargs)
        return real_convert(*args, **kwargs)

    monkeypatch.setattr(cli, "convert", spy)

    assert main(["--config", str(conf)]) == 0
    assert calls["sep"] == ";"
    assert calls["compression"] == "zstd"
    assert feather.read_table(tmp_path / "data.feather").column_names == ["a", "b"]


def test_cli_overrides_config(sample_csv: Path, tmp_path: Path, monkeypatch):
    conf = tmp_path / "c.yaml"
    conf.write_text("to: feather\ncompression: zstd\n")
    calls = {}

    import ia_data_format_converter.cli as cli

    real_convert = cli.convert

    def spy(*args, **kwargs):
        calls.update(kwargs)
        return real_convert(*args, **kwargs)

    monkeypatch.setattr(cli, "convert", spy)

    assert main([str(sample_csv), "--config", str(conf), "--compression", "lz4"]) == 0
    assert calls["compression"] == "lz4"


def test_invalid_config(sample_csv: Path, tmp_path: Path, capsys):
    conf = tmp_path / "c.yaml"
    conf.write_text("compresion: zstd\n")

    assert main([str(sample_csv), "--to", "feather", "--config", str(conf)]) != 0
    assert "compresion" in capsys.readouterr().err
