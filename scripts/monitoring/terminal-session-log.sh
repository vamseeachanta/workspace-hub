#!/usr/bin/env bash
# terminal-session-log.sh — WRK-1022 terminal session logger
# Run at the END of a session to snapshot recent commands and detect friction.
# Works on Linux and Windows Git Bash.
#
# Usage:
#   bash scripts/monitoring/terminal-session-log.sh [--note "any friction or comment"]
#
# Output: state/terminal-monitoring/sessions.jsonl

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
LOG_DIR="$REPO_ROOT/state/terminal-monitoring"
LOG_FILE="$LOG_DIR/sessions.jsonl"
HISTORY_SNAPSHOT="$LOG_DIR/last-snapshot.txt"
mkdir -p "$LOG_DIR"

# --- args ---
NOTE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --note) NOTE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# --- gather context ---
MACHINE="$(hostname)"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
DATE="$(date +"%Y-%m-%d")"

# OS detection (Linux vs Windows Git Bash)
OS="linux"
if [[ "$(uname -s)" == MINGW* ]] || [[ "$(uname -s)" == MSYS* ]] || [[ "$(uname -s)" == CYGWIN* ]]; then
  OS="windows-gitbash"
fi

# Flush in-memory history to file first
history -w 2>/dev/null || true

# Grab last 30 commands from history (strip line numbers)
HIST_FILE="${HISTFILE:-$HOME/.bash_history}"
LAST_CMDS=""
if [[ -f "$HIST_FILE" ]]; then
  LAST_CMDS="$(tail -30 "$HIST_FILE" | grep -v '^#' | grep -v '^$' | tr '\n' '|')"
fi

# --- friction pattern detection ---
FRICTION_FLAGS=""

# cls on Linux = Windows habit confusion
if [[ "$OS" == "linux" ]] && echo "$LAST_CMDS" | grep -qw "cls"; then
  FRICTION_FLAGS="${FRICTION_FLAGS}cls-on-linux,"
fi

# Wrong startup flags (just "claude" or "codex" without flags = likely intentional, skip)
# Detect if they used a flag that failed (codex --dangerously-skip-permissions = wrong agent)
if echo "$LAST_CMDS" | grep -q "codex --dangerously-skip-permissions"; then
  FRICTION_FLAGS="${FRICTION_FLAGS}wrong-flag-codex,"
fi
if echo "$LAST_CMDS" | grep -q "claude --yolo"; then
  FRICTION_FLAGS="${FRICTION_FLAGS}wrong-flag-claude,"
fi
if echo "$LAST_CMDS" | grep -q "gemini --dangerously"; then
  FRICTION_FLAGS="${FRICTION_FLAGS}wrong-flag-gemini,"
fi

# xit / exxit / ext = mistyped exit
if echo "$LAST_CMDS" | grep -qE '\bxit\b|\bexxit\b|\bext\b'; then
  FRICTION_FLAGS="${FRICTION_FLAGS}mistyped-exit,"
fi

FRICTION_FLAGS="${FRICTION_FLAGS%,}"  # strip trailing comma

# --- count session type ---
CLAUDE_STARTS="$(echo "$LAST_CMDS" | tr '|' '\n' | grep -c "claude" || true)"
CODEX_STARTS="$(echo "$LAST_CMDS" | tr '|' '\n' | grep -c "codex" || true)"
GEMINI_STARTS="$(echo "$LAST_CMDS" | tr '|' '\n' | grep -c "gemini" || true)"

# --- write JSONL entry (single line per session) ---
SAMPLE="$(echo "$LAST_CMDS" | cut -c1-200 | sed 's/"/\\"/g')"
printf '{"timestamp":"%s","date":"%s","machine":"%s","os":"%s","wrk":"WRK-1022","friction_flags":"%s","note":"%s","agents_seen":{"claude":%d,"codex":%d,"gemini":%d},"last_cmds_sample":"%s"}\n' \
  "$TIMESTAMP" "$DATE" "$MACHINE" "$OS" \
  "$FRICTION_FLAGS" "$NOTE" \
  "$CLAUDE_STARTS" "$CODEX_STARTS" "$GEMINI_STARTS" \
  "$SAMPLE" >> "$LOG_FILE"

# --- print summary ---
echo "=== WRK-1022 Session Logged ==="
echo "  Machine : $MACHINE ($OS)"
echo "  Time    : $TIMESTAMP"
echo "  Friction: ${FRICTION_FLAGS:-none detected}"
echo "  Note    : ${NOTE:-<none>}"
echo "  Log     : $LOG_FILE"
echo ""
echo "Total sessions logged: $(wc -l < "$LOG_FILE")"
