# Plan for #2911: pre-push config-drift check is worktree-incompatible

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-06-03
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2911
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-06-03-plan-2911-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/quality/check-all.sh:435-438` — FAILs (increments `FAIL_COUNT`) when a sibling repo directory is absent; this is the root cause of the worktree block.
- Found: `scripts/enforcement/check-pre-commit-hook-drift.sh:41-43` — already has the correct SKIP pattern for absent repos (`log "skip: $repo (not present)"` + `continue`). This is the model to follow.
- Found: `scripts/agents/install-pre-commit-hook-cross-repo.sh:60-70` — canonical `--git-common-dir` vs `--git-dir` worktree-detection pattern; comment reads "worktree-safe per #2722 prior art".
- Found: `.claude/skills/workspace-hub/worktree-branch-sync-hygiene/references/worktree-pre-push-bypass-for-tier1-checks.md` — documents the live bypass `GIT_PRE_PUSH_SKIP=1 git push`, confirming the bug is active and workers are using the escape hatch daily.
- Found: `docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md` — broader prior plan attempting to create a fully tracked `scripts/hooks/pre-push.sh`; status draft; MAJOR×9 adversarial review results due to scope complexity. Issue #2911 is an intentionally narrower cut targeting only the FAIL-vs-SKIP and worktree-detection gaps.
- Gap: `scripts/hooks/pre-push.sh` — does not exist; `tests/hooks/test_pre_push.py` references it and is currently red. Creating it is out of scope for this plan (deferred to #2203).

### Standards
Not applicable.

### LLM Wiki pages consulted
No relevant wiki pages.

### Documents consulted
- `docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md` — prior approach; MAJOR×9 because it tried to scope-limit by changed-file diff, which proved complex. This plan avoids that path and uses the simpler SKIP-on-missing pattern.
- `.claude/skills/workspace-hub/worktree-branch-sync-hygiene/references/worktree-pre-push-bypass-for-tier1-checks.md` — confirms `GIT_PRE_PUSH_SKIP=1` bypass is the current live workaround.
- Issue #2911 body — exact repro steps; three proposed options. This plan adopts Option 2 (SKIP on missing) + Option 1 (worktree detection guard); explicitly NOT Option 3 (scope-limit by changed files, proven complex in #2203 history).

### Gaps identified
- `check-all.sh` has no worktree guard and FAILs (not SKIPs) for absent sibling repo dirs.
- `check-pre-commit-hook-drift.sh` resolves `WS_ROOT/../$repo` from `git show-toplevel`, which returns the wrong path from a worktree. In practice the SKIP-on-missing at lines 41-43 prevents hard failure, but only because the wrong path resolves to a nonexistent dir. A proper worktree-early-exit guard removes the reliance on that coincidence.
- No test exists verifying pre-push enforcement behaves correctly (SKIP, not FAIL) when called from a worktree.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-03 via GitHub MCP):
- `#2911` — OPEN — "bug(hooks): pre-push config-drift check is worktree-incompatible (blocks push from any worktree)"

**File existence** (verified by resource intel agent 2026-06-03):
- EXISTS: `scripts/quality/check-all.sh`
- EXISTS: `scripts/enforcement/check-pre-commit-hook-drift.sh`
- EXISTS: `scripts/agents/install-pre-commit-hook-cross-repo.sh`
- EXISTS: `tests/hooks/test_pre_push.py` (red — missing `scripts/hooks/pre-push.sh`, out of this plan's scope)
- MISSING: `scripts/hooks/pre-push.sh` — deferred to #2203
- MISSING: `.git/hooks/pre-push` (only `.sample` present in this environment)

**Line excerpts** (from resource intel agent):
```bash
# check-all.sh:435-438 — root cause (target for FAIL→SKIP change)
if [[ ! -d "$repo_path" ]]; then
  FAIL_COUNT++   # ← change to: log WARN + continue (no FAIL_COUNT increment)
fi

# check-pre-commit-hook-drift.sh:41-43 — existing SKIP pattern (follow this model)
if [[ ! -e "$REPO_PATH/.git" ]]; then
  log "skip: $repo (not present at $REPO_PATH)"
  continue
fi

# install-pre-commit-hook-cross-repo.sh:60-70 — canonical worktree detection
GIT_COMMON_DIR="$(git -C "$REPO_PATH" rev-parse --git-common-dir 2>/dev/null)"
GIT_DIR="$(git -C "$REPO_PATH" rev-parse --git-dir 2>/dev/null)"
# worktree condition: GIT_COMMON_DIR != GIT_DIR when in linked worktree
```

**Reproduction proof:**
```bash
# Exact repro from issue body:
git worktree add -b tmp/x /tmp/wt origin/main
cd /tmp/wt && touch x && git add x && git commit -m x && git push -u origin tmp/x
# Observed output:
#   []  ERROR: directory not found: /tmp/wt/digitalmodel
#   Summary: 0/1 PASS, 1/1 FAIL
#   Exit code: 1
```
- Failure mode matches issue claim: YES
- Live bypass confirmed: `GIT_PRE_PUSH_SKIP=1 git push` in skill file

<!-- Verification: 6 distinct sources: issue body (#2911), check-all.sh, check-pre-commit-hook-drift.sh, install-pre-commit-hook-cross-repo.sh, worktree bypass skill, docs/plans/2026-04-21-issue-2203. Count: 6 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-03-issue-2911-prepush-worktree-skip.md` |
| Root cause fix | `scripts/quality/check-all.sh` |
| Secondary guard | `scripts/enforcement/check-pre-commit-hook-drift.sh` |
| Tests (new) | `tests/hooks/test_check_all_worktree.sh` |
| Plan review — Claude | `scripts/review/results/2026-06-03-plan-2911-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-03-plan-2911-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-03-plan-2911-gemini.md` |

---

## Deliverable

`git push` from any git worktree no longer hard-fails due to absent sibling-repo directories: `check-all.sh` emits a SKIP warning for absent repos instead of incrementing `FAIL_COUNT`, and `check-pre-commit-hook-drift.sh` gains a worktree-early-exit guard so the `WS_ROOT/../$repo` path error is preempted.

---

## Pseudocode

Trivial — see Files to Change. Both changes are targeted 3–5 line edits following existing codebase patterns; no new logic design required.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/quality/check-all.sh:435-438` | Change FAIL→SKIP for absent sibling repo dirs; emit a WARN line instead of incrementing `FAIL_COUNT`. Follow `check-pre-commit-hook-drift.sh:41-43` pattern. |
| Modify | `scripts/enforcement/check-pre-commit-hook-drift.sh` | Add worktree early-exit at top of script using `--git-common-dir` vs `--git-dir` canonical pattern. Exit 0 with "SKIP: running from a linked worktree" log line. |
| Create | `tests/hooks/test_check_all_worktree.sh` | Bash regression tests for the new SKIP behavior: absent-dir exits 0 with SKIP message; present-dir with drift still FAILs (regression guard). |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_check_all_missing_sibling_emits_skip` | SKIP (not FAIL) when sibling dir absent | `QUALITY_REPO_ROOT` pointing to dir with no siblings | exit 0; stdout/stderr contains "SKIP" or "skip"; no "ERROR: directory not found" |
| `test_check_all_missing_sibling_no_fail_count` | FAIL_COUNT not incremented for absent repos | same as above | summary line shows 0 failures |
| `test_check_all_present_drift_still_fails` | regression — drift in a present repo still exits non-zero | create a present sibling dir with deliberate drift | exit non-zero; "FAIL" in output |
| `test_drift_guard_worktree_early_exit` | `check-pre-commit-hook-drift.sh` exits 0 when GIT_DIR points into `.git/worktrees/` | simulate worktree env via `GIT_DIR` override | exit 0; "SKIP: linked worktree" in output |

---

## Acceptance Criteria

- [ ] `git push` from a worktree (exact repro in issue body) exits 0 (no FAIL from absent sibling dirs).
- [ ] `check-all.sh` emits a SKIP warning for absent sibling repos and exits 0; does NOT emit "ERROR: directory not found".
- [ ] `check-pre-commit-hook-drift.sh` detects a linked-worktree caller via `--git-common-dir` and exits 0 with a SKIP message.
- [ ] `check-all.sh` still FAILs when a *present* repo has an actual config drift (regression guard).
- [ ] All new tests in `tests/hooks/test_check_all_worktree.sh` pass.
- [ ] `GIT_PRE_PUSH_SKIP=1` bypass remains valid — the bypass skill file needs no change.
- [ ] `scripts/hooks/pre-push.sh` is NOT created by this plan (deferred to #2203); `tests/hooks/test_pre_push.py` remains red and that is expected.
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

<!-- Filled after adversarial review. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** FAIL→SKIP change could silently hide drift if sibling repos are expected to be present on the executing machine. Mitigation: emit a distinct `[SKIP] repo not found` WARN line (not silent) so operators know the check was bypassed, not passed.
- **Risk:** This plan does NOT create `scripts/hooks/pre-push.sh`, so `tests/hooks/test_pre_push.py` remains red. That is explicitly deferred to #2203. Scope is intentional.
- **Relationship to #2203:** #2203 is the broader work to create a fully tracked, TDD-covered `scripts/hooks/pre-push.sh`. #2911 is a targeted unblock that can land independently. #2203 can then proceed cleanly with the SKIP behavior already in place.
- **Open:** Should the worktree early-exit in `check-pre-commit-hook-drift.sh` warn to stderr or be silent? Recommend warn, matching the `install-pre-commit-hook-cross-repo.sh` precedent.

---

## Complexity: T1

**T1** — 2 existing files modified (each a targeted 3–5 line edit matching established codebase SKIP patterns), 1 new test file. No new modules or API surface added.
