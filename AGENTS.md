# Instructions for Python Utility Projects

Use this guide as the baseline for new Python command-line tools packaged with Poetry. Adapt names and optional components to the project; do not add layers or dependencies without a concrete need.

## Architecture

- Use a `src/` layout and one importable package for the project. Group related operations into modules or subpackages instead of creating unrelated top-level packages for each command.
- Keep command-line parsing and process exit handling in the CLI layer. Keep file operations, transformations, and business rules in importable functions that do not read `sys.argv`, call `sys.exit`, or configure global logging.
- Let the CLI load and validate configuration, call the application logic, report errors, and return a process status. Keep reusable functions independently callable and testable.
- Export only the intended public Python API from the package. Do not import CLI modules from `__init__.py`.
- Use type hints for public functions and clear exceptions for invalid inputs or failed operations.

Recommended starting layout:

```text
project-name/
├── conf/
│   ├── example.yaml
│   └── README.md
├── src/
│   └── project_package/
│       ├── __init__.py
│       ├── __main__.py       # Optional: enables python -m project_package
│       ├── cli.py            # Argument parsing and CLI orchestration
│       ├── config.py         # Configuration loading and validation, if needed
│       └── operations.py     # Reusable application logic
├── tests/
│   ├── test_operations.py
│   └── test_cli.py
├── .gitignore
├── Makefile
├── README.md
├── pyproject.toml
└── poetry.lock
```

For multiple substantial operations, split `operations.py` into focused modules and map each command to a small CLI function. Avoid a generic framework for a handful of commands.

## Poetry and Metadata

- Keep project metadata and runtime dependencies in `pyproject.toml`; commit `poetry.lock` for applications and tools so installs are reproducible.
- Provide a meaningful description, supported Python version, README, and console-script entry points. Add a license only when the project owner has chosen one.
- Put test and quality tools in a development dependency group, not in runtime dependencies.
- Keep the package build configuration consistent with the `src/` layout.
- Do not commit virtual environments, generated output, large data files, or secrets. Keep small, sanitized configuration examples in `conf/`.

Example packaging configuration (replace the names and versions):

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Short description of the tools"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
project-tool = "project_package.cli:main"

[tool.poetry]
packages = [{ include = "project_package", from = "src" }]

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
ruff = "^0.9"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

For several commands, declare one console script per user-facing command and point each at a named CLI function. Keep command names stable and document them in the README.

## Configuration

- Store tracked YAML examples and project-owned configuration templates in `conf/`; do not scatter them at the repository root.
- Keep secrets and machine-specific paths out of committed configuration. Read sensitive values from environment variables or an approved secret store.
- Validate required keys and value types at the configuration boundary, and report which setting is invalid.
- Document how relative paths are resolved. Prefer predictable paths and avoid silently depending on the caller's current directory.
- Do not silently overwrite an existing output unless that behavior is explicitly requested or documented.

## Tests and Quality

- Add tests for every operation and important error path. Use small temporary files and `tmp_path` for filesystem and HDF5 integration tests; do not depend on private or large production data.
- Test CLI behavior separately from core logic, including invalid configuration and a non-zero failure status.
- Keep tests deterministic and runnable offline where practical.
- Run tests and lint checks before considering a change complete. Add CI to run the same checks when the repository has a CI system.

## Makefile

Provide a small, discoverable Makefile. Keep each target a thin wrapper around Poetry and the project's registered commands; do not duplicate application logic in Make recipes.

```make
.PHONY: help install test lint format-check run check

APP ?= project-tool
ARGS ?= --help

help:
	@echo "install       Install dependencies"
	@echo "test          Run tests"
	@echo "lint          Check code with Ruff"
	@echo "format-check  Check formatting with Ruff"
	@echo "run           Run the application (APP=... ARGS=...)"
	@echo "check         Run tests and lint"

install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .

format-check:
	poetry run ruff format --check .

run:
	poetry run $(APP) $(ARGS)

check: lint test
```

Examples:

```bash
make install
make test
make check
make run ARGS="--config conf/example.yaml"
make run APP=another-command ARGS="--help"
```

## Documentation

The README must explain installation, supported Python version, available commands, configuration examples, expected inputs and outputs, and how to run tests. Use paths under `conf/` in examples and ensure documented commands match the registered console scripts and Makefile.