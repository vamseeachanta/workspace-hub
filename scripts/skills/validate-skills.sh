#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.claude/skills}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || pwd)"

if [[ ! -d "$ROOT" ]]; then
  echo "Skills root not found: $ROOT" >&2
  exit 2
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to validate skill frontmatter" >&2
  exit 2
fi

export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.claude/state/uv-cache}"
exec uv run --no-project --with pyyaml python "$SCRIPT_DIR/validate_skills_frontmatter.py" "$ROOT"
