#!/usr/bin/env bash
# Git selection errors must not become completed legal scans.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
unset LEGAL_SCAN_REPO_ROOTS LEGAL_SCAN_RESOLVE_ONLY RIPGREP_CONFIG_PATH
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_CEILING_DIRECTORIES
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
TMP="$(mktemp -d "${TMPDIR:-/tmp}/legal-selection.XXXXXXXX")"
[[ "$TMP" == "${TMPDIR:-/tmp}"/legal-selection.* ]] || exit 2
trap 'rm -rf -- "$TMP"' EXIT
export REAL_GIT="$(command -v git)" REAL_RG="$(command -v rg)"
export GIT_LOG="$TMP/git.log" RG_LOG="$TMP/rg.log"
mkdir -p "$TMP/bin"
cat > "$TMP/bin/git" <<'SHIM'
#!/usr/bin/env bash
if [[ "$1" == diff && "$2" == --name-only && "$3" == HEAD &&
      "$(pwd -P)" == "$FIXTURE_TARGET" ]]; then
  printf '%s\n' "$FIXTURE_BEHAVIOR" >> "$GIT_LOG"
  case "$FIXTURE_BEHAVIOR" in
    fail)
      [[ "$FIXTURE_PARTIAL" == yes ]] && printf 'hit.txt\n'
      printf 'fixture git selection failed\n' >&2
      exit 73 ;;
    warn) printf 'fixture git warning\n' >&2 ;;
  esac
fi
exec "$REAL_GIT" "$@"
SHIM
cat > "$TMP/bin/rg" <<'SHIM'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$RG_LOG"
exec "$REAL_RG" "$@"
SHIM
chmod +x "$TMP/bin/git" "$TMP/bin/rg"
export PATH="$TMP/bin:$PATH"
export FIXTURE_TARGET='' FIXTURE_BEHAVIOR=pass FIXTURE_PARTIAL=no
FAILURES=0

commit_clean() {
  printf 'clean\n' > "$1/hit.txt"
  git -C "$1" add hit.txt
  git -C "$1" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm fixture
}

build_case() {
  local mode="$1" base="$TMP/$1"
  unset LEGAL_SCAN_REPO_ROOTS
  WS="$(make_workspace "$base")"
  TARGET="$WS"
  ARGS=(--diff-only)
  case "$mode" in
    named|registered)
      TARGET="$base/marked"
      make_repo "$TARGET"
      commit_clean "$TARGET"
      if [[ "$mode" == named ]]; then ARGS+=(--repo=marked)
      else ARGS+=(--all); export LEGAL_SCAN_REPO_ROOTS="$TARGET"; fi ;;
    submodule)
      make_repo "$base/source"
      commit_clean "$base/source"
      git -C "$WS" -c protocol.file.allow=always submodule add -q "$base/source" module
      TARGET="$WS/module"
      ARGS+=(--all) ;;
    default) commit_clean "$TARGET" ;;
  esac
  FIXTURE_TARGET="$(cd "$TARGET" && pwd -P)"
  printf 'FORBID_MARKER_X\n' > "$TARGET/hit.txt"
}

capture_scan() {
  : > "$GIT_LOG"; : > "$RG_LOG"
  RUN_RC=0
  bash "$WS/scripts/legal/legal-sanity-scan.sh" "${ARGS[@]}" "$@" \
    > "$TMP/stdout" 2> "$TMP/stderr" || RUN_RC=$?
  RUN_OUT="$(cat "$TMP/stdout")"
  RUN_ERR="$(cat "$TMP/stderr")"
}

assert_incomplete() {
  [[ $RUN_RC -eq 2 ]] || fail "expected incomplete exit 2, got $RUN_RC"
  assert_contains "$RUN_ERR" 'ERROR: LEGAL_SCAN_INCOMPLETE: Git file selection failed' 'Git diagnostic missing'
  assert_not_contains "$RUN_OUT" 'LEGAL_SCAN_INCOMPLETE' 'diagnostic leaked to stdout'
  assert_not_contains "$RUN_OUT" 'RESULT: PASS' 'incomplete scan passed'
  assert_not_contains "$RUN_OUT" 'RESULT: FAIL' 'incomplete scan completed'
}

failure_case() {
  local output_mode="$1" partial="$2" extra=()
  [[ "$output_mode" == normal ]] || extra+=("--$output_mode")
  FIXTURE_BEHAVIOR=pass
  capture_scan "${extra[@]}"
  [[ $RUN_RC -eq 1 ]] || fail "positive control returned $RUN_RC"
  assert_contains "$RUN_OUT" FORBID_MARKER_X 'positive marker absent'
  [[ -s "$RG_LOG" ]] || fail 'positive instrumentation did not record calls'
  assert_contains "$(cat "$GIT_LOG")" pass 'pass-through Git shim not reached'
  FIXTURE_BEHAVIOR=fail; FIXTURE_PARTIAL="$partial"
  capture_scan "${extra[@]}"
  assert_contains "$(cat "$GIT_LOG")" fail 'failing Git shim not reached'
  assert_contains "$RUN_ERR" 'fixture git selection failed' 'Git stderr suppressed'
  assert_not_contains "$RUN_OUT" 'fixture git selection failed' 'Git stderr leaked'
  [[ ! -s "$RG_LOG" ]] || fail 'failed selection reached ripgrep'
  assert_incomplete
}

successful_selections() {
  local kind="$1" output_mode="$2" extra=()
  [[ "$output_mode" == normal ]] || extra+=("--$output_mode")
  FIXTURE_BEHAVIOR=warn
  printf 'clean\n' > "$TARGET/hit.txt"
  case "$kind" in
    nonempty) printf 'FORBID_MARKER_X\n' > "$TARGET/hit.txt" ;;
    deleted) rm -- "$TARGET/hit.txt" ;;
    excluded)
      printf 'FORBID_MARKER_X\n' > "$TARGET/hit.txt"
      printf 'exclusions:\n  - "hit.txt"\n' >> "$WS/.legal-deny-list.yaml" ;;
  esac
  capture_scan "${extra[@]}"
  assert_contains "$RUN_ERR" 'fixture git warning' 'successful warning suppressed'
  assert_not_contains "$RUN_OUT" 'fixture git warning' 'warning leaked to stdout'
  assert_not_contains "$RUN_ERR" LEGAL_SCAN_INCOMPLETE 'warning treated as failure'
  if [[ "$kind" == nonempty ]]; then
    [[ $RUN_RC -eq 1 && -s "$RG_LOG" ]] || fail 'warning prevented genuine search'
    assert_contains "$RUN_OUT" FORBID_MARKER_X 'warning control marker absent'
  else
    [[ $RUN_RC -eq 0 && ! -s "$RG_LOG" ]] || fail 'successful empty selection changed'
    [[ "$output_mode" != normal ]] || assert_contains "$RUN_OUT" 'RESULT: PASS' 'empty stdout changed'
  fi
  # Restore the exclusion-free fixture without changing the production helper.
  printf 'deny_patterns:\n  - pattern: "FORBID_MARKER_X"\n    case_sensitive: true\n' > "$WS/.legal-deny-list.yaml"
  printf 'clean\n' > "$TARGET/hit.txt"
}

real_git_failure() {
  local kind="$1" parent="$TMP/real-$1"
  unset LEGAL_SCAN_REPO_ROOTS
  WS="$(make_workspace "$parent")"
  TARGET="$parent/target"
  mkdir -p "$TARGET"
  [[ "$kind" != unborn ]] || git -C "$TARGET" init -q
  export GIT_CEILING_DIRECTORIES="$(cd "$parent" && pwd -P)"
  if [[ "$kind" == nonrepo ]]; then
    if git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1; then
      fail 'non-repository fixture discovered an ancestor'
    fi
  else
    if git -C "$TARGET" rev-parse --verify HEAD >/dev/null 2>&1; then
      fail 'unborn fixture has a HEAD'
    fi
  fi
  local expected_git_err direct_rc=0
  "$REAL_GIT" -C "$TARGET" diff --name-only HEAD > "$TMP/git-stdout" 2> "$TMP/git-stderr" || direct_rc=$?
  expected_git_err="$(cat "$TMP/git-stderr")"
  [[ $direct_rc -ne 0 && -n "$expected_git_err" ]] || fail 'real Git failure control absent'
  FIXTURE_TARGET=''; ARGS=(--repo=target --diff-only --json)
  capture_scan
  assert_incomplete
  [[ "$RUN_ERR" == *"$expected_git_err"* ]] || fail 'real Git stderr absent'
  [[ ! -s "$RG_LOG" ]] || fail 'invalid Git target was searched'
}

multiple_targets() {
  build_case registered
  local later="$TARGET" earlier="$TMP/registered/earlier"
  make_repo "$earlier"; commit_clean "$earlier"
  printf 'FORBID_MARKER_X\n' > "$earlier/hit.txt"
  export LEGAL_SCAN_REPO_ROOTS="$earlier;$later"
  FIXTURE_BEHAVIOR=pass
  capture_scan
  [[ $RUN_RC -eq 1 ]] || fail 'multiple-target control did not deny'
  assert_contains "$(cat "$RG_LOG")" "$earlier/hit.txt" 'earlier control invocation absent'
  assert_contains "$(cat "$RG_LOG")" "$later/hit.txt" 'later control invocation absent'
  FIXTURE_BEHAVIOR=fail; FIXTURE_PARTIAL=yes
  capture_scan
  assert_incomplete
  assert_contains "$RUN_OUT" "$earlier/hit.txt" 'earlier finding lost'
  assert_contains "$(cat "$RG_LOG")" "$earlier/hit.txt" 'earlier search lost'
  assert_not_contains "$(cat "$RG_LOG")" "$later/hit.txt" 'failed target searched'
  assert_contains "$(cat "$GIT_LOG")" fail 'later failure not reached'
}

check_case() {
  local label="$1"; shift
  if ( "$@" ); then echo "PASS: $label"
  else echo "FAIL: $label" >&2; FAILURES=$((FAILURES + 1)); fi
}

for dispatch in default named registered submodule; do
  build_case "$dispatch"
  for output_mode in normal quiet json; do
    for partial in no yes; do
      check_case "$dispatch/$output_mode/partial-$partial" failure_case "$output_mode" "$partial"
    done
  done
done
# Reuse an existing committed root for success-preservation controls.
WS="$TMP/default/workspace-hub"; TARGET="$WS"
FIXTURE_TARGET="$(cd "$TARGET" && pwd -P)"; ARGS=(--diff-only)
unset LEGAL_SCAN_REPO_ROOTS
for kind in empty nonempty deleted excluded; do
  for output_mode in normal json; do
    check_case "success-$kind/$output_mode" successful_selections "$kind" "$output_mode"
  done
done
check_case real-unborn real_git_failure unborn
check_case real-nonrepo real_git_failure nonrepo
# Use a new directory for the multi-target fixture.
TMP_PARENT="$TMP"; TMP="$TMP/multi"; mkdir -p "$TMP"
check_case multiple-targets multiple_targets
TMP="$TMP_PARENT"
[[ $FAILURES -eq 0 ]] || fail "$FAILURES selection cases failed"
echo 'PASS: Git selection contract (35 cases)'
