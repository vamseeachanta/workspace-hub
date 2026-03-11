#!/usr/bin/env bash
# active-sessions.sh — List all WRK items with active session locks on this workstation.
# Liveness = age-only heuristic: locked_at within 2h (7200s)
# Claimed/unclaimed = queue folder location (working/ vs pending/)
# Usage: bash scripts/work-queue/active-sessions.sh [--json] [--unclaimed-only]

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
MAX_AGE_S=7200   # 2h
JSON=false
UNCLAIMED_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)           JSON=true; shift ;;
    --unclaimed-only) UNCLAIMED_ONLY=true; shift ;;
    *) shift ;;
  esac
done

# Output accumulators (json mode)
declare -a JSON_ROWS

_age_seconds() {
  local locked_at="$1"
  local now lock_ts age_s
  now=$(date +%s)
  lock_ts=$(date -d "$locked_at" +%s 2>/dev/null) || { echo ""; return; }
  age_s=$(( now - lock_ts ))
  # Reject future-dated locks (clock skew: more than 1 day in future)
  (( age_s < -86400 )) && { echo ""; return; }
  echo "$age_s"
}

_queue_location() {
  local wrk_id="$1"
  if [[ -f "$QUEUE_DIR/working/$wrk_id.md" ]]; then
    echo "working"
  elif [[ -f "$QUEUE_DIR/pending/$wrk_id.md" ]]; then
    echo "pending"
  else
    echo "unknown"
  fi
}

_classify() {
  local loc="$1"
  if [[ "$loc" == "working" ]]; then
    echo "claimed"
  elif [[ "$loc" == "pending" ]]; then
    echo "unclaimed"
  else
    echo "unknown"
  fi
}

HR=$(printf '%0.s─' {1..78})

if [[ "$JSON" == "false" ]]; then
  echo ""
  printf "\033[1m╔══════════════════════════════════════════════╗\033[0m\n"
  printf "\033[1m║   ACTIVE SESSIONS  %-26s║\033[0m\n" "$(date '+%Y-%m-%d %H:%M')     "
  printf "\033[1m╚══════════════════════════════════════════════╝\033[0m\n"
fi

found=0

for lock in "$QUEUE_DIR/assets"/WRK-*/evidence/session-lock.yaml; do
  [[ -f "$lock" ]] || continue

  wrk_id=$(basename "$(dirname "$(dirname "$lock")")")

  # Read locked_at — strip quotes
  locked_at=$(grep "^locked_at:" "$lock" 2>/dev/null | tr -d '"' | awk '{print $2}')
  [[ -z "$locked_at" ]] && continue

  hostname=$(grep "^hostname:" "$lock" 2>/dev/null | awk '{print $2}')

  age_s=$(_age_seconds "$locked_at")
  [[ -z "$age_s" ]] && continue

  # Skip stale locks (age >= MAX_AGE_S)
  if (( age_s >= MAX_AGE_S )); then
    continue
  fi

  age_min=$(( age_s / 60 ))
  loc=$(_queue_location "$wrk_id")
  status=$(_classify "$loc")

  # Filter for unclaimed-only mode
  if [[ "$UNCLAIMED_ONLY" == "true" && "$status" != "unclaimed" ]]; then
    continue
  fi

  found=$(( found + 1 ))

  if [[ "$JSON" == "true" ]]; then
    JSON_ROWS+=("{\"wrk_id\":\"$wrk_id\",\"status\":\"$status\",\"age_min\":$age_min,\"hostname\":\"$hostname\",\"locked_at\":\"$locked_at\"}")
  else
    # Colour by status
    if [[ "$status" == "unclaimed" ]]; then
      colour="\033[33m"  # yellow
    else
      colour="\033[32m"  # green
    fi
    printf "${colour}%-14s %-10s %-8s %-20s %s\033[0m\n" \
      "$wrk_id" "$status" "${age_min}min" "$hostname" "$locked_at"
  fi
done

if [[ "$JSON" == "true" ]]; then
  echo "["
  for (( i=0; i<${#JSON_ROWS[@]}; i++ )); do
    if (( i < ${#JSON_ROWS[@]} - 1 )); then
      echo "  ${JSON_ROWS[$i]},"
    else
      echo "  ${JSON_ROWS[$i]}"
    fi
  done
  echo "]"
else
  if (( found == 0 )); then
    echo "  (no active sessions found)"
  fi
  echo ""
fi
