#!/usr/bin/env bash
# classify.sh — Phase 2: Route signals to improvement targets via deterministic event routing
# Replaces LLM classification (call_anthropic_api) with pure shell routing by event type.
# See WRK-1102 Fix 7: signals have structured `event` field — no LLM needed.

# --- Route helper stubs ---

route_to_memory() {
    local line="$1"
    [[ -z "${MEMORY_FILE:-}" || ! -f "${MEMORY_FILE}" ]] && return 0
    local wrk event
    wrk=$(echo "$line" | jq -r '.wrk // empty' 2>/dev/null || true)
    event=$(echo "$line" | jq -r '.event // empty' 2>/dev/null || true)
    [[ -z "$event" ]] && return 0
    printf '\n<!-- improve: %s -->\n- [%s] %s\n' \
        "$(date +%Y-%m-%d)" "$event" "${wrk:-session}" >> "$MEMORY_FILE" 2>/dev/null || true
}

route_to_skill_scores() {
    local line="$1"
    [[ -z "${SKILL_SCORES_FILE:-}" || ! -f "${SKILL_SCORES_FILE}" ]] && return 0
    local skill count
    skill=$(echo "$line" | jq -r '.skill // empty' 2>/dev/null || true)
    [[ -z "$skill" ]] && return 0
    count=$(echo "$line" | jq -r '.count // 1' 2>/dev/null || echo 1)
    # Read-modify-write: increment usage count in YAML via Python (safe structured update)
    if command -v python3 &>/dev/null; then
        python3 - <<PYEOF 2>/dev/null || true
import yaml, sys, os
path = os.environ.get('SKILL_SCORES_FILE', '')
if not path or not os.path.exists(path):
    sys.exit(0)
with open(path) as f:
    data = yaml.safe_load(f) or {}
skills = data.setdefault('skills', {})
entry = skills.setdefault('${skill}', {'usage_count': 0})
entry['usage_count'] = entry.get('usage_count', 0) + ${count}
with open(path, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
PYEOF
    fi
}

route_to_rules() {
    local line="$1"
    [[ -z "${RULES_FILE:-}" || ! -f "${RULES_FILE}" ]] && return 0
    local summary
    summary=$(echo "$line" | jq -r '.summary // .violation // empty' 2>/dev/null || true)
    [[ -z "$summary" ]] && return 0
    printf '\n<!-- improve: %s -->\n- %s\n' "$(date +%Y-%m-%d)" "$summary" >> "$RULES_FILE" 2>/dev/null || true
}

# --- Main classifier (pure shell event router) ---

phase_classify() {
    local merged="${1:-${IMPROVE_WORKDIR:-}/merged_signals.jsonl}"
    local classified="${IMPROVE_WORKDIR:-/tmp}/classified.json"

    [[ ! -f "$merged" || ! -s "$merged" ]] && { echo "[]" > "$classified"; return 0; }

    local count=0
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        local event
        event=$(echo "$line" | jq -r '.event // empty' 2>/dev/null || true)
        case "$event" in
            session_tool_summary) route_to_memory "$line" ; count=$((count + 1)) ;;
            skill_invoked)        route_to_skill_scores "$line" ; count=$((count + 1)) ;;
            drift_counts)         route_to_rules "$line" ; count=$((count + 1)) ;;
            stage_exit)           route_to_memory "$line" ; count=$((count + 1)) ;;
            context_reset)        route_to_memory "$line" ; count=$((count + 1)) ;;
            *)                    true ;;  # unknown events: drop (no LLM fallback)
        esac
    done < "$merged"

    echo "[]" > "$classified"  # no structured output needed; writes happened inline
    echo "improve/classify: ${count} signal(s) routed deterministically (no API)"
    return 0
}
