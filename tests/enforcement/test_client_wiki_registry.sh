#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

uv run --frozen pytest tests/enforcement/test_client_wiki_registry.py -q
