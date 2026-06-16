#!/usr/bin/env bats
# Tests for .claude/statusline-command.sh quota-file staleness handling (#3034).
# The quota files carry a top-level `timestamp` (query-quota.sh). The statusline
# must source each displayed value from the freshest file and append a `?`
# marker to any component whose source file is stale (older than
# STATUSLINE_QUOTA_MAX_AGE_HOURS, default 6) or undatable. Root cause: on
# ace-linux-2 the git-tracked primary is a propagated snapshot that read 79%
# codex remaining while the live number was 29% (2026-06-10).

SCRIPT="$BATS_TEST_DIRNAME/../../.claude/statusline-command.sh"

setup() {
  TMPDIR=$(mktemp -d)
  export STATUSLINE_QUOTA_PRIMARY="$TMPDIR/agent-quota-latest.json"
  export STATUSLINE_QUOTA_CACHE="$TMPDIR/agent-quota-cache.json"
  export STATUSLINE_GEMINI_SNAPSHOT="$TMPDIR/agy-usage-snapshot.json"
  export STATUSLINE_CLAUDE_STATS_CACHE="$TMPDIR/no-stats-cache.json"
  export STATUSLINE_CLAUDE_CREDS="$TMPDIR/no-claude-creds.json"
  export GEMINI_ERROR_DIR="$TMPDIR"
  cat > "$STATUSLINE_GEMINI_SNAPSHOT" <<EOF
{
  "captured_at": "$(iso_at_age_hours 0.1)",
  "gemini": {
    "weekly": {"pct_remaining": 100, "reset_hours": 159.5},
    "five_hour": {"pct_remaining": 100, "reset_hours": 3.2}
  }
}
EOF
}

teardown() {
  rm -rf "$TMPDIR"
}

# stdin payload without rate_limits → Claude falls through to the quota files.
INPUT_NO_LIVE='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10}}'
# stdin payload WITH live 7-day rate limits (used 29% → C:71%) but no resets_at
# → Claude pct is live while any countdown would be file-sourced.
INPUT_LIVE_PCT='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0},"context_window":{"used_percentage":10},"rate_limits":{"seven_day":{"used_percentage":29}}}'

iso_at_age_hours() {  # emit an ISO timestamp N hours in the past
  python3 -c "import datetime,sys; print((datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(hours=float(sys.argv[1]))).isoformat())" "$1"
}

write_file() {  # write_file <path> <age_hours|none> <agents-json>
  local path="$1" age="$2" agents="$3" ts_field=""
  if [[ "$age" != "none" ]]; then
    ts_field="\"timestamp\": \"$(iso_at_age_hours "$age")\","
  fi
  cat > "$path" <<EOF
{
  $ts_field
  "agents": $agents
}
EOF
}

CODEX_GEMINI='[{"provider":"codex","week_pct":21,"pct_remaining":79,"hours_to_reset":60,"resets_at":"","source":"app-server-live"},{"provider":"gemini","week_pct":0,"pct_remaining":100,"source":"app-server-live"}]'
CACHE_FRESH_CODEX='[{"provider":"codex","pct_remaining":29,"hours_to_reset":12,"resets_at":"","source":"local-session-rate-limits"}]'

@test "stale primary, no cache: file-sourced codex carries the ? marker" {
  write_file "$STATUSLINE_QUOTA_PRIMARY" 72 "$CODEX_GEMINI"
  rm -f "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT_NO_LIVE' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:79%?"* ]]
  [[ "$output" == *"G:100%·6.6d"* ]]  # Gemini is independently sourced from fresh agy snapshot
  [[ "$output" != *"G:100%?"* ]]
}

@test "fresh primary: no markers, rendering matches pre-change shape" {
  write_file "$STATUSLINE_QUOTA_PRIMARY" 0.1 "$CODEX_GEMINI"
  rm -f "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT_NO_LIVE' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:79%·2.5d"* ]]   # 60h/24 suffix intact, no ? anywhere in it
  [[ "$output" == *"G:100%"* ]]
  [[ "$output" != *"?"* ]]
}

@test "missing timestamp counts as stale (undatable = visible doubt)" {
  write_file "$STATUSLINE_QUOTA_PRIMARY" none "$CODEX_GEMINI"
  rm -f "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT_NO_LIVE' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:79%?"* ]]
}

@test "unparseable timestamp counts as stale" {
  write_file "$STATUSLINE_QUOTA_PRIMARY" 0.1 "$CODEX_GEMINI"
  python3 - "$STATUSLINE_QUOTA_PRIMARY" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["timestamp"] = "not-a-date"
json.dump(d, open(p, "w"))
PY
  rm -f "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT_NO_LIVE' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:79%?"* ]]
}

@test "fresher cache wins over stale primary (per-value, unmarked)" {
  write_file "$STATUSLINE_QUOTA_PRIMARY" 72 "$CODEX_GEMINI"
  write_file "$STATUSLINE_QUOTA_CACHE" 0.1 "$CACHE_FRESH_CODEX"
  run bash -c "printf '%s' '$INPUT_NO_LIVE' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:29%·0.5d"* ]]   # value AND countdown from the fresh cache (12h/24)
  [[ "$output" != *"O:29%?"* ]]       # percentage unmarked
  [[ "$output" != *"O:29%·0.5d?"* ]]  # countdown unmarked too (freshest-file-first)
  [[ "$output" == *"G:100%·6.6d"* ]]  # Gemini is independently sourced from fresh agy snapshot
  [[ "$output" != *"G:100%?"* ]]
}

@test "claude live percentage stays unmarked while file-sourced countdown is marked" {
  # claude entry only in the stale primary, carrying reset telemetry
  write_file "$STATUSLINE_QUOTA_PRIMARY" 72 '[{"provider":"claude","week_pct":50,"pct_remaining":50,"hours_to_reset":48,"resets_at":"","source":"app-server-live"},{"provider":"codex","week_pct":21,"pct_remaining":79,"source":"app-server-live"}]'
  rm -f "$STATUSLINE_QUOTA_CACHE"
  run bash -c "printf '%s' '$INPUT_LIVE_PCT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"C:71%"* ]]        # live 100-29, NOT the file's 50
  [[ "$output" != *"C:71%?"* ]]       # live pct unmarked
  [[ "$output" == *"C:71%·2.0d?"* ]]  # 48h/24 countdown from stale file → marked
}

@test "threshold env is bounds-validated: huge value cannot disable marking" {
  write_file "$STATUSLINE_QUOTA_PRIMARY" 72 "$CODEX_GEMINI"
  rm -f "$STATUSLINE_QUOTA_CACHE"
  STATUSLINE_QUOTA_MAX_AGE_HOURS=999999 run bash -c \
    "STATUSLINE_QUOTA_MAX_AGE_HOURS=999999; export STATUSLINE_QUOTA_MAX_AGE_HOURS; printf '%s' '$INPUT_NO_LIVE' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:79%?"* ]]       # >168 falls back to default 6h → still stale
}

@test "threshold env: non-numeric falls back to default; small valid value honored" {
  write_file "$STATUSLINE_QUOTA_PRIMARY" 1 "$CODEX_GEMINI"
  rm -f "$STATUSLINE_QUOTA_CACHE"
  run bash -c "STATUSLINE_QUOTA_MAX_AGE_HOURS=banana; export STATUSLINE_QUOTA_MAX_AGE_HOURS; printf '%s' '$INPUT_NO_LIVE' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" != *"O:79%?"* ]]       # 1h-old file fresh under default 6h
  run bash -c "STATUSLINE_QUOTA_MAX_AGE_HOURS=0.5; export STATUSLINE_QUOTA_MAX_AGE_HOURS; printf '%s' '$INPUT_NO_LIVE' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:79%?"* ]]       # 1h-old file stale under 0.5h threshold
}
