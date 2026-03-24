#!/usr/bin/env bash
# renumber-to-gh.sh — Batch rename WRK files to repo-prefixed GH numbers
# HIGHEST RISK OPERATION — always run --dry-run first
#
# Usage:
#   bash scripts/work-queue/renumber-to-gh.sh --dry-run    # preview changes
#   bash scripts/work-queue/renumber-to-gh.sh --execute     # do the rename
#   bash scripts/work-queue/renumber-to-gh.sh --rollback    # reverse from log
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
CONFIG="$REPO_ROOT/config/work-queue/gh-repos.yaml"
LOG_DIR="$REPO_ROOT/logs"
LOG_FILE="$LOG_DIR/wrk-renumber-$(date -u +%Y%m%d).jsonl"

MODE=""
case "${1:-}" in
  --dry-run)  MODE="dry-run" ;;
  --execute)  MODE="execute" ;;
  --rollback) MODE="rollback" ;;
  *)
    echo "Usage: renumber-to-gh.sh --dry-run | --execute | --rollback"
    exit 1
    ;;
esac

OWNER=$(grep '^owner:' "$CONFIG" | sed 's/^owner: *//')

# ── Rollback mode ───────────────────────────────────────────────────────────
if [[ "$MODE" == "rollback" ]]; then
  if [[ ! -f "$LOG_FILE" ]]; then
    echo "ERROR: No rename log found at $LOG_FILE" >&2
    exit 1
  fi
  echo "Rolling back from $LOG_FILE..."
  tac "$LOG_FILE" | while IFS= read -r line; do
    from=$(echo "$line" | python3 -c "import json,sys; print(json.load(sys.stdin)['from'])")
    to=$(echo "$line" | python3 -c "import json,sys; print(json.load(sys.stdin)['to'])")
    type=$(echo "$line" | python3 -c "import json,sys; print(json.load(sys.stdin)['type'])")
    if [[ "$type" == "file" && -f "$REPO_ROOT/$to" ]]; then
      git mv "$REPO_ROOT/$to" "$REPO_ROOT/$from" 2>/dev/null || mv "$REPO_ROOT/$to" "$REPO_ROOT/$from"
      echo "  ↩ $to → $from"
    elif [[ "$type" == "dir" && -d "$REPO_ROOT/$to" ]]; then
      git mv "$REPO_ROOT/$to" "$REPO_ROOT/$from" 2>/dev/null || mv "$REPO_ROOT/$to" "$REPO_ROOT/$from"
      echo "  ↩ $to → $from"
    fi
  done
  echo "Rollback complete. Run rebuild-wrk-index.sh to refresh index."
  exit 0
fi

# ── Scan and plan renames ───────────────────────────────────────────────────
mkdir -p "$LOG_DIR"

renamed=0
skipped=0
no_ref=0

_extract_repo_from_ref() {
  # https://github.com/owner/repo/issues/NNN → repo
  echo "$1" | sed -n 's|https://github.com/[^/]*/\([^/]*\)/issues/.*|\1|p'
}

_extract_num_from_ref() {
  echo "$1" | sed -n 's|.*/issues/\([0-9]*\)$|\1|p'
}

echo "═══ WRK Renumber to GH (mode: $MODE) ═══"
echo ""

for dir in pending working blocked done; do
  dir_path="$QUEUE_DIR/$dir"
  [[ -d "$dir_path" ]] || continue

  for f in "$dir_path"/WRK-*.md; do
    [[ -f "$f" ]] || continue
    wrk_id=$(basename "$f" .md)

    # Read github_issue_ref
    gh_ref=$(grep -m1 '^github_issue_ref:' "$f" 2>/dev/null | sed 's/^github_issue_ref: *//' | tr -d '"' || echo "")

    if [[ -z "$gh_ref" || "$gh_ref" == "pending" ]]; then
      echo "  SKIP (no gh ref): $wrk_id"
      no_ref=$((no_ref + 1))
      continue
    fi

    target_repo=$(_extract_repo_from_ref "$gh_ref")
    gh_num=$(_extract_num_from_ref "$gh_ref")

    if [[ -z "$target_repo" || -z "$gh_num" ]]; then
      echo "  SKIP (bad ref): $wrk_id → $gh_ref"
      skipped=$((skipped + 1))
      continue
    fi

    new_name="${target_repo}-${gh_num}.md"
    old_rel=".claude/work-queue/$dir/$wrk_id.md"
    new_rel=".claude/work-queue/$dir/$new_name"

    # Skip if already renamed
    if [[ "$wrk_id" == "${target_repo}-${gh_num}" ]]; then
      skipped=$((skipped + 1))
      continue
    fi

    if [[ "$MODE" == "dry-run" ]]; then
      echo "  $old_rel → $new_rel"
      renamed=$((renamed + 1))
    else
      # Rename file
      git mv "$REPO_ROOT/$old_rel" "$REPO_ROOT/$new_rel" 2>/dev/null || \
        mv "$REPO_ROOT/$old_rel" "$REPO_ROOT/$new_rel"

      # Update id: in frontmatter
      sed -i "s/^id: .*/id: ${target_repo}#${gh_num}/" "$REPO_ROOT/$new_rel"

      # Log the rename
      echo "{\"from\": \"$old_rel\", \"to\": \"$new_rel\", \"type\": \"file\", \"wrk_id\": \"$wrk_id\", \"new_id\": \"${target_repo}#${gh_num}\"}" >> "$LOG_FILE"

      echo "  ✔ $old_rel → $new_rel"
      renamed=$((renamed + 1))

      # Rename assets dir if exists
      old_assets=".claude/work-queue/assets/$wrk_id"
      new_assets=".claude/work-queue/assets/${target_repo}-${gh_num}"
      if [[ -d "$REPO_ROOT/$old_assets" && ! -d "$REPO_ROOT/$new_assets" ]]; then
        git mv "$REPO_ROOT/$old_assets" "$REPO_ROOT/$new_assets" 2>/dev/null || \
          mv "$REPO_ROOT/$old_assets" "$REPO_ROOT/$new_assets"
        echo "{\"from\": \"$old_assets\", \"to\": \"$new_assets\", \"type\": \"dir\", \"wrk_id\": \"$wrk_id\"}" >> "$LOG_FILE"
        echo "    ✔ assets: $old_assets → $new_assets"
      fi
    fi
  done
done

# ── Archive subdirs ─────────────────────────────────────────────────────────
if [[ -d "$QUEUE_DIR/archive" ]]; then
  while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    wrk_id=$(basename "$f" .md)
    subdir=$(dirname "$f" | sed "s|$QUEUE_DIR/||")

    gh_ref=$(grep -m1 '^github_issue_ref:' "$f" 2>/dev/null | sed 's/^github_issue_ref: *//' | tr -d '"' || echo "")
    if [[ -z "$gh_ref" || "$gh_ref" == "pending" ]]; then
      no_ref=$((no_ref + 1))
      continue
    fi

    target_repo=$(_extract_repo_from_ref "$gh_ref")
    gh_num=$(_extract_num_from_ref "$gh_ref")
    [[ -z "$target_repo" || -z "$gh_num" ]] && { skipped=$((skipped + 1)); continue; }

    new_name="${target_repo}-${gh_num}.md"
    old_rel=".claude/work-queue/$subdir/$wrk_id.md"
    new_rel=".claude/work-queue/$subdir/$new_name"

    [[ "$wrk_id" == "${target_repo}-${gh_num}" ]] && { skipped=$((skipped + 1)); continue; }

    if [[ "$MODE" == "dry-run" ]]; then
      echo "  $old_rel → $new_rel"
      renamed=$((renamed + 1))
    else
      git mv "$REPO_ROOT/$old_rel" "$REPO_ROOT/$new_rel" 2>/dev/null || \
        mv "$REPO_ROOT/$old_rel" "$REPO_ROOT/$new_rel"
      sed -i "s/^id: .*/id: ${target_repo}#${gh_num}/" "$REPO_ROOT/$new_rel"
      echo "{\"from\": \"$old_rel\", \"to\": \"$new_rel\", \"type\": \"file\", \"wrk_id\": \"$wrk_id\", \"new_id\": \"${target_repo}#${gh_num}\"}" >> "$LOG_FILE"
      echo "  ✔ $old_rel → $new_rel"
      renamed=$((renamed + 1))
    fi
  done < <(find "$QUEUE_DIR/archive" -name "WRK-*.md" 2>/dev/null | sort)
fi

echo ""
echo "Summary: $renamed renamed, $skipped already done/skipped, $no_ref missing GH ref"
[[ "$MODE" == "dry-run" ]] && echo "Run with --execute to apply changes."
[[ "$MODE" == "execute" ]] && echo "Rename log: $LOG_FILE"
