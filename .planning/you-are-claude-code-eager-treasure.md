# Audit: should Claude execute #2070 now? — Verdict: **DEFER (do not execute)**

> Operator: Hermes / ace-linux-1, ~40% weekly capacity, ~36 h to reset
> Lane: read-only / plan-mode unless explicitly authorized
> Date: 2026-04-30
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2070
> Plan under review: `docs/plans/2026-04-16-issue-2070-state-size-guard.md`

---

## Context — why this audit exists

Issue #2070 ("Guard Claude state sync against oversized session-signal files") shows the dual-label combination `status:plan-approved` + `status:working` + `agent:codex` and is OPEN. The local approval marker is missing. The operator wants to know whether this Claude lane should execute or defer, before any code is written.

The plan was approved on 2026-04-17 after a 3-way adversarial review (Claude/Codex MAJOR, Gemini MINOR → revisions applied). The original 13 acceptance criteria were implemented end-to-end in 7 atomic commits on 2026-04-17 and merged to `main`. A separate Codex follow-on tranche landed on a feature branch on 2026-04-28 and is **still unmerged**. Restarting implementation here would race that branch and likely lose its work.

---

## Worker contention check — 2026-04-30

### What's already on `main`

Six `#2070` commits are reachable from `main` (all dated 2026-04-17):

| Commit | Component |
|---|---|
| `45a00c9ad` | pre-commit state-file size guard |
| `671aeccbb` | pre-push state-file size guard |
| `885cfe9b2` | consumer-compat verifier + gz support in `wrk_cost_report.py` |
| `5811f9451` | rotation script (gated on verifier, no auto-commit) |
| `260e425d8` | weekly state-size cron report + first run |
| `fcd4862cf` | recovery runbook |
| `0dd242932` | first real rotation: `cost-tracking.jsonl` 45 MB → 3.9 MB gz |

Verified tracked on `main` right now:
- `.claude/hooks/check-state-file-size-precommit.sh`
- `.claude/hooks/check-state-file-size-prepush.sh`
- `scripts/state/rotate-cost-tracking.sh`
- `scripts/state/verify-consumer-compat.sh`
- `scripts/cron/state-size-report.sh`
- `tests/hooks/test_check_state_file_size_prepush.py`
- `docs/reports/state-size-2026-W16.md`

The 13 acceptance criteria in the approved plan are fully discharged on `main`. There is no fresh Claude implementation work left for the originally approved plan.

### What's on the unmerged Codex tranche

Branch `codex/10thread-20260428-issue-2070`, single commit `7ca04f25b` ("fix(state): wire session signal size guards"). The `#2070`-substantive deltas vs. `main` are exactly four files:

| File | Delta nature |
|---|---|
| `.claude/settings.json` | **NEW** PreToolUse matchers wiring `Bash(git commit*)` → precommit hook and `Bash(git push*)` → prepush hook (currently main has neither) |
| `.claude/hooks/check-state-file-size-prepush.sh` | Hardens stdin parsing — adds `is_oid` validator, splits the loop into `check_push_ref`, and adds `infer_current_push_ref` fallback so Claude PreToolUse JSON stdin no longer no-ops the guard |
| `tests/hooks/test_check_state_file_size_prepush.py` | Adds `test_prepush_blocks_when_invoked_from_claude_pretooluse_json` regression test |
| `tests/hooks/test_state_size_settings_wiring.py` | **NEW** file; asserts settings.json wires both matchers to the guard scripts |

Plus `docs/reports/state-size-2026-W18.md` (a regenerated weekly report — main has W16 only, no W17/W18).

The tranche is genuinely novel and load-bearing: without it, the hooks exist on disk but are never invoked by Claude's harness, so the guards are effectively dormant for the most common write path on this repo.

### Why merging is non-trivial

The codex branch diverged ~2 days ago and has not been rebased. `git diff --stat main..origin/codex/10thread-20260428-issue-2070` shows hundreds of additional lines of drift across `.claude/memory/`, `docs/plans/`, `docs/reports/`, `config/`, etc. — many are deletions of files that have since been added to main. A naive merge or fast-forward would silently revert recent ecosystem work (consistent with the `feedback_merge_race_silent_revert.md` and `feedback_autosync_silent_pusher.md` hazards in memory).

### Active processes touching #2070

`pgrep -af 'codex|claude|hermes|2070'` shows VS Code Codex extension hosts, Hermes TUI/gateway processes, and Claude Desktop electron — none are an active executor for #2070 on this branch right now. The Apr 28 dispatch comment says the lane was a Codex 10-thread bounded run; Codex's last update on this issue was 2026-04-28 07:32 UTC and the branch has not advanced since.

---

## Verdict — DEFER

Claude should **not** open a new implementation lane for #2070. Reasons:

1. **No work remains for the approved plan.** All 13 acceptance criteria are already merged to `main` with 24/24 tests green.
2. **The remaining gap is already authored.** The Claude-harness wiring and JSON-stdin fallback hardening that close the "guards exist but never fire" gap live on `codex/10thread-20260428-issue-2070`. Re-implementing them in a parallel lane would duplicate ~70 lines of shell + 2 tests and would race the codex branch on `.claude/settings.json`.
3. **The bottleneck is human PR review, not implementation.** Codex's last comment explicitly leaves the issue open for human review of `7ca04f25b`. The dual `plan-approved` + `working` labels reflect that — not a missed local marker.
4. **Operator constraints align with deferral.** Read-only / plan-mode lane; "do not mutate GitHub labels or close issues"; subscription-budget conservation.

---

## Exact safe next action

The next action is **not a Claude execution lane** — it is a human-gated merge decision on the existing Codex tranche. Concretely, in priority order:

### 1. Surface the unmerged tranche to the operator (read-only — can be done now)

The Codex Apr 28 commit `7ca04f25b` is pushed to `origin/codex/10thread-20260428-issue-2070` and has no PR opened against it yet (per `gh issue view 2070` thread; PR-list verification was not approved in this lane). Recommended operator nudge: open a PR from that branch with the diff scoped to the four `#2070` files only, so reviewers don't have to mentally subtract the unrelated drift.

### 2. Decide merge mechanics (operator call)

Two viable paths, both human-driven:

| Path | Pros | Cons |
|---|---|---|
| **Cherry-pick the 4 #2070 files onto a fresh branch from `main`** | Surgical; avoids the ~250-commit drift; clean PR | Requires hand-rebuilding the commit message; loses authorship link to `7ca04f25b` |
| **Rebase `codex/10thread-20260428-issue-2070` onto `main` and resolve conflicts file-by-file** | Preserves authorship | Large conflict surface in `.claude/memory/` and `docs/plans/`; high risk of silently reverting recent main work; touches files this lane is told not to clean |

The cherry-pick path is safer for this repo's auto-sync environment. Either path needs a human at the keyboard — neither is a fit for an autonomous Claude lane.

### 3. Validate before merging (any lane, after PR is open)

Run from the merge candidate:

```
uv run --no-project python -m pytest \
  tests/hooks/test_check_state_file_size_precommit.py \
  tests/hooks/test_check_state_file_size_prepush.py \
  tests/hooks/test_state_size_settings_wiring.py \
  tests/state/test_rotate_cost_tracking.py \
  tests/cron/test_state_size_report.py \
  tests/ai/test_wrk_cost_report_rotation.py -q

bash scripts/state/verify-consumer-compat.sh
bash scripts/cron/state-size-report.sh    # regenerate the current-week report
```

Expected: all tests green (Codex previously reported 23 passing), verifier exits 0, cron writes a fresh `docs/reports/state-size-2026-W18.md` (or current-ISO-week file).

### 4. After merge, close the loop on labels (operator only)

Per operator instruction this lane will not mutate labels. The operator should drop `status:working`, leave `status:plan-approved` (per `feedback_issue_2460_approval_binding`-style precedent of revision-bound markers, ideally append a comment citing the merged SHA), and apply whatever close label is conventional once the merge lands and verification passes.

---

## Why no TDD implementation prompt is drafted

The original task brief asked for a TDD prompt "if safe." It is not safe here:

- The plan's TDD test list is already implemented and merged (every test in the plan's "TDD Test List" table maps to a file present on `main`).
- The remaining delta (Claude harness wiring + JSON-stdin fallback) is already implemented and tested on the codex branch — there are no failing tests to drive a fresh TDD cycle from.
- A TDD prompt that re-derives the same code in a worktree would create a divergent second implementation, force a merge conflict on `.claude/settings.json`, and burn weekly capacity for zero net delivery.

If, after human review, the operator decides the codex tranche should be replaced rather than landed (e.g., for stylistic or attribution reasons), a fresh TDD plan should be authored against the *current* `main` — not against the 2026-04-16 plan, which is closed-out.

---

## Verification checklist for this audit

- [x] Plan file read in full (`docs/plans/2026-04-16-issue-2070-state-size-guard.md`, 246 lines).
- [x] Issue metadata + comment thread inspected via `gh issue view 2070`.
- [x] All `#2070` commits traced; presence on `main` verified via `git ls-files`.
- [x] Codex tranche identity, branch position, and substantive diff confirmed (`git log main..origin/codex/...`, `git diff --stat`, `git diff` on the 3 modified files, `git show` on the new file).
- [x] Active-process scan run; no live executor competing for #2070.
- [x] No labels mutated, no issues closed, no files outside this plan file edited, no processes killed.

---

## Critical files referenced (for follow-up)

| Purpose | Path |
|---|---|
| Approved plan | `docs/plans/2026-04-16-issue-2070-state-size-guard.md` |
| Pre-commit guard (on main) | `.claude/hooks/check-state-file-size-precommit.sh` |
| Pre-push guard (on main; hardened on codex branch) | `.claude/hooks/check-state-file-size-prepush.sh` |
| Rotation script (on main) | `scripts/state/rotate-cost-tracking.sh` |
| Consumer-compat verifier (on main) | `scripts/state/verify-consumer-compat.sh` |
| Weekly cron (on main) | `scripts/cron/state-size-report.sh` |
| Settings wiring (**only on codex branch**) | `.claude/settings.json` |
| Wiring test (**only on codex branch**) | `tests/hooks/test_state_size_settings_wiring.py` |
| Codex tranche commit | `7ca04f25bdb57b1ba420cd11295a63be8bb41263` |
| Codex tranche branch | `origin/codex/10thread-20260428-issue-2070` |
