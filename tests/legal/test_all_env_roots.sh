#!/usr/bin/env bash
# --all with zero submodules falls back to enumerating LEGAL_SCAN_REPO_ROOTS
# entries; every registered root is scanned and violations are reported.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$(make_workspace "$TMP/ws")"   # git repo with zero submodules
make_repo "$TMP/roots/repoA"                       # clean
make_repo "$TMP/roots/repoB" "FORBID_MARKER_X"     # dirty

export LEGAL_SCAN_REPO_ROOTS="$TMP/roots/repoA;$TMP/roots/repoB"
run_scan "$WS" --all
[[ $RUN_RC -eq 1 ]] || fail "expected exit 1 (violation in registered root), got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "Scanning: repoA" "registered root repoA was not enumerated"
assert_contains "$RUN_OUT" "Scanning: repoB" "registered root repoB was not enumerated"
assert_contains "$RUN_OUT" "repoB/hit.txt" "violation in registered root not reported"

# A registered root that does not exist is a hard error (fail closed).
export LEGAL_SCAN_REPO_ROOTS="$TMP/roots/repoA;$TMP/roots/does-not-exist"
run_scan "$WS" --all
[[ $RUN_RC -eq 2 ]] || fail "expected exit 2 for missing registered root, got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "Registered repo root not found" "missing-root error text absent"

echo "PASS: --all enumerates LEGAL_SCAN_REPO_ROOTS when no submodules exist"
