#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

CROSS_REVIEW_DOC="${REPO_ROOT}/docs/modules/ai/CROSS_REVIEW_POLICY.md"
CODEX_DOC="${REPO_ROOT}/docs/modules/ai/CODEX_REVIEW_WORKFLOW.md"
GEMINI_DOC="${REPO_ROOT}/docs/modules/ai/GEMINI_REVIEW_WORKFLOW.md"
AI_README="${REPO_ROOT}/docs/modules/ai/README.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

for path in "${CROSS_REVIEW_DOC}" "${CODEX_DOC}" "${GEMINI_DOC}" "${AI_README}"; do
  [[ -f "${path}" ]] || fail "missing required doc: ${path}"
done

cross_review_patterns=(
  'Claude Code is the default orchestrator'
  'Codex is the default adversarial reviewer'
  'Gemini is an optional third reviewer'
  'two-provider review by default'
  'three-provider review only when justified'
  '\.hive-mind'
  '\.swarm'
  '\.SLASH_COMMAND_ECOSYSTEM'
  'legacy'
  '#1514'
)

for pattern in "${cross_review_patterns[@]}"; do
  if ! grep -Eq "${pattern}" "${CROSS_REVIEW_DOC}"; then
    fail "cross-review policy missing required content: ${pattern}"
  fi
done

if ! grep -Eq 'Codex is the default adversarial reviewer' "${CODEX_DOC}"; then
  fail "Codex workflow missing default reviewer policy"
fi

if ! grep -Eq 'Gemini is an optional third reviewer' "${GEMINI_DOC}"; then
  fail "Gemini workflow missing optional-third-reviewer policy"
fi

if ! grep -Eq 'CROSS_REVIEW_POLICY\.md|MINIMAL_HARNESS_OPERATING_MODEL_2026-03\.md' "${AI_README}"; then
  fail "AI README missing discoverability link to review/routing policy"
fi

echo "PASS: AI review routing policy docs reflect the minimal operating model"
