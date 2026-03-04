#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

pass=0
fail=0

report_pass() {
  echo "  PASS: $1"
  pass=$((pass + 1))
}

report_fail() {
  echo "  FAIL: $1"
  fail=$((fail + 1))
}

tmp_wrk="WRK-9998"
wrk_assets=".claude/work-queue/assets/${tmp_wrk}/evidence"
wrk_log=".claude/work-queue/logs/${tmp_wrk}-plan_draft.log"

mkdir -p "$wrk_assets"
cat > "$wrk_assets/user-review-browser-open.yaml" <<'YAML'
events: []
YAML

tmp_html="$(mktemp --suffix=.html)"
trap 'rm -f "$tmp_html"; rm -rf ".claude/work-queue/assets/${tmp_wrk}" ".claude/work-queue/logs/${tmp_wrk}-plan_draft.log"' EXIT
cat > "$tmp_html" <<'HTML'
<html><body>tmp review</body></html>
HTML

echo "Test 1: log-gate-event writes explicit signal key"
bash scripts/work-queue/log-gate-event.sh "$tmp_wrk" "plan_draft" "plan_html_review_draft" "codex" "smoke"
if rg -q '^signal:[[:space:]]*plan_html_review_draft$' "$wrk_log"; then
  report_pass "signal key emitted"
else
  report_fail "signal key missing"
fi

echo "Test 2: user-review logger writes stage signal (no-open mode)"
bash scripts/work-queue/log-user-review-browser-open.sh "$tmp_wrk" \
  --stage plan_draft \
  --html "$tmp_html" \
  --reviewer tester \
  --no-open

if rg -q '^action:[[:space:]]*plan_html_review_draft$' "$wrk_log"; then
  report_pass "stage action logged"
else
  report_fail "stage action not logged"
fi

if rg -q '^action:[[:space:]]*html_open_default_browser$' "$wrk_log"; then
  report_fail "browser-open action should not log when --no-open is used"
else
  report_pass "browser-open action skipped in --no-open mode"
fi

echo ""
echo "Results: ${pass} passed, ${fail} failed"
[[ "$fail" -eq 0 ]]
