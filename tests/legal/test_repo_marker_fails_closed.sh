#!/usr/bin/env bash
# --repo=<name> must scan the resolved repo path and fail when a block marker
# is present there. This guards against an empty resolved path passing silently.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$(make_workspace "$TMP/ws")"
make_repo "$WS/submod" "ZZTESTMARKERZZ"

cat > "$WS/.legal-deny-list.yaml" <<'EOF'
patterns:
  - pattern: "ZZTESTMARKERZZ"
    case_sensitive: true
    severity: block
default_severity: block
exclusions:
  - ".git/"
EOF

run_scan "$WS" --repo=submod
[[ $RUN_RC -eq 1 ]] || fail "expected exit 1 (block marker in named repo), got $RUN_RC:
$RUN_OUT"
assert_contains "$RUN_OUT" "Scanning: submod ($WS/submod)" "resolved repo path was not reported"
assert_contains "$RUN_OUT" "submod/hit.txt" "block marker in named repo was not reported"
assert_contains "$RUN_OUT" "RESULT: FAIL" "scan did not report failure"

echo "PASS: --repo scans named repo and fails on a block marker"
