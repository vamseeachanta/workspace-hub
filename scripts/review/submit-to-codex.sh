#!/usr/bin/env bash
# submit-to-codex.sh — Submit content to OpenAI Codex CLI for review
# Usage:
#   submit-to-codex.sh --file <path> --prompt <prompt>
#   submit-to-codex.sh --commit <sha> [--prompt <prompt>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RENDERER="${SCRIPT_DIR}/render-structured-review.py"
VALIDATOR="${SCRIPT_DIR}/validate-review-output.sh"
CODEX_TIMEOUT_SECONDS="${CODEX_TIMEOUT_SECONDS:-300}"
CODEX_COMPACT_RETRY_CHARS="${CODEX_COMPACT_RETRY_CHARS:-24000}"

CONTENT_FILE=""
COMMIT_SHA=""
PROMPT=""
WRK_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)   CONTENT_FILE="$2"; shift 2 ;;
    --commit) COMMIT_SHA="$2"; shift 2 ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "$CONTENT_FILE" ]]; then
  if [[ "$CONTENT_FILE" =~ (WRK-[0-9]+) ]]; then
    WRK_ID="${BASH_REMATCH[1]}"
  fi
fi

if [[ -z "$COMMIT_SHA" && -z "$CONTENT_FILE" ]]; then
  echo "ERROR: Provide --file <path> or --commit <sha>" >&2
  exit 1
fi

# Check if codex CLI is available (also check npm global bin)
CODEX_BIN="codex"
if ! command -v codex &>/dev/null; then
  if [[ -x "${HOME}/.npm-global/bin/codex" ]]; then
    CODEX_BIN="${HOME}/.npm-global/bin/codex"
  fi
fi
if ! command -v "$CODEX_BIN" &>/dev/null && [[ ! -x "$CODEX_BIN" ]]; then
  echo "# Codex CLI not found"
  echo "# Install: npm install -g @openai/codex"
  echo "# CODEX REVIEW IS COMPULSORY — install the CLI and retry"
  echo ""
  echo "## Review Prompt"
  echo "$PROMPT"
  echo ""
  echo "## Content to Review"
  echo '```'
  if [[ -n "$CONTENT_FILE" ]]; then
    head -200 "$CONTENT_FILE"
  else
    echo "Commit: $COMMIT_SHA"
  fi
  echo '```'
  exit 2
fi

if [[ -n "$COMMIT_SHA" ]]; then
  # Review a specific git commit
  # codex review --commit <SHA> cannot be combined with positional PROMPT.
  # Codex writes review output to stderr, so capture both streams.
  "$CODEX_BIN" review --commit "$COMMIT_SHA" 2>&1 || {
    echo "# Codex review --commit failed (exit $?)"
    echo "# Commit: $COMMIT_SHA"
  }
else
  # Review file content via codex exec using output-schema + output-last-message
  SCOPE_PREFIX=""
  if [[ -n "$WRK_ID" ]]; then
    SCOPE_PREFIX="WRK in scope: ${WRK_ID}
This review is being run under the active approved work item above.

"
  fi

  CONTENT_TEXT="$(cat "$CONTENT_FILE")"
  FULL_PROMPT="${SCOPE_PREFIX}${PROMPT}

---
CONTENT TO REVIEW:
---

${CONTENT_TEXT}"

  schema_file="$(mktemp)"
  raw_file="$(mktemp)"
  err_file="$(mktemp)"
  rendered_file="$(mktemp)"
  trap 'rm -f "$schema_file" "$raw_file" "$err_file" "$rendered_file"' EXIT

  cat > "$schema_file" <<'EOF'
{
  "type": "object",
  "properties": {
    "verdict": { "type": "string" },
    "summary": { "type": "string" },
    "issues_found": { "type": "array", "items": { "type": "string" } },
    "suggestions": { "type": "array", "items": { "type": "string" } },
    "questions_for_author": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["verdict", "summary", "issues_found", "suggestions", "questions_for_author"],
  "additionalProperties": false
}
EOF

  run_codex_exec() {
    local prompt_text="$1"
    if command -v timeout >/dev/null 2>&1; then
      timeout "$CODEX_TIMEOUT_SECONDS" "$CODEX_BIN" exec "$prompt_text" \
        --skip-git-repo-check \
        --output-schema "$schema_file" \
        --output-last-message "$raw_file" >/dev/null 2>"$err_file"
    else
      "$CODEX_BIN" exec "$prompt_text" \
        --skip-git-repo-check \
        --output-schema "$schema_file" \
        --output-last-message "$raw_file" >/dev/null 2>"$err_file"
    fi
  }

  classify_codex_failure() {
    if [[ -s "$err_file" ]] && rg -qi \
      "(insufficient[_ -]?quota|quota (exceeded|reached)|billing (limit|quota)|payment required|hard limit reached|credits? (exhausted|depleted|remaining:[[:space:]]*0))" \
      "$err_file"; then
      echo "QUOTA"
      return
    fi
    if [[ -s "$err_file" ]] && rg -qi "(timed out|timeout|deadline exceeded)" "$err_file"; then
      echo "TIMEOUT"
      return
    fi
    if [[ -s "$err_file" ]] && rg -qi "(operation not permitted|permission denied|failed to connect|stream disconnected|error sending request)" "$err_file"; then
      echo "TRANSPORT"
      return
    fi
    echo "GENERIC"
  }

  exec_exit=0
  run_codex_exec "$FULL_PROMPT" || exec_exit=$?

  # One compact retry when full payload returns no usable output.
  if [[ "$exec_exit" -ne 0 || ! -s "$raw_file" ]]; then
    compact_text="$(printf '%s' "$CONTENT_TEXT" | head -c "$CODEX_COMPACT_RETRY_CHARS")"
    COMPACT_PROMPT="${SCOPE_PREFIX}${PROMPT}

---
CONTENT TO REVIEW (TRUNCATED FOR PROVIDER RELIABILITY):
---

${compact_text}

[truncated by submit-to-codex compact retry to avoid provider NO_OUTPUT]"
    : > "$raw_file"
    exec_exit=0
    run_codex_exec "$COMPACT_PROMPT" || exec_exit=$?
  fi

  if [[ "$exec_exit" -ne 0 ]]; then
    failure_kind="$(classify_codex_failure)"
    if [[ "$failure_kind" == "QUOTA" ]]; then
      echo "# Codex quota/credits exhausted"
      echo "# Action: refresh usage/credits, then rerun this review."
    elif [[ "$failure_kind" == "TIMEOUT" ]]; then
      echo "# Codex exec timed out (exit $exec_exit)"
      echo "# Action: retry or increase CODEX_TIMEOUT_SECONDS."
    elif [[ "$failure_kind" == "TRANSPORT" ]]; then
      echo "# Codex transport/network failure (exit $exec_exit)"
      echo "# Action: run outside restricted sandbox or restore provider connectivity."
    else
      echo "# Codex exec failed (exit $exec_exit)"
    fi
    echo "# File: $CONTENT_FILE"
    if [[ -s "$err_file" ]]; then
      echo "# STDERR:"
      sed -n '1,20p' "$err_file"
    fi
    exit 0
  fi

  if python3 "$RENDERER" --provider codex --input "$raw_file" > "$rendered_file" 2>/dev/null \
    && [[ "$("$VALIDATOR" "$rendered_file")" == "VALID" ]]; then
    cat "$rendered_file"
  else
    if [[ -s "$raw_file" ]]; then
      cat "$raw_file"
    else
      echo "# Codex returned NO_OUTPUT"
    fi
  fi
fi
