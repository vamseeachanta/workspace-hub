#!/usr/bin/env bash
# promote-local-ids.sh — Promote WRK-LOCAL-* items to GitHub-derived WRK IDs
#
# Finds all WRK-LOCAL-*.md files in pending/ and promotes each to a real
# GitHub-derived WRK ID by calling gh-next-id.sh.
#
# Critical: rewrites ALL references to the old LOCAL ID across the entire
# workspace (blocked_by, specs, docs, session handoff notes, etc.).
#
# Usage:
#   promote-local-ids.sh [--dry-run]
#
# Flags:
#   --dry-run   Preview changes without modifying any files
#
# Exit codes:
#   0 = success (all items promoted, or nothing to promote)
#   1 = error (partial failure)
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GH_NEXT_ID="${SCRIPT_DIR}/gh-next-id.sh"

DRY_RUN=false

# ── Parse arguments ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN=true; shift ;;
    --help|-h)
      echo "Usage: $0 [--dry-run]"
      echo ""
      echo "Promotes WRK-LOCAL-*.md items in pending/ to GitHub-derived WRK IDs."
      echo ""
      echo "Flags:"
      echo "  --dry-run   Preview changes without modifying any files"
      echo ""
      echo "For each LOCAL item:"
      echo "  1. Creates a GitHub issue via gh-next-id.sh"
      echo "  2. Renames the file from WRK-LOCAL-*.md to WRK-{N}.md"
      echo "  3. Renames the assets directory"
      echo "  4. Updates frontmatter (id, github_issue_ref, provisional_id)"
      echo "  5. Rewrites ALL references to the old LOCAL ID across the workspace"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# ── Verify gh-next-id.sh exists ─────────────────────────────────────────────
if [[ ! -x "$GH_NEXT_ID" ]]; then
  echo "Error: gh-next-id.sh not found or not executable at: $GH_NEXT_ID" >&2
  exit 1
fi

# ── Find LOCAL items ─────────────────────────────────────────────────────────
shopt -s nullglob
LOCAL_FILES=("${QUEUE_DIR}/pending/WRK-LOCAL-"*.md)
shopt -u nullglob

if [[ ${#LOCAL_FILES[@]} -eq 0 ]]; then
  echo "No WRK-LOCAL-* items found in pending/. Nothing to promote."
  exit 0
fi

echo "Found ${#LOCAL_FILES[@]} LOCAL item(s) to promote:"
for f in "${LOCAL_FILES[@]}"; do
  echo "  $(basename "$f")"
done
echo ""

PROMOTED=0
FAILED=0

for local_file in "${LOCAL_FILES[@]}"; do
  local_basename="$(basename "$local_file" .md)"  # e.g., WRK-LOCAL-20260323-120000-devpri

  # Extract title from frontmatter
  title=$(awk '/^---$/{n++; next} n==1 && /^title:/{sub(/^title:[[:space:]]*"?/,""); sub(/"?[[:space:]]*$/,""); print; exit}' "$local_file")
  title="${title:-Untitled LOCAL item}"

  echo "─── Promoting: ${local_basename} ───"
  echo "  Title: ${title}"

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY RUN] Would call gh-next-id.sh --title \"${title}\""
    echo "  [DRY RUN] Would rename ${local_basename}.md → WRK-{N}.md"
    echo "  [DRY RUN] Would rewrite all references to ${local_basename} across workspace"
    echo ""
    PROMOTED=$((PROMOTED + 1))
    continue
  fi

  # Call gh-next-id.sh to get the real ID
  gh_output=$(bash "$GH_NEXT_ID" --title "$title" 2>/dev/null) || {
    echo "  ERROR: gh-next-id.sh failed for ${local_basename}" >&2
    FAILED=$((FAILED + 1))
    continue
  }

  # Parse output: line 1 = ID, line 2 = URL
  new_id=$(echo "$gh_output" | sed -n '1p')
  issue_url=$(echo "$gh_output" | sed -n '2p')

  # If we got another LOCAL ID back, skip (gh unavailable)
  if [[ "$new_id" == LOCAL-* ]]; then
    echo "  SKIP: gh unavailable — cannot promote ${local_basename} (got another LOCAL ID)"
    FAILED=$((FAILED + 1))
    continue
  fi

  new_wrk_id="WRK-${new_id}"
  new_file="${QUEUE_DIR}/pending/${new_wrk_id}.md"
  echo "  New ID: ${new_wrk_id}"
  echo "  Issue URL: ${issue_url}"

  # 1. Update frontmatter in the file
  sed -i "s/^id:.*/id: ${new_wrk_id}/" "$local_file"
  sed -i "s/^provisional_id:.*/provisional_id: false/" "$local_file"
  # Add or update github_issue_ref
  if grep -q '^github_issue_ref:' "$local_file"; then
    sed -i "s|^github_issue_ref:.*|github_issue_ref: ${issue_url}|" "$local_file"
  else
    sed -i "/^id: ${new_wrk_id}/a github_issue_ref: ${issue_url}" "$local_file"
  fi

  # 2. Rename the WRK file
  mv "$local_file" "$new_file"
  echo "  Renamed file: ${local_basename}.md → ${new_wrk_id}.md"

  # 3. Rename assets directory if it exists
  old_assets="${QUEUE_DIR}/assets/${local_basename}"
  new_assets="${QUEUE_DIR}/assets/${new_wrk_id}"
  if [[ -d "$old_assets" ]]; then
    mv "$old_assets" "$new_assets"
    echo "  Renamed assets: ${local_basename}/ → ${new_wrk_id}/"
  fi

  # 4. Rewrite ALL references to old LOCAL ID across the workspace
  ref_count=0
  while IFS= read -r ref_file; do
    # Skip binary files and the file we already renamed
    [[ ! -f "$ref_file" ]] && continue
    if file --mime-type "$ref_file" 2>/dev/null | grep -q 'binary'; then
      continue
    fi
    # Escape sed metacharacters in local_basename to prevent injection
    local_escaped=$(printf '%s\n' "$local_basename" | sed 's/[&/\\.^$*[\]]/\\&/g')
    new_escaped=$(printf '%s\n' "$new_wrk_id" | sed 's/[&/\\]/\\&/g')
    sed -i "s/${local_escaped}/${new_escaped}/g" "$ref_file"
    ref_count=$((ref_count + 1))
  done < <(grep -rl "${local_basename}" "${WORKSPACE_ROOT}" \
    --include="*.md" --include="*.yaml" --include="*.yml" \
    --include="*.sh" --include="*.py" --include="*.json" \
    --include="*.toml" 2>/dev/null || true)

  echo "  Rewrote ${ref_count} file(s) containing references to ${local_basename}"

  # 5. Update GitHub issue body with full content if update-github-issue.py exists
  UPDATE_SCRIPT="${WORKSPACE_ROOT}/scripts/knowledge/update-github-issue.py"
  if [[ -f "$UPDATE_SCRIPT" ]]; then
    uv run --no-project --quiet python "$UPDATE_SCRIPT" "$new_wrk_id" --update 2>/dev/null || true
  fi

  PROMOTED=$((PROMOTED + 1))
  echo ""
done

echo "=== Promotion Summary ==="
echo "  Promoted: ${PROMOTED}"
echo "  Failed:   ${FAILED}"
echo "  Dry run:  ${DRY_RUN}"

if [[ "$FAILED" -gt 0 ]]; then
  exit 1
fi
exit 0
