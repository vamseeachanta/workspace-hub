#!/usr/bin/env bash
# knowledge-stats.sh - Knowledge base health dashboard
# Usage: knowledge-stats.sh [--json]

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
KNOWLEDGE_DIR="${WORKSPACE_ROOT}/.claude/knowledge"
INDEX_FILE="${KNOWLEDGE_DIR}/index.json"
ENTRIES_DIR="${KNOWLEDGE_DIR}/entries"
ARCHIVE_DIR="${KNOWLEDGE_DIR}/archive"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JSON_MODE=false
[[ "${1:-}" == "--json" ]] && JSON_MODE=true

# Rebuild index if stale or missing
if [[ ! -f "$INDEX_FILE" ]]; then
    if [[ -x "${SCRIPT_DIR}/knowledge-index.sh" ]]; then
        "${SCRIPT_DIR}/knowledge-index.sh" "$WORKSPACE_ROOT" > /dev/null 2>&1 || true
    fi
fi

if [[ ! -f "$INDEX_FILE" ]]; then
    echo "ERROR: No index.json found and could not rebuild." >&2
    exit 1
fi

# Extract stats from index
TOTAL=$(jq -r '.metadata.entry_count // 0' "$INDEX_FILE")
ACTIVE=$(jq -r '.metadata.active_count // 0' "$INDEX_FILE")
AVG_CONF=$(jq -r '.metadata.avg_confidence // 0' "$INDEX_FILE")
GENERATED=$(jq -r '.metadata.generated_at // "unknown"' "$INDEX_FILE")

# Type counts
DECISIONS=$(jq -r '.metadata.type_counts.decision // 0' "$INDEX_FILE")
PATTERNS=$(jq -r '.metadata.type_counts.pattern // 0' "$INDEX_FILE")
GOTCHAS=$(jq -r '.metadata.type_counts.gotcha // 0' "$INDEX_FILE")
CORRECTIONS=$(jq -r '.metadata.type_counts.correction // 0' "$INDEX_FILE")
TIPS=$(jq -r '.metadata.type_counts.tip // 0' "$INDEX_FILE")

# Category counts
CATEGORIES=$(jq -r '.metadata.category_counts | to_entries | sort_by(-.value) | .[] | "\(.key): \(.value)"' "$INDEX_FILE")

# Stale entries (confidence < 0.5)
STALE=$(jq '[.entries[] | select(.status == "active" and .confidence < 0.5)] | length' "$INDEX_FILE")

# Low confidence (< 0.3 - archive candidates)
ARCHIVE_CANDIDATES=$(jq '[.entries[] | select(.status == "active" and .confidence < 0.3)] | length' "$INDEX_FILE")

# Never accessed
NEVER_ACCESSED=$(jq '[.entries[] | select(.access_count == 0)] | length' "$INDEX_FILE")

# Most accessed
TOP_ACCESSED=$(jq -r '[.entries[] | select(.access_count > 0)] | sort_by(-.access_count) | .[:5] | .[] | "  \(.id) (\(.access_count)x) \(.title)"' "$INDEX_FILE" 2>/dev/null)

# Archived entries count
ARCHIVED=$(find "$ARCHIVE_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d '[:space:]')
ARCHIVED=${ARCHIVED:-0}

# Source type breakdown
MANUAL=$(jq '[.entries[] | select(.source_type == "manual")] | length' "$INDEX_FILE")
REFLECT=$(jq '[.entries[] | select(.source_type == "reflect")] | length' "$INDEX_FILE")
CORRECTION_SYN=$(jq '[.entries[] | select(.source_type == "correction-synthesis")] | length' "$INDEX_FILE")

if [[ "$JSON_MODE" == true ]]; then
    jq -n \
        --argjson total "$TOTAL" \
        --argjson active "$ACTIVE" \
        --argjson archived "$ARCHIVED" \
        --arg avg_confidence "$AVG_CONF" \
        --argjson stale "$STALE" \
        --argjson archive_candidates "$ARCHIVE_CANDIDATES" \
        --argjson never_accessed "$NEVER_ACCESSED" \
        --argjson decisions "$DECISIONS" \
        --argjson patterns "$PATTERNS" \
        --argjson gotchas "$GOTCHAS" \
        --argjson corrections "$CORRECTIONS" \
        --argjson tips "$TIPS" \
        --argjson manual "$MANUAL" \
        --argjson reflect "$REFLECT" \
        --argjson correction_synthesis "$CORRECTION_SYN" \
        --arg generated_at "$GENERATED" \
        '{
            total: $total,
            active: $active,
            archived: $archived,
            avg_confidence: ($avg_confidence | tonumber),
            stale: $stale,
            archive_candidates: $archive_candidates,
            never_accessed: $never_accessed,
            by_type: { decisions: $decisions, patterns: $patterns, gotchas: $gotchas, corrections: $corrections, tips: $tips },
            by_source: { manual: $manual, reflect: $reflect, correction_synthesis: $correction_synthesis },
            generated_at: $generated_at
        }'
    exit 0
fi

# Display dashboard
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                 Knowledge Base Dashboard                     ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  OVERVIEW                                                    ║"
echo "║  Total Entries: $TOTAL  Active: $ACTIVE  Archived: $ARCHIVED"
echo "║  Avg Confidence: $AVG_CONF"
echo "║  Index Generated: $GENERATED"
echo "║  ───────────────────────────────────────────────────────────  ║"
echo "║  BY TYPE                                                     ║"
echo "║  Decisions (ADR): $DECISIONS  Patterns (PAT): $PATTERNS"
echo "║  Gotchas (GOT):   $GOTCHAS  Corrections (COR): $CORRECTIONS"
echo "║  Tips (TIP):      $TIPS"
echo "║  ───────────────────────────────────────────────────────────  ║"
echo "║  BY CATEGORY                                                 ║"
echo "$CATEGORIES" | while IFS= read -r line; do
    echo "║  $line"
done
echo "║  ───────────────────────────────────────────────────────────  ║"
echo "║  BY SOURCE                                                   ║"
echo "║  Manual: $MANUAL  Reflect: $REFLECT  Correction: $CORRECTION_SYN"
echo "║  ───────────────────────────────────────────────────────────  ║"
echo "║  HEALTH                                                      ║"
echo "║  Stale (conf < 0.5):     $STALE"
echo "║  Archive candidates:     $ARCHIVE_CANDIDATES"
echo "║  Never accessed:         $NEVER_ACCESSED"
if [[ -n "$TOP_ACCESSED" ]]; then
    echo "║  ───────────────────────────────────────────────────────────  ║"
    echo "║  MOST ACCESSED                                               ║"
    echo "$TOP_ACCESSED" | while IFS= read -r line; do
        echo "║  $line"
    done
fi
echo "╚═══════════════════════════════════════════════════════════════╝"
