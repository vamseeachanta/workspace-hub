#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DOC_PATH="${REPO_ROOT}/docs/modules/ai/MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[[ -f "${DOC_PATH}" ]] || fail "architecture note missing: ${DOC_PATH}"

required_patterns=(
  '^# Minimal Harness Operating Model'
  '^## Recommendation$'
  '^## Role Assignment$'
  '^## Review Policy$'
  '^## Tradeoffs$'
  '^## Migration Steps$'
  '^## Do Less Harness$'
  '^## Adversarial Review$'
  'Should Claude Code be the default orchestrator now\?'
  'What should Codex be used for more aggressively\?'
  'What should Gemini be used for narrowly\?'
  'two-provider review by default'
  'three-provider review only'
)

for pattern in "${required_patterns[@]}"; do
  if ! grep -Eq "${pattern}" "${DOC_PATH}"; then
    fail "missing required content matching: ${pattern}"
  fi
done

echo "PASS: minimal harness operating model note covers required sections"
