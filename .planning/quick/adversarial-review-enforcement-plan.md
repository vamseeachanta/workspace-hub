# Adversarial Review Enforcement — Plan

## Problem Statement
Current review enforcement gates only fire on `gh pr create`, `gsd-ship`,
and `gsd-execute-phase`. The actual workflow is direct `git commit` + `git push`
to main, which bypasses ALL review gates. Result: 40 commits on April 2, 2026
with ZERO adversarial reviews.

Additionally, Hermes agent sessions don't use `.claude/hooks` at all, and
overnight batch subagents also bypass them.

## Solution: Two-Layer Enforcement

### Layer 1: Git Pre-Push Review Gate
Add a review-evidence check to the existing `pre-push.sh` hook (already at
`.git/hooks/pre-push.sh` but NOT symlinked as active `pre-push`).

**Behavior:**
- On `git push`, scan commits being pushed for feature/fix commits
- Check for review evidence using `require-cross-review.sh`
- If no review evidence found for feature/fix commits:
  - WARN mode (default): print warning with review instructions, allow push
  - STRICT mode (`REVIEW_GATE_STRICT=1`): block push
- Skip for: docs-only, chore/sync, merge commits, CI-only changes
- Escape hatch: `SKIP_REVIEW_GATE=1` env var (logged to bypass audit)

**Why WARN by default:**
- Overnight batch agents push unattended — blocking would break them
- WARN creates visible audit trail of unreviewed pushes
- Can upgrade to STRICT once review workflow is habitual

### Layer 2: Daily Cron Review Audit
New script: `scripts/maintenance/review-audit.sh`

**Behavior:**
- Runs daily at 06:30 (after overnight batches complete)
- Scans previous 24h of commits for feature/fix commits
- Checks each for matching review evidence in:
  - `scripts/review/results/`
  - `.planning/phases/*/REVIEWS.md`
  - `.planning/quick/REVIEWS.md`
  - `.claude/reports/*review*`
  - Git commit messages with review keywords
- Produces a compliance score (reviewed / total feature commits)
- If compliance < 80%, creates a GitHub issue titled
  "Review backlog: N unreviewed commits from YYYY-MM-DD"
- Lists each unreviewed commit with its diff-stat for easy review dispatch
- Scheduled in `config/scheduled-tasks/schedule-tasks.yaml`

### Layer 3: Symlink pre-push hook
Activate the existing pre-push.sh by symlinking it as `.git/hooks/pre-push`.

## Files Changed
1. `scripts/enforcement/require-review-on-push.sh` — NEW, review gate for pre-push
2. `.git/hooks/pre-push.sh` — MODIFIED, add review gate call
3. `.git/hooks/pre-push` — SYMLINK to pre-push.sh (activate hook)
4. `scripts/maintenance/review-audit.sh` — NEW, daily cron audit
5. `config/scheduled-tasks/schedule-tasks.yaml` — MODIFIED, add review-audit cron entry
6. Tests for both scripts

## Acceptance Criteria
- [ ] Pre-push hook warns on unreviewed feature/fix commits
- [ ] SKIP_REVIEW_GATE=1 bypasses with audit log
- [ ] REVIEW_GATE_STRICT=1 blocks push without review evidence
- [ ] Daily audit script produces correct compliance score
- [ ] Daily audit creates GitHub issue when compliance < 80%
- [ ] Docs-only and chore commits are excluded from review requirement
- [ ] Tests pass for both scripts
