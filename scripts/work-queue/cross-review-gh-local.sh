#!/usr/bin/env bash
# cross-review-gh-local.sh — Verify GH issues match local WRK files
# Queries all repos in gh-repos.yaml and compares against local queue
# Usage: bash scripts/work-queue/cross-review-gh-local.sh [--repo <name>]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
CONFIG="$REPO_ROOT/config/work-queue/gh-repos.yaml"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
FILTER_REPO=""
[[ "${1:-}" == "--repo" ]] && FILTER_REPO="${2:-}"

if ! command -v gh &>/dev/null || ! gh auth status &>/dev/null; then
  echo "ERROR: gh CLI not available or not authenticated" >&2
  exit 1
fi

OWNER=$(grep '^owner:' "$CONFIG" | sed 's/^owner: *//')
REPOS=$(grep '^ *- ' "$CONFIG" | sed 's/^ *- *//')
[[ -n "$FILTER_REPO" ]] && REPOS="$FILTER_REPO"

echo "═══ GH ↔ Local Cross-Review ═══"
echo ""

total_gh=0
total_local=0
discrepancies=0
missing_local=0
missing_gh=0

for repo in $REPOS; do
  full_repo="${OWNER}/${repo}"
  echo "── $full_repo ──"

  # Fetch all wrk-item issues from GH
  gh_issues=$(gh issue list --repo "$full_repo" --label wrk-item \
    --state all --json number,title,state --limit 500 2>/dev/null) || {
    echo "  ⚠ Failed to fetch — skipping"
    continue
  }

  gh_count=$(echo "$gh_issues" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)
  total_gh=$((total_gh + gh_count))

  # Check each GH issue has a local file
  echo "$gh_issues" | python3 -c "
import json, sys, os
from pathlib import Path

issues = json.load(sys.stdin)
queue = Path('$QUEUE_DIR')
repo = '$repo'
missing = 0
state_mismatch = 0

for issue in issues:
    num = issue['number']
    state = issue.get('state', 'OPEN')

    # Look for local file
    found = False
    local_status = None
    for d in ['pending', 'working', 'blocked', 'done']:
        for pattern in [f'{repo}-{num}.md', f'WRK-{num}.md']:
            candidate = queue / d / pattern
            if candidate.exists():
                found = True
                # Read status from frontmatter
                for line in candidate.read_text(errors='replace').split('\n'):
                    if line.startswith('status:'):
                        local_status = line.split(':',1)[1].strip().strip('\"')
                        break
                break
        if found:
            break

    # Check archive too
    if not found:
        for af in queue.glob(f'archive/**/{repo}-{num}.md'):
            found = True
            local_status = 'archived'
            break
        if not found:
            for af in queue.glob(f'archive/**/WRK-{num}.md'):
                found = True
                local_status = 'archived'
                break

    if not found:
        print(f'  MISSING LOCAL: {repo}#{num} ({issue[\"title\"][:50]})')
        missing += 1

print(f'  GH issues: {len(issues)}, missing local: {missing}')
" 2>/dev/null
  _ml=$(echo "$gh_issues" | python3 -c "
import json, sys
from pathlib import Path
issues = json.load(sys.stdin)
queue = Path('$QUEUE_DIR')
repo = '$repo'
m = 0
for i in issues:
    n = i['number']
    found = False
    for d in ['pending','working','blocked','done']:
        for p in [f'{repo}-{n}.md', f'WRK-{n}.md']:
            if (queue/d/p).exists(): found=True; break
        if found: break
    if not found:
        for af in queue.glob(f'archive/**/{repo}-{n}.md'):
            found=True; break
        if not found:
            for af in queue.glob(f'archive/**/WRK-{n}.md'):
                found=True; break
    if not found: m+=1
print(m)
" 2>/dev/null || echo 0)
  missing_local=$((missing_local + _ml))

  # Check local files have matching GH issue
  local_count=0
  for d in pending working blocked done; do
    for f in "$QUEUE_DIR/$d/${repo}"-*.md; do
      [[ -f "$f" ]] || continue
      local_count=$((local_count + 1))
    done
  done
  total_local=$((total_local + local_count))

  echo ""
done

discrepancies=$((missing_local + missing_gh))

echo "═══ Summary ═══"
echo "GH issues (wrk-item label): $total_gh"
echo "Local files (repo-prefixed): $total_local"
echo "Missing local files: $missing_local"
echo "Discrepancies: $discrepancies"
echo ""

if [[ $discrepancies -eq 0 ]]; then
  echo "✔ PASS — GH and local are consistent"
  exit 0
else
  echo "✖ FAIL — $discrepancies discrepancies found"
  exit 1
fi
