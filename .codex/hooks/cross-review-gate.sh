#!/usr/bin/env bash
# cross-review-gate.sh — Claude PreToolUse hook
# Fires before Bash commands; blocks PR creation without cross-review evidence
# Also gates verification completion claims and surfaces routing recommendations
# Issues: #1537, #1515

set -euo pipefail

REPO_ROOT="${REPO_ROOT_OVERRIDE:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

# Resolve Python interpreter portably (uv python find → python3 → python)
_UV_PY=$(uv python find 2>/dev/null) || _UV_PY=""
[[ -z "$_UV_PY" ]] && _UV_PY=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)

# Read tool input from stdin (Claude hook protocol)
INPUT=$(cat)

# Extract the bash command from the hook input
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null || true)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || true)

# Only act on Bash tool calls
if [[ "$TOOL_NAME" != "Bash" || -z "$COMMAND" ]]; then
  exit 0
fi

# --- Helper: get routing recommendation for current diff ---
get_routing_recommendation() {
  local diff
  diff="$(git diff HEAD~1..HEAD 2>/dev/null || git diff --cached 2>/dev/null || true)"
  if [[ -n "$diff" ]]; then
    if [[ -n "$_UV_PY" ]]; then
      echo "$diff" | "$_UV_PY" "${REPO_ROOT}/scripts/ai/review_routing_gate.py" --stdin 2>/dev/null || true
    fi
  fi
}

# --- Gate 1: PR creation requires cross-review + routing recommendation ---
if echo "$COMMAND" | grep -qE 'gh\s+pr\s+create'; then
  # Always compute routing recommendation (even if review passes)
  ROUTING_REC=$(get_routing_recommendation)
  REVIEWERS=$(echo "$ROUTING_REC" | jq -r '.reviewers // [] | join(", ")' 2>/dev/null || echo "codex")
  PRIORITY=$(echo "$ROUTING_REC" | jq -r '.priority // "normal"' 2>/dev/null || echo "normal")
  TRIGGERS=$(echo "$ROUTING_REC" | jq -r '.triggers_matched // [] | join(", ")' 2>/dev/null || echo "none")

  if ! bash "${REPO_ROOT}/scripts/enforcement/require-cross-review.sh" 2>&1; then
    REASON="Cross-review required before PR creation. Recommended reviewers: ${REVIEWERS} (priority: ${PRIORITY}). Triggers: ${TRIGGERS}. Run /gsd:review --codex or create review artifacts first. Policy: AI_REVIEW_ROUTING_POLICY.md (#1515, #1537)"
    echo "{\"decision\": \"block\", \"reason\": \"${REASON}\"}" >&2
    # Output block decision for Claude hook protocol
    printf '{"decision": "block", "reason": "%s"}\n' "$REASON"
    exit 0
  fi
  # Review exists — surface routing recommendation as informational stderr
  if [[ -n "$ROUTING_REC" ]]; then
    echo "[review-routing] Recommended: ${REVIEWERS} | Priority: ${PRIORITY} | Triggers: ${TRIGGERS}" >&2
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

# --- Gate 4: TDD pairing check on commit commands ---
if echo "$COMMAND" | grep -qE 'git\s+commit'; then
  TDD_OUTPUT=$(bash "${REPO_ROOT}/scripts/enforcement/require-tdd-pairing.sh" --staged 2>&1) || true
  if echo "$TDD_OUTPUT" | grep -q "WARNING"; then
    echo "$TDD_OUTPUT" >&2
  fi
fi

exit 0
