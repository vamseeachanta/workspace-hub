#!/usr/bin/env bash
# test-user-review-evidence-writers.sh — Producer-script regression tests (AC-57e, WRK-1017)
#
# Tests log-user-review-browser-open.sh and log-user-review-publish.sh
# for correct schema/provenance fields and error handling.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
BROWSER_OPEN="${REPO_ROOT}/scripts/work-queue/log-user-review-browser-open.sh"
PUBLISH="${REPO_ROOT}/scripts/work-queue/log-user-review-publish.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; (( PASS++ )) || true; }
fail() { echo "  FAIL: $1"; (( FAIL++ )) || true; }

# ── Test fixtures ──────────────────────────────────────────────────────────────
TMPDIR_ROOT="$(mktemp -d)"
TEST_WRK="WRK-99998"  # high number, won't collide with real WRKs
ASSETS_DIR="${REPO_ROOT}/.claude/work-queue/assets/${TEST_WRK}"
EVIDENCE_DIR="${ASSETS_DIR}/evidence"
# Create a dummy HTML file for the browser-open script
HTML_FILE="${TMPDIR_ROOT}/dummy-review.html"
echo "<html><body>test</body></html>" > "$HTML_FILE"

cleanup() {
  rm -rf "$TMPDIR_ROOT"
  rm -rf "$ASSETS_DIR"
}
trap cleanup EXIT

echo "=== Producer-script regression tests ==="
echo "    test WRK: $TEST_WRK"
echo ""

# ── log-user-review-browser-open.sh ───────────────────────────────────────────
echo "--- log-user-review-browser-open.sh ---"

# T1: script exists
if [[ -f "$BROWSER_OPEN" ]]; then
  pass "T1 browser-open script exists"
else
  fail "T1 browser-open script exists"; exit 1
fi

# T2: syntax valid
if bash -n "$BROWSER_OPEN" 2>/dev/null; then
  pass "T2 browser-open syntax valid"
else
  fail "T2 browser-open syntax valid"
fi

# T3: missing WRK id → exits non-zero
bo_exit=0
bash "$BROWSER_OPEN" >/dev/null 2>&1 || bo_exit=$?
if [[ "$bo_exit" -ne 0 ]]; then
  pass "T3 browser-open missing WRK exits non-zero"
else
  fail "T3 browser-open missing WRK exits non-zero"
fi

# T4: invalid stage → exits non-zero
bo_exit=0
bash "$BROWSER_OPEN" "$TEST_WRK" --stage invalid_stage --html "$HTML_FILE" --no-open >/dev/null 2>&1 || bo_exit=$?
if [[ "$bo_exit" -ne 0 ]]; then
  pass "T4 browser-open invalid stage exits non-zero"
else
  fail "T4 browser-open invalid stage exits non-zero"
fi

# T5: missing --html → exits non-zero
bo_exit=0
bash "$BROWSER_OPEN" "$TEST_WRK" --stage plan_draft --no-open >/dev/null 2>&1 || bo_exit=$?
if [[ "$bo_exit" -ne 0 ]]; then
  pass "T5 browser-open missing --html exits non-zero"
else
  fail "T5 browser-open missing --html exits non-zero"
fi

# T6: nonexistent HTML file → exits non-zero
bo_exit=0
bash "$BROWSER_OPEN" "$TEST_WRK" --stage plan_draft --html "/no/such/file.html" --no-open >/dev/null 2>&1 || bo_exit=$?
if [[ "$bo_exit" -ne 0 ]]; then
  pass "T6 browser-open nonexistent HTML exits non-zero"
else
  fail "T6 browser-open nonexistent HTML exits non-zero"
fi

# T7: successful plan_draft event write
mkdir -p "$EVIDENCE_DIR"
bash "$BROWSER_OPEN" "$TEST_WRK" --stage plan_draft --html "$HTML_FILE" --no-open >/dev/null 2>&1
BO_FILE="${EVIDENCE_DIR}/user-review-browser-open.yaml"
if [[ -f "$BO_FILE" ]]; then
  pass "T7 browser-open creates evidence file"
else
  fail "T7 browser-open creates evidence file"
fi

# T8: evidence file has 'events' key
if [[ -f "$BO_FILE" ]] && grep -q "^events:" "$BO_FILE"; then
  pass "T8 browser-open evidence has events key"
else
  fail "T8 browser-open evidence has events key"
fi

# T9: event has required fields (stage, opened_in_default_browser, html_ref, opened_at, reviewer)
if [[ -f "$BO_FILE" ]]; then
  MISSING_FIELDS=()
  for field in stage opened_in_default_browser html_ref opened_at reviewer; do
    if ! grep -q "$field" "$BO_FILE"; then
      MISSING_FIELDS+=("$field")
    fi
  done
  if [[ ${#MISSING_FIELDS[@]} -eq 0 ]]; then
    pass "T9 browser-open event has required schema fields"
  else
    fail "T9 browser-open event missing fields: ${MISSING_FIELDS[*]}"
  fi
fi

# T10: opened_in_default_browser is false when --no-open given
if grep -q "opened_in_default_browser: false" "$BO_FILE" 2>/dev/null; then
  pass "T10 browser-open records opened_in_default_browser=false with --no-open"
else
  fail "T10 browser-open records opened_in_default_browser=false with --no-open"
fi

# T11: YAML is parseable
uv run --no-project python -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]).read()); print('ok')" \
  "$BO_FILE" >/dev/null 2>&1 && pass "T11 browser-open YAML is valid" || fail "T11 browser-open YAML is valid"

# T12: append second event (plan_final) to same file
bash "$BROWSER_OPEN" "$TEST_WRK" --stage plan_final --html "$HTML_FILE" --no-open >/dev/null 2>&1
EVENT_COUNT=$(uv run --no-project python -c \
  "import yaml, sys; d=yaml.safe_load(open(sys.argv[1])); print(len(d.get('events', [])))" \
  "$BO_FILE" 2>/dev/null || echo 0)
if [[ "$EVENT_COUNT" -eq 2 ]]; then
  pass "T12 browser-open appends second event (plan_final)"
else
  fail "T12 browser-open appends second event — got $EVENT_COUNT events"
fi

echo ""

# ── log-user-review-publish.sh ────────────────────────────────────────────────
echo "--- log-user-review-publish.sh ---"

# T13: script exists
if [[ -f "$PUBLISH" ]]; then
  pass "T13 publish script exists"
else
  fail "T13 publish script exists"; exit 1
fi

# T14: syntax valid
if bash -n "$PUBLISH" 2>/dev/null; then
  pass "T14 publish syntax valid"
else
  fail "T14 publish syntax valid"
fi

# T15: missing WRK id → exits non-zero
pub_exit=0
bash "$PUBLISH" >/dev/null 2>&1 || pub_exit=$?
if [[ "$pub_exit" -ne 0 ]]; then
  pass "T15 publish missing WRK exits non-zero"
else
  fail "T15 publish missing WRK exits non-zero"
fi

# T16: invalid stage → exits non-zero
pub_exit=0
bash "$PUBLISH" "$TEST_WRK" --stage invalid_stage --doc dummy.md >/dev/null 2>&1 || pub_exit=$?
if [[ "$pub_exit" -ne 0 ]]; then
  pass "T16 publish invalid stage exits non-zero"
else
  fail "T16 publish invalid stage exits non-zero"
fi

# T17: missing --doc → exits non-zero
pub_exit=0
bash "$PUBLISH" "$TEST_WRK" --stage plan_draft >/dev/null 2>&1 || pub_exit=$?
if [[ "$pub_exit" -ne 0 ]]; then
  pass "T17 publish missing --doc exits non-zero"
else
  fail "T17 publish missing --doc exits non-zero"
fi

# T18: successful plan_draft event write
bash "$PUBLISH" "$TEST_WRK" --stage plan_draft --doc "$HTML_FILE" \
  --commit "abc1234" --remote "origin" --branch "main" >/dev/null 2>&1
PUB_FILE="${EVIDENCE_DIR}/user-review-publish.yaml"
if [[ -f "$PUB_FILE" ]]; then
  pass "T18 publish creates evidence file"
else
  fail "T18 publish creates evidence file"
fi

# T19: evidence file has 'events' key
if [[ -f "$PUB_FILE" ]] && grep -q "^events:" "$PUB_FILE"; then
  pass "T19 publish evidence has events key"
else
  fail "T19 publish evidence has events key"
fi

# T20: event has required provenance fields (stage, pushed_to_origin, remote, branch, commit, documents, published_at, reviewer)
if [[ -f "$PUB_FILE" ]]; then
  MISSING_FIELDS=()
  for field in stage pushed_to_origin remote branch commit documents published_at reviewer; do
    if ! grep -q "$field" "$PUB_FILE"; then
      MISSING_FIELDS+=("$field")
    fi
  done
  if [[ ${#MISSING_FIELDS[@]} -eq 0 ]]; then
    pass "T20 publish event has required provenance fields"
  else
    fail "T20 publish event missing fields: ${MISSING_FIELDS[*]}"
  fi
fi

# T21: pushed_to_origin is true
if grep -q "pushed_to_origin: true" "$PUB_FILE" 2>/dev/null; then
  pass "T21 publish records pushed_to_origin=true"
else
  fail "T21 publish records pushed_to_origin=true"
fi

# T22: YAML is parseable
uv run --no-project python -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]).read()); print('ok')" \
  "$PUB_FILE" >/dev/null 2>&1 && pass "T22 publish YAML is valid" || fail "T22 publish YAML is valid"

# T23: append second event (plan_final)
bash "$PUBLISH" "$TEST_WRK" --stage plan_final --doc "$HTML_FILE" >/dev/null 2>&1
PUB_EVENT_COUNT=$(uv run --no-project python -c \
  "import yaml, sys; d=yaml.safe_load(open(sys.argv[1])); print(len(d.get('events', [])))" \
  "$PUB_FILE" 2>/dev/null || echo 0)
if [[ "$PUB_EVENT_COUNT" -eq 2 ]]; then
  pass "T23 publish appends second event (plan_final)"
else
  fail "T23 publish appends second event — got $PUB_EVENT_COUNT events"
fi

echo ""
echo "=== RESULTS: $PASS passed, $FAIL failed ==="
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
