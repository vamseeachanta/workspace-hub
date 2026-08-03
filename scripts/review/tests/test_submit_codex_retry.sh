#!/usr/bin/env bash
# test_submit_codex_retry.sh — regression tests for #3578.
#
# Covers the compact-retry path in scripts/review/submit-to-codex.sh: that the
# retry fires on the documented failure shapes, that it truncates its payload,
# that it does NOT fire on a good first response, and — the #3578 defect class —
# that the codex subprocess never inherits the caller's stdin pipe.
#
# Every test drives the real script against a MOCK codex on PATH, so no live
# provider call, no network, and no quota spend. Invocations are counted through
# a file the mock appends to, because the mock runs in a subprocess and cannot
# mutate the test shell's variables.
#
# Plan: docs/plans/2026-07-29-issue-3578-codex-retry-stdin-hang.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SUBMIT="${REPO_ROOT}/scripts/review/submit-to-codex.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() { TESTS_RUN=$((TESTS_RUN + 1)); echo ""; echo "--- Test ${TESTS_RUN}: $1 ---"; }
pass() { TESTS_PASSED=$((TESTS_PASSED + 1)); echo "  PASS: $1"; }
fail() { TESTS_FAILED=$((TESTS_FAILED + 1)); echo "  FAIL: $1"; [[ -n "${2:-}" ]] && echo "        $2"; }

# ── Mock codex ────────────────────────────────────────────────────────────
#
# Behaviour is driven by files in the mock's own directory so each test can
# script a different first/second-call outcome:
#   calls        — one line appended per invocation (invocation counter)
#   exit_codes   — whitespace-separated exit codes, Nth applies to Nth call
#   stdin_seen   — written when the mock reads ANY byte from stdin
#   argv_chars   — prompt length per call, one line per invocation
#
# The stdin probe is the heart of the #3578 test. `read -t 0` returns success
# when a descriptor has data ready; against /dev/null the read hits immediate
# EOF and returns failure. So "the mock saw stdin data" == "stdin was NOT
# isolated" == the hang condition, observed without ever having to hang.
write_codex_mock() {
  local bin_dir="$1"
  mkdir -p "$bin_dir"
  cat > "$bin_dir/codex" <<'MOCK'
#!/usr/bin/env bash
STATE="$(cd "$(dirname "$0")" && pwd)"

if [[ "${1:-}" == "--version" ]]; then
  echo "codex-cli ${MOCK_CODEX_VERSION:-0.146.0}"
  exit 0
fi

echo "call" >> "$STATE/calls"
call_no="$(wc -l < "$STATE/calls" | tr -d ' ')"

# Record the prompt length. `exec` is $1; the prompt is $2.
printf '%s\n' "${#2}" >> "$STATE/argv_chars"

# Probe stdin for actual DATA, not mere readiness.
#
# `read -t 0` is wrong here: it reports whether the descriptor is *ready*, and
# /dev/null is always ready (it returns EOF immediately), so it false-positives
# on exactly the isolated case we want to prove. Read a real byte instead:
#   /dev/null      -> EOF, read fails, $probe empty  => isolated (good)
#   inherited pipe -> "noise" lands in $probe        => NOT isolated (the bug)
probe=""
IFS= read -r -t 2 probe <&0 2>/dev/null || true
if [[ -n "$probe" ]]; then
  echo "stdin-data-visible (call ${call_no}): ${probe:0:20}" >> "$STATE/stdin_seen"
fi

# Locate --output-last-message so we can emit a body on a successful call.
out_file=""
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "--output-last-message" ]]; then out_file="${2:-}"; break; fi
  shift
done

codes="$(cat "$STATE/exit_codes" 2>/dev/null || echo 0)"
read -r -a code_arr <<< "$codes"
idx=$((call_no - 1))
rc="${code_arr[$idx]:-${code_arr[-1]:-0}}"

if [[ "$rc" == "0" && -n "$out_file" ]]; then
  printf '%s\n' '{"verdict":"MINOR","summary":"mock review body"}' > "$out_file"
fi
exit "$rc"
MOCK
  chmod +x "$bin_dir/codex"
}

# Run submit-to-codex.sh with the mock on PATH.
# Critically, stdin is a LIVE PIPE that stays open — reproducing the
# orchestrator shape from #3578. If the script fails to isolate stdin, the
# mock's probe sees data.
run_submit() {
  local bin_dir="$1" content_file="$2"
  # `yes` alone holds the pipe open for the script's lifetime and dies of
  # SIGPIPE when it exits — no background sleep, so no orphaned processes.
  yes "noise" 2>/dev/null \
    | PATH="$bin_dir:$PATH" \
      CODEX_BIN="$bin_dir/codex" \
      CODEX_TIMEOUT_SECONDS=20 \
      CODEX_VERSION_GUARD_CEILING=0.0.0 \
      bash "$SUBMIT" --file "$content_file" --prompt "review this" \
      >"$bin_dir/out.txt" 2>"$bin_dir/err.txt"
  echo $?
}

new_case() {
  local td; td="$(mktemp -d)"
  write_codex_mock "$td/bin"
  printf 'def add(a, b):\n    return a - b\n' > "$td/content.py"
  echo "$td"
}

calls_made() { wc -l < "$1/bin/calls" 2>/dev/null | tr -d ' ' || echo 0; }

# ── Tests ─────────────────────────────────────────────────────────────────

run_test "retry does NOT fire when the first invocation returns valid output"
td="$(new_case)"; echo "0" > "$td/bin/exit_codes"
rc="$(run_submit "$td/bin" "$td/content.py" || true)"
n="$(calls_made "$td")"
if [[ "$n" == "1" ]]; then
  pass "codex invoked exactly once (rc=$rc)"
else
  fail "expected exactly 1 invocation, got $n" "$(tail -3 "$td/bin/err.txt" 2>/dev/null)"
fi
rm -rf "$td"

run_test "retry fires when the first invocation exits non-zero (124 timeout shape)"
td="$(new_case)"; echo "124 0" > "$td/bin/exit_codes"
rc="$(run_submit "$td/bin" "$td/content.py" || true)"
n="$(calls_made "$td")"
if [[ "$n" == "2" ]]; then
  pass "codex invoked twice — compact retry fired (rc=$rc)"
else
  fail "expected 2 invocations, got $n" "$(tail -3 "$td/bin/err.txt" 2>/dev/null)"
fi
rm -rf "$td"

run_test "retry fires when the first invocation exits 0 but writes no output"
td="$(new_case)"; echo "5 0" > "$td/bin/exit_codes"
rc="$(run_submit "$td/bin" "$td/content.py" || true)"
n="$(calls_made "$td")"
if [[ "$n" == "2" ]]; then
  pass "codex invoked twice on empty-output first call (rc=$rc)"
else
  fail "expected 2 invocations, got $n" "$(tail -3 "$td/bin/err.txt" 2>/dev/null)"
fi
rm -rf "$td"

run_test "#3578 core: codex never sees the caller's stdin pipe (first call)"
td="$(new_case)"; echo "0" > "$td/bin/exit_codes"
run_submit "$td/bin" "$td/content.py" >/dev/null || true
if [[ ! -s "$td/bin/stdin_seen" ]]; then
  pass "stdin isolated — mock observed immediate EOF, not the caller's pipe"
else
  fail "codex inherited the caller's stdin pipe" "$(cat "$td/bin/stdin_seen")"
fi
rm -rf "$td"

run_test "#3578 core: codex never sees the caller's stdin pipe (RETRY call)"
td="$(new_case)"; echo "124 0" > "$td/bin/exit_codes"
run_submit "$td/bin" "$td/content.py" >/dev/null || true
n="$(calls_made "$td")"
if [[ "$n" != "2" ]]; then
  fail "retry did not fire, so stdin isolation on the retry path is untested" "calls=$n"
elif [[ ! -s "$td/bin/stdin_seen" ]]; then
  pass "stdin isolated on BOTH the initial call and the compact retry"
else
  fail "retry path inherited the caller's stdin pipe" "$(cat "$td/bin/stdin_seen")"
fi
rm -rf "$td"

run_test "compact retry truncates its payload to CODEX_COMPACT_RETRY_CHARS"
td="$(mktemp -d)"; write_codex_mock "$td/bin"; echo "124 0" > "$td/bin/exit_codes"
# 50K of content — comfortably above the 24000-char default.
head -c 50000 /dev/zero | tr '\0' 'x' > "$td/content.py"
yes "noise" 2>/dev/null \
  | PATH="$td/bin:$PATH" CODEX_BIN="$td/bin/codex" \
    CODEX_TIMEOUT_SECONDS=20 CODEX_VERSION_GUARD_CEILING=0.0.0 \
    CODEX_COMPACT_RETRY_CHARS=24000 \
    bash "$SUBMIT" --file "$td/content.py" --prompt "review" \
    >"$td/bin/out.txt" 2>"$td/bin/err.txt" || true
if [[ -s "$td/bin/argv_chars" ]]; then
  first="$(sed -n '1p' "$td/bin/argv_chars")"
  second="$(sed -n '2p' "$td/bin/argv_chars")"
  if [[ -n "$second" && "$second" -lt "$first" ]]; then
    pass "retry payload shrank (${first} -> ${second} chars)"
  else
    fail "retry payload was not truncated" "first=${first} second=${second:-<none>}"
  fi
else
  fail "mock recorded no invocations" "$(tail -3 "$td/bin/err.txt" 2>/dev/null)"
fi
rm -rf "$td"

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "Tests run:    ${TESTS_RUN}"
echo "Tests passed: ${TESTS_PASSED}"
echo "Tests failed: ${TESTS_FAILED}"
echo "========================================"
[[ "${TESTS_FAILED}" -eq 0 ]]
