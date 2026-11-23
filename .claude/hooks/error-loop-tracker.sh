#!/usr/bin/env bash
# error-loop-tracker.sh — PostToolUse hook for consecutive error detection
# Issue: #2056 — Wire error-loop-breaker into session governance hooks
#
# Tracks consecutive tool errors by hashing error signatures.
# When the same error repeats N times consecutively, the PreToolUse
# session-governor-check.sh reads the count and triggers a hard stop.
#
# State files (in .claude/state/session-governor/):
#   consecutive-error-count  — current consecutive identical error count
#   last-error-hash          — hash of the last error (for dedup)
#
# Protocol: PostToolUse hooks receive JSON on stdin with tool_name,
# tool_input, and tool_response (when available). The tool_response
# may contain is_error, stderr, stdout, or content fields.
#
# This hook is non-blocking and never emits stdout (no decision influence).
# All output goes to stderr for operator visibility.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
WS="${WORKSPACE_HUB:-$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)}"
STATE_DIR="$WS/.claude/state/session-governor"
ERROR_COUNT_FILE="$STATE_DIR/consecutive-error-count"
ERROR_HASH_FILE="$STATE_DIR/last-error-hash"
ERROR_DATE_FILE="$STATE_DIR/error-date"

mkdir -p "$STATE_DIR" 2>/dev/null

# -- Reset on new day (same pattern as session-governor-check.sh) --
TODAY=$(date +%Y%m%d)
if [[ -f "$ERROR_DATE_FILE" ]]; then
  STORED_DATE=$(cat "$ERROR_DATE_FILE" 2>/dev/null) || STORED_DATE=""
  if [[ "$STORED_DATE" != "$TODAY" ]]; then
    echo "0" > "$ERROR_COUNT_FILE"
    echo "" > "$ERROR_HASH_FILE"
    echo "$TODAY" > "$ERROR_DATE_FILE"
  fi
else
  echo "$TODAY" > "$ERROR_DATE_FILE"
fi

# -- Read stdin (PostToolUse JSON) --
INPUT=""
if [[ ! -t 0 ]]; then
  INPUT=$(cat 2>/dev/null) || INPUT=""
fi
[[ -z "$INPUT" ]] && exit 0

# -- Check if jq is available (required for JSON parsing) --
if ! command -v jq &>/dev/null; then
  exit 0
fi

# -- Detect error in tool response --
# Claude Code PostToolUse provides tool_response with is_error flag,
# or we can detect errors from content patterns.
IS_ERROR="false"
ERROR_SIG=""

# Check tool_response.is_error first (most reliable)
RESP_IS_ERROR=$(echo "$INPUT" | jq -r '.tool_response.is_error // false' 2>/dev/null) || RESP_IS_ERROR="false"
if [[ "$RESP_IS_ERROR" == "true" ]]; then
  IS_ERROR="true"
  # Build error signature from response content for dedup
  ERROR_SIG=$(echo "$INPUT" | jq -r '
    (.tool_name // "") + "|" +
    (.tool_response.content // .tool_response.stderr // .tool_response.stdout // "" | tostring | .[0:200])
  ' 2>/dev/null) || ERROR_SIG=""
fi

# Fallback: check tool_response content/stderr for error patterns
if [[ "$IS_ERROR" == "false" ]]; then
  RESPONSE_TEXT=$(echo "$INPUT" | jq -r '
    (.tool_response.stderr // "") + " " + (.tool_response.content // "" | tostring | .[0:500])
  ' 2>/dev/null) || RESPONSE_TEXT=""

  if [[ -n "$RESPONSE_TEXT" && "$RESPONSE_TEXT" != " " ]]; then
    # Check for common error indicators (case-insensitive)
    if echo "$RESPONSE_TEXT" | grep -qiE '(^Error:|^FATAL:|Traceback \(most recent|panic:|SyntaxError:|TypeError:|NameError:|ImportError:|ModuleNotFoundError:|FileNotFoundError:|PermissionError:|ConnectionError:)'; then
      IS_ERROR="true"
      TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null) || TOOL_NAME="unknown"
      ERROR_SIG="${TOOL_NAME}|$(echo "$RESPONSE_TEXT" | head -c 200)"
    fi
  fi

  # Check Bash tool exit code if available
  EXIT_CODE=$(echo "$INPUT" | jq -r '.tool_response.exit_code // 0' 2>/dev/null) || EXIT_CODE="0"
  if [[ "$EXIT_CODE" != "0" && "$EXIT_CODE" != "null" && "$EXIT_CODE" != "" ]]; then
    IS_ERROR="true"
    if [[ -z "$ERROR_SIG" ]]; then
      TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null) || TOOL_NAME="unknown"
      CMD=$(echo "$INPUT" | jq -r '.tool_input.command // "" | .[0:100]' 2>/dev/null) || CMD=""
      ERROR_SIG="${TOOL_NAME}|exit:${EXIT_CODE}|${CMD}"
    fi
  fi
fi

# -- Update consecutive error state --
if [[ "$IS_ERROR" == "true" && -n "$ERROR_SIG" ]]; then
  # Hash the error signature for comparison
  CURRENT_HASH=$(echo "$ERROR_SIG" | md5sum | cut -d' ' -f1)
  PREV_HASH=""
  if [[ -f "$ERROR_HASH_FILE" ]]; then
    PREV_HASH=$(cat "$ERROR_HASH_FILE" 2>/dev/null) || PREV_HASH=""
  fi

  if [[ "$CURRENT_HASH" == "$PREV_HASH" ]]; then
    # Same error repeating — increment counter
    CURRENT_COUNT=0
    if [[ -f "$ERROR_COUNT_FILE" ]]; then
      CURRENT_COUNT=$(cat "$ERROR_COUNT_FILE" 2>/dev/null) || CURRENT_COUNT=0
    fi
    CURRENT_COUNT=$((CURRENT_COUNT + 1))
    echo "$CURRENT_COUNT" > "$ERROR_COUNT_FILE"
    echo "[error-loop-tracker] Same error repeated: ${CURRENT_COUNT}x consecutive" >&2
  else
    # Different error — reset counter to 1, update hash
    echo "1" > "$ERROR_COUNT_FILE"
    echo "$CURRENT_HASH" > "$ERROR_HASH_FILE"
  fi
else
  # Successful tool call — reset consecutive error counter
  echo "0" > "$ERROR_COUNT_FILE"
  echo "" > "$ERROR_HASH_FILE"
fi

exit 0
