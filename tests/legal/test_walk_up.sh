#!/usr/bin/env bash
# Bounded walk-up (cap 8 levels): a repo above the sibling level is still
# found when neither nested nor sibling candidates exist.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Workspace three levels deep; the repo sits at $TMP (three dirname steps
# above the workspace root — within the 8-level cap).
WS="$(make_workspace "$TMP/a/b/ws")"
make_repo "$TMP/myrepo" "FORBID_MARKER_X"

run_scan "$WS" --repo=myrepo
[[ $RUN_RC -eq 1 ]] || fail "expected exit 1 (violation in walked-up repo), got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "$TMP/myrepo/hit.txt" "walk-up did not resolve the repo above the sibling level"

echo "PASS: bounded walk-up resolves repos above the sibling level"
