#!/usr/bin/env bash
set -euo pipefail

# Ecosystem Sync — operator command bundle
# Date: 2026-04-20
# Purpose: copy/paste bundle for the next operator wave.
# Scope:
#   1) promote enforcement fix 07e7e7d07 to main
#   2) create the 3 review-derived follow-up issues
#   3) run Stage 2 doctor/dry-run checks on ace-linux-1 main checkout
#
# Default repo for issue creation is workspace-hub. Change if needed.

REPO="vamseeachanta/workspace-hub"
MAIN_CHECKOUT="/mnt/local-analysis/workspace-hub"
TMPDIR="${TMPDIR:-/tmp}/ecosystem-sync-gh-issues"
mkdir -p "$TMPDIR"

cat <<'HEADER'
============================================================
Ecosystem Sync — Operator Command Bundle
============================================================
Sequence:
  1. Promote enforcement fix 07e7e7d07 to main
  2. Create 3 follow-up GitHub issues
  3. Run Stage 2 validation on ace-linux-1 main checkout

Guardrails:
  - no hook bypass
  - no production enablement from the feature worktree
  - Stage 2 scope is Tasks 12–17 only
============================================================
HEADER

cat <<'STEP1'

[STEP 1] Promote enforcement fix 07e7e7d07 to main
--------------------------------------------------
cd /mnt/local-analysis/workspace-hub
git status --short --branch
git branch --show-current
git fetch origin --prune
git pull --ff-only origin main
git show --stat 07e7e7d07
git show 07e7e7d07 -- tests/hooks/test-require-plan-approval.sh scripts/enforcement/require-plan-approval.sh
git cherry-pick 07e7e7d07
bash tests/hooks/test-require-plan-approval.sh
git status --short --branch
git log --oneline -3
git push origin main

# Stop if any of the above fails.
STEP1

cat > "$TMPDIR/issue-1.md" <<'EOF1'
## Summary
The ecosystem-sync signal tests currently hard-fail on a clean checkout if the local git fixture repos have not already been built under `tests/ecosystem-sync/fixtures/repos/`.

## Why this matters
Stage 1 test coverage is no longer self-contained. The current suite assumes a prior manual run of `tests/ecosystem-sync/fixtures/repos/build_fixtures.sh`, which means a fresh checkout can fail before any product bug is exercised.

## Evidence
- Review artifact: `docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md`
- Affected tests:
  - `tests/ecosystem-sync/test_signals_release.py`
  - `tests/ecosystem-sync/test_signals_casestudy.py`
  - `tests/ecosystem-sync/test_signals_readme.py`
- Supporting fixture builder:
  - `tests/ecosystem-sync/fixtures/repos/build_fixtures.sh`

## Reproduction
1. Remove locally built fixture artifacts under `tests/ecosystem-sync/fixtures/repos/`.
2. Run:
   - `uv run pytest tests/ecosystem-sync/test_signals_release.py tests/ecosystem-sync/test_signals_casestudy.py tests/ecosystem-sync/test_signals_readme.py -q`
3. Observed review result: 9 failures including fixture-related errors.

## Expected behavior
Either:
1. tests auto-build the required fixture repos, or
2. tests skip gracefully with a clear diagnostic when fixtures are absent.

## Proposed change
Add bootstrap logic in `tests/ecosystem-sync/conftest.py` to detect missing fixtures and run `bash tests/ecosystem-sync/fixtures/repos/build_fixtures.sh`, or explicitly skip with a diagnostic if autobuild is not desired.

## Acceptance criteria
- clean checkout can run ecosystem-sync signal tests without manual fixture prep
- missing fixtures no longer produce opaque hard failures
- output clearly distinguishes product failures from fixture-bootstrap failures
EOF1

cat > "$TMPDIR/issue-2.md" <<'EOF2'
## Summary
`_extract_section()` in `scripts/ecosystem-sync/signals.py` currently treats `## <heading>` text inside fenced code blocks as real README headings. That can create malformed extracted bodies and false README-diff signals.

## Why this matters
Signal 3 should detect meaningful capability-section drift. Right now an example snippet inside a fenced block can be misread as the actual `## Capabilities` section.

## Evidence
- Review artifact: `docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md`
- Affected implementation:
  - `scripts/ecosystem-sync/signals.py:144-159`
- Current tests do not cover fenced-code false positives:
  - `tests/ecosystem-sync/test_signals_readme.py`

## Reproduction
Evaluate `_extract_section()` on markdown with `## Capabilities` inside a fenced code block.
Observed review result: extracted body incorrectly included fenced content.

## Expected behavior
Heading-looking text inside fenced code blocks should be ignored.

## Proposed change
Make `_extract_section()` fence-aware:
- track fenced-code entry/exit
- ignore heading matches while inside a fence
- only stop on the next unfenced `## ` heading

## Acceptance criteria
- fenced `## Capabilities` does not trigger extraction
- existing basic heading extraction still passes
- tests gain adversarial fenced-block coverage
EOF2

cat > "$TMPDIR/issue-3.md" <<'EOF3'
## Summary
`detect_release_tag()` currently uses commit date (`git log -1 --format=%cI <tag>`) for the 90-day freshness cutoff. That is wrong for annotated tags created recently on older commits.

## Why this matters
A real recent release can be silently excluded if the tagged commit is old.

## Evidence
- Review artifact: `docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md`
- Affected implementation:
  - `scripts/ecosystem-sync/signals.py:30-76`
- Review repro showed annotated tagger date differed from commit date and should govern freshness.

## Expected behavior
- annotated tags use tagger date for freshness
- lightweight tags may fall back to commit date

## Proposed change
Attempt annotated tagger date first via `git for-each-ref` or `git cat-file tag`, then fall back to commit date for lightweight tags.

## Acceptance criteria
- recent annotated tag on an old commit is still detected as fresh
- lightweight tag behavior remains supported
- tests cover both annotated and lightweight cases
EOF3

cat <<STEP2

[STEP 2] Create the 3 follow-up GitHub issues
---------------------------------------------
# Review body files were written to: $TMPDIR

# 1) Fixture autobuild / graceful skip
gh issue create --repo "$REPO" \
  --title "test(ecosystem-sync): autobuild or skip missing local git fixtures" \
  --label bug \
  --label tests \
  --label priority:medium \
  --label area:ecosystem-sync \
  --body-file "$TMPDIR/issue-1.md"

# 2) Fenced-code-aware README extraction
gh issue create --repo "$REPO" \
  --title "fix(ecosystem-sync): ignore fenced code blocks when extracting README sections" \
  --label bug \
  --label priority:medium \
  --label area:ecosystem-sync \
  --label parsing \
  --body-file "$TMPDIR/issue-2.md"

# 3) Annotated tagger-date release freshness
gh issue create --repo "$REPO" \
  --title "fix(ecosystem-sync): use annotated tagger date for release freshness cutoff" \
  --label bug \
  --label priority:medium \
  --label area:ecosystem-sync \
  --label releases \
  --body-file "$TMPDIR/issue-3.md"
STEP2

cat <<'STEP3'

[STEP 3] Stage 2 validation on ace-linux-1 main checkout
--------------------------------------------------------
cd /mnt/local-analysis/workspace-hub
git status --short --branch
git branch --show-current
git fetch origin --prune
git pull --ff-only origin main

# Task 12/13/14 prep checks
# - audit README headings across the 6 repos
# - verify/create showcase + website labels
# - ensure initial .claude/state/ecosystem-sync/last-sync.yaml backfill exists

# Task 15 doctor checks
uv run scripts/ecosystem-sync/run.py --doctor
bash .claude/cron/ecosystem-sync.sh --doctor

# Task 16 dry-run burn-in
bash .claude/cron/ecosystem-sync.sh --dry-run

# Review outputs before Task 17:
# - wrapper reaches run.py
# - logs/ecosystem-sync/ has same-day log output
# - digest/log output is credible after backfill
# - no new verified blocker surfaced

# Only then consider Task 17 timer/service enablement.
STEP3

cat <<'FOOTER'

Reference artifacts
-------------------
- docs/plans/2026-04-20-aceengineer-ecosystem-sync-enforcement-fix-note.md
- docs/plans/2026-04-20-aceengineer-ecosystem-sync-enforcement-promotion-procedure.md
- docs/plans/2026-04-20-aceengineer-ecosystem-sync-follow-up-issues.md
- docs/plans/2026-04-20-aceengineer-ecosystem-sync-gh-issue-packets.md
- docs/plans/2026-04-20-aceengineer-ecosystem-sync-stage2-authorization.md
- docs/plans/2026-04-20-aceengineer-ecosystem-sync-deploy-readiness-checklist.md
- docs/plans/2026-04-20-aceengineer-ecosystem-sync-operator-runbook.md

Recommended sequence
--------------------
1. Promote 07e7e7d07
2. Create the 3 review-derived issues
3. Execute Stage 2 on ace-linux-1 main checkout
FOOTER
