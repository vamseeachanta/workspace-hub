#!/usr/bin/env bash
# gh-sync-down.sh — Sync GH issue metadata → local WRK frontmatter
# Multi-repo: iterates repos from config/work-queue/gh-repos.yaml
# Delta-sync: only fetches issues updated since last sync per repo
# Usage: bash scripts/work-queue/gh-sync-down.sh [--force] [--repo <name>]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
CONFIG="$REPO_ROOT/config/work-queue/gh-repos.yaml"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
STATE_FILE="$REPO_ROOT/config/work-queue/gh-sync-state.json"
CACHE_TTL_MIN=5
FORCE=false
FILTER_REPO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=true; shift ;;
    --repo)  FILTER_REPO="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if ! command -v gh &>/dev/null || ! gh auth status &>/dev/null; then
  echo "ERROR: gh CLI not available or not authenticated" >&2
  exit 1
fi

# Parse config
OWNER=$(grep '^owner:' "$CONFIG" | sed 's/^owner: *//')
REPOS=$(grep '^ *- ' "$CONFIG" | sed 's/^ *- *//')
[[ -n "$FILTER_REPO" ]] && REPOS="$FILTER_REPO"

# Init state file if missing
[[ -f "$STATE_FILE" ]] || echo '{}' > "$STATE_FILE"

synced=0
skipped=0
failed=0

for repo in $REPOS; do
  full_repo="${OWNER}/${repo}"

  # Check TTL (skip if synced recently unless --force)
  if ! $FORCE; then
    last_sync=$(python3 -c "
import json, sys
from datetime import datetime, timezone
d = json.load(open('$STATE_FILE'))
ts = d.get('$repo', {}).get('last_sync_at', '')
if not ts:
    print('stale')
    sys.exit()
try:
    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
    age_min = (datetime.now(timezone.utc) - dt).total_seconds() / 60
    print('fresh' if age_min < $CACHE_TTL_MIN else 'stale')
except:
    print('stale')
" 2>/dev/null || echo "stale")

    if [[ "$last_sync" == "fresh" ]]; then
      echo "⏭ $repo: synced < ${CACHE_TTL_MIN}min ago (use --force to override)"
      skipped=$((skipped + 1))
      continue
    fi
  fi

  # Build delta-sync query
  since=""
  last_ts=$(python3 -c "
import json
d = json.load(open('$STATE_FILE'))
print(d.get('$repo', {}).get('last_sync_at', ''))
" 2>/dev/null || echo "")

  search_filter=""
  if [[ -n "$last_ts" ]] && ! $FORCE; then
    # Extract date portion for updated: filter
    since_date="${last_ts%%T*}"
    search_filter="updated:>=${since_date}"
  fi

  echo "── Syncing $full_repo ${search_filter:+(delta: $search_filter)} ──"

  # Fetch issues with wrk-item label using pagination
  issues_json=""
  if [[ -n "$search_filter" ]]; then
    issues_json=$(gh issue list --repo "$full_repo" --label wrk-item \
      --search "$search_filter" --state all \
      --json number,title,state,labels,updatedAt,body --limit 500 2>/dev/null) || {
      echo "  ⚠ Failed to fetch $repo [STALE: using cached data]" >&2
      failed=$((failed + 1))
      continue
    }
  else
    issues_json=$(gh issue list --repo "$full_repo" --label wrk-item \
      --state all \
      --json number,title,state,labels,updatedAt,body --limit 500 2>/dev/null) || {
      echo "  ⚠ Failed to fetch $repo [STALE: using cached data]" >&2
      failed=$((failed + 1))
      continue
    }
  fi

  # Process each issue → update local WRK frontmatter
  count=$(echo "$issues_json" | python3 -c "
import json, sys, re, os
from pathlib import Path

data = json.load(sys.stdin)
queue = Path('$QUEUE_DIR')
repo = '$repo'
count = 0

def extract_label(labels, prefix):
    for l in labels:
        name = l.get('name', '')
        if name.startswith(prefix):
            return name[len(prefix):]
    return ''

for issue in data:
    num = issue['number']
    title = issue.get('title', '').replace('[WRK] ', '')
    state = issue.get('state', 'OPEN')
    labels = issue.get('labels', [])

    # Extract metadata from labels
    priority = extract_label(labels, 'priority:')
    status_label = extract_label(labels, 'status:')
    machine = extract_label(labels, 'machine:')
    route = extract_label(labels, 'route:')
    category = extract_label(labels, 'cat:')

    # Map GH state to local status
    if state == 'CLOSED':
        local_status = status_label or 'closed'
    else:
        local_status = status_label or 'pending'

    gh_ref = f'https://github.com/$OWNER/{repo}/issues/{num}'

    # Find existing local file (check all dirs)
    local_file = None
    for d in ['pending', 'working', 'blocked', 'done']:
        # Check both old WRK-NNN and new repo-NNN naming
        for pattern in [f'WRK-{num}.md', f'{repo}-{num}.md']:
            candidate = queue / d / pattern
            if candidate.exists():
                local_file = candidate
                break
        if local_file:
            break

    # Also match by github_issue_ref in any file
    if not local_file:
        for d in ['pending', 'working', 'blocked', 'done']:
            dpath = queue / d
            if not dpath.is_dir():
                continue
            for f in dpath.glob('WRK-*.md'):
                try:
                    text = f.read_text(encoding='utf-8', errors='replace')
                    if gh_ref in text:
                        local_file = f
                        break
                except:
                    pass
            if local_file:
                break

    if not local_file:
        # No local file — skip (don't auto-create from GH, that's /work add's job)
        continue

    # Update frontmatter fields from GH
    text = local_file.read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')

    def update_fm(lines, key, value):
        if not value:
            return lines
        for i, line in enumerate(lines):
            if line.startswith(f'{key}:'):
                lines[i] = f'{key}: {value}'
                return lines
        return lines

    # Only update fields that GH is authoritative for
    if priority:
        lines = update_fm(lines, 'priority', priority)
    if machine:
        lines = update_fm(lines, 'computer', machine)
    if category:
        lines = update_fm(lines, 'category', category)

    local_file.write_text('\n'.join(lines), encoding='utf-8')
    count += 1

print(count)
" 2>/dev/null) || count=0

  echo "  ✔ $repo: $count items synced"
  synced=$((synced + count))

  # Update sync state
  python3 -c "
import json
from datetime import datetime, timezone
d = json.load(open('$STATE_FILE'))
d.setdefault('$repo', {})['last_sync_at'] = datetime.now(timezone.utc).isoformat()
with open('$STATE_FILE', 'w') as f:
    json.dump(d, f, indent=2)
" 2>/dev/null || true
done

echo ""
echo "Summary: $synced synced, $skipped skipped (fresh), $failed failed"
