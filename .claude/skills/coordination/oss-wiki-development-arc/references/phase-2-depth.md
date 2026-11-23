# Phase 2 — Depth

**Audit-version range observed in llm-wiki:** V12 → V15 (≈7 iters)
**Goal:** transform high-citation thin pages into doctrinally-distinctive content. This is where the wiki acquires value-density that competing references (textbooks, vendor docs, Wikipedia) lack.

## When Applicable

Use Phase 2 when:

- Substrate is saturated (Phase 1 exit criteria met — see `phase-1-substrate.md`)
- High-inbound-citation pages exist but are <300 lines / lack worked examples
- The wiki has breadth but reviewers note it "reads like an outline"
- Audit identifies a "thin-starter cohort" — pages with high inbound-citation count and low line count

If substrate is incomplete, **do not start Phase 2**. Depth-content references resolvers; depth-expanding before resolvers exist is wasted work.

## Top-N Inbound-Citation Candidate Selection

Phase 2's value comes from prioritizing pages with high inbound-link count. Process:

1. Compute inbound-citation count for every page (in-wiki + cross-wiki).
2. Sort descending; take top-N (llm-wiki used N=10-15 per iter).
3. Filter: keep only pages where current line-count is below the cohort target (see growth-profile below).
4. Assign 1 expansion-agent per ~3 pages. With 4-agent fanout, that's ~12 pages per iter.

Inbound-citation count is the right signal because each citation is a reader who will land on the page. Expanding low-citation pages is low-leverage even if they're long.

## The 4-Element Recipe (Doctrinally Distinctive Content)

Every depth-expanded page must include these four elements. This is the doctrinally-distinctive shape that makes the wiki citable rather than reference-equivalent:

### 1. Worked-example named-incident

A real, named incident or case study with quantitative detail. Not a hypothetical. Examples (engineering wiki):

- "1980 Alexander L. Kielland capsize: 5-leg semi-submersible, fatigue failure at brace D-6 weld..."
- "2020 Sherwood naval-architecture review of fast-ferry hull: GZ curve at 25° heel showed..."

The incident grounds the concept in defensible engineering reality. It's also a natural cross-link target (the named-incident gets its own entity page in Phase 1, and depth-pages link back).

### 2. Multi-criteria comparison table

A table comparing alternatives, methods, or codes across ≥3 axes. This is the content that's hardest to find elsewhere because vendor docs only cover their option and textbooks treat methods sequentially without side-by-side comparison.

### 3. Intra-wiki link enrichment ≥30 outbound

Every depth-expanded page must have ≥30 outbound intra-wiki links. This is the threshold at which the page becomes a hub-node in the wiki graph. Below ~20 links, the page is a leaf; above ~30, it actively routes readers to neighboring concepts.

### 4. Cross-link to entity page + source page

At least one outbound link to a named-entity page (the incident from element 1) and at least one to a source/standards page (the code or paper that grounds the comparison from element 2). This pulls the page into the cross-wiki graph and makes it citable from sister wikis.

**A page lacking any of the 4 elements has not been depth-expanded** — it's been edited. Track the four-element-completion rate per iter.

## 3-Cohort Growth Profile

Empirically observed in llm-wiki V12-V15 across the depth-pilot pages:

| Cohort | Starting line count | Post-expansion growth | Notes |
|--------|--------------------|-----------------------|-------|
| **Thin-starter** | <100 lines | +200% to +300% | Highest leverage; 4-element recipe applied to near-blank canvas |
| **Mid-tier** | 100-300 lines | +100% to +130% | Moderate leverage; usually need to add worked-example + comparison table |
| **Already-expanded** | >300 lines | +35% to +50% | Lowest leverage; usually only missing 30-link threshold or cross-link |

Use this profile to:

1. **Set per-page expansion targets** — don't ask a thin-starter to grow only 50%; don't expect already-expanded to triple.
2. **Detect anomalies** — a thin-starter growing only 50% suggests the agent didn't apply the full 4-element recipe.
3. **Predict iter cost** — an iter targeting 12 thin-starters costs more agent-time than 12 already-expanded.

## Iter-Shape Recipe (Phase 2)

```
iter-N (Phase 2)
├── Lane A: Audit agent (1)
│   └── Reports inbound-citation rankings + cohort distribution
│       + 4-element-completion rates from prior iter
├── Lanes B-D: Depth-expansion agents (3)
│   └── Each takes ~3-4 pages from the prioritized list
│       Each page gets full 4-element recipe applied
```

Same 4-agent fanout as Phase 1, but content lanes are depth-expansion rather than substrate-fill. Race-management is similar — depth-pages on different topics rarely conflict.

## Saturation Signal — When to Transition to Phase 3

Phase 2 is **complete** when:

- Median per-iter line-growth across top-N pages drops below 50%
- Thin-starter cohort exhausted (no <100-line top-citation pages remain)
- Already-expanded cohort dominates the next-target list (signaling diminishing returns)
- 4-element-completion rate plateaus at ≥90% across the top-50 cited pages

When these fire, the next iter's value is in Phase 3 (structural quality verification), not another depth iter.

## Common Phase-2 Anti-Patterns

- **Skipping the worked-example element** — agents default to abstract description; the named-incident is the load-bearing differentiator
- **Padding for line count** — depth-expansion measured by 4-element completion, not lines added
- **Targeting already-expanded pages first** — they have the worst leverage; sort by inbound-citation × (1 - completion-fraction)
- **Depth-expanding orphans** — a page with zero inbound citations gets zero readers; fix the orphan in Phase 3 first or expand a different page

## Reference Exemplar

llm-wiki audit docs `V12.md` through `V15.md` show the depth-pilot progression. The 4-element recipe was extracted from V13's pattern-recognition across the first depth iter's outputs.
