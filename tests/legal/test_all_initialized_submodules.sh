#!/usr/bin/env bash
# Actual initialized submodule enumeration must detect denied content.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS LEGAL_SCAN_RESOLVE_ONLY
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
WS="$(make_workspace "$TMP/ws")"
make_repo "$TMP/source" FORBID_MARKER_X
git -C "$TMP/source" add readme.txt hit.txt
git -C "$TMP/source" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm fixture
git -C "$WS" -c protocol.file.allow=always submodule add -q "$TMP/source" module
[[ "$(git -C "$WS" submodule --quiet foreach 'echo $sm_path')" == module ]] || fail "fixture is not initialized"
run_scan "$WS" --all
[[ $RUN_RC -eq 1 ]] || fail "initialized submodule expected exit 1, got $RUN_RC: $RUN_OUT"
assert_contains "$RUN_OUT" "Scanning: module ($WS/module)" "wrong submodule target"
assert_contains "$RUN_OUT" "module/hit.txt" "submodule violation missing"
assert_contains "$RUN_OUT" "RESULT: FAIL" "missing denial summary"
echo "PASS: initialized submodule is scanned"
