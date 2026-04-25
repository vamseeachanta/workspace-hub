# Flywheel P0 Decision Panel — Single-Pass Approval Surface

> **Date:** 2026-04-25
> **Purpose:** Consolidate the 5 user-input questions across the three P0 plans into one place, with recommended answers, so the user can resolve all three plans in a single review pass.
> **Parent epic:** [aceengineer-strategy #1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1)

---

## Why This Exists

The three P0 plans ([aces-#2](https://github.com/vamseeachanta/aceengineer-strategy/issues/2), [aces-#3](https://github.com/vamseeachanta/aceengineer-strategy/issues/3), [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4)) each defer some content to user input. Reading three plan files to extract five questions is friction. This panel collapses that friction: read one document, reply to five rows, all three P0 plans become approval-ready (or revisable based on your answers).

This document is **not** an approval mechanism. The user-only `status:plan-approved` gate per epic #1 still applies. This panel just collects answers; once you approve, the answers populate the plans and you apply `status:plan-approved` per the issue-planning-mode skill.

---

## The Five Decisions

| # | Issue | Section | Question | Recommended answer | Rationale | Your answer |
|---|---|---|---|---|---|---|
| 1 | [#2](https://github.com/vamseeachanta/aceengineer-strategy/issues/2) | §Decision Content #4 | Mooring wedge time horizon before considering vertical-2 | **18 months** | Plan body specifies 12–18mo range; 18mo gives meaningful loop cycles (≥3 quarterly cycles after first anchor pilot lands) without being indefinite. 12mo too tight given anchor-pilot procurement cycle. 24mo risks losing momentum. | _____ |
| 2 | [#2](https://github.com/vamseeachanta/aceengineer-strategy/issues/2) | §Decision Content #6 | Rollback gate type when triggers fire | **soft** (checkpoint) | A "hard" rollback forces a wedge change without context-aware judgment. A "soft" checkpoint forces the explicit review (per the rollback procedure (i)/(ii)/(iii) added in the v2 patch) but lets you accept context that justifies continuing. The procedure requirement is the actual discipline; the gate type just controls automaticity. | _____ |
| 3 | [#3](https://github.com/vamseeachanta/aceengineer-strategy/issues/3) | §Decision Content #1 | Primary ICP for v1 paid integration tier | **A — Operators** | Best fit with mooring wedge: operators own the FPSOs/spread-mooring assets, generate the telemetry that closes the loop ([#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11)), and have the dollar-value to support institutional pricing. EPCs (B) are second-best but their bid-cycle data is harder to feed back. C and D are downstream segments. | _____ |
| 4 | [#3](https://github.com/vamseeachanta/aceengineer-strategy/issues/3) | §Decision Content #3 | Named anchor accounts (3–5) | **Cannot recommend** — depends on your existing AceEngineer relationship strength | Per [#9](https://github.com/vamseeachanta/aceengineer-strategy/issues/11) plan, the anchor pilot is the keystone of layers 6 and 7. Account selection should be: 2–3 with strongest existing AceEngineer relationship + 1–2 strategic stretch (industry leaders whose endorsement compounds inbound). Name them and we proceed. | _____ |
| 5 | [#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) | §License-Class Frontmatter Field | Standards-text licensing posture for DNV/API public publication | **`summary-only-with-citation` as default + engage outside counsel before broad rollout beyond DNV-OS-E301 + API RP 2SK seed** | The v2 patch already encoded `summary-only-with-citation` as the default for copyrighted standards. The only open decision is whether to engage outside counsel proactively (recommended) before populating beyond the wedge-pair, or wait until publication challenge. Outside-counsel-first is cheaper than litigation-first. | _____ |

---

## How to Reply

Either:

**A. Accept recommendations + name accounts.** Reply with:
> ```
> 1: 18mo
> 2: soft
> 3: A
> 4: <Account 1>, <Account 2>, <Account 3>[, <Account 4>, <Account 5>]
> 5: agree (engage counsel first)
> ```

**B. Override any subset.** Reply with `1: <answer>` lines for whichever rows you want to change. Unspecified rows default to the recommendation.

**C. Defer any subset.** Reply with `defer 4` (or similar) for any row that needs more thought. Plans with deferred fields stay at `status:plan-review` for those specific items.

---

## What Happens After You Reply

1. Each plan's user-input section gets populated with your answer.
2. The corresponding decision artifact (`docs/governance/flywheel-{wedge,icp,offshore-marine-standards-canonical-home}-decision.md`) gets drafted using the locked answer.
3. Plans move to `status:plan-approved` *only via your label action* — I do not self-label.
4. P1 issue planning ([aces-#5](https://github.com/vamseeachanta/aceengineer-strategy/issues/5), [aces-#6](https://github.com/vamseeachanta/aceengineer-strategy/issues/6)) can then begin since the wedge + ICP decisions cascade into their resource intelligence.

---

## Provenance

- 2026-04-25 brainstorm session (this file's commit history is authoritative)
- Companion design spec: [`2026-04-25-cradle-to-grave-engineering-flywheel-design.md`](./2026-04-25-cradle-to-grave-engineering-flywheel-design.md)
- The five questions are extracted verbatim or near-verbatim from the §Open Questions sections of the three P0 plan files; recommendations reflect plan-internal logic.
