---
name: state-directory-manager-4-state-file-operations
description: 'Sub-skill of state-directory-manager: 4. State File Operations.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 4. State File Operations

## 4. State File Operations


Track persistent state between runs:

```bash
#!/bin/bash
# ABOUTME: State file operations
# ABOUTME: Track last run, progress, etc.

STATE_FILE="$STATE_DIR/state.json"

# Initialize state
init_state() {
    if [[ ! -f "$STATE_FILE" ]]; then
        cat > "$STATE_FILE" << EOF
{
    "version": "1.0.0",
    "created": "$(date -Iseconds)",
    "last_run": null,
    "run_count": 0,
    "last_status": null
}
EOF
    fi
}

# Get state value (requires jq)
get_state() {
    local key="$1"
    local default="${2:-null}"

    if [[ -f "$STATE_FILE" ]] && command -v jq &>/dev/null; then
        jq -r ".$key // $default" "$STATE_FILE"
    else
        echo "$default"
    fi
}

# Update state value (requires jq)
set_state() {
    local key="$1"
    local value="$2"

    init_state

    if command -v jq &>/dev/null; then
        local temp=$(mktemp)
        jq ".$key = $value" "$STATE_FILE" > "$temp" && mv "$temp" "$STATE_FILE"
    fi
}

# Record run
record_run() {
    local status="$1"

    set_state "last_run" "\"$(date -Iseconds)\""
    set_state "last_status" "\"$status\""
    set_state "run_count" "$(($(get_state run_count 0) + 1))"
}

# Simple key-value state (no jq required)
STATE_KV_FILE="$STATE_DIR/state.kv"

get_state_kv() {
    local key="$1"
    local default="$2"

    if [[ -f "$STATE_KV_FILE" ]]; then
        grep "^${key}=" "$STATE_KV_FILE" 2>/dev/null | cut -d'=' -f2- || echo "$default"
    else
        echo "$default"
    fi
}

set_state_kv() {
    local key="$1"
    local value="$2"

    mkdir -p "$(dirname "$STATE_KV_FILE")"

    if [[ -f "$STATE_KV_FILE" ]] && grep -q "^${key}=" "$STATE_KV_FILE"; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$STATE_KV_FILE"
    else
        echo "${key}=${value}" >> "$STATE_KV_FILE"
    fi
}
```
