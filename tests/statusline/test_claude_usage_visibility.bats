#!/usr/bin/env bats
# Tests for #2893 Claude usage visibility in the compact provider statusline.

SCRIPT="$BATS_TEST_DIRNAME/../../.claude/statusline-command.sh"
PROVIDERS="$BATS_TEST_DIRNAME/../../scripts/ai/assessment/lib/providers.sh"

setup() {
  TMPDIR=$(mktemp -d)
  export STATUSLINE_QUOTA_PRIMARY="$TMPDIR/agent-quota-latest.json"
  export STATUSLINE_QUOTA_CACHE="$TMPDIR/agent-quota-cache.json"
  export STATUSLINE_GEMINI_SNAPSHOT="$TMPDIR/agy-usage-snapshot.json"
  export GEMINI_ERROR_DIR="$TMPDIR"
  export STATUSLINE_CLAUDE_STATS_CACHE="$TMPDIR/stats-cache.json"
  export STATUSLINE_CLAUDE_CREDS="$TMPDIR/.credentials.json"
  write_codex_quota
  write_gemini_snapshot
}

teardown() {
  rm -rf "$TMPDIR"
}

INPUT='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10}}'

strip_ansi() {
  printf '%s' "$1" | sed 's/\x1b\[[0-9;]*m//g'
}

write_codex_quota() {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "agents": [
    {"provider":"claude","week_pct":null,"pct_remaining":null,"hours_to_reset":null,"resets_at":"","source":"unavailable"},
    {"provider":"codex","week_pct":65,"pct_remaining":35,"five_hour_pct":1,"hours_to_reset":60,"resets_at":"","source":"app-server-live"}
  ]
}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
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

write_claude_local_estimate_inputs() {
  cat > "$STATUSLINE_CLAUDE_CREDS" <<'EOF'
{"claudeAiOauth":{"subscriptionType":"pro","rateLimitTier":"pro"}}
EOF
  cat > "$STATUSLINE_CLAUDE_STATS_CACHE" <<EOF
{
  "dailyActivity": [
    {"date":"$(date +%F)","messageCount":1500,"sessionCount":3,"toolCallCount":9},
    {"date":"2000-01-01","messageCount":9000,"sessionCount":9,"toolCallCount":90}
  ]
}
EOF
}

@test "claude live seven-day rate limit remains authoritative when present" {
  write_claude_local_estimate_inputs
  in='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10},"rate_limits":{"seven_day":{"used_percentage":32}}}'
  run bash -c "printf '%s' '$in' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"C:68%"* ]]
  [[ "$clean" != *"C:95%?"* ]]
}

@test "malformed claude live seven-day percentage falls closed to unknown" {
  in='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10},"rate_limits":{"seven_day":{"used_percentage":"not-a-number"}}}'
  run bash -c "printf '%s' '$in' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"C:-%"* ]]
  [[ "$clean" != *"C:100%"* ]]
}

@test "claude local stats-cache fallback renders an explicitly marked estimate" {
  write_claude_local_estimate_inputs
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"C:95%?"* ]]
}

@test "claude estimate ratio falls back safely when CLAUDE_MESSAGE_RATIO is zero" {
  write_claude_local_estimate_inputs
  run bash -c "CLAUDE_MESSAGE_RATIO=0; export CLAUDE_MESSAGE_RATIO; printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"C:95%?"* ]]
}

@test "malformed claude stats-cache falls closed to unknown without stderr leakage" {
  cat > "$STATUSLINE_CLAUDE_CREDS" <<'EOF'
{"claudeAiOauth":{"subscriptionType":"pro","rateLimitTier":"pro"}}
EOF
  printf '{not-json' > "$STATUSLINE_CLAUDE_STATS_CACHE"
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  clean=$(strip_ansi "$output")
  [[ "$clean" == *"C:-%"* ]]
  [[ "$output" != *"jq:"* ]]
}

@test "query_claude_stats guards invalid CLAUDE_MESSAGE_RATIO in adjacent provider helper" {
  HOME="$TMPDIR/home"
  mkdir -p "$HOME/.claude"
  cat > "$HOME/.claude/.credentials.json" <<'EOF'
{"claudeAiOauth":{"subscriptionType":"pro","rateLimitTier":"pro"}}
EOF
  cat > "$HOME/.claude/stats-cache.json" <<EOF
{"dailyActivity":[{"date":"$(date +%F)","messageCount":1500,"sessionCount":3,"toolCallCount":9}]}
EOF
  run bash -c "set -euo pipefail; source '$PROVIDERS'; HOME='$HOME'; export HOME; CLAUDE_MESSAGE_RATIO=0; export CLAUDE_MESSAGE_RATIO; query_claude_stats | jq -r '[.pct_remaining, .source] | @tsv'"
  [ "$status" -eq 0 ]
  [ "$output" = $'95\tstats-cache.json-estimate' ]
}
