# Design Spec — Cradle-to-Grave Engineering Flywheel

> **Date:** 2026-04-25
> **Status:** Brainstorm-validated. Captured for execution via aceengineer-strategy issue tree.
> **Parent epic:** [aceengineer-strategy #1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1)
> **Cross-repo governance:** issues live in `vamseeachanta/aceengineer-strategy` (private); plans, adversarial reviews, and approval markers live in `vamseeachanta/workspace-hub` per the `issue-planning-mode` skill.

---

## Vision

Build the offshore/marine engineering equivalent of an integrated operating system across the full design → construction → maintenance lifecycle. SemiAnalysis (semianalysis.com) provides the analogy for tiered open/closed publication and audience-building, but the architecture extends structurally: SemiAnalysis only observes its industry; we participate in offshore engineering. Participation lets us close a feedback loop they cannot.

## Operating Motto

> **The flywheel must continue. Loop velocity > revenue maximization.**

Locked 2026-04-25.

## Locked Policy: Public-by-Default with Client-Elective Privacy

- All work is public by default. Standards substrate, calculators, parametric outputs, anonymized failure entries, atlas results, loop-closure findings — all default to public release.
- Client opt-out is allowed for specific engagements / specific findings.
- Free-by-client-preference is acceptable. Any client may consume any subscription-tier service for free if it serves loop velocity.
- Revenue comes from **integration**, not exclusivity. We charge for: API access tiers + SLA, embedded engineering and advisory hours, custom calibrations, real-time copilot deployment. Reference comparable: HashiCorp / Cloudera / MongoDB open-core, not SemiAnalysis closed-data subscription.

## 7-Layer Architecture

| # | Layer | What it is | Existing asset |
|---|---|---|---|
| 1 | Codes & standards (LLM-wikis) | Queryable, versioned, cross-referenced standards substrate (DNV / API / ISO / ABS) | partial — content currently dispersed across `data/standards/`, `docs/standards/`, `knowledge/wikis/marine-engineering/`. Canonical durable home decision is upstream of workspace-hub #2471 (CSA Z276) and is the scope of [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4). |
| 2 | Program code | Engineering analysis libraries that cite (1) | `digitalmodel/` (OrcaFlex, OrcaWave, mooring, riser) — separate git repo |
| 3 | Parametric analysis | Precomputed reference scenarios across (2) | Solver queue + nightly batch (5 terminals) |
| 4 | Public datasets | Public calculators, browsers, atlas outputs (default-public) | `knowledge/seeds/mooring-failures-lng-terminals.yaml` and adjacent corpora; aceengineer-website |
| 5 | Custom client inputs | Site-specific client data (private only by client opt-out) | `client_projects/` (consulting only — not productized) |
| 6 | Real-time assistance | Live copilot for design/construction/maintenance | Greenfield |
| 7 | Feedback loop | Field measurements → atlas/code/standards updates; **public loop-closure log by default** | Unformalized |

## Recommended Wedge: Approach C — Mooring vertical end-to-end

Three approaches were considered and discarded:

- **Approach A — Standards-first.** Build the standards LLM-wiki to industrial grade first; the rest cascades. Strongest substrate; slowest to revenue; produces publisher-tier outcomes only.
- **Approach B — Calculators-first.** Ship 3–5 high-value public calculators fast for inbound velocity. Mirrors SemiAnalysis playbook closely; fastest visible momentum; still produces publisher-tier outcomes only.
- **Approach C — Closed loop on one vertical.** Build all 7 layers for a single narrow vertical (mooring), prove the loop closes, then replicate.

**Approach C selected** because A and B both produce publisher-tier outcomes (best case: SemiAnalysis-for-marine). C is the only approach that exercises layers 6 (real-time assistance) and 7 (feedback loop) where the structural moat lives.

**Mooring selected as wedge** because: (a) `digitalmodel` mooring code is mature, (b) `knowledge/seeds/` mooring corpus exists, (c) DNV-OS-E301 + API RP 2SK are well-bounded standards, (d) operators currently lack credible mooring-integrity intelligence product.

## Moat Thesis

The moat is the **loop**, not the data. With public-by-default policy, the data alone cannot be the moat — anyone can read it. The moat is:

1. **Loop velocity** — we run more cycles per quarter than anyone else because every public release feeds inbound, which feeds engagements, which feed measurements, which feed the loop.
2. **Operational integration** — real-time copilot, custom calibrations, embedded engineers, SLA-backed APIs are operational moats that competitors must build separately even if they can read our public data.
3. **Standards interpretation accumulation** — interpreting DNV-OS-E301 et al. correctly across hundreds of incident-grounded examples is a tacit-knowledge advantage that public data alone doesn't transfer.

A copycat reading our public corpus would still be 4–8 quarters behind on loop cycles.

## Issue Tree (created 2026-04-25 in aceengineer-strategy)

| Priority | Issues | Theme |
|---|---|---|
| Epic | [#1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1) | Cradle-to-grave engineering flywheel — strategic initiative |
| **P0** | [#2](https://github.com/vamseeachanta/aceengineer-strategy/issues/2), [#3](https://github.com/vamseeachanta/aceengineer-strategy/issues/3), [#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) | Foundation: wedge confirmation, ICP confirmation, standards canonical home + DNV-OS-E301/API RP 2SK populate |
| P1 | [#5](https://github.com/vamseeachanta/aceengineer-strategy/issues/5), [#6](https://github.com/vamseeachanta/aceengineer-strategy/issues/6) | Public layer / lead magnet: quick-screen calculator, full failure-case browser |
| P2 | [#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7), [#8](https://github.com/vamseeachanta/aceengineer-strategy/issues/8), [#9](https://github.com/vamseeachanta/aceengineer-strategy/issues/9), [#10](https://github.com/vamseeachanta/aceengineer-strategy/issues/10) | Paid integration tier + portfolio management |
| P3 | [#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11), [#12](https://github.com/vamseeachanta/aceengineer-strategy/issues/12), [#13](https://github.com/vamseeachanta/aceengineer-strategy/issues/13) | Loop closure / moat: anchor pilot, real-time copilot, feedback-loop pipeline + public log |
| P4 | [#14](https://github.com/vamseeachanta/aceengineer-strategy/issues/14) | Replication harness for riser + field-development verticals |

## P0 Plans Drafted (workspace-hub)

- [`docs/plans/2026-04-25-aces-2-flywheel-wedge-mooring.md`](../plans/2026-04-25-aces-2-flywheel-wedge-mooring.md) — T1, Claude r3 MINOR (patched), `status:plan-review`
- [`docs/plans/2026-04-25-aces-3-flywheel-icp.md`](../plans/2026-04-25-aces-3-flywheel-icp.md) — T1, Claude r3 MINOR (patched), `status:plan-review`
- [`docs/plans/2026-04-25-aces-4-flywheel-standards-canonical-home.md`](../plans/2026-04-25-aces-4-flywheel-standards-canonical-home.md) — T2, Claude v1 MAJOR → v2 MINOR (patched), `status:plan-review`

Adversarial review provenance: Claude single-author r3 with documented Codex unavailability (codex-cli 0.124.0 upstream regression — workspace-hub #2479) and Gemini deferred for these strategy/decision plans. Cross-provider review recommended for #4 once codex-cli regression resolves; until then, single-author r3 is the documented fallback per workspace-hub feedback memory `feedback_permission_gate_blocks_cross_review.md`.

## What's Next (User-Owned)

1. Review the three P0 plans above. Each is at `status:plan-review`.
2. Apply `status:plan-approved` to any/all that look right; create `.planning/plan-approved/aces-N.md` markers per the issue-planning-mode skill. **Do not delegate this approval to any agent** — the gate is intentionally user-only.
3. P1–P4 issues remain at `status:scoping`. Plans for those will be drafted in subsequent sessions, in priority order, only after the P0 wedge + ICP decisions are locked (since they cascade into every downstream plan's resource intelligence).

## Out of Scope (for now)

- Any work outside offshore/marine vertical
- LLM-wiki spinout (per workspace-hub project decision: stays embedded; #2398)
- Replication to risers / field-dev (deferred until mooring loop proves out — see [aces-#14](https://github.com/vamseeachanta/aceengineer-strategy/issues/14))

## Decision Log

- 2026-04-25 — User initially selected Option B (closed-data subscription as primary revenue) over A/C, then revised to **public-by-default open-core** policy after considering loop-velocity vs revenue-maximization tradeoff.
- 2026-04-25 — User selected Approach C (mooring-vertical wedge end-to-end) over A/B.
- 2026-04-25 — User confirmed `aceengineer-strategy` (private) as the issue tracker for this initiative.
- 2026-04-25 — User added portfolio management ([#10](https://github.com/vamseeachanta/aceengineer-strategy/issues/10)) for ongoing oversight.
- 2026-04-25 — Public-by-default policy locked. Operating motto: *the flywheel must continue*.
- 2026-04-25 — Factual correction. Earlier issue bodies referenced a sanctioned `llm-wiki/wiki/standards/` subtree that does not exist; workspace-hub #2471 is scoped to CSA Z276 routing only. [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) reframed as two-phase (decide canonical home → populate).
