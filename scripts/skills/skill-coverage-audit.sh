#!/usr/bin/env bash
# skill-coverage-audit.sh — Report which SKILL.md files lack any script call reference.
#
# For each SKILL.md, checks if it has a script call via:
#   - Frontmatter `scripts:` field (non-empty list)
#   - Body contains `bash scripts/`, `uv run`, or `bash .claude/skills/`
#
# Exit: 0 = all wired, 1 = gaps found, 2 = usage error
# Output: YAML to stdout (gaps only on exit 1; silent on exit 0)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Ensure uv cache is writable in sandbox/CI environments
export UV_CACHE_DIR="${UV_CACHE_DIR:-${REPO_ROOT}/.cache/uv}"

# --- Defaults ---
SKILL_DIR="${REPO_ROOT}/.claude/skills"

# --- Argument parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill-dir)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --skill-dir requires a path argument" >&2
        exit 2
      fi
      SKILL_DIR="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--skill-dir <path>]" >&2
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$SKILL_DIR" ]]; then
  echo "Error: skill dir not found: ${SKILL_DIR}" >&2
  exit 2
fi

# --- Collect SKILL.md files ---
mapfile -t SKILL_FILES < <(find "$SKILL_DIR" -name "SKILL.md" | sort)

if [[ ${#SKILL_FILES[@]} -eq 0 ]]; then
  exit 0
fi

SKILL_ENTRIES=()
GAP_COUNT=0

for SKILL_FILE in "${SKILL_FILES[@]}"; do
  # Check 1: frontmatter `scripts:` field (non-empty list)
  HAS_FM_SCRIPTS=$(uv run --no-project python -c "
import re, sys
try:
    content = open('${SKILL_FILE}').read()
    parts = content.split('---', 2)
    if len(parts) < 2:
        print('false')
        sys.exit(0)
    fm_text = parts[1]
    # Find scripts: field — match list items under it
    # Match: scripts:\n  - item OR scripts: [item]
    block = re.search(r'^scripts:\s*\n((?:[ \t]+-[^\n]+\n?)+)', fm_text, re.MULTILINE)
    if block and block.group(1).strip():
        print('true')
        sys.exit(0)
    inline = re.search(r'^scripts:\s*\[([^\]]+)\]', fm_text, re.MULTILINE)
    if inline and inline.group(1).strip():
        print('true')
        sys.exit(0)
    print('false')
except Exception:
    print('false')
" 2>/dev/null || echo "false")

  # Check 2: body contains exec patterns
  HAS_BODY_SCRIPTS=false
  if grep -qE '(bash scripts/|uv run|bash \.claude/skills/)' "$SKILL_FILE" 2>/dev/null; then
    HAS_BODY_SCRIPTS=true
  fi

  HAS_SCRIPT_REF=false
  SOURCES=()
  GAPS=()

  if [[ "$HAS_FM_SCRIPTS" == "true" ]]; then
    HAS_SCRIPT_REF=true
    SOURCES+=("frontmatter_scripts")
  fi
  if [[ "$HAS_BODY_SCRIPTS" == "true" ]]; then
    HAS_SCRIPT_REF=true
    SOURCES+=("body_exec_pattern")
  fi

  if [[ "$HAS_SCRIPT_REF" == "false" ]]; then
    GAPS+=("no_frontmatter_scripts")
    GAPS+=("no_exec_pattern")
    GAP_COUNT=$((GAP_COUNT + 1))
  fi

  # Build YAML entry — only store gap entries (cron-safe: silent when clean)
  if [[ "$HAS_SCRIPT_REF" == "false" ]]; then
    SKILL_ENTRIES+=("  - path: ${SKILL_FILE}")
    SKILL_ENTRIES+=("    has_script_ref: false")
    SKILL_ENTRIES+=("    gaps:")
    for gap in "${GAPS[@]}"; do
      SKILL_ENTRIES+=("      - ${gap}")
    done
  fi
done

# --- Output ---
if [[ "$GAP_COUNT" -eq 0 ]]; then
  # Cron-safe: no output on clean run
  exit 0
fi

printf "skills:\n"
for line in "${SKILL_ENTRIES[@]}"; do
  printf "%s\n" "$line"
done
printf "gaps_total: %d\n" "$GAP_COUNT"

exit 1
