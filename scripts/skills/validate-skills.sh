#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-digitalmodel/.claude/skills}"

if [[ ! -d "$ROOT" ]]; then
  echo "Skills root not found: $ROOT" >&2
  exit 2
fi

fail=0
checked=0

while IFS= read -r -d '' file; do
  checked=$((checked + 1))
  first_line="$(head -n1 "$file" | tr -d '\r')"
  if [[ "$first_line" != "---" ]]; then
    echo "Missing frontmatter start: $file"
    fail=1
    continue
  fi

  if ! awk 'NR==1 { next } /^---[[:space:]]*$/ { found=1; exit } END { exit(found?0:1) }' "$file"; then
    echo "Missing frontmatter end: $file"
    fail=1
    continue
  fi

  frontmatter="$(awk '
    NR==1 { next }           # skip opening ---
    /^---[[:space:]]*$/ { exit }
    { sub(/\r$/, ""); print }
  ' "$file")"

  if ! printf '%s\n' "$frontmatter" | grep -Eq '^name:[[:space:]]*[^[:space:]].*'; then
    echo "Missing or empty name: $file"
    fail=1
  fi

  if ! printf '%s\n' "$frontmatter" | grep -Eq '^description:[[:space:]]*[^[:space:]].*'; then
    echo "Missing or empty description: $file"
    fail=1
  fi
done < <(find "$ROOT" -type f -name 'SKILL.md' -print0)

if [[ "$checked" -eq 0 ]]; then
  echo "No SKILL.md files found under: $ROOT" >&2
  exit 2
fi

if [[ "$fail" -ne 0 ]]; then
  echo "Skill validation failed."
  exit 1
fi

echo "Skill validation passed ($checked files)."
