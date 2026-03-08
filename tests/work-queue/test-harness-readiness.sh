#!/usr/bin/env bash
# test-harness-readiness.sh — TDD tests for WRK-1047 harness readiness checks
# Tests T1-T12 (Phase A), T13-T14 (Phase C), T15-T16 (Phase E)
# Run: bash tests/work-queue/test-harness-readiness.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
READINESS_SCRIPT="${REPO_ROOT}/scripts/readiness/nightly-readiness.sh"
COMPARE_SCRIPT="${REPO_ROOT}/scripts/readiness/compare-harness-state.sh"
REMEDIATE_SCRIPT="${REPO_ROOT}/scripts/readiness/remediate-harness.sh"
HARNESS_CONFIG="${REPO_ROOT}/scripts/readiness/harness-config.yaml"

pass=0
fail=0
errors=()

ok()   { echo "  PASS  $1"; pass=$((pass + 1)); }
fail() { echo "  FAIL  $1"; fail=$((fail + 1)); errors+=("$1"); }

# Create an isolated temp workspace for each test
mk_ws() {
  local ws
  ws=$(mktemp -d)
  # Minimal workspace structure
  mkdir -p "${ws}/.claude/settings.json" 2>/dev/null || true
  mkdir -p "${ws}/.claude/state"
  mkdir -p "${ws}/.claude/skills"
  mkdir -p "${ws}/.claude/commands"
  echo '{}' > "${ws}/.claude/settings.json" 2>/dev/null || \
    { rm -rf "${ws}/.claude/settings.json"; echo '{}' > "${ws}/.claude/settings.json"; }
  # Copy harness-config so checks can read it
  cp "${HARNESS_CONFIG}" "${ws}/scripts/readiness/harness-config.yaml" 2>/dev/null || \
    { mkdir -p "${ws}/scripts/readiness"; cp "${HARNESS_CONFIG}" "${ws}/scripts/readiness/harness-config.yaml"; }
  echo "$ws"
}

rm_ws() { rm -rf "$1"; }

echo "=== WRK-1047 harness readiness tests ==="

# ── T1: All checks pass → exit 0 ─────────────────────────────────────────────
T1() {
  # Use the real workspace — if all checks pass on ace-linux-1, exit should be 0
  # This is a live smoke test; skip if nightly-readiness.sh not yet extended
  if ! grep -q "check_r_plugins\|R-PLUGINS" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T1: nightly-readiness.sh not yet extended (pre-implementation)"
    return
  fi
  if WORKSPACE_HUB="${REPO_ROOT}" bash "${READINESS_SCRIPT}" 2>/dev/null | grep -q "FAIL"; then
    fail "T1: expected all checks pass on ace-linux-1 — FAIL lines found"
  else
    ok "T1: all checks pass on ace-linux-1"
  fi
}
T1

# ── T2: Required plugin missing → R-PLUGINS FAIL ─────────────────────────────
T2() {
  if ! grep -q "check_r_plugins\|R-PLUGINS" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T2: R-PLUGINS not yet implemented"
    return
  fi
  ws=$(mk_ws)
  # Simulate claude plugin list returning only 1 plugin (missing most required)
  local fake_claude="${ws}/bin/claude"
  mkdir -p "${ws}/bin"
  cat > "${fake_claude}" << 'EOF'
#!/usr/bin/env bash
if [[ "$1 $2" == "plugin list" ]]; then
  echo "Installed plugins:"
  echo "  > frontend-design@claude-plugins-official"
  echo "    Status: ✔ enabled"
fi
EOF
  chmod +x "${fake_claude}"
  local output
  output=$(PATH="${ws}/bin:${PATH}" WORKSPACE_HUB="${REPO_ROOT}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-PLUGINS.*FAIL\|FAIL.*R-PLUGINS"; then
    ok "T2: R-PLUGINS FAIL on missing required plugin"
  else
    fail "T2: expected R-PLUGINS FAIL — got: $(echo "$output" | grep -i plugin | head -2)"
  fi
  rm_ws "$ws"
}
T2

# ── T3: Extra unlisted plugin present → R-PLUGINS PASS ───────────────────────
T3() {
  if ! grep -q "check_r_plugins\|R-PLUGINS" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T3: R-PLUGINS not yet implemented"
    return
  fi
  ws=$(mk_ws)
  local fake_claude="${ws}/bin/claude"
  mkdir -p "${ws}/bin"
  # Return all 10 required plugins + one extra unknown plugin
  cat > "${fake_claude}" << 'EOF'
#!/usr/bin/env bash
if [[ "$1 $2" == "plugin list" ]]; then
  for p in frontend-design skill-creator code-review pr-review-toolkit feature-dev playground pyright-lsp claude-md-management hookify superpowers some-unknown-extra-plugin; do
    echo "  > ${p}@claude-plugins-official"
    echo "    Status: ✔ enabled"
  done
fi
EOF
  chmod +x "${fake_claude}"
  local output
  output=$(PATH="${ws}/bin:${PATH}" WORKSPACE_HUB="${REPO_ROOT}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -qE "OK.*R-PLUGINS|R-PLUGINS.*OK"; then
    ok "T3: R-PLUGINS PASS with extra unknown plugin present"
  else
    fail "T3: expected R-PLUGINS PASS — got: $(echo "$output" | grep -i plugin | head -2)"
  fi
  rm_ws "$ws"
}
T3

# ── T4: Oversized CLAUDE.md in tier-1 repo → R-HARNESS FAIL ──────────────────
T4() {
  if ! grep -q "tier1_repos\|tier.1.*scan\|R-HARNESS.*tier" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T4: R-HARNESS tier-1 extension not yet implemented"
    return
  fi
  ws=$(mk_ws)
  mkdir -p "${ws}/assetutilities"
  # Create CLAUDE.md with 25 lines (>20 limit)
  printf 'line %s\n' {1..25} > "${ws}/assetutilities/CLAUDE.md"
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-HARNESS.*FAIL\|FAIL.*R-HARNESS"; then
    ok "T4: R-HARNESS FAIL on oversized tier-1 CLAUDE.md"
  else
    fail "T4: expected R-HARNESS FAIL — got: $(echo "$output" | grep -i harness | head -2)"
  fi
  rm_ws "$ws"
}
T4

# ── T5: Hook file absent from disk → R-HOOKS FAIL ────────────────────────────
T5() {
  if ! grep -q "check_r_hooks\|R-HOOKS" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T5: R-HOOKS not yet implemented"
    return
  fi
  ws=$(mk_ws)
  mkdir -p "${ws}/.claude"
  # settings.json references a hook that doesn't exist
  cat > "${ws}/.claude/settings.json" << 'EOF'
{
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": "bash /nonexistent/stop-hook.sh"}]}]
  }
}
EOF
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-HOOKS.*FAIL\|FAIL.*R-HOOKS"; then
    ok "T5: R-HOOKS FAIL on missing hook file"
  else
    fail "T5: expected R-HOOKS FAIL — got: $(echo "$output" | grep -i hooks | head -2)"
  fi
  rm_ws "$ws"
}
T5

# ── T6: Hook file contains 'git commit' → R-HOOK-STATIC FAIL ─────────────────
T6() {
  if ! grep -q "check_r_hook_static\|R-HOOK-STATIC" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T6: R-HOOK-STATIC not yet implemented"
    return
  fi
  ws=$(mk_ws)
  mkdir -p "${ws}/.claude/hooks"
  cat > "${ws}/.claude/hooks/stop.sh" << 'EOF'
#!/usr/bin/env bash
echo "stop hook"
git commit -am "auto commit from hook"
EOF
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-HOOK-STATIC.*FAIL\|FAIL.*R-HOOK-STATIC"; then
    ok "T6: R-HOOK-STATIC FAIL on 'git commit' pattern in hook"
  else
    fail "T6: expected R-HOOK-STATIC FAIL — got: $(echo "$output" | grep -i static | head -2)"
  fi
  rm_ws "$ws"
}
T6

# ── T7: Hook file >200 lines → R-HOOK-STATIC FAIL ────────────────────────────
T7() {
  if ! grep -q "check_r_hook_static\|R-HOOK-STATIC" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T7: R-HOOK-STATIC not yet implemented"
    return
  fi
  ws=$(mk_ws)
  mkdir -p "${ws}/.claude/hooks"
  printf '# line %s\n' {1..210} > "${ws}/.claude/hooks/stop.sh"
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-HOOK-STATIC.*FAIL\|FAIL.*R-HOOK-STATIC"; then
    ok "T7: R-HOOK-STATIC FAIL on hook >200 lines"
  else
    fail "T7: expected R-HOOK-STATIC FAIL — got: $(echo "$output" | grep -i static | head -2)"
  fi
  rm_ws "$ws"
}
T7

# ── T8: settings.json invalid JSON → R-SETTINGS FAIL ─────────────────────────
T8() {
  if ! grep -q "check_r_settings\|R-SETTINGS" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T8: R-SETTINGS not yet implemented"
    return
  fi
  ws=$(mk_ws)
  mkdir -p "${ws}/.claude"
  echo '{invalid json' > "${ws}/.claude/settings.json"
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-SETTINGS.*FAIL\|FAIL.*R-SETTINGS"; then
    ok "T8: R-SETTINGS FAIL on invalid JSON"
  else
    fail "T8: expected R-SETTINGS FAIL — got: $(echo "$output" | grep -i settings | head -2)"
  fi
  rm_ws "$ws"
}
T8

# ── T9: uv absent → R-UV FAIL ────────────────────────────────────────────────
T9() {
  if ! grep -q "check_r_uv\|R-UV" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T9: R-UV not yet implemented"
    return
  fi
  ws=$(mk_ws)
  local output
  # PATH with no uv
  output=$(PATH="/usr/bin:/bin" WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-UV.*FAIL\|FAIL.*R-UV"; then
    ok "T9: R-UV FAIL when uv absent from PATH"
  else
    fail "T9: expected R-UV FAIL — got: $(echo "$output" | grep -i " uv\|R-UV" | head -2)"
  fi
  rm_ws "$ws"
}
T9

# ── T10: pre-commit missing legal entry → R-PRECOMMIT FAIL ───────────────────
T10() {
  if ! grep -q "check_r_precommit\|R-PRECOMMIT" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T10: R-PRECOMMIT not yet implemented"
    return
  fi
  ws=$(mk_ws)
  mkdir -p "${ws}/assetutilities"
  # pre-commit config present but no legal scan entry
  cat > "${ws}/assetutilities/.pre-commit-config.yaml" << 'EOF'
repos:
  - repo: local
    hooks:
      - id: black
        name: black
        entry: black
        language: python
EOF
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-PRECOMMIT.*FAIL\|FAIL.*R-PRECOMMIT"; then
    ok "T10: R-PRECOMMIT FAIL on missing legal-sanity-scan entry"
  else
    fail "T10: expected R-PRECOMMIT FAIL — got: $(echo "$output" | grep -i precommit | head -2)"
  fi
  rm_ws "$ws"
}
T10

# ── T11: SKILL.md count below baseline → R-SKILLS FAIL ──────────────────────
T11() {
  if ! grep -q "skill_count_baseline\|R-SKILLS.*count\|count.*baseline" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T11: R-SKILLS count check not yet implemented"
    return
  fi
  ws=$(mk_ws)
  mkdir -p "${ws}/scripts/readiness"
  # Set baseline to 100, but workspace has 0 skills
  sed "s/skill_count_baseline: 0/skill_count_baseline: 100/" \
    "${HARNESS_CONFIG}" > "${ws}/scripts/readiness/harness-config.yaml"
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-SKILLS.*FAIL\|FAIL.*R-SKILLS"; then
    ok "T11: R-SKILLS FAIL when skill count below baseline"
  else
    fail "T11: expected R-SKILLS FAIL — got: $(echo "$output" | grep -i skills | head -2)"
  fi
  rm_ws "$ws"
}
T11

# ── T12: command count below baseline → R-SKILLS FAIL ───────────────────────
T12() {
  if ! grep -q "command_count_baseline\|R-SKILLS.*command\|command.*baseline" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T12: R-SKILLS command count check not yet implemented"
    return
  fi
  ws=$(mk_ws)
  mkdir -p "${ws}/scripts/readiness"
  # Set command baseline to 100, but workspace has 0 commands
  sed "s/command_count_baseline: 0/command_count_baseline: 100/" \
    "${HARNESS_CONFIG}" > "${ws}/scripts/readiness/harness-config.yaml"
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${READINESS_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -q "R-SKILLS.*FAIL\|FAIL.*R-SKILLS"; then
    ok "T12: R-SKILLS FAIL when command count below baseline"
  else
    fail "T12: expected R-SKILLS FAIL — got: $(echo "$output" | grep -i skills | head -2)"
  fi
  rm_ws "$ws"
}
T12

# ── T13: SSH to ace-linux-2 unreachable → DEGRADED (no crash) ────────────────
T13() {
  if [[ ! -f "${COMPARE_SCRIPT}" ]]; then
    echo "  SKIP  T13: compare-harness-state.sh not yet implemented"
    return
  fi
  local output
  output=$(WORKSPACE_HUB="${REPO_ROOT}" \
    HARNESS_CONFIG="${HARNESS_CONFIG}" \
    bash "${COMPARE_SCRIPT}" --dry-run --force-ssh-fail 2>&1 || true)
  if echo "$output" | grep -qi "degraded\|unreachable\|skip"; then
    ok "T13: compare-harness-state.sh handles SSH failure gracefully (DEGRADED)"
  else
    fail "T13: expected DEGRADED/unreachable on SSH fail — got: $(echo "$output" | head -3)"
  fi
}
T13

# ── T14: Stale acma-ansys05 report (>25h) → DEGRADED ────────────────────────
T14() {
  if [[ ! -f "${COMPARE_SCRIPT}" ]]; then
    echo "  SKIP  T14: compare-harness-state.sh not yet implemented"
    return
  fi
  ws=$(mk_ws)
  local stale_report="${ws}/.claude/state/harness-readiness-acma-ansys05.yaml"
  # Write a report timestamped 30 hours ago
  local stale_ts
  stale_ts=$(date -u -d "30 hours ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
    date -u -v-30H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "2026-03-07T00:00:00Z")
  cat > "${stale_report}" << EOF
schema_version: 1
host: acma-ansys05
generated_at: "${stale_ts}"
overall: pass
pass_count: 5
fail_count: 0
checks: {}
EOF
  local output
  output=$(WORKSPACE_HUB="${ws}" HARNESS_CONFIG="${HARNESS_CONFIG}" \
    bash "${COMPARE_SCRIPT}" 2>&1 || true)
  if echo "$output" | grep -qi "degraded\|stale"; then
    ok "T14: compare-harness-state.sh flags stale acma-ansys05 report as DEGRADED"
  else
    fail "T14: expected DEGRADED for stale report — got: $(echo "$output" | head -3)"
  fi
  rm_ws "$ws"
}
T14

# ── T15: remediate-harness.sh R-PLUGINS FAIL → prints install command ─────────
T15() {
  if [[ ! -f "${REMEDIATE_SCRIPT}" ]]; then
    echo "  SKIP  T15: remediate-harness.sh not yet implemented"
    return
  fi
  ws=$(mk_ws)
  cat > "${ws}/.claude/state/harness-readiness-ace-linux-1.yaml" << 'EOF'
schema_version: 1
host: ace-linux-1
generated_at: "2026-03-08T02:00:00Z"
overall: fail
pass_count: 9
fail_count: 1
checks:
  R-PLUGINS:
    status: fail
    detail: "missing: pyright-lsp"
EOF
  local output
  output=$(WORKSPACE_HUB="${ws}" bash "${REMEDIATE_SCRIPT}" --workstation ace-linux-1 2>&1)
  if echo "$output" | grep -q "pyright-lsp\|plugin install"; then
    ok "T15: remediate-harness.sh prints plugin install command for R-PLUGINS FAIL"
  else
    fail "T15: expected plugin install command — got: $(echo "$output" | head -5)"
  fi
  rm_ws "$ws"
}
T15

# ── T16: harness-readiness-report.yaml schema validation ─────────────────────
T16() {
  if ! grep -q "harness-readiness-\|harness_readiness_report" "${READINESS_SCRIPT}" 2>/dev/null; then
    echo "  SKIP  T16: YAML report output not yet implemented"
    return
  fi
  local report="${REPO_ROOT}/.claude/state/harness-readiness-ace-linux-1.yaml"
  if [[ ! -f "$report" ]]; then
    echo "  SKIP  T16: no report generated yet (run nightly-readiness.sh first)"
    return
  fi
  local required_fields=("schema_version" "host" "generated_at" "overall" "pass_count" "fail_count" "checks")
  local missing=()
  for field in "${required_fields[@]}"; do
    grep -q "^${field}:" "$report" || missing+=("$field")
  done
  if [[ ${#missing[@]} -eq 0 ]]; then
    ok "T16: harness-readiness-report.yaml has all required schema fields"
  else
    fail "T16: report missing fields: ${missing[*]}"
  fi
}
T16

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Results: ${pass} pass, ${fail} fail ==="
if [[ ${#errors[@]} -gt 0 ]]; then
  echo "Failed:"
  for e in "${errors[@]}"; do echo "  - $e"; done
  exit 1
fi
exit 0
