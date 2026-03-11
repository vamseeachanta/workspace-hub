#!/usr/bin/env bash
# test_wrk1053_scripts.sh — Tests for WRK-1053 scripts
# Tests: audit-skill-violations.sh (3) + skill-coverage-audit.sh (3) + wiring (2) = 8 total
# Note: outer script intentionally does NOT use set -e so expected-failure tests don't abort run

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
AUDIT="${REPO_ROOT}/scripts/skills/audit-skill-violations.sh"
COVERAGE="${REPO_ROOT}/scripts/skills/skill-coverage-audit.sh"

PASS=0
FAIL=0

pass() { echo "PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL: $1"; FAIL=$((FAIL + 1)); }

run_script() {
  # run_script <script> [args...] — captures exit code without || true masking
  local _exit=0
  "$@" > /tmp/_wrk1053_out 2>/tmp/_wrk1053_err || _exit=$?
  echo "$_exit"
}

# --- Setup ---
TMP=$(mktemp -d)
TMP2=$(mktemp -d)
TMP3=$(mktemp -d)
trap 'rm -rf "$TMP" "$TMP2" "$TMP3"' EXIT

# --- audit-skill-violations.sh tests ---

# T1: Happy path — clean skill dir, no violations
mkdir -p "${TMP}/my-skill"
cat > "${TMP}/my-skill/SKILL.md" << 'EOF'
---
name: my-skill
description: A short description under 1024 chars.
---
# My Skill
Some content here with no XML tags.
EOF
ec=$(run_script bash "$AUDIT" --skill-dir "$TMP")
if [[ "$ec" -eq 0 ]]; then
  pass "T1: clean skill dir → exit 0"
else
  fail "T1: clean skill dir → expected exit 0, got $ec"
fi

# T2: README.md presence = violation
touch "${TMP}/my-skill/README.md"
ec=$(run_script bash "$AUDIT" --skill-dir "$TMP")
out=$(cat /tmp/_wrk1053_out)
if [[ "$ec" -eq 1 ]] && echo "$out" | grep -q "readme_present"; then
  pass "T2: README.md present → exit 1 with readme_present"
else
  fail "T2: README.md present → expected exit 1 + readme_present (got exit $ec, output: $out)"
fi
rm "${TMP}/my-skill/README.md"

# T3: Word count > 5000 = violation
python3 -c "
fm = '---\nname: big\ndescription: short\n---\n'
print(fm + ' '.join(['word'] * 5001))
" > "${TMP}/my-skill/SKILL.md"
ec=$(run_script bash "$AUDIT" --skill-dir "$TMP")
out=$(cat /tmp/_wrk1053_out)
if [[ "$ec" -eq 1 ]] && echo "$out" | grep -q "word_count"; then
  pass "T3: oversized SKILL.md → exit 1 with word_count"
else
  fail "T3: oversized SKILL.md → expected exit 1 + word_count (got exit $ec, output: $out)"
fi

# --- skill-coverage-audit.sh tests ---

# T4: Happy path — frontmatter scripts: field present
mkdir -p "${TMP2}/wired-skill"
cat > "${TMP2}/wired-skill/SKILL.md" << 'EOF'
---
name: wired-skill
scripts:
  - scripts/skills/audit-skill-violations.sh
---
# Wired Skill
EOF
ec=$(run_script bash "$COVERAGE" --skill-dir "$TMP2")
if [[ "$ec" -eq 0 ]]; then
  pass "T4: frontmatter scripts: present → exit 0"
else
  fail "T4: frontmatter scripts: present → expected exit 0 (got $ec)"
fi

# T5: Gap — no scripts: and no exec patterns
mkdir -p "${TMP3}/unwired-skill"
cat > "${TMP3}/unwired-skill/SKILL.md" << 'EOF'
---
name: unwired-skill
description: No scripts here.
---
# Unwired Skill
This skill has only prose and no script calls.
EOF
ec=$(run_script bash "$COVERAGE" --skill-dir "$TMP3")
out=$(cat /tmp/_wrk1053_out)
if [[ "$ec" -eq 1 ]] && echo "$out" | grep -q "has_script_ref: false"; then
  pass "T5: no scripts + no exec → exit 1 with has_script_ref: false"
else
  fail "T5: no scripts + no exec → expected exit 1 + has_script_ref: false (got exit $ec)"
fi

# T6: Nonexistent dir → exit 2
ec=$(run_script bash "$COVERAGE" --skill-dir "/nonexistent-path-xyz")
if [[ "$ec" -eq 2 ]]; then
  pass "T6: nonexistent --skill-dir → exit 2"
else
  fail "T6: nonexistent --skill-dir → expected exit 2 (got $ec)"
fi

# --- Wiring checks ---

# T7: skill-eval references validate-skills.sh (original AC wiring)
SKILL_EVAL_FILE="${REPO_ROOT}/.claude/skills/development/skill-eval/SKILL.md"
if grep -q "validate-skills.sh" "$SKILL_EVAL_FILE" 2>/dev/null && grep -q "skill-coverage-audit.sh" "$SKILL_EVAL_FILE" 2>/dev/null; then
  pass "T7: skill-eval/SKILL.md references validate-skills.sh + skill-coverage-audit.sh"
else
  fail "T7: skill-eval/SKILL.md missing validate-skills.sh or skill-coverage-audit.sh"
fi

# T8: comprehensive-learning references skill-coverage-audit.sh
CL_FILE="${REPO_ROOT}/.claude/skills/workspace-hub/comprehensive-learning/SKILL.md"
if grep -q "skill-coverage-audit.sh" "$CL_FILE" 2>/dev/null; then
  pass "T8: comprehensive-learning/SKILL.md references skill-coverage-audit.sh"
else
  fail "T8: comprehensive-learning/SKILL.md missing skill-coverage-audit.sh reference"
fi

# --- Summary ---
echo ""
echo "Results: $((PASS + FAIL)) total, $PASS pass, $FAIL fail"
[[ "$FAIL" -eq 0 ]]
