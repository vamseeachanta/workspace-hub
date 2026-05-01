# Adversarial Approval-Readiness Review — 2026-04-29 Credit-Burn Wave

> **Reviewer:** Claude Opus 4.7 (1M ctx) — adversarial lane
> **Date:** 2026-04-29
> **Scope:** false-positive prevention for promotion to `status:plan-approved` across 14 candidate issues
> **Approval packs read:** `results/approval-pack-elements-2540-2544.md` and `results/approval-pack-additional-5.md` are **NOT YET PRESENT** (results/ was empty at audit time). This review re-derives readiness from primary sources.
> **Stance:** hostile — defect-hunting, not charitable reading
> **Authorization:** planning/review/prep ONLY. This prompt does NOT authorize implementation, label mutation, or issue close/reopen.

---

## Executive verdict

**Honest count: 0 of 14 candidates are unconditionally promotion-ready right now.**

Two are **already CLOSED** so the question is moot (#2542, #2543). One is approve-eligible only with a **live legal-clearance side-record** the plan does not produce on its own (#2541). One is approve-eligible only for a **bounded scout subset** that the issue title does not currently describe (#2544). The remaining ten fail at least one of: missing plan, untracked plan, single-provider review, sustained MAJOR loop, fake/blocked second-provider review, missing legal gate, scope mismatch.

| Bucket | Count | Issues |
|---|---:|---|
| Already CLOSED — not a promotion target | 2 | #2542, #2543 |
| Bounded-subset promotion possible only with explicit user wording | 2 | #2541 (SESA), #2544 (Woodfibre scout) |
| T1 deferred-review path — user can promote at own risk if comfortable | 1 | #2490 |
| Single-provider review only — second-provider gap | 4 | #2363, #2370, #2474, #2378 |
| MAJOR/UNAVAILABLE/sustained-loop or stub-only reviews | 3 | #2375, #2509, #2510 |
| No plan exists at all | 2 | #2538, #2540 (epic) |

---

## Per-issue readiness table

| Issue | Live state / labels | Plan path | Plan tracked? | Latest valid review (verdict) | Second-provider OK? | Legal gate | ready_now | False-positive risk if promoted |
|---:|---|---|---|---|---|---|---|---|
| **#2540** | OPEN, `status:plan-review` (epic) | **none found** | n/a | n/a | n/a | n/a (epic header) | **NO** | Epic carrying `status:plan-review` without an issue-level plan; promotion would be label-only. |
| **#2541** | OPEN, `status:plan-review` | `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` | YES | Codex rereview = MINOR; Gemini rereview = APPROVE (post-hardening) | Two providers — see noise note below | SESA row-level clearance is a HARD prerequisite per Codex; vendor/TBE controls metadata-only | **CONDITIONAL** | Plan is approve-ready only for "clearance/schema/test scaffolding + curated SESA extraction *gated on* explicit row-level clearance record." Promoting without that wording = false positive. |
| **#2542** | **CLOSED**, `status:done` (closed 2026-04-29T09:45:46Z) | `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md` | YES | Codex APPROVE / Gemini APPROVE rereview | OK | Per-artifact IP screening still required for any text/figure | **N/A — already done** | Adding `status:plan-approved` to a CLOSED `status:done` issue is incoherent. Requires reopen first via Hermes control surface (not authorized here). |
| **#2543** | **CLOSED**, `status:done` (closed 2026-04-29T09:45:50Z) | `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md` | YES | Codex APPROVE / Gemini APPROVE rereview | OK | Public metadata only; no clause text | **N/A — already done** | Same as #2542. The 2026-04-29 rereview synthesis still lists this as an "approval candidate" — that synthesis is now stale relative to live state. |
| **#2544** | OPEN, `status:plan-review` | `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` | YES | Codex rereview = APPROVE; Gemini rereview = APPROVE (scout subset only) | Two providers (with rereview-noise caveat) | All extraction blocked; pointer/scout metadata-only | **CONDITIONAL** | Approve-ready ONLY for "pointer/scout metadata + clearance schema preparation." If user approval text says "Woodfibre LNG corpus" without "scout-only," that promotes a scope larger than what was reviewed. |
| **#2370** | OPEN, **not** at `status:plan-review` (labels: enhancement, priority:high, cat:data-pipeline, domain:knowledge-management) | `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md` | YES (committed); feed10 patch is **unstaged** ` M` per feed11 | Claude feed9 = MINOR | **NO** — feed11 Codex was BLOCKED (permission gate + #2479 stdin regression); feed12 "Gemini lane" was self-authored by Claude per its own header ("Claude-authored independent analysis performed in lieu of Gemini execution"). Effectively single-provider. | Ledger is meta-tooling, not standards-derived; legal gate light | **NO** | Promoting on basis of "two reviews" is a false positive: only one independent provider verdict exists. Also `status:plan-review` label is missing. |
| **#2375** | OPEN, **not** at `status:plan-review` (labels: enhancement, priority:high, …) | `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md` (newest) | **NO — UNTRACKED in git** per `git status` | 2026-04-27 fanout = **all UNAVAILABLE** (Claude UNAVAILABLE; Codex UNAVAILABLE — stdin pipe; Gemini rc=55 trust-env) | NO | n/a — internal harness data | **NO** | Memory rule "queue git-tracked" (`feedback_queue_git_tracked.md`) is violated. The previous `2026-04-26-...-seeds.md` plan exists but the new 2026-04-29 plan is the one in flight; reviews on the old plan are stale. |
| **#2378** | OPEN, **not** at `status:plan-review` (labels: enhancement, priority:high, cat:documentation) | `docs/plans/2026-04-28-issue-2378-plan-draft.md` | YES | Claude feed5 = MINOR (post feed4 patch) | **NO** — only Claude lane; 2026-04-27 Codex/Gemini reviews are stub UNAVAILABLE; no Codex/Gemini review of the post-patch plan | Wiki ingest of marine-eng index — stays in standards namespace; legal already settled | **NO** | Single-provider MINOR is not sufficient evidence; promotion would be a one-author judgement. |
| **#2363** | OPEN, **not** at `status:plan-review` | `docs/plans/2026-04-26-issue-2363-wiki-refs-reverse-lookup.md` (newest) | YES | Claude r1 = **MAJOR** (5× MAJOR + 3× MINOR), unanswered | **NO** — older 2026-04-23 codex/gemini reviews target the *previous* 2026-04-23 plan that was rewritten | Wiki refs index — citation contract; legal moot | **NO** | MAJOR findings are substantive (e.g., "delete subcommand does not exist," "row count off by 380K," "AC vacuously satisfied"). Promoting now ships the wrong relation. |
| **#2474** | OPEN, **not** at `status:plan-review` | `docs/plans/2026-04-26-issue-2474-orcaflex-reverse-parser.md` | YES | Claude r1 = **MAJOR** (3× MAJOR + 5× MINOR) | **NO** — no Codex or Gemini review exists for #2474 at all | Engineering-internal tooling; legal moot | **NO** | MAJOR findings name concrete API contradictions (ModularModelGenerator, OrcaFlexVersion key) — this is not a polish-needed plan, it's a wrong-shape plan. |
| **#2509** | OPEN, **not** at `status:plan-review` | `docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` | YES | 2026-04-27 fanout = **all stub UNAVAILABLE** (286-526 byte files, no findings) | NO | Public OpenLane/OpenROAD demo — public artifact: legal must verify license headers + chip baseline reuse (#2511 referenced) | **NO** | No real verdict has ever been produced for this plan; promoting is ungrounded. |
| **#2510** | OPEN, `status:plan-review` | `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` | YES (49KB) | r13 (latest valid round): **Codex MAJOR / Gemini MAJOR / Claude UNAVAILABLE** after 13 review rounds | YES providers, but **sustained-MAJOR-loop pattern** per memory `feedback_codex_sustained_major_loop.md` | Public CAD demo — legal/license gate needed | **NO** | This is the textbook anti-pattern flagged in `#2045/#2289` memory: 13 rounds of review have not converged. Promoting now means accepting that Codex's MAJOR is wrong without surfacing the consensus-vs-minority decision to the user. |
| **#2538** | OPEN, priority:medium | **none found** (no `docs/plans/*2538*`) | n/a | n/a | n/a | Personal property imagery — `achantas-data` style; raw photo data privacy gate before publishing anything | **NO** | No plan exists. Promoting a plan-less issue would mean labeling intent without artifact. |
| **#2490** | OPEN, `status:plan-review` | `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md` | YES | **None by design** — plan declares "T1, adversarial review deferred to user approval gate" | n/a (waived per T1 convention) | Internal CI gate — no legal exposure | **CONDITIONAL** | This is the only honest plan-approved candidate. Risk: bypassing external review is a *convention*, not a verified safety property. If user accepts T1 deferred-review, promotion is reasonable. |

**Provenance noise note (#2541, #2544):** the Gemini rereview file `scripts/review/results/2026-04-29-plan-2541-2544-gemini-rereview.md` is 717 lines, of which the first ~30 are 429 capacity-exhausted errors and stack traces, and the substantive verdict block does not begin until line 695. The review eventually emitted APPROVE verdicts but the noise prefix should be acknowledged when citing it as second-provider evidence.

---

## False-positive risks (in priority order)

1. **CLOSED-issue label drift (#2542, #2543).** The synthesis at `scripts/review/results/2026-04-29-plan-2541-2544-rereview-synthesis.md` still calls these "approval candidates," but live `gh issue view` shows both are CLOSED `status:done` since 2026-04-29T09:45Z. Any approval-pack that re-recommends them is operating on stale state. **Mitigation:** any pack must re-query live `gh issue view` immediately before drafting commands.
2. **Single-author review masquerading as second-provider (#2370 feed12).** The file is named `…gemini-feed12.md` but its own header says "Claude-authored independent analysis performed in lieu of Gemini execution." This is precedent-misaligned with the cross-provider review policy (`project_cross_review_policy.md`) and `feedback_permission_gate_blocks_cross_review.md`. Honest framing is "single-author r3 with transparent provenance," not a "Gemini lane review." **Mitigation:** require the readiness pack to count #2370 as single-provider.
3. **Untracked plan promotion (#2375).** `git status` shows `?? docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`. Per `feedback_queue_git_tracked.md`, untracked plans cannot enter the queue. The pack must commit or exclude.
4. **Sustained-MAJOR-loop bypass (#2510).** Thirteen review rounds have produced repeated MAJOR verdicts. Memory rule `feedback_codex_sustained_major_loop.md` says: at 3+ rounds of MAJOR, surface the consensus-vs-minority decision to the user; do not auto-cycle into approval. The approval-pack must not silence this.
5. **Stub-only "reviews" treated as evidence (#2509, #2375, #2378-2026-04-27, #2510 r9-r12 stubs).** Files of 286/429/526 bytes with verdict text "UNAVAILABLE (fanout timed out…)" are not reviews. Counting them as review coverage = false positive.
6. **Legal-gate elision on Elements wave (#2541, #2544).** Both Codex and Gemini explicitly preserve hard runtime gates (SESA clearance for #2541; row-level clearance + separate post-scout plan for #2544). Promotion language must repeat those gates verbatim or it silently authorizes more than the reviewers approved.
7. **Plan-less promotion (#2538, #2540).** Promoting an issue that has no plan in `docs/plans/` is a label-only change with no artifact. The approval-pack must list "plan path" as `none found` and route to plan-draft, not plan-approved.
8. **Stale Codex/Gemini reviews for rewritten plans (#2363).** The 2026-04-23 codex/gemini files target a plan that has been substantially rewritten on 2026-04-26. Citing them as "second-provider coverage" of the new plan is a category error.
9. **`status:plan-review` label missing on #2363, #2370, #2375, #2378, #2474, #2509.** None of these carry `status:plan-review` per live labels — yet several have draft plans dating back days. Promotion to `status:plan-approved` from no `status:plan-review` skips the user-in-loop gate; per `feedback_never_offer_to_self_label_plan_approved.md`, this is exactly the path that must remain user-driven.
10. **Plan past-tense drift risk in #2541-#2544 plans.** Rereview synthesis has been hardening these for two days; per `feedback_plan_past_tense_artifact_claims.md`, the approval-pack should sample the plan body for past-tense claims about not-yet-shipped work before forwarding to user.

---

## Exact recommended actions for Hermes (no labels mutated by this review)

These are recommendations only — none are executed by this audit per the operating rules.

1. **Drop #2542, #2543, #2538, #2540 from the approval-readiness wave.** They are either CLOSED (#2542, #2543) or have no plan (#2538, #2540).
2. **Reclassify #2370, #2363, #2474, #2378 as "needs second-provider review," not "ready."** Dispatch a real Codex/Gemini fanout — the prompt-pack at `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/plan-review-command-pack.md` already has the recipe.
3. **Reclassify #2509 as "needs first real review."** The 2026-04-27 fanout produced only stubs; rerun once the codex-cli regression (#2479) is workable or via `js_repl + GitHub connector` fallback per `feedback_codex_sandbox_fallback_paths.md`.
4. **Surface #2510 as a consensus-vs-minority decision for the user.** Do NOT auto-cycle round 14. Present: "13 rounds, latest = Codex MAJOR + Gemini MAJOR + Claude UNAVAILABLE; minority position would say plan is sound; user picks."
5. **For #2375: commit the 2026-04-29 plan first, then re-run fanout.** The `?? docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md` line in `git status` is the blocker.
6. **For #2541, #2544: only dispatch user-approval requests with bounded-scope wording.** Both Codex and Gemini explicitly approved subsets, not the issue-as-titled. Suggested wording (verbatim from rereview synthesis):
   - #2541 → "Approve clearance/schema/test scaffolding plus curated SESA extraction *gated on row-level clearance record*; vendor/TBE remains metadata-only."
   - #2544 → "Approve pointer/scout metadata-only subset; all extraction/abstract/quote work blocked pending separate post-scout plan + row-level clearance."
7. **For #2490: surface to user as 'T1 deferred-review path — user accepts approval without external provider review.'** Do not auto-promote; this is a policy decision for the user.
8. **Honor the user-in-loop gate everywhere else.** Per `feedback_never_offer_to_self_label_plan_approved.md`, no batch agent in this wave should self-label `status:plan-approved`.

---

## Honest path to "10 promotion-ready issues"

Given the above, the wave cannot honestly produce 10 promotion-ready issues today. A truthful path:

- **Day 0 (today):** user can plan-approve at most 3 with bounded wording: #2541 (SESA gated), #2544 (scout-only), #2490 (T1 deferred-review). #2542 and #2543 are already done.
- **Day 1:** after committing the 2026-04-29 #2375 plan and re-running working Codex/Gemini fanouts on #2363, #2370, #2474, #2378, #2509, those five become candidates.
- **Day 2:** #2510 gets a consensus-vs-minority surfacing. #2538 needs a plan drafted before it can enter review at all. #2540 is an epic and should not carry `status:plan-approved` independently.

The honest near-term ceiling is **~5 promotion-ready issues by end of Day 1, ~7 by end of Day 2,** not 10 today.

---

## Sources audited

- Live labels via `gh issue view` for all 14 issues at 2026-04-29.
- `docs/plans/2026-04-2*-issue-{2363,2370,2375,2378,2474,2490,2509,2510,2541,2542,2543,2544}*.md` (file existence + git-tracked status via `git ls-files --error-unmatch`).
- `scripts/review/results/2026-04-2*-plan-{2363,2370,2375,2378,2474,2509,2510,2541-2544}*` (verdict headers, file size, authorship lines).
- `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/lane-monitor-latest.md` and `next-dispatch-queue.md`.
- Memory feedback files referenced inline by tag.
