#!/usr/bin/env bash
# test-test-health-check.sh — Unit tests for test-health-check.sh helper functions.
# Tests: _is_impl_file, _is_test_file, _expected_test_basenames, _json_str
#
# Usage:
#   bash scripts/test/test-test-health-check.sh
#
# Exit codes:
#   0 — all tests pass
#   1 — one or more tests failed
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SUBJECT="${WORKSPACE_HUB}/scripts/readiness/test-health-check.sh"

# ---------------------------------------------------------------------------
# Minimal test harness
# ---------------------------------------------------------------------------
_pass_count=0
_fail_count=0

_pass() { echo "  PASS  $1"; _pass_count=$(( _pass_count + 1 )); }
_fail() { echo "  FAIL  $1"; _fail_count=$(( _fail_count + 1 )); }

assert_true()  {
  local desc="$1"; shift
  if "$@" &>/dev/null; then _pass "$desc"; else _fail "$desc"; fi
}
assert_false() {
  local desc="$1"; shift
  if ! "$@" &>/dev/null; then _pass "$desc"; else _fail "$desc"; fi
}
assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then _pass "$desc"
  else _fail "$desc (expected='${expected}' got='${actual}')"; fi
}
assert_contains() {
  local desc="$1" needle="$2" haystack="$3"
  if [[ "$haystack" == *"$needle"* ]]; then _pass "$desc"
  else _fail "$desc (needle='${needle}' not in '${haystack}')"; fi
}

# ---------------------------------------------------------------------------
# Source only the helper functions from the subject script.
# We override the main execution block by setting a guard variable.
# The subject script uses `exit 0` at the end — source in a subshell is not
# needed; we parse out function definitions manually with a sourcing shim.
# ---------------------------------------------------------------------------
[[ -f "$SUBJECT" ]] || { echo "ERROR: subject not found: $SUBJECT" >&2; exit 1; }

# Extract and eval only the function definitions (lines between first `() {`
# and their matching closing brace), skipping the main execution block.
# Approach: source the file but redirect exit to a no-op via a subshell trick.
# We wrap in a function to catch the final `exit 0` gracefully.
_load_subject() {
  # Temporarily override exit to prevent sourcing from terminating the shell
  # shellcheck disable=SC1090
  (
    # Provide stub for mkdir and git to prevent side-effects during sourcing
    mkdir() { true; }
    # Source within subshell — functions become available here only, so we
    # print them for eval in the parent shell.
    source "$SUBJECT" 2>/dev/null || true
    # Emit each function definition for parent to eval
    declare -f _json_str _is_impl_file _is_test_file \
               _expected_test_basenames _analyse_repo 2>/dev/null || true
  )
}

# Eval the function definitions into the current shell
eval "$(_load_subject)"

echo "=== test-health-check.sh unit tests ==="
echo ""

# ---------------------------------------------------------------------------
# Tests: _is_impl_file
# ---------------------------------------------------------------------------
echo "--- _is_impl_file ---"

assert_true  "impl: src/module.py"         _is_impl_file "src/module.py"
assert_true  "impl: lib/utils.ts"          _is_impl_file "lib/utils.ts"
assert_true  "impl: src/api.js"            _is_impl_file "src/api.js"
assert_true  "impl: src/main.go"           _is_impl_file "src/main.go"
assert_true  "impl: src/lib.rs"            _is_impl_file "src/lib.rs"
assert_true  "impl: src/Util.java"         _is_impl_file "src/Util.java"
assert_false "non-impl: README.md"         _is_impl_file "README.md"
assert_false "non-impl: .gitignore"        _is_impl_file ".gitignore"
assert_false "non-impl: config.yaml"       _is_impl_file "config.yaml"
# Test files must not be flagged as impl files
assert_false "not-impl: tests/test_foo.py"     _is_impl_file "tests/test_foo.py"
assert_false "not-impl: test/foo.test.ts"      _is_impl_file "test/foo.test.ts"
assert_false "not-impl: spec/foo_spec.rb"      _is_impl_file "spec/foo_spec.rb"
assert_false "not-impl: src/test_util.py"      _is_impl_file "src/test_util.py"
assert_false "not-impl: src/util_test.py"      _is_impl_file "src/util_test.py"
echo ""

# ---------------------------------------------------------------------------
# Tests: _is_test_file
# ---------------------------------------------------------------------------
echo "--- _is_test_file ---"

assert_true  "test: tests/test_foo.py"      _is_test_file "tests/test_foo.py"
assert_true  "test: test/test_bar.py"       _is_test_file "test/test_bar.py"
assert_true  "test: src/foo_test.go"        _is_test_file "src/foo_test.go"
assert_true  "test: src/util.test.ts"       _is_test_file "src/util.test.ts"
assert_true  "test: src/util.spec.ts"       _is_test_file "src/util.spec.ts"
assert_true  "test: src/FooTest.java"       _is_test_file "src/FooTest.java"
assert_true  "test: spec/bar_spec.rb"       _is_test_file "spec/bar_spec.rb"
assert_true  "test: src/bar_test.py"        _is_test_file "src/bar_test.py"
assert_false "not-test: src/module.py"      _is_test_file "src/module.py"
assert_false "not-test: lib/utils.ts"       _is_test_file "lib/utils.ts"
assert_false "not-test: src/testing.py"     _is_test_file "src/testing.py"
echo ""

# ---------------------------------------------------------------------------
# Tests: _expected_test_basenames
# ---------------------------------------------------------------------------
echo "--- _expected_test_basenames ---"

py_names=$(_expected_test_basenames "src/module.py")
assert_contains "py: prefix pattern"   "test_module.py"    "$py_names"
assert_contains "py: suffix pattern"   "module_test.py"    "$py_names"

ts_names=$(_expected_test_basenames "src/utils.ts")
assert_contains "ts: .test pattern"    "utils.test.ts"     "$ts_names"
assert_contains "ts: .spec pattern"    "utils.spec.ts"     "$ts_names"

go_names=$(_expected_test_basenames "pkg/client.go")
assert_contains "go: _test pattern"    "client_test.go"    "$go_names"

java_names=$(_expected_test_basenames "src/Parser.java")
assert_contains "java: Test suffix"    "ParserTest.java"   "$java_names"

rb_names=$(_expected_test_basenames "lib/client.rb")
assert_contains "rb: _spec suffix"     "client_spec.rb"    "$rb_names"
echo ""

# ---------------------------------------------------------------------------
# Tests: _json_str
# ---------------------------------------------------------------------------
echo "--- _json_str ---"

out=$(_json_str 'hello world')
assert_eq "plain string passthrough"    "hello world"          "$out"

out=$(_json_str 'say "hi"')
assert_contains "double-quote escaped"  '\\"'                   "$out"

out=$(_json_str 'back\slash')
assert_contains "backslash escaped"     '\\\\'                  "$out"

out=$(_json_str 'src/foo/bar.py')
assert_eq "filepath preserved"          "src/foo/bar.py"       "$out"
echo ""

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
total=$(( _pass_count + _fail_count ))
echo "=== Results: ${_pass_count}/${total} passed ==="
if [[ "$_fail_count" -gt 0 ]]; then
  echo "FAIL: ${_fail_count} test(s) failed"
  exit 1
else
  echo "PASS: all tests passed"
  exit 0
fi
