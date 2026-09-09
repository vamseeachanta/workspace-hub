# Handoff — dispatch control surface complete; client-PII leak found and fixed but NOT merged

**Date:** 2026-08-02
**Repo state:** on `main`, `0 ahead / 0 behind origin/main`, nothing of mine uncommitted
**Prior handoff:** [`2026-08-02-dispatch-epic-complete-entry-prompt.md`](2026-08-02-dispatch-epic-complete-entry-prompt.md) — PR #3761, **closed** rather than merged; its §3 lessons held, its §5 inventory did not

---

## 1. Do this first

**Provision `LEGAL_CLIENT_MAP` as a repo secret, then merge [#3777](https://github.com/vamseeachanta/workspace-hub/pull/3777).** It is CLEAN and waiting.

The order matters: #3777 makes `reconcile.py` fail closed without that map, so merging first turns a leaking cron into a red cron. Both beat the status quo; secret-then-merge beats both.

**The leak is live and regenerating.** Verified minutes before writing this, on artifacts a cron rewrote *during* the session:

```
$ check-client-pii.py config/ai-tools/provider-kanban.json config/ai-tools/provider-work-queue.json
✖ Client identifier(s) found in tracked file(s)
  provider-kanban.json:    line(s) 1321,1334,1360,1373,4035,4048,9484,9497,9523,9536 …
  provider-work-queue.json: line(s) 1201,1379,3323
```

Every 20 minutes (`reconcile.py`) and every 4 hours (`provider-*`), unscanned. #3777 fixes all of it.

---

## 2. What shipped

Merged to `main`, all verified by content after merge:

| PR | |
|---|---|
| #3767 | routed cards had empty titles — the fetch never requested the field |
| #3769 | those titles then leaked client identifiers into public queue files |
| #3771 | **22 board files mirroring PRIVATE repos** into this public one — 595 cards, 214 body excerpts |
| #3774 | the pull loop made real, six unattended-running rails, cross-machine leases (#3772), refused-claim fix (#3764) |
| #3776 | heartbeat beater lifting the 90-minute payload ceiling, schedule, operator runbook |

**857 tests** on the dispatch surface. Every rail mutation-verified.

Open: **#3777** (CLEAN, see §1) and **#3766** (the #3762 harness plan, two MAJOR reviews absorbed, awaiting the approval gate).

---

## 3. The dispatch surface is done except for one deliberate gap

Everything works: the loop invokes `drain.py`, leases cross machines, claims can't strand, the WIP cap binds, `PAUSE` stops it, timeouts kill, exhaustion quarantines, `chain.py` separates *ran* from *succeeded*, and it is scheduled `7 */6 * * *` with a runbook.

**`.claude/dispatch/commands.yaml` does not exist**, so a run reports 1344 × `no_command` and executes zero.

That is the design. An unbound issue is one nobody has authorized to run unattended, and the binding file is where that authorization lands — the same place the plan-approval gate already sits. The rejected alternative was a template firing "work this issue" at 1344 issues that never passed that gate.

**To start real throughput: bind two or three issues.** Prefer work whose shape is already proven over a bulk fill.

Ceilings that remain: `per_provider` caps and `budget_pools.*.max_concurrent` bind nowhere at claim time; `.claude/dispatch/PAUSE` is checked only on an **armed** drain, so a dry run's exit 0 must not be read as "PAUSE is broken" (runbook says so, with the line reference).

---

## 4. The one lesson worth carrying

**A check that is correct, passing, and measuring nothing is this repo's most common defect.** Nine distinct instances in this session — now written up as [`.claude/rules/guards-must-discriminate.md`](../../.claude/rules/guards-must-discriminate.md) (in #3777) with all nine tabulated.

Six of the nine were written *by people who had just read about the other three*. That rules out carelessness: the failure mode is invisible from inside the code, because the code is usually correct. Only mutation finds it — break the thing, confirm a **named** test goes red.

Three that cost real time:

- `check_r5` reported `PASS: 4KB / 16KB` while the real per-session load was ~24 KB. The largest file was never a candidate.
- The Client-PII Gate is `on: pull_request`, and every automated writer pushes straight to `main`. **A push trigger alone would not have fixed it** — GitHub raises no `push` event for the default `GITHUB_TOKEN`, which *is* the anti-loop split, so `on: push` is permanently blind to the exact writer #3775 names. It needed `push` **+** `schedule`.
- `check-client-pii.py <directory>` scanned nothing and exited 0. My first local run said 2 files flagged; the same run with an explicit file list said 15.

---

## 5. Operational facts that cost time

- **The local checkout drifts faster than the work.** It diverged twice today (session start: 4 ahead / 7 behind; again at 03:30 via `return-to-main-guard`). The second time it had reverted to a **pre-#3771 state with the 22 private-repo boards back on disk** — and `auto-sync` does `git add -u` + push from this checkout. Left alone it would have re-published family and estate material automatically. Nothing was published; caught in the diff. **Check `git rev-list --count` both ways before trusting anything local.**
- **The private client map is available locally** at `config/agents/.client-codename-map.local.yaml` (gitignored) and is `check-client-pii.py`'s `DEFAULT_MAP`. I spent hours treating it as a CI-only secret. You can run the real gate.
- **`legal-sanity-scan.sh` is not the gate.** It passes on files the gate rejects. Use `check-client-pii.py`.
- **`[remote rejected]` is usually auto-sync winning the race, not a failure.** Happened three times; every time the content had already landed. Verify with `git cat-file` / `ls-remote`, never the exit code.
- **`deckhand` is PRIVATE.** I asserted otherwise twice.
- **A cron stages files into your index.** 36 entries blocked a cherry-pick; path-scoped `git reset --` clears it without touching the working tree.
- **`git checkout --` is unsafe against uncommitted regeneration** — it reverts to HEAD, not to what you just wrote. A subagent caught me handing it that instruction and used a hash-verified backup instead.

---

## 6. Issues filed today

| | |
|---|---|
| [#3762](https://github.com/vamseeachanta/workspace-hub/issues/3762) | both harness context guards are name-based and miss the 20 KB file that auto-loads |
| [#3764](https://github.com/vamseeachanta/workspace-hub/issues/3764) | a refused claim still publishes — **fixed**, #3774 |
| [#3768](https://github.com/vamseeachanta/workspace-hub/issues/3768) | ~9,000 raw titles + 1,531 body excerpts across 9 writers — **7 fixed**, #3777 |
| [#3770](https://github.com/vamseeachanta/workspace-hub/issues/3770) | PUBLIC repo mirrored 595 cards from PRIVATE repos — **recurrence stopped**, #3771 |
| [#3772](https://github.com/vamseeachanta/workspace-hub/issues/3772) | lease namespaces diverged — **fixed**, #3774 |
| [#3773](https://github.com/vamseeachanta/workspace-hub/issues/3773) | six rails for unattended running — **all six shipped**, #3774/#3776 |
| [#3775](https://github.com/vamseeachanta/workspace-hub/issues/3775) | the gate cannot see bot pushes — **fixed**, #3777 |

---

## 7. Owner-only work, not closable by an agent

1. **`LEGAL_CLIENT_MAP` repo secret** — blocks #3777 (§1).
2. **History rewrite for #3770.** ~9,000 identifiers and 595 private-repo cards remain in **public git history** across 297 commits, live since 2026-05-22. Everything merged today stops new leakage and removes nothing already published. Needs a force-push.
3. **#3755** — the identifiers originate in workspace-hub's own public issue titles. Everything today redacts *mirrors*; the source is untouched.
4. **#3766 approval gate** — never self-applied.

---

## 8. External actions taken

Created issues #3762, #3764, #3768, #3770, #3772, #3773, #3775. Opened PRs #3765, #3766, #3767, #3769, #3771, #3774, #3776, #3777; merged #3767, #3769, #3771, #3774, #3776 under explicit per-PR authorization; closed #3761 and #3765 on instruction. Commented on deckhand#33 with reproduction findings. Created 4 `dispatch:` labels in `digitalmodel` and `deckhand`. Ran one real drain against deckhand#33 (diagnostic only, `state=done returncode=0`).

**No force-push. No history rewrite. No `LEGAL_PII_ALLOW` bypass. Nothing merged from a non-CLEAN state.**

---

## 9. Residue

- **Preserved deliberately:** `backup/pre-reset-2026-08-02` and `backup/pre-reset-2026-08-02b` tags (the two checkout reconciliations); branch `docs/2026-08-02-dispatch-epic-handoff` kept after closing #3761 so its text stays reachable.
- **Pre-existing, not mine:** 13 worktrees, ~60 branches, 2 stashes from prior sessions. One stash from today (`guard-auto-stash-20260802T033022`) created by `return-to-main-guard`, not by me.
- **Expected churn:** ~248 cron-regenerated files dirty in the working tree (provider artifacts, `.claude/state`, memory runtimes). Two of them currently carry client identifiers — that is §1, not residue to clean.
- **Known-failing, pre-existing:** 7 tests in `tests/legal/test_legal_scan_resolution.py` / `test_repo_resolution.py`. Confirmed identical on a clean `origin/main` worktree; they exercise `legal-sanity-scan.sh` and predate this session.
