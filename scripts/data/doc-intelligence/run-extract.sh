#!/usr/bin/env bash
# Shell wrapper for extract-document.py
# Usage: bash scripts/data/doc-intelligence/run-extract.sh --input <file> [--domain <domain>] [--output <path>]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

PYTHONPATH="${REPO_ROOT}/scripts" \
  uv run --no-project \
    --with pyyaml --with pdfplumber --with python-docx --with openpyxl \
    python "${REPO_ROOT}/scripts/data/doc-intelligence/extract-document.py" "$@"
