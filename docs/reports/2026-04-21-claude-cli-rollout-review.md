# 2026-04-21 Claude Code CLI Rollout Review — Source Artifact

**Status:** superseded first-pass; revision in progress (umbrella #2425)
**Author:** Claude Code (Opus 4.7) session, 2026-04-21
**Cited from:** umbrella issue #2425

## Purpose

This document is the source-of-truth artifact for the "2026-04-21 ecosystem review" that generated the Claude Code CLI integration rollout in umbrella issue #2425. It exists because the umbrella's first-pass body cited a review without naming an artifact — reviewer #2425 flagged the missing citation as a governance-traceability defect.

## Method (first pass)

1. **Survey** — listed all 80 open GitHub issues, label-weighted
2. **Shortlist** — picked 5 initial candidates based on fit-for-Claude-CLI heuristics
3. **Parallel-work check** — scanned recent commits (3 days) and active worktrees
4. **Existing-footprint check** — inventoried ~25 existing Claude-CLI integration points to avoid duplication
5. **Framing comments** — posted per-pilot framing comments on 4 candidates + created umbrella #2425
6. **Adversarial review wave** — 5 parallel Claude subagents reviewed each pilot (and the umbrella) with explicit adversarial stance
7. **Revision** — current phase; reviewer findings being incorporated

## Candidates considered

| Issue | First-pass disposition | Current status after review |
|---|---|---|
| #2347 reconcile stale trackers | Pilot #1 (recommended) | **MAJOR** — scope 30+ sub-issues, 2/4 trackers require semantic judgment, #2405 attestation over-applied |
| #2424 cross-repo CI audit | Pilot #2 | **MAJOR** — "never-merge" lacks technical gate, log-size undefined, "6 of 7 red" is actually 4-active + 2-dormant |
| #2413 email automation epic | Pilot #3 (framing) | **MAJOR** — framing contradicts #2017 v7 D1 locked decision; scope-selection bias; #2413 is itself an epic, not a pilotable unit |
| #2417 autoresearch generalization | Pilot #4 (framing) | **MAJOR** — reuse claim overstated 5×; flagged items miss actual reviewer MAJORs; `.claude/hooks/` category error |
| #2325 umbrella self | — | **MAJOR** — pilot #1 misranked, anti-candidates collide with epic #2390, parallel-work scan >6× undercounted |
| #2346 GTM prospect pipeline | Dropped (parallel work) | Correct — commit `d31bcdc29` landed today |
| #2324 MEMORY.md curation | Dropped (already implemented) | Correct — commit `1f7fd855b` 2026-04-20 |

### Bench candidates (not promoted)
#2418 compounding autoresearch (pairs with #2417) · #2351 GTM checkpoint dashboard · #2333 transient-read classification · #2408/#2399 release-readiness golden-task corpus

### Anti-candidates (first-pass)
#2359 plugin removal · #2416 tagger-date fix · #2415 fenced-block extract · #2386 fixture relocation · #2357 sitemap backfill · #2360–#2362 schema/frontmatter edits

**Reviewer correction:** #2360 and #2362 are **not** anti-candidates — they are explicit prerequisites in epic #2390's Wave 0. #2357 is `status:plan-approved` in the `domain:gtm` track and should be classified as "out-of-rollout-domain (GTM), approved separately" rather than anti-candidate.

## Parallel-work scan — corrected

First-pass scan named 4 items. Actual `git worktree list` output as of 2026-04-21:

**27 active worktrees**, including several with direct pilot overlap:
- `issue-2323` — cross-AI-review-fanout (directly overlaps the review infrastructure used in this wave)
- `issue-2322` — rule-promotion to Level 2 scripts (overlaps enforcement framing for #2424)
- `issue-2320` — skill-usage-audit (overlaps #2417 target surface)
- `issue-2206` / `issue-2207` / `issue-2209` — verify-close on commit `227569442` (all on 2026-04-21)
- `issue-2348-exec` + `issue-2348-nightly` — live scanner triage (two worktrees)
- `issue-2281` / `issue-2282` — skills audit and policy
- `ecosystem-sync` + `workspace-hub-ecosystem-sync-integration` — release infra
- `issue-2290-v2` — skill dedup v2
- `nightly-2026-04-20-batch` — batch execution surface
- plus 14 more planning/verify worktrees

**Implication:** any Claude-CLI rollout must coordinate with #2323's cross-AI review fanout (not duplicate it), #2322's rule-promotion scripts (the same enforcement-gradient pattern), and #2320's skill-usage-audit (overlaps #2417).

## Cross-epic reconciliation

| Claim in first-pass umbrella | Conflict | Correction |
|---|---|---|
| #2360 is an anti-candidate | #2390 Wave 0 lists #2360 as prerequisite for ~20 downstream issues | Remove from anti-candidate list; reference as #2390 Wave 0 prerequisite |
| #2362 is an anti-candidate | #2390 Wave 0 lists #2362 as prerequisite | Remove from anti-candidate list |
| #2357 is an anti-candidate | #2357 is `status:plan-approved` in `domain:gtm` | Reclassify as "out-of-domain approved separately" |
| #2413 is pilotable | #2413 is itself an epic deferring to #2017 | Drop from pilot sequence; keep as coordination reference |

## Adversarial review artifacts

- `scripts/review/results/2026-04-21-rollout-2347-claude.md` — MAJOR
- `scripts/review/results/2026-04-21-rollout-2424-claude.md` — MAJOR
- `scripts/review/results/2026-04-21-rollout-2413-claude.md` — MAJOR
- `scripts/review/results/2026-04-21-rollout-2417-claude.md` — MAJOR
- `scripts/review/results/2026-04-21-rollout-2425-claude.md` — MAJOR
- Commit: `4682a2c18`

## Machine-binding

Per memory `feedback_cross_machine_execution.md`: per-machine tasks coordinate via shared git repo, not SSH/rsync. Any Claude-CLI rollout pilot executes on the machine that picks up `status:plan-approved` for that pilot's concrete plan. Cross-machine coordination is via:
- commit + push of plan file to `docs/plans/`
- `.planning/plan-approved/NNN.md` approval marker
- no SSH-triggered dispatch

## Approval discipline

Per user direction 2026-04-21: **execution only after user-applied `status:plan-approved` label on GitHub**. This applies to each pilot's concrete plan file, not to this umbrella or to coordination artifacts. The umbrella itself does not carry a `status:*` label — it is a meta-tracker, not a plan.

Per memory `feedback_never_offer_to_self_label_plan_approved.md`: agent presents options + CLI commands; user labels.

## Lifecycle of umbrella #2425

- **Active:** while any of #2347/#2424/#2417 pilots are being scoped, planned, or executed
- **Closed:** when all referenced pilots are either closed or formally withdrawn
- Does NOT carry `status:plan-review` or `status:plan-approved` labels
- Does NOT require its own plan file — coordination/meta issue

## Open questions for user

1. Proceed with revised umbrella body (current draft in session)?
2. After umbrella revision lands: which (if any) pilot to scope down to a plan-worthy shape? Options:
   - #2347 narrowed to mechanical-only tracker subset (#2016, #1669 only)
   - #2424 re-scoped to just active-red repos + defined log-size contract + technical never-merge gate
   - #2417 deferred entirely until its current rewrite wave concludes
   - #2413 withdrawn as pilot (keep as coordination reference only)
3. Whether to invest in Codex/Gemini cross-provider review on the revised artifacts (#2323 worktree is building this infra — coordinate or wait?).
