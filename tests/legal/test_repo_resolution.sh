#!/usr/bin/env bash
# Exercise resolution through actual scans, including path assertion controls.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS LEGAL_SCAN_RESOLVE_ONLY
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
WS="$(make_workspace "$TMP/grand/parent")"

# Identically named files in different repositories must remain distinguishable.
make_repo "$TMP/one" FORBID_MARKER_X
make_repo "$TMP/two" FORBID_MARKER_X
reported="$TMP/one/hit.txt:1:FORBID_MARKER_X"
if command -v cygpath >/dev/null; then
  reported="$(cygpath -m "$TMP/one")\\hit.txt:1:FORBID_MARKER_X"
fi
assert_contains "$reported" "$TMP/one/hit.txt" 'equivalent path rejected'
if (assert_contains "$reported" "$TMP/two/hit.txt" 'wrong repo') >/dev/null 2>&1; then
  fail 'path assertion accepted the same basename in a different repository'
fi
if (assert_contains "$reported" "$TMP/one/other.txt" 'wrong file') >/dev/null 2>&1; then
  fail 'path assertion accepted a different file'
fi
if (assert_contains "$reported" 'RESULT: FAIL' 'missing summary') >/dev/null 2>&1; then
  fail 'literal assertion accepted an absent summary'
fi

check_target() {
  local name="$1" target="$2"
  run_scan "$WS" "--repo=$name"
  [[ $RUN_RC -eq 0 ]] || fail "$name clean control: $RUN_RC: $RUN_OUT"
  assert_contains "$RUN_OUT" "Scanning: $name ($target)" 'wrong clean target'
  assert_contains "$RUN_OUT" 'RESULT: PASS' 'clean summary absent'
  printf '%s\n' FORBID_MARKER_X > "$target/hit.txt"
  run_scan "$WS" "--repo=$name"
  [[ $RUN_RC -eq 1 ]] || fail "$name positive control: $RUN_RC: $RUN_OUT"
  assert_contains "$RUN_OUT" "$target/hit.txt" 'wrong denied target'
  assert_contains "$RUN_OUT" 'RESULT: FAIL' 'denial summary absent'
  rm -- "$target/hit.txt"
}

make_repo "$WS/dualrepo"
make_repo "$TMP/grand/parent/dualrepo" FORBID_MARKER_X
check_target dualrepo "$WS/dualrepo"
make_repo "$TMP/grand/parent/sibonly"
check_target sibonly "$TMP/grand/parent/sibonly"
make_repo "$TMP/grand/walkrepo"
check_target walkrepo "$TMP/grand/walkrepo"
make_repo "$WS/envrepo" FORBID_MARKER_X
make_repo "$TMP/roots/rootA/envrepo"
export LEGAL_SCAN_REPO_ROOTS="$TMP/roots/rootA"
check_target envrepo "$TMP/roots/rootA/envrepo"
make_repo "$TMP/roots/rootB/semirepo"
export LEGAL_SCAN_REPO_ROOTS="$TMP/roots/rootA;$TMP/roots/rootB"
check_target semirepo "$TMP/roots/rootB/semirepo"
make_repo "$WS/nestedonly"
run_scan "$WS" --repo=nestedonly
[[ $RUN_RC -eq 2 ]] || fail 'explicit roots incorrectly fell back to nested repo'
assert_contains "$RUN_OUT" 'Candidates tried:' 'missing resolution evidence'
assert_contains "$RUN_OUT" 'ERROR: Repository not found: nestedonly' 'wrong missing-repository diagnostic'
assert_contains "$RUN_OUT" "$TMP/roots/rootA/nestedonly" 'first candidate missing'
assert_contains "$RUN_OUT" "$TMP/roots/rootB/nestedonly" 'second candidate missing'
assert_contains "$RUN_OUT" 'LEGAL_SCAN_REPO_ROOTS' 'explicit-root hint missing'
unset LEGAL_SCAN_REPO_ROOTS
run_scan "$WS" --repo=no-such-repo
[[ $RUN_RC -eq 2 ]] || fail 'missing repo did not fail with exit 2'
assert_contains "$RUN_OUT" 'ERROR: Repository not found: no-such-repo' 'wrong missing-repository diagnostic'
assert_contains "$RUN_OUT" 'Candidates tried:' 'missing default candidates'
run_scan "$WS" --all
[[ $RUN_RC -eq 2 ]] || fail 'empty enumeration did not fail with exit 2'
assert_contains "$RUN_OUT" 'nothing to scan' 'empty enumeration diagnostic missing'
export LEGAL_SCAN_REPO_ROOTS="$TMP/roots/rootA;$TMP/roots/rootB"
# Production scans registered roots recursively, including non-repository children.
mkdir -p "$TMP/roots/rootB/nogit"
run_scan "$WS" --all
[[ $RUN_RC -eq 0 ]] || fail "registered roots clean control: $RUN_OUT"
assert_contains "$RUN_OUT" 'Scanning: rootA' 'first root missing'
assert_contains "$RUN_OUT" 'Scanning: rootB' 'second root missing'
printf '%s\n' FORBID_MARKER_X > "$TMP/roots/rootB/semirepo/hit.txt"
run_scan "$WS" --all
[[ $RUN_RC -eq 1 ]] || fail "registered roots positive control: $RUN_OUT"
assert_contains "$RUN_OUT" "$TMP/roots/rootB/semirepo/hit.txt" 'registered-root file missing'
assert_contains "$RUN_OUT" 'RESULT: FAIL' 'registered-root denial summary missing'
rm -- "$TMP/roots/rootB/semirepo/hit.txt"
printf '%s\n' FORBID_MARKER_X > "$TMP/roots/rootB/nogit/hit.txt"
run_scan "$WS" --all
[[ $RUN_RC -eq 1 ]] || fail 'registered-root scan omitted non-repository content'
assert_contains "$RUN_OUT" "$TMP/roots/rootB/nogit/hit.txt" 'non-repository child denial absent'
echo 'PASS: actual resolution scans and path assertion controls'
