#!/usr/bin/env bash
# bootstrap-stage5-gate.sh — Stage 5 gate bootstrap inventory and dry-run
#
# Usage:
#   bootstrap-stage5-gate.sh --dry-run [--report <path>]
#   bootstrap-stage5-gate.sh --dry-run --wrk-id WRK-NNN [--report <path>]
#   bootstrap-stage5-gate.sh --apply   (after dry-run shows go)
#
# Exit codes:
#   0 = go (no blocking issues found; safe to wire next entrypoint)
#   1 = no-go (one or more blocking issues require resolution before live wiring)
#   2 = infrastructure failure (cannot determine state; abort)
#
# Report path default: .claude/work-queue/assets/WRK-1017/evidence/bootstrap-stage5-gate-report.yaml
set -euo pipefail

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
DEFAULT_REPORT="${QUEUE_DIR}/assets/WRK-1017/evidence/bootstrap-stage5-gate-report.yaml"
CHECKER="${WORKSPACE_ROOT}/scripts/work-queue/verify-gate-evidence.py"

mode=""
report_path="$DEFAULT_REPORT"
single_wrk=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) mode="dry_run"; shift ;;
        --apply)   mode="apply";   shift ;;
        --report)  report_path="$2"; shift 2 ;;
        --wrk-id)  single_wrk="$2"; shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 2 ;;
    esac
done

if [[ -z "$mode" ]]; then
    echo "Usage: bootstrap-stage5-gate.sh --dry-run [--report <path>] [--wrk-id WRK-NNN]" >&2
    echo "       bootstrap-stage5-gate.sh --apply" >&2
    exit 2
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: uv not found — required for checker invocation." >&2
    exit 2
fi

# Discover candidate WRK files (exclude archive)
discover_wrk_files() {
    local dirs=("pending" "working" "blocked" "done")
    for d in "${dirs[@]}"; do
        local dir="${QUEUE_DIR}/${d}"
        if [[ -d "$dir" ]]; then
            find "$dir" -maxdepth 1 -name 'WRK-*.md' 2>/dev/null || true
        fi
    done
}

# Determine if a WRK is Stage 5+ candidate (has stage evidence or plan_approved=true)
is_stage5_candidate() {
    local wrk_file="$1"
    local wrk_id
    wrk_id="$(basename "$wrk_file" .md)"
    local assets_dir="${QUEUE_DIR}/assets/${wrk_id}"
    local evidence_dir="${assets_dir}/evidence"
    # Has stage evidence yaml (authoritative stage source)
    if [[ -f "${evidence_dir}/stage-evidence.yaml" ]]; then
        return 0
    fi
    # Has plan_approved=true in frontmatter (fallback heuristic)
    if grep -q "^plan_approved: true" "$wrk_file" 2>/dev/null; then
        return 0
    fi
    return 1
}

eligible_wrks=()
bootstrap_incomplete=()
go_wrks=()
nogo_wrks=()
exemption_wrks=()

if [[ -n "$single_wrk" ]]; then
    # Single WRK debugging mode
    cand_file="${QUEUE_DIR}/pending/${single_wrk}.md"
    for d in pending working blocked done; do
        if [[ -f "${QUEUE_DIR}/${d}/${single_wrk}.md" ]]; then
            cand_file="${QUEUE_DIR}/${d}/${single_wrk}.md"
            break
        fi
    done
    if [[ ! -f "$cand_file" ]]; then
        echo "ERROR: ${single_wrk} not found in queue dirs" >&2
        exit 2
    fi
    all_wrk_files=("$cand_file")
else
    mapfile -t all_wrk_files < <(discover_wrk_files | sort)
fi

for wrk_file in "${all_wrk_files[@]}"; do
    wrk_id="$(basename "$wrk_file" .md)"
    assets_dir="${QUEUE_DIR}/assets/${wrk_id}"
    evidence_dir="${assets_dir}/evidence"

    if ! is_stage5_candidate "$wrk_file"; then
        continue
    fi

    eligible_wrks+=("$wrk_id")

    # Check for bootstrap_incomplete (no stage evidence)
    if [[ ! -f "${evidence_dir}/stage-evidence.yaml" ]]; then
        bootstrap_incomplete+=("$wrk_id")
        nogo_wrks+=("${wrk_id}:bootstrap_incomplete")
        continue
    fi

    # Run Stage 5 canonical checker in stage5-check mode
    stage5_exit=0
    stage5_out="$(uv run --no-project python "$CHECKER" --stage5-check "$wrk_id" 2>&1)" \
        || stage5_exit=$?

    if [[ "$stage5_exit" -eq 0 ]]; then
        go_wrks+=("$wrk_id")
    elif [[ "$stage5_exit" -eq 1 ]]; then
        # Check if an exemption exists
        if [[ -f "${evidence_dir}/stage5-migration-exemption.yaml" ]]; then
            exemption_wrks+=("$wrk_id")
            # Exemption validity was already checked by the canonical checker above
            # (if exit=1, even with exemption file, the exemption failed validation)
            nogo_wrks+=("${wrk_id}:exemption_invalid")
        else
            nogo_wrks+=("${wrk_id}:predicate_fail")
        fi
    elif [[ "$stage5_exit" -eq 2 ]]; then
        nogo_wrks+=("${wrk_id}:infra_fail")
    fi
done

eligible_count="${#eligible_wrks[@]}"
nogo_count="${#nogo_wrks[@]}"
go_count="${#go_wrks[@]}"
incomplete_count="${#bootstrap_incomplete[@]}"

# Compute unresolved history ratio (simplified: incomplete/eligible)
unresolved_ratio="0"
if [[ "$eligible_count" -gt 0 ]]; then
    # Shell integer division; use awk for ratio
    unresolved_ratio="$(awk "BEGIN {printf \"%.3f\", ${incomplete_count}/${eligible_count}}")"
fi

# Thresholds from plan: abort if unresolved-history > max(2, 20% of eligible)
nogo_threshold_count=2
nogo_threshold_ratio="0.20"
over_threshold=false
if [[ "$incomplete_count" -gt "$nogo_threshold_count" ]]; then
    over_threshold=true
fi
# Check ratio via awk
if awk "BEGIN {exit (${unresolved_ratio} <= ${nogo_threshold_ratio}) ? 0 : 1}"; then
    : # ratio within threshold
else
    over_threshold=true
fi

decision="go"
if [[ "$nogo_count" -gt 0 ]]; then
    decision="no_go"
fi
if [[ "$over_threshold" == "true" ]]; then
    decision="no_go"
fi

# Write report
mkdir -p "$(dirname "$report_path")"
timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "$report_path" << YAML
# bootstrap-stage5-gate-report.yaml — go/no-go report for Stage 5 gate rollout
generated_at: "${timestamp}"
mode: "${mode}"
decision: "${decision}"
eligible_wrk_count: ${eligible_count}
go_count: ${go_count}
nogo_count: ${nogo_count}
unresolved_history_count: ${incomplete_count}
unresolved_history_ratio: ${unresolved_ratio}
over_threshold: ${over_threshold}
proposed_first_gated_writes: []
proposed_exemptions: []
go_wrks:
$(for w in "${go_wrks[@]+"${go_wrks[@]}"}"; do echo "  - ${w}"; done)
nogo_wrks:
$(for w in "${nogo_wrks[@]+"${nogo_wrks[@]}"}"; do echo "  - ${w}"; done)
bootstrap_incomplete_wrks:
$(for w in "${bootstrap_incomplete[@]+"${bootstrap_incomplete[@]}"}"; do echo "  - ${w}"; done)
YAML

echo "Bootstrap Stage 5 gate ${mode} complete."
echo "  eligible_wrk_count: ${eligible_count}"
echo "  go_count: ${go_count}"
echo "  nogo_count: ${nogo_count}"
echo "  unresolved_history_count: ${incomplete_count}"
echo "  unresolved_history_ratio: ${unresolved_ratio}"
echo "  decision: ${decision}"
echo "  report: ${report_path}"

if [[ "$decision" == "no_go" ]]; then
    echo ""
    echo "✖ Bootstrap decision: NO_GO — resolve blocking issues before wiring live entrypoints." >&2
    exit 1
fi

echo ""
echo "✔ Bootstrap decision: GO — safe to proceed with next entrypoint wiring."
exit 0
