#!/usr/bin/env bash
# Nested $WORKSPACE_ROOT/<name> wins over the sibling checkout.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$(make_workspace "$TMP/ws")"
make_repo "$WS/myrepo" "FORBID_MARKER_X"   # nested — carries the marker
make_repo "$TMP/ws/myrepo"                  # sibling — clean decoy

run_scan "$WS" --repo=myrepo
[[ $RUN_RC -eq 1 ]] || fail "expected exit 1 (violation in nested copy), got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "workspace-hub/myrepo/hit.txt" "nested checkout was not the one scanned"

echo "PASS: nested checkout wins over sibling"
