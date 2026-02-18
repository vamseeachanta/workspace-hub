#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  echo "Run this script from inside a git repository." >&2
  exit 2
fi

hook_path="$repo_root/.git/hooks/pre-commit"
validator_cmd='bash scripts/skills/validate-skills.sh'

mkdir -p "$(dirname "$hook_path")"

if [[ -f "$hook_path" ]] && grep -Fq "$validator_cmd" "$hook_path"; then
  echo "Pre-commit hook already contains skill validator."
  exit 0
fi

if [[ -f "$hook_path" ]] && [[ -s "$hook_path" ]]; then
  cat >> "$hook_path" <<'EOF'

# Validate skills frontmatter
bash scripts/skills/validate-skills.sh
EOF
else
  cat > "$hook_path" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Validate skills frontmatter
bash scripts/skills/validate-skills.sh
EOF
fi

chmod +x "$hook_path"
echo "Installed pre-commit hook at: $hook_path"
