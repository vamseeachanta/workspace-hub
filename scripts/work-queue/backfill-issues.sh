#!/usr/bin/env bash
# backfill-issues.sh — Update all GitHub issues to the WRK-5104 template format
#
# Fetches all issues, matches to local WRK files by title, backfills
# github_issue_ref into WRK frontmatter if missing, then calls
# update-github-issue.py --update to refresh each issue body.
#
# Usage:
#   bash scripts/work-queue/backfill-issues.sh [--dry-run] [--limit N] [--resume-from ISSUE_NUMBER] [--verbose]
set -euo pipefail

REPO="vamseeachanta/workspace-hub"
REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
UPDATE_SCRIPT="$REPO_ROOT/scripts/knowledge/update-github-issue.py"

DRY_RUN=false
LIMIT=0
RESUME_FROM=0
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --limit) LIMIT="$2"; shift 2 ;;
        --resume-from) RESUME_FROM="$2"; shift 2 ;;
        --verbose) VERBOSE=true; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

# --- Phase 0: Preflight ---
echo "=== Phase 0: Preflight ==="
if ! command -v gh &>/dev/null; then
    echo "ERROR: gh CLI not found" >&2; exit 1
fi
if ! gh auth status &>/dev/null; then
    echo "ERROR: gh not authenticated — run 'gh auth login'" >&2; exit 1
fi
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found" >&2; exit 1
fi
if [[ ! -f "$UPDATE_SCRIPT" ]]; then
    echo "ERROR: update-github-issue.py not found at $UPDATE_SCRIPT" >&2; exit 1
fi
echo "Preflight OK"

# --- Phase 1: Fetch & Match ---
echo ""
echo "=== Phase 1: Fetch all issues ==="
ISSUES_FILE=$(mktemp)
trap 'rm -f "$ISSUES_FILE"' EXIT

gh issue list --repo "$REPO" --state all --limit 5000 \
    --json number,title \
    --jq 'sort_by(.number) | .[] | "\(.number)\t\(.title)"' \
    > "$ISSUES_FILE"

TOTAL=$(wc -l < "$ISSUES_FILE")
echo "Fetched $TOTAL issues"

# Truncation check
if [[ "$TOTAL" -ge 5000 ]]; then
    echo "WARNING: Fetched exactly 5000 issues — results may be truncated!" >&2
    echo "Consider using pagination or increasing the limit." >&2
    exit 1
fi

# Find WRK file across all queue directories
find_wrk_file() {
    local wrk_name="$1"
    for dir in pending working done blocked archived; do
        local candidate="$QUEUE_DIR/$dir/$wrk_name.md"
        if [[ -f "$candidate" ]]; then
            echo "$candidate"
            return
        fi
    done
    find "$QUEUE_DIR/archive" "$QUEUE_DIR/archived" -name "$wrk_name.md" -type f 2>/dev/null | head -1
}

# Backfill github_issue_ref into WRK frontmatter using Python (safe YAML handling)
backfill_ref() {
    local wrk_file="$1"
    local issue_num="$2"
    local issue_url="https://github.com/$REPO/issues/$issue_num"

    uv run --no-project python3 -c "
import re, sys
path = sys.argv[1]
url = sys.argv[2]
text = open(path).read()
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
if not m:
    print('SKIP: no frontmatter', file=sys.stderr)
    sys.exit(1)
fm = m.group(1)
if 'github_issue_ref:' in fm:
    print('SKIP: already has ref')
    sys.exit(0)
# Insert before closing ---
new_fm = fm.rstrip() + '\ngithub_issue_ref: ' + url
new_text = text[:m.start(1)] + new_fm + text[m.end(1):]
open(path, 'w').write(new_text)
print('BACKFILLED')
" "$wrk_file" "$issue_url"
}

# --- Phase 2 & 3: Process issues ---
echo ""
echo "=== Phase 2-3: Process issues ==="
COUNT=0
PROCESSED=0
UPDATED=0
REFS_BACKFILLED=0
SKIPPED_NO_WRK=0
SKIPPED_AMBIGUOUS=0
SKIPPED_NO_FILE=0
SKIPPED_RESUME=0
ERRORS=0

while IFS=$'\t' read -r ISSUE_NUM TITLE; do
    # Guard against malformed lines
    [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]] || { echo "WARN: unexpected line, skipping" >&2; continue; }
    COUNT=$((COUNT + 1))

    # Resume support
    if [[ "$RESUME_FROM" -gt 0 && "$ISSUE_NUM" -lt "$RESUME_FROM" ]]; then
        SKIPPED_RESUME=$((SKIPPED_RESUME + 1))
        continue
    fi

    # Limit support
    if [[ "$LIMIT" -gt 0 && "$PROCESSED" -ge "$LIMIT" ]]; then
        break
    fi
    PROCESSED=$((PROCESSED + 1))

    # Extract WRK ID from title (safe: only issue number goes to shell, title stays in read var)
    WRK_NAME=$(echo "$TITLE" | grep -oP 'WRK-\d+' | head -1 || true)
    WRK_COUNT=$(echo "$TITLE" | grep -oP 'WRK-\d+' | wc -l || true)

    if [[ -z "$WRK_NAME" ]]; then
        SKIPPED_NO_WRK=$((SKIPPED_NO_WRK + 1))
        $VERBOSE && echo "  [$ISSUE_NUM] SKIP: no WRK ID in title"
        continue
    fi

    if [[ "$WRK_COUNT" -gt 1 ]]; then
        SKIPPED_AMBIGUOUS=$((SKIPPED_AMBIGUOUS + 1))
        $VERBOSE && echo "  [$ISSUE_NUM] SKIP: ambiguous — multiple WRK IDs in title"
        continue
    fi

    # Find local WRK file
    WRK_FILE=$(find_wrk_file "$WRK_NAME")
    if [[ -z "$WRK_FILE" ]]; then
        SKIPPED_NO_FILE=$((SKIPPED_NO_FILE + 1))
        $VERBOSE && echo "  [$ISSUE_NUM] SKIP: $WRK_NAME — no local file"
        continue
    fi

    # Dry-run: report only, no file writes or API calls
    if $DRY_RUN; then
        echo "  [$ISSUE_NUM] DRY-RUN: would update $WRK_NAME"
        UPDATED=$((UPDATED + 1))
        continue
    fi

    # Phase 2: Backfill github_issue_ref if missing
    REF_RESULT=$(backfill_ref "$WRK_FILE" "$ISSUE_NUM" 2>&1) || {
        echo "  [$ISSUE_NUM] WARN: backfill_ref failed for $WRK_NAME, skipping update" >&2
        ERRORS=$((ERRORS + 1))
        continue
    }
    if [[ "$REF_RESULT" == "BACKFILLED" ]]; then
        REFS_BACKFILLED=$((REFS_BACKFILLED + 1))
        $VERBOSE && echo "  [$ISSUE_NUM] $WRK_NAME — backfilled github_issue_ref"
    fi

    # Retry up to 3 times
    SUCCESS=false
    for ATTEMPT in 1 2 3; do
        if uv run --no-project python3 "$UPDATE_SCRIPT" "$WRK_NAME" --update 2>/dev/null; then
            SUCCESS=true
            break
        fi
        $VERBOSE && echo "  [$ISSUE_NUM] $WRK_NAME — attempt $ATTEMPT failed, retrying..."
        sleep $((ATTEMPT * 2))
    done

    if $SUCCESS; then
        UPDATED=$((UPDATED + 1))
        echo "  [$COUNT/$TOTAL] $WRK_NAME #$ISSUE_NUM — updated"
    else
        ERRORS=$((ERRORS + 1))
        echo "  [$COUNT/$TOTAL] ERROR: $WRK_NAME #$ISSUE_NUM — failed after 3 attempts" >&2
    fi

    sleep 1
done < "$ISSUES_FILE"

# --- Phase 4: Report ---
echo ""
echo "=== Backfill Report ==="
echo "  Total fetched:        $TOTAL"
echo "  Processed:            $PROCESSED"
echo "  Updated:              $UPDATED"
echo "  Refs backfilled:      $REFS_BACKFILLED"
echo "  Skipped (no WRK ID): $SKIPPED_NO_WRK"
echo "  Skipped (ambiguous):  $SKIPPED_AMBIGUOUS"
echo "  Skipped (no file):    $SKIPPED_NO_FILE"
echo "  Skipped (resume):     $SKIPPED_RESUME"
echo "  Errors:               $ERRORS"

if [[ "$ERRORS" -gt 0 ]]; then
    exit 1
fi
