#!/usr/bin/env bash
# Debug session logger

echo "DEBUG: Script started" >&2

WS="/d/workspace-hub"
[ ! -d "$WS" ] && WS="/mnt/github/workspace-hub"
[ ! -d "$WS" ] && WS="$HOME/workspace-hub"

echo "DEBUG: WS=$WS" >&2

LOG_DIR="$WS/.claude/skills/session-logs"
LOG_FILE="$LOG_DIR/session_$(date +%Y%m%d).jsonl"

echo "DEBUG: LOG_FILE=$LOG_FILE" >&2

mkdir -p "$LOG_DIR"

ENTRY="{\"ts\":\"$(date -Iseconds)\",\"hook\":\"${1:-pre}\",\"tool\":\"debug\",\"project\":\"$(basename $(pwd))\"}"
echo "DEBUG: ENTRY=$ENTRY" >&2

echo "$ENTRY" >> "$LOG_FILE"
echo "DEBUG: Write complete" >&2
