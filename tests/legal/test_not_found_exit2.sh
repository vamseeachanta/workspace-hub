#!/usr/bin/env bash
# --repo with no resolvable candidate exits 2 and lists every candidate tried.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$(make_workspace "$TMP/ws")"

run_scan "$WS" --repo=no-such-repo
[[ $RUN_RC -eq 2 ]] || fail "expected exit 2 for unresolvable repo, got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "ERROR: Repository not found: no-such-repo" "missing error line"
assert_contains "$RUN_OUT" "Candidates tried:" "missing candidate list header"
assert_contains "$RUN_OUT" "$WS/no-such-repo" "nested candidate not listed"
assert_contains "$RUN_OUT" "$TMP/ws/no-such-repo" "sibling candidate not listed"

# Env-registered mode also exits 2 listing the env-derived candidates.
export LEGAL_SCAN_REPO_ROOTS="$TMP/rootA;$TMP/rootB"
mkdir -p "$TMP/rootA" "$TMP/rootB"
run_scan "$WS" --repo=no-such-repo
[[ $RUN_RC -eq 2 ]] || fail "env mode: expected exit 2 for unresolvable repo, got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "$TMP/rootA/no-such-repo" "env candidate rootA not listed"
assert_contains "$RUN_OUT" "$TMP/rootB/no-such-repo" "env candidate rootB not listed"
assert_contains "$RUN_OUT" "LEGAL_SCAN_REPO_ROOTS" "env-mode hint missing from error text"

echo "PASS: unresolvable --repo exits 2 and lists candidates tried"
