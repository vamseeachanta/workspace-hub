#!/usr/bin/env bash
# setup-gh-labels.sh — Idempotent label creation across all repos in gh-repos.yaml
# Usage: bash scripts/work-queue/setup-gh-labels.sh [--dry-run]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
CONFIG="$REPO_ROOT/config/work-queue/gh-repos.yaml"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

if ! command -v gh &>/dev/null || ! gh auth status &>/dev/null; then
  echo "ERROR: gh CLI not available or not authenticated" >&2
  exit 1
fi

# Parse repos from config
OWNER=$(grep '^owner:' "$CONFIG" | sed 's/^owner: *//')
REPOS=$(grep '^ *- ' "$CONFIG" | sed 's/^ *- *//')

# Label definitions: name|color|description
LABELS=(
  "wrk-item|0075ca|Work queue item"
  "priority:high|b60205|High priority"
  "priority:medium|fbca04|Medium priority"
  "priority:low|0e8a16|Low priority"
  "status:pending|c5def5|Pending"
  "status:working|1d76db|In progress"
  "status:done|0e8a16|Completed"
  "status:blocked|d93f0b|Blocked"
  "status:closed|6e7781|Closed"
  "machine:dev-primary|e4e669|Assigned to dev-primary"
  "machine:dev-secondary|e4e669|Assigned to dev-secondary"
  "machine:licensed-win-1|e4e669|Assigned to licensed-win-1"
  "machine:licensed-win-2|e4e669|Assigned to licensed-win-2"
  "route:A|d4c5f9|Route A (simple)"
  "route:B|d4c5f9|Route B (medium)"
  "route:C|d4c5f9|Route C (complex)"
  "cat:harness|bfdadc|Category: harness"
  "cat:engineering-calculations|bfdadc|Category: engineering calculations"
  "cat:data|bfdadc|Category: data"
  "cat:tooling|bfdadc|Category: tooling"
)

created=0
skipped=0
failed=0

for repo in $REPOS; do
  full_repo="${OWNER}/${repo}"
  echo "── $full_repo ──"

  # Get existing labels
  existing=$(gh label list --repo "$full_repo" --json name --jq '.[].name' 2>/dev/null || echo "")

  for label_def in "${LABELS[@]}"; do
    IFS='|' read -r name color desc <<< "$label_def"

    if echo "$existing" | grep -qx "$name" 2>/dev/null; then
      skipped=$((skipped + 1))
      continue
    fi

    if $DRY_RUN; then
      echo "  [dry-run] would create: $name ($color)"
      created=$((created + 1))
    else
      if gh label create "$name" --repo "$full_repo" --color "$color" --description "$desc" 2>/dev/null; then
        echo "  ✔ $name"
        created=$((created + 1))
      else
        echo "  ✖ $name (failed)" >&2
        failed=$((failed + 1))
      fi
    fi
  done
done

echo ""
echo "Summary: $created created, $skipped already exist, $failed failed"
