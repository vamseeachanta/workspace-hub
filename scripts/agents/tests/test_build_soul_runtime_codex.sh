#!/usr/bin/env bash
# TDD — #2841 Phase B: build-soul-runtime.sh appends a Skill index + inlined universal
# rules to the Codex AGENTS.runtime.md ONLY (F3: codex/claude SOUL.runtime.md unchanged).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
AGENTS="${REPO_ROOT}/config/agents/codex/AGENTS.runtime.md"
CODEX_SOUL="${REPO_ROOT}/config/agents/codex/SOUL.runtime.md"
CLAUDE_SOUL="${REPO_ROOT}/config/agents/claude/SOUL.runtime.md"

fail=0
chk() { if eval "$2"; then echo "  PASS: $1"; else echo "  FAIL: $1"; fail=$((fail+1)); fi; }

if ! bash "${REPO_ROOT}/scripts/agents/build-soul-runtime.sh" >/dev/null 2>&1; then
    echo "FAIL: runtime generation failed"; exit 1
fi

# Native discovery and canonical authorship are distinct contracts (#3186).
for runtime in "${AGENTS}" "${CODEX_SOUL}"; do
    chk "native discovery documented: ${runtime##*/}" "grep -Fq 'Codex supports native skill discovery' '${runtime}'"
    chk "native roots documented: ${runtime##*/}" "grep -Fq 'Repository discovery uses' '${runtime}'"
    chk "native preservation documented: ${runtime##*/}" "grep -Fq 'Preserve native .system skills' '${runtime}'"
    chk "false loader claims absent from skills guidance: ${runtime##*/}" "! sed -n '/^## Skill Loader/,/^## Required Gates/p; /^## Skill index/,/^## Universal rules/p' '${runtime}' | grep -Eqi 'no native skill loader|no native loader|skills/.*currently empty|wins over.*agents/skills'"
done

# AGENTS.runtime.md gains the Codex-only sections
chk "AGENTS.runtime.md has Skill index"          "grep -q '## Skill index' '${AGENTS}'"
chk "Skill index lists at least one SKILL"        "grep -qE '^- \*\*' '${AGENTS}'"
chk "AGENTS.runtime.md inlines universal rules"   "grep -q 'Universal rules (inlined for Codex)' '${AGENTS}'"
chk "AGENTS.runtime.md inlines coding-style"      "grep -qi 'Edit Safety\|Path Handling' '${AGENTS}'"
chk "AGENTS.runtime.md inlines patterns"          "grep -qi 'Enforcement Gradient' '${AGENTS}'"

# F3: the codex + claude SOUL.runtime.md must NOT gain those sections (divergence)
chk "codex SOUL.runtime.md has NO Skill index"    "! grep -q '## Skill index' '${CODEX_SOUL}'"
chk "claude SOUL.runtime.md has NO Skill index"   "! grep -q '## Skill index' '${CLAUDE_SOUL}'"

# Claude-only rules NOT inlined into Codex (goal-invocation 'binds Claude only')
chk "goal-invocation NOT inlined into AGENTS"     "! grep -qi '/goal invocation contract' '${AGENTS}'"

# Drift checker must mirror the Codex-only append, not flag the skill index as drift.
chk "drift check accepts Codex AGENTS extras"     "bash '${REPO_ROOT}/scripts/enforcement/check-soul-runtime-drift.sh' --quiet"

# Idempotent: a second build does not double-append
# cmp is available on GNU/BSD; avoid requiring GNU-only sha256sum on macOS.
before_agents=$(mktemp) || exit 1
before_soul=$(mktemp) || { rm -f "${before_agents}"; exit 1; }
trap 'rm -f "${before_agents}" "${before_soul}"' EXIT
if ! cp "${AGENTS}" "${before_agents}" || ! cp "${CODEX_SOUL}" "${before_soul}"; then
    echo "FAIL: runtime snapshot failed"; exit 1
fi
if ! bash "${REPO_ROOT}/scripts/agents/build-soul-runtime.sh" >/dev/null 2>&1; then
    echo "FAIL: runtime regeneration failed"; exit 1
fi
chk "rebuild is byte-identical for both Codex artifacts" "cmp -s '${before_agents}' '${AGENTS}' && cmp -s '${before_soul}' '${CODEX_SOUL}'"

echo "---"
if [ "${fail}" -gt 0 ]; then echo "FAILED: ${fail} check(s)"; exit 1; fi
echo "ALL PASS"
