#!/usr/bin/env bash
# monitor-sessions.sh — unified view of all Claude Code / Cowork sessions on this machine.
#
# Ground truth: ~/.claude/sessions/<pid>.json (the registry the desktop sidebar reads).
# Each entry is cross-checked against a LIVE process, because a registry file
# existing on disk is NOT proof the session is still running (stale entries linger
# after a crash/kill). A session counts as active only if its PID is alive.
#
# Usage:
#   monitor-sessions.sh             # one-shot table
#   monitor-sessions.sh -w [SECS]   # watch mode, refresh every SECS (default 5)
#   monitor-sessions.sh -l          # long: add gitBranch + last-activity snippet
#   monitor-sessions.sh --prune     # delete registry files whose PID is dead
#   monitor-sessions.sh -h          # help
#
# Read-only by default. --prune is the only mutating action and touches ONLY
# entries whose PID is confirmed dead.

# No `set -e`: a missing transcript or empty `read` must degrade gracefully,
# never abort the whole table. `-u`/pipefail stay for real bugs.
set -uo pipefail

SESS_DIR="${CLAUDE_HOME:-$HOME/.claude}/sessions"
PROJ_DIR="${CLAUDE_HOME:-$HOME/.claude}/projects"
WATCH=0; INTERVAL=5; LONG=0; PRUNE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -w|--watch) WATCH=1; [[ "${2:-}" =~ ^[0-9]+$ ]] && { INTERVAL="$2"; shift; } ;;
    -l|--long)  LONG=1 ;;
    --prune)    PRUNE=1 ;;
    -h|--help)  awk 'NR>1 && /^#/{print} NR>1 && !/^#/{exit}' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

command -v jq >/dev/null || { echo "jq required" >&2; exit 1; }

# ms-epoch -> compact human duration (e.g. 3h12m, 45s)
human() {
  local ms="$1" now sec d h m
  now=$(date +%s%3N)
  sec=$(( (now - ms) / 1000 ))
  (( sec < 0 )) && sec=0
  d=$(( sec/86400 )); h=$(( (sec%86400)/3600 )); m=$(( (sec%3600)/60 ))
  if   (( d > 0 )); then printf '%dd%dh' "$d" "$h"
  elif (( h > 0 )); then printf '%dh%dm' "$h" "$m"
  elif (( m > 0 )); then printf '%dm' "$m"
  else printf '%ds' "$sec"; fi
}

# Pull gitBranch + last user-message snippet from a session's transcript.
transcript_info() {
  local sid="$1" f
  f=$(ls "$PROJ_DIR"/*/"$sid".jsonl 2>/dev/null | head -1) || return 0
  [[ -z "${f:-}" ]] && return 0
  # last line carrying a gitBranch; snippet from last user text
  local br snip
  br=$(tac "$f" 2>/dev/null | grep -m1 '"gitBranch"' | jq -r '.gitBranch // ""' 2>/dev/null || true)
  # newest non-empty text block from any message (user typed OR assistant reply);
  # tool_result lines carry no .text and are skipped automatically.
  snip=$(tail -n 400 "$f" 2>/dev/null | tac \
        | jq -r 'select(.message.content?)
                 | if (.message.content|type)=="string" then .message.content
                   else (.message.content[]?|select(.type=="text")|.text) end' 2>/dev/null \
        | grep -m1 . | tr '\n' ' ' | cut -c1-60 || true)
  printf '%s\t%s' "${br:-—}" "${snip:-}"
}

declare -i alive=0 stale=0 busy=0
declare -a STALE_FILES=()

render() {
  alive=0; stale=0; busy=0; STALE_FILES=()
  printf '\033[1m%-8s %-9s %-6s %-7s %-7s %-8s %s\033[0m\n' \
         PID STATUS KIND AGE IDLE VER CWD
  printf '%s\n' "────────────────────────────────────────────────────────────────────────────"

  shopt -s nullglob
  for f in "$SESS_DIR"/*.json; do
    pid=$(jq -r '.pid'        "$f"); [[ "$pid" == null ]] && continue
    sid=$(jq -r '.sessionId'  "$f")
    cwd=$(jq -r '.cwd // "?"' "$f")
    kind=$(jq -r '.kind // .entrypoint // "?"' "$f")
    ver=$(jq -r '.version // "?"' "$f")
    started=$(jq -r '.startedAt // 0' "$f")
    updated=$(jq -r '.updatedAt // .startedAt // 0' "$f")
    rstatus=$(jq -r '.status // "?"' "$f")

    if kill -0 "$pid" 2>/dev/null; then
      alive+=1
      [[ "$rstatus" == busy ]] && { busy+=1; st="● busy"; col='\033[33m'; } \
                               || { st="○ idle"; col='\033[32m'; }
    else
      stale+=1; STALE_FILES+=("$f"); st="✗ dead"; col='\033[31m'
    fi

    printf "${col}%-8s %-9s\033[0m %-6s %-7s %-7s %-8s %s\n" \
      "$pid" "$st" "${kind:0:6}" "$(human "$started")" "$(human "$updated")" "$ver" "$cwd"

    if (( LONG )); then
      IFS=$'\t' read -r br snip < <(transcript_info "$sid")
      printf '         └ \033[36m%s\033[0m  %s\n' "$br" "$snip"
    fi
  done

  printf '%s\n' "────────────────────────────────────────────────────────────────────────────"
  printf 'alive: \033[1m%d\033[0m  (busy %d / idle %d)   stale: %d\n' \
         "$alive" "$busy" "$((alive-busy))" "$stale"
  if (( stale > 0 && PRUNE == 0 )); then
    printf '  ↳ %d stale registry file(s); run with --prune to remove\n' "$stale"
  fi
  return 0   # arithmetic tests above must not become the function's exit code
}

if (( PRUNE )); then
  render
  if (( ${#STALE_FILES[@]} > 0 )); then
    echo; echo "Pruning ${#STALE_FILES[@]} dead-PID registry file(s):"
    for f in "${STALE_FILES[@]}"; do echo "  rm $f"; rm -f "$f"; done
  else
    echo "No stale entries to prune."
  fi
  exit 0
fi

if (( WATCH )); then
  trap 'tput cnorm 2>/dev/null; exit 0' INT
  tput civis 2>/dev/null || true
  while :; do
    clear
    printf '\033[2mmonitor-sessions — %s — refresh %ss (Ctrl-C to exit)\033[0m\n\n' \
           "$(date '+%H:%M:%S')" "$INTERVAL"
    render
    sleep "$INTERVAL"
  done
else
  render
fi
