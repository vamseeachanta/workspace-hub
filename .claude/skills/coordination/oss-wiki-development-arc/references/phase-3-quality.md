# Phase 3 — Quality

**Audit-version range observed in llm-wiki:** V15 → V17 (≈2 iters)
**Goal:** structural-quality verification and publication-readiness gating. The wiki has substrate (Phase 1) and depth (Phase 2); Phase 3 ensures it's defensible against external readers and tooling.

## When Applicable

Use Phase 3 when:

- Depth is saturated (Phase 2 exit criteria met — see `phase-2-depth.md`)
- Wiki is approaching public publication, syndication, or external citation
- Audit reports structural defects (orphans, unidirectional bridges, frontmatter drift) that depth-expansion didn't address
- A reviewer / consumer has flagged link-integrity or graph-structure issues

Phase 3 is **short** (2 iters in llm-wiki). It's not a perpetual grooming phase — it's a gate.

## The Diagnose-Then-Execute 2-Iter Cycle

Phase 3 has a distinctive iter shape: **diagnostic iter** produces reports; **execution iter** consumes the reports. This is unlike Phase 1 / Phase 2 where audit + content happen in the same iter.

```
iter-N (Phase 3 diagnostic) — produces reports
├── Lane A: Orphan-detection agent → docs/audits/W251-orphans.md
├── Lane B: Bridge-direction audit agent → docs/audits/W252-unidir-bridges.md
├── Lane C: Frontmatter-consistency agent → docs/audits/W253-frontmatter.md
└── Lane D: Link-integrity agent → docs/audits/W254-link-integrity.md

iter-N+1 (Phase 3 execution) — consumes reports
├── Lane A: Orphan-removal agent (reads W251) → fixes
├── Lane B: Bridge-reciprocation agent (reads W252) → adds reverse links
├── Lane C: Frontmatter-normalization agent (reads W253) → fixes
└── Lane D: Link-repair agent (reads W254) → fixes
```

(W251-W258 are the actual workitem labels llm-wiki used; substitute your project's tracking scheme.)

**Why split into 2 iters:**

- Diagnostic agents need read-only access to the full graph. Execution agents need write access.
- Diagnostic reports are durable artifacts (cite-able in publication notes).
- Execution agents have explicit, auditable input (the report) — easier to verify they did the right thing.
- Race-management: diagnostic iter is fully parallel-safe (read-only). Execution iter often touches overlapping link-graph state and benefits from sequenced commits or worktree isolation.

## The 4-Criterion Publication-Readiness Gate

Phase 3 is **complete** when all four pass simultaneously in a single audit cycle:

### 1. Orphans ≤ 3

An "orphan" is a page with zero inbound links from anywhere in the wiki ecosystem. Some are legitimate (deliberate landing pages, root index pages) — hence the threshold of 3 rather than 0. More than 3 orphans signals navigation gaps.

Detection: build the link graph; find nodes with in-degree 0; subtract whitelisted root pages.

### 2. Unidirectional Bridges = 0

A "unidirectional bridge" is a cross-wiki link from page A (in wiki X) to page B (in wiki Y) where B does not link back to A. Cross-wiki bridges should be reciprocated — each side should mention the other.

Why zero (strict): a unidir-bridge means one wiki's reader can navigate to the sister wiki, but a sister-wiki reader can't navigate back. This breaks the cross-wiki value proposition.

Detection: for each cross-wiki link (A→B), check if B contains a link to A. Report all that don't.

### 3. Frontmatter Consistency

Every page has the expected frontmatter fields populated correctly:

- `code_id` (if applicable — standards/codes pages)
- `publisher`
- `revision`
- (project-specific fields per `.claude/rules/calc-citation-contract.md`)

A "consistency violation" is a missing required field, a malformed value, or a value-pattern that doesn't match the project's frontmatter schema.

Detection: schema-validate every page's frontmatter. Report violations.

### 4. Link Integrity ≥ 99%

Internal links resolve to existing pages; external links return 200 OK (sampled). Below 99% means broken citations are common enough that a reader will hit one in normal browsing.

Detection: parse all links; resolve internal targets against page index; HTTP-HEAD external links (rate-limited).

## Iter-Shape Recipe (Phase 3)

Both diagnostic and execution iters use 4-agent fanout. Diagnostic is parallel-safe by construction (read-only). Execution requires care:

- If two execution agents target the same file, sequence them or use worktrees
- If unidir-bridge-fixes (Lane B) need to add links to pages that orphan-removal (Lane A) is also editing, run A then B sequentially within a single agent
- See `iter-shape-recipes.md` for the W231 race-block lesson

## Saturation Signal — When to Publish

Phase 3 is **done** (and the wiki is publish-ready) when:

- All 4 closure criteria green simultaneously across 1 audit cycle
- Frontmatter mismatch count = 0
- unidir-bridges = 0
- orphans ≤ 3
- link-integrity ≥ 99%
- Diagnostic reports show no new issues (delta vs prior diagnostic iter is empty)

At this point, additional Phase 3 iters yield no measurable value. Publish, then resume Phase 1 or Phase 2 work as new gaps emerge.

## Common Phase-3 Anti-Patterns

- **Single-iter Phase 3** — trying to diagnose + fix in one iter conflates read-only and write operations; race conflicts dominate
- **Diagnostic-only Phase 3** — producing reports without execution iter to consume them; reports go stale within ~3 substrate iters
- **Threshold-relaxation** — declaring "orphans ≤ 10" or "link-integrity ≥ 95%" to pass the gate; the thresholds are calibrated to publication-readiness, not aspirational
- **Skipping the audit cycle that confirms 4-criterion green** — execution iter completion ≠ gate-pass; verify with a fresh diagnostic iter

## Reference Exemplar

llm-wiki audit docs `V15.md` through `V17.md` document the diagnose-then-execute cycle. W251-W258 work-items show the report → execution split.
