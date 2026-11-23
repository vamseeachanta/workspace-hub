# Skill-Sprawl Analysis (refreshed telemetry) — #3062 / harden-epic #3058

> 2026-06-15. Companion to the model-parity work (#3043). Read-only analysis; no skills retired. Feeds #3062.

## What changed — and a correction
**Canonical telemetry is NOT stale.** `origin/main`'s `.claude/state/skill-scores.yaml` is current: `total_skills: 830`, generated **2026-06-14** (cadence running, last touched by #1725/#1742). The `402` / `2026-04-03` file initially observed was the **working copy of an unrelated feature branch** (`fix/cron-render…`, branched from an old base) checked out in this session's primary clone — a checkout artifact, not a cadence failure. Regenerating via `scripts/skills/skill-usage-report.py` produced **831 skills** — effectively identical to canonical (830), confirming the cadence is healthy.

So the telemetry "refresh" was a no-op against canonical. The valuable output is the **sprawl picture below**, which matches origin/main.

## Fresh picture

| Tier | Count | Share | Meaning (per the tool's heuristic) |
|---|---|---|---|
| HOT | 117 | 14% | 5+ cross-refs or recent git activity |
| WARM | 115 | 14% | 2–4 cross-refs |
| COLD | 65 | 8% | 1 cross-ref |
| **DEAD** | **534** | **64%** | 0 cross-refs AND no git mention (90 days) |

Plus, off the active tree:
- `.claude/skills/_archive/` — **2,166** SKILL.md (already archived; consolidation target)
- `_archive/skills/` — 88 SKILL.md (second archive convention — #3062 wants these unified)
- `.claude/state/` — **390 MB** across 60 entries (stale-state audit surface)

## Critical caveat (do not skip)
The **DEAD tier is NOT proof a skill is unused.** The classifier measures (a) reference-graph centrality and (b) git-commit mentions over 90 days. It does **not** measure actual invocation — and there is no reliable invocation data because the eval cadence had lapsed. A domain skill invoked *directly* by users (e.g. an engineering or email skill that nothing else cross-references) is indistinguishable from true dead weight under this heuristic.

Repo memory records the exact failure mode of acting on this kind of metric: *"subagent acceptance-metric drives signal deletion — fan-out agents over-removed chasing grep-empty, deleted a knowledge domain."* Mass-retiring 534 skills on a centrality heuristic would repeat it.

## Safe retirement methodology (proposed — needs a clean #3062 plan + approval)
1. **Archive, never delete.** Move retirement candidates to a single unified `_archive` (also resolves the two-archive-tree split). Reversible.
2. **Exclude direct-use domains.** Whitelist HOT-domain neighbours: engineering (orcaflex/aqwa/mooring/fatigue/hydrodynamics), email, data — DEAD skills *inside* an active domain are likely direct-use, not dead.
3. **Confirm zero-signal independently** per candidate: no cross-ref AND no git mention AND no invocation trace in session transcripts (the `~/.claude/projects` corpus) before archiving.
4. **Batch + verify each batch's artifact**, not the report — per the parallel-agent over-removal lesson.
5. **Verify eval-cadence machine coverage.** The cadence is running on canonical (telemetry was fresh as of 2026-06-14); confirm it covers all machines and that feature-branch checkouts don't mislead operators reading stale working copies (the trap this report initially fell into).

## Governance flags
- **#3062 approval drift:** carries `status:plan-approved` but has **no plan doc in `docs/plans/` and no `.planning/plan-approved/3062.md` marker**. Per `issue-planning-mode`, that's approval-state drift — not a clean approve-and-implement. A real plan should precede any deletion/archival.
- The telemetry refresh itself (this report's input) is operational/read-generating and safe; the *retirement* is the gated step.

## Recommended next step
Draft the #3062 implementation plan around the **safe methodology above** (archive-not-delete, domain whitelist, per-candidate zero-signal confirmation, eval-cadence restoration), run adversarial review, and surface for approval. Do not retire skills until then.
