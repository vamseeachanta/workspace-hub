#!/usr/bin/env bash
# test-plan-gate.sh — Integration test harness for Stage 5 gate (WRK-1017)
#
# Covers: AC-13, AC-19, AC-32, AC-54, AC-54a, AC-57b, AC-57c, AC-57d, AC-57g
#
# Test groups:
#   GROUP 1 — Checker invocation / wiring smoke tests
#   GROUP 2 — Entrypoint guard syntax + code-path tests
#   GROUP 3 — Bootstrap dry-run inventory
#   GROUP 4 — Activation-sim blocking tests (requires temporary config swap)
#
# Usage:
#   bash scripts/agents/tests/test-plan-gate.sh           # all groups
#   bash scripts/agents/tests/test-plan-gate.sh --group 1 # one group
#   bash scripts/agents/tests/test-plan-gate.sh --sim      # include group 4 (config-swap)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
CHECKER="${REPO_ROOT}/scripts/work-queue/verify-gate-evidence.py"
BOOTSTRAP="${REPO_ROOT}/scripts/work-queue/bootstrap-stage5-gate.sh"
CONFIG="${REPO_ROOT}/scripts/work-queue/stage5-gate-config.yaml"

PASS=0
FAIL=0
RUN_SIM=false
FILTER_GROUP=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sim)    RUN_SIM=true; shift ;;
    --group)  FILTER_GROUP="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--sim] [--group N]"
      exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

pass() { echo "  PASS: $1"; (( PASS++ )) || true; }
fail() { echo "  FAIL: $1"; (( FAIL++ )) || true; }
skip() { echo "  SKIP: $1 (${2:-})"; }
group() {
  local g="$1"
  [[ -z "$FILTER_GROUP" || "$FILTER_GROUP" == "$g" ]] || return 0
  echo ""
  echo "=== GROUP $g: $2 ==="
}

# ─── GROUP 1: Checker invocation / wiring smoke tests ─────────────────────────
group 1 "Checker invocation smoke tests"
if [[ -z "$FILTER_GROUP" || "$FILTER_GROUP" == "1" ]]; then

  # 1.1 checker file exists
  if [[ -f "$CHECKER" ]]; then pass "1.1 checker file exists"; else fail "1.1 checker file exists"; fi

  # 1.2 --stage5-check mode returns exit 0 for WRK-1017 (activation=disabled)
  if uv run --no-project python "$CHECKER" --stage5-check WRK-1017 >/dev/null 2>&1; then
    pass "1.2 --stage5-check WRK-1017 exits 0 (activation=disabled)"
  else
    fail "1.2 --stage5-check WRK-1017 exits 0 (activation=disabled)"
  fi

  # 1.3 --stage5-check exits 2 for WRK without assets dir (infra failure, pre-flight check)
  # The assets dir pre-flight runs before activation check, so missing assets → exit 2 always
  missing_exit=0
  uv run --no-project python "$CHECKER" --stage5-check WRK-9999 >/dev/null 2>&1 || missing_exit=$?
  if [[ "$missing_exit" -eq 2 ]]; then
    pass "1.3 --stage5-check WRK without assets dir exits 2 (infra failure)"
  else
    fail "1.3 --stage5-check WRK without assets dir exits 2 — got exit $missing_exit"
  fi

  # 1.4 stage5-gate-config.yaml exists and has activation field
  if [[ -f "$CONFIG" ]]; then
    if grep -q "^activation:" "$CONFIG"; then
      pass "1.4 stage5-gate-config.yaml has activation field"
    else
      fail "1.4 stage5-gate-config.yaml missing activation field"
    fi
  else
    fail "1.4 stage5-gate-config.yaml exists"
  fi

  # 1.5 config owned_by_wrk is WRK-1017
  if grep -q "owned_by_wrk: WRK-1017" "$CONFIG"; then
    pass "1.5 stage5-gate-config.yaml owned_by_wrk=WRK-1017"
  else
    fail "1.5 stage5-gate-config.yaml owned_by_wrk=WRK-1017"
  fi

  # 1.6 --stage5-check exits 0 for WRK-1011 (has migration exemption)
  if uv run --no-project python "$CHECKER" --stage5-check WRK-1011 >/dev/null 2>&1; then
    pass "1.6 --stage5-check WRK-1011 exits 0 (exemption + disabled)"
  else
    fail "1.6 --stage5-check WRK-1011 exits 0 (exemption + disabled)"
  fi

fi

# ─── GROUP 2: Entrypoint guard syntax + code-path tests ───────────────────────
group 2 "Entrypoint guard syntax + code-path tests"
if [[ -z "$FILTER_GROUP" || "$FILTER_GROUP" == "2" ]]; then

  ENTRYPOINTS=(
    "scripts/agents/plan.sh"
    "scripts/review/cross-review.sh"
    "scripts/work-queue/claim-item.sh"
    "scripts/work-queue/close-item.sh"
  )

  for ep in "${ENTRYPOINTS[@]}"; do
    fpath="${REPO_ROOT}/${ep}"
    bname="$(basename "$ep")"

    # 2.x.1 file exists
    if [[ -f "$fpath" ]]; then
      pass "2.${bname}.exists"
    else
      fail "2.${bname}.exists"
      continue
    fi

    # 2.x.2 bash syntax valid
    if bash -n "$fpath" 2>/dev/null; then
      pass "2.${bname}.syntax"
    else
      fail "2.${bname}.syntax"
    fi

    # 2.x.3 guard pattern present (references --stage5-check)
    if grep -q "\-\-stage5-check" "$fpath"; then
      pass "2.${bname}.guard_present"
    else
      fail "2.${bname}.guard_present"
    fi

    # 2.x.4 exit 1 handler present for predicate fail
    if grep -q 'stage5_exit.*-eq 1\|"$stage5_exit" -eq 1' "$fpath"; then
      pass "2.${bname}.exit1_handled"
    else
      fail "2.${bname}.exit1_handled"
    fi

    # 2.x.5 exit 2 handler present for infra fail
    if grep -q 'stage5_exit.*-eq 2\|"$stage5_exit" -eq 2' "$fpath"; then
      pass "2.${bname}.exit2_handled"
    else
      fail "2.${bname}.exit2_handled"
    fi

    # 2.x.6 uses uv run --no-project python (not bare python3)
    # uv run appears on the line BEFORE --stage5-check in the heredoc pattern
    if grep -B3 "\-\-stage5-check" "$fpath" | grep -q "uv run --no-project python"; then
      pass "2.${bname}.uv_invocation"
    else
      fail "2.${bname}.uv_invocation"
    fi

    # 2.x.7 fail-closed: guard uses ! -f (not fail-open -f pattern)
    if grep -q '! -f.*STAGE5_CHECKER\|STAGE5_CHECKER.*! -f' "$fpath"; then
      pass "2.${bname}.fail_closed"
    else
      fail "2.${bname}.fail_closed (entrypoint is fail-open when checker missing)"
    fi
  done

  # 2.cross-review: --wrk-id parameter present
  cross_review="${REPO_ROOT}/scripts/review/cross-review.sh"
  if grep -q "\-\-wrk-id" "$cross_review"; then
    pass "2.cross-review.wrk_id_param"
  else
    fail "2.cross-review.wrk_id_param"
  fi

  # 2.cross-review: gate only fires for --type plan (not all review types)
  if grep -q 'REVIEW_TYPE.*==.*plan.*&&.*-n.*WRK_ID\|type.*plan.*wrk.id' "$cross_review"; then
    pass "2.cross-review.gate_scoped_to_plan_type"
  else
    fail "2.cross-review.gate_scoped_to_plan_type"
  fi

  # 2.AC-57b: all four callers must be guarded (fully hardened state)
  ALL_GUARDED=true
  for ep in "${ENTRYPOINTS[@]}"; do
    if ! grep -q "\-\-stage5-check" "${REPO_ROOT}/${ep}" 2>/dev/null; then
      ALL_GUARDED=false
      break
    fi
  done
  if $ALL_GUARDED; then
    pass "2.AC-57b all_four_callers_guarded"
  else
    fail "2.AC-57b all_four_callers_guarded"
  fi

fi

# ─── GROUP 3: Bootstrap dry-run inventory ─────────────────────────────────────
group 3 "Bootstrap dry-run inventory"
if [[ -z "$FILTER_GROUP" || "$FILTER_GROUP" == "3" ]]; then

  # 3.1 bootstrap script exists
  if [[ -f "$BOOTSTRAP" ]]; then
    pass "3.1 bootstrap script exists"
  else
    fail "3.1 bootstrap script exists"
  fi

  # 3.2 bootstrap syntax valid
  if bash -n "$BOOTSTRAP" 2>/dev/null; then
    pass "3.2 bootstrap syntax valid"
  else
    fail "3.2 bootstrap syntax valid"
  fi

  # 3.3 bootstrap --dry-run exits 0 (go decision)
  # Note: decision depends on queue state — skip in CI where queue may have incomplete WRKs
  REPORT_TMP="$(mktemp /tmp/bootstrap-test-report-XXXXXX.yaml)"
  bootstrap_exit=0
  bash "$BOOTSTRAP" --dry-run --report "$REPORT_TMP" >/dev/null 2>&1 || bootstrap_exit=$?
  if [[ "$bootstrap_exit" -eq 0 ]]; then
    pass "3.3 bootstrap --dry-run exits 0 (go)"
  elif [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    skip "3.3 bootstrap --dry-run exits 0 (go)" "CI queue state may differ"
  else
    fail "3.3 bootstrap --dry-run exits 0 (go) — exit $bootstrap_exit"
  fi

  # 3.4 bootstrap report has required fields
  if [[ -f "$REPORT_TMP" ]]; then
    MISSING_FIELDS=()
    for field in decision eligible_wrk_count go_count nogo_count; do
      if ! grep -q "^${field}:" "$REPORT_TMP"; then
        MISSING_FIELDS+=("$field")
      fi
    done
    if [[ ${#MISSING_FIELDS[@]} -eq 0 ]]; then
      pass "3.4 bootstrap report has required fields"
    else
      fail "3.4 bootstrap report missing: ${MISSING_FIELDS[*]}"
    fi
  else
    fail "3.4 bootstrap report file created"
  fi

  # 3.5 bootstrap decision is 'go'
  if grep -q 'decision: "go"' "$REPORT_TMP" 2>/dev/null; then
    pass "3.5 bootstrap decision=go"
  else
    # Try unquoted form too
    if grep -q "^decision: go" "$REPORT_TMP" 2>/dev/null; then
      pass "3.5 bootstrap decision=go"
    elif [[ -n "${GITHUB_ACTIONS:-}" ]]; then
      skip "3.5 bootstrap decision=go" "CI queue state may differ"
    else
      decision_val="$(grep "^decision:" "$REPORT_TMP" 2>/dev/null || echo 'missing')"
      fail "3.5 bootstrap decision=go — got: $decision_val"
    fi
  fi

  rm -f "$REPORT_TMP"

fi

# ─── GROUP 4: Activation-sim blocking tests ───────────────────────────────────
group 4 "Activation-sim blocking tests (requires --sim flag)"
if [[ -z "$FILTER_GROUP" || "$FILTER_GROUP" == "4" ]]; then

  if ! $RUN_SIM; then
    skip "4.all" "pass --sim to run activation simulation tests"
  else
    # Temporarily swap activation to full, run blocking test, restore
    BACKUP_CONFIG="${CONFIG}.bak_testrun_$$"
    RESTORE_NEEDED=false

    cleanup_sim() {
      if $RESTORE_NEEDED && [[ -f "$BACKUP_CONFIG" ]]; then
        mv "$BACKUP_CONFIG" "$CONFIG"
      fi
    }
    trap cleanup_sim EXIT

    cp "$CONFIG" "$BACKUP_CONFIG"
    RESTORE_NEEDED=true

    # Write full-activation config with test WRK id list
    cat > "$CONFIG" << 'SIMCFG'
schema_version: "1.0"
owned_by_wrk: WRK-1017
activation: full
gate_activation_commit: "test-sim"
checker_timeout_seconds: 30
git_history_timeout_seconds: 8
emergency_bypass_until: ""
emergency_bypass_reason: ""
emergency_bypass_approved_by: ""
human_authority_allowlist:
  - user
  - vamsee
SIMCFG

    # 4.1 checker blocks on WRK with no evidence (activation=full)
    sim_exit=0
    uv run --no-project python "$CHECKER" --stage5-check WRK-9888 >/dev/null 2>&1 || sim_exit=$?
    # WRK-9888 doesn't exist → no assets → should fail with exit 1 or 2
    if [[ "$sim_exit" -ne 0 ]]; then
      pass "4.1 checker blocks non-existent WRK when activation=full (exit $sim_exit)"
    else
      fail "4.1 checker blocks non-existent WRK when activation=full"
    fi

    # 4.2 checker blocks on WRK-1017 without evidence (activation=full, no exemption)
    # WRK-1017 has its own assets but no common-draft with approve_as_is under full activation
    # The checker should check for common-draft.yaml → if missing or not approve_as_is → exit 1
    sim_1017_exit=0
    sim_1017_out="$(uv run --no-project python "$CHECKER" --stage5-check WRK-1017 2>&1)" || sim_1017_exit=$?
    # WRK-1017 has migration exemption — but exemption approved_by=user which IS in allowlist
    # So if exemption exists → should pass (exit 0) even under full activation
    # This tests exemption authority validation
    if [[ "$sim_1017_exit" -eq 0 ]]; then
      pass "4.2 WRK-1017 passes under full activation via valid migration exemption"
    else
      fail "4.2 WRK-1017 passes under full activation via valid migration exemption — exit $sim_1017_exit output: $sim_1017_out"
    fi

    # Restore original config
    mv "$BACKUP_CONFIG" "$CONFIG"
    RESTORE_NEEDED=false
    trap - EXIT

    pass "4.sim config restored"
  fi

fi

# ─── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "=== RESULTS: $PASS passed, $FAIL failed ==="
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
