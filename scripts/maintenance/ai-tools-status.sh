#!/usr/bin/env bash
# ABOUTME: Check AI CLI tool versions on this machine; aggregate on ace-linux-1
# ABOUTME: Runs hourly via cron. Latest npm versions cached 24h.
# Usage: ./ai-tools-status.sh [--quiet]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STATUS_DIR="$REPO_ROOT/config/ai_agents/status"
AGGREGATE="$REPO_ROOT/config/ai_agents/ai-tools-status.yaml"
mkdir -p "$STATUS_DIR"
NPM_CACHE="/tmp/ai-tools-npm-latest.cache"
NPM_CACHE_TTL=86400  # 24h
THIS_HOST=$(hostname -s)
QUIET="${1:-}"
TS=$(date -Iseconds)

# ── helpers ──────────────────────────────────────────────────────────────────
log() { [[ "$QUIET" == "--quiet" ]] || echo "$*"; }

tool_ver() {
    local cmd="$1"
    command -v "$cmd" &>/dev/null || { echo "not-installed"; return; }
    "$cmd" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1 || echo "unknown"
}

node_ver() {
    command -v node &>/dev/null || { echo "not-installed"; return; }
    node --version 2>/dev/null | tr -d 'v' || echo "unknown"
}

refresh_npm_cache() {
    local age=999999
    [[ -f "$NPM_CACHE" ]] && age=$(( $(date +%s) - $(stat -c %Y "$NPM_CACHE") ))
    (( age < NPM_CACHE_TTL )) && return
    log "[ai-tools-status] Refreshing npm latest versions..."
    {
        echo "claude=$(npm view @anthropic-ai/claude-code version 2>/dev/null || echo unknown)"
        echo "codex=$(npm view @openai/codex version 2>/dev/null || echo unknown)"
        echo "gemini=$(npm view @google/gemini-cli version 2>/dev/null || echo unknown)"
        echo "gh=$(gh --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1 || echo unknown)"
    } > "$NPM_CACHE"
}

npm_latest() { grep "^$1=" "$NPM_CACHE" 2>/dev/null | cut -d= -f2 || echo "unknown"; }

status_for() {
    local installed="$1" latest="$2"
    [[ "$installed" == "not-installed" ]] && echo "missing" && return
    [[ "$installed" == "$latest" || "$latest" == "unknown" ]] && echo "ok" && return
    echo "behind"
}

# ── write per-machine YAML ────────────────────────────────────────────────────
write_machine_yaml() {
    local host="$1" node_v="$2" claude_v="$3" codex_v="$4" gemini_v="$5" gh_v="$6"

    refresh_npm_cache
    local l_claude l_codex l_gemini
    l_claude=$(npm_latest claude); l_codex=$(npm_latest codex); l_gemini=$(npm_latest gemini)

    local issues=""
    local node_major; node_major=$(echo "$node_v" | cut -d. -f1)
    (( node_major < 20 )) && issues+=$'\n    - "node '"$node_v"' < 20 required — upgrade to v22"'
    [[ $(status_for "$claude_v" "$l_claude") != "ok" ]] && issues+=$'\n    - "claude: '"$claude_v"' (latest '"$l_claude"')"'
    [[ $(status_for "$codex_v" "$l_codex") != "ok" ]] && issues+=$'\n    - "codex: '"$codex_v"' (latest '"$l_codex"')"'
    [[ $(status_for "$gemini_v" "$l_gemini") != "ok" ]] && issues+=$'\n    - "gemini: '"$gemini_v"' (latest '"$l_gemini"')"'
    [[ $(status_for "$gh_v" "unknown") == "missing" ]] && issues+=$'\n    - "gh: not installed"'

    local overall="ok"
    [[ -n "$issues" ]] && overall="needs-update"

    cat > "$STATUS_DIR/$host.yaml" <<EOF
host: $host
checked_at: "$TS"
status: $overall
versions:
  node: "$node_v"
  claude: "$claude_v"
  codex: "$codex_v"
  gemini: "$gemini_v"
  gh: "$gh_v"
latest:
  claude: "$l_claude"
  codex: "$l_codex"
  gemini: "$l_gemini"
issues:${issues:-" []"}
EOF
}

# ── collect local ─────────────────────────────────────────────────────────────
log "[ai-tools-status] Collecting versions on $THIS_HOST..."
write_machine_yaml "$THIS_HOST" \
    "$(node_ver)" "$(tool_ver claude)" "$(tool_ver codex)" "$(tool_ver gemini)" "$(tool_ver gh)"

# ── auto-update if any npm tools are behind ───────────────────────────────────
UPDATE_SCRIPT="$(dirname "${BASH_SOURCE[0]}")/ai-tools-update.sh"
if grep -q "^status: needs-update" "$STATUS_DIR/$THIS_HOST.yaml" 2>/dev/null && [[ -x "$UPDATE_SCRIPT" ]]; then
    log "[ai-tools-status] Issues found — running ai-tools-update.sh..."
    bash "$UPDATE_SCRIPT" "$QUIET" || true
    # Re-collect versions after update
    write_machine_yaml "$THIS_HOST" \
        "$(node_ver)" "$(tool_ver claude)" "$(tool_ver codex)" "$(tool_ver gemini)" "$(tool_ver gh)"
fi

# ── on ace-linux-1: also check peer machines ──────────────────────────────────
if [[ "$THIS_HOST" == "ace-linux-1" ]]; then
    log "[ai-tools-status] Checking ace-linux-2 via SSH..."
    if ssh -o ConnectTimeout=5 ace-linux-2 true 2>/dev/null; then
        peer_versions=$(ssh ace-linux-2 '
            export PATH=/home/vamsee/.npm-global/bin:/usr/local/bin:/usr/bin:/bin
            nv() { command -v "$1" &>/dev/null && "$1" --version 2>/dev/null | grep -oP '"'"'\d+\.\d+\.\d+'"'"' | head -1 || echo not-installed; }
            echo "$(node --version 2>/dev/null | tr -d v || echo not-installed)"
            nv claude; nv codex; nv gemini; nv gh
        ' 2>/dev/null) || peer_versions=""
        if [[ -n "$peer_versions" ]]; then
            p_node=$(echo "$peer_versions" | sed -n '1p')
            p_claude=$(echo "$peer_versions" | sed -n '2p')
            p_codex=$(echo "$peer_versions" | sed -n '3p')
            p_gemini=$(echo "$peer_versions" | sed -n '4p')
            p_gh=$(echo "$peer_versions" | sed -n '5p')
            write_machine_yaml "ace-linux-2" "$p_node" "$p_claude" "$p_codex" "$p_gemini" "$p_gh"
        fi
    else
        log "[ai-tools-status] ace-linux-2 unreachable — skipping"
    fi

    # acma-ansys05: Windows stub (only written once)
    if [[ ! -f "$STATUS_DIR/acma-ansys05.yaml" ]]; then
        cat > "$STATUS_DIR/acma-ansys05.yaml" <<EOF
host: acma-ansys05
platform: windows
status: manual-check-required
note: "No SSH access. Check manually via RDP. Use Windows Task Scheduler for automation."
checked_at: "$TS"
EOF
    fi

    # ── aggregate ────────────────────────────────────────────────────────────
    log "[ai-tools-status] Writing aggregate to ai-tools-status.yaml..."
    {
        echo "# Auto-generated by scripts/maintenance/ai-tools-status.sh"
        echo "last_updated: \"$TS\""
        echo "machines:"
        for f in "$STATUS_DIR"/*.yaml; do
            agg_host=$(basename "$f" .yaml)
            echo "  $agg_host:"
            sed 's/^/    /' "$f"
        done
    } > "$AGGREGATE"
fi

log "[ai-tools-status] Done. Status: $STATUS_DIR/$THIS_HOST.yaml"
