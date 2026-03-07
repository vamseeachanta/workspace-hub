#!/usr/bin/env bash
# comprehensive-learning.sh — Session Learning Pipeline orchestrator (v2.0.0)
# Implements the 10-phase pipeline from comprehensive-learning SKILL.md.
# Runs on ace-linux-1 only. Other machines commit/push state files.

set -uo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
STATE_DIR="${WS_HUB}/.claude/state"
LEARNING_REPORTS_DIR="${STATE_DIR}/learning-reports"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
REPORT_FILE="${LEARNING_REPORTS_DIR}/${TIMESTAMP}.md"
START_TIME=$(date +%s)

# Determine analysis date (forward to session-analysis.sh)
ANALYSIS_DATE_ARG=""
if [[ "${1:-}" == "--date" && -n "${2:-}" ]]; then
    ANALYSIS_DATE_ARG="--date $2"
fi

mkdir -p "$LEARNING_REPORTS_DIR"

# --- Machine Identity ---
MACHINE=$(hostname | tr '[:upper:]' '[:lower:]')

# --- Single-Machine Guard ---
if [[ "$MACHINE" != "ace-linux-1" ]]; then
  echo "comprehensive-learning runs on ace-linux-1 only."
  echo "From this machine, commit state files and push:"
  
  # State files to commit
  cd "$WS_HUB"
  git add .claude/state/candidates/ \
          .claude/state/corrections/ \
          .claude/state/patterns/ \
          .claude/state/reflect-history/ \
          .claude/state/trends/ \
          .claude/state/session-signals/ \
          .claude/state/cc-insights/ \
          .claude/state/learned-patterns.json \
          .claude/state/skill-scores.yaml \
          .claude/state/cc-user-insights.yaml
  
  if ! git diff --staged --quiet; then
    git commit -m "chore: session learnings from $(hostname)"
    git push origin main
    echo "Learning state pushed."
  else
    echo "No new learning state to push."
  fi
  exit 0
fi

# --- Status Tracking ---
# Format: "Phase | Status | Notes"
PHASE_RESULTS=()

log_phase() {
    local phase="$1"
    local status="$2"
    local notes="$3"
    PHASE_RESULTS+=("${phase}|${status}|${notes}")
    echo "[comprehensive-learning] ${phase}: ${status} - ${notes}"
}

# --- Phase 10: Report (registered via trap) ---
write_report() {
    echo "--- Phase 10: Report ---"
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))

    {
        printf "# Learning Report — %s\n\n" "$(date)"
        printf "| Phase | Status | Notes |\n"
        printf "|-------|--------|-------|\n"
        for result in "${PHASE_RESULTS[@]}"; do
            IFS='|' read -r p s n <<< "$result"
            printf "| %s | %s | %s |\n" "$p" "$s" "$n"
        done
        printf "\n"
        printf "Machine: ace-linux-1 | Mode: full | Elapsed: %ds\n" "$ELAPSED"
    } > "$REPORT_FILE"

    echo "Report written to ${REPORT_FILE}"
}
trap write_report EXIT

# --- Analysis Helpers (via Python) ---
ANALYSIS_PY="${WS_HUB}/scripts/analysis/comprehensive_learning_pipeline.py"

run_py_phase() {
    local phase_num="$1"
    local phase_name="$2"
    echo "--- Phase ${phase_num}: ${phase_name} ---"
    
    local output
    output=$(python3 "$ANALYSIS_PY" "$phase_num")
    
    # Extract the PHASE_RESULT line
    local result_line
    result_line=$(echo "$output" | grep "^PHASE_RESULT|" | tail -1)
    
    if [[ -n "$result_line" ]]; then
        IFS='|' read -r prefix num status notes <<< "$result_line"
        log_phase "${num} ${phase_name}" "$status" "$notes"
    else
        log_phase "${phase_num} ${phase_name}" "FAILED" "Python analysis script failed"
    fi
}

# --- Step 0: Git Pull (Aggregate contributions) ---
echo "--- Step 0: Aggregating machine contributions ---"
git -C "$WS_HUB" pull --no-rebase origin main --quiet || echo "Warning: git pull failed"

# --- Phase 1: Insights (mandatory) ---
echo "--- Phase 1: Insights ---"
if bash "${WS_HUB}/scripts/analysis/session-analysis.sh" ${ANALYSIS_DATE_ARG} > /tmp/cl_phase1.log 2>&1; then
    log_phase "1 Insights" "DONE" "Processed session signals"
    # Additional session-quality signals via Python
    run_py_phase "1" "Quality Signals"
else
    log_phase "1 Insights" "FAILED" "session-analysis.sh failed"
    exit 1
fi

# --- Phase 1b: Drift Detection ---
DETECT_DRIFT="${WS_HUB}/scripts/session/detect-drift.sh"
YESTERDAY=$(date -d "yesterday" +%Y%m%d 2>/dev/null || date -v-1d +%Y%m%d 2>/dev/null || true)
LAST_LOG="${WS_HUB}/logs/orchestrator/claude/session_${YESTERDAY}.jsonl"
if [[ -f "$DETECT_DRIFT" && -f "$LAST_LOG" ]]; then
    if bash "$DETECT_DRIFT" --log "$LAST_LOG" --since "$YESTERDAY" > /tmp/cl_drift.log 2>&1; then
        log_phase "1b Drift Detection" "DONE" "Drift summary appended to .claude/state/drift-summary.yaml"
        # Append drift violation counts to session-quality signals YAML
        SIGNALS_DIR="${WS_HUB}/.claude/state/session-signals"
        mkdir -p "$SIGNALS_DIR"
        py_viol=$(grep "^python_runtime:" /tmp/cl_drift.log | awk '{print $2}' || echo 0)
        fp_viol=$(grep "^file_placement:" /tmp/cl_drift.log | awk '{print $2}' || echo 0)
        gw_viol=$(grep "^git_workflow:" /tmp/cl_drift.log | awk '{print $2}' || echo 0)
        printf -- '{"event":"drift_counts","ts":"%s","date":"%s","python_runtime_violations":%s,"file_placement_violations":%s,"git_workflow_violations":%s}\n' \
          "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$YESTERDAY" "$py_viol" "$fp_viol" "$gw_viol" \
          >> "${SIGNALS_DIR}/drift-counts.jsonl" || true
    else
        log_phase "1b Drift Detection" "WARN" "detect-drift.sh failed (non-fatal)"
    fi
else
    log_phase "1b Drift Detection" "SKIP" "No session log for ${YESTERDAY} or detect-drift.sh missing"
fi

# --- Phase 2: Reflect (non-mandatory) ---
echo "--- Phase 2: Reflect ---"
REFLECT_SCRIPT="${WS_HUB}/.claude/skills/coordination/workspace/claude-reflect/scripts/daily-reflect.sh"
if [[ -f "$REFLECT_SCRIPT" ]]; then
    if WORKSPACE_ROOT="$WS_HUB" bash "$REFLECT_SCRIPT" > /tmp/cl_phase2.log 2>&1; then
        log_phase "2 Reflect" "DONE" "Daily reflection completed"
    else
        log_phase "2 Reflect" "FAILED" "daily-reflect.sh failed"
    fi
else
    log_phase "2 Reflect" "SKIPPED" "Not found"
fi

# --- Phase 3: Knowledge (non-mandatory) ---
echo "--- Phase 3: Knowledge ---"
KNOWLEDGE_SCRIPT="${WS_HUB}/.claude/skills/coordination/workspace/knowledge-manager/scripts/knowledge-capture.sh"
if [[ -f "$KNOWLEDGE_SCRIPT" ]]; then
    if WORKSPACE_HUB="$WS_HUB" bash "$KNOWLEDGE_SCRIPT" > /tmp/cl_phase3.log 2>&1; then
        log_phase "3 Knowledge" "DONE" "Knowledge captured"
    else
        log_phase "3 Knowledge" "FAILED" "knowledge-capture.sh failed"
    fi
else
    log_phase "3 Knowledge" "SKIPPED" "Not found"
fi

# Additional Phase 3: Memory Staleness Check
run_py_phase "3" "Memory Staleness"

# --- Phase 4: Improve (mandatory) ---
echo "--- Phase 4: Improve ---"
IMPROVE_SCRIPT="${WS_HUB}/scripts/improve/improve.sh"
if [[ -f "$IMPROVE_SCRIPT" ]]; then
    if bash "$IMPROVE_SCRIPT" > /tmp/cl_phase4.log 2>&1; then
        log_phase "4 Improve" "DONE" "Ecosystem improved"
    else
        log_phase "4 Improve" "FAILED" "improve.sh failed"
        exit 1
    fi
else
    log_phase "4 Improve" "SKIPPED" "improve.sh not found"
    exit 1
fi

# --- Phases 5-9: Analysis (via Python) ---
run_py_phase "5" "Correction Trends"
run_py_phase "6" "WRK Feedback"
run_py_phase "7" "Candidates"
run_py_phase "8" "Report Review"
run_py_phase "9" "Coverage Audit"

exit 0
