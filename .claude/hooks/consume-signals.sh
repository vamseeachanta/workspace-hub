#!/usr/bin/env bash
# consume-signals.sh — Last-mile signal consumer for session learning pipeline
# Trigger: Stop hook (runs after session-review.sh and post-task-review.sh)
# Input:   .claude/state/pending-reviews/*.jsonl (produced by session-review.sh)
# Output:  .claude/state/session-briefing.md     (overwritten each run)
#          .claude/state/pending-insights.md      (appended, human/Claude trims)
#          .claude/state/accumulator.json         (cross-session tracking)
#          .claude/state/archive/YYYYMMDD/        (processed signals)
#
# Platform: Linux, macOS, Windows (Git Bash/MINGW)
# Dependencies: bash, jq, date

set -uo pipefail

# Drain stdin (hook may pipe data)
if [[ ! -t 0 ]]; then
    cat > /dev/null 2>&1 || true
fi

# --- Workspace resolution ---
source "$(dirname "${BASH_SOURCE[0]}")/resolve-workspace.sh" 2>/dev/null || {
    # Inline fallback if resolve-workspace.sh is missing
    WORKSPACE_HUB="${WORKSPACE_HUB:-/d/workspace-hub}"
}

WS_HUB="${WORKSPACE_HUB}"
STATE_DIR="${WS_HUB}/.claude/state"
REVIEW_DIR="${STATE_DIR}/pending-reviews"
DATE_TAG=$(date +%Y%m%d)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# --- Guard: exit if no signals ---
has_data=false
for f in "${REVIEW_DIR}"/*.jsonl; do
    [[ ! -f "$f" ]] && continue
    [[ "$(basename "$f")" == "session-summaries.jsonl" ]] && continue
    if [[ -s "$f" ]]; then
        has_data=true
        break
    fi
done
if [[ "$has_data" == "false" ]]; then
    echo "consume-signals: no pending signals, skipping"
    exit 0
fi

# --- Count signals per type ---
count_lines() {
    local file="$1"
    if [[ -f "$file" && -s "$file" ]]; then
        wc -l < "$file" 2>/dev/null | tr -d ' '
    else
        echo "0"
    fi
}

INSIGHTS_COUNT=$(count_lines "${REVIEW_DIR}/insights.jsonl")
ERRORS_COUNT=$(count_lines "${REVIEW_DIR}/errors.jsonl")
SKILLS_COUNT=$(count_lines "${REVIEW_DIR}/skill-candidates.jsonl")
MEMORY_COUNT=$(count_lines "${REVIEW_DIR}/memory-updates.jsonl")
NEW_FILES_COUNT=$(count_lines "${REVIEW_DIR}/new-files.jsonl")

# --- 1. Append insights to pending-insights.md ---
PENDING_INSIGHTS="${STATE_DIR}/pending-insights.md"
if [[ "$INSIGHTS_COUNT" -gt 0 && -f "${REVIEW_DIR}/insights.jsonl" ]]; then
    # Create file with header if it doesn't exist
    if [[ ! -f "$PENDING_INSIGHTS" ]]; then
        cat > "$PENDING_INSIGHTS" <<'HEADER'
# Pending Insights
> Review and triage. Move to skills/memory, then delete entry.

HEADER
    fi

    # Get session tag from first entry
    session_tag=$(jq -r '.session // "unknown"' "${REVIEW_DIR}/insights.jsonl" 2>/dev/null | head -1)

    # Append new insights
    echo "### ${DATE_TAG} [session:${session_tag}]" >> "$PENDING_INSIGHTS"
    jq -r '.content_preview // "" | .[0:300]' "${REVIEW_DIR}/insights.jsonl" 2>/dev/null | while IFS= read -r line; do
        [[ -n "$line" ]] && echo "> ${line}" >> "$PENDING_INSIGHTS"
    done
    echo "" >> "$PENDING_INSIGHTS"
fi

# --- 2. Update accumulator.json ---
ACCUMULATOR="${STATE_DIR}/accumulator.json"
if [[ ! -f "$ACCUMULATOR" ]]; then
    # Initialize accumulator
    jq -cn \
        --arg ts "$TIMESTAMP" \
        '{
            version: 1,
            last_processed: $ts,
            session_count: 0,
            totals: { insights: 0, errors: 0, skill_candidates: 0, memory_updates: 0, new_files: 0 },
            skill_patterns: {}
        }' > "$ACCUMULATOR" 2>/dev/null
fi

# Read current accumulator
acc_session_count=$(jq -r '.session_count // 0' "$ACCUMULATOR" 2>/dev/null)
acc_insights=$(jq -r '.totals.insights // 0' "$ACCUMULATOR" 2>/dev/null)
acc_errors=$(jq -r '.totals.errors // 0' "$ACCUMULATOR" 2>/dev/null)
acc_skills=$(jq -r '.totals.skill_candidates // 0' "$ACCUMULATOR" 2>/dev/null)
acc_memory=$(jq -r '.totals.memory_updates // 0' "$ACCUMULATOR" 2>/dev/null)
acc_new_files=$(jq -r '.totals.new_files // 0' "$ACCUMULATOR" 2>/dev/null)

# Update skill patterns from this session
skill_patterns_update=""
if [[ "$SKILLS_COUNT" -gt 0 && -f "${REVIEW_DIR}/skill-candidates.jsonl" ]]; then
    # Build jq update for skill patterns
    skill_patterns_update=$(jq -sc '
        [.[] | {key: .tool_sequence, value: (.occurrences // 0)}]
        | group_by(.key)
        | map({key: .[0].key, value: (map(.value) | add)})
        | from_entries
    ' "${REVIEW_DIR}/skill-candidates.jsonl" 2>/dev/null || echo "{}")
fi

# Merge into accumulator
jq \
    --arg ts "$TIMESTAMP" \
    --argjson sc "$((acc_session_count + 1))" \
    --argjson ins "$((acc_insights + INSIGHTS_COUNT))" \
    --argjson err "$((acc_errors + ERRORS_COUNT))" \
    --argjson skl "$((acc_skills + SKILLS_COUNT))" \
    --argjson mem "$((acc_memory + MEMORY_COUNT))" \
    --argjson nf "$((acc_new_files + NEW_FILES_COUNT))" \
    --argjson dt "\"${DATE_TAG}\"" \
    --argjson new_patterns "${skill_patterns_update:-"{}"}" \
    '
    .last_processed = $ts |
    .session_count = $sc |
    .totals.insights = $ins |
    .totals.errors = $err |
    .totals.skill_candidates = $skl |
    .totals.memory_updates = $mem |
    .totals.new_files = $nf |
    # Merge skill patterns: add session date, increment total, check maturity
    .skill_patterns as $existing |
    reduce ($new_patterns | to_entries[]) as $entry (
        .;
        .skill_patterns[$entry.key] as $cur |
        if $cur then
            # Existing pattern: add session if new, increment total
            .skill_patterns[$entry.key].total = ($cur.total + $entry.value) |
            .skill_patterns[$entry.key].sessions = (
                if ($cur.sessions | index($dt)) then $cur.sessions
                else $cur.sessions + [$dt] end
            ) |
            .skill_patterns[$entry.key].mature = (
                (.skill_patterns[$entry.key].sessions | length) >= 3
            )
        else
            # New pattern
            .skill_patterns[$entry.key] = {
                sessions: [$dt],
                total: $entry.value,
                mature: false
            }
        end
    )
    ' "$ACCUMULATOR" > "${ACCUMULATOR}.tmp" 2>/dev/null && mv "${ACCUMULATOR}.tmp" "$ACCUMULATOR"

# --- 3. Generate session-briefing.md ---
BRIEFING="${STATE_DIR}/session-briefing.md"

# Count pending insights (total lines in pending-insights.md minus header)
pending_insight_count=0
if [[ -f "$PENDING_INSIGHTS" ]]; then
    pending_insight_count=$(grep -c '^>' "$PENDING_INSIGHTS" 2>/dev/null || echo "0")
fi

# Get mature skill candidates
mature_table=""
if [[ -f "$ACCUMULATOR" ]]; then
    mature_table=$(jq -r '
        .skill_patterns
        | to_entries
        | map(select(.value.mature == true))
        | sort_by(-.value.total)
        | if length > 0 then
            map("| \(.key) | \(.value.sessions | length) | \(.value.total) |")
            | join("\n")
          else empty end
    ' "$ACCUMULATOR" 2>/dev/null || true)
fi

# Get latest insight previews (up to 3)
insight_previews=""
if [[ "$INSIGHTS_COUNT" -gt 0 && -f "${REVIEW_DIR}/insights.jsonl" ]]; then
    insight_previews=$(jq -r '.content_preview // "" | .[0:120]' "${REVIEW_DIR}/insights.jsonl" 2>/dev/null | tail -3 | while IFS= read -r line; do
        [[ -n "$line" ]] && echo "- \"${line}...\""
    done)
fi

# Read all-time totals from accumulator
all_insights=$(jq -r '.totals.insights // 0' "$ACCUMULATOR" 2>/dev/null)
all_errors=$(jq -r '.totals.errors // 0' "$ACCUMULATOR" 2>/dev/null)
all_skills=$(jq -r '.totals.skill_candidates // 0' "$ACCUMULATOR" 2>/dev/null)
all_memory=$(jq -r '.totals.memory_updates // 0' "$ACCUMULATOR" 2>/dev/null)
all_sessions=$(jq -r '.session_count // 0' "$ACCUMULATOR" 2>/dev/null)

cat > "$BRIEFING" <<EOF
# Session Briefing
> Auto-generated by consume-signals.sh | Updated: ${DATE_TAG} | Sessions tracked: ${all_sessions}

## Pending Insights (${pending_insight_count} unreviewed)
See \`.claude/state/pending-insights.md\` for full list.
${insight_previews:-"_No new insights this session._"}

EOF

if [[ -n "$mature_table" ]]; then
    cat >> "$BRIEFING" <<EOF
## Mature Skill Candidates
| Pattern | Sessions | Total |
|---------|----------|-------|
${mature_table}

EOF
fi

cat >> "$BRIEFING" <<EOF
## Stats
| Metric | This Session | All Time |
|--------|-------------|----------|
| Insights | ${INSIGHTS_COUNT} | ${all_insights} |
| Errors | ${ERRORS_COUNT} | ${all_errors} |
| Skill candidates | ${SKILLS_COUNT} | ${all_skills} |
| Memory updates | ${MEMORY_COUNT} | ${all_memory} |
EOF

# --- 4. Generate draft work item if significant work was done ---
WORK_QUEUE="${WS_HUB}/.claude/work-queue"
STATE_YAML="${WORK_QUEUE}/state.yaml"
WRK_CREATED=""

# Significant = at least 1 new file created in this session
if [[ "$NEW_FILES_COUNT" -gt 0 && -f "${REVIEW_DIR}/new-files.jsonl" && -f "$STATE_YAML" ]]; then
    # Read and increment last_id
    last_id=$(grep '^last_id:' "$STATE_YAML" 2>/dev/null | awk '{print $2}')
    if [[ -n "$last_id" && "$last_id" =~ ^[0-9]+$ ]]; then
        next_id=$((last_id + 1))
        WRK_ID="WRK-$(printf '%03d' $next_id)"

        # Detect project from new file paths (handles both Unix and Windows paths)
        project=$(jq -r '.file_path // ""' "${REVIEW_DIR}/new-files.jsonl" 2>/dev/null \
            | head -1 \
            | sed 's|\\|/|g; s|.*workspace-hub/||; s|.*workspace.hub/||i; s|/.*||' \
            | tr -d '\r')
        [[ -z "$project" || "$project" == *":"* ]] && project=$(basename "$(pwd)")

        # Collect file list (normalize paths for display)
        file_list=$(jq -r '.file_path // ""' "${REVIEW_DIR}/new-files.jsonl" 2>/dev/null \
            | sed 's|\\|/|g; s|.*workspace-hub/||; s|.*workspace.hub/||i' \
            | while IFS= read -r fp; do
                [[ -n "$fp" ]] && echo "  - \`${fp}\`"
            done)

        # Get session tag
        session_tag=$(jq -r '.session // "unknown"' "${REVIEW_DIR}/new-files.jsonl" 2>/dev/null | head -1)

        # Determine module from file paths
        module=$(jq -r '.file_path // ""' "${REVIEW_DIR}/new-files.jsonl" 2>/dev/null \
            | head -1 \
            | sed 's|\\|/|g' \
            | grep -oiE '(orcaflex|diffraction|mooring|fatigue|structural|hydrodynamic|hooks)' \
            | head -1)
        [[ -z "$module" ]] && module="general"

        mkdir -p "${WORK_QUEUE}/pending" 2>/dev/null

        cat > "${WORK_QUEUE}/pending/${WRK_ID}.md" <<WRKEOF
---
id: ${WRK_ID}
title: "Session ${session_tag} — ${NEW_FILES_COUNT} file(s) created"
status: pending
priority: medium
complexity: low
compound: false
created_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
source: auto-captured
session: ${session_tag}
target_repos:
  - ${project}
module: ${module}
tags: [auto-captured, session-work]
spec_ref:
related: []
blocked_by: []
synced_to: []
---

# Session Work — ${session_tag}

## What
Auto-captured work item from session signals. Review and update title/description.

## Files Created
${file_list}

## Session Stats
- Insights: ${INSIGHTS_COUNT}
- Errors: ${ERRORS_COUNT}
- Skill candidates: ${SKILLS_COUNT}
- Memory updates: ${MEMORY_COUNT}

## Action Required
- [ ] Review and update title to reflect actual work done
- [ ] Set appropriate priority and complexity
- [ ] Link to spec if applicable
- [ ] Move to \`working/\` if in progress, or \`archived/\` if complete
WRKEOF

        # Update state.yaml
        sed -i "s/^last_id:.*/last_id: ${next_id}/" "$STATE_YAML" 2>/dev/null
        # Increment total_captured
        total=$(grep 'total_captured:' "$STATE_YAML" 2>/dev/null | awk '{print $2}')
        if [[ -n "$total" && "$total" =~ ^[0-9]+$ ]]; then
            sed -i "s/total_captured:.*/total_captured: $((total + 1))/" "$STATE_YAML" 2>/dev/null
        fi
        WRK_CREATED="$WRK_ID"
    fi
fi

# Add work item to briefing if created
if [[ -n "$WRK_CREATED" ]]; then
    cat >> "$BRIEFING" <<EOF

## Draft Work Item
\`${WRK_CREATED}\` created in \`.claude/work-queue/pending/\` — review and update title.
EOF
fi

# --- 5. Archive processed signals ---
ARCHIVE_DIR="${STATE_DIR}/archive/${DATE_TAG}"
mkdir -p "$ARCHIVE_DIR" 2>/dev/null

# Move non-empty JSONL files to archive (append if archive already exists for today)
for f in "${REVIEW_DIR}"/*.jsonl; do
    [[ ! -f "$f" ]] && continue
    fname=$(basename "$f")
    if [[ -s "$f" ]]; then
        cat "$f" >> "${ARCHIVE_DIR}/${fname}" 2>/dev/null
    fi
done

# --- 5. Clear pending-reviews for next session ---
for f in "${REVIEW_DIR}"/*.jsonl; do
    [[ ! -f "$f" ]] && continue
    : > "$f"  # Truncate to empty
done

echo "consume-signals: processed — insights:${INSIGHTS_COUNT} errors:${ERRORS_COUNT} skills:${SKILLS_COUNT} memory:${MEMORY_COUNT} → archived to ${DATE_TAG}/"
exit 0
