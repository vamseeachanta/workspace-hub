#!/usr/bin/env bash
# --all refuses with exit 2 when its enumeration is empty (zero initialized
# submodules and no LEGAL_SCAN_REPO_ROOTS) — a legal gate must never pass by
# scanning nothing.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$(make_workspace "$TMP/ws")"   # git repo with zero submodules

run_scan "$WS" --all
[[ $RUN_RC -eq 2 ]] || fail "expected exit 2 for empty --all enumeration, got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "nothing to scan" "missing empty-enumeration refusal message"

echo "PASS: --all with empty enumeration refuses with exit 2"
