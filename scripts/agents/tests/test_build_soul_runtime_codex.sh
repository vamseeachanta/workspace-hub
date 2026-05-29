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

bash "${REPO_ROOT}/scripts/agents/build-soul-runtime.sh" >/dev/null 2>&1

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

# Idempotent: a second build does not double-append
before=$(wc -l < "${AGENTS}")
bash "${REPO_ROOT}/scripts/agents/build-soul-runtime.sh" >/dev/null 2>&1
after=$(wc -l < "${AGENTS}")
chk "rebuild is idempotent (no double-append)"    "[ '${before}' = '${after}' ]"

# ── r2 review additions ──
chk "drift checker passes after build (F1)"        "bash '${REPO_ROOT}/scripts/enforcement/check-soul-runtime-drift.sh' --quiet"
chk "no empty (0-skill) family in index (F5)"      "! grep -qE '— 0 skill' '${AGENTS}'"
chk "SOUL.delta has Skills section (Phase B)"      "grep -q 'Skills (no native loader' '${REPO_ROOT}/config/agents/codex/SOUL.delta.md'"
chk "enumerate hint is recursive find, not ls (F2)" "! grep -qE 'ls .claude/skills/[^ ]+/\*/SKILL.md' '${AGENTS}'"
# F2: a sampled family's index count equals its recursive find count
wh_idx=$(awk '/^## Skill index/,/^## Universal rules/' "${AGENTS}" | sed -n 's/.*\*\*workspace-hub\/\*\* — \([0-9]*\) skill.*/\1/p')
wh_real=$(find "${REPO_ROOT}/.claude/skills/workspace-hub" -name SKILL.md -not -path '*_archive*' 2>/dev/null | wc -l | tr -d ' ')
chk "index count matches recursive find (F2)"      "[ -n '${wh_idx}' ] && [ '${wh_idx}' = '${wh_real}' ]"

echo "---"
if [ "${fail}" -gt 0 ]; then echo "FAILED: ${fail} check(s)"; exit 1; fi
echo "ALL PASS"
