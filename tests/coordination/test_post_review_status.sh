#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT="${REPO_ROOT}/scripts/coordination/post_review_status.sh"

PASS=0
FAIL=0

pass() { echo "PASS  $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL  $1"; echo "      $2"; FAIL=$((FAIL + 1)); }

assert_exit() {
  [[ "$3" -eq "$2" ]] \
    && pass "$1" \
    || fail "$1" "expected exit $2, got $3"
}

assert_contains() {
  [[ "$3" == *"$2"* ]] \
    && pass "$1" \
    || fail "$1" "missing '$2' in: ${3:0:200}"
}

assert_not_contains() {
  [[ "$3" != *"$2"* ]] \
    && pass "$1" \
    || fail "$1" "unexpected '$2' in: ${3:0:200}"
}

MOCK_DIR="$(mktemp -d)"
GH_LOG="$(mktemp)"
trap 'rm -rf "$MOCK_DIR"; rm -f "$GH_LOG"' EXIT

make_fake_gh() {
  cat >"${MOCK_DIR}/gh" <<'FAKE_GH'
#!/usr/bin/env bash
set -euo pipefail

printf '%q ' "$@" >>"${GH_LOG}"
printf '\n' >>"${GH_LOG}"

if [[ "$1 $2" == "pr view" ]]; then
  for arg in "$@"; do
    if [[ "$arg" == "--jq" ]]; then
      printf 'abc123def456\n'
      exit 0
    fi
  done
  printf '{"headRefOid":"abc123def456"}\n'
  exit 0
fi

if [[ "$1" == "repo" && "$2" == "view" ]]; then
  printf 'vamseeachanta/workspace-hub\n'
  exit 0
fi

if [[ "$1" == "api" ]]; then
  printf '{"state":"created"}\n'
  exit 0
fi

echo "unexpected gh call: $*" >&2
exit 99
FAKE_GH
  chmod +x "${MOCK_DIR}/gh"
}

run_script() {
  GH_LOG="$GH_LOG" PATH="${MOCK_DIR}:${PATH}" bash "$SCRIPT" "$@" 2>&1
}

make_fake_gh

# T01: dry-run is default and does not call the statuses API.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider codex) || ec=$?
  assert_exit "T01 dry-run success exits 0" 0 "$ec"
  assert_contains "T01 dry-run reports state" "state=success" "$out"
  assert_contains "T01 dry-run reports default" "dry-run" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T01 dry-run reads PR" "pr view" "$log"
  assert_not_contains "T01 dry-run does not post" "statuses" "$log"
}

# T02: --post sends a review/cross-provider commit status to the PR head SHA.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider codex) || ec=$?
  assert_exit "T02 post exits 0" 0 "$ec"
  assert_contains "T02 post confirms status" "posted review/cross-provider success" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T02 posts to status endpoint" "repos/vamseeachanta/workspace-hub/statuses/abc123def456" "$log"
  assert_contains "T02 context is fixed" "context=review/cross-provider" "$log"
  assert_contains "T02 state is success" "state=success" "$log"
}

# T03: same-provider success is refused before posting.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider codex --author-provider codex) || ec=$?
  assert_exit "T03 same-provider success exits 2" 2 "$ec"
  assert_contains "T03 same-provider message" "refusing success" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T03 same-provider does not post" "statuses" "$log"
}

# T04: blocking verdicts map to failure and may be posted even for same provider.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict MAJOR --reviewer-provider codex --author-provider codex) || ec=$?
  assert_exit "T04 failure exits 0" 0 "$ec"
  assert_contains "T04 failure posts" "posted review/cross-provider failure" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T04 state is failure" "state=failure" "$log"
}

# T05: in-progress verdicts map to pending.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict PENDING --reviewer-provider gemini --author-provider codex) || ec=$?
  assert_exit "T05 pending exits 0" 0 "$ec"
  assert_contains "T05 pending posts" "posted review/cross-provider pending" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T05 state is pending" "state=pending" "$log"
}

# T06: invalid review output is blocking and maps to failure.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict INVALID_OUTPUT --reviewer-provider gemini --author-provider codex) || ec=$?
  assert_exit "T06 invalid output exits 0" 0 "$ec"
  assert_contains "T06 invalid output posts" "posted review/cross-provider failure" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T06 state is failure" "state=failure" "$log"
}

if [[ "$FAIL" -gt 0 ]]; then
  echo
  echo "$FAIL failed, $PASS passed"
  exit 1
fi

echo
echo "$PASS passed"
