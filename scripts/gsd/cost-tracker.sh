#!/usr/bin/env bash
# GSD Cost Tracker — append and summarize cost events from .planning/cost-events.jsonl
# Usage: cost-tracker.sh <command> [args]
#   append_event   --session <id> --phase <p> --agent <type> --provider <prov> --model <m> \
#                  --input <n> --output <n> [--cached <n>] --cost <cents>
#   summarize_session <session_id>
#   summarize_rolling [24h|7d]    (default: 24h)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
COST_FILE="${COST_FILE:-${REPO_ROOT}/.planning/cost-events.jsonl}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
die()  { echo "error: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"; }

need jq
need date

iso_now() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# Cross-platform epoch conversion (GNU date vs BSD date)
to_epoch() {
  local ts="$1"
  # Try GNU date first
  date -d "$ts" +%s 2>/dev/null && return
  # Fall back to BSD date
  date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts" +%s 2>/dev/null && return
  # Fall back to jq for portability
  echo "$ts" | jq -r 'now - (now - (. | sub("Z$"; "+00:00") | fromdate))' 2>/dev/null && return
  die "cannot parse timestamp: $ts"
}

# ---------------------------------------------------------------------------
# append_event — write one JSONL line
# ---------------------------------------------------------------------------
cmd_append_event() {
  local session="" phase="" agent="" provider="anthropic" model=""
  local input_tokens=0 output_tokens=0 cached_tokens=0 cost_cents=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --session)  session="$2";       shift 2 ;;
      --phase)    phase="$2";         shift 2 ;;
      --agent)    agent="$2";         shift 2 ;;
      --provider) provider="$2";      shift 2 ;;
      --model)    model="$2";         shift 2 ;;
      --input)    input_tokens="$2";  shift 2 ;;
      --output)   output_tokens="$2"; shift 2 ;;
      --cached)   cached_tokens="$2"; shift 2 ;;
      --cost)     cost_cents="$2";    shift 2 ;;
      *) die "unknown flag: $1" ;;
    esac
  done

  [[ -n "$session" ]] || die "append_event: --session required"
  [[ -n "$agent" ]]   || die "append_event: --agent required"
  [[ -n "$model" ]]   || die "append_event: --model required"

  mkdir -p "$(dirname "$COST_FILE")"

  local phase_val
  if [[ -n "$phase" ]]; then
    phase_val="\"$phase\""
  else
    phase_val="null"
  fi

  jq -cn \
    --arg ts "$(iso_now)" \
    --arg sid "$session" \
    --argjson phase "$phase_val" \
    --arg agent "$agent" \
    --arg provider "$provider" \
    --arg model "$model" \
    --argjson input "$input_tokens" \
    --argjson output "$output_tokens" \
    --argjson cached "$cached_tokens" \
    --argjson cost "$cost_cents" \
    '{
      timestamp: $ts,
      session_id: $sid,
      phase: $phase,
      agent_type: $agent,
      provider: $provider,
      model: $model,
      input_tokens: $input,
      output_tokens: $output,
      cached_input_tokens: $cached,
      cost_cents: $cost
    }' >> "$COST_FILE"

  echo "ok: event appended to $COST_FILE"
}

# ---------------------------------------------------------------------------
# summarize_session — totals for one session_id
# ---------------------------------------------------------------------------
cmd_summarize_session() {
  local sid="${1:-}"
  [[ -n "$sid" ]] || die "summarize_session: session_id required"
  [[ -f "$COST_FILE" ]] || die "no cost file: $COST_FILE"

  local result
  result=$(jq -s --arg sid "$sid" '
    [ .[] | select(.session_id == $sid) ] |
    if length == 0 then error("no events for session: " + $sid) else . end |
    {
      session_id: $sid,
      events: length,
      input_tokens: (map(.input_tokens) | add),
      output_tokens: (map(.output_tokens) | add),
      cached_input_tokens: (map(.cached_input_tokens) | add),
      total_cost_cents: (map(.cost_cents) | add),
      agents: (map(.agent_type) | unique),
      models: (map(.model) | unique)
    }
  ' "$COST_FILE") || die "no events found for session: $sid"

  # Table output
  echo ""
  echo "Session: $sid"
  echo "─────────────────────────────────────"
  echo "$result" | jq -r '
    "Events:          \(.events)",
    "Input tokens:    \(.input_tokens)",
    "Output tokens:   \(.output_tokens)",
    "Cached tokens:   \(.cached_input_tokens)",
    "Total cost:      $\(.total_cost_cents / 100 | . * 100 | round / 100)",
    "Agents:          \(.agents | join(", "))",
    "Models:          \(.models | join(", "))"
  '
  echo ""
}

# ---------------------------------------------------------------------------
# summarize_rolling — totals for last 24h or 7d
# ---------------------------------------------------------------------------
cmd_summarize_rolling() {
  local window="${1:-24h}"
  [[ -f "$COST_FILE" ]] || die "no cost file: $COST_FILE"

  local seconds
  case "$window" in
    24h) seconds=86400 ;;
    7d)  seconds=604800 ;;
    *)   die "unsupported window: $window (use 24h or 7d)" ;;
  esac

  local cutoff_epoch
  cutoff_epoch=$(( $(date -u +%s) - seconds ))

  local result
  result=$(jq -s --argjson cutoff "$cutoff_epoch" '
    [ .[] | select((.timestamp | strptime("%Y-%m-%dT%H:%M:%SZ") | mktime) >= $cutoff) ] |
    {
      window_events: length,
      sessions: (map(.session_id) | unique | length),
      input_tokens: (if length > 0 then map(.input_tokens) | add else 0 end),
      output_tokens: (if length > 0 then map(.output_tokens) | add else 0 end),
      cached_input_tokens: (if length > 0 then map(.cached_input_tokens) | add else 0 end),
      total_cost_cents: (if length > 0 then map(.cost_cents) | add else 0 end),
      by_model: (group_by(.model) | map({
        model: .[0].model,
        events: length,
        cost_cents: (map(.cost_cents) | add)
      })),
      by_agent: (group_by(.agent_type) | map({
        agent: .[0].agent_type,
        events: length,
        cost_cents: (map(.cost_cents) | add)
      }))
    }
  ' "$COST_FILE")

  echo ""
  echo "Rolling window: $window"
  echo "─────────────────────────────────────"
  echo "$result" | jq -r '
    "Events:          \(.window_events)",
    "Sessions:        \(.sessions)",
    "Input tokens:    \(.input_tokens)",
    "Output tokens:   \(.output_tokens)",
    "Cached tokens:   \(.cached_input_tokens)",
    "Total cost:      $\(.total_cost_cents / 100 | . * 100 | round / 100)",
    "",
    "By Model:",
    (.by_model[] | "  \(.model): \(.events) events, $\(.cost_cents / 100 | . * 100 | round / 100)"),
    "",
    "By Agent:",
    (.by_agent[] | "  \(.agent): \(.events) events, $\(.cost_cents / 100 | . * 100 | round / 100)")
  '
  echo ""
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
cmd="${1:-help}"
shift || true

case "$cmd" in
  append_event)      cmd_append_event "$@" ;;
  summarize_session) cmd_summarize_session "$@" ;;
  summarize_rolling) cmd_summarize_rolling "$@" ;;
  help|--help|-h)
    echo "Usage: cost-tracker.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  append_event      Append a cost event to the JSONL file"
    echo "  summarize_session Summarize costs for a session ID"
    echo "  summarize_rolling Summarize costs for last 24h or 7d"
    echo ""
    echo "Environment:"
    echo "  COST_FILE  Override default path (.planning/cost-events.jsonl)"
    ;;
  *) die "unknown command: $cmd (try --help)" ;;
esac
