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
  jq -n \
    --arg head "${FAKE_HEAD_SHA:-abc123def456}" \
    --arg branch "${FAKE_BRANCH:-codex/l5-review-status}" \
    --arg commit_body "${FAKE_COMMIT_BODY:-Co-Authored-By: Codex <codex@example.invalid>}" \
    --arg comment_url "${FAKE_COMMENT_URL:-https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1}" \
    --arg comment_body "${FAKE_COMMENT_BODY:-## Claude review -- verdict: APPROVED}" \
    '{
      headRefOid: $head,
      headRefName: $branch,
      commits: [{oid: "c1", messageBody: $commit_body}],
      comments: [{url: $comment_url, author: {login: "reviewer"}, body: $comment_body}]
    }'
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
  out=$(run_script --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
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
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T02 post exits 0" 0 "$ec"
  assert_contains "T02 post confirms status" "posted review/cross-provider success" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T02 posts to status endpoint" "repos/vamseeachanta/workspace-hub/statuses/abc123def456" "$log"
  assert_contains "T02 context is fixed" "context=review/cross-provider" "$log"
  assert_contains "T02 state is success" "state=success" "$log"
  assert_contains "T02 evidence is target URL" "target_url=https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1" "$log"
}

# T03: same-provider success is refused before posting.
{
  : >"$GH_LOG"
  ec=0
  out=$(FAKE_COMMENT_BODY="## Codex review -- verdict: APPROVED" run_script --post --pr 17 --verdict APPROVE --reviewer-provider codex --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T03 same-provider success exits 2" 2 "$ec"
  assert_contains "T03 same-provider message" "refusing success" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T03 same-provider does not post" "statuses" "$log"
}

# T04: blocking verdicts map to failure and may be posted even for same provider.
{
  : >"$GH_LOG"
  ec=0
  out=$(FAKE_COMMENT_BODY="## Codex review -- verdict: MAJOR" run_script --post --pr 17 --verdict MAJOR --reviewer-provider codex --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T04 failure exits 0" 0 "$ec"
  assert_contains "T04 failure posts" "posted review/cross-provider failure" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T04 state is failure" "state=failure" "$log"
}

# T05: in-progress verdicts map to pending.
{
  : >"$GH_LOG"
  ec=0
  out=$(FAKE_COMMENT_BODY="## Gemini review -- verdict: PENDING" run_script --post --pr 17 --verdict PENDING --reviewer-provider gemini --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T05 pending exits 0" 0 "$ec"
  assert_contains "T05 pending posts" "posted review/cross-provider pending" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T05 state is pending" "state=pending" "$log"
}

# T06: invalid review output is blocking and maps to failure.
{
  : >"$GH_LOG"
  ec=0
  out=$(FAKE_COMMENT_BODY="## Gemini review -- verdict: INVALID_OUTPUT" run_script --post --pr 17 --verdict INVALID_OUTPUT --reviewer-provider gemini --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T06 invalid output exits 0" 0 "$ec"
  assert_contains "T06 invalid output posts" "posted review/cross-provider failure" "$out"
  log=$(cat "$GH_LOG")
  assert_contains "T06 state is failure" "state=failure" "$log"
}

# T07: provider aliases and whitespace spoofing are rejected.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider claude-opus --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T07 unknown provider exits 1" 1 "$ec"
  assert_contains "T07 unknown provider message" "unsupported provider" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T07 unknown provider does not post" "statuses" "$log"

  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider " claude " --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T07 whitespace provider exits 1" 1 "$ec"
  assert_contains "T07 whitespace provider message" "unsupported provider" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T07 whitespace provider does not post" "statuses" "$log"
}

# T08: caller-declared author provider must match the PR-derived provider.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider gemini --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T08 author mismatch exits 1" 1 "$ec"
  assert_contains "T08 author mismatch message" "does not match derived PR author provider codex" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T08 author mismatch does not post" "statuses" "$log"
}

# T09: mixed branch/trailer providers are refused.
{
  : >"$GH_LOG"
  ec=0
  out=$(FAKE_COMMIT_BODY="Co-Authored-By: Claude <claude@example.invalid>" FAKE_COMMENT_BODY="## Gemini review -- verdict: APPROVE" run_script --post --pr 17 --verdict APPROVE --reviewer-provider gemini --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T09 mixed providers exits 1" 1 "$ec"
  assert_contains "T09 mixed providers message" "mixed author providers" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T09 mixed providers does not post" "statuses" "$log"
}

# T10: reviewed SHA must equal the current PR head.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider codex --sha stale123 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T10 stale sha exits 1" 1 "$ec"
  assert_contains "T10 stale sha message" "does not match current PR head" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T10 stale sha does not post" "statuses" "$log"
}

# T11: success cannot be posted without evidence.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider codex --sha abc123def456) || ec=$?
  assert_exit "T11 missing evidence exits 1" 1 "$ec"
  assert_contains "T11 missing evidence message" "--evidence-url is required" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T11 missing evidence does not post" "statuses" "$log"
}

# T12: evidence URL must point at a same-PR reviewer verdict comment.
{
  : >"$GH_LOG"
  ec=0
  out=$(run_script --post --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-missing) || ec=$?
  assert_exit "T12 missing evidence comment exits 1" 1 "$ec"
  assert_contains "T12 missing evidence comment message" "comment on the same PR" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T12 missing evidence comment does not post" "statuses" "$log"
}

# T13: every PR commit must carry a provider Co-Authored-By trailer.
{
  : >"$GH_LOG"
  ec=0
  out=$(FAKE_COMMIT_BODY="Reviewed-by: reviewer@example.invalid" run_script --post --pr 17 --verdict APPROVE --reviewer-provider claude --author-provider codex --sha abc123def456 --evidence-url https://github.com/vamseeachanta/workspace-hub/pull/17#issuecomment-1) || ec=$?
  assert_exit "T13 missing commit provider exits 1" 1 "$ec"
  assert_contains "T13 missing commit provider message" "Co-Authored-By trailers" "$out"
  log=$(cat "$GH_LOG")
  assert_not_contains "T13 missing commit provider does not post" "statuses" "$log"
}

if [[ "$FAIL" -gt 0 ]]; then
  echo
  echo "$FAIL failed, $PASS passed"
  exit 1
fi

echo
echo "$PASS passed"
