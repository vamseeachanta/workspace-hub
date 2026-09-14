#!/usr/bin/env bash
# An inherited test-mode variable must never turn the legal gate into a no-op.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS LEGAL_SCAN_RESOLVE_ONLY
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
WS="$(make_workspace "$TMP/ws")"
make_repo "$TMP/ws/marked"
for mode in named default all; do
  args=()
  target="$TMP/ws/marked"
  unset LEGAL_SCAN_REPO_ROOTS
  case "$mode" in
    named) args=(--repo=marked) ;;
    default)
      target="$WS"
      # Exercise default dispatch with a nonempty diff. Full-root grep scans
      # have a separate pre-existing exclusion defect (including the deny list).
      args=(--diff-only)
      printf '%s\n' 'initial clean content' > "$WS/hit.txt"
      printf '%s\n' 'initial companion' > "$WS/companion.txt"
      git -C "$WS" add hit.txt companion.txt
      git -C "$WS" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm fixture
      printf '%s\n' 'changed clean content' > "$WS/hit.txt"
      printf '%s\n' 'changed companion' > "$WS/companion.txt"
      ;;
    all) args=(--all); export LEGAL_SCAN_REPO_ROOTS="$target" ;;
  esac
  export LEGAL_SCAN_RESOLVE_ONLY=1
  run_scan "$WS" "${args[@]}"
  [[ $RUN_RC -eq 0 ]] || fail "$mode clean scan returned $RUN_RC: $RUN_OUT"
  assert_contains "$RUN_OUT" 'Scanning:' "$mode clean scan absent"
  if [[ "$mode" == default ]]; then
    assert_contains "$RUN_OUT" 'Scanning: workspace-hub (root)' 'wrong default target'
  else
    assert_contains "$RUN_OUT" "Scanning: marked ($target)" "$mode wrong clean target"
  fi
  assert_contains "$RUN_OUT" 'RESULT: PASS' "$mode clean summary absent"
  printf '%s\n' FORBID_MARKER_X > "$target/hit.txt"
  run_scan "$WS" "${args[@]}"
  [[ $RUN_RC -eq 1 ]] || fail "$mode inherited variable bypassed denial: $RUN_RC: $RUN_OUT"
  assert_contains "$RUN_OUT" "$target/hit.txt" "$mode wrong denied file"
  assert_contains "$RUN_OUT" 'RESULT: FAIL' "$mode denial summary absent"
  rm -- "$target/hit.txt"
done
echo "PASS: inherited variable preserves named, default and all scanning"
