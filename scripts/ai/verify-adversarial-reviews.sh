#!/usr/bin/env bash
# verify-adversarial-reviews.sh — Audit adversarial cross-review compliance
#
# Checks recent session data, git history, and review artifacts to measure
# how often cross-review actually happens vs. how often it should.
#
# Usage:
#   scripts/ai/verify-adversarial-reviews.sh [--days N] [--json] [--verbose]
#
# Exit codes:
#   0 = compliance >= 80%
#   1 = compliance < 80%
#   2 = error
#
# Issue: #1538 | Policy: docs/standards/AI_REVIEW_ROUTING_POLICY.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Defaults
DAYS=30
JSON_OUTPUT=false
VERBOSE=false
COMPLIANCE_THRESHOLD=80

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --days) DAYS="$2"; shift 2 ;;
        --json) JSON_OUTPUT=true; shift ;;
        --verbose) VERBOSE=true; shift ;;
        --threshold) COMPLIANCE_THRESHOLD="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--days N] [--json] [--verbose] [--threshold N]"
            echo ""
            echo "Audits adversarial cross-review compliance over the last N days."
            echo ""
            echo "Options:"
            echo "  --days N        Look back N days (default: 30)"
            echo "  --json          Output results as JSON"
            echo "  --verbose       Show detailed findings"
            echo "  --threshold N   Compliance threshold percent (default: 80)"
            exit 0
            ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

cd "$REPO_ROOT"

log() {
    if $VERBOSE; then
        echo "[audit] $*" >&2
    fi
}

# ============================================================================
# 1. Check infrastructure exists
# ============================================================================
log "Checking review infrastructure..."

infra_score=0
infra_max=6
infra_findings=()

if [[ -f "docs/standards/AI_REVIEW_ROUTING_POLICY.md" ]]; then
    infra_score=$((infra_score + 1))
    infra_findings+=("PASS: AI_REVIEW_ROUTING_POLICY.md exists")
else
    infra_findings+=("FAIL: AI_REVIEW_ROUTING_POLICY.md missing")
fi

if [[ -f "docs/modules/ai/CROSS_REVIEW_POLICY.md" ]]; then
    infra_score=$((infra_score + 1))
    infra_findings+=("PASS: CROSS_REVIEW_POLICY.md exists")
else
    infra_findings+=("FAIL: CROSS_REVIEW_POLICY.md missing")
fi

if [[ -f "scripts/enforcement/require-cross-review.sh" ]]; then
    infra_score=$((infra_score + 1))
    infra_findings+=("PASS: require-cross-review.sh gate script exists")
else
    infra_findings+=("FAIL: require-cross-review.sh missing")
fi

if [[ -f "scripts/enforcement/require-plan-review.sh" ]]; then
    infra_score=$((infra_score + 1))
    infra_findings+=("PASS: require-plan-review.sh gate script exists")
else
    infra_findings+=("FAIL: require-plan-review.sh missing")
fi

if [[ -f ".claude/hooks/cross-review-gate.sh" ]]; then
    infra_score=$((infra_score + 1))
    infra_findings+=("PASS: cross-review-gate.sh hook exists")
else
    infra_findings+=("FAIL: cross-review-gate.sh hook missing")
fi

# Check hook is registered in settings.json
if [[ -f ".claude/settings.json" ]] && grep -q "cross-review-gate" ".claude/settings.json" 2>/dev/null; then
    infra_score=$((infra_score + 1))
    infra_findings+=("PASS: cross-review-gate.sh registered in settings.json")
else
    infra_findings+=("FAIL: cross-review-gate.sh not registered in settings.json")
fi

log "Infrastructure: $infra_score/$infra_max"

# ============================================================================
# 2. Count review artifacts in WRK/assets directories
# ============================================================================
log "Scanning review artifacts..."

wrk_dirs_total=0
wrk_dirs_with_review=0
review_artifact_files=()

if [[ -d "assets" ]]; then
    for d in assets/WRK-*/; do
        [[ -d "$d" ]] || continue
        wrk_dirs_total=$((wrk_dirs_total + 1))
        if find "$d" -maxdepth 2 -name "*review*" -o -name "*REVIEW*" 2>/dev/null | grep -q .; then
            wrk_dirs_with_review=$((wrk_dirs_with_review + 1))
        fi
    done
fi

# Count review results in scripts/review/results/
review_result_count=0
if [[ -d "scripts/review/results" ]]; then
    review_result_count=$(find scripts/review/results/ -type f -name "*.md" 2>/dev/null | wc -l)
fi

log "WRK dirs with review artifacts: $wrk_dirs_with_review / $wrk_dirs_total"
log "Review result files: $review_result_count"

# ============================================================================
# 3. Analyze git history for review evidence
# ============================================================================
log "Analyzing git history (last $DAYS days)..."

since_date=$(date -d "$DAYS days ago" +%Y-%m-%d 2>/dev/null || date -v-${DAYS}d +%Y-%m-%d 2>/dev/null)

# Total non-trivial commits
total_commits=$(git log --oneline --since="$since_date" | wc -l)
trivial_commits=$(git log --oneline --since="$since_date" | grep -ciE '(auto-sync|chore\(sync\)|merge branch)' || true)
nontrivial_commits=$((total_commits - trivial_commits))

# Commits with review evidence
review_commits=$(git log --oneline --since="$since_date" | grep -ciE '(cross-review|adversarial|codex review|gemini review|review finding)' || true)

# Commits with verdict evidence
verdict_commits=$(git log --oneline --since="$since_date" | grep -ciE '(APPROVE|MINOR|MAJOR|REQUEST_CHANGES)' || true)

# Commits explicitly addressing review feedback
feedback_commits=$(git log --oneline --since="$since_date" | grep -ciE '(address.*review|fix.*review|resolve.*review|review feedback)' || true)

log "Total commits: $total_commits (non-trivial: $nontrivial_commits)"
log "Review-related commits: $review_commits"
log "Verdict commits: $verdict_commits"
log "Feedback-addressing commits: $feedback_commits"

# ============================================================================
# 4. Check session signals for review events
# ============================================================================
log "Checking session signals..."

session_signal_count=0
review_signal_count=0

if [[ -d ".claude/state/session-signals" ]]; then
    session_signal_count=$(find .claude/state/session-signals/ -name "*.jsonl" -type f 2>/dev/null | wc -l)
    review_signal_count=$(grep -rlc 'review\|adversarial\|cross.review' .claude/state/session-signals/ 2>/dev/null | wc -l || echo 0)
fi

log "Session signal files: $session_signal_count"
log "Session signals with review mentions: $review_signal_count"

# ============================================================================
# 5. Check pending-reviews directory
# ============================================================================
pending_reviews_exists=false
pending_review_count=0
if [[ -d ".claude/state/pending-reviews" ]]; then
    pending_reviews_exists=true
    pending_review_count=$(find .claude/state/pending-reviews/ -type f 2>/dev/null | wc -l)
fi

# ============================================================================
# 6. Calculate compliance
# ============================================================================

# Compliance formula:
# - Infrastructure readiness: infra_score / infra_max (weighted 30%)
# - Artifact coverage: wrk_dirs_with_review / wrk_dirs_total (weighted 30%)
# - Git evidence: review_commits / nontrivial_commits (weighted 40%)
#
# We use integer math (multiply by 100 first)

if [[ $infra_max -gt 0 ]]; then
    infra_pct=$((infra_score * 100 / infra_max))
else
    infra_pct=0
fi

if [[ $wrk_dirs_total -gt 0 ]]; then
    artifact_pct=$((wrk_dirs_with_review * 100 / wrk_dirs_total))
else
    artifact_pct=0
fi

if [[ $nontrivial_commits -gt 0 ]]; then
    git_pct=$((review_commits * 100 / nontrivial_commits))
else
    git_pct=0
fi

# Weighted compliance
compliance=$(( (infra_pct * 30 + artifact_pct * 30 + git_pct * 40) / 100 ))

# ============================================================================
# 7. Output results
# ============================================================================

if $JSON_OUTPUT; then
    cat <<EOF
{
  "compliance_pct": $compliance,
  "threshold_pct": $COMPLIANCE_THRESHOLD,
  "pass": $([ $compliance -ge $COMPLIANCE_THRESHOLD ] && echo true || echo false),
  "days_analyzed": $DAYS,
  "infrastructure": {
    "score": $infra_score,
    "max": $infra_max,
    "pct": $infra_pct,
    "findings": $(printf '%s\n' "${infra_findings[@]}" | jq -R . | jq -s .)
  },
  "artifacts": {
    "wrk_dirs_total": $wrk_dirs_total,
    "wrk_dirs_with_review": $wrk_dirs_with_review,
    "pct": $artifact_pct,
    "review_result_files": $review_result_count
  },
  "git_evidence": {
    "total_commits": $total_commits,
    "nontrivial_commits": $nontrivial_commits,
    "review_commits": $review_commits,
    "verdict_commits": $verdict_commits,
    "feedback_commits": $feedback_commits,
    "pct": $git_pct
  },
  "session_signals": {
    "total_files": $session_signal_count,
    "with_review_mentions": $review_signal_count
  },
  "pending_reviews": {
    "directory_exists": $pending_reviews_exists,
    "file_count": $pending_review_count
  }
}
EOF
else
    echo "============================================"
    echo "  ADVERSARIAL REVIEW COMPLIANCE AUDIT"
    echo "  Period: last $DAYS days"
    echo "  Date: $(date +%Y-%m-%d)"
    echo "============================================"
    echo ""
    echo "INFRASTRUCTURE ($infra_score/$infra_max = ${infra_pct}%)"
    for f in "${infra_findings[@]}"; do
        echo "  $f"
    done
    echo ""
    echo "REVIEW ARTIFACTS"
    echo "  WRK dirs with review artifacts: $wrk_dirs_with_review / $wrk_dirs_total (${artifact_pct}%)"
    echo "  Review result files: $review_result_count"
    echo ""
    echo "GIT EVIDENCE (last $DAYS days)"
    echo "  Total commits: $total_commits (non-trivial: $nontrivial_commits)"
    echo "  Review-related commits: $review_commits (${git_pct}%)"
    echo "  Verdict commits: $verdict_commits"
    echo "  Feedback-addressing commits: $feedback_commits"
    echo ""
    echo "SESSION SIGNALS"
    echo "  Signal files: $session_signal_count"
    echo "  With review mentions: $review_signal_count"
    echo "  Pending reviews dir exists: $pending_reviews_exists"
    echo ""
    echo "============================================"
    echo "  OVERALL COMPLIANCE: ${compliance}%"
    echo "  Threshold: ${COMPLIANCE_THRESHOLD}%"
    if [[ $compliance -ge $COMPLIANCE_THRESHOLD ]]; then
        echo "  VERDICT: PASS"
    else
        echo "  VERDICT: FAIL"
    fi
    echo "============================================"
    echo ""
    echo "Formula: 30% infra + 30% artifacts + 40% git evidence"
    echo "  Infra:     ${infra_pct}% * 0.30 = $((infra_pct * 30 / 100))%"
    echo "  Artifacts: ${artifact_pct}% * 0.30 = $((artifact_pct * 30 / 100))%"
    echo "  Git:       ${git_pct}% * 0.40 = $((git_pct * 40 / 100))%"
fi

# Exit code based on compliance
if [[ $compliance -ge $COMPLIANCE_THRESHOLD ]]; then
    exit 0
else
    exit 1
fi
