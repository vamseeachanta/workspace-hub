# Plan for #2557: Weekly work-pattern review and flow hacks

> **Status:** draft (post-nextwave-followup-patch 2026-04-29 ~13:56 CT — plan-level F1/F2/F3/F4/F5/F6 addressed; ready for re-review only after companion report regeneration runs and a fresh multi-provider fanout lands. **Not** ready for `status:plan-review` and **not** approved.)
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2557
> **Review artifacts:** `scripts/review/results/2026-04-29-plan-2557-nextwave-claude.md` (MAJOR, single-author Claude self-review — pre-patch r1) | `...-codex.md` (UNAVAILABLE, #2479 + permission gate) | `...-gemini.md` (UNAVAILABLE, permission gate). Patch result note: `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2557-20260429-1356.md`

---

## Resource Intelligence Summary

Five distinct sources consulted (issue body counts as 1). Each finding cites a specific path and a concrete observation.

### Existing repo code / artifacts
- Found: `docs/BUSINESS_BRAIN.md` lines 80-99 — `Autonomous Hard-Gate Evolution` already names the productivity goal (owner on origination/GTM, agents self-cycle); lines 65-74 confirm Claude Max + Gemini + Codex provider posture and that "harness throughput is the bottleneck, not credits".
- Found: `docs/reports/provider-utilization-weekly.md` (regenerated 2026-04-29T17:20:31Z; this plan pins to that generation header — every cron run overwrites the snapshot) — current week W18 utilization is **claude 7.6%, codex 0.4%, gemini 0.1%**; W17 was 31.4% / 0.4% / 3.0%; alerts section flags all three as underutilized.
- Found: `docs/reports/provider-routing-scorecard.md` (regenerated 2026-04-29T17:20:36Z) — scorecard explicitly says: "Reserve Claude for adversarial review… do not burn Claude on mechanical loops that Codex can absorb"; Codex status `underused` priority `highest`; Gemini status `underused` priority `highest`.
- Found: `docs/reports/provider-work-queue.md` (regenerated 2026-04-29T17:20:44Z) — **6 Claude** `status:plan-approved` issues ready out of 159 routed (top: #2540, #2490, #2510, #2515, #2541, #2544); **18 Codex** `status:plan-approved` issues ready out of 39 routed (top 8: #2269, #2289, #2346, #2364, #2368, #2369, #2373, #2402); Gemini lane has 2 candidates with 0 ready (#2295, #2501).
- Found: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/lane-monitor-latest.md` — all 6 named lanes (C1/C2/C3/D1/D2/D3) plus 21 follow-up feeds completed with results, **zero GitHub mutations performed**. Operator-only command packs left at `github-command-pack.md`, `plan-review-command-pack.md`, `next-dispatch-queue.md`.
- Found: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/` — `#2374` plan was revised in feeds 16, 17, 18, 19, 20, 21 (six revisions in 12 hours, never exited plan-review).

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable — this is a workflow/productivity audit, not an engineering calc. | n/a | — |

### LLM Wiki pages consulted
- Not applicable — this is an internal-process audit; no public-facing wiki promotion is in scope.

### Documents consulted
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` v3.1.0 — defines the mandatory workflow this plan must respect; lines 100-188 catalogue label/marker/README drift handling, evidence the workflow already pays a high coordination tax that hacks #6 (drift reconciler) and #11 (confidence-threshold gates) are designed to reduce.
- `.claude/memory/topics/feedback_codex_cli_0_124_upstream_regression.md` — codex-cli 0.124.0 installed 2026-04-23 hangs on stdin; #2479 filed. Workaround = downgrade to 0.123.0 **only** restores Codex for plain-terminal (operator-driven) invocations. Per memory verification 2026-04-24, the downgrade also hangs from inside Claude Code's Bash tool — so agent-session lanes (Hermes-dispatched, Claude-Code-Bash-spawned) remain upstream-blocked until #2479 closes. Direct contributor to W18 codex 0.4%; any hack proposing the 0.123.0 pin must scope its owner-time-impact estimate to terminal-only invocations and explicitly exclude agent-session recovery.
- `.claude/memory/topics/feedback_codex_sustained_major_loop.md` — when Codex returns MAJOR for 3+ consecutive rounds while other providers MINOR/APPROVE, surface as consensus-vs-minority decision instead of auto-cycling. Explains the #2374 feed16-21 pattern.
- `.claude/memory/topics/feedback_hermes_active_preflight_check.md` — Hermes cleanup loops can revert parallel commits within minutes; preflight `pgrep` required.
- `.claude/memory/topics/feedback_gemini_sandbox_overlay_blindness.md` — Gemini cross-review false-positive MAJOR rate due to sparse-checkout overlay invisibility; ~54 false claims in one batch.
- Related issue `#2254` (provider-telemetry: improve Claude and Gemini quota observability) — already filed; today blocks accurate routing.
- Related issue `#2519` (feat(hermes): orchestrate AI provider usage and workstation dispatch), `#2523` (Hermes preflight readiness checker), `#2524` (machine-aware dispatch ledger), `#2525` (Codex burn-down controller) — overlapping orchestration work; this plan must coordinate, not duplicate.

### Gaps identified
- No regular **owner-time accounting** — there is no artifact answering "how many minutes/week is the owner spending on orchestration vs origination".
- No **command-pack execution layer** — overnight feeds produce safe-to-execute (comment-only) command packs, but execution is fully manual.
- No **plan-review stop-rule** — sustained-MAJOR loops auto-cycle without surfacing the consensus-vs-minority decision.
- No **plan-confidence telemetry** — Business Brain's "confidence-threshold gates" goal has no measurement substrate yet.
- No **GTM artifact pipeline** — the week's target (capability charts, contractor brochure send) has no executable definition; overnight prompts for #2554/#2555/#2556 staged but never ran.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29 via `gh issue view`):
- `#2557` — OPEN — chore(productivity): weekly work-pattern review and flow hacks
- `#2479` — codex-cli 0.124.0 stdin hang (referenced — separate issue)
- `#2254`, `#2519`, `#2523`, `#2524`, `#2525` — referenced as related orchestration work

**File existence** (`ls -la` 2026-04-29):
- EXISTS: `docs/BUSINESS_BRAIN.md`
- EXISTS: `docs/reports/provider-utilization-weekly.md` (regenerated 2026-04-29T17:20:31Z — header literal: `Generated: 2026-04-29T17:20:31.354384Z`)
- EXISTS: `docs/reports/provider-routing-scorecard.md` (regenerated 2026-04-29T17:20:36Z — header literal: `Generated: 2026-04-29T17:20:36.733667Z`)
- EXISTS: `docs/reports/provider-work-queue.md` (regenerated 2026-04-29T17:20:44Z — header literal: `Generated: 2026-04-29T17:20:44.772375Z`)
- EXISTS: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/lane-monitor-latest.md`
- MISSING (this plan creates): `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md`, `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md`, `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2557-summary.md`

**Line excerpts**

`docs/reports/provider-utilization-weekly.md` (W18 alerts block):
```
- claude at 7.6% (activity_vs_recent_peak)
- codex at 0.4% (quota)
- gemini at 0.1% (activity_vs_recent_peak)
```

`docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/lane-monitor-latest.md` (guardrails section):
```
- No launches after stop target.
- No merges, closes, force-pushes, hard resets, label removals,
  issue comments, PR actions, or other GitHub mutations.
- No implementation launched.
- No approval markers created.
```

**Gap proofs:**
- `ls docs/reports/owner-time-accounting* 2>&1 | head -3` → "No such file or directory" → confirms owner-time accounting artifact does not exist.
- `ls scripts/govern/exec-safe-command-pack* 2>&1 | head -3` → "No such file or directory" → confirms safe-command-pack auto-executor does not exist.

<!-- Distinct sources: 6 (issue body, BUSINESS_BRAIN.md, three provider reports, lane-monitor + 12h continuation, issue-planning-mode skill, four feedback memories, related-issue ledger). Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` |
| First-pass report | `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md` |
| Overnight summary | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2557-summary.md` |
| Plan index update | `docs/plans/README.md` (add row) |
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2557-claude.md` (pending) |
| Plan review — Codex | `scripts/review/results/2026-04-29-plan-2557-codex.md` (pending; #2479 risk) |
| Plan review — Gemini | `scripts/review/results/2026-04-29-plan-2557-gemini.md` (pending) |

Implementation of any individual hack will spawn its own bounded issue + plan; this plan does **not** implement workflow changes.

---

## Deliverable

A repo-tracked weekly productivity review at `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md` containing 10-15 evidence-anchored productivity hacks ranked by owner-time reduction and implementation effort, each with a concrete first action and a follow-up issue candidate (filed only when strongly justified). The report distinguishes GTM throughput, engineering throughput, agent orchestration, and context/handoff hygiene per acceptance criteria, and packages ≥3 hacks for execution without further owner input.

---

## Pseudocode

```
audit_phase:
    sources = [
        issue_2557_body,
        business_brain,
        provider_utilization_weekly,
        provider_routing_scorecard,
        provider_work_queue,
        lane_monitor_latest_2026_04_28,
        twenty_one_overnight_feed_artifacts,
        feedback_memories[codex_cli_regression,
                          codex_sustained_major_loop,
                          hermes_active_preflight,
                          gemini_overlay_blindness]
    ]
    friction = extract_distinct_friction_points(sources)
    # 4 dimensions per acceptance criteria:
    bucket_by_dimension(friction, [gtm_throughput,
                                   engineering_throughput,
                                   agent_orchestration,
                                   context_handoff_hygiene])

rank_phase:
    for hack in proposed_hacks:
        owner_time_saved = estimate_minutes_per_week(hack)
        effort = classify(hack, [immediate, this_week, structural])
        first_action = specific_repo_path_or_command(hack)
        follow_up_issue = recommend_only_if(non_duplicate_and_high_confidence)
    sort by (owner_time_saved desc, effort asc)

output_phase:
    write report with 4-dimension grouping + top-3 immediate
    write canonical plan (this file)
    write overnight summary
    update docs/plans/README.md index row
    post progress comment on #2557
    do NOT mutate to status:plan-approved
    do NOT promote to status:plan-review (no review artifacts yet)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` | This canonical plan |
| Create | `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md` | First-pass report with ranked hacks |
| Create | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2557-summary.md` | Overnight-prompt-style status summary |
| Update | `docs/plans/README.md` | Add `2557` row to plan index |

No source code changes in this plan. Implementation work is deferred to bounded follow-up issues per the report.

---

## Verifiable Evidence Checks

This is an analysis deliverable; instead of a TDD test list, the plan commits to falsifiable evidence checks (per #2208 retrieval contract).

| Check | What it verifies | Evidence path |
|---|---|---|
| EC-1 | Each hack cites at least one specific file path or issue number | grep `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md` for `\.md\|#[0-9]\{3,4\}` per hack section |
| EC-2 | Each hack carries an Owner-time impact field that is **either** a numeric/bounded estimate (e.g. "~20-30 min/wk") **or** an explicit `Indirect (precondition: <named precondition>)` label that names the dependency unblocking measurable savings. Plain "Indirect" without a precondition fails the check. | grep "Owner-time impact:" rows in report; verify each "Indirect" row matches the regex `Indirect \(precondition: .+\)` |
| EC-3 | Each hack has a first-action that names a concrete file, command, or issue | grep "First action:" rows in report |
| EC-4 | At least 3 immediately actionable hacks are flagged for execution-without-owner-input | "Immediate" section count ≥ 3 |
| EC-5 | All 4 dimensions covered: GTM throughput / engineering throughput / agent orchestration / context-and-handoff hygiene | report dimension matrix non-empty per dimension |
| EC-6 | Follow-up issue candidates are flagged but **not auto-filed** in this session | report's "Follow-up issue candidates" table marks all `state: candidate (not filed)` |

---

## Acceptance Criteria

- [ ] `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md` exists and contains 10-15 hacks
- [ ] Each hack names: dimension, evidence path, owner-time impact, effort tier, first action, follow-up issue candidate
- [ ] At least 3 hacks marked `Immediate` with first-action runnable without further owner input
- [ ] All 4 acceptance dimensions populated
- [ ] `docs/plans/README.md` carries a `2557` row
- [ ] `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2557-summary.md` exists with status, blockers, next action
- [ ] Plan status remains `draft` (no `status:plan-review` label flip without real adversarial-review artifacts)
- [ ] No `status:plan-approved` mutation
- [ ] No new follow-up issues filed during this drafting session unless explicitly authorized

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (single-author r1, 2026-04-29 nextwave) | MAJOR | (1) Report TL;DR cites `claude 6.6%` for W18; live `provider-utilization-weekly.md` shows `claude 5.8%` — the 6.6% figure does not exist in current source. (2) Generation-timestamp cited as `2026-04-29T13:20Z`, actual is `2026-04-29T09:20:08Z`. (3) Codex work-queue cited as "8 ready / 17 routed" — live source shows `18 ready / 41 routed`. (4) Claude work-queue cited as 3 ready (`#2490, #2510, #2515`); live source shows 1 ready (`#2515`). (5) H1 "Pin codex-cli to 0.123.0" Tier-1 framing misleading — per `feedback_codex_cli_0_124_upstream_regression.md` (verified 2026-04-24), 0.123.0 also hangs from inside Claude Code's Bash tool, so the pin only restores Codex for plain-terminal invocations, not Hermes-dispatched lanes; recovery estimate must be re-derived against the actual surface. (6) EC-2 internally inconsistent — three hacks (H7, H11, H12) explicitly mark "Indirect / Zero immediate" but EC-2 demands "numeric or bounded" estimates; report's Validation log claims EC-2 satisfied. (7) H10's 4-deliverable GTM split overlaps with sibling brochure outline (#2556 §3.3, §4) without naming the overlap. (8) Plan/report references `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/` while live overnight-prompts root for this batch is `2026-04-29-next-wave-autofeed/` — declare canonical summary location to avoid future split-brain. |
| Codex | UNAVAILABLE | Bash permission gate in this planning-only autofeed session blocked `scripts/review/plan-review-fanout.sh` dispatch (`feedback_permission_gate_blocks_cross_review.md`); even if dispatched, codex-cli 0.124.0 hangs on stdin per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) and downgrade does not help from inside Claude Code's Bash tool. Operator should run from un-sandboxed terminal after `npm install -g @openai/codex@0.123.0`. |
| Gemini | UNAVAILABLE | Same Bash permission-gate; Gemini wrapper itself is healthy after the 2026-04-24 `GEMINI_CLI_TRUST_WORKSPACE` fix. Run from un-sandboxed terminal; validate any "file missing" claim against `git ls-files` per `feedback_gemini_sandbox_overlay_blindness.md`. |

**Overall result:** SINGLE-AUTHOR MAJOR — multi-provider consensus is not yet established. Plan must remain at `status: draft` until at least one additional provider lands a structured artifact. Three Claude findings (#1 stale W18 number, #3 stale Codex queue counts, #5 H1 misleading owner-time estimate) were blocking at r1; the **plan-level fixes are now applied** in this revision pass (2026-04-29 nextwave-followup-patch). The companion **report file regeneration remains operator-gated** — see Risks section.

Per `docs/BUSINESS_BRAIN.md` lines 89–97, promoting to `status:plan-approved` requires *"repeated APPROVE/MINOR adversarial-review outcomes across Claude/Codex/Gemini"* — current artifacts do not satisfy that criterion.

Revisions made based on review (2026-04-29 nextwave-followup-patch lane, planning-only):
- F1 (stale W18 number): Plan §Resource Intelligence Summary now cites `claude 7.6%` against the `2026-04-29T17:20:31Z` regeneration of `provider-utilization-weekly.md`, with explicit pin to that generation header. Report TL;DR remains stale until report regeneration runs.
- F2 (stale generation timestamp): Plan §Evidence (file existence) timestamps refreshed from `13:20Z` placeholder to the actual generation headers (`17:20:31Z`, `17:20:36Z`, `17:20:44Z`); literal header strings included so a future reviewer can verify line-for-line.
- F3 (stale Codex work-queue counts): Plan §Resource Intelligence Summary now cites `18 ready / 39 routed` (was `8 ready / 17 routed`); top-8 example list retained because the same eight issues remain in the current ready set.
- F4 (stale Claude work-queue counts): Plan §Resource Intelligence Summary now cites `6 ready / 159 routed` (was `3 ready / 157 routed`) with current top: #2540, #2490, #2510, #2515, #2541, #2544.
- F5 (H1 framing scope-limit): Plan §Resource Intelligence Summary feedback-memory bullet now explicitly records that the 0.123.0 downgrade only restores Codex for plain-terminal invocations, not agent-session lanes; any hack proposing the pin must scope its owner-time estimate accordingly. Report-side H1 hack text **not yet rewritten** — operator regeneration required.
- F6 (EC-2 internally inconsistent): Plan §Verifiable Evidence Checks EC-2 now accepts either a numeric/bounded estimate **or** an explicit `Indirect (precondition: <named>)` label, matching how the report's H7/H11/H12 currently classify their owner-time impact. Plain `Indirect` without a precondition still fails.
- F7 (H10 GTM-split overlap with #2554/#2555/#2556): **Deferred** — content lives in the report file (out of scope for this patch lane). Captured in Risks/Open Questions for the report regeneration pass.
- F8 (overnight-prompts canonical location): **Deferred** — same reason. Open question retained.

**Provider-coverage honesty:** Codex and Gemini remain UNAVAILABLE on this artifact wave; the patch did not run any new cross-review. The Codex/Gemini stub artifacts (`scripts/review/results/2026-04-29-plan-2557-nextwave-{codex,gemini}.md`) are the latest provider-side input and explicitly mark the absence. Promotion past `status:draft` is not justified by this patch alone — operator must run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` from an un-sandboxed terminal (after `npm install -g @openai/codex@0.123.0`) to land real Codex + Gemini artifacts before any `status:plan-review` flip.

---

## Risks and Open Questions

- **Risk (residual after 2026-04-29 patch):** The companion report `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md` was **not** regenerated by this patch lane (planning-only scope). Until operator regenerates the report against the `2026-04-29T17:20:31Z` provider-data snapshot the plan now pins to, the report's TL;DR / friction map / H1 owner-time estimate / H10 GTM-split content remain stale. Re-cross-review must wait for that regeneration (or accept that another regeneration cycle will land before re-review and the plan numbers will need a second refresh).
- **Risk:** Codex review unavailable due to #2479 — fall back to Claude + Gemini and explicitly note in review summary; do not pretend two-provider coverage existed.
- **Risk:** Several hacks overlap with existing in-flight issues (#2254, #2519, #2523, #2524, #2525) — the report must cross-reference rather than duplicate; "follow-up issue candidate" means *only if no duplicate exists*. Specifically (per Claude r1 finding 7), report H10's 4-deliverable GTM split must declare which deliverables are already absorbed by `#2556` brochure outline §3.3 (chart slot) and §4 (outbound copy variants) before claiming H10 net-new scope.
- **Risk:** Owner-time savings are estimates, not measurements — an "owner-time accounting" instrument (hack #?) is needed before claims can be validated; the report flags this explicitly.
- **Risk:** Some hacks (auto-execute command packs, confidence-threshold gates) sit on the autonomous-hard-gate-evolution boundary; any implementation must respect Business Brain's "establish threshold metrics over time, then relax specific user approvals" principle.
- **Risk:** Provider-data snapshot drift — `provider-utilization-weekly.md` and siblings are regenerated by the daily-readiness cron (next run after 2026-04-29T17:20Z is 2026-04-30 ~06:00 CT). Every regeneration overwrites the snapshot this plan pins to. Mitigation: the plan now records the literal `Generated:` header of each source so a reviewer can verify whether they're reading the same generation. If a regeneration lands before promotion, treat the plan numbers as a snapshot pin, not as live state.
- **Open:** Should the report file 1-2 of the highest-confidence follow-up issues this session, or queue all of them for owner review? Default is queue — confirm at approval.
- **Open:** Does the owner want hack #11 (plan-confidence telemetry) bundled into the existing #2018 enforcement-gate epic, or stand-alone?
- **Open (Claude r1 finding 8):** Two coexisting overnight-prompts roots for 2026-04-29 (`2026-04-29-weekly-gtm-targets/` and `2026-04-29-next-wave-autofeed/`) both produce summaries that update this issue. Plan currently lists `weekly-gtm-targets/results/issue-2557-summary.md` in the Artifact Map, but the next-wave-autofeed root has produced more recent summaries. Operator decision required: which root is canonical for #2557 follow-ups going forward? Until decided, treat both as acceptable input but consolidate the **next** summary under whichever root the operator names.

---

## Complexity: T2

Analysis deliverable across multiple coordinated artifacts (plan, report, summary, index update), with explicit no-implementation boundary and a downstream follow-up-issue queue. Not T1 because of the cross-artifact verification requirement; not T3 because no source-code change is in scope.
