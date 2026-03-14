#!/usr/bin/env bash
# tests/work-queue/test-lifecycle-gates.sh — integration tests for claim/close/archive gate checks
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

PASS=0
FAIL=0
pass() { echo "  PASS: $1"; ((PASS++)) || true; }
fail() { echo "  FAIL: $1"; ((FAIL++)) || true; }

TMP_REPO="$(mktemp -d)"
trap 'rm -rf "$TMP_REPO"' EXIT

export UV_CACHE_DIR="${TMP_REPO}/.uv-cache"
mkdir -p "$UV_CACHE_DIR"

mkdir -p "${TMP_REPO}/scripts/work-queue"
mkdir -p "${TMP_REPO}/.claude/work-queue"/{pending,working,done,blocked,scripts}
mkdir -p "${TMP_REPO}/.claude/work-queue/assets"
mkdir -p "${TMP_REPO}/specs/templates"

cp "${REPO_ROOT}/scripts/work-queue/claim-item.sh" "${TMP_REPO}/scripts/work-queue/"
cp "${REPO_ROOT}/scripts/work-queue/close-item.sh" "${TMP_REPO}/scripts/work-queue/"
cp "${REPO_ROOT}/scripts/work-queue/archive-item.sh" "${TMP_REPO}/scripts/work-queue/"
cp "${REPO_ROOT}/scripts/work-queue/set-active-wrk.sh" "${TMP_REPO}/scripts/work-queue/"
chmod +x "${TMP_REPO}/scripts/work-queue/"*.sh

cat > "${TMP_REPO}/scripts/work-queue/verify-gate-evidence.py" <<'PY'
import os
import sys

phase = "claim"
if "--phase" in sys.argv:
    idx = sys.argv.index("--phase")
    if idx + 1 < len(sys.argv):
        phase = sys.argv[idx + 1]

if phase == "claim" and os.getenv("VERIFY_CLAIM_FAIL") == "1":
    sys.exit(1)
if phase == "close" and os.getenv("VERIFY_CLOSE_FAIL") == "1":
    sys.exit(1)
sys.exit(0)
PY

cat > "${TMP_REPO}/.claude/work-queue/scripts/generate-index.py" <<'PY'
print("ok")
PY

cat > "${TMP_REPO}/specs/templates/stage-evidence-template.yaml" <<'YAML'
wrk_id: WRK-000
generated_at: "2026-03-03T00:00:00Z"
reviewed_by: "agent"
stages:
  - order: 1
    stage: Capture
    status: done
    evidence: .claude/work-queue/working/WRK-000.md
YAML

cat > "${TMP_REPO}/.claude/work-queue/pending/WRK-900.md" <<'MD'
---
id: WRK-900
title: test item
status: pending
route: C
provider: codex
provider_alt: gemini
orchestrator: claude
blocked_by: []
---
MD

cd "$TMP_REPO"
git init -q

echo "── claim-item.sh ───────────────────────────────────"
WORKSPACE_HUB="$TMP_REPO" bash scripts/work-queue/claim-item.sh WRK-900 >/tmp/test-claim.out 2>&1 && pass "T1 claim command succeeds" || fail "T1 claim command succeeds"
[[ -f ".claude/work-queue/working/WRK-900.md" ]] && pass "T2 item moved to working/" || fail "T2 item moved to working/"
[[ -f ".claude/work-queue/assets/WRK-900/evidence/activation.yaml" ]] && pass "T3 activation evidence created" || fail "T3 activation evidence created"
[[ -f ".claude/work-queue/assets/WRK-900/evidence/user-review-close.yaml" ]] && pass "T4 close user-review template bootstrapped" || fail "T4 close user-review template bootstrapped"
[[ -f ".claude/work-queue/assets/WRK-900/evidence/user-review-browser-open.yaml" ]] && pass "T5 browser-open template bootstrapped" || fail "T5 browser-open template bootstrapped"
[[ -f ".claude/work-queue/assets/WRK-900/evidence/stage-evidence.yaml" ]] && pass "T6 stage evidence bootstrapped" || fail "T6 stage evidence bootstrapped"
[[ "$(head -n1 .claude/state/active-wrk)" == "WRK-900" ]] && pass "T7 active WRK state written" || fail "T7 active WRK state written"

echo "── close-item.sh gate block ────────────────────────"
mkdir -p .claude/work-queue/assets/WRK-900
printf '<html></html>\n' > .claude/work-queue/assets/WRK-900/review.html
printf 'ok\n' > .claude/work-queue/assets/WRK-900/html-verification.md
VERIFY_CLOSE_FAIL=1 bash scripts/work-queue/close-item.sh WRK-900 \
  --html-output .claude/work-queue/assets/WRK-900/review.html \
  --html-verification .claude/work-queue/assets/WRK-900/html-verification.md \
  >/tmp/test-close-fail.out 2>&1 \
  && fail "T8 close should fail when validator fails" || pass "T8 close blocked by validator"
[[ -f ".claude/work-queue/working/WRK-900.md" ]] && pass "T9 item remains in working after failed close" || fail "T9 item remains in working after failed close"

echo "── close-item.sh success path ──────────────────────"
bash scripts/work-queue/close-item.sh WRK-900 \
  --html-output .claude/work-queue/assets/WRK-900/review.html \
  --html-verification .claude/work-queue/assets/WRK-900/html-verification.md \
  >/tmp/test-close-pass.out 2>&1 \
  && pass "T10 close succeeds when validator passes" || fail "T10 close succeeds when validator passes"
[[ -f ".claude/work-queue/done/WRK-900.md" ]] && pass "T11 item moved to done/" || fail "T11 item moved to done/"

echo "── archive-item.sh gate block ──────────────────────"
VERIFY_CLOSE_FAIL=1 bash scripts/work-queue/archive-item.sh WRK-900 >/tmp/test-archive-fail.out 2>&1 \
  && fail "T12 archive should fail when close-phase validator fails" || pass "T12 archive blocked by validator"
[[ -f ".claude/work-queue/done/WRK-900.md" ]] && pass "T13 item remains in done after failed archive" || fail "T13 item remains in done after failed archive"

echo "── archive-item.sh success path ────────────────────"
bash scripts/work-queue/archive-item.sh WRK-900 >/tmp/test-archive-pass.out 2>&1 \
  && pass "T14 archive succeeds when validator passes" || fail "T14 archive succeeds when validator passes"
ARCHIVE_FILE="$(find .claude/work-queue/archive -name 'WRK-900.md' | head -n1)"
[[ -n "$ARCHIVE_FILE" && -f "$ARCHIVE_FILE" ]] && pass "T15 archived file created" || fail "T15 archived file created"
[[ ! -f ".claude/work-queue/done/WRK-900.md" ]] && pass "T16 done copy removed after archive" || fail "T16 done copy removed after archive"

echo "────────────────────────────────────────────────────"
echo "Results: ${PASS} passed, ${FAIL} failed"
(( FAIL == 0 )) || exit 1
