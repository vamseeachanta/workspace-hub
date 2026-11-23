# Audit-Doc Template

The audit-iter is the first lane of every iter across all 3 phases. It produces a durable artifact (`docs/audits/V<N>.md`) that the next iter's content lanes consume.

## Audit-Iter Recipe

```
iter-N audit team
├── 1 audit agent (read-only across full wiki ecosystem)
└── 3 content agents (read-write, scoped to their lanes)
```

The audit agent runs first and produces V<N>.md. The content agents start once V<N>.md is committed (or, for parallel iters, consume V<N-1>.md while audit produces V<N>).

## Audit Doc Structure

A well-formed audit doc has these sections in order:

### 1. Executive Summary (≤200 words)

The single most important section. A reader who only reads the executive summary should know:

- What state the wiki is in (which phase, how saturated)
- What the largest gap is
- What iter-N+1 should do
- Whether a phase-transition is recommended

### 2. State Change Since Prior Audit

Numerical deltas:

- Pages added / removed
- Lines added / removed
- Links added / removed
- New entities, new resolvers, new bridges
- Frontmatter coverage delta

This makes the audit doc **comparable across versions** — a reader of V13.md can quickly scan back to V12.md and see what changed.

### 3. Wiki-by-Wiki State

For each wiki in the ecosystem (engineering, marine, naval, etc.), report:

- Page count + line count
- Phase classification (substrate / depth / quality)
- Top 3 strengths
- Top 3 gaps
- Cross-wiki edges in/out

### 4. Cross-Wiki Bridge Report

- Total bridge count
- Bidirectional count (and ratio — should approach 100% by Phase 3)
- New bridges this iter
- Recommended bridge targets for iter-N+1

### 5. Phase-Specific Metrics

Phase 1: substrate-completeness dimensions (see `phase-1-substrate.md`)
Phase 2: top-N inbound-citation rankings + cohort distribution + 4-element completion rates
Phase 3: 4-criterion closure measurements + diagnostic deltas

### 6. Iter-N+1 Recommendation

Concrete lane assignments:

- Lane B: <agent role> → <pages or topics>
- Lane C: <agent role> → <pages or topics>
- Lane D: <agent role> → <pages or topics>

Each lane has a measurable success criterion that the next audit will verify.

## Per-Audit-Version Measurement-Discipline Progression

Empirically observed in llm-wiki V1 → V17. Each audit version added measurement rigor; copying this progression into a new wiki saves ~10 iters of audit-format churn.

| Version range | Measurement-discipline level | What it added |
|---------------|------------------------------|---------------|
| V1-V3 | Prose-only | Free-text observations; no quantitative state |
| V4-V6 | Counts | Page counts, line counts, link counts |
| V7-V9 | Deltas | Counts + state-change vs prior audit |
| V10-V11 | Per-wiki breakdown | Counts split by wiki within ecosystem |
| V12-V13 | Inbound-citation rankings | Top-N most-cited pages identified for depth-targeting |
| V14-V15 | Cohort analysis | Pages grouped by cohort (thin-starter / mid-tier / already-expanded) |
| V16-V17 | 4-criterion closure measurements | Orphans, unidir-bridges, frontmatter-consistency, link-integrity |

**Pre-load all 7 levels from iter-1** in a new wiki. The audit doc template should have placeholder sections for every measurement type. They start empty and fill in as the wiki grows — but the section headers are baked.

## Audit-Doc Review Checklist

Before committing V<N>.md, verify:

- [ ] Executive summary has all 4 required points (state, largest gap, iter-N+1 ask, transition recommendation)
- [ ] State-change section has numerical deltas (not prose)
- [ ] Every wiki in the ecosystem has its own subsection
- [ ] Cross-wiki bridge ratio is reported even if 0
- [ ] Phase-specific metrics match the current phase (don't report Phase-3 metrics during Phase 1)
- [ ] Iter-N+1 recommendation has concrete lane assignments with measurable success criteria
- [ ] Doc is self-contained — a reader who hasn't seen V<N-1>.md can still understand current state

## Common Audit-Doc Anti-Patterns

- **Audit-as-content-summary** — describes what content lanes did, doesn't measure state. Audit is forward-looking; content-summaries are backward-looking.
- **Audit without recommendation** — "here's the state" with no iter-N+1 lane assignments forces the next iter's planning to redo audit work
- **Skipping deltas** — without state-change deltas, the audit lineage is uncomparable. Every audit MUST report deltas vs prior.
- **Inconsistent phase classification** — claiming Phase-2 metrics matter while still in Phase-1; pick a phase per audit and report its metrics.

## Reference Exemplar

llm-wiki audit lineage at `docs/audits/V1.md` through `V17.md`. V12 is the inflection where measurement-discipline shifted from substrate counts to depth metrics. V15 introduces 4-criterion measurements.
