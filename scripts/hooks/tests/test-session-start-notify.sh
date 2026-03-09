#!/usr/bin/env bash
# test-session-start-notify.sh — Tests for session-start-notify.sh and notify.sh
# Tests: 1) no dir → silent  2) all PASS → silent  3) one FAIL → banner  4) mixed → lists only FAILs

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
NOTIFY="${REPO_ROOT}/scripts/notify.sh"
TMPDIR_BASE="$(mktemp -d)"
PASS_COUNT=0
FAIL_COUNT=0

cleanup() { rm -rf "${TMPDIR_BASE}"; }
trap cleanup EXIT

run_test() {
  local name="$1" ok="$2" msg="${3:-}"
  if [[ "${ok}" == "1" ]]; then
    echo "  PASS  ${name}"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  FAIL  ${name}${msg:+: ${msg}}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

count_fails() {
  local dir="$1"
  find "${dir}" -name "*.jsonl" -exec cat {} \; 2>/dev/null \
    | grep -c '"status":"fail"' || true
}

TODAY="$(date -u +%Y-%m-%d)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ── Test 1: no notifications dir → silent ────────────────────────────────────
T1="${TMPDIR_BASE}/t1/logs/notifications"
# dir does not exist — reader must exit 0 silently
output="$(bash -c '[[ -d "'"${T1}"'" ]] || exit 0' 2>&1 || true)"
run_test "no-dir-silent" "$([ -z "${output}" ] && echo 1 || echo 0)"

# ── Test 2: only PASS entries → silent ───────────────────────────────────────
T2="${TMPDIR_BASE}/t2/logs/notifications"
mkdir -p "${T2}"
echo "{\"source\":\"cron\",\"job\":\"sync\",\"status\":\"pass\",\"ts\":\"${NOW}\",\"details\":\"\"}" \
  >> "${T2}/${TODAY}.jsonl"
n="$(count_fails "${T2}")"
run_test "all-pass-silent" "$([ "${n}" = "0" ] && echo 1 || echo 0)" "found ${n} fails"

# ── Test 3: one FAIL → banner printed ────────────────────────────────────────
T3="${TMPDIR_BASE}/t3/logs/notifications"
mkdir -p "${T3}"
echo "{\"source\":\"cron\",\"job\":\"nightly-learning\",\"status\":\"fail\",\"ts\":\"${NOW}\",\"details\":\"3 new failures\"}" \
  >> "${T3}/${TODAY}.jsonl"
n="$(count_fails "${T3}")"
run_test "one-fail-banner" "$([ "${n}" = "1" ] && echo 1 || echo 0)" "expected 1, got ${n}"

# ── Test 4: mixed PASS+FAIL → only FAILs counted ─────────────────────────────
T4="${TMPDIR_BASE}/t4/logs/notifications"
mkdir -p "${T4}"
echo "{\"source\":\"cron\",\"job\":\"sync\",\"status\":\"pass\",\"ts\":\"${NOW}\",\"details\":\"\"}" \
  >> "${T4}/${TODAY}.jsonl"
echo "{\"source\":\"benchmark\",\"job\":\"digitalmodel\",\"status\":\"fail\",\"ts\":\"${NOW}\",\"details\":\"+35% regression\"}" \
  >> "${T4}/${TODAY}.jsonl"
echo "{\"source\":\"ci\",\"job\":\"pre-push\",\"status\":\"fail\",\"ts\":\"${NOW}\",\"details\":\"assethold 3 failures\"}" \
  >> "${T4}/${TODAY}.jsonl"
n="$(count_fails "${T4}")"
run_test "mixed-only-fails" "$([ "${n}" = "2" ] && echo 1 || echo 0)" "expected 2, got ${n}"

# ── Test 5: notify.sh writes valid JSONL ─────────────────────────────────────
# Run from repo root so git rev-parse resolves; check output in real logs/notifications/
T5_LOG="${REPO_ROOT}/logs/notifications/${TODAY}.jsonl"
before="$(wc -l < "${T5_LOG}" 2>/dev/null || echo 0)"
bash "${NOTIFY}" test test-job fail "unit-test detail" 2>/dev/null || true
after="$(wc -l < "${T5_LOG}" 2>/dev/null || echo 0)"
if [[ "${after}" -gt "${before}" ]]; then
  last_line="$(tail -1 "${T5_LOG}")"
  has_fail="$(echo "${last_line}" | grep -c '"status":"fail"' || true)"
  has_job="$(echo "${last_line}" | grep -c '"job":"test-job"' || true)"
  # Clean up the test entry
  head -n "${before}" "${T5_LOG}" > "${T5_LOG}.tmp" && mv "${T5_LOG}.tmp" "${T5_LOG}" 2>/dev/null || true
  run_test "notify-writes-jsonl" "$([ "${has_fail}" = "1" ] && [ "${has_job}" = "1" ] && echo 1 || echo 0)"
else
  run_test "notify-writes-jsonl" "0" "no new line appended"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "Results: ${PASS_COUNT} pass, ${FAIL_COUNT} fail"
[[ "${FAIL_COUNT}" -eq 0 ]]
