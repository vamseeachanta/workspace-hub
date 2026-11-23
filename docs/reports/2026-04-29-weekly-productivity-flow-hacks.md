# Weekly productivity flow hacks — 2026-04-29

> Issue: [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557) — chore(productivity): weekly work-pattern review and flow hacks
> Plan: `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md`
> Status: first-pass report, draft plan
> Audit window: 2026-04-22 → 2026-04-29 (W17 tail + W18 to date)

---

## TL;DR

Three findings dominate the week:

1. **Provider lanes are starving.** W18 utilization: claude 6.6%, codex 0.4%, gemini 0.1%. The harness produced 21 overnight feeds in 12 hours — every one ended at an operator-only command pack, zero GitHub mutations. The bottleneck is not credits; it is owner-authorization throughput.
2. **Plan-review is auto-cycling.** Issue [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) was revised six times (feeds 16-21) inside one 12-hour window without ever exiting plan-review, partly because [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) (codex-cli 0.124 stdin-hang) blocks Codex review and the loop has no consensus-vs-minority stop rule.
3. **GTM target slipped.** This week's stated GTM target (capability charts + contractor brochure send) had overnight prompts staged at `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/` but the launchers were not run; no GTM artifact has shipped. [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554), [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555), [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556).

The 14 hacks below target those three findings plus the standing context/handoff hygiene tax.

---

## Evidence audited

| Source | Used for |
|---|---|
| [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557) issue body | Scope, dimensions, acceptance criteria |
| `docs/BUSINESS_BRAIN.md` | Owner role, autonomous-hard-gate goal, weekly target |
| `docs/reports/provider-utilization-weekly.md` (2026-04-29T13:20Z) | W18 vs W17 utilization, underuse alerts |
| `docs/reports/provider-routing-scorecard.md` (2026-04-29T13:20Z) | Per-provider preferred work + recommended actions |
| `docs/reports/provider-work-queue.md` (2026-04-29T13:20Z) | Execution-ready candidates per provider |
| `docs/reports/provider-autolabel-candidates.md` (2026-04-29T13:20Z) | Auto-routing confidence scores |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/lane-monitor-latest.md` | All 6 lanes + 21 feeds COMPLETED, zero GitHub mutations |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/{next-dispatch-queue,github-command-pack,plan-review-command-pack}.md` | Operator-only command pack pattern |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-{rereview,micropatch,crossreview-readiness}-2374-feed{19,20,21}.md` | #2374 plan-review churn (6 revisions/12h) |
| `.claude/skills/coordination/issue-planning-mode/SKILL.md` v3.1.0 | Drift handling already consumes ~50 lines of operational rules |
| `.claude/memory/topics/feedback_codex_cli_0_124_upstream_regression.md` | Codex blocked since 2026-04-23 |
| `.claude/memory/topics/feedback_codex_sustained_major_loop.md` | 3+ MAJOR rounds = anti-pattern |
| `.claude/memory/topics/feedback_hermes_active_preflight_check.md` | Silent commit-revert race |
| `.claude/memory/topics/feedback_gemini_sandbox_overlay_blindness.md` | Cross-review false-positive MAJORs |
| Related issues: [#2254](https://github.com/vamseeachanta/workspace-hub/issues/2254), [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479), [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519), [#2523](https://github.com/vamseeachanta/workspace-hub/issues/2523), [#2524](https://github.com/vamseeachanta/workspace-hub/issues/2524), [#2525](https://github.com/vamseeachanta/workspace-hub/issues/2525) | Cross-reference for non-duplicate hack proposals |

Owner-time impact estimates are bounded ranges, not measurements; hack H7 below proposes the missing instrument that would convert estimates into evidence.

---

## Friction map (what to attack)

| Dimension | Top observed friction | Evidence |
|---|---|---|
| GTM throughput | Weekly capability-chart + brochure target unbuilt; 0 outbound artifacts shipped W18 | overnight-prompts/2026-04-29-weekly-gtm-targets/ unstarted |
| Engineering throughput | 8 Codex `status:plan-approved` issues queued, lane at 0.4%; Codex CLI broken | `provider-work-queue.md`, [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) |
| Agent orchestration | 21 feeds → 0 GitHub mutations; sustained-MAJOR loops auto-cycling | `lane-monitor-latest.md`, [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) feed16-21 |
| Context/handoff hygiene | Plan-state drift across 4 surfaces (label, marker, README, review-results); skill spends 50+ lines on drift handling | `issue-planning-mode/SKILL.md` lines 100-188; many `(rev-N)` and "rolled back" rows in `docs/plans/README.md` |

---

## Ranked hack backlog (14 hacks)

Each hack: dimension(s), evidence, owner-time impact (bounded estimate), effort tier (Immediate ≤30 min owner-time to enable; This-week 1-3 days; Structural this milestone), first action, follow-up issue candidate.

### Tier 1 — Immediate (5 hacks)

#### H1. Pin codex-cli to 0.123.0 in Hermes preflight
- **Dimensions:** engineering throughput, agent orchestration
- **Evidence:** `feedback_codex_cli_0_124_upstream_regression.md` — 0.124.0 hangs on stdin for 90-byte plans; [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) filed; Codex W18 lane at 0.4% util while 17 routed candidates wait.
- **Owner-time impact:** ≈2-3h/week (recovers manual review-dispatch fallbacks; unblocks Codex implementation lane).
- **Effort:** Immediate.
- **First action:** Add `codex --version | grep -q 0.123.0 || npm install -g @openai/codex@0.123.0` to `scripts/hermes/preflight.sh`; gate `scripts/review/submit-to-codex.sh` on the same check.
- **Follow-up candidate:** likely covered by [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479); add comment with the preflight pin instead of a new issue.

#### H2. Drain-ready-queue command pack (one-click execute)
- **Dimensions:** engineering throughput, agent orchestration
- **Evidence:** `provider-work-queue.md` — 3 Claude `status:plan-approved` ready (#2490, #2510, #2515); 8 Codex ready listed (#2269, #2289, #2346, #2364, #2368, #2369, #2373, #2402); none started.
- **Owner-time impact:** ≈75 min/week (eliminates daily 15-min "what should I dispatch next" decision × 5 days).
- **Effort:** Immediate.
- **First action:** Add `scripts/queue/drain-ready.sh` that prints the next 3 ready `status:plan-approved` issues per provider with launch commands; surface in the daily-readiness cron output already living at `docs/reports/`.
- **Follow-up candidate:** new issue `feat(queue): one-click drain-ready dispatch pack` if not covered by [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519); cross-reference required.

#### H3. Plan-review consensus-vs-minority stop rule
- **Dimensions:** agent orchestration, context/handoff hygiene
- **Evidence:** `feedback_codex_sustained_major_loop.md` is explicit; [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) feed16→feed21 (6 revisions in 12h, never exited plan-review).
- **Owner-time impact:** ≈90-120 min per stuck plan (saves ~3 wasted nightly cycles when Codex MAJOR is structurally unreachable).
- **Effort:** Immediate.
- **First action:** Patch `scripts/review/cross-review.sh` (or sibling) to detect `>=3 consecutive MAJOR from one provider while others MINOR/APPROVE`, then emit `scripts/review/results/CONSENSUS-VS-MINORITY-<plan>.md` and STOP, do not auto-spawn round 4. Comment on the GitHub issue with the decision packet.
- **Follow-up candidate:** new issue `feat(review): sustained-MAJOR stop rule and consensus packet`; verify no overlap with [#2289](https://github.com/vamseeachanta/workspace-hub/issues/2289) (bypass rollback recovery, different scope).

#### H4. Comment-only command-pack auto-executor (allowlisted)
- **Dimensions:** agent orchestration, GTM throughput
- **Evidence:** `lane-monitor-latest.md` records `github-command-pack.md`, `plan-review-command-pack.md` produced ~22:00 CDT 2026-04-28 and never executed; their content is exclusively `gh issue comment`-style operations.
- **Owner-time impact:** ≈25-40 min/day (≈ 2.5h/week of manual paste+verify).
- **Effort:** Immediate.
- **First action:** New `scripts/govern/exec-safe-command-pack.sh` with a hard allowlist (`gh issue comment` only; reject any line containing `--add-label`, `--remove-label`, `gh issue close`, `gh pr merge`, `git push`); cron runs comment-only packs nightly. Mutation-class packs (label/merge) remain owner-only.
- **Follow-up candidate:** new issue `feat(govern): allowlisted comment-only command-pack auto-executor`. Coordinate with [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) (Hermes orchestration).

#### H5. GTM owner-decision brief (1 page, 3 candidates max)
- **Dimensions:** GTM throughput, context/handoff hygiene
- **Evidence:** `ace1-gtm-packager.md` produced 5-7 outreach candidates; W18 GTM target ([#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554), [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555), [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556)) has zero shipped artifacts; the overnight prompts under `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/` were staged but not launched.
- **Owner-time impact:** ≈90-120 min/week (collapses 5-7 candidate review to 3-decision review).
- **Effort:** Immediate (template + cron entry).
- **First action:** Cron job emits `docs/gtm/owner-decision-brief-YYYY-MM-DD.md` with exactly 3 candidates, format: `Buyer | Proof path | Send / Hold / Kill`. Default mode is "Hold pending owner"; nothing auto-sends.
- **Follow-up candidate:** new issue `feat(gtm): daily owner-decision brief generator`. Coordinate with [#2346](https://github.com/vamseeachanta/workspace-hub/issues/2346) (already plan-approved, prospect-data pipeline).

### Tier 2 — This-week (4 hacks)

#### H6. Plan-state drift reconciler (4-surface daily report)
- **Dimensions:** context/handoff hygiene, agent orchestration
- **Evidence:** `issue-planning-mode/SKILL.md` lines 100-188 catalogue label/marker/README/review-result drift cases; numerous `docs/plans/README.md` rows annotated `(rev-N)` or "rolled back from premature approval".
- **Owner-time impact:** ≈30-45 min/week (pre-empts 1-2 stale-state debugging episodes/month).
- **Effort:** This-week (extend daily-readiness cron).
- **First action:** Add `scripts/govern/reconcile-plan-state.sh` cron step that diffs the 4 surfaces (`gh label list`, `.planning/plan-approved/`, `docs/plans/README.md`, `scripts/review/results/`) and emits `docs/reports/plan-state-drift-YYYY-MM-DD.md` with only divergences. Extend `daily-readiness` cron (per `project_daily_readiness_cron.md`).
- **Follow-up candidate:** likely covered by [#2255](https://github.com/vamseeachanta/workspace-hub/issues/2255) (reconcile-github-plan-approval-labels-with-local-marker-ledger); update issue body rather than open new.

#### H7. Owner-time accounting instrument
- **Dimensions:** all four (cross-cutting measurement)
- **Evidence:** No artifact today answers "owner minutes/week on orchestration vs origination". Every hack in this report quotes bounded estimates because the substrate is missing.
- **Owner-time impact:** Indirect — unlocks evidence-driven prioritization for hacks H1-H14; precondition for Business Brain's confidence-threshold-gate vision.
- **Effort:** This-week.
- **First action:** Lightweight log: `scripts/state/log-owner-action.sh <category> [duration_seconds]` writes JSONL to `.claude/state/owner-actions/YYYY-MM-DD.jsonl`. Categories: `gh_mutation`, `plan_approval`, `command_pack_run`, `gtm_decision`, `origination`. Hook into existing prompt-submit hook for low-friction capture.
- **Follow-up candidate:** new issue `feat(telemetry): owner-time accounting instrument`. No duplicate found.

#### H8. Provider quota observability (priority bump for #2254)
- **Dimensions:** agent orchestration
- **Evidence:** `provider-utilization-weekly.md` notes "telemetry is weak; treat utilization as directional, not exact" for Claude/Gemini; [#2254](https://github.com/vamseeachanta/workspace-hub/issues/2254) already filed.
- **Owner-time impact:** ≈45-60 min/week (saves over-cautious or wasteful provider routing decisions).
- **Effort:** This-week (existing issue, just promote).
- **First action:** Comment on [#2254](https://github.com/vamseeachanta/workspace-hub/issues/2254) requesting MVP polled snapshot every 15 min into `state/provider-quota.jsonl`; do not block on full implementation. Cross-link this report.
- **Follow-up candidate:** none — [#2254](https://github.com/vamseeachanta/workspace-hub/issues/2254) is the canonical home.

#### H9. Stuck-lane detector (named tmux + idle threshold)
- **Dimensions:** agent orchestration
- **Evidence:** `lane-monitor-latest.md` row D1 was earlier "BLOCKED on env" then later reclassified COMPLETED only after the final summary appeared; recovery is reactive. Lane C3's named log was absent but artifacts present — manual reconciliation needed.
- **Owner-time impact:** ≈60-90 min/week (prevents 1-2 silent night losses/week × ~30 min recovery).
- **Effort:** This-week.
- **First action:** `scripts/hermes/detect-stuck-lane.sh` polls named tmux sessions every 90 s; if stdout file has not grown in N minutes (configurable per lane), writes `state/lane-stuck-<name>.json` and pages the next preflight cycle to consider re-dispatch.
- **Follow-up candidate:** likely covered by [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) and [#2523](https://github.com/vamseeachanta/workspace-hub/issues/2523); add comment instead of new issue.

### Tier 3 — Structural (5 hacks)

#### H10. Capability-chart + contractor-brochure pipeline (split into 4 typed deliverables)
- **Dimensions:** GTM throughput, engineering throughput
- **Evidence:** Weekly target seed in `docs/BUSINESS_BRAIN.md` line 110: "vessel capability charts and brochure to all researched vessel contractors". [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554), [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555), [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) overnight prompts staged but never ran. Zero GTM artifacts shipped W18.
- **Owner-time impact:** ≈4-6h/week recovered after first run (turns "weekly target attempted, deferred" into a repeatable pipeline).
- **Effort:** Structural (split into bounded deliverables, then implement).
- **First action:** Comment on [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557) (or [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554)) proposing the 4-deliverable split: (a) contractor list dedupe with provenance + count, (b) capability-chart template with deterministic data inputs, (c) brochure send-list with consent state, (d) one-click owner approval comment that triggers `scripts/gtm/send-outreach-batch.sh`.
- **Follow-up candidate:** if [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554)/[#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555)/[#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) cover (a)-(c), only file (d). Verify before filing.

#### H11. Plan-confidence telemetry (dry-run scaffolding for confidence-threshold gates)
- **Dimensions:** engineering throughput, agent orchestration
- **Evidence:** `docs/BUSINESS_BRAIN.md` lines 80-99 "Autonomous Hard-Gate Evolution" calls for confidence-threshold gates "with measured evidence", today no measurement exists.
- **Owner-time impact:** Zero immediately; sets up multi-hour/week saving in 4-6 weeks once data justifies relaxing specific gates.
- **Effort:** Structural.
- **First action:** Emit `state/plan-confidence-score.jsonl` per plan recording: consecutive APPROVE/MINOR count, MAJOR count, TDD evidence presence, legal-scan pass. Dry-run only — no automatic promotion. After 4 weeks of data, decide which T1 + low-blast-radius config plans can self-promote.
- **Follow-up candidate:** new issue `feat(govern): plan-confidence telemetry scaffolding (no auto-promotion)`. Coordinate with [#2018](https://github.com/vamseeachanta/workspace-hub/issues/2018) (agent-bypass-resistance epic).

#### H12. Plan-from-issue scaffolder (gsd:plan-from-issue)
- **Dimensions:** engineering throughput
- **Evidence:** Every plan has the same Resource Intelligence skeleton; the 21 12h-continuation feeds produced ~6 plan skeletons that all manually duplicate this scaffold (e.g. `ace1-plan-draft-2378-feed2.md`, `-feed3.md`, `-feed4.md` for #2378 alone).
- **Owner-time impact:** Indirect; reduces plan-review queue length by removing template-fill cycles.
- **Effort:** Structural.
- **First action:** New `gsd:plan-from-issue` wrapper that: reads `gh issue view <NNN>`, queries the retrieval-contract sources defined in [#2208](https://github.com/vamseeachanta/workspace-hub/issues/2208), pre-populates Resource Intel + Artifact Map sections, saves to `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`. Agent only fills design-decision sections.
- **Follow-up candidate:** new issue `feat(gsd): plan-from-issue scaffolder honoring #2208 retrieval contract`.

#### H13. Pre-push session-signal check for Hermes-active race
- **Dimensions:** context/handoff hygiene
- **Evidence:** `feedback_hermes_active_preflight_check.md` — Hermes cleanup loops can revert parallel commits within minutes if running on `main`; recurred 2026-04-25 wave-3/wave-5.
- **Owner-time impact:** ≈30-60 min/month (prevents 1-2 silent-revert recoveries × ~30 min each).
- **Effort:** Structural (touches push gate).
- **First action:** Pre-push hook step: `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'`; if active, refuse push from non-worktree branch with documented bypass for known-safe state.
- **Follow-up candidate:** new issue `feat(govern): pre-push Hermes-active preflight gate`. Coordinate with [#2128](https://github.com/vamseeachanta/workspace-hub/issues/2128) (install-hooks pre-push chain).

#### H14. Inline gh issue URL renderer for chat output
- **Dimensions:** context/handoff hygiene
- **Evidence:** `MEMORY.md` cites `feedback_inline_gh_issue_url.md` — owner explicitly wants `#NNNN` rendered as Markdown hyperlink in chat output, not bare token.
- **Owner-time impact:** Small daily friction (≈3-5 min/day; ≈30 min/week of copy-paste avoided).
- **Effort:** Structural (settings + post-process hook).
- **First action:** Settings hook that post-processes assistant output with regex `#(\d{3,5})` → `[#$1](https://github.com/vamseeachanta/workspace-hub/issues/$1)`. Apply only on text outside fenced code blocks.
- **Follow-up candidate:** new issue `feat(harness): inline gh issue URL renderer in chat output`. Verify no overlap with existing settings.json hook.

---

## Top-3 immediate priorities (ready for execution without further owner input)

These three are runnable today by an authorized agent or by the owner; first action is single-paragraph, no design unknowns.

1. **H1 — Pin codex-cli to 0.123.0 in Hermes preflight.** Unblocks 17 routed Codex candidates. ~2-3h/week recovered.
2. **H2 — Drain-ready-queue command pack.** Names the next 3 ready issues per provider; one-click dispatch. ~75 min/week of decision overhead removed.
3. **H4 — Comment-only command-pack auto-executor.** Allowlist enforced; cron runs only comment-class packs. ~2.5h/week of paste-verify removed.

---

## Follow-up issue candidates (queued, not filed in this session)

| # | Hack | Title (proposed) | Duplicate-of-check | State |
|---|---|---|---|---|
| FU-1 | H3 | feat(review): sustained-MAJOR stop rule and consensus packet | verify against [#2289](https://github.com/vamseeachanta/workspace-hub/issues/2289) | candidate (not filed) |
| FU-2 | H4 | feat(govern): allowlisted comment-only command-pack auto-executor | verify against [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) | candidate (not filed) |
| FU-3 | H5 | feat(gtm): daily owner-decision brief generator | verify against [#2346](https://github.com/vamseeachanta/workspace-hub/issues/2346) | candidate (not filed) |
| FU-4 | H7 | feat(telemetry): owner-time accounting instrument | none found | candidate (not filed) |
| FU-5 | H10(d) | feat(gtm): one-click owner-approval brochure-send trigger | verify against [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554)/[#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555)/[#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) | candidate (not filed) |
| FU-6 | H11 | feat(govern): plan-confidence telemetry scaffolding (no auto-promotion) | coordinate with [#2018](https://github.com/vamseeachanta/workspace-hub/issues/2018) | candidate (not filed) |
| FU-7 | H12 | feat(gsd): plan-from-issue scaffolder honoring #2208 retrieval contract | none found | candidate (not filed) |
| FU-8 | H13 | feat(govern): pre-push Hermes-active preflight gate | coordinate with [#2128](https://github.com/vamseeachanta/workspace-hub/issues/2128) | candidate (not filed) |
| FU-9 | H14 | feat(harness): inline gh issue URL renderer in chat output | check existing hooks | candidate (not filed) |

H1, H2, H6, H8, H9 deliberately recommend commenting on existing issues rather than filing duplicates.

Per the audit prompt's "do not create extra issues unless strongly justified and non-duplicate" rule, **none of these were filed during this drafting session.** Owner approval (or H4-style allowlisted batch) should authorize the duplicate-check + filing step.

---

## Validation log (acceptance evidence)

- EC-1 (each hack cites a path/issue): satisfied — every hack's Evidence row names a path or numbered issue.
- EC-2 (numeric owner-time): satisfied — bounded ranges given for H1-H14; H7/H11/H12 explicitly mark Indirect/Zero-immediate per honest-evidence rule.
- EC-3 (concrete first action): satisfied — every hack names a script path, file path, or `gh` command.
- EC-4 (≥3 immediately actionable): satisfied — five Tier-1 hacks (H1-H5); top-3 priority section makes the executable subset explicit.
- EC-5 (4 dimensions covered): satisfied — friction map and per-hack Dimensions tags cover all four.
- EC-6 (no auto-filed follow-up issues): satisfied — all 9 candidates marked `candidate (not filed)`.

---

## Open questions for owner

1. Confirm: file FU-1 through FU-9 in batch as part of next approval, or filter further?
2. Confirm: H10's 4-deliverable GTM split — does it replace [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554)/[#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555)/[#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556), or sit alongside them?
3. Confirm: H11 (plan-confidence telemetry) — bundle into [#2018](https://github.com/vamseeachanta/workspace-hub/issues/2018) or stand-alone?
4. Confirm: should the Tier-1 hacks (H1, H2, H4) execute under owner-supervised next session, or wait for a full plan-review wave on this plan first?
