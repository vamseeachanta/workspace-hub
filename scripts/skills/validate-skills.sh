#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || pwd)"
ROOT="${1:-$REPO_ROOT/.claude/skills}"
if [[ "$ROOT" != /* ]]; then
  ROOT="$REPO_ROOT/$ROOT"
fi

source "$REPO_ROOT/scripts/lib/uv-env.sh"
source "$REPO_ROOT/scripts/lib/uv-resolver.sh"

if [[ ! -d "$ROOT" ]]; then
  echo "Skills root not found: $ROOT" >&2
  exit 2
fi

# uv_env_setup preserves explicit UV_CACHE_DIR and otherwise derives the repo-local default.
uv_env_setup "$REPO_ROOT"

UV=""
if ! UV="$(resolve_uv)"; then
  exit 2
fi

exec "$UV" run --no-project --with pyyaml python "$SCRIPT_DIR/validate_skills_frontmatter.py" "$ROOT"
