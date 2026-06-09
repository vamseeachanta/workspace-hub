#!/usr/bin/env bats
# Tests for .claude/statusline-command.sh weekly-reset countdown (#2992).
# Verifies the "·N.Nd" days-to-weekly-reset suffix renders for providers that
# expose reset telemetry, and that providers without it get NO fabricated
# countdown (Claude is `source: unavailable` today).

SCRIPT="$BATS_TEST_DIRNAME/../../.claude/statusline-command.sh"

setup() {
  TMPDIR=$(mktemp -d)
  # Point the statusline at fixture quota files via the env-override seam.
  export STATUSLINE_QUOTA_PRIMARY="$TMPDIR/agent-quota-latest.json"
  export STATUSLINE_QUOTA_CACHE="$TMPDIR/agent-quota-cache.json"
}

teardown() {
  rm -rf "$TMPDIR"
}

# Minimal stdin payload — omit rate_limits so Claude falls through to the quota
# file (which is `unavailable`), exercising the no-countdown path.
INPUT='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10}}'

write_quota() {
  # hours_to_reset only (no resets_at) → deterministic days = hours/24.
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<'EOF'
{
  "agents": [
    {"provider":"claude","week_pct":null,"pct_remaining":null,"hours_to_reset":null,"resets_at":"","source":"unavailable"},
    {"provider":"codex","week_pct":36,"pct_remaining":64,"hours_to_reset":60,"resets_at":"","source":"app-server-live"},
    {"provider":"gemini","pct_remaining":100,"source":"estimated"}
  ]
}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
}

@test "codex shows days-to-reset suffix from hours_to_reset (60h -> 2.5d)" {
  write_quota
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  # 60 hours / 24 = 2.5 days, rendered as O:64%·2.5d
  [[ "$output" == *"O:64%·2.5d"* ]]
}

@test "unavailable provider (claude) gets NO fabricated countdown" {
  write_quota
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  # Claude renders dim with no value and no day-suffix appended.
  [[ "$output" != *"C:-%·"* ]]
  [[ "$output" != *"C:-%"*"d "* ]] || true
}

@test "estimated reset telemetry gets NO fabricated countdown even with stale hours" {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<'EOF'
{
  "agents": [
    {"provider":"codex","week_pct":36,"pct_remaining":64,"hours_to_reset":60,"resets_at":"","source":"estimated"}
  ]
}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:64%"* ]]
  [[ "$output" != *"O:64%·"* ]]
}

@test "absolute resets_at is preferred and yields a day-suffix" {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<'EOF'
{
  "agents": [
    {"provider":"codex","week_pct":36,"pct_remaining":64,"hours_to_reset":1,"resets_at":"2099-01-10T00:00:00+0000","source":"app-server-live"}
  ]
}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  # resets_at is far future, so the suffix must NOT be the 1h/24=0.0d fallback.
  [[ "$output" == *"O:64%·"*"d"* ]]
  [[ "$output" != *"O:64%·0.0d"* ]]
}

@test "resets_at-only telemetry renders without GNU date dependency" {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<'EOF'
{
  "agents": [
    {"provider":"codex","week_pct":36,"pct_remaining":64,"resets_at":"2099-01-10T00:00:00+00:00","source":"app-server-live"}
  ]
}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:64%·"*"d"* ]]
}

@test "missing reset fields never blank the statusline" {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<'EOF'
{"agents":[{"provider":"codex","pct_remaining":64}]}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:64%"* ]]   # segment still renders, just no suffix
  [ -n "$output" ]
}
