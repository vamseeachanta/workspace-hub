---
name: oss-wiki-development-arc
description: Three-phase methodology (Substrate → Depth → Quality) for building open-source engineering wikis efficiently. Skip 70%+ of empirical iteration cost by pre-loading the pattern.
version: 1.0.0
author: Workspace Hub
category: coordination
tags: [wiki, methodology, oss, content-development, llm-wiki, multi-agent]
related_skills:
  - engineering-issue-workflow
  - artifact-verification
---

# OSS-Wiki Development Arc — Three-Phase Methodology

**Empirical basis:** Traced across 38 iterations of [llm-wiki](https://github.com/vamseeachanta/llm-wiki) (iter-22 → iter-59, V1 → V17 audit lineage). Phases were observed, not designed; this skill codifies them so future wiki projects can pre-load the pattern.

## The 3-Phase Pattern

| Phase | Audit-version range | Iters observed | Marginal-cost signature | Exit criterion |
|-------|--------------------|----------------|------------------------|----------------|
| **1. Substrate** | V1 → V11 | ~27 | Cheap breadth wins | substrate-fill marginal-cost > marginal-value |
| **2. Depth** | V12 → V15 | ~7 | Compounding per-page value via 4-element recipe | median per-iter line-growth <50% + thin-starter cohort exhausted |
| **3. Quality** | V15 → V17 | ~2 | Diagnose-then-execute closure | 4-criterion publication-readiness gate met |

Each phase has a distinct iter-shape, distinct success metric, and distinct saturation signal. Mixing phases (e.g., depth-expanding while substrate is incomplete) wastes effort because depth-content depends on substrate-resolvers being citable.

## When To Use This Skill

- Bootstrapping a new engineering/marine/scientific OSS wiki (greenfield)
- Resuming work on a stalled wiki (which phase are we in?)
- Diagnosing wiki-development thrash ("we keep adding pages but nothing improves")
- Auditing a wiki for publication readiness

## When NOT To Use

- Closed/internal documentation projects (audit-trail, governance constraints differ)
- Single-page reference docs (no substrate/depth/quality distinction)
- Wikis whose authoritative content is mirrored from elsewhere (use sync tooling, not this arc)

## Phase Invocation

Read the phase-specific reference before kicking off iter-N+1. Each reference is self-contained — a future agent can apply it without reading the others.

- **Phase 1 — Substrate:** `references/phase-1-substrate.md`
  - 4-agent fanout (audit + 2-3 content lanes + bridge)
  - Goal: every concept page links to a resolver page; every entity has a stub; substrate-completeness measured per-wiki
- **Phase 2 — Depth:** `references/phase-2-depth.md`
  - Top-N inbound-citation candidate selection
  - 4-element recipe per expanded page (worked example + comparison table + ≥30 outbound intra-wiki links + cross-link to entity/source)
  - 3-cohort growth-profile (thin-starter +200-300% / mid-tier +100-130% / already-expanded +35-50%)
- **Phase 3 — Quality:** `references/phase-3-quality.md`
  - Diagnose-then-execute 2-iter cycle
  - 4-criterion gate: orphans ≤3 + unidir-bridges=0 + frontmatter consistency + link-integrity ≥99%

Supporting references applicable to all phases:

- `references/audit-template.md` — audit-doc structure + V1→V17 measurement-discipline progression
- `references/iter-shape-recipes.md` — 4-agent fanout default; bundled-sequential exception (W231 race-block lesson)
- `references/cross-wiki-bridges.md` — sister-pair pattern; sibling-template recognition; substantive (not "see also") bridge content

## Saturation-Detection Signals

Before kicking off another iter in the current phase, verify the saturation signal hasn't fired:

| Phase 1 → 2 transition | Phase 2 → 3 transition | Phase 3 → publish |
|------------------------|------------------------|-------------------|
| Substrate-fill audit identifies <3 high-value gaps per wiki | Median per-iter line-growth across top-N pages drops <50% | All 4 closure criteria green simultaneously across 1 audit cycle |
| Cross-wiki edge-density plateaus | Thin-starter cohort exhausted (no <100-line top-citation pages remain) | Frontmatter mismatch count = 0 |
| Resolver-coverage ≥95% on canonical concept set | Already-expanded cohort dominates the next-target list | unidir-bridges = 0 (every cross-wiki link is reciprocated) |

If a saturation signal fires while in-phase, **transition** rather than spend another substrate-iter or depth-iter; the marginal value has collapsed.

## Reference Exemplar

[vamseeachanta/llm-wiki](https://github.com/vamseeachanta/llm-wiki) — public OSS wiki where this arc was empirically traced. Repository structure, audit-doc lineage (`docs/audits/V1.md` … `V17.md`), and iter-shape decisions are all visible.

## Critical Cost-Avoidance

A future wiki using this skill should:

1. Start with the **audit-doc skeleton** (see `audit-template.md`) on iter-1, not iter-15. Most of llm-wiki's measurement-discipline gain happened V12→V15; loading it pre-baked saves ~10 iters of audit-format churn.
2. Adopt the **4-agent fanout default** from iter-1. Solo-author iters were the dominant low-throughput pattern in llm-wiki's V1-V8.
3. Track **inbound-citation count per page** from iter-1 (substrate-phase metric is just count; depth-phase ranks by it). This avoids retroactive instrumentation.
4. Resist the urge to depth-expand before substrate is saturated. Depth-content references resolvers; if resolvers are stubs, the cross-links don't compound.
