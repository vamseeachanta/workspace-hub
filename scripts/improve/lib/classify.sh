#!/usr/bin/env bash
# classify.sh — Phase 2: Route signals to improvement targets via Anthropic API
# 10% shell, 90% API

# --- Anthropic API helper ---
call_anthropic_api() {
    local prompt="$1"
    local max_tokens="${2:-2000}"

    # Get model from registry
    local model
    model=$(yq -r '.latest_models.claude_balanced // empty' \
        "${WORKSPACE_HUB}/config/agents/model-registry.yaml" 2>/dev/null)
    model="${model:-claude-sonnet-4-5-20250929}"

    # Get OAuth token
    local token
    token=$(jq -r '.claudeAiOauth.accessToken // empty' \
        ~/.claude/.credentials.json 2>/dev/null)

    # Build auth header
    local auth_header auth_value
    if [[ -n "$token" ]]; then
        auth_header="Authorization"
        auth_value="Bearer $token"
    elif [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        auth_header="x-api-key"
        auth_value="$ANTHROPIC_API_KEY"
    else
        echo "improve/classify: no API credentials, skipping" >&2
        return 1
    fi

    local response
    response=$(curl -s --max-time 30 "https://api.anthropic.com/v1/messages" \
        -H "Content-Type: application/json" \
        -H "${auth_header}: ${auth_value}" \
        -H "anthropic-version: 2023-06-01" \
        -d "$(jq -n \
            --arg model "$model" \
            --arg prompt "$prompt" \
            --argjson max_tokens "$max_tokens" \
            '{model: $model, max_tokens: $max_tokens,
              messages: [{role: "user", content: $prompt}]}')" 2>/dev/null)

    # Extract text content
    echo "$response" | jq -r '.content[0].text // empty' 2>/dev/null
}

phase_classify() {
    local merged="${IMPROVE_WORKDIR}/merged_signals.jsonl"
    local classified="${IMPROVE_WORKDIR}/classified.json"

    [[ ! -f "$merged" || ! -s "$merged" ]] && return 1

    # Build prompt with signal summary
    local signal_summary
    signal_summary=$(head -50 "$merged" | jq -sc '.')

    local prompt
    prompt=$(cat <<'PROMPT_TEMPLATE'
You are an ecosystem improvement classifier. Given these session signals (JSONL entries), classify each into an improvement action.

SIGNALS:
SIGNAL_DATA

For each actionable signal, output a JSON array of objects with these fields:
- "target": one of "memory", "rules", "skills", "docs", "claude_md"
- "target_file": specific file path relative to .claude/ (e.g., "memory/MEMORY.md", "rules/patterns.md")
- "action": one of "append", "create", "enhance"
- "content": the actual content to add/write (1-3 sentences, actionable)
- "reason": why this improvement is needed (1 sentence)
- "score": confidence 0.0-1.0

Rules:
- Only output improvements with score >= 0.6
- Prefer appending to existing files over creating new ones
- Memory entries should be concise (1-2 lines)
- Rules should be specific and actionable
- Skip vague or already-known patterns
- Output ONLY the JSON array, no markdown wrapping

If no actionable improvements, output: []
PROMPT_TEMPLATE
    )

    # Replace placeholder with actual data
    prompt="${prompt/SIGNAL_DATA/$signal_summary}"

    echo "improve/classify: calling Anthropic API..."
    local result
    result=$(call_anthropic_api "$prompt" 3000)

    if [[ -z "$result" ]]; then
        echo "improve/classify: API returned empty, skipping" >&2
        echo "[]" > "$classified"
        return 1
    fi

    # Validate JSON array
    if echo "$result" | jq 'type == "array"' 2>/dev/null | grep -q true; then
        echo "$result" | jq '.' > "$classified"
        local count
        count=$(jq 'length' "$classified")
        echo "improve/classify: ${count} improvements classified"
    else
        echo "improve/classify: invalid API response, skipping" >&2
        echo "[]" > "$classified"
        return 1
    fi

    return 0
}
