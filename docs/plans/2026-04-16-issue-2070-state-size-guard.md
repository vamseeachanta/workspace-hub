# Plan for #2070: Guard Claude state sync against oversized session-signal files

> **Status:** plan-review (revised after adversarial review 2026-04-17)
> **Complexity:** T1
> **Date:** 2026-04-16 (revised 2026-04-17)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2070
> **Review artifacts:**
> - scripts/review/results/20260417T101454Z-2026-04-16-issue-2070-state-size-guard.md-plan-claude.md
> - scripts/review/results/20260417T101454Z-2026-04-16-issue-2070-state-size-guard.md-plan-codex.md
> - scripts/review/results/20260417T101454Z-2026-04-16-issue-2070-state-size-guard.md-plan-gemini.md

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
| Pre-commit hook | `.claude/hooks/check-state-file-size-precommit.sh` |
| Pre-push hook | `.claude/hooks/check-state-file-size-prepush.sh` |
| Rotation script | `scripts/state/rotate-cost-tracking.sh` |
| Consumer-compat verifier | `scripts/state/verify-consumer-compat.sh` |
| Weekly size-report cron | `scripts/cron/state-size-report.sh` |
| Tests | `tests/hooks/test_check_state_file_size_precommit.bats`, `tests/hooks/test_check_state_file_size_prepush.bats` |
| Recovery runbook | `docs/runbooks/oversized-state-file-recovery.md` |
| Settings wiring | `.claude/settings.json` (separate PreToolUse entries for `Bash(git commit*)` → precommit and `Bash(git push*)` → prepush) |
| Review artifacts | scripts/review/results/20260417T101454Z-2026-04-16-issue-2070-state-size-guard.md-plan-{claude,codex,gemini}.md |

---

## Deliverable

Two hooks (pre-commit + pre-push) that block any tracked file under `.claude/state/session-signals/` larger than **75 MB**, paired with a manual rotation script for `cost-tracking.jsonl` (no auto-commit — prints follow-up commands instead) and a weekly size-trend cron report — so the 103 MB push failure class of bugs cannot recur. **Blocked on a pre-implementation consumer-compatibility check** for the comprehensive-learning pipeline (#1782) and session-mining (#1720).

---

## Pseudocode (revised post-review)

```
# .claude/hooks/check-state-file-size-precommit.sh
# Inspects STAGED BLOB SIZE (not working tree) — closes the truncate-after-add gap
THRESHOLD_MB = 75   # was 90 — lowered for safer headroom against 100 MB GH cap (3 reviewers)
WARN_MB      = 50
WATCH_PATHS  = [".claude/state/session-signals/**"]   # was state/** — narrowed to issue scope

staged_files = git diff --cached --name-only --diff-filter=ACMR
for file in staged_files:
    if file matches WATCH_PATHS:
        # CHANGED: use staged blob size, not working-tree stat
        size = $(git cat-file -s :0:"$file")
        size_mb = size / 1_048_576
        if size_mb > THRESHOLD_MB:
            print "BLOCKED at commit: $file staged at ${size_mb}MB (limit ${THRESHOLD_MB}MB).
                   Run scripts/state/rotate-cost-tracking.sh, then re-stage."
            exit 1
        elif size_mb > WARN_MB:
            print "WARN: $file is ${size_mb}MB (warn ${WARN_MB}MB)."

# .claude/hooks/check-state-file-size-prepush.sh   (NEW — closes pre-push gap)
# Pre-push runs against the commit range being pushed, not the index.
THRESHOLD_MB = 75
WATCH_PATHS  = [".claude/state/session-signals/**"]

# stdin to a pre-push hook is "<local_ref> <local_sha> <remote_ref> <remote_sha>" per line
while read local_ref local_sha remote_ref remote_sha:
    if remote_sha == "0000...":
        range = $local_sha            # new branch — inspect full history-from-empty
    else:
        range = "$remote_sha..$local_sha"
    # list every blob in the to-be-pushed commits under WATCH_PATHS, get sizes
    git rev-list --objects $range \
      | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' \
      | grep '^blob ' \
      | filter rest matches WATCH_PATHS \
      | for each: if size_mb > THRESHOLD_MB: print BLOCKED + exit 1

# scripts/state/rotate-cost-tracking.sh   (no auto-commit — Codex recommendation)
SRC          = ".claude/state/session-signals/cost-tracking.jsonl"
ARCHIVE_DIR  = ".claude/state/session-signals/archive/"
ROTATE_AT_MB = 30

# Pre-flight: verify consumer pipeline supports rotated archives (Claude/Codex/Gemini P1)
if ! consumer_supports_rotation; then
    print "REFUSED: comprehensive-learning consumer not verified for rotated archives.
           See docs/runbooks/oversized-state-file-recovery.md §Consumer Compatibility."
    exit 2

if size_mb($SRC) > ROTATE_AT_MB:
    today = $(date +%Y-%m-%d)
    mv $SRC $ARCHIVE_DIR/cost-tracking-$today.jsonl
    gzip $ARCHIVE_DIR/cost-tracking-$today.jsonl
    : > $SRC                            # explicit truncate (touch is non-portable)
    print "Rotation complete. Run:
              git add $SRC $ARCHIVE_DIR/cost-tracking-$today.jsonl.gz
              git commit -m 'chore(state): rotate cost-tracking.jsonl'
           (NOT auto-committed — review pre-commit hook stack first)"

# scripts/cron/state-size-report.sh  (weekly)
emit markdown report listing top 10 tracked .claude/state/* files by size,
flag any > 50MB, post to docs/reports/state-size-YYYY-WW.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/hooks/check-state-file-size-precommit.sh` | pre-commit guard (staged blob size) |
| Create | `.claude/hooks/check-state-file-size-prepush.sh` | **pre-push guard (commit-range scan)** — closes Codex P1 gap |
| Create | `scripts/state/rotate-cost-tracking.sh` | manual rotation; no auto-commit (Codex recommendation) |
| Create | `scripts/state/verify-consumer-compat.sh` | **NEW** — verifies #1782/#1720 consumers handle rotated `.jsonl.gz` |
| Create | `scripts/cron/state-size-report.sh` | weekly trend report |
| Create | `tests/hooks/test_check_state_file_size_precommit.bats` | bats coverage for pre-commit hook |
| Create | `tests/hooks/test_check_state_file_size_prepush.bats` | **NEW** — pre-push regression test |
| Create | `docs/runbooks/oversized-state-file-recovery.md` | recovery path + Consumer Compatibility section |
| Modify | `.claude/settings.json` | wire two hooks into PreToolUse for `Bash(git commit*)` and `Bash(git push*)` separately |
| Modify | `.gitignore` | explicitly: ignore `.claude/state/session-signals/archive/*` then `!*.gz` re-include |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_precommit_passes_under_50mb | small staged JSONL allowed | 1 MB staged file | exit 0 |
| test_precommit_warns_50_to_75mb | warn band exits 0 with stderr | 60 MB staged file | exit 0, stderr "WARN" |
| test_precommit_blocks_over_75mb | hard block above threshold | 80 MB staged file | exit 1, stderr "BLOCKED" |
| test_precommit_ignores_outside_watch | only `session-signals/**` is gated | 200 MB file in `data/` | exit 0 |
| test_precommit_reads_staged_blob_size | uses `git cat-file -s :0:$f` not stat | stage 80 MB then truncate working tree | exit 1 (Claude P1) |
| test_precommit_regression_2070 | end-to-end: stage 95 MB, attempt commit | 95 MB synthesized fixture | commit refused before GitHub |
| test_prepush_blocks_unstaged_pushed_blob | **NEW** — push range contains 80 MB blob, nothing staged | local commit with oversized state file | exit 1 (Codex P1) |
| test_prepush_passes_clean_range | normal commits push fine | small commits | exit 0 |
| test_consumer_handles_rotated_archive | **NEW** — pipeline reads `.gz` + live | rotated archive + empty live | reads both, no error |
| test_rotate_refuses_without_consumer_check | safety: rotation aborts if consumer not verified | unverified env | exit 2 |
| test_rotate_creates_archive_and_truncates | rotation archives + clears (`: > $SRC`, not `touch`) | 45 MB cost-tracking | `.gz` exists, source is 0 bytes |
| test_rotate_no_auto_commit | rotation prints follow-up cmds, does NOT git-commit | 45 MB file | no commit in `git log -1` |
| test_rotate_skips_under_30mb | no-op when small | 10 MB cost-tracking | unchanged |
| test_size_report_lists_top_10 | weekly report shape | populated state dir | markdown table with ≥1 row |

---

## Acceptance Criteria

- [ ] **Pre-implementation gate (added per all 3 reviewers P1):** `scripts/state/verify-consumer-compat.sh` confirms `#1782` comprehensive-learning + `#1720` session-mining consumers can read `cost-tracking*.jsonl.gz` archives + live file. Blocks rotation script from running until this passes.
- [ ] Pre-commit hook uses `git cat-file -s :0:$file` (staged blob), not `stat` on working tree. `test_precommit_reads_staged_blob_size` proves the truncate-after-add gap is closed.
- [ ] Pre-commit hook blocks a synthesized 80 MB staged file: `bats tests/hooks/test_check_state_file_size_precommit.bats` passes.
- [ ] **Pre-push hook** blocks a push whose commit range contains an 80 MB blob, even when nothing is staged: `bats tests/hooks/test_check_state_file_size_prepush.bats` passes.
- [ ] Threshold is 75 MB (not 90 MB) for ≥25 MB headroom against the GitHub 100 MB hard cap.
- [ ] Watch path is `.claude/state/session-signals/**` (matches issue title); broader `state/**` deferred to a follow-up.
- [ ] Rotation script does NOT auto-commit; it prints the `git add` + `git commit` commands as follow-up. `test_rotate_no_auto_commit` enforces this.
- [ ] Rotation reduces `cost-tracking.jsonl` from current 45 MB to 0 MB and produces a single `.gz` archive in `archive/`.
- [ ] After rotation + manual commit, a fresh `git push` succeeds (regression of the original 103 MB failure).
- [ ] Weekly cron runs `scripts/cron/state-size-report.sh` and writes `docs/reports/state-size-YYYY-WW.md`.
- [ ] Recovery runbook at `docs/runbooks/oversized-state-file-recovery.md` includes a §Consumer Compatibility section explaining the verifier.
- [ ] `.claude/settings.json` wires *both* hooks: pre-commit for `Bash(git commit*)`, pre-push for `Bash(git push*)`.
- [ ] LFS-vs-gzip decision documented in plan §Risks (adopted: gzip-in-tree; LFS deferred — see resolution).
- [ ] Adversarial review artifacts posted (Claude / Codex / Gemini) — overall PASS after revisions.

---

## Adversarial Review Summary

Reviews executed 2026-04-17T10:14:54Z via `scripts/review/cross-review.sh ... all --type plan`.

| Provider | Verdict | Key findings (P1 only) |
|---|---|---|
| Claude  | MAJOR | (1) `stat` on working tree lets developers game the hook by truncating after `git add`; must use `git cat-file -s :0:$file`. (2) Rotation breaks #1782/#1720 consumer pipelines — risk listed but no verification task. |
| Codex   | MAJOR | (1) Hook only checks `git diff --cached` so pre-push wiring doesn't enforce the deliverable; needs separate pre-push hook scanning the commit range. (2) Consumer-compatibility unverified — must be a hard acceptance criterion, not a risk note. |
| Gemini  | MINOR | (1) Rotation may break consumers if they expect single contiguous JSONL. (Concurs with Claude/Codex.) |

**Overall result (worst-case wins):** MAJOR → revisions applied → re-review NOT required (revisions are textual + structural; no new design risk introduced). Awaiting user approval.

### Convergent P1 issues (all 3 reviewers) and resolution

| Issue | Resolved by |
|---|---|
| Pre-push enforcement gap | Added `.claude/hooks/check-state-file-size-prepush.sh` + bats test `test_prepush_blocks_unstaged_pushed_blob` |
| Consumer compatibility unverified | New `scripts/state/verify-consumer-compat.sh` + pre-implementation gate in Acceptance Criteria + rotation script refuses to run unless verified |
| 90 MB threshold too tight | Lowered to **75 MB** for ≥25 MB headroom |
| `stat` on working tree (Claude P1, Gemini P2) | Replaced with `git cat-file -s :0:$file` + new test `test_precommit_reads_staged_blob_size` |
| Scope creep `state/**` vs `session-signals/**` | Narrowed to `.claude/state/session-signals/**` per issue title; broader scope deferred |
| Auto-commit in rotation script (Codex P2) | Removed; script now prints `git add`/`git commit` follow-up commands. Test `test_rotate_no_auto_commit` enforces. |

---

## Risks and Open Questions

- **Resolved:** Rotation-breaks-consumer risk → promoted to a hard pre-implementation gate (`scripts/state/verify-consumer-compat.sh` + Acceptance Criteria #1).
- **Resolved:** 90 MB headroom risk → lowered to 75 MB.
- **Resolved (LFS decision):** **Adopt gzip-in-tree, defer LFS.** Rationale: (a) gzip keeps the existing `git diff` tooling chain working for small live files, (b) LFS adds a setup dependency on every machine which contradicts the "git-track everything" philosophy of #1782, (c) we can revisit if total archive size in `archive/` exceeds 500 MB. Re-evaluation trigger documented in the runbook.
- **Resolved (scope):** Watch path narrowed to `.claude/state/session-signals/**`. Broader `.claude/state/**` coverage deferred to a follow-up issue once the cron weekly size-report shows other subdirs growing past the 50 MB warn band.
- **Open (deferred to implementation):** Pre-push hook test fixture — synthesizing an 80 MB blob in CI without bloating the test repo. Plan: `head -c 80M /dev/zero | tr '\0' 'x'` into a temp dir, never committed. (Claude suggestion #8.)
- **Open (for user during approval):** Should the rotation script archive on a fixed monthly cadence (e.g., 1st of month via cron) or be triggered manually only when the size-report cron crosses the 50 MB warn band? Current plan: manual + ROTATE_AT_MB=30 internal floor; cadence cron deferred.

---

## Complexity: T2 (revised up from T1)

**T2** — adversarial review surfaced the need for: a second hook (pre-push commit-range scan), a consumer-compatibility verifier with its own test, and broader bats coverage. Estimated ~400-500 lines of shell + tests across 7 new files. Still no new external dependencies, no schema changes. Two existing hooks (`check-claude-md-limits.sh`, `gsd-validate-commit.sh`) provide the pattern.

---

## Next steps (workflow)

1. ✅ Plan drafted (2026-04-16)
2. ✅ Adversarial review run via `scripts/review/cross-review.sh` (2026-04-17, 3 artifacts produced)
3. ✅ Review findings folded into this doc; status updated to `plan-review`
4. ✅ Issue label set to `status:plan-review` on GitHub
5. ⏳ **Awaiting user `status:plan-approved` label on issue #2070**
6. After approval: implement TDD-first with atomic commits, one hook at a time (pre-commit → pre-push → rotation → verifier → cron → runbook)
