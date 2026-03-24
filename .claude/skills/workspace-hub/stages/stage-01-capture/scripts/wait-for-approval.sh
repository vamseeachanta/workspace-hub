#!/usr/bin/env bash
# wait-for-approval.sh WRK-NNN <stage>
# Polls GitHub issue comments every 60s until "approved" is found after
# the last "AWAITING APPROVAL" comment. Exits 0 when approved.
#
# Usage: bash scripts/work-queue/wait-for-approval.sh WRK-5104 5
# Timeout: 30 minutes (30 polls × 60s)

set -euo pipefail

WRK_ID="${1:?Usage: wait-for-approval.sh WRK-NNN <stage>}"
STAGE="${2:?Usage: wait-for-approval.sh WRK-NNN <stage>}"

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)}"
POLL_INTERVAL=60
MAX_POLLS=30

# Read github_issue_ref from WRK frontmatter
_get_issue_number() {
    local wrk_file=""
    for folder in pending working done; do
        local candidate="$REPO_ROOT/.claude/work-queue/$folder/$WRK_ID.md"
        if [[ -f "$candidate" ]]; then
            wrk_file="$candidate"
            break
        fi
    done
    if [[ -z "$wrk_file" ]]; then
        echo "ERROR: WRK file not found for $WRK_ID" >&2
        exit 1
    fi
    local ref
    ref=$(grep -m1 '^github_issue_ref:' "$wrk_file" 2>/dev/null | sed 's/^github_issue_ref:\s*//' | tr -d '"'"'" | xargs)
    if [[ -z "$ref" ]]; then
        echo "ERROR: No github_issue_ref in $WRK_ID frontmatter" >&2
        exit 1
    fi
    echo "${ref##*/}"
}

ISSUE_NUM=$(_get_issue_number)

# Verify gh is available
if ! command -v gh &>/dev/null || ! gh auth status &>/dev/null; then
    echo "ERROR: gh CLI not available or not authenticated" >&2
    exit 1
fi

echo "⏳ Waiting for approval on GitHub issue #${ISSUE_NUM} (stage ${STAGE})..."
echo "   Post a comment containing 'approved' on the issue to proceed."
echo "   Polling every ${POLL_INTERVAL}s (timeout: $(( MAX_POLLS * POLL_INTERVAL / 60 ))min)"

for (( i=1; i<=MAX_POLLS; i++ )); do
    comments_json=$(gh issue view "$ISSUE_NUM" --comments --json comments 2>/dev/null) || {
        echo "⚠ Failed to read issue comments (poll $i/$MAX_POLLS)" >&2
        sleep "$POLL_INTERVAL"
        continue
    }

    approved=$(echo "$comments_json" | jq -r '
        [.comments | to_entries[] | select(.value.body | startswith("## Stage")) | select(.value.body | test("AWAITING APPROVAL")) | .key] as $awaiting |
        if ($awaiting | length) == 0 then "no_awaiting"
        else
            ($awaiting | last) as $last_await |
            [.comments | to_entries[] | select(.key > $last_await) | select(.value.body | test("(?i)\\bapprove"))] |
            if length > 0 then "yes" else "no" end
        end
    ' 2>/dev/null) || approved="error"

    case "$approved" in
        yes)
            echo "✔ Approval received on GitHub issue #${ISSUE_NUM}. Proceeding."
            exit 0
            ;;
        no_awaiting)
            echo "⚠ No 'AWAITING APPROVAL' comment found on issue #${ISSUE_NUM}." >&2
            echo "  Run exit_stage.py first to post the awaiting comment." >&2
            exit 1
            ;;
        no)
            elapsed=$(( i * POLL_INTERVAL ))
            echo "   ⏳ Poll $i/$MAX_POLLS (${elapsed}s elapsed) — not yet approved"
            ;;
        *)
            echo "⚠ Error parsing comments (poll $i/$MAX_POLLS)" >&2
            ;;
    esac

    sleep "$POLL_INTERVAL"
done

echo "TIMEOUT: No approval after $(( MAX_POLLS * POLL_INTERVAL / 60 )) minutes." >&2
exit 1
