#!/usr/bin/env bash
set -euo pipefail

AGENTS_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "$AGENTS_LIB_DIR/../../.." && pwd)"
SESSION_STATE_FILE="${SESSION_STATE_FILE:-$WS_HUB/.claude/work-queue/session-state.yaml}"

session_now_iso() {
    date -u +%Y-%m-%dT%H:%M:%SZ
}

ensure_session_store() {
    mkdir -p "$(dirname "$SESSION_STATE_FILE")"
    if [[ ! -f "$SESSION_STATE_FILE" ]]; then
        cat > "$SESSION_STATE_FILE" <<'YAML'
session_id: ""
orchestrator_agent: ""
subagents_used: []
active_wrk: ""
last_stage: ""
handoff_allowed: false
updated_at: ""
YAML
    fi
}

session_get() {
    local key="$1"
    awk -F': ' -v key="$key" '$1==key {gsub(/^"|"$/, "", $2); print $2; exit}' "$SESSION_STATE_FILE" 2>/dev/null || true
}

session_set_scalar() {
    local key="$1"
    local value="$2"
    local tmp
    tmp="$(mktemp)"
    awk -v key="$key" -v value="$value" '
        BEGIN { updated=0 }
        $1==key":" {
            print key ": \"" value "\""
            updated=1
            next
        }
        { print }
        END {
            if (!updated) {
                print key ": \"" value "\""
            }
        }
    ' "$SESSION_STATE_FILE" > "$tmp"
    mv "$tmp" "$SESSION_STATE_FILE"
}

session_set_bool() {
    local key="$1"
    local value="$2"
    local tmp
    tmp="$(mktemp)"
    awk -v key="$key" -v value="$value" '
        BEGIN { updated=0 }
        $1==key":" {
            print key ": " value
            updated=1
            next
        }
        { print }
        END {
            if (!updated) {
                print key ": " value
            }
        }
    ' "$SESSION_STATE_FILE" > "$tmp"
    mv "$tmp" "$SESSION_STATE_FILE"
}

session_set_list() {
    local key="$1"
    shift
    local values=("$@")
    local tmp
    tmp="$(mktemp)"
    awk -v key="$key" '
        BEGIN { skipping=0; replaced=0 }
        $1==key":" {
            if (!replaced) {
                print key ":"
                replaced=1
            }
            skipping=1
            next
        }
        skipping && $0 ~ /^[[:space:]]*-[[:space:]]/ { next }
        skipping { skipping=0 }
        { print }
        END {
            if (!replaced) print key ":"
        }
    ' "$SESSION_STATE_FILE" > "$tmp"
    mv "$tmp" "$SESSION_STATE_FILE"

    tmp="$(mktemp)"
    if [[ ${#values[@]} -eq 0 ]]; then
        awk -v key="$key" '
            BEGIN { done=0 }
            {
                if (!done && $1==key":") {
                    print key ": []"
                    done=1
                } else {
                    print
                }
            }
        ' "$SESSION_STATE_FILE" > "$tmp"
    else
        awk -v key="$key" -v vals="${values[*]}" '
            BEGIN { split(vals, arr, " "); done=0 }
            {
                if (!done && $1==key":") {
                    print key ":"
                    for (i=1; i<=length(arr); i++) {
                        if (arr[i] != "") print "  - " arr[i]
                    }
                    done=1
                } else {
                    print
                }
            }
        ' "$SESSION_STATE_FILE" > "$tmp"
    fi
    mv "$tmp" "$SESSION_STATE_FILE"
}

session_add_subagent() {
    local provider="$1"
    local existing
    existing="$(awk '/^[[:space:]]*-[[:space:]]/{print $2}' "$SESSION_STATE_FILE" 2>/dev/null | tr '\n' ' ')"
    if [[ " $existing " != *" $provider "* ]]; then
        local values=($existing "$provider")
        session_set_list "subagents_used" "${values[@]}"
    fi
}

session_update_timestamp() {
    session_set_scalar "updated_at" "$(session_now_iso)"
}

session_clear() {
    ensure_session_store
    session_set_scalar "session_id" ""
    session_set_scalar "orchestrator_agent" ""
    session_set_list "subagents_used"
    session_set_scalar "active_wrk" ""
    session_set_scalar "last_stage" ""
    session_set_bool "handoff_allowed" "false"
    session_update_timestamp
}
