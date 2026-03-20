#!/usr/bin/env bash
# Sanitize machine names, IPs, and usernames from repo files.
# Usage: ./sanitize-machine-names.sh [--dry-run]
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

MEMORY_DIR="/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory"

# Ordered sed expressions (longer/more-specific patterns first)
SED_ARGS=(
  -e 's/aceengineer-va/home-win/g'
  -e 's/acma-ansys05/licensed-win-1/g'
  -e 's/ACMA-ANSYS05/licensed-win-1/g'
  -e 's/acma-ws014/licensed-win-2/g'
  -e 's/ace-linux-2/dev-secondary/g'
  -e 's/ace-linux-1/dev-primary/g'
  -e 's/ace_linux_2/dev_secondary/g'
  -e 's/ace_linux_1/dev_primary/g'
  -e 's/MacBook Air/macbook-portable/g'
  -e 's/100\.107\.64\.76/10.1.0.1/g'
  -e 's/100\.93\.161\.27/10.1.0.2/g'
  -e 's/192\.168\.1\.100/10.0.0.1/g'
  -e 's/192\.168\.1\.103/10.0.0.2/g'
  -e 's/192\.168\.1\.148/10.0.0.3/g'
  -e 's/192\.168\.1\.166/10.0.0.4/g'
  -e 's/vamsee\.achanta/devuser/g'
  -e 's/krishna@192/devuser2@10/g'
  -e 's/user `vamsee`/user `devuser`/g'
  -e 's/user: vamsee/user: devuser/g'
)

SEARCH='ace-linux|acma-ansys|aceengineer-va|ACMA-ANSYS|acma-ws014|MacBook Air|100\.107\.64\.76|100\.93\.161\.27|192\.168\.1\.(100|103|148|166)|vamsee\.achanta|krishna@192'

GLOBS=(--include '*.md' --include '*.yaml' --include '*.yml' --include '*.json' --include '*.sh' --include '*.py' --include '*.txt' --include '*.toml' --include '*.jsonl')

# Directories to scan (excludes code submodules)
DIRS=(
  "$REPO_ROOT/.claude"
  "$REPO_ROOT/config"
  "$REPO_ROOT/scripts"
  "$REPO_ROOT/admin"
  "$REPO_ROOT/docs"
  "$REPO_ROOT/specs"
  "$REPO_ROOT/logs"
  "$REPO_ROOT/aceengineer-admin"
  "$REPO_ROOT/coordination"
  "$REPO_ROOT/state"
  "$REPO_ROOT/knowledge"
  "$REPO_ROOT/notes"
  "$REPO_ROOT/docker"
  "$MEMORY_DIR"
)

total=0
for dir in "${DIRS[@]}"; do
  [[ -d "$dir" ]] || continue
  echo "Scanning $dir ..."
  files=$(grep -rlE "$SEARCH" "${GLOBS[@]}" --exclude-dir='.git' "$dir" 2>/dev/null || true)
  [[ -z "$files" ]] && continue
  count=$(echo "$files" | wc -l)
  total=$((total + count))
  if $DRY_RUN; then
    echo "  Would modify $count files"
  else
    echo "$files" | xargs sed -i "${SED_ARGS[@]}"
    echo "  Modified $count files"
  fi
done

# Top-level files
echo "Scanning top-level files..."
files=$(grep -rlE "$SEARCH" "${GLOBS[@]}" --exclude-dir='.git' --max-depth=1 "$REPO_ROOT" 2>/dev/null || true)
if [[ -n "$files" ]]; then
  count=$(echo "$files" | wc -l)
  total=$((total + count))
  if $DRY_RUN; then
    echo "  Would modify $count files"
  else
    echo "$files" | xargs sed -i "${SED_ARGS[@]}"
    echo "  Modified $count files"
  fi
fi

echo ""
echo "Total files: $total"
