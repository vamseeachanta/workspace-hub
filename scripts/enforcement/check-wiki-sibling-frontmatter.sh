#!/usr/bin/env bash
# check-wiki-sibling-frontmatter.sh — workspace-hub #2778 wrapper.
# Thin .sh wrapper that exec's the Python implementation. Lets hook callers
# invoke by .sh filename; canonical logic lives in the .py sibling.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/check-wiki-sibling-frontmatter.py" "$@"
