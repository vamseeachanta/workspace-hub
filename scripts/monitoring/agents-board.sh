#!/usr/bin/env bash
# agents-board.sh — single board for Claude + Codex + Hermes agents on this machine.
#
# Each tool exposes liveness differently, so this normalizes on the ONE thing they
# share — a live process / authoritative daemon — never on a stale on-disk file:
#
#   Claude  ~/.claude/sessions/<pid>.json   → registry w/ status; trust only if PID alive
#   Codex   live `codex` process            → no liveness registry exists; session_index
#                                             .jsonl is history only (can be days stale)
#   Hermes  ~/.hermes/gateway_state.json     → authoritative daemon: gateway_state,
#           + tui_gateway.slash_worker procs   active_agents, platform health; workers=procs
#
# Usage:
#   agents-board.sh            one-shot board
#   agents-board.sh -w [SECS]  watch mode (default 5s)
#   agents-board.sh -h         help
#
# Read-only. Never writes or kills anything.

set -uo pipefail   # no -e: a missing/!installed provider must degrade, not abort

CLAUDE_DIR="${CLAUDE_HOME:-$HOME/.claude}"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
HERMES_DIR="${HERMES_HOME:-$HOME/.hermes}"
WATCH=0; INTERVAL=5

while [[ $# -gt 0 ]]; do
  case "$1" in
    -w|--watch) WATCH=1; [[ "${2:-}" =~ ^[0-9]+$ ]] && { INTERVAL="$2"; shift; } ;;
    -h|--help)  awk 'NR>1 && /^#/{print} NR>1 && !/^#/{exit}' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done
command -v jq >/dev/null || { echo "jq required" >&2; exit 1; }

# ---- duration helpers -------------------------------------------------------
hs() {  # seconds -> compact
  local s="${1:-0}" d h m; [[ "$s" =~ ^[0-9]+$ ]] || s=0; (( s<0 )) && s=0
  d=$((s/86400)); h=$(((s%86400)/3600)); m=$(((s%3600)/60))
  if   (( d>0 )); then printf '%dd%dh' "$d" "$h"
  elif (( h>0 )); then printf '%dh%dm' "$h" "$m"
  elif (( m>0 )); then printf '%dm'    "$m"
  else printf '%ds' "$s"; fi
}
hms() { local now; now=$(date +%s%3N); hs $(( (now - ${1:-0}) / 1000 )); }   # ms-epoch
etimes() { ps -o etimes= -p "$1" 2>/dev/null | tr -d ' '; }                  # proc age (s)
iso_age() { # ISO8601 -> "<dur> ago" using GNU date
  local t; t=$(date -d "$1" +%s 2>/dev/null) || { printf '?'; return; }
  hs $(( $(date +%s) - t ))
}

# ---- colors -----------------------------------------------------------------
C_CLAUDE='\033[38;5;75m'; C_CODEX='\033[38;5;213m'; C_HERMES='\033[38;5;220m'
G_LIVE='\033[32m'; G_BUSY='\033[33m'; G_DOWN='\033[31m'; G_IDLE='\033[2m'; R='\033[0m'

row() { # provider_color provider status_color status ref age idle detail
  printf "${1}%-7s${R} ${3}%-8s${R} %-9s %-7s %-6s %s\n" \
         "$2" "$4" "${5:0:9}" "${6:-—}" "${7:-—}" "$8"
}

declare -i n_claude n_codex n_hermes

# ---- Claude -----------------------------------------------------------------
collect_claude() {
  n_claude=0; shopt -s nullglob
  for f in "$CLAUDE_DIR"/sessions/*.json; do
    local pid cwd st started updated rstatus
    pid=$(jq -r '.pid // empty' "$f"); [[ -z "$pid" ]] && continue
    kill -0 "$pid" 2>/dev/null || continue          # stale registry → skip
    cwd=$(jq -r '.cwd // "?"' "$f")
    rstatus=$(jq -r '.status // "?"' "$f")
    started=$(jq -r '.startedAt // 0' "$f")
    updated=$(jq -r '.updatedAt // .startedAt // 0' "$f")
    n_claude+=1
    if [[ "$rstatus" == busy ]]; then row "$C_CLAUDE" claude "$G_BUSY" "● busy" "$pid" "$(hms "$started")" "$(hms "$updated")" "$cwd"
    else                                row "$C_CLAUDE" claude "$G_IDLE" "○ idle" "$pid" "$(hms "$started")" "$(hms "$updated")" "$cwd"; fi
  done
}

# ---- Codex ------------------------------------------------------------------
collect_codex() {
  n_codex=0
  # live agent = a `codex` process that is NOT the update-manager daemon
  local pids; pids=$(pgrep -af 'codex' 2>/dev/null | grep -v 'codex-update-manager' \
                     | grep -vi 'agents-board\|monitor-sessions' | awk '{print $1}')
  for pid in $pids; do
    kill -0 "$pid" 2>/dev/null || continue
    local cmd; cmd=$(ps -o args= -p "$pid" 2>/dev/null | cut -c1-50)
    n_codex+=1
    row "$C_CODEX" codex "$G_LIVE" "● live" "$pid" "$(hs "$(etimes "$pid")")" "—" "$cmd"
  done
  if (( n_codex == 0 )); then
    # no active agent — surface most-recent thread from the history index
    local last; last=$(tail -1 "$CODEX_DIR/session_index.jsonl" 2>/dev/null)
    local name age; name=$(jq -r '.thread_name // ""' <<<"$last" 2>/dev/null | cut -c1-44)
    age=$(iso_age "$(jq -r '.updated_at // ""' <<<"$last" 2>/dev/null)")
    row "$C_CODEX" codex "$G_IDLE" "○ none" "—" "—" "—" "no active agent · last: ${name:-—} (${age} ago)"
  fi
}

# ---- Hermes -----------------------------------------------------------------
collect_hermes() {
  n_hermes=0
  local gs="$HERMES_DIR/gateway_state.json"
  if [[ -f "$gs" ]]; then
    local gpid gstate gactive plats start updated alive detail
    gpid=$(jq -r '.pid // empty' "$gs")
    gstate=$(jq -r '.gateway_state // "?"' "$gs")
    gactive=$(jq -r '.active_agents // 0' "$gs")
    plats=$(jq -r '.platforms | to_entries | map("\(.key):\(.value.state)") | join(" ")' "$gs" 2>/dev/null)
    updated=$(jq -r '.updated_at // ""' "$gs")
    detail="agents:${gactive}  ${plats}"
    if [[ -n "$gpid" ]] && kill -0 "$gpid" 2>/dev/null; then
      n_hermes+=1
      row "$C_HERMES" hermes "$G_LIVE" "◆ ${gstate}" "$gpid" "$(hs "$(etimes "$gpid")")" "$(iso_age "$updated")" "gateway · $detail"
    else
      row "$C_HERMES" hermes "$G_DOWN" "◆ down" "${gpid:-—}" "—" "$(iso_age "$updated")" "gateway not running · $detail"
    fi
  fi
  # spawned agent workers (one row each)
  local wpids; wpids=$(pgrep -af 'tui_gateway.slash_worker' 2>/dev/null | awk '{print $1}')
  for pid in $wpids; do
    kill -0 "$pid" 2>/dev/null || continue
    local args sk model
    args=$(ps -o args= -p "$pid" 2>/dev/null)
    sk=$(grep -oP '(?<=--session-key )\S+' <<<"$args"); model=$(grep -oP '(?<=--model )\S+' <<<"$args")
    n_hermes+=1
    row "$C_HERMES" hermes "$G_LIVE" "● worker" "$pid" "$(hs "$(etimes "$pid")")" "—" "model:${model:-?} key:${sk:-?}"
  done
}

render() {
  printf '\033[1m%-7s %-8s %-9s %-7s %-6s %s\033[0m\n' PROVIDER STATUS REF AGE IDLE DETAIL
  printf '%s\n' "──────────────────────────────────────────────────────────────────────────────"
  collect_claude
  collect_codex
  collect_hermes
  printf '%s\n' "──────────────────────────────────────────────────────────────────────────────"
  printf "${C_CLAUDE}claude:%d${R}  ${C_CODEX}codex:%d${R}  ${C_HERMES}hermes:%d${R}   total live rows: %d\n" \
         "$n_claude" "$n_codex" "$n_hermes" "$(( n_claude + n_codex + n_hermes ))"
  return 0
}

if (( WATCH )); then
  trap 'tput cnorm 2>/dev/null; exit 0' INT
  tput civis 2>/dev/null || true
  while :; do
    clear
    printf '\033[2magents-board — %s — refresh %ss (Ctrl-C to exit)\033[0m\n\n' "$(date '+%H:%M:%S')" "$INTERVAL"
    render
    sleep "$INTERVAL"
  done
else
  render
fi
