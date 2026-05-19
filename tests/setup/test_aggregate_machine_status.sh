#!/usr/bin/env bash
# test_aggregate_machine_status.sh — TDD tests for aggregate-machine-status.sh
# Issue: vamseeachanta/workspace-hub#2751 (Phase 3, G9)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HELPER="${REPO_ROOT}/scripts/setup/aggregate-machine-status.sh"

PASS=0
FAIL=0
FAILED_TESTS=()

_pass() { echo "  PASS  $1"; PASS=$((PASS + 1)); }
_fail() { echo "  FAIL  $1"; echo "        $2"; FAIL=$((FAIL + 1)); FAILED_TESTS+=("$1"); }

echo "=== test_aggregate_machine_status.sh (issue #2751 Phase 3 G9) ==="
echo ""

if [[ ! -f "$HELPER" ]]; then
    _fail "helper_exists" "missing: $HELPER (expected in TDD RED phase)"
    echo ""; echo "=== Summary: $PASS PASS, $FAIL FAIL ==="; exit 1
fi

# Helper: set up a fake repo with N machine-baseline YAML fixtures, run aggregator, return report path
_make_fake_repo() {
    local fake_repo="$1"; shift
    mkdir -p "${fake_repo}/config/machine-baselines" "${fake_repo}/docs/reports"
    local i=0
    for status_combo in "$@"; do
        local machine_name="${status_combo%%:*}"
        local soul_status="${status_combo##*:}"
        cat > "${fake_repo}/config/machine-baselines/${machine_name}.yaml" <<YAMLEOF
hostname: "${machine_name}-raw"
os: "linux"
last_updated: "2026-05-19T00:00:00Z"

dimensions:
  soul_contracts: ${soul_status}
  skills: PASS
  rules: PASS
  bridged_memory: PASS
  claude_global_pointer: PASS
  codex_agents_symlink: PASS
  hermes_soul_symlink: PASS
  claude_cli_auth: PASS
  codex_cli_auth: PASS
  gh_cli_auth: PASS
  gemini_cli_auth: PASS
  hermes_can_boot: PASS
  raw_session_state: "machine-local-by-design"
  submodules_initialized: PASS
  git_hooks_installed: PASS
  shell_profile_wired: PASS
  npm_global_prefix: PASS
  scheduler_entries: PASS
  ssh_key_present: PASS
  env_file_present: PASS
  uv_or_python_available: PASS
  git_bash_available: "n/a"

cli_versions:
  claude: "1.0"
  codex: "0.123.0"
  gh: "2.0"
  gemini: "0.42.0"
  hermes: "0.4.0"
  node: "20.0"
  npm: "10.0"
  uv: "0.5"
YAMLEOF
        i=$((i + 1))
    done
}

# --- Test 1: empty registry → placeholder report ---
fake_repo="$(mktemp -d)"
mkdir -p "${fake_repo}/config/machine-baselines" "${fake_repo}/docs/reports"
output=$(bash "$HELPER" "$fake_repo" 2>&1)
report="${fake_repo}/docs/reports/fleet-harness-status.md"
if [[ -f "$report" ]]; then
    if grep -qi "no machines" "$report"; then
        _pass "zero_machines_placeholder"
    else
        _fail "zero_machines_placeholder" "report does not say 'No machines'. content: $(cat "$report")"
    fi
else
    _fail "zero_machines_report_created" "report not created"
fi
rm -rf "$fake_repo"

# --- Test 2: single machine → 1-row table ---
fake_repo="$(mktemp -d)"
_make_fake_repo "$fake_repo" "ace-linux-1:PASS"
bash "$HELPER" "$fake_repo" >/dev/null
report="${fake_repo}/docs/reports/fleet-harness-status.md"
if grep -qF "ace-linux-1" "$report"; then
    _pass "single_machine_in_report"
else
    _fail "single_machine_in_report" "machine name not in report"
fi
rm -rf "$fake_repo"

# --- Test 3: N machines → N-row table ---
fake_repo="$(mktemp -d)"
_make_fake_repo "$fake_repo" "ace-linux-1:PASS" "ace-linux-2:PASS" "win-host-1:PASS"
bash "$HELPER" "$fake_repo" >/dev/null
report="${fake_repo}/docs/reports/fleet-harness-status.md"
hits=$(grep -cE "^\| (ace-linux-1|ace-linux-2|win-host-1) " "$report" 2>/dev/null || echo 0)
if [[ "$hits" -ge 3 ]]; then
    _pass "three_machines_in_table"
else
    _fail "three_machines_in_table" "expected 3 machine rows, got $hits"
fi
rm -rf "$fake_repo"

# --- Test 4: drift detection — 2 machines, 1 dimension differs ---
fake_repo="$(mktemp -d)"
_make_fake_repo "$fake_repo" "ace-linux-1:PASS" "ace-linux-2:FAIL"
bash "$HELPER" "$fake_repo" >/dev/null
report="${fake_repo}/docs/reports/fleet-harness-status.md"
# Report should mention drift OR show FAIL for one of the machines
if grep -qiE "drift|FAIL" "$report"; then
    _pass "drift_surfaces_in_report"
else
    _fail "drift_surfaces_in_report" "report doesn't mention drift or FAIL"
fi
rm -rf "$fake_repo"

# --- Test 5: per-dimension coverage row ---
fake_repo="$(mktemp -d)"
_make_fake_repo "$fake_repo" "ace-linux-1:PASS" "ace-linux-2:PASS"
bash "$HELPER" "$fake_repo" >/dev/null
report="${fake_repo}/docs/reports/fleet-harness-status.md"
if grep -qiE "coverage|of [0-9]+ machines" "$report"; then
    _pass "per_dimension_coverage_present"
else
    _fail "per_dimension_coverage_present" "no coverage summary in report"
fi
rm -rf "$fake_repo"

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
    echo "    Failed: ${FAILED_TESTS[*]}"
    exit 1
fi
exit 0
