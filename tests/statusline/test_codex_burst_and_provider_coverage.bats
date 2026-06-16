#!/usr/bin/env bats
# Tests for #2893 Codex 5-hour headroom and Hermes alias rendering.

SCRIPT="$BATS_TEST_DIRNAME/../../.claude/statusline-command.sh"

setup() {
  TMPDIR=$(mktemp -d)
  export STATUSLINE_QUOTA_PRIMARY="$TMPDIR/agent-quota-latest.json"
  export STATUSLINE_QUOTA_CACHE="$TMPDIR/agent-quota-cache.json"
  export STATUSLINE_GEMINI_SNAPSHOT="$TMPDIR/agy-usage-snapshot.json"
  export GEMINI_ERROR_DIR="$TMPDIR"
  write_gemini_snapshot
}

teardown() {
  rm -rf "$TMPDIR"
}

INPUT='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10}}'

strip_ansi() {
  printf '%s' "$1" | sed 's/\x1b\[[0-9;]*m//g'
}

write_gemini_snapshot() {
  cat > "$STATUSLINE_GEMINI_SNAPSHOT" <<EOF
{
  "captured_at": "$(date -Iseconds)",
  "gemini": {
    "weekly": {"pct_remaining": 100, "reset_hours": 159.5},
    "five_hour": {"pct_remaining": 100, "reset_hours": 3.2}
  }
}
EOF
}

write_quota() {
  local source="${1:-app-server-live}" week_pct="${2:-65}" five_hour_pct="${3:-1}" hours="${4:-60}"
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "agents": [
    {"provider":"claude","week_pct":null,"pct_remaining":null,"hours_to_reset":null,"resets_at":"","source":"unavailable"},
    {"provider":"codex","week_pct":$week_pct,"pct_remaining":$((100 - week_pct)),"five_hour_pct":$five_hour_pct,"hours_to_reset":$hours,"resets_at":"","source":"$source"}
  ]
}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
}

@test "codex shows weekly remaining, reset countdown, 5h remaining, and Hermes alias" {
  write_quota app-server-live 65 1 60
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT' --usage-tail"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"O:35%·2.5d·5h99%"* ]]
  [[ "$clean" == *"|H=O"* ]]
}

@test "codex 5h color is independent from weekly headroom color" {
  # Weekly remaining is green (90%), but 5h remaining is red (10%).
  write_quota app-server-live 10 90 60
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT' --usage-tail"
  [ "$status" -eq 0 ]
  red_5h=$'\033[31m5h10%\033[0m'
  [[ "$output" == *"$red_5h"* ]]
}

@test "codex null five-hour usage does not invent a 5h suffix" {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "agents": [
    {"provider":"codex","week_pct":65,"pct_remaining":35,"five_hour_pct":null,"hours_to_reset":60,"resets_at":"","source":"app-server-live"}
  ]
}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT' --usage-tail"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"O:35%·2.5d"* ]]
  [[ "$clean" != *"5h"* ]]
  [[ "$clean" == *"|H=O"* ]]
}

@test "codex estimate source is visibly marked and does not borrow reset telemetry" {
  write_quota history.jsonl-estimate 65 30 60
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT' --usage-tail"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"O:35%?"* ]]
  [[ "$clean" == *"·5h70%?"* ]]
  [[ "$clean" != *"O:35%?·2.5d"* ]]
  [[ "$clean" == *"|H=O?"* ]]
}

@test "fresh authoritative cache wins over fresh estimate primary for weekly reset and 5h" {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "agents": [
    {"provider":"codex","week_pct":80,"pct_remaining":20,"five_hour_pct":90,"hours_to_reset":99,"resets_at":"","source":"history.jsonl-estimate"}
  ]
}
EOF
  cat > "$STATUSLINE_QUOTA_CACHE" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "agents": [
    {"provider":"codex","pct_remaining":35,"five_hour_pct":1,"hours_to_reset":60,"resets_at":"","source":"app-server-live"}
  ]
}
EOF
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT' --usage-tail"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"O:35%·2.5d·5h99%"* ]]
  [[ "$clean" != *"O:20%?"* ]]
  [[ "$clean" == *"|H=O"* ]]
  [[ "$clean" != *"|H=O?"* ]]
}

@test "missing Codex/OpenAI pool makes Hermes alias visibly unknown" {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "agents": [
    {"provider":"claude","week_pct":null,"pct_remaining":null,"hours_to_reset":null,"resets_at":"","source":"unavailable"}
  ]
}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT' --usage-tail"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"O:-%"* ]]
  [[ "$clean" == *"|H=O?"* ]]
}
