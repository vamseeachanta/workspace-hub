#!/usr/bin/env bash
# backfill-github-refs.sh — Create GitHub issues for WRK items missing github_issue_ref
#
# Scans pending/, working/, and blocked/ for items without github_issue_ref.
# For each, searches existing GitHub issues by title to prevent duplicates,
# then creates a new issue if none found.
#
# Usage:
#   backfill-github-refs.sh [--dry-run] [--limit N]
#
# Flags:
#   --dry-run   Preview what would be created without making changes
#   --limit N   Process at most N items (default: unlimited)
#
# Safety:
#   - 1-second delay between GitHub API calls to avoid rate limiting
#   - Duplicate detection by searching existing issues by WRK ID in title
#   - Idempotent: re-running skips items that already have github_issue_ref
#
# Exit codes:
#   0 = success
#   1 = error
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
REPO="vamseeachanta/workspace-hub"

DRY_RUN=false
LIMIT=0  # 0 = unlimited

# ── Parse arguments ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --limit)   LIMIT="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 [--dry-run] [--limit N]"
      echo ""
      echo "Creates GitHub issues for WRK items missing github_issue_ref."
      echo ""
      echo "Flags:"
      echo "  --dry-run   Preview changes without creating issues"
      echo "  --limit N   Process at most N items"
      echo ""
      echo "Safety features:"
      echo "  - 1s delay between API calls"
      echo "  - Duplicate detection via title search"
      echo "  - Idempotent (skips items with existing refs)"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# ── Verify gh is available ───────────────────────────────────────────────────
if ! command -v gh &>/dev/null; then
  echo "Error: gh CLI not found. Install from https://cli.github.com/" >&2
  exit 1
fi

if ! gh auth status &>/dev/null 2>&1; then
  echo "Error: gh not authenticated. Run 'gh auth login' first." >&2
  exit 1
fi

# ── Find items missing github_issue_ref ──────────────────────────────────────
MISSING_FILES=()
for dir in pending working blocked; do
  dir_path="${QUEUE_DIR}/${dir}"
  [[ -d "$dir_path" ]] || continue

  shopt -s nullglob
  for file in "${dir_path}"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    # Check if github_issue_ref is present and non-empty
    ref=$(grep -m1 '^github_issue_ref:' "$file" 2>/dev/null | sed 's/^github_issue_ref:[[:space:]]*//' | tr -d '"'"'" | xargs 2>/dev/null || true)
    if [[ -z "$ref" ]]; then
      MISSING_FILES+=("$file")
    fi
  done
  shopt -u nullglob
done

if [[ ${#MISSING_FILES[@]} -eq 0 ]]; then
  echo "All WRK items have github_issue_ref. Nothing to backfill."
  exit 0
fi

echo "Found ${#MISSING_FILES[@]} item(s) missing github_issue_ref."
if [[ "$LIMIT" -gt 0 ]]; then
  echo "Processing up to ${LIMIT} items."
fi
echo ""

CREATED=0
LINKED=0
SKIPPED=0
FAILED=0
PROCESSED=0

for file in "${MISSING_FILES[@]}"; do
  if [[ "$LIMIT" -gt 0 && "$PROCESSED" -ge "$LIMIT" ]]; then
    echo "Reached limit of ${LIMIT} items. Stopping."
    break
  fi

  wrk_id="$(basename "$file" .md)"
  title=$(awk '/^---$/{n++; next} n==1 && /^title:/{sub(/^title:[[:space:]]*"?/,""); sub(/"?[[:space:]]*$/,""); print; exit}' "$file")
  title="${title:-Untitled}"

  echo "─── ${wrk_id}: ${title} ───"

  # Duplicate detection: search existing GitHub issues by WRK ID
  existing=$(gh issue list --repo "$REPO" \
    --search "${wrk_id}" --json number,title,url --limit 5 2>/dev/null || echo "[]")

  # Check if any result has a title starting with the WRK ID
  match_url=$(echo "$existing" | jq -r --arg id "$wrk_id" '
    .[] | select(.title | startswith($id)) | .url' 2>/dev/null | head -1)

  if [[ -n "$match_url" && "$match_url" != "null" ]]; then
    match_num=$(echo "$existing" | jq -r --arg id "$wrk_id" '
      .[] | select(.title | startswith($id)) | .number' 2>/dev/null | head -1)
    echo "  Found existing issue #${match_num}: ${match_url}"

    if [[ "$DRY_RUN" == true ]]; then
      echo "  [DRY RUN] Would link ${wrk_id} → ${match_url}"
    else
      # Store the reference in frontmatter
      if grep -q '^github_issue_ref:' "$file"; then
        sed -i "s|^github_issue_ref:.*|github_issue_ref: ${match_url}|" "$file"
      else
        sed -i "/^id: ${wrk_id}/a github_issue_ref: ${match_url}" "$file"
      fi
      echo "  Linked ${wrk_id} → ${match_url}"
    fi
    LINKED=$((LINKED + 1))
  else
    if [[ "$DRY_RUN" == true ]]; then
      echo "  [DRY RUN] Would create GitHub issue for ${wrk_id}: ${title}"
    else
      # Create the issue via update-github-issue.py
      UPDATE_SCRIPT="${WORKSPACE_ROOT}/scripts/knowledge/update-github-issue.py"
      if [[ -f "$UPDATE_SCRIPT" ]]; then
        if uv run --no-project --quiet python "$UPDATE_SCRIPT" "$wrk_id" --create 2>/dev/null; then
          echo "  Created GitHub issue for ${wrk_id}"
          CREATED=$((CREATED + 1))
        else
          echo "  ERROR: Failed to create issue for ${wrk_id}" >&2
          FAILED=$((FAILED + 1))
        fi
      else
        echo "  ERROR: update-github-issue.py not found" >&2
        FAILED=$((FAILED + 1))
      fi

      # Rate limit protection
      sleep 1
    fi
  fi

  PROCESSED=$((PROCESSED + 1))
  echo ""
done

echo "=== Backfill Summary ==="
echo "  Processed: ${PROCESSED}"
echo "  Created:   ${CREATED}"
echo "  Linked:    ${LINKED} (existing issues found)"
echo "  Failed:    ${FAILED}"
echo "  Dry run:   ${DRY_RUN}"

if [[ "$FAILED" -gt 0 ]]; then
  exit 1
fi
exit 0
