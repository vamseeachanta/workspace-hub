#!/usr/bin/env bash
# Shell wrapper for extract-url.py
# Usage: bash scripts/data/doc-intelligence/run-extract-url.sh --url <url> [--domain <domain>] [--output <path>]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

PYTHONPATH="${REPO_ROOT}" \
  uv run --no-project \
    --with pyyaml --with pdfplumber --with requests --with beautifulsoup4 \
    python "${REPO_ROOT}/scripts/data/doc-intelligence/extract-url.py" "$@"
