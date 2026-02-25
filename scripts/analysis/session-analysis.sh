#!/usr/bin/env bash
# session-analysis.sh — morning session analysis cron (3AM)
# Reads signal files from previous day, produces structured analysis
# Outputs: skill scores, candidate files, gap reports, session summary
#
# Idempotent: running twice on the same day does not create duplicate entries.
# Cross-machine: git pull first to pick up signals from other machines.
#
# Usage: bash scripts/analysis/session-analysis.sh [--date YYYY-MM-DD]
# Dependencies: bash, jq (optional), git, awk, date

set -uo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"

SIGNALS_DIR="${WS_HUB}/.claude/state/session-signals"
PENDING_REVIEWS_DIR="${WS_HUB}/.claude/state/pending-reviews"
SKILL_SCORES_FILE="${WS_HUB}/.claude/state/skill-scores.yaml"
CANDIDATES_DIR="${WS_HUB}/.claude/state/candidates"
ANALYSIS_DIR="${WS_HUB}/.claude/state/session-analysis"
WORK_QUEUE_PENDING="${WS_HUB}/.claude/work-queue/pending"

# Determine analysis date (default: yesterday)
if [[ "${1:-}" == "--date" && -n "${2:-}" ]]; then
    ANALYSIS_DATE="$2"
else
    ANALYSIS_DATE=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null \
        || date -v-1d +%Y-%m-%d 2>/dev/null \
        || date +%Y-%m-%d)
fi

TODAY=$(date +%Y-%m-%d)
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SUMMARY_FILE="${ANALYSIS_DIR}/${ANALYSIS_DATE}.md"

log() { echo "[session-analysis] $*"; }
warn() { echo "[session-analysis] WARN: $*" >&2; }

# Idempotency guard: exit silently if summary already written today
if [[ -f "$SUMMARY_FILE" ]] && [[ "${FORCE_RERUN:-}" != "true" ]]; then
    log "Summary for ${ANALYSIS_DATE} already exists at ${SUMMARY_FILE} — skipping (set FORCE_RERUN=true to override)"
    exit 0
fi

# --- Ensure directories exist ---
mkdir -p "$ANALYSIS_DIR" "$CANDIDATES_DIR"

# --- Step 1: Cross-machine aggregation via git pull ---
log "Step 1: cross-machine aggregation"
if command -v git &>/dev/null && git -C "$WS_HUB" rev-parse --git-dir &>/dev/null 2>&1; then
    if git -C "$WS_HUB" pull --quiet --rebase 2>/dev/null; then
        log "  git pull: OK"
    else
        warn "git pull failed — proceeding with local signals only"
    fi
else
    warn "git not available — skipping cross-machine aggregation"
fi

# --- Step 2: Collect signal files from analysis date ---
log "Step 2: collecting signal files for ${ANALYSIS_DATE}"

SIGNAL_FILES=()
if [[ -d "$SIGNALS_DIR" ]]; then
    while IFS= read -r -d '' f; do
        SIGNAL_FILES+=("$f")
    done < <(find "$SIGNALS_DIR" -name "${ANALYSIS_DATE}-*.jsonl" -print0 2>/dev/null || true)
fi

N_SESSIONS="${#SIGNAL_FILES[@]}"
log "  Found ${N_SESSIONS} signal file(s)"

# Also scan pending-reviews for same-date signals (from session-review.sh)
PENDING_SIGNAL_FILES=()
if [[ -d "$PENDING_REVIEWS_DIR" ]]; then
    while IFS= read -r -d '' f; do
        PENDING_SIGNAL_FILES+=("$f")
    done < <(find "$PENDING_REVIEWS_DIR" -name "*.jsonl" -newer "${PENDING_REVIEWS_DIR}" -print0 2>/dev/null \
        | head -c 0 || true)
    # Fallback: all files modified within past 2 days
    while IFS= read -r -d '' f; do
        PENDING_SIGNAL_FILES+=("$f")
    done < <(find "$PENDING_REVIEWS_DIR" -name "*.jsonl" -mtime -2 -print0 2>/dev/null || true)
fi

# --- Step 3: Score skills ---
log "Step 3: scoring skills from signal files"

declare -A skill_usage=()

for sig_file in "${SIGNAL_FILES[@]}"; do
    [[ -f "$sig_file" ]] || continue
    # Extract skill_invocations array from each JSONL line
    if command -v jq &>/dev/null; then
        while IFS= read -r skill; do
            [[ -n "$skill" ]] || continue
            skill_usage["$skill"]=$(( ${skill_usage["$skill"]:-0} + 1 ))
        done < <(jq -r '
            select(.event == "session_end")
            | .signals.skill_invocations[]?
        ' "$sig_file" 2>/dev/null || true)
    fi
done

N_SKILLS_SCORED="${#skill_usage[@]}"
log "  Skills scored: ${N_SKILLS_SCORED}"

# Update skill-scores.yaml (append/update usage counts, preserve existing)
if [[ "${N_SKILLS_SCORED}" -gt 0 ]]; then
    # Read existing skills block if present, then write updated file
    {
        printf '# Skill performance scorecard — updated by session-analysis.sh (3AM cron)\n'
        printf '# Fields: usage_rate, one_shot_rate, mean_corrections, last_used, sessions_tracked\n'
        printf 'version: 1.0.0\n'
        printf 'updated: %s\n' "$TODAY"
        printf 'skills:\n'
        # Preserve existing entries that are not being updated
        if [[ -f "$SKILL_SCORES_FILE" ]]; then
            # Extract existing skill names to avoid duplicates
            existing_skills=$(grep -E '^  [a-zA-Z0-9_-]+:' "$SKILL_SCORES_FILE" 2>/dev/null \
                | awk '{gsub(/:$/,"",$1); print $1}' || true)
        fi
        # Write updated skill entries
        for skill in "${!skill_usage[@]}"; do
            count="${skill_usage[$skill]}"
            printf '  %s:\n' "$skill"
            printf '    usage_rate: %.2f\n' "$(echo "scale=2; $count / $N_SESSIONS" | bc 2>/dev/null || echo 0)"
            printf '    one_shot_rate: null\n'
            printf '    mean_corrections: null\n'
            printf '    last_used: "%s"\n' "$ANALYSIS_DATE"
            printf '    sessions_tracked: %d\n' "$count"
        done
    } > "${SKILL_SCORES_FILE}.tmp" && mv "${SKILL_SCORES_FILE}.tmp" "$SKILL_SCORES_FILE"
    log "  Updated ${SKILL_SCORES_FILE}"
fi

# --- Step 4: Detect anti-patterns ---
log "Step 4: detecting anti-patterns"

declare -a anti_patterns=()

# Scan pending-reviews for bash-file-ops anti-pattern
# (bash used for grep/cat/find instead of dedicated tools)
bash_file_ops_count=0
if [[ -d "$PENDING_REVIEWS_DIR" ]]; then
    bash_file_ops_count=$(grep -rl 'grep\|cat\|find\|sed' "$PENDING_REVIEWS_DIR"/*.jsonl 2>/dev/null \
        | wc -l | tr -d ' ' || echo 0)
fi
if [[ "${bash_file_ops_count:-0}" -gt 2 ]]; then
    anti_patterns+=("bash-file-ops: bash used for file ops instead of dedicated tools (${bash_file_ops_count} occurrences)")
fi

# Detect inline complex work (long tool sequences without delegation)
if command -v jq &>/dev/null && [[ -d "$PENDING_REVIEWS_DIR" ]]; then
    skill_candidates_count=$(wc -l < "${PENDING_REVIEWS_DIR}/skill-candidates.jsonl" 2>/dev/null || echo 0)
    if [[ "${skill_candidates_count:-0}" -gt 5 ]]; then
        anti_patterns+=("inline-complex-work: ${skill_candidates_count} tool sequences could be delegated")
    fi
fi

N_ANTI_PATTERNS="${#anti_patterns[@]}"
log "  Anti-patterns detected: ${N_ANTI_PATTERNS}"

# --- Step 5: Route candidates ---
log "Step 5: routing candidates"

declare -A candidate_counts=(
    [script]=0 [skill]=0 [hook]=0 [agent]=0 [mcp]=0
)

# Script candidates: repeated bash sequences (2+ times) from pending-reviews
if [[ -f "${PENDING_REVIEWS_DIR}/skill-candidates.jsonl" ]]; then
    n_script=$(wc -l < "${PENDING_REVIEWS_DIR}/skill-candidates.jsonl" 2>/dev/null || echo 0)
    candidate_counts[script]="${n_script}"

    if [[ "${n_script}" -gt 0 ]]; then
        {
            printf '# Script Candidates\n'
            printf '*Updated by session-analysis.sh — do not edit manually*\n'
            printf '*Last run: %s*\n\n' "$NOW"
            printf '## Candidates\n\n'
            if command -v jq &>/dev/null; then
                # skill-candidates.jsonl schema: {signal, score, type, source, ...}
                # Only emit lines that have a non-null, non-empty signal field.
                jq -r 'select(.signal != null and .signal != "")
                    | "- **" + (.signal // "") + "** — score: " + ((.score // 0) | tostring)
                      + " (source: " + (.source // "unknown") + ")"' \
                    "${PENDING_REVIEWS_DIR}/skill-candidates.jsonl" 2>/dev/null || true
            else
                grep '"signal"' "${PENDING_REVIEWS_DIR}/skill-candidates.jsonl" 2>/dev/null \
                    | grep -o '"signal":"[^"]*"' | sed 's/"signal":"//; s/"//' || true
            fi
        } >> "${CANDIDATES_DIR}/script-candidates.md"
    fi
fi

# Skill candidates: patterns from insights + errors that recur across sessions
if [[ -f "${PENDING_REVIEWS_DIR}/insights.jsonl" ]]; then
    n_skill=$(wc -l < "${PENDING_REVIEWS_DIR}/insights.jsonl" 2>/dev/null || echo 0)
    candidate_counts[skill]="${n_skill}"

    if [[ "${n_skill}" -gt 0 ]]; then
        {
            printf '\n## Candidates (from %s)\n\n' "$ANALYSIS_DATE"
            if command -v jq &>/dev/null; then
                jq -r '"- " + .content_preview' \
                    "${PENDING_REVIEWS_DIR}/insights.jsonl" 2>/dev/null | head -20 || true
            fi
        } >> "${CANDIDATES_DIR}/skill-candidates.md"
    fi
fi

# Hook candidates: recurring triggers (new_file events for hooks/scripts)
if [[ -f "${PENDING_REVIEWS_DIR}/new-files.jsonl" ]]; then
    n_hook=$(grep -c '"signal":"new_file"' "${PENDING_REVIEWS_DIR}/new-files.jsonl" 2>/dev/null || echo 0)
    candidate_counts[hook]="${n_hook}"

    if [[ "${n_hook}" -gt 0 ]]; then
        {
            printf '\n## Candidates (from %s)\n\n' "$ANALYSIS_DATE"
            if command -v jq &>/dev/null; then
                jq -r 'select(.signal == "new_file") | "- `" + .file_path + "`"' \
                    "${PENDING_REVIEWS_DIR}/new-files.jsonl" 2>/dev/null | head -20 || true
            fi
        } >> "${CANDIDATES_DIR}/hook-candidates.md"
    fi
fi

# Agent candidates: skill candidates with high occurrence counts (>= 5)
if [[ -f "${PENDING_REVIEWS_DIR}/skill-candidates.jsonl" ]] && command -v jq &>/dev/null; then
    n_agent=$(jq 'select(.occurrences >= 5) | .tool_sequence' \
        "${PENDING_REVIEWS_DIR}/skill-candidates.jsonl" 2>/dev/null | wc -l | tr -d ' ' || echo 0)
    candidate_counts[agent]="${n_agent}"
fi

# MCP candidates: memory update candidates referencing external tools
if [[ -f "${PENDING_REVIEWS_DIR}/memory-updates.jsonl" ]]; then
    n_mcp=$(grep -ci 'api\|endpoint\|external\|mcp\|tool' \
        "${PENDING_REVIEWS_DIR}/memory-updates.jsonl" 2>/dev/null || echo 0)
    candidate_counts[mcp]="${n_mcp}"
fi

log "  Candidates: script=${candidate_counts[script]} skill=${candidate_counts[skill]} hook=${candidate_counts[hook]} agent=${candidate_counts[agent]} mcp=${candidate_counts[mcp]}"

# --- Step 6: Detect deep gaps (topics hit 3+ times with no resolution) ---
log "Step 6: detecting deep knowledge gaps"

declare -a deep_gaps=()

if [[ -f "${PENDING_REVIEWS_DIR}/errors.jsonl" ]] && command -v jq &>/dev/null; then
    # Find error patterns that appear 3+ times
    while IFS= read -r gap; do
        [[ -n "$gap" ]] && deep_gaps+=("$gap")
    done < <(jq -r '.error_preview' "${PENDING_REVIEWS_DIR}/errors.jsonl" 2>/dev/null \
        | sort | uniq -c | sort -rn \
        | awk '$1 >= 3 {print $2}' \
        | head -5 || true)
fi

N_GAPS="${#deep_gaps[@]}"
log "  Deep gaps: ${N_GAPS}"

# --- Step 7: Write session summary ---
log "Step 7: writing session summary to ${SUMMARY_FILE}"

{
    printf '# Session Analysis — %s\n\n' "$ANALYSIS_DATE"
    printf '_Generated: %s_\n\n' "$NOW"
    printf '## Summary\n\n'
    printf 'Sessions analysed: %d\n' "$N_SESSIONS"
    printf 'Skills scored: %d\n' "$N_SKILLS_SCORED"
    printf 'Candidates identified: %d script, %d skill, %d hook, %d agent, %d mcp\n' \
        "${candidate_counts[script]}" "${candidate_counts[skill]}" \
        "${candidate_counts[hook]}" "${candidate_counts[agent]}" \
        "${candidate_counts[mcp]}"
    printf 'Anti-patterns detected: %d\n' "$N_ANTI_PATTERNS"
    printf 'Deep gaps: %d\n\n' "$N_GAPS"

    if [[ "${N_ANTI_PATTERNS}" -gt 0 ]]; then
        printf '## Anti-patterns\n\n'
        for ap in "${anti_patterns[@]}"; do
            printf '- %s\n' "$ap"
        done
        printf '\n'
    fi

    if [[ "${N_GAPS}" -gt 0 ]]; then
        printf '## Deep Gaps\n\n'
        for gap in "${deep_gaps[@]}"; do
            printf '- %s\n' "$gap"
        done
        printf '\n'
    fi

    printf '## Skills Scored\n\n'
    if [[ "${N_SKILLS_SCORED}" -gt 0 ]]; then
        for skill in "${!skill_usage[@]}"; do
            printf '- %s: %d session(s)\n' "$skill" "${skill_usage[$skill]}"
        done
    else
        printf '_No skill invocations recorded in signal files._\n'
    fi
    printf '\n'

    printf '## Signal Files\n\n'
    if [[ "${N_SESSIONS}" -gt 0 ]]; then
        for f in "${SIGNAL_FILES[@]}"; do
            printf '- %s\n' "$(basename "$f")"
        done
    else
        printf '_No signal files found for %s._\n' "$ANALYSIS_DATE"
    fi
    printf '\n'

    printf '## Quality Metric\n\n'
    total_candidates=$(( ${candidate_counts[script]} + ${candidate_counts[skill]} + \
        ${candidate_counts[hook]} + ${candidate_counts[agent]} + ${candidate_counts[mcp]} + N_GAPS ))
    if [[ "${N_SESSIONS}" -gt 0 && "${total_candidates}" -gt 0 ]]; then
        printf 'At least one actionable output produced: YES (%d total)\n' "$total_candidates"
    elif [[ "${N_SESSIONS}" -gt 0 ]]; then
        printf 'At least one actionable output produced: NO (0 candidates, 0 gaps)\n'
    else
        printf 'No sessions to analyse.\n'
    fi
} > "$SUMMARY_FILE"

log "  Written: ${SUMMARY_FILE}"

# --- Step 8: Create WRK items for deep gaps ---
if [[ "${N_GAPS}" -gt 0 ]]; then
    log "Step 8: creating WRK items for ${N_GAPS} deep gap(s)"

    # Find next available WRK ID
    last_wrk=$(ls "${WORK_QUEUE_PENDING}"/WRK-*.md "${WS_HUB}/.claude/work-queue/working"/WRK-*.md \
        "${WS_HUB}/.claude/work-queue/archive"/***/WRK-*.md 2>/dev/null \
        | grep -oE 'WRK-[0-9]+' | sort -t- -k2 -n | tail -1 \
        | grep -oE '[0-9]+' || echo 200)
    next_wrk=$(( last_wrk + 1 ))

    for gap in "${deep_gaps[@]}"; do
        wrk_id="WRK-${next_wrk}"
        wrk_file="${WORK_QUEUE_PENDING}/${wrk_id}.md"

        # Skip if WRK file already exists (idempotency)
        [[ -f "$wrk_file" ]] && { next_wrk=$(( next_wrk + 1 )); continue; }

        {
            printf '# %s — Knowledge Gap: %s\n\n' "$wrk_id" "${gap:0:60}"
            printf '_Auto-created by session-analysis.sh on %s_\n\n' "$TODAY"
            printf '## Background\n\n'
            printf 'Session analysis detected this error pattern appearing 3+ times with no resolution:\n\n'
            printf '```\n%s\n```\n\n' "$gap"
            printf '## Route\n\nA\n\n'
            printf '## Done When\n\n'
            printf '- [ ] Root cause identified\n'
            printf '- [ ] Fix or workaround documented\n'
            printf '- [ ] Pattern added to relevant skill or rule file\n\n'
            printf '## Status\n\npending\n'
        } > "$wrk_file"

        log "  Created ${wrk_id} for gap: ${gap:0:60}"
        next_wrk=$(( next_wrk + 1 ))
    done
else
    log "Step 8: no deep gaps — no WRK items created"
fi

log "Done. Summary: ${SUMMARY_FILE}"
exit 0
