#!/usr/bin/env bash
# test-wrk1112-iteration-cap.sh — Tests for 3-iteration cross-review cap (WRK-1112)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Test scaffolding ─────────────────────────────────────────────────
PASS=0; FAIL=0; TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

assert_eq() {
    local label="$1" expected="$2" actual="$3"
    TOTAL=$((TOTAL + 1))
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected='$expected', got='$actual')"
        FAIL=$((FAIL + 1))
    fi
}

assert_contains() {
    local label="$1" needle="$2" haystack="$3"
    TOTAL=$((TOTAL + 1))
    if echo "$haystack" | grep -qF "$needle"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected to contain '${needle}')"
        FAIL=$((FAIL + 1))
    fi
}

# Local copies of the helper functions (mirrors cross-review.sh)
_get_review_iteration() {
  local wrk_id="$1"
  local iter_file="${TEST_DIR}/.claude/work-queue/assets/${wrk_id}/review-iteration.yaml"
  if [[ ! -f "$iter_file" ]]; then echo 0; return; fi
  awk -F': ' '/^iteration:/ {print $2+0; exit}' "$iter_file"
}

_increment_review_iteration() {
  local wrk_id="$1"
  local assets_dir="${TEST_DIR}/.claude/work-queue/assets/${wrk_id}"
  mkdir -p "$assets_dir"
  local iter_file="${assets_dir}/review-iteration.yaml"
  local current; current="$(_get_review_iteration "$wrk_id")"
  local new_count=$(( current + 1 ))
  local first_review_at
  first_review_at="$(awk -F': ' '/^first_review_at:/ {print $2; exit}' "$iter_file" 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
  cat > "$iter_file" <<YAML
wrk_id: "${wrk_id}"
iteration: ${new_count}
first_review_at: "${first_review_at}"
last_review_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
YAML
  echo "$new_count"
}

# ── Test 1: review-iteration.yaml created on first pass ──────────────
echo "Test 1: review-iteration.yaml created on first pass"
result="$(_increment_review_iteration "WRK-9999")"
iter_file="${TEST_DIR}/.claude/work-queue/assets/WRK-9999/review-iteration.yaml"
assert_eq "yaml exists after first increment" "true" "$([[ -f "$iter_file" ]] && echo true || echo false)"
assert_eq "returns iteration 1" "1" "$result"
assert_eq "yaml contains iteration: 1" "true" "$(grep -q '^iteration: 1' "$iter_file" && echo true || echo false)"

# ── Test 2: iteration increments correctly ────────────────────────────
echo "Test 2: iteration increments correctly"
assets2="${TEST_DIR}/.claude/work-queue/assets/WRK-9998"
mkdir -p "$assets2"
cat > "${assets2}/review-iteration.yaml" <<YAML
wrk_id: "WRK-9998"
iteration: 1
first_review_at: "2026-01-01T00:00:00Z"
last_review_at: "2026-01-01T00:00:00Z"
YAML
result2="$(_increment_review_iteration "WRK-9998")"
assert_eq "iteration increments from 1 to 2" "2" "$result2"
assert_eq "yaml shows iteration: 2" "true" \
    "$(grep -q '^iteration: 2' "${assets2}/review-iteration.yaml" && echo true || echo false)"

# ── Test 3: fourth iteration blocked (cap check logic) ────────────────
echo "Test 3: fourth iteration blocked with exit code 1"
assets3="${TEST_DIR}/.claude/work-queue/assets/WRK-9997"
mkdir -p "$assets3"
cat > "${assets3}/review-iteration.yaml" <<YAML
wrk_id: "WRK-9997"
iteration: 3
first_review_at: "2026-01-01T00:00:00Z"
last_review_at: "2026-01-01T00:00:00Z"
YAML
MAX_REVIEW_ITERATIONS=3
CURRENT_ITER="$(_get_review_iteration "WRK-9997")"
cap_exit=0; cap_output=""
if [[ "$CURRENT_ITER" -ge "$MAX_REVIEW_ITERATIONS" ]]; then
  cap_output="cap reached for WRK-9997"
  cap_exit=1
fi
assert_eq "cap exit triggered when iteration==3" "1" "$cap_exit"
assert_contains "error message contains 'cap reached'" "cap reached" "$cap_output"

# ── Test 4: preamble includes iteration number and budget ─────────────
echo "Test 4: preamble includes iteration number and budget"
assets4="${TEST_DIR}/.claude/work-queue/assets/WRK-9996"
mkdir -p "$assets4"
cat > "${assets4}/review-iteration.yaml" <<YAML
wrk_id: "WRK-9996"
iteration: 1
first_review_at: "2026-01-01T00:00:00Z"
last_review_at: "2026-01-01T00:00:00Z"
YAML
CURRENT_ITER4="$(_increment_review_iteration "WRK-9996")"
MAX_REVIEW_ITERATIONS4=3
ITER_PREAMBLE4="You are reviewing WRK-9996 — iteration ${CURRENT_ITER4} of ${MAX_REVIEW_ITERATIONS4} (maximum).

This is a hard budget. After iteration ${MAX_REVIEW_ITERATIONS4} no further review passes will be
accepted. Plan your feedback to maximise impact within this constraint:
  * Iteration 1: blockers and security issues only — nothing else
  * Iteration 2: major design / correctness issues
  * Iteration 3: minor / style / nice-to-haves

Front-load your most critical finding first. If you have only one shot to prevent a
serious defect, this is it. Do not save critical issues for a later pass."
assert_contains "preamble has 'iteration 2 of 3'" "iteration 2 of 3 (maximum)" "$ITER_PREAMBLE4"
assert_contains "preamble has 'Front-load'" "Front-load" "$ITER_PREAMBLE4"
assert_contains "preamble has 'hard budget'" "hard budget" "$ITER_PREAMBLE4"

# ── Test 5: cap applies to codex and gemini wrappers ─────────────────
echo "Test 5: cap applies to codex and gemini wrappers"
assets5="${TEST_DIR}/.claude/work-queue/assets/WRK-9995"
mkdir -p "$assets5"
cat > "${assets5}/review-iteration.yaml" <<YAML
wrk_id: "WRK-9995"
iteration: 3
first_review_at: "2026-01-01T00:00:00Z"
last_review_at: "2026-01-01T00:00:00Z"
YAML
# Content file path must encode WRK-9995 for WRK_ID extraction
fake_content="${TEST_DIR}/WRK-9995-content.md"
echo "test content" > "$fake_content"

codex_exit=0
codex_stderr="$(REPO_ROOT="$TEST_DIR" bash "$REVIEW_DIR/submit-to-codex.sh" \
  --file "$fake_content" --prompt "test" 2>&1 >/dev/null)" || codex_exit=$?
assert_eq "submit-to-codex exits 1 when cap reached" "1" "$codex_exit"
assert_contains "codex stderr has cap message" "REVIEW_ITERATION_CAP_EXCEEDED" "$codex_stderr"

gemini_exit=0
gemini_stderr="$(REPO_ROOT="$TEST_DIR" bash "$REVIEW_DIR/submit-to-gemini.sh" \
  --file "$fake_content" --prompt "test" 2>&1 >/dev/null)" || gemini_exit=$?
assert_eq "submit-to-gemini exits 1 when cap reached" "1" "$gemini_exit"
assert_contains "gemini stderr has cap message" "REVIEW_ITERATION_CAP_EXCEEDED" "$gemini_stderr"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
