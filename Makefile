.PHONY: help install test lint format-check run check

APP ?= ia-convert
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
