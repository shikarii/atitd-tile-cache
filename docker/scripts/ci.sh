#!/usr/bin/env bash
set -euo pipefail

uv sync --group dev
uv run ruff check .
uv run ruff format --check .
