#!/usr/bin/env bash
# skills-curation.sh — Thin wrapper for the deterministic weekly skills audit.
# Launches scripts/skills/weekly_skills_audit.py with correct env.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash scripts/cron/skills-curation.sh [--dry-run]

Deterministic weekly skills audit wrapper.

Options:
  --dry-run   Print the audit command without executing it.
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
WORKSPACE_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export WORKSPACE_HUB

AUDIT_SCRIPT="${WORKSPACE_HUB}/scripts/skills/weekly_skills_audit.py"
AUDIT_CMD=(uv run --no-project python "$AUDIT_SCRIPT")

# Forward output root if set
if [[ -n "${SKILLS_AUDIT_OUTPUT_ROOT:-}" ]]; then
  AUDIT_CMD+=(--output-dir "$SKILLS_AUDIT_OUTPUT_ROOT")
fi

cd "$WORKSPACE_HUB"

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf 'Working directory: %s\n' "$WORKSPACE_HUB"
  printf 'Command: uv run --no-project python %s' "$AUDIT_SCRIPT"
  if [[ -n "${SKILLS_AUDIT_OUTPUT_ROOT:-}" ]]; then
    printf ' --output-dir %s' "$SKILLS_AUDIT_OUTPUT_ROOT"
  fi
  printf '\n'
  exit 0
fi

exec "${AUDIT_CMD[@]}"
