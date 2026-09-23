#!/usr/bin/env bash
# LEGAL_SCAN_REPO_ROOTS wins over default resolution when set — even when a
# nested checkout exists. Both semicolon- and newline-separated forms work.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$(make_workspace "$TMP/ws")"
make_repo "$WS/myrepo"                              # nested exists but is CLEAN
make_repo "$TMP/elsewhere/myrepo" "FORBID_MARKER_X" # env-registered — carries the marker
make_repo "$TMP/other/decoy"                        # non-matching env entry

# Semicolon-separated (survives Windows drive letters under git-bash)
export LEGAL_SCAN_REPO_ROOTS="$TMP/other/decoy;$TMP/elsewhere/myrepo"
run_scan "$WS" --repo=myrepo
[[ $RUN_RC -eq 1 ]] || fail "semicolon form: expected exit 1 (env-registered repo scanned), got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "elsewhere/myrepo/hit.txt" "semicolon form: env-registered checkout was not the one scanned"

# Newline-separated
export LEGAL_SCAN_REPO_ROOTS="$TMP/other/decoy
$TMP/elsewhere/myrepo"
run_scan "$WS" --repo=myrepo
[[ $RUN_RC -eq 1 ]] || fail "newline form: expected exit 1 (env-registered repo scanned), got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "elsewhere/myrepo/hit.txt" "newline form: env-registered checkout was not the one scanned"

echo "PASS: LEGAL_SCAN_REPO_ROOTS wins over nested default (semicolon + newline forms)"
