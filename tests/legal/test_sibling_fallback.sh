#!/usr/bin/env bash
# When no nested checkout exists, the sibling $(dirname WORKSPACE_ROOT)/<name>
# is resolved and scanned.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$(make_workspace "$TMP/ws")"
make_repo "$TMP/ws/myrepo" "FORBID_MARKER_X"   # sibling only

run_scan "$WS" --repo=myrepo
[[ $RUN_RC -eq 1 ]] || fail "expected exit 1 (violation in sibling copy), got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "ws/myrepo/hit.txt" "sibling checkout was not the one scanned"
assert_not_contains "$RUN_OUT" "workspace-hub/myrepo/hit.txt" "nested path reported but no nested checkout exists"

echo "PASS: sibling checkout resolved when nested is absent"
