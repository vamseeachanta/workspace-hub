#!/usr/bin/env bash
# wiki-cross-links.sh — Cross-wiki link discovery wrapper
#
# Scans all wiki directories for concept overlap and discovers
# cross-wiki links using fuzzy matching on titles, tags, and keywords.
#
# Usage:
#   bash scripts/knowledge/wiki-cross-links.sh --dry-run   # report only
#   bash scripts/knowledge/wiki-cross-links.sh --apply      # update pages
#
# Issue: #2011
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "$REPO_ROOT"
exec uv run scripts/knowledge/wiki-cross-links.py "$@"
