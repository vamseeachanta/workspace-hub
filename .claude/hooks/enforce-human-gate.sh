#!/usr/bin/env bash
# WRK-1316 L3 Hook: Block exit_stage.py on human-gate stages without approval evidence
#
# For stages 1, 5, 7, 17 (human gates), exit_stage.py must not be called
# unless the approval evidence file exists AND has a non-zero file age
# (prevents instant write-then-exit within same second).
#
# Receives tool input on stdin as JSON from Claude Code PreToolUse.
# Exit 0 = allow, Exit 2 = block with message.

set -euo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)}"

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null)

# Only check exit_stage.py calls
if ! echo "$COMMAND" | grep -qP 'exit_stage\.py' 2>/dev/null; then
    exit 0
fi

# Extract WRK ID and stage number
WRK_ID=$(echo "$COMMAND" | grep -oP 'WRK-\d+' | head -1)
STAGE=$(echo "$COMMAND" | grep -oP 'WRK-\d+\s+(\d+)' | grep -oP '\d+$')

if [[ -z "$WRK_ID" || -z "$STAGE" ]]; then
    exit 0  # Can't parse — allow (exit_stage.py will validate internally)
fi

# Check if this is a human gate stage
HG_SCRIPT="$REPO_ROOT/scripts/work-queue/is-human-gate.sh"
if [[ ! -f "$HG_SCRIPT" ]]; then
    exit 0
fi

if ! bash "$HG_SCRIPT" "$STAGE" 2>/dev/null; then
    exit 0  # Not a human gate — allow
fi

# It IS a human gate. Check for approval evidence.
EVIDENCE_DIR="$REPO_ROOT/.claude/work-queue/assets/$WRK_ID/evidence"

# ── WRK-5104: GitHub issue comment-based approval (checked first) ─────────

# Explicit escape hatch
if [[ "${SKIP_GATE_GITHUB_CHECK:-0}" == "1" ]]; then
    GITHUB_CHECK="skip"
else
    GITHUB_CHECK="try"
fi

_check_github_approval() {
    # Read github_issue_ref from WRK frontmatter
    local wrk_file=""
    for folder in pending working done; do
        local candidate="$REPO_ROOT/.claude/work-queue/$folder/$WRK_ID.md"
        if [[ -f "$candidate" ]]; then
            wrk_file="$candidate"
            break
        fi
    done
    [[ -z "$wrk_file" ]] && return 1

    local issue_ref
    issue_ref=$(grep -m1 '^github_issue_ref:' "$wrk_file" 2>/dev/null | sed 's/^github_issue_ref:\s*//' | tr -d '"'"'" | xargs)
    [[ -z "$issue_ref" ]] && return 1

    local issue_num="${issue_ref##*/}"
    [[ -z "$issue_num" ]] && return 1

    # Check gh is available and authenticated
    if ! command -v gh &>/dev/null || ! gh auth status &>/dev/null; then
        return 1  # Fall back to local
    fi

    # Read comments as JSON
    local comments_json
    comments_json=$(gh issue view "$issue_num" --comments --json comments 2>/dev/null) || return 1

    # Find the last "AWAITING APPROVAL" comment index, then check for "approved" after it
    # Uses jq: find last AWAITING index, then check if any comment after it contains "approved"
    local approved
    approved=$(echo "$comments_json" | jq -r '
        [.comments | to_entries[] | select(.value.body | test("AWAITING APPROVAL")) | .key] as $awaiting |
        if ($awaiting | length) == 0 then "no_awaiting"
        else
            ($awaiting | last) as $last_await |
            [.comments | to_entries[] | select(.key > $last_await) | select(.value.body | test("(?i)approved"))] |
            if length > 0 then "yes" else "no" end
        end
    ' 2>/dev/null) || return 1

    if [[ "$approved" == "yes" ]]; then
        return 0  # Approved on GitHub
    fi
    return 2  # AWAITING exists but no approval yet
}

if [[ "$GITHUB_CHECK" == "try" ]]; then
    _check_github_approval
    gh_result=$?
    if [[ $gh_result -eq 0 ]]; then
        # Approved via GitHub comment
        exit 0
    elif [[ $gh_result -eq 2 ]]; then
        # AWAITING APPROVAL posted but no approval comment yet
        echo "BLOCKED: Stage $STAGE awaiting approval on GitHub issue." >&2
        echo "  Comment 'approved' on the GitHub issue to proceed." >&2
        echo "  (Or set SKIP_GATE_GITHUB_CHECK=1 to use local evidence instead)" >&2
        exit 2
    fi
    # gh_result == 1: GitHub unavailable, fall through to local check
fi

# ── Local evidence fallback ───────────────────────────────────────────────

# Map stage → expected evidence file and field
case "$STAGE" in
    1)
        GATE_FILE="$EVIDENCE_DIR/user-review-capture.yaml"
        GATE_FIELD="scope_approved"
        GATE_VALUE="true"
        ;;
    5)
        GATE_FILE="$EVIDENCE_DIR/user-review-plan-draft.yaml"
        GATE_FIELD="decision"
        GATE_VALUE="approved"
        ;;
    7)
        GATE_FILE="$EVIDENCE_DIR/plan-final-review.yaml"
        GATE_FIELD="decision"
        GATE_VALUE="passed"
        ;;
    17)
        GATE_FILE="$EVIDENCE_DIR/user-review-close.yaml"
        GATE_FIELD="decision"
        GATE_VALUE="approved"
        ;;
    *)
        exit 0
        ;;
esac

# Check evidence file exists
if [[ ! -f "$GATE_FILE" ]]; then
    echo "BLOCKED: Stage $STAGE is a human gate. Evidence file missing: $(basename $GATE_FILE)" >&2
    echo "  STOP and wait for user to type: \"I approve stage $STAGE\"" >&2
    echo "  Then write the evidence file via Write tool, THEN call exit_stage.py." >&2
    exit 2
fi

# Check the approval field is present and correct
if ! grep -q "${GATE_FIELD}:.*${GATE_VALUE}" "$GATE_FILE" 2>/dev/null; then
    echo "BLOCKED: Stage $STAGE evidence missing ${GATE_FIELD}: ${GATE_VALUE}" >&2
    echo "  Wait for user approval before calling exit_stage.py." >&2
    exit 2
fi

# Check evidence file is not brand-new (prevent write-then-immediate-exit)
# 30 seconds minimum — agent cannot trivially sleep past this, and real user
# interaction always takes longer than 30 seconds.
FILE_AGE_S=$(( $(date +%s) - $(stat -c %Y "$GATE_FILE" 2>/dev/null || echo "$(date +%s)") ))
if [[ "$FILE_AGE_S" -lt 30 ]]; then
    REMAINING=$(( 30 - FILE_AGE_S ))
    echo "BLOCKED: Stage $STAGE approval evidence written only ${FILE_AGE_S}s ago (minimum 30s)." >&2
    echo "  Real user review takes > 30 seconds. Do NOT use 'sleep' to bypass this." >&2
    echo "  If user genuinely approved, wait ${REMAINING}s and retry exit_stage.py." >&2
    exit 2
fi

exit 0
