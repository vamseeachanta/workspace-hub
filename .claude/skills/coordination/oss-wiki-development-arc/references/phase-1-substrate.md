# Phase 1 — Substrate

**Audit-version range observed in llm-wiki:** V1 → V11 (≈27 iters)
**Goal:** every canonical concept has a resolver page; every named entity has a stub; every concept page can be cited without producing a broken link.

## When Applicable

Use Phase 1 when **any** of the following holds:

- New wiki bootstrap (zero or near-zero pages)
- Concept-page coverage of the canonical taxonomy is <70%
- Cross-wiki bridge density is sparse (multiple wikis exist but they don't reference each other meaningfully)
- A representative concept-page citation chain has ≥1 broken hop (page → resolver missing)
- Audit reports a "substrate-gap-cluster" — a topical region where most expected pages are absent

If none of these hold, skip to Phase 2 (depth).

## Iter-Shape Recipe — 4-Agent Fanout

Each Phase-1 iter is a single audit + parallel content lanes. **4-agent fanout** is the default: it dominates solo-author iters by ~3x throughput while keeping race-management tractable.

```
iter-N
├── Lane A: Audit agent (1)
│   └── Produces docs/audits/V<N>.md
│       — measures substrate state, identifies gaps, recommends iter-N+1 lanes
├── Lane B: Resolver-fill agent (1)
│   └── Creates / fleshes out resolver pages identified in V<N-1>
├── Lane C: Concept-page-creation agent (1)
│   └── Creates new concept pages in identified gap-clusters
├── Lane D: Cross-wiki bridge agent (1)
│   └── Adds substantive bridges between sibling wikis
│       (see references/cross-wiki-bridges.md)
```

**Variation by iter:** sometimes 2 content lanes (B+C bundled when gap-cluster overlaps), sometimes 3 (split B into resolver-pages + entity-stubs). Audit + bridge are constant.

**Why parallel works in Phase 1:** content lanes operate on disjoint files (different wikis, different topical regions). Race conflicts are rare. Compare to Phase 3 where lanes intentionally touch overlapping link-graph state and sequentialization matters.

## Audit Dimensions (Phase 1)

The Phase-1 audit measures:

1. **Coverage breadth** — concept-page count vs. canonical taxonomy expectation, per-wiki
2. **Cross-wiki edge density** — count of inter-wiki links / total link count
3. **Substrate-gap-cluster identification** — which topical sub-trees are <50% covered
4. **Resolver-page coverage** — for each ambiguous term, does a resolver page exist that disambiguates and routes to the canonical concept page
5. **Entity-stub coverage** — every named incident, person, vessel, project mentioned ≥3 times has at least a stub page

These five dimensions are reported in the audit doc (see `audit-template.md`). Iter-N+1 lanes are explicitly assigned to close the largest-gap dimension.

## Substrate-Completeness Validation

Validation is not "did we add N pages this iter" — that's input metric. Validation is:

- **Citation-chain integrity**: pick 5 random concept pages; trace every outbound cross-wiki link; count broken hops. Target: 0 broken hops in the sampled set.
- **Resolver-routing**: pick 5 random ambiguous terms; verify a resolver page exists and routes correctly. Target: 5/5.
- **Entity reachability**: pick 5 named entities mentioned in concept pages; verify each has at least a stub. Target: 5/5.

If any validation drops below 4/5, run another substrate iter targeting that dimension.

## Saturation Signal — When to Transition to Phase 2

Phase 1 is **complete** when the audit reports:

- Substrate-fill marginal-cost > marginal-value (V11 in llm-wiki — declared explicitly by V11 audit)
- <3 high-value gaps remain per wiki
- Cross-wiki edge density has plateaued (last 2 iters added <5% edge growth)
- Resolver-coverage ≥95% on canonical concept set
- Top-N citation candidates are now mostly thin pages (under-developed) rather than missing pages

When all five fire, the next iter's value is in Phase 2 (depth-expansion of the top-cited thin pages), not Phase 1 (more substrate).

## Common Phase-1 Anti-Patterns

- **Depth-expanding before substrate saturated** — adds 4-element-recipe content that references resolvers that don't exist yet. The cross-links don't compound; you'll redo the work.
- **Bridge-only iters** — bridges added without substrate underneath produce sister-pages that link to stubs. Bridge construction needs substrate on both sides.
- **Audit-skip iters** — skipping the audit lane to "do more content" causes the next iter to mis-target gap-clusters. Always run the audit lane.
- **Solo-author Phase-1** — single-agent substrate-fill is the dominant low-throughput pattern from llm-wiki V1-V8. 4-agent fanout from iter-1 saves ~10 iters of catch-up.

## Reference Exemplar

llm-wiki audit docs `V1.md` through `V11.md` show this phase's progression. V11 is the explicit substrate-saturation declaration.
