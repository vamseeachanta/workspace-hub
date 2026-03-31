#!/usr/bin/env bash
# cross-review-gate.sh — Claude PreToolUse hook
# Fires before Bash commands; blocks PR creation without cross-review evidence
# Also gates verification completion claims
# Issue: #1537

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Read tool input from stdin (Claude hook protocol)
INPUT=$(cat)

# Extract the bash command from the hook input
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null || true)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || true)

# Only act on Bash tool calls
if [[ "$TOOL_NAME" != "Bash" || -z "$COMMAND" ]]; then
  exit 0
fi

# --- Gate 1: PR creation requires cross-review ---
if echo "$COMMAND" | grep -qE 'gh\s+pr\s+create'; then
  if ! bash "${REPO_ROOT}/scripts/enforcement/require-cross-review.sh" 2>&1; then
    echo '{"decision": "block", "reason": "Cross-review required before PR creation. Run /gsd:review --codex or create review artifacts first. See #1537."}' >&2
    # Output block decision for Claude hook protocol
    cat <<'JSON'
{"decision": "block", "reason": "Cross-review required before PR creation. Run /gsd:review --phase <N> --codex or save review artifacts. Policy: CROSS_REVIEW_POLICY.md (#1537)"}
JSON
    exit 0
  fi
fi

# --- Gate 2: Ship/verify commands require verify artifacts ---
if echo "$COMMAND" | grep -qE '(gsd-ship|gsd.*ship|gh\s+pr\s+merge)'; then
  if ! bash "${REPO_ROOT}/scripts/enforcement/require-verify-artifacts.sh" 2>&1; then
    cat <<'JSON'
{"decision": "block", "reason": "Verify-step enforcement failed. Ensure cross-review, TDD evidence, and artifact review exist. Policy: CROSS_REVIEW_POLICY.md (#1537)"}
JSON
    exit 0
  fi
fi

# --- Gate 3: Plan execution requires plan cross-review ---
if echo "$COMMAND" | grep -qE '(gsd-execute-phase|gsd.*execute)'; then
  if ! bash "${REPO_ROOT}/scripts/enforcement/require-plan-review.sh" 2>&1; then
    cat <<'JSON'
{"decision": "block", "reason": "Plan cross-review required before execution. Run /gsd:review --phase <N> --codex first. Policy: CROSS_REVIEW_POLICY.md (#1537)"}
JSON
    exit 0
  fi
fi

exit 0
