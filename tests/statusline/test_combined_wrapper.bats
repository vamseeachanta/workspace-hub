#!/usr/bin/env bats
# Tests for .claude/statusline-combined.sh (#2893) — the wrapper that composes
# the vendored GSD statusline with the AI-usage tail (quota + #2992 weekly-reset
# countdown) from statusline-command.sh, so the reset shows in workspace-hub.

SCRIPT="$BATS_TEST_DIRNAME/../../.claude/statusline-combined.sh"

setup() {
  TMPDIR=$(mktemp -d)
  export STATUSLINE_QUOTA_PRIMARY="$TMPDIR/q.json"
  export STATUSLINE_QUOTA_CACHE="$TMPDIR/qc.json"
  cat > "$STATUSLINE_QUOTA_PRIMARY" <<'EOF'
{"agents":[
  {"provider":"claude","week_pct":null,"pct_remaining":null,"hours_to_reset":null,"resets_at":"","source":"unavailable"},
  {"provider":"codex","week_pct":36,"pct_remaining":64,"hours_to_reset":60,"resets_at":"","source":"app-server-live"},
  {"provider":"gemini","pct_remaining":100,"source":"estimated"}
]}
EOF
  # #3034: stamp the fixture fresh so this pre-staleness test keeps exercising
  # the original (unmarked) rendering.
  jq --arg ts "$(date -Iseconds)" '. + {timestamp: $ts}' "$STATUSLINE_QUOTA_PRIMARY" \
    > "$STATUSLINE_QUOTA_PRIMARY.tmp" && mv "$STATUSLINE_QUOTA_PRIMARY.tmp" "$STATUSLINE_QUOTA_PRIMARY"
  cp "$STATUSLINE_QUOTA_PRIMARY" "$STATUSLINE_QUOTA_CACHE"
}

teardown() { rm -rf "$TMPDIR"; }

INPUT='{"model":{"display_name":"Opus 4.8"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0.42},"context_window":{"used_percentage":15}}'

@test "combined output carries the usage tail with the weekly-reset countdown" {
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  clean=$(printf '%s' "$output" | sed 's/\x1b\[[0-9;]*m//g')   # strip ANSI colors
  [[ "$clean" == *"O:64%·2.5d"* ]]   # 60h/24 = 2.5d, via reused reset_days
  [[ "$clean" == *"ctx:15%"* ]]
}

@test "combined output includes the GSD base (model) and the joiner" {
  run bash -c "printf '%s' '$INPUT' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Opus 4.8"* ]]     # from the GSD statusline base
  [[ "$output" == *" │ "* ]]          # both parts non-empty -> separator present
}

@test "never blanks even with minimal input" {
  run bash -c "printf '%s' '{\"model\":{\"display_name\":\"Sonnet\"}}' | bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  [ -n "$output" ]
}

@test "usage tail alone renders when the GSD base produces nothing" {
  # Point the wrapper's GSD lookup at an empty hooks dir via a copy in TMPDIR so
  # gsd-statusline.js is absent; the wrapper must still emit the usage tail.
  cp "$SCRIPT" "$TMPDIR/statusline-combined.sh"
  cp "$BATS_TEST_DIRNAME/../../.claude/statusline-command.sh" "$TMPDIR/statusline-command.sh"
  run bash -c "printf '%s' '$INPUT' | bash '$TMPDIR/statusline-combined.sh'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"O:64%·2.5d"* ]]   # tail still present
  [[ "$output" != *" │ "* ]]          # no joiner since GSD half was empty
}
