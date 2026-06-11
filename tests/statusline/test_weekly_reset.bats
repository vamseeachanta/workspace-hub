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

# #3034: quota files carry a freshness timestamp; stamp fixtures fresh so these
# pre-staleness tests keep exercising their original (unmarked) rendering.
stamp_fresh() {
  local f
  for f in "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"; do
    [ -f "$f" ] || continue
    jq --arg ts "$(date -Iseconds)" '. + {timestamp: $ts}' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  done
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
  stamp_fresh
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  # 60 hours / 24 = 2.5 days, rendered as O:64%·2.5d
  [[ "$output" == *"O:64%·2.5d"* ]]
}

@test "unavailable provider (claude) gets NO fabricated countdown" {
  write_quota
  stamp_fresh
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  # Claude renders dim with no value and no day-suffix appended (any day
  # suffix would start with "·" immediately after the "%").
  [[ "$output" != *"C:-%·"* ]]
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
  stamp_fresh
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
  stamp_fresh
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
  stamp_fresh
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:64%·"*"d"* ]]
}

@test "claude shows days-to-reset from session rate_limits resets_at" {
  write_quota
  in='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10},"rate_limits":{"seven_day":{"used_percentage":37,"resets_at":"2099-01-10T00:00:00Z"}}}'
  stamp_fresh
  run bash -c "printf '%s' '$in' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  # 100-37=63% remaining, with a day-countdown sourced from the session JSON
  # (the quota file's claude entry is source:unavailable and must not matter).
  [[ "$output" == *"C:63%·"*"d"* ]]
}

@test "claude session weekly pct without resets_at gets no fabricated countdown" {
  write_quota
  in='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10},"rate_limits":{"seven_day":{"used_percentage":37}}}'
  stamp_fresh
  run bash -c "printf '%s' '$in' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"C:63%"* ]]
  [[ "$output" != *"C:63%·"* ]]
}

@test "session resets_at without weekly pct gets no countdown on unknown C" {
  write_quota
  # resets_at present but used_percentage absent: pairing a countdown with an
  # unknown (or quota-file-sourced) percentage would mix telemetry sources, so
  # the C segment must stay bare (codex r2 finding on PR #3021).
  in='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10},"rate_limits":{"seven_day":{"resets_at":"2099-01-10T00:00:00Z"}}}'
  stamp_fresh
  run bash -c "printf '%s' '$in' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" != *"C:-%·"* ]]
}

@test "malformed session resets_at never blanks the statusline" {
  write_quota
  in='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10},"rate_limits":{"seven_day":{"used_percentage":37,"resets_at":"not-a-timestamp"}}}'
  stamp_fresh
  run bash -c "printf '%s' '$in' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"C:63%"* ]]
  [[ "$output" != *"C:63%·"* ]]
}

@test "missing reset fields never blank the statusline" {
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<'EOF'
{"agents":[{"provider":"codex","pct_remaining":64}]}
EOF
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
  stamp_fresh
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:64%"* ]]   # segment still renders, just no suffix
  [ -n "$output" ]
}
