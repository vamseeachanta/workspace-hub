#!/usr/bin/env bash
# check-harness-file-size.sh — #2322
# Enforce the 20-line cap on agent harness files
# (CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md) per
# .claude/rules/coding-style.md "Agent Harness Files".
#
# Usage:
#   scripts/enforcement/check-harness-file-size.sh [--max=<N>] [<file>...]
#
# With no positional args, scans the repo for the four harness filenames,
# excluding well-known content dirs that contain look-alike files:
#   - knowledge/wikis/**         (wiki content, not live harness)
#   - config/agents/**/memory-snapshots/** (archived state, not live)
#   - _archive/**                (historical)
#   - **/tests/fixtures/**       (test fixtures)
#   - **/node_modules/**, **/venv/**, **/.git/** (vendored)
#
# With positional args, scans exactly those files; the exclusions do not
# apply (useful for tests).
#
# Bypass: ALLOW_HARNESS_OVERSIZE=1 (logs to stderr).

set -euo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SELF_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SELF_DIR")"

MAX_LINES=20
declare -a POSITIONAL=()

while (( $# > 0 )); do
  case "$1" in
    --max=*) MAX_LINES="${1#*=}"; shift ;;
    --max)   MAX_LINES="${2:?--max requires a value}"; shift 2 ;;
    --)      shift; POSITIONAL+=("$@"); break ;;
    -*)      echo "check-harness-file-size: unknown flag: $1" >&2; exit 2 ;;
    *)       POSITIONAL+=("$1"); shift ;;
  esac
done

is_excluded_path() {
  local p="$1"
  case "$p" in
    */knowledge/wikis/*)            return 0 ;;
    */config/agents/*/memory-snapshots/*) return 0 ;;
    */_archive/*)                   return 0 ;;
    */tests/fixtures/*)             return 0 ;;
    */node_modules/*)               return 0 ;;
    */venv/*)                       return 0 ;;
    */.git/*)                       return 0 ;;
  esac
  return 1
}

declare -a TARGETS=()
if (( ${#POSITIONAL[@]} == 0 )); then
  while IFS= read -r f; do
    local_abs="$REPO_ROOT/$f"
    is_excluded_path "$local_abs" && continue
    TARGETS+=("$local_abs")
  done < <(
    cd "$REPO_ROOT" && \
    git ls-files 'CLAUDE.md' 'MEMORY.md' 'AGENTS.md' 'GEMINI.md' \
                 '**/CLAUDE.md' '**/MEMORY.md' '**/AGENTS.md' '**/GEMINI.md' \
    | sort -u
  )
else
  for arg in "${POSITIONAL[@]}"; do
    [[ -f "$arg" ]] || { echo "check-harness-file-size: not a file: $arg" >&2; exit 2; }
    TARGETS+=("$arg")
  done
fi

declare -a OFFENDERS=()
for f in "${TARGETS[@]}"; do
  # Count lines. `wc -l` counts \n characters. For a file whose final line
  # lacks a trailing newline, we still want to count that partial line, so
  # add 1 when the last byte is NOT a newline.
  # Note: $(...) strips trailing newlines, so read the last byte via a
  # sentinel trick: append 'x', then peel it off.
  count="$(wc -l < "$f")"
  last="$(tail -c1 "$f"; printf x)"
  last="${last%x}"
  [[ -s "$f" && "$last" != $'\n' ]] && count=$((count + 1))
  if (( count > MAX_LINES )); then
    OFFENDERS+=("$f:$count")
    printf '%s: %d lines (>%d)\n' "$f" "$count" "$MAX_LINES"
  fi
done

if (( ${#OFFENDERS[@]} > 0 )); then
  if [[ "${ALLOW_HARNESS_OVERSIZE:-0}" == "1" ]]; then
    echo "check-harness-file-size: ${#OFFENDERS[@]} oversize file(s); ALLOW_HARNESS_OVERSIZE=1 bypass in effect" >&2
    exit 0
  fi
  echo "" >&2
  echo "check-harness-file-size: ${#OFFENDERS[@]} file(s) exceed the ${MAX_LINES}-line cap." >&2
  echo "  Migrate excess content to a skill or doc per .claude/rules/coding-style.md." >&2
  echo "  One-shot bypass (logged): ALLOW_HARNESS_OVERSIZE=1 ..." >&2
  exit 1
fi
exit 0
