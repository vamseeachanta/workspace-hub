#!/usr/bin/env bash
# check-model-id-sourcing.sh — guard against NEW hardcoded model IDs outside the registry.
#
# Part of the config/model regression guard (#3060, harden-ecosystem epic #3058).
# Generalizes #3055's model-swap preflight: the next model swap should be a
# `config/agents/model-registry.yaml` edit, not the grep-archaeology of 2026-06-13.
#
# RATCHET design: current in-scope literals (pricing tables, the migration table,
# provider-CLI args, fallbacks, skills) are grandfathered as occurrence keys; the
# guard flags occurrence keys NOT in the baseline — i.e. newly introduced
# hardcodes. Advisory by default; --enforce exits 1 on new or stale entries.
#
# Usage:
#   check-model-id-sourcing.sh                 # scan tracked scope, advisory
#   check-model-id-sourcing.sh --enforce       # exit 1 if NEW literals found
#   check-model-id-sourcing.sh --update-baseline
#   check-model-id-sourcing.sh <file>...       # scan only these (pre-commit/tests)
#   --baseline <path>  (default scripts/enforcement/model-id-baseline.txt)
#
# An individual line is exempt if it contains an allow-token:
#   latest_models | registry_model(...) | # model-id-ok
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$ROOT" || exit 1

BASELINE="scripts/enforcement/model-id-baseline.txt"
MODE="advisory"; [ "${MODEL_ID_ENFORCE:-}" = "1" ] && MODE="enforce"
UPDATE=0
FILES=()
DEFAULT_SCOPE=1
while [ $# -gt 0 ]; do
  case "$1" in
    --enforce) MODE="enforce" ;;
    --advisory) MODE="advisory" ;;
    --update-baseline) UPDATE=1 ;;
    --baseline) BASELINE="$2"; shift ;;
    *) FILES+=("$1"); DEFAULT_SCOPE=0 ;;
  esac
  shift
done

# model-ID literal pattern; tier aliases (claude_primary, "opus") deliberately excluded
PAT='(claude-[A-Za-z0-9][A-Za-z0-9._-]*-[0-9][A-Za-z0-9._-]*|gpt-[0-9][A-Za-z0-9._-]*|gemini-[0-9][A-Za-z0-9._-]*|o[0-9][A-Za-z0-9._-]*|codex-mini[A-Za-z0-9._-]*)'
ALLOW='(^|[^A-Za-z0-9_])latest_models([^A-Za-z0-9_]|$)|(^|[^A-Za-z0-9_])registry_model[[:space:]]*\(|# model-id-ok'
# self + the registry are never scanned
SELF='scripts/enforcement/check-model-id-sourcing.sh|scripts/enforcement/model-id-baseline.txt|config/agents/model-registry.yaml'

scope_files() {
  if [ "${#FILES[@]}" -gt 0 ]; then printf '%s\n' "${FILES[@]}"; return; fi
  git ls-files 'scripts' 'config' '.claude/skills' '.agents/skills' \
    '.claude/agent-library' '.agents/agent-library' 2>/dev/null |
    grep -E '\.(py|sh|ya?ml|json|md)$'
}

# emit "path<TAB>token<TAB>line-hash<TAB>ordinal" for every offending occurrence.
# The occurrence key catches added hardcodes even when the same file already has the
# same token, while the line hash avoids line-number churn when unrelated lines move.
findings() {
  local f line_no line line_hash tok
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    echo "$f" | grep -qE "$SELF" && continue
    grep -nIE "$PAT" "$f" 2>/dev/null | while IFS=: read -r line_no line; do
      printf '%s\n' "$line" | grep -qE "$ALLOW" && continue
      line_hash="$(printf '%s' "$line" | cksum | awk '{print $1 ":" $2}')"
      # extract every model-id token on the line
      printf '%s\n' "$line" | grep -oE "$PAT" | sort -u | while IFS= read -r tok; do
        printf '%s\t%s\t%s\n' "$f" "$tok" "$line_hash"
      done
    done
  done < <(scope_files) |
    sort |
    awk -F '\t' 'BEGIN { OFS = "\t" } { key = $1 FS $2 FS $3; seen[key] += 1; print $1, $2, $3, seen[key] }' |
    sort -u
}

found="$(findings)"

if [ "$UPDATE" = "1" ]; then
  printf '# model-id-baseline.txt — grandfathered (path<TAB>model-id<TAB>line-hash<TAB>ordinal) occurrences (#3060).\n' > "$BASELINE"
  printf '# Regenerate: scripts/enforcement/check-model-id-sourcing.sh --update-baseline\n' >> "$BASELINE"
  printf '%s\n' "$found" | grep -v '^$' >> "$BASELINE"
  echo "baseline updated: $(printf '%s\n' "$found" | grep -vc '^$') entries -> $BASELINE"
  exit 0
fi

# NEW = findings not present in the baseline
base_tmp="$(mktemp)"
found_tmp="$(mktemp)"
trap 'rm -f "$base_tmp" "$found_tmp"' EXIT
printf '%s\n' "$found" | grep -v '^$' | sort -u > "$found_tmp"
[ -f "$BASELINE" ] && grep -vE '^\s*#|^\s*$' "$BASELINE" | sort -u > "$base_tmp"
new="$(comm -23 "$found_tmp" "$base_tmp" 2>/dev/null)"
stale=""
if [ "$DEFAULT_SCOPE" = "1" ]; then
  stale="$(comm -13 "$found_tmp" "$base_tmp" 2>/dev/null)"
fi

new_count="$(printf '%s\n' "$new" | grep -vc '^$')"
total_count="$(printf '%s\n' "$found" | grep -vc '^$')"
stale_count="$(printf '%s\n' "$stale" | grep -vc '^$')"
echo "model-id-sourcing: $total_count in-scope literal(s), $new_count NOT in baseline, $stale_count STALE baseline entr$( [ "$stale_count" = "1" ] && echo "y" || echo "ies" )"
if [ "$new_count" -gt 0 ]; then
  echo "NEW hardcoded model IDs (source from the registry, or add '# model-id-ok', or --update-baseline if intentional):"
  printf '%s\n' "$new" | grep -v '^$' | sed 's/^/  /'
fi
if [ "$stale_count" -gt 0 ]; then
  echo "STALE baselined model IDs (regenerate with --update-baseline if removals are intentional):"
  printf '%s\n' "$stale" | grep -v '^$' | sed 's/^/  /'
fi

if [ "$MODE" = "enforce" ] && { [ "$new_count" -gt 0 ] || [ "$stale_count" -gt 0 ]; }; then
  exit 1
fi
exit 0
