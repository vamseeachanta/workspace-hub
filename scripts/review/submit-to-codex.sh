#!/usr/bin/env bash
# submit-to-codex.sh — Submit content to OpenAI Codex CLI for review
# Usage:
#   submit-to-codex.sh --file <path> --prompt <prompt>
#   submit-to-codex.sh --commit <sha> [--prompt <prompt>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)}"
RENDERER="${SCRIPT_DIR}/render-structured-review.py"
VALIDATOR="${SCRIPT_DIR}/validate-review-output.sh"
CODEX_TIMEOUT_SECONDS="${CODEX_TIMEOUT_SECONDS:-300}"
CODEX_COMPACT_RETRY_CHARS="${CODEX_COMPACT_RETRY_CHARS:-24000}"
CODEX_MAX_PROMPT_CHARS="${CODEX_MAX_PROMPT_CHARS:-120000}"

CONTENT_FILE=""
COMMIT_SHA=""
PROMPT=""
WRK_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      [[ $# -ge 2 ]] || { echo "ERROR: --file requires a value" >&2; exit 1; }
      CONTENT_FILE="$2"; shift 2
      ;;
    --commit)
      [[ $# -ge 2 ]] || { echo "ERROR: --commit requires a value" >&2; exit 1; }
      COMMIT_SHA="$2"; shift 2
      ;;
    --prompt)
      [[ $# -ge 2 ]] || { echo "ERROR: --prompt requires a value" >&2; exit 1; }
      PROMPT="$2"; shift 2
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "$CONTENT_FILE" ]]; then
  if [[ "$CONTENT_FILE" =~ (WRK-[0-9]+) ]]; then
    WRK_ID="${BASH_REMATCH[1]}"
  fi
fi

# Secondary iteration cap guard (prevents direct invocations bypassing cross-review.sh)
if [[ -n "$WRK_ID" && -n "$REPO_ROOT" ]]; then
  _iter_file="${REPO_ROOT}/.claude/work-queue/assets/${WRK_ID}/review-iteration.yaml"
  if [[ -f "$_iter_file" ]]; then
    _iter_count="$(awk -F': ' '/^iteration:/ {print $2+0; exit}' "$_iter_file")"
    if [[ "$_iter_count" -ge 3 ]]; then
      echo "# REVIEW_ITERATION_CAP_EXCEEDED: ${WRK_ID} has used ${_iter_count}/3 review passes." >&2
      echo "# No further review passes accepted. Resolve findings and close the WRK." >&2
      exit 1
    fi
  fi
fi

# Orchestrator log: unified cross-agent log directory
ORCH_LOG_FILE=""
if [[ -n "$REPO_ROOT" ]]; then
  _ts="$(date -u +%Y%m%dT%H%M%SZ)"
  _tag="${WRK_ID:-unknown}"
  _uniq="$$-${RANDOM}"
  ORCH_LOG_FILE="${REPO_ROOT}/logs/orchestrator/codex/${_tag}-${_ts}-${_uniq}.log"
  ( mkdir -p "$(dirname "$ORCH_LOG_FILE")" ) 2>/dev/null || true
fi

if [[ -z "$COMMIT_SHA" && -z "$CONTENT_FILE" ]]; then
  echo "ERROR: Provide --file <path> or --commit <sha>" >&2
  exit 1
fi

# Check if codex CLI is available (also check npm global bin)
CODEX_BIN="${CODEX_BIN:-codex}"
if ! command -v codex &>/dev/null; then
  if [[ "$CODEX_BIN" == "codex" && -x "${HOME}/.npm-global/bin/codex" ]]; then
    CODEX_BIN="${HOME}/.npm-global/bin/codex"
  fi
fi
if ! command -v "$CODEX_BIN" &>/dev/null && [[ ! -x "$CODEX_BIN" ]]; then
  echo "# Codex CLI not found"
  echo "# Install: npm install -g @openai/codex"
  echo "# CODEX REVIEW IS COMPULSORY — install the CLI and retry"
  echo ""
  echo "## Review Context"
  if [[ -n "$CONTENT_FILE" ]]; then
    file_size="$(wc -c < "$CONTENT_FILE" 2>/dev/null | tr -d ' ' || echo "unknown")"
    echo "- File: $CONTENT_FILE"
    echo "- Size: ${file_size} bytes"
  else
    echo "- Commit: $COMMIT_SHA"
  fi
  echo ""
  echo "## Review Prompt"
  echo "$PROMPT"
  exit 2
fi

if [[ -n "$COMMIT_SHA" ]]; then
  if [[ ! "$COMMIT_SHA" =~ ^[0-9a-fA-F]{7,40}$ ]]; then
    echo "ERROR: invalid commit SHA: $COMMIT_SHA" >&2
    exit 1
  fi
  commit_exit=0
  if command -v timeout >/dev/null 2>&1; then
    timeout "$CODEX_TIMEOUT_SECONDS" "$CODEX_BIN" review --commit "$COMMIT_SHA" 2>&1 || commit_exit=$?
  elif command -v perl >/dev/null 2>&1; then
    perl -e 'alarm shift; exec @ARGV' "$CODEX_TIMEOUT_SECONDS" "$CODEX_BIN" review --commit "$COMMIT_SHA" 2>&1 || commit_exit=$?
  else
    "$CODEX_BIN" review --commit "$COMMIT_SHA" 2>&1 || commit_exit=$?
  fi
  if [[ "$commit_exit" -ne 0 ]]; then
    echo "# Codex review --commit failed (exit $commit_exit)"
    echo "# Commit: $COMMIT_SHA"
    exit "$commit_exit"
  fi
else
  if [[ ! -f "$CONTENT_FILE" ]]; then
    echo "ERROR: file not found: $CONTENT_FILE" >&2
    exit 1
  fi
  # Review file content via codex exec using output-schema + output-last-message
  SCOPE_PREFIX=""
  if [[ -n "$WRK_ID" ]]; then
    SCOPE_PREFIX="WRK in scope: ${WRK_ID}
This review is being run under the active approved work item above.

"
  fi

  # Read up to 5MB to prevent bash OOMs on accidentally provided binaries or giant files
  CONTENT_TEXT="$(head -c 5000000 "$CONTENT_FILE" | tr -d '\000')"
  FULL_PROMPT="${SCOPE_PREFIX}${PROMPT}

---
CONTENT TO REVIEW:
---

${CONTENT_TEXT}"
  payload_chars="${#FULL_PROMPT}"

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
    elif command -v perl >/dev/null 2>&1; then
      perl -e 'alarm shift; exec @ARGV' "$CODEX_TIMEOUT_SECONDS" "$CODEX_BIN" exec "$prompt_text" \
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

  check_uv_readiness() {
    if command -v uv >/dev/null 2>&1; then
      if ! uv run --no-project python -c "print(1)" >/dev/null 2>&1; then
        echo "# ERROR: uv is installed but not functional" >&2
        echo "# Diagnose: uv run --no-project python -c \"print(1)\"" >&2
        return 1
      fi
    fi
    return 0
  }

  classify_codex_failure() {
    if [[ -s "$err_file" ]] && grep -Eqi \
      "(insufficient[_ -]?quota|quota (exceeded|reached)|billing (limit|quota)|payment required|hard limit reached|credits? (exhausted|depleted|remaining:[[:space:]]*0)|usage limit|you.ve hit your usage|try again at)" \
      "$err_file"; then
      echo "QUOTA"
      return
    fi
    if [[ -s "$err_file" ]] && grep -Eqi "(timed out|timeout|deadline exceeded)" "$err_file"; then
      echo "TIMEOUT"
      return
    fi
    if [[ -s "$err_file" ]] && grep -Eqi "(operation not permitted|permission denied|failed to connect|stream disconnected|error sending request)" "$err_file"; then
      echo "TRANSPORT"
      return
    fi
    echo "GENERIC"
  }

  run_renderer() {
    uv run --no-project python "$RENDERER" --provider codex --input "$raw_file"
  }

  prompt_for_run="$FULL_PROMPT"
  if [[ "$payload_chars" -gt "$CODEX_MAX_PROMPT_CHARS" ]]; then
    compact_text="${CONTENT_TEXT:0:CODEX_COMPACT_RETRY_CHARS}"
    prompt_for_run="${SCOPE_PREFIX}${PROMPT}

---
CONTENT TO REVIEW (TRUNCATED FOR ARGUMENT SIZE SAFETY):
---

${compact_text}

[truncated by submit-to-codex initial guard to avoid oversized CLI payload]"
  fi

  exec_exit=0
  run_codex_exec "$prompt_for_run" || exec_exit=$?

  # One compact retry when full payload returns no usable output.
  if [[ "$exec_exit" -ne 0 || ! -s "$raw_file" ]]; then
    compact_text="${CONTENT_TEXT:0:CODEX_COMPACT_RETRY_CHARS}"
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
      echo "# CODEX_QUOTA_EXHAUSTED"
      echo "# Codex quota/credits exhausted"
      echo "# Action: Claude Opus fallback will be used automatically."
      exit 3  # Reserved exit code for quota exhaustion (triggers Opus fallback in cross-review.sh)
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
    exit "$exec_exit"
  fi

  check_uv_readiness || exit 1

  if run_renderer > "$rendered_file" 2>/dev/null \
    && [[ "$("$VALIDATOR" "$rendered_file")" == "VALID" ]]; then
    cat "$rendered_file"
    ( [[ -n "$ORCH_LOG_FILE" ]] && cat "$rendered_file" >> "$ORCH_LOG_FILE" ) 2>/dev/null || true
  else
    render_exit=$?
    if [[ -s "$raw_file" ]]; then
      cat "$raw_file"
      ( [[ -n "$ORCH_LOG_FILE" ]] && cat "$raw_file" >> "$ORCH_LOG_FILE" ) 2>/dev/null || true
      if [[ "$render_exit" -eq 127 ]]; then
        echo "# Renderer runtime unavailable (need uv)" >&2
      fi
      exit 6
    else
      echo "# Codex returned NO_OUTPUT"
      exit 5
    fi
  fi
fi
