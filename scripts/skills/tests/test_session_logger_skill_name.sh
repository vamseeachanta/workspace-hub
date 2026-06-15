#!/usr/bin/env bash
# TDD for #3112 BUG-1 (emit step): session-logger.sh must record skill_name
# (rel-path under .claude/skills) when a SKILL.md is Read, so the scanner has
# events to count. Non-skill Reads must NOT get a skill_name (fast-exit).
set -uo pipefail
WS="$(git rev-parse --show-toplevel)"
HOOK="$WS/.claude/hooks/session-logger.sh"
fail=0

run_hook() { # $1=input json -> echoes last log line
  local tmp; tmp="$(mktemp -d)"
  mkdir -p "$tmp/.claude/state/sessions"
  echo "$1" | WORKSPACE_HUB="$tmp" CLAUDE_SESSION_LOGGING=true bash "$HOOK" post >/dev/null 2>&1
  tail -1 "$tmp/.claude/state/sessions/"session_*.jsonl 2>/dev/null
  rm -rf "$tmp"
}

# 1) Read of a SKILL.md -> skill_name = rel-path
line=$(run_hook '{"tool_name":"Read","tool_input":{"file_path":"/x/.claude/skills/email/gmail-triage/SKILL.md"},"session_id":"s1"}')
got=$(echo "$line" | jq -r '.skill_name // "MISSING"' 2>/dev/null)
if [ "$got" = "email/gmail-triage" ]; then echo "PASS: skill_name from SKILL.md Read"; else echo "FAIL: expected email/gmail-triage, got '$got'"; fail=1; fi

# 2) Read of a non-skill file -> no skill_name
line=$(run_hook '{"tool_name":"Read","tool_input":{"file_path":"/x/src/main.py"},"session_id":"s1"}')
got=$(echo "$line" | jq -r '.skill_name // "ABSENT"' 2>/dev/null)
if [ "$got" = "ABSENT" ]; then echo "PASS: non-skill Read has no skill_name"; else echo "FAIL: non-skill Read got skill_name '$got'"; fail=1; fi

exit $fail
