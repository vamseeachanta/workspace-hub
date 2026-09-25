#!/usr/bin/env bash
# --repo= with an empty value is a usage error. It must not fall through to a
# root scan and pass over the wrong target.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$(make_workspace "$TMP/ws")"

run_scan "$WS" --repo=
[[ $RUN_RC -eq 2 ]] || fail "expected exit 2 for empty --repo=, got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "ERROR: --repo requires a non-empty repository name" "missing empty-repo error"

echo "PASS: empty --repo= exits 2"
