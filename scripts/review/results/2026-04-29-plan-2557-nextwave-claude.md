## Verdict
MAJOR

## Provenance note
Single-author Claude self-review (r1, "nextwave"). Same permission-gate scenario as plan #2556's nextwave artifacts — the `scripts/review/plan-review-fanout.sh` dispatch was rejected by the Bash permission gate in this autofeed session. Per `feedback_permission_gate_blocks_cross_review.md`, this artifact is Claude-authored adversarial review with explicit absence stubs for Codex and Gemini. **Multi-provider consensus is not established by this batch.** Run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` from an un-sandboxed terminal before promoting past `status:plan-review`.

## Retrieval
- Read `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` end-to-end.
- Read `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md` end-to-end (14 hacks, friction map, EC checks).
- Read `docs/reports/provider-utilization-weekly.md` (Generated `2026-04-29T09:20:08Z`). W18 row: `claude 5.8% (activity_vs_recent_peak)`, `codex 0.4%`, `gemini 0.1%`. Underutilization-alerts block confirms `claude at 5.8%`.
- Read `docs/reports/provider-routing-scorecard.md` (Generated `2026-04-29T09:20:08Z`). Confirms `claude 5.8%`.
- Read `docs/reports/provider-work-queue.md` (Generated `2026-04-29T09:20:10Z`). codex: `Execution-ready candidates: 18; Total routed candidates: 41`. claude: `Execution-ready candidates: 1; Total routed candidates: 157`.
- Read `docs/BUSINESS_BRAIN.md` lines 60–125. Lines 65, 80–99 cited verbatim. Line 110 verbatim: *"for the week of April 1, produce vessel capability charts and send a good brochure to all researched vessel contractors"*.
- Read `.claude/memory/topics/feedback_codex_cli_0_124_upstream_regression.md`. Confirms 0.124.0 hangs on stdin for plans as small as 90 bytes; **0.123.0 also hangs from inside Claude Code's Bash tool** (verified 2026-04-24 session). Downgrade may help in plain terminal but cannot be validated from agent sessions.
- `gh issue view 2479` — OPEN; `bug, priority:high, cat:harness, domain:knowledge-management`; title `fix(review): Codex stdin-hang regression post-#2406 closure (size-dependent)`.
- `gh issue view 2289` — OPEN; labels `priority:high, cat:harness, domain:workflow, status:working, agent:codex, status:plan-approved`. Title (per `provider-work-queue.md`): "Plan rollback/recovery for enforcement bypasses detected after commit or push".
- `gh issue view 2016` — OPEN; `priority:high, cat:business, cat:strategy, domain:gtm`.

## Findings

1. **Stale W18 utilization in report TL;DR (report TL;DR / friction map).**
   Report claim: *"W18 utilization: claude 6.6%, codex 0.4%, gemini 0.1%"*. Live `docs/reports/provider-utilization-weekly.md` (Generated `2026-04-29T09:20:08Z`) shows W18 `claude 5.8%`. The 6.6% number does not appear anywhere in the current source. The plan and report repeat the 6.6% figure in TL;DR, friction map, and H2 framing. Either the report was drafted from an earlier regeneration that has since been overwritten, or the figure is simply wrong. Either way, the headline finding "Provider lanes are starving" is now under-counted by ~14% — and a public productivity report that quotes the wrong claude utilization will undermine reviewer confidence in every other number in the document.

2. **Stale generation timestamp (plan §Resource Intelligence and report Evidence-audited).**
   Plan + report both cite the three provider reports as "(generated 2026-04-29T13:20Z)". Live file headers read `Generated: 2026-04-29T09:20:08.080229Z` (utilization-weekly), `2026-04-29T09:20:08.282381Z` (routing-scorecard), `2026-04-29T09:20:10.666336Z` (work-queue). The 13:20Z timestamp is wrong — the regeneration ran at 09:20Z UTC, not 13:20Z. The `09:20Z` hour matches the documented daily-readiness cron; treating 13:20Z as authoritative misrepresents the cron's run time.

3. **Stale Codex work-queue numbers (report H2 "Drain-ready-queue").**
   Report claim: *"8 Codex `status:plan-approved` issues ready out of 17 routed (e.g. #2269, #2289, #2346, #2364, #2368, #2369, #2373, #2402)"*. Live `docs/reports/provider-work-queue.md`: codex `Execution-ready candidates: 18; Total routed candidates: 41`. Both numbers are roughly half of current reality. The example issue list is internally inconsistent — the report says "8 Codex" then lists 8 example issue numbers, but the live source shows 18 ready (so the example list under-represents available work by >50%). H2's first-action proposes "next 3 ready `status:plan-approved` issues per provider"; the underlying inventory data is wrong.

4. **Stale Claude work-queue numbers (report H2).**
   Report claim: *"3 Claude `status:plan-approved` ready (#2490, #2510, #2515)"*. Live source shows Claude `Execution-ready candidates: 1; Total routed candidates: 157` — only #2515 is in the current ready set. #2490 and #2510 are not in the current top of the routed list (which is `#2515, #2431, #2519, #2520, #2254, ...`). The report is treating its own snapshot as authoritative when the live source has moved.

5. **H1 `Pin codex-cli to 0.123.0 in Hermes preflight` does not actually unblock the agent-session lane (report H1, evidence cite vs memory `feedback_codex_cli_0_124_upstream_regression.md`).**
   The memory file (verified 2026-04-24 session) records: *"Downgrade does NOT help from Claude Code's Bash tool. Tested 0.124.0, 0.123.0, and 0.122.0 — all three hang."* H1's First-action gates `submit-to-codex.sh` on `codex --version | grep -q 0.123.0`; that gate is only meaningful for invocations that originate from outside Claude Code (plain user terminal). The hack should either declare that scope ("agent sessions remain blocked until upstream fix; this hack only restores Codex review for owner-driven cross-review runs") or be downgraded from "Tier-1 immediate, ~2-3h/week recovered" — the recovery only materializes for the operator's terminal sessions, not Hermes-dispatched lanes. Tier-1 owner-time-impact framing is misleading without that caveat.

6. **EC-2 internally inconsistent (plan §Verifiable Evidence Checks).**
   EC-2: *"Each hack has a numeric or bounded owner-time reduction estimate"*. The report's H7 explicitly lists owner-time impact as *"Indirect — unlocks evidence-driven prioritization"*; H11 lists *"Zero immediately; sets up multi-hour/week saving in 4-6 weeks"*; H12 *"Indirect; reduces plan-review queue length"*. Three of the 14 hacks fail EC-2 as written. Either rewrite EC-2 to accept "Indirect (with named precondition)" or downgrade those hacks. Report's "Validation log" claims EC-2 "satisfied" — that claim is wrong.

7. **H10's "4-deliverable GTM split" overlaps with #2554/#2555/#2556 without flagging the overlap concretely (report H10 Evidence/First-action vs the live `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`).**
   H10 proposes (a) contractor list dedupe with provenance, (b) capability-chart template, (c) brochure send-list with consent state, (d) one-click owner-approval comment trigger. The current brochure outline (sibling artifact for #2556 in the same plan-batch) already covers (b) via §3.3 chart slot contract and (c) via §4 outbound copy variants per tier. The report's H10 first-action says "Comment on #2557 (or #2554) proposing the 4-deliverable split" but the duplicate-of-check is not actually performed — the report should declare which of (a)–(c) is already absorbed by existing issues so only (d) remains as the candidate filing.

8. **`docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/` directory referenced in plan §Files-to-Change (Artifact Map "Overnight summary"), but the live overnight-prompts root for this batch is `2026-04-29-next-wave-autofeed/`. Reviewer cannot tell whether the `weekly-gtm-targets` directory was a one-time staging area for first-pass summaries or a canonical location.**
   The summary file `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2557-summary.md` exists and is consumed by this nextwave prompt as input — so the path resolves. But the plan does not name how the `weekly-gtm-targets` overnight pack relates to the `next-wave-autofeed` overnight pack. Two coexisting overnight pack roots for the same calendar day, both producing summaries that update the same issue, creates a de-facto split-brain. Plan should declare canonical location for follow-up summaries, or the next nightly run will produce summaries in a third location.

## Blockers

- Finding 1 — public productivity report quotes the wrong W18 claude utilization (6.6% vs live 5.8%). Block until corrected: regenerate the report against the current `docs/reports/provider-utilization-weekly.md` and re-derive W18 framing from 5.8%.
- Finding 3 — Codex work-queue example list (8 vs 18 ready) is materially stale; H2's owner-time-impact claim ("eliminates daily 15-min decision × 5 days") rests on this list.
- Finding 5 — H1 mis-frames its own owner-time-impact estimate. Block H1's "Tier-1 immediate" classification until the agent-session-vs-terminal scope is corrected and the recovery estimate is re-derived against the actual surface the pin restores.

Findings 2, 4, 6, 7, 8 are MINOR-MAJOR borderline; they all reflect the same root issue — the plan/report were drafted against a snapshot that was overwritten by the next regeneration cycle. Fix is structural: rebuild the report from a freshly-read live source, then re-stamp the timestamps and counts.
