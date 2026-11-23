#!/usr/bin/env bash
# ABOUTME: Daily cron script that audits commit review compliance.
# ABOUTME: Scans recent commits, checks for review evidence, and files GitHub issues for backlogs.
# Writes JSON summary to logs/maintenance/review-audit-YYYYMMDD.json
# Exit 0 = audit ran successfully; Exit 1 = operational failure.

set -uo pipefail

# ── Ensure PATH for cron environment ────────────────────────────────────────
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"

# ── Configuration ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "ERROR: Not inside a git repository" >&2
    exit 1
}

AUDIT_HOURS="${AUDIT_HOURS:-24}"
REVIEW_COMPLIANCE_THRESHOLD="${REVIEW_COMPLIANCE_THRESHOLD:-80}"
DATE="$(date +%Y-%m-%d)"
DATE_COMPACT="$(date +%Y%m%d)"
LOG_DIR="$REPO_ROOT/logs/maintenance"
JSON_OUTPUT="$LOG_DIR/review-audit-${DATE_COMPACT}.json"
DRY_RUN="${DRY_RUN:-false}"
GH_AUTHENTICATED="false"
GH_AUTH_ERROR=""

mkdir -p "$LOG_DIR"

# ── Auth Check ────────────────────────────────────────────────────────────────
# Verify gh CLI authentication upfront so we fail fast.
if command -v gh >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
        GH_AUTHENTICATED="true"
        echo "gh auth: authenticated"
    else
        GH_AUTHENTICATED="false"
        GH_AUTH_ERROR="gh CLI is not authenticated; cannot create or update review backlog issues"
        echo "WARNING: gh CLI is not authenticated — issue creation will be skipped" >&2
    fi
else
    GH_AUTHENTICATED="false"
    GH_AUTH_ERROR="gh CLI is not installed"
    echo "WARNING: gh CLI is not installed — issue creation will be skipped" >&2
fi

# ── Helpers ───────────────────────────────────────────────────────────────────
die() { echo "ERROR: $*" >&2; exit 1; }

# Classify a commit message as requiring review or not.
# Returns 0 (needs review) for feature/fix commits.
# Returns 1 (skip) for chore/docs/style/ci/test/refactor/merge/revert.
commit_needs_review() {
    local msg="$1"
    local msg_lower
    msg_lower="$(echo "$msg" | tr '[:upper:]' '[:lower:]')"

    # Skip: conventional commit types that don't need review
    # chore, docs, style, ci, test, build, revert, merge
    if echo "$msg_lower" | grep -qE '^(chore|docs|style|ci|test|tests|build|revert|merge)(\(|:| )'; then
        return 1
    fi

    # Skip: merge commits
    if echo "$msg_lower" | grep -qE '^merge (branch|pull|remote|tag)'; then
        return 1
    fi

    # Skip: docs-only indicators
    if echo "$msg_lower" | grep -qE '^\[docs\]|^\[skip.?review\]|^wip:'; then
        return 1
    fi

    # Everything else (feat, fix, perf, refactor with code, or untyped) needs review
    return 0
}

# Check if a commit has review evidence.
# Returns 0 if evidence found, 1 if not.
commit_has_review_evidence() {
    local commit_hash="$1"
    local commit_msg="$2"
    local commit_ts="$3"  # epoch timestamp of the commit
    local audit_start="$4"  # epoch timestamp of audit window start

    # Evidence 1: Review results in scripts/review/results/ within audit window
    local results_dir="$REPO_ROOT/scripts/review/results"
    if [[ -d "$results_dir" ]]; then
        while IFS= read -r f; do
            if [[ -n "$f" ]]; then
                local file_mtime
                file_mtime="$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0)"
                if [[ "$file_mtime" -ge "$audit_start" ]]; then
                    return 0
                fi
            fi
        done < <(find "$results_dir" -type f -newer "$REPO_ROOT/.git/HEAD" -o -type f -newermt "@${audit_start}" 2>/dev/null | head -20)
        # Fallback: check any files modified within window
        while IFS= read -r f; do
            if [[ -n "$f" ]]; then
                return 0
            fi
        done < <(find "$results_dir" -type f -newermt "$(date -d "@${audit_start}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r "${audit_start}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null)" 2>/dev/null | head -5)
    fi

    # Evidence 2: REVIEWS.md in .planning/phases/ or .planning/quick/ modified within window
    local planning_dir="$REPO_ROOT/.planning"
    if [[ -d "$planning_dir" ]]; then
        while IFS= read -r f; do
            if [[ -n "$f" ]]; then
                local file_mtime
                file_mtime="$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0)"
                if [[ "$file_mtime" -ge "$audit_start" ]]; then
                    return 0
                fi
            fi
        done < <(find "$planning_dir/phases" "$planning_dir/quick" -name "REVIEWS.md" 2>/dev/null)
    fi

    # Evidence 3: .claude/reports/*review* modified within window
    local reports_dir="$REPO_ROOT/.claude/reports"
    if [[ -d "$reports_dir" ]]; then
        while IFS= read -r f; do
            if [[ -n "$f" ]]; then
                local file_mtime
                file_mtime="$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0)"
                if [[ "$file_mtime" -ge "$audit_start" ]]; then
                    return 0
                fi
            fi
        done < <(find "$reports_dir" -iname "*review*" -type f 2>/dev/null)
    fi

    # Evidence 4: Commit message contains review-related keywords
    local msg_lower
    msg_lower="$(echo "$commit_msg" | tr '[:upper:]' '[:lower:]')"
    if echo "$msg_lower" | grep -qiE '(review|codex|gemini|adversarial|cross-review|cross_review|reviewed-by|reviewed.by)'; then
        return 0
    fi

    return 1
}

# ── Main Logic ────────────────────────────────────────────────────────────────
cd "$REPO_ROOT"

echo "=== Review Audit Report — $DATE ==="
echo "Audit window: last ${AUDIT_HOURS} hours"
echo "Compliance threshold: ${REVIEW_COMPLIANCE_THRESHOLD}%"
echo ""

# Calculate audit window timestamps
AUDIT_START_EPOCH="$(date -d "${AUDIT_HOURS} hours ago" +%s 2>/dev/null || date -v-${AUDIT_HOURS}H +%s 2>/dev/null)" || die "Cannot compute audit start time"
NOW_EPOCH="$(date +%s)"
SINCE_DATE="$(date -d "@${AUDIT_START_EPOCH}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r "${AUDIT_START_EPOCH}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null)"

# Collect commits in the audit window
TOTAL_COMMITS=0
FEATURE_FIX_COMMITS=0
REVIEWED_COMMITS=0
CHORE_DOC_COMMITS=0
UNREVIEWED_HASHES=()
UNREVIEWED_MESSAGES=()

while IFS='|' read -r hash timestamp message; do
    [[ -z "$hash" ]] && continue
    TOTAL_COMMITS=$((TOTAL_COMMITS + 1))

    if commit_needs_review "$message"; then
        FEATURE_FIX_COMMITS=$((FEATURE_FIX_COMMITS + 1))

        if commit_has_review_evidence "$hash" "$message" "$timestamp" "$AUDIT_START_EPOCH"; then
            REVIEWED_COMMITS=$((REVIEWED_COMMITS + 1))
        else
            UNREVIEWED_HASHES+=("$hash")
            UNREVIEWED_MESSAGES+=("$message")
        fi
    else
        CHORE_DOC_COMMITS=$((CHORE_DOC_COMMITS + 1))
    fi
done < <(git log --since="${AUDIT_HOURS} hours ago" --format='%H|%ct|%s' 2>/dev/null)

# Compute compliance percentage
if [[ "$FEATURE_FIX_COMMITS" -eq 0 ]]; then
    COMPLIANCE=100
else
    # Integer arithmetic: multiply first, then divide to avoid truncation
    COMPLIANCE=$(( (REVIEWED_COMMITS * 100) / FEATURE_FIX_COMMITS ))
fi

UNREVIEWED_COUNT=${#UNREVIEWED_HASHES[@]}

# (gh auth already checked at script start)

# ── Output ────────────────────────────────────────────────────────────────────
echo "Summary:"
echo "  Total commits:        $TOTAL_COMMITS"
echo "  Feature/fix commits:  $FEATURE_FIX_COMMITS"
echo "  Chore/docs commits:   $CHORE_DOC_COMMITS"
echo "  Reviewed:             $REVIEWED_COMMITS"
echo "  Unreviewed:           $UNREVIEWED_COUNT"
echo "  Compliance:           ${COMPLIANCE}%"
echo ""

if [[ "$COMPLIANCE" -ge "$REVIEW_COMPLIANCE_THRESHOLD" ]]; then
    echo "PASS: Review compliance meets threshold (${COMPLIANCE}% >= ${REVIEW_COMPLIANCE_THRESHOLD}%)"
else
    echo "FAIL: Review compliance below threshold (${COMPLIANCE}% < ${REVIEW_COMPLIANCE_THRESHOLD}%)"
fi

# List unreviewed commits
if [[ "$UNREVIEWED_COUNT" -gt 0 ]]; then
    echo ""
    echo "Unreviewed commits:"
    for i in "${!UNREVIEWED_HASHES[@]}"; do
        echo "  ${UNREVIEWED_HASHES[$i]:0:12} ${UNREVIEWED_MESSAGES[$i]}"
    done
fi

# ── Write JSON summary ───────────────────────────────────────────────────────
cat > "$JSON_OUTPUT" <<EOF
{
  "date": "$DATE",
  "audit_hours": $AUDIT_HOURS,
  "audit_start": "$SINCE_DATE",
  "total_commits": $TOTAL_COMMITS,
  "feature_fix_commits": $FEATURE_FIX_COMMITS,
  "chore_doc_commits": $CHORE_DOC_COMMITS,
  "reviewed_commits": $REVIEWED_COMMITS,
  "unreviewed_commits": $UNREVIEWED_COUNT,
  "compliance_percent": $COMPLIANCE,
  "threshold_percent": $REVIEW_COMPLIANCE_THRESHOLD,
  "gh_authenticated": ${GH_AUTHENTICATED},
  "gh_auth_error": "$(echo "$GH_AUTH_ERROR" | sed 's/"/\\"/g')",
  "pass": $([ "$COMPLIANCE" -ge "$REVIEW_COMPLIANCE_THRESHOLD" ] && echo "true" || echo "false"),
  "unreviewed": [
$(for i in "${!UNREVIEWED_HASHES[@]}"; do
    # Escape double quotes in commit messages for valid JSON
    escaped_msg="$(echo "${UNREVIEWED_MESSAGES[$i]}" | sed 's/"/\\"/g')"
    if [[ $i -lt $((UNREVIEWED_COUNT - 1)) ]]; then
        echo "    {\"hash\": \"${UNREVIEWED_HASHES[$i]}\", \"message\": \"${escaped_msg}\"},"
    else
        echo "    {\"hash\": \"${UNREVIEWED_HASHES[$i]}\", \"message\": \"${escaped_msg}\"}"
    fi
done)
  ]
}
EOF

echo ""
echo "JSON summary written to: $JSON_OUTPUT"

# ── Create GitHub issue if compliance is below threshold ──────────────────────
if [[ "$COMPLIANCE" -lt "$REVIEW_COMPLIANCE_THRESHOLD" && "$UNREVIEWED_COUNT" -gt 0 ]]; then
    ISSUE_TITLE="Review backlog: ${UNREVIEWED_COUNT} unreviewed commits from ${DATE}"

    # Build issue body
    ISSUE_BODY="## Review Compliance Audit — ${DATE}

**Compliance:** ${COMPLIANCE}% (threshold: ${REVIEW_COMPLIANCE_THRESHOLD}%)
**Audit window:** last ${AUDIT_HOURS} hours (since ${SINCE_DATE})
**Total commits:** ${TOTAL_COMMITS} | **Feature/fix:** ${FEATURE_FIX_COMMITS} | **Reviewed:** ${REVIEWED_COMMITS}

### Unreviewed Commits

| Hash | Message | Diff Stats |
|------|---------|------------|"

    for i in "${!UNREVIEWED_HASHES[@]}"; do
        h="${UNREVIEWED_HASHES[$i]}"
        m="${UNREVIEWED_MESSAGES[$i]}"
        # Get diff --stat for this commit (compact)
        diffstat="$(git diff --stat "${h}^..${h}" 2>/dev/null | tail -1 | sed 's/|//g' || echo 'N/A')"
        ISSUE_BODY="${ISSUE_BODY}
| \`${h:0:12}\` | ${m} | ${diffstat} |"
    done

    ISSUE_BODY="${ISSUE_BODY}

### Next Steps
- [ ] Run cross-review on unreviewed commits
- [ ] Update REVIEWS.md with findings
- [ ] Close this issue when compliance is restored

---
*Auto-generated by \`scripts/maintenance/review-audit.sh\`*"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        echo "[DRY RUN] Would create GitHub issue:"
        echo "  Title: $ISSUE_TITLE"
        echo "  Labels: maintenance, review-backlog"
        echo ""
        echo "$ISSUE_BODY"
    elif [[ -n "$GH_AUTH_ERROR" ]]; then
        echo ""
        echo "WARNING: Skipping GitHub issue creation — $GH_AUTH_ERROR" >&2
    else
        echo ""
        echo "Creating or updating GitHub issue for review backlog..."

        # Ensure required labels exist (idempotent: ignore if already present)
        gh label create "maintenance" --description "Maintenance & housekeeping" --color "0052CC" 2>/dev/null || true
        gh label create "review-backlog" --description "Commits lacking review evidence" --color "FBCA04" 2>/dev/null || true

        # Search for existing open issue with matching title to avoid duplicates
        EXISTING_ISSUE_NUMBER="$(gh issue list --state open --label "review-backlog" --search "Review backlog:" --json number,title --jq '.[0].number' 2>/dev/null || true)"

        if [[ -n "$EXISTING_ISSUE_NUMBER" && "$EXISTING_ISSUE_NUMBER" != "null" ]]; then
            gh issue comment "$EXISTING_ISSUE_NUMBER" --body "## Update — ${DATE}\n\n$ISSUE_BODY" >/dev/null
            echo "Updated existing review backlog issue: #$EXISTING_ISSUE_NUMBER"
        else
            ISSUE_URL="$(gh issue create \
                --title "$ISSUE_TITLE" \
                --body "$ISSUE_BODY" \
                --label "maintenance" \
                --label "review-backlog" \
                2>&1)" || {
                echo "WARNING: Failed to create GitHub issue: $ISSUE_URL" >&2
                echo "(gh CLI may not be authenticated or repo may not have issues enabled)"
            }

            if [[ -n "$ISSUE_URL" && "$ISSUE_URL" == http* ]]; then
                echo "Issue created: $ISSUE_URL"
            fi
        fi
    fi
fi

echo ""
echo "=== Review audit complete ==="
exit 0
