# Plan for #2070: Guard Claude state sync against oversized session-signal files

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2070
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2070-claude.md | ...-codex.md | ...-gemini.md (pending)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/hooks/check-claude-md-limits.sh` — exact pattern to mirror; uses `git diff --cached --name-only --diff-filter=ACMR` then exits non-zero on violation. Reusable shell skeleton.
- Found: `.claude/hooks/` already contains 30 hooks (`plan-approval-gate.sh`, `gsd-validate-commit.sh`, etc.) — established convention for pre-commit / pre-push gates.
- Gap: no existing size-guard hook for tracked state files (grep on `session-signals|MAX_FILE_SIZE|100.MB|95.MB` across `.claude/` returns zero matches).

### Standards
| Standard | Status | Source |
|---|---|---|
| GitHub blob size limit (100 MB hard, 50 MB warn) | external constraint | https://docs.github.com/en/repositories/working-with-files/managing-large-files |
| Internal `.claude/rules/patterns.md` enforcement gradient | applies | `.claude/rules/patterns.md` — promotes prose → script → hook |

### LLM Wiki pages consulted
Not applicable — infrastructure issue, no domain knowledge.

### Documents consulted
- Issue #2070 body — confirms 103 MB push failure on `cost-tracking.jsonl`; lists 4 acceptance criteria.
- `.gitignore` — confirms `.claude/state/session-signals/` is intentionally tracked (`!.claude/state/session-signals/`); explicit re-include for `cost-tracking.jsonl`. Bypassing with ignore is therefore wrong remedy.
- Related issue #1782 — "zero-loss agent learnings" epic explains *why* these JSONL files are deliberately git-tracked: they feed the comprehensive-learning pipeline and are corpus for #1720 (session corpus mining).
- Related issue #1995 (closed) — LLM Wiki epic; tangential, confirms compounding-knowledge philosophy that motivates keeping the data.
- Live filesystem snapshot (2026-04-17): `.claude/state/session-signals/` is **58 MB total**; `cost-tracking.jsonl` alone is **45 MB** — already 45% of the GitHub hard limit and trending toward another push failure within 6–8 weeks at current growth.

### Gaps identified
- No pre-commit guard exists that rejects tracked state files above a size threshold.
- No rotation policy for `cost-tracking.jsonl` — it grows unbounded.
- No documented recovery path for the next time a tracked file blows past 100 MB (the prior fix was ad-hoc worktree reconstruction, not in any runbook).
- No weekly health report — currently the only signal is a failed push (too late).

Source count: 6 (issue body + 5 others). ✅ ≥3 required.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-16-issue-2070-state-size-guard.md |
| Pre-commit hook | `.claude/hooks/check-state-file-size.sh` |
| Rotation script | `scripts/state/rotate-cost-tracking.sh` |
| Weekly size-report cron | `scripts/cron/state-size-report.sh` |
| Tests | `tests/hooks/test_check_state_file_size.bats` |
| Recovery runbook | `docs/runbooks/oversized-state-file-recovery.md` |
| Settings wiring | `.claude/settings.json` (PreToolUse hook entry for `Bash(git commit*)` and `Bash(git push*)`) |

---

## Deliverable

A pre-commit / pre-push hook that blocks any tracked file under `.claude/state/` larger than 90 MB, paired with a monthly rotation script for `cost-tracking.jsonl` and a weekly size-trend cron report — so the 103 MB push failure class of bugs cannot recur.

---

## Pseudocode

```
# .claude/hooks/check-state-file-size.sh
THRESHOLD_MB = 90
WARN_MB      = 50
WATCH_PATHS  = [".claude/state/**"]

staged_files = git diff --cached --name-only --diff-filter=ACMR
for file in staged_files:
    if file matches WATCH_PATHS:
        size = stat --format=%s working_tree/$file        # use working tree, not blob
        size_mb = size / 1_048_576
        if size_mb > THRESHOLD_MB:
            print "BLOCKED: $file is ${size_mb}MB (limit ${THRESHOLD_MB}MB).
                   Run scripts/state/rotate-cost-tracking.sh or move to LFS."
            exit 1
        elif size_mb > WARN_MB:
            print "WARN: $file is ${size_mb}MB (warn ${WARN_MB}MB)."

# scripts/state/rotate-cost-tracking.sh
SRC = ".claude/state/session-signals/cost-tracking.jsonl"
ARCHIVE_DIR = ".claude/state/session-signals/archive/"
if size_mb(SRC) > 30:
    today = $(date +%Y-%m-%d)
    mv $SRC $ARCHIVE_DIR/cost-tracking-$today.jsonl
    gzip $ARCHIVE_DIR/cost-tracking-$today.jsonl
    touch $SRC
    git add $SRC $ARCHIVE_DIR/cost-tracking-$today.jsonl.gz
    git commit -m "chore(state): rotate cost-tracking.jsonl ($(date))"

# scripts/cron/state-size-report.sh  (weekly)
emit markdown report listing top 10 tracked .claude/state/* files by size,
flag any > 50MB, post to docs/reports/state-size-YYYY-WW.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/hooks/check-state-file-size.sh` | pre-commit guard |
| Create | `scripts/state/rotate-cost-tracking.sh` | manual + monthly rotation |
| Create | `scripts/cron/state-size-report.sh` | weekly trend report |
| Create | `tests/hooks/test_check_state_file_size.bats` | bats coverage for hook |
| Create | `docs/runbooks/oversized-state-file-recovery.md` | recovery path documentation |
| Modify | `.claude/settings.json` | wire hook into PreToolUse for `Bash(git commit*)` + `Bash(git push*)` |
| Modify | `.gitignore` | add `.claude/state/session-signals/archive/` rule (gzip rotated archives stay tracked) |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_hook_passes_under_50mb | small staged JSONL allowed | 1 MB file in `.claude/state/` | exit 0 |
| test_hook_warns_50_to_90mb | warn band emits stderr but exits 0 | 60 MB file | exit 0, stderr contains "WARN" |
| test_hook_blocks_over_90mb | hard block above threshold | 95 MB file | exit 1, stderr contains "BLOCKED" |
| test_hook_ignores_outside_watch_paths | only `.claude/state/**` is gated | 200 MB file in `data/` | exit 0 |
| test_hook_uses_working_tree_size | reads filesystem, not blob (handles LFS) | symlink / large blob | size from `stat`, not `git cat-file` |
| test_rotate_creates_archive_and_resets | rotation archives + truncates | 45 MB cost-tracking | archive .gz exists, source is 0 bytes |
| test_rotate_skips_when_under_30mb | no-op when small | 10 MB cost-tracking | unchanged |
| test_size_report_lists_top_10 | weekly report shape | populated state dir | markdown table with ≥1 row |

---

## Acceptance Criteria

- [ ] Hook blocks a synthesized 95 MB staged file in `.claude/state/`: `bats tests/hooks/test_check_state_file_size.bats` passes.
- [ ] Hook ignores files outside `.claude/state/`: no false positives on a 200 MB `data/` fixture.
- [ ] Rotation script reduces `cost-tracking.jsonl` from current 45 MB to 0 MB and produces a single `.gz` archive committed alongside.
- [ ] After rotation, a fresh `git push` succeeds (regression of the original failure).
- [ ] Weekly cron runs `scripts/cron/state-size-report.sh` and writes `docs/reports/state-size-YYYY-WW.md`.
- [ ] Recovery runbook exists at `docs/runbooks/oversized-state-file-recovery.md` with step-by-step worktree-reconstruction commands.
- [ ] `.claude/settings.json` references the hook so it fires on `git commit` and `git push`.
- [ ] Adversarial review artifacts posted (Claude / Codex / Gemini) — overall PASS.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** Rotating `cost-tracking.jsonl` may break the comprehensive-learning pipeline (#1782) if it expects a single contiguous file. Verify the consumer concatenates archive + live before mining.
- **Risk:** A 90 MB threshold leaves only 10 MB of headroom against GitHub's 100 MB hard cap; if a single commit adds >10 MB to a borderline file, the push still fails. Consider lowering to 75 MB.
- **Open:** Should rotated archives go to Git LFS instead of gzip-in-tree? LFS keeps history searchable but adds a dependency. (Flag for user during approval.)
- **Open:** Several other state subdirs may have the same growth profile — `cc-insights/`, `cron-health/`, `daily-summaries/`. Should the hook scan all of them or only `session-signals/`? Current plan: scan all of `.claude/state/**`, which is broader than the issue title.

---

## Complexity: T1

**T1** — single bash hook, single rotation script, single cron, ~250 lines of shell + tests. No new dependencies, no schema changes. Mirrors an existing hook (`check-claude-md-limits.sh`).

---

## Next steps (workflow)

1. User reviews this draft → requests changes or approves direction.
2. On user nod, run adversarial review via `scripts/review/run-plan-review.sh 2070` (Claude + Codex + Gemini).
3. Fold review findings into this doc, change status to `adversarial-reviewed`.
4. Set issue label to `status:plan-review`; await user `status:plan-approved`.
5. Only after `status:plan-approved` is set: implement, TDD-first, atomic commits.
