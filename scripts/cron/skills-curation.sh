#!/usr/bin/env bash
# skills-curation.sh — Wrapper for the weekly Claude-driven skills curation cron.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash scripts/cron/skills-curation.sh [--dry-run]

Options:
  --dry-run   Print the Claude CLI invocation without executing it.
  -h, --help  Show this help text.
EOF
}

DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
PROMPT="Archive stale skills (unused >90 days), validate frontmatter (name, description, type fields) on all .claude/skills/ files, and report findings."
CLAUDE_CMD=(claude -p "$PROMPT" --dangerously-skip-permissions)

cd "$WORKSPACE_HUB"

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf 'Working directory: %s\n' "$WORKSPACE_HUB"
  printf 'Command: claude -p "%s" --dangerously-skip-permissions\n' "$PROMPT"
  exit 0
fi

exec "${CLAUDE_CMD[@]}"
