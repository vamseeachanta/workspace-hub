#!/usr/bin/env bash
# Required backend and execution failures must be distinguishable from findings.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS LEGAL_SCAN_RESOLVE_ONLY RIPGREP_CONFIG_PATH
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
REAL_PATH="$PATH"
command -v rg >/dev/null
WS="$(make_workspace "$TMP/ws")"
MARKED="$TMP/ws/marked"
make_repo "$MARKED" FORBID_MARKER_X
printf '%s\n' FORBID_MARKER_X > "$WS/hit.txt"
SUBWS="$(make_workspace "$TMP/sub")"
git -C "$MARKED" add readme.txt hit.txt
git -C "$MARKED" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm fixture
git -C "$SUBWS" -c protocol.file.allow=always submodule add -q "$MARKED" module
DIFFWS="$(make_workspace "$TMP/diff")"
mkdir -p "$DIFFWS/.hidden"
printf '%s\n' clean > "$DIFFWS/.hidden/hit.txt"
git -C "$DIFFWS" add -- .hidden/hit.txt
git -C "$DIFFWS" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm fixture
printf '%s\n' FORBID_MARKER_X > "$DIFFWS/.hidden/hit.txt"

# A utility-complete PATH with no rg; no user HOME or executable is modified.
mkdir -p "$TMP/no-rg" "$TMP/failing"
for utility in bash dirname basename awk sed git tr wc cut grep; do
  printf '#!%s\nexec %q "$@"\n' "$BASH" "$(command -v "$utility")" > "$TMP/no-rg/$utility"
  chmod +x "$TMP/no-rg/$utility"
done
printf '#!%s\nprintf "partial-backend-result\\n"\nprintf "fixture forced backend error\\n" >&2\nexit "${FIXTURE_RG_STATUS:-2}"\n' "$BASH" > "$TMP/failing/rg"
chmod +x "$TMP/failing/rg"
FAILURES=0
check_case() {
  local label="$1"; shift
  if ( "$@" ); then
    echo "PASS: $label"
  else
    echo "FAIL: $label" >&2
    FAILURES=$((FAILURES + 1))
  fi
}
expect_denied() {
  [[ $RUN_RC -eq 1 ]] || fail "positive control expected denial, got $RUN_RC: $RUN_OUT"
  assert_contains "$RUN_OUT" FORBID_MARKER_X 'positive marker absent'
  assert_contains "$RUN_OUT" hit.txt 'positive file evidence absent'
}
missing_dependency() {
  run_scan "$WS" --repo=marked
  expect_denied
  PATH="$TMP/no-rg" run_scan "$WS" --help
  [[ $RUN_RC -eq 0 ]] || fail "help requires backend: $RUN_OUT"
  PATH="$TMP/no-rg" run_scan "$WS" --unknown-test-option
  [[ $RUN_RC -eq 2 ]] || fail 'unknown option did not return 2'
  assert_contains "$RUN_OUT" 'Unknown argument' 'usage diagnostic absent'
  PATH="$TMP/no-rg" run_scan "$WS" --repo=marked
  [[ $RUN_RC -eq 2 ]] || fail "missing rg returned $RUN_RC: $RUN_OUT"
  assert_contains "$RUN_OUT" 'ERROR: RIPGREP_REQUIRED' 'dependency diagnostic absent'
  assert_not_contains "$RUN_OUT" 'RESULT: PASS' 'missing backend passed'
}
backend_error() {
  local target_mode="$1" output_mode="$2" status="${3:-2}" ws="$WS"
  local args=()
  unset LEGAL_SCAN_REPO_ROOTS
  case "$target_mode" in
    named) args=(--repo=marked) ;;
    registered) args=(--all); export LEGAL_SCAN_REPO_ROOTS="$MARKED" ;;
    submodule) args=(--all); ws="$SUBWS" ;;
    diff) args=(--diff-only); ws="$DIFFWS" ;;
  esac
  [[ "$output_mode" == normal ]] || args+=("--$output_mode")
  run_scan "$ws" "${args[@]}"
  expect_denied
  if [[ "$target_mode" == diff ]]; then
    assert_contains "$RUN_OUT" '.hidden/hit.txt' 'hidden explicit diff target not searched'
  fi
  FIXTURE_RG_STATUS="$status" PATH="$TMP/failing:$REAL_PATH" run_scan "$ws" "${args[@]}"
  [[ $RUN_RC -eq 2 ]] || fail "$target_mode/$output_mode error returned $RUN_RC: $RUN_OUT"
  assert_contains "$RUN_OUT" 'ERROR: LEGAL_SCAN_INCOMPLETE' 'incomplete-scan diagnostic absent'
  assert_contains "$RUN_OUT" 'fixture forced backend error' 'backend stderr lost'
  assert_not_contains "$RUN_OUT" 'partial-backend-result' 'failed search output issued as complete'
  assert_not_contains "$RUN_OUT" 'RESULT: PASS' 'failed search reported PASS'
}
inherited_config() {
  run_scan "$WS" --repo=marked
  expect_denied
  printf '%s\n' --glob '!**' > "$TMP/rg.conf"
  RIPGREP_CONFIG_PATH="$TMP/rg.conf" run_scan "$WS" --repo=marked
  expect_denied
}
count_boundary() {
  local i
  for ((i=0; i<256; i++)); do printf '%s\n' FORBID_MARKER_X; done > "$MARKED/hit.txt"
  run_scan "$WS" --repo=marked
  expect_denied
  assert_contains "$RUN_OUT" '256 block violation(s)' 'match count did not survive status handling'
}
mixed_findings_error() {
  local mode="$1" ws early later
  ws="$(make_workspace "$TMP/mixed-$mode")"
  early="$TMP/mixed-$mode/early"
  later="$TMP/mixed-$mode/later"
  make_repo "$early" FORBID_MARKER_X
  make_repo "$later" FORBID_MARKER_X
  printf '  - pattern: "SECOND_MARKER_X"\n    case_sensitive: true\n' >> "$ws/.legal-deny-list.yaml"
  mkdir -p "$TMP/selective-$mode"
  printf '#!%s\n' "$BASH" > "$TMP/selective-$mode/rg"
  cat >> "$TMP/selective-$mode/rg" <<'SHIM'
second=false; later=false
for argument in "$@"; do
  [[ "$argument" == SECOND_MARKER_X ]] && second=true
  [[ "$argument" == */later ]] && later=true
done
if $second && { [[ "$FIXTURE_FAIL_MODE" == pattern ]] || $later; }; then
  printf 'fixture selective backend error\n' >&2
  exit 2
fi
exec "$FIXTURE_REAL_RG" "$@"
SHIM
  chmod +x "$TMP/selective-$mode/rg"
  local args=(--repo=early)
  if [[ "$mode" == targets ]]; then
    args=(--all)
    export LEGAL_SCAN_REPO_ROOTS="$early;$later"
  fi
  run_scan "$ws" "${args[@]}"
  expect_denied
  FIXTURE_REAL_RG="$(command -v rg)" FIXTURE_FAIL_MODE="$mode" PATH="$TMP/selective-$mode:$REAL_PATH" run_scan "$ws" "${args[@]}"
  [[ $RUN_RC -eq 2 ]] || fail "prior findings hid backend error: $RUN_RC"
  assert_contains "$RUN_OUT" "$early/hit.txt" 'genuine earlier findings absent'
  assert_contains "$RUN_OUT" 'ERROR: LEGAL_SCAN_INCOMPLETE' 'mixed-result error absent'
  assert_contains "$RUN_OUT" 'fixture selective backend error' 'selective error absent'
  assert_not_contains "$RUN_OUT" 'RESULT: FAIL' 'incomplete scan issued completed failure summary'
  assert_not_contains "$RUN_OUT" 'RESULT: PASS' 'incomplete scan issued completed pass summary'
}
check_case 'PATH-only required dependency and usable help' missing_dependency
for target in named default registered submodule diff; do
  for output in normal quiet json; do
    check_case "$target/$output incomplete scan" backend_error "$target" "$output"
  done
done
check_case 'nonstandard backend status' backend_error named normal 7
check_case 'backend launch-style status' backend_error named normal 126
check_case 'inherited ripgrep config cannot hide a marker' inherited_config
check_case 'findings before later pattern error' mixed_findings_error pattern
check_case 'findings before later registered-target error' mixed_findings_error targets
check_case '256 findings retain denied status' count_boundary
[[ $FAILURES -eq 0 ]] || exit 1
