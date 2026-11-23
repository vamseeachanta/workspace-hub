# Lane C1 — ace-linux-1 control-plane reconciler — overnight result

Lane: C1 / ace1-control-feed-20260428.
Generated: 2026-04-28 ~22:00 CDT (start 21:49). Stop target: 2026-04-29 09:49 CDT.
Worker: Claude Opus 4.7 (1M ctx) on ace-linux-1, orchestration / read-mostly mode.

## Companion deliverables (this lane)

- `results/github-command-pack.md` — exact `gh` mutation drafts, none executed.
- `results/next-dispatch-queue.md` — drop-in next prompts per lane (C2, C3, D1, D2, D3).
- `results/ace1-control-reconciler.md` — this file.

## Execution boundaries observed

- No code edits. No PR opens, comments, label changes, closures, or merges.
- Sandbox blocked `tmux ls` and `ssh ace-linux-2 ...` from this lane in unattended mode; live process probing was deferred to file-evidence and `gh` introspection.
- All `gh` calls were read-only (`view`, `list`, `api .../refs/heads`).
- Priority seed list from prompt was fully enumerated; live state captured for all 20.

## Bucketed queue (priority-ranked)

### Bucket 1 — VERIFY_CLOSE (work pushed; needs PR / merge / comment evidence)

| Issue | Where | Latest evidence | Next action | Risk |
|---|---|---|---|---|
| #2519 | umbrella | spinoffs #2523/#2524/#2525 created; pack commit `3e136a524` in main | Comment status; keep open until spinoffs ship | low |
| #2462 | digitalmodel branch `codex/burn-20260427-issue-2462` head `4ad99a36af` | branch pushed, no PR | Open DRAFT PR | low |
| #2458 | digitalmodel two scoped refs pushed | branches present per 2026-04-27T18:55 comment | Confirm branch names then open DRAFT PR | low |
| #2433 | worldenergydata PR #356 head `397686ed68` | PR open, original blocker addressed | Re-check status, comment readiness | low |
| #2459 | assethold PR #47 head `b922e2533b` | PR open, focused tests pass | Re-check status, comment readiness | low |
| #2346 | branch `codex/10thread-20260428-issue-2346` commit `44735e979a` | demo_03 inputs added | Open DRAFT PR if branch was pushed; otherwise queue push | low |
| #2269 | branch `codex/10thread-20260428-issue-2269` commit `464efb8cc3` | OpenFOAM validator contract | Open DRAFT PR if pushed; otherwise queue push | low |

### Bucket 2 — BLOCKED_RESOURCE (gate must be collapsed before any implementation)

| Issue | Blocker | Collapse path |
|---|---|---|
| #2402 | Approval-revision drift on `.planning/plan-approved/2402.md` | User refreshes marker SHA OR confirms plan SHA in comment |
| #2364 | Approved-plan artifact mismatch | Same pattern — refresh marker; check sister batch packs |
| #2272 | Codex env mismatch in sparse-fallback worktree | Re-dispatch on fresh non-sparse worktree |
| #2289 | Pre-push hook blocks Codex commit `681da033` | Diagnose hook in fresh worktree; never `--no-verify` |
| #2515 | ace-linux-2 lane B1 sandbox blocked writes (env mismatch) | Re-dispatch on ace-linux-1 fresh worktree (plan already approved) |

### Bucket 3 — NEEDS_REVIEW (status:plan-review, awaiting adversarial review)

| Issue | State | Next |
|---|---|---|
| #2510 | Plan stuck since r13 (2026-04-27 10:36) | Lane C3 produces r14 plan-edit pack; surface consensus-vs-minority decision per memory |
| #2490 | Plan draft pushed `f14872956b` 2026-04-27 17:07; no cross-review yet | Lane C3 runs r1 adversarial review |

### Bucket 4 — NEEDS_PLAN (priority seed, no plan, no comments)

All four are direct children of the orchestration epic #2519 plus one machine-readiness sibling.

| Issue | Title | Priority | Plan owner |
|---|---|---|---|
| #2525 | Codex expiring-credit burn-down controller | high | Lane C3 next slice |
| #2548 | Control-plane machine inventory + OrcaFlex/AQWA dispatch | high | Lane C3 next slice |
| #2524 | Machine-aware dispatch ledger and reconciler | high | Lane C3 next slice |
| #2523 | Hermes preflight readiness checker | high | Lane C3 next slice |

### Bucket 5 — GTM_PACKAGING (engineering evidence ready for client-ready material)

| Issue | Evidence boundary | C2 angle |
|---|---|---|
| #2346 | `scripts/gtm/prospect_adapter.py` diff at `44735e979a` | "48hr customized prospect demo" — claim limited to demo_03 inputs |
| #2515 | Approved deterministic-output schema (impl in flight) | "Cross-section deliverable schema locked; impl in flight" |
| #2462 / #2458 | digitalmodel branches pushed | "Operator-map / multi-body fixture coverage" — boundary "branches pushed, PR pending" |
| #2510 | DO NOT package (plan still under review) | hold |

### Bucket 6 — READY_TO_IMPLEMENT (plan-approved AND not blocked AND not in-flight)

After applying the in-flight filter, the plan-approved set narrows to issues where no Codex/Claude lane left a "starting work" comment in the last 24h. Candidates worth a fresh ace-linux-1 implementation lane:

- **#2229** Windows parity NightlyReadiness — no recent code activity; needs licensed-win-1 access (overlaps #2548 inventory).
- **#2152** Golden fixture corpus for weekly review — no recent code activity; safe ace1 implementation if test surface is well-bounded.
- **#2129** Issue-state drift audit — no recent code activity; orchestration-side, low risk.
- **#2105** Knowledge freshness cadences — last action 2026-04-28 08:07 (planning); ready to implement.
- **#2070** Guard Claude state-sync against oversized session-signal files — no recent code activity; low-risk harness work.

These should NOT auto-launch tonight. Reconciler recommends queueing them for the next planned wave (after morning user review).

## Lane status (best evidence I could gather without remote/tmux probes)

| Lane | Session | Status | Evidence | Recommended next |
|---|---|---|---|---|
| C1 | ace1-control-feed-20260428 | RUNNING — produced 3 deliverables | this directory | continue monitor + 1 mid-cycle refresh at 04:00 CDT |
| C2 | ace1-gtm-feed-20260428 | RUNNING_BUT_RESULTS_PENDING | `results/ace1-gtm-packager.md` empty | feed prompt from `next-dispatch-queue.md` |
| C3 | ace1-plan-hardener-20260428 | RUNNING_BUT_RESULTS_PENDING | `results/ace1-plan-review-hardener.md` empty | feed prompt from `next-dispatch-queue.md` |
| D1 | ace2-digitalmodel-feed-20260428 | LIKELY_BLOCKED | B1 last comment 2026-04-29T02:28Z env-blocked | redirect to env diagnosis (see queue file) |
| D2 | ace2-knowledge-feed-20260428 | RUNNING_BUT_RESULTS_PENDING | results pending | feed marker-inventory prompt |
| D3 | ace2-review-feed-20260428 | RUNNING_BUT_RESULTS_PENDING | results pending | feed false-completion sweep prompt |

> Operator should run `tmux ls; ssh ace-linux-2 tmux ls` at next morning check to confirm session liveness; sandbox blocked those probes from this lane.

## Recent main-branch activity (last 24h, signal only)

- 7 commits on the orchestration/planning surface alone (`fix(orchestration): use quoted runner...`, `chore(orchestration): add 12h continuation lane pack`, ...).
- 1 plan-approval commit: `b711f3b46b` — `docs(plans): mark issue 2515 plan approved`.
- 4 auto-sync commits — Hermes was active. Reconciler did not trigger any code commits to avoid a Hermes-revert race per memory `feedback_hermes_active_preflight_check`.
- New continuation pack at `2026-04-28-12h-continuation/` already committed (`fb985cfe1`).

No false-completion claims spotted in commit titles.

## Morning action table (operator hand-off)

Order: read top-down. Each row is a single, gated action.

| # | Issue | State now | Next action | Provider/machine | Approval needed | Evidence path |
|---|---|---|---|---|---|---|
| 1 | #2515 | plan-approved; ace2 lane env-blocked | Reissue on ace-linux-1 fresh worktree under `/mnt/local-analysis/night-runs/ace1-2515/` | Claude / ace1 | none (already plan-approved) | `b711f3b46b`; B1 blocker comment |
| 2 | #2462 | plan-approved; branch pushed; no PR | Open DRAFT PR per command-pack §A1 | gh / ace1 | review PR before posting | digitalmodel branch `codex/burn-20260427-issue-2462` |
| 3 | #2458 | plan-approved; branches pushed; no PR | Confirm branch names; open DRAFT PR per §A2 | gh / ace1 | review PR before posting | digitalmodel branches per 2026-04-27T18:55 comment |
| 4 | #2433 | plan-approved; PR #356 open | Re-check PR; comment readiness per §A3 | gh / ace1 | yes — review comment | worldenergydata#356 head `397686ed68` |
| 5 | #2459 | plan-approved; PR #47 open | Re-check PR; comment readiness per §A4 | gh / ace1 | yes — review comment | assethold#47 head `b922e2533b` |
| 6 | #2289 | plan-approved; pre-push hook blocked | Diagnose hook in fresh worktree per §B4 | Claude / ace1 | none for diagnosis | local commit `681da0334a` |
| 7 | #2402 | plan-approved; approval-revision drift | Refresh marker SHA per §B1 | user | yes — marker write | `.planning/plan-approved/2402.md` |
| 8 | #2364 | plan-approved; artifact mismatch | Refresh marker per §B2 | user | yes — marker write | comment 2026-04-28T09:17 |
| 9 | #2510 | plan-review (r13 stuck) | C3 r14 plan-edit pack per `next-dispatch-queue.md` | Claude / ace1 | none for draft | plan path docs/plans/2026-04-26-issue-2510-... |
| 10 | #2490 | plan-review (no review yet) | C3 r1 adversarial pass | Claude / ace1 | none for draft | plan `f14872956b` |
| 11 | #2548 | OPEN no plan, priority:high | C3 plan skeleton draft | Claude / ace1 | none for draft | issue body |
| 12 | #2525 | OPEN no plan, priority:high | C3 plan skeleton draft (Codex burn-down) | Claude / ace1 | none for draft | issue body |
| 13 | #2524 | OPEN no plan, priority:high | C3 plan skeleton draft | Claude / ace1 | none for draft | issue body |
| 14 | #2523 | OPEN no plan, priority:high | C3 plan skeleton draft | Claude / ace1 | none for draft | issue body |
| 15 | #2272 | plan-approved; env-blocked | Re-dispatch on non-sparse worktree | Claude / ace1 | none | comment 2026-04-28T06:08 |
| 16 | #2519 | priority:critical, epic | Comment status per §A7; keep open | gh / ace1 | yes — review comment | spinoffs #2523/#2524/#2525, commit `3e136a524` |
| 17 | #2346 | plan-approved; commit `44735e979a` | If branch pushed, draft PR per §A6 | gh / ace1 | yes — review PR | branch `codex/10thread-20260428-issue-2346` |
| 18 | #2269 | plan-approved; commit `464efb8cc3` | If branch pushed, draft PR per §A5 | gh / ace1 | yes — review PR | branch `codex/10thread-20260428-issue-2269` |
| 19 | #2373 | plan-approved | Likely shares Batch-Pack approval drift; group with §B2 | user | yes — marker | sibling of #2364 |
| 20 | #2368 / #2369 | plan-approved | Same — bundle with §B2 batch-marker rebind | user | yes — marker | sibling of #2364 |

## Anti-patterns avoided this lane

Pulled directly from MEMORY.md to keep this concrete:

- **`feedback_never_offer_to_self_label_plan_approved`** — no marker writes; no `gh issue edit --add-label` proposals applied.
- **`feedback_check_parallel_work`** — checked recent commits, lane prompts, and ledger before composing next-wave prompts.
- **`feedback_codex_sustained_major_loop`** — surfaced #2510 r13 as consensus-vs-minority decision rather than auto-cycle.
- **`feedback_hermes_active_preflight_check`** — did not commit code from this lane while Hermes auto-sync activity is visible in last 30 min.
- **`feedback_isolated_clone_dispatch_race`** — drafted blocker-collapse for #2515 instead of opening a parallel write path.
- **`feedback_codex_cli_0_124_upstream_regression`** — no Codex `exec` dispatch this lane (and noted version guard for next wave).
- **`feedback_inline_gh_issue_url`** — issue numbers rendered as `#NNNN`; full URLs only where evidence is referenced (e.g., `vamseeachanta/digitalmodel#…`).

## Open items for the next reconciler pass (mid-cycle, ~04:00 CDT)

1. Re-poll `gh issue view 2515 --comments` for an ace-linux-1 fresh-worktree retry signal.
2. Re-check `gh pr view 356 --repo vamseeachanta/worldenergydata` and `gh pr view 47 --repo vamseeachanta/assethold` status; if green, escalate the comment-readiness drafts in §A3/§A4.
3. Verify operator did not silently advance any approval marker; if any moved without a corresponding push of the bound plan SHA, flag as drift.
4. Confirm whether C3 actually wrote the four NEEDS_PLAN skeletons; if not, queue them again with shorter time slices.
5. Confirm whether D1 produced an env diagnostic for the #2515 ace2 sandbox failure; if not, escalate to manual inspection in morning.

## Reconciler self-audit

- Issues touched: 20 priority seeds + cross-references to ~10 sibling/dependency issues.
- gh API mutations: 0.
- Code edits: 0.
- Files written: 3 (this file + `github-command-pack.md` + `next-dispatch-queue.md`), all under the lane-allowed paths.
- Read-only commands used: `gh issue list`, `gh issue view --json`, `gh issue view --comments --jq`, `gh api .../refs/heads`, `git log --since`, `Read`, `Glob`.
- Approval-gate violations: 0.
- Hermes-conflict commits: 0.
