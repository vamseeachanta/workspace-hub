#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-digitalmodel/.claude/skills}"

if [[ ! -d "$ROOT" ]]; then
  echo "Skills root not found: $ROOT" >&2
  exit 2
fi

updated=0

while IFS= read -r -d '' file; do
  first_line="$(head -n1 "$file" | tr -d '\r')"
  if [[ "$first_line" == "---" ]]; then
    continue
  fi

  skill_name="$(basename "$(dirname "$file")")"
  tmp_file="$(mktemp)"

  {
    printf '%s\n' '---'
    printf 'name: %s\n' "$skill_name"
    printf 'description: TODO - describe what this skill does and when to use it.\n'
    printf '%s\n\n' '---'
    cat "$file"
  } > "$tmp_file"

  mv "$tmp_file" "$file"
  echo "Added frontmatter: $file"
  updated=$((updated + 1))
done < <(find "$ROOT" -type f -name 'SKILL.md' -print0)

echo "Updated files: $updated"
