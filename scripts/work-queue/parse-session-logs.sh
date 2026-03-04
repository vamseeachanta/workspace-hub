#!/usr/bin/env bash
# parse-session-logs.sh — Read and summarise orchestrator session logs for given WRK IDs
#
# Usage:
#   bash scripts/work-queue/parse-session-logs.sh WRK-1002 WRK-1003 WRK-1004
#
# Outputs a markdown log-review table to stdout and (optionally) to
# assets/WRK-<last-arg>/session-log-review.md when WRK IDs are supplied.
#
# Handles:
#   - Claude JSONL:  logs/orchestrator/claude/session_YYYYMMDD.jsonl
#   - Codex  text:   logs/orchestrator/codex/session_YYYYMMDD.log
#   - Gemini text:   logs/orchestrator/gemini/session_YYYYMMDD.log
#   - Native stores: ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
#                    ~/.gemini/tmp/<project>/chats/session-*.json
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
LOG_BASE="${REPO_ROOT}/logs/orchestrator"
TODAY="$(date +%Y%m%d)"
WRKS=("$@")

# ── helpers ────────────────────────────────────────────────────────────────────

present() { [ -n "$1" ] && echo "✅" || echo "❌"; }

count_jsonl_events() {
  local file="$1" event="$2"
  [ -f "$file" ] && grep -c "\"event\":\"${event}\"" "$file" 2>/dev/null || echo 0
}

count_text_pattern() {
  local file="$1" pattern="$2"
  [ -f "$file" ] && grep -c "${pattern}" "$file" 2>/dev/null || echo 0
}

jsonl_duration() {
  local file="$1"
  [ -f "$file" ] || { echo "n/a"; return; }
  local first last
  first=$(grep -m1 '"ts":' "$file" | grep -oP '"ts":"\K[^"]+' 2>/dev/null || true)
  last=$(grep '"ts":' "$file" | tail -1 | grep -oP '"ts":"\K[^"]+' 2>/dev/null || true)
  [ -n "$first" ] && [ -n "$last" ] && echo "${first} → ${last}" || echo "n/a"
}

text_duration() {
  local file="$1"
  [ -f "$file" ] || { echo "n/a"; return; }
  local first last
  first=$(grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}' "$file" 2>/dev/null | head -1 || true)
  last=$(grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}' "$file" 2>/dev/null | tail -1 || true)
  [ -n "$first" ] && [ -n "$last" ] && echo "${first} → ${last}" || echo "n/a"
}

# ── find latest log file for a provider ────────────────────────────────────────

latest_log() {
  local provider="$1" ext="$2"
  local dir="${LOG_BASE}/${provider}"
  [ -d "$dir" ] || { echo ""; return; }
  ls -t "${dir}/session_"*".${ext}" 2>/dev/null | head -1 || echo ""
}

latest_native_codex() {
  ls -t ~/.codex/sessions/*/*/rollout-*.jsonl 2>/dev/null | head -1 || echo ""
}

latest_native_gemini() {
  local proj
  proj=$(basename "${REPO_ROOT}")
  ls -t ~/.gemini/tmp/"${proj}"/chats/session-*.json 2>/dev/null | head -1 || \
  ls -t ~/.gemini/tmp/*/chats/session-*.json 2>/dev/null | head -1 || echo ""
}

# ── per-provider summary ────────────────────────────────────────────────────────

summarise_claude() {
  local wrk="$1"
  local log
  log=$(latest_log claude jsonl)
  local present_flag tool_count session_open load_assess wrk_ref errors duration

  if [ -n "$log" ] && [ -f "$log" ]; then
    present_flag="✅ $(basename "$log")"
    session_open=$(count_jsonl_events "$log" "session_open")
    load_assess=$(count_jsonl_events "$log" "load_assessment")
    wrk_ref=$(grep -c "\"${wrk}\"" "$log" 2>/dev/null || echo 0)
    tool_count=$(grep -c '"type":"tool_use"' "$log" 2>/dev/null || echo 0)
    errors=$(grep -c '"level":"error"' "$log" 2>/dev/null || echo 0)
    duration=$(jsonl_duration "$log")
  else
    present_flag="❌ missing"
    session_open=0; load_assess=0; wrk_ref=0; tool_count=0; errors=0; duration="n/a"
  fi

  echo "| Claude | ${present_flag} | ${session_open} | ${load_assess} | ${wrk_ref} | ${tool_count} | ${errors} | ${duration} |"
}

summarise_codex() {
  local wrk="$1"
  local log native
  log=$(latest_log codex log)
  native=$(latest_native_codex)
  local present_flag tool_count wrk_ref errors duration gate_events

  if [ -n "$log" ] && [ -f "$log" ]; then
    present_flag="✅ $(basename "$log")"
    wrk_ref=$(grep -c "${wrk}" "$log" 2>/dev/null || echo 0)
    tool_count=$(grep -c "^TOOL\|tool_call\|function_call" "$log" 2>/dev/null || echo 0)
    errors=$(grep -c "^ERROR\|error:" "$log" 2>/dev/null || echo 0)
    gate_events=$(grep -c "gate\|gatepass\|plan_gate\|tdd_gate" "$log" 2>/dev/null || echo 0)
    duration=$(text_duration "$log")
  else
    present_flag="❌ missing (native: $([ -n "$native" ] && echo "✅" || echo "❌"))"
    wrk_ref=0; tool_count=0; errors=0; gate_events=0; duration="n/a"
  fi

  echo "| Codex  | ${present_flag} | n/a | n/a | ${wrk_ref} | ${tool_count} | ${errors} | ${duration} |"
}

summarise_gemini() {
  local wrk="$1"
  local log native
  log=$(latest_log gemini log)
  native=$(latest_native_gemini)
  local present_flag tool_count wrk_ref errors duration

  if [ -n "$log" ] && [ -f "$log" ]; then
    present_flag="✅ $(basename "$log")"
    wrk_ref=$(grep -c "${wrk}" "$log" 2>/dev/null || echo 0)
    tool_count=$(grep -c "^TOOL\|tool_use\|function_call" "$log" 2>/dev/null || echo 0)
    errors=$(grep -c "^ERROR\|error:" "$log" 2>/dev/null || echo 0)
    duration=$(text_duration "$log")
  else
    present_flag="❌ missing (native: $([ -n "$native" ] && echo "✅" || echo "❌"))"
    wrk_ref=0; tool_count=0; errors=0; duration="n/a"
  fi

  echo "| Gemini | ${present_flag} | n/a | n/a | ${wrk_ref} | ${tool_count} | ${errors} | ${duration} |"
}

# ── main ───────────────────────────────────────────────────────────────────────

main() {
  local output=""
  output+="# Session Log Review\n"
  output+="generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)\n"
  output+="wrks: ${WRKS[*]:-all}\n\n"

  for wrk in "${WRKS[@]:-ALL}"; do
    [ "$wrk" = "ALL" ] && wrk=""
    output+="## ${wrk:-All WRKs}\n\n"
    output+="| Provider | Log Present | session_open | load_assess | WRK refs | Tool calls | Errors | Duration |\n"
    output+="|----------|-------------|-------------|------------|----------|------------|--------|----------|\n"
    output+="$(summarise_claude "$wrk")\n"
    output+="$(summarise_codex  "$wrk")\n"
    output+="$(summarise_gemini "$wrk")\n"
    output+="\n"
  done

  printf "%b" "$output"

  # Write to assets dir of last WRK if supplied
  if [ "${#WRKS[@]}" -gt 0 ]; then
    local last_wrk="${WRKS[-1]}"
    local asset_dir="${REPO_ROOT}/.claude/work-queue/assets/${last_wrk}"
    mkdir -p "$asset_dir"
    printf "%b" "$output" > "${asset_dir}/session-log-review.md"
    echo "→ Written to ${asset_dir}/session-log-review.md" >&2
  fi
}

main
