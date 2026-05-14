---
name: production-engineering-corpus-initiative
description: 2026-05-13 founding of the 10th llm-wiki domain (production-engineering) as the production-side complement to drilling-engineering; triggered by scope-edge note on drilling-engineering/concepts/artificial-lift-method-selection.md
metadata: 
  node_type: memory
  type: project
  originSessionId: 72238262-9b25-493d-9731-fc22b67185aa
---

`production-engineering/` is the **10th wiki domain** in `vamseeachanta/llm-wiki`, founded 2026-05-13 in commit [`7dc802d1`](https://github.com/vamseeachanta/llm-wiki/commit/7dc802d1). Founding-trigger anchor: scope-edge note on drilling-engineering's `concepts/artificial-lift-method-selection.md` which explicitly anticipated this domain founding. Bidirectional cross-link closed in commit [`f78ee76e`](https://github.com/vamseeachanta/llm-wiki) (or successor — drilling-engineering scope-edge note updated to remove the "if/when... future" hypothetical and point at the now-founded domain).

**Why:** the user's directive "continue with next session candidates" (2026-05-13 after Phase 2 drilling-engineering closeout) authorized expanding the upstream value-chain coverage in llm-wiki. drilling-engineering + production-engineering together cover well construction → production handover. The scope-split decision was already documented in drilling-engineering Phase 1: rod-pump stays in drilling per API "drilling and well servicing" umbrella; other 4 lift methods (ESP, gas lift, PCP, plunger lift) plus completions / stimulation / production operations / well-integrity-during-production go to production-engineering.

**Founding state.** Repo layout: `wikis/production-engineering/{CLAUDE.md, raw/, wiki/{overview.md, index.md, log.md, concepts/artificial-lift-overview.md}}`. page_count=1, source_count=0 (no external founding source like Papkov for drilling-engineering — trigger was internal cross-wiki structural completeness, not an external LinkedIn post).

**How to apply:**

1. **Seed roadmap captured in [overview.md](https://github.com/vamseeachanta/llm-wiki/blob/main/wikis/production-engineering/wiki/overview.md)** — 4 phases scoped at founding-time:
   - **Phase 1**: artificial-lift family expansion (ESP / gas lift / PCP / plunger lift / jet pump / hydraulic lift deep pages plus API RP 11S, 11V6 standards)
   - **Phase 2**: completions (perforating, sand control, multi-zone, smart completions)
   - **Phase 3**: stimulation (matrix acid, hydraulic fracturing, refrac)
   - **Phase 4**: production operations and well integrity (flow assurance, choke management, integrity monitoring)
2. **Founding concept anchor**: `concepts/artificial-lift-overview.md` is the production-engineering-side counterpart to drilling-engineering's `artificial-lift-method-selection.md`. Together they form the bidirectional cross-link the original scope-edge note had been anticipating. The page covers six lift-method families with production-engineering framing (lifecycle-aware, field-mix-aware).
3. **Rod-pump scope-split is operational**: rod-pump deep pages (sucker-rod-pumping-overview, api-11ax-pump-designation, api-11l-design-charts, pump-cards-and-dynamometer, sucker-rods-and-tapered-strings) stay in `drilling-engineering/wiki/concepts/`. Production-engineering's artificial-lift-overview.md cross-links to them rather than duplicating.
4. **Cross-wiki anchors** declared in CLAUDE.md and overview.md:
   - `drilling-engineering` — well-construction handover boundary; founding-trigger anchor
   - `naval-architecture` — FPSO host platforms; topside coupling at wellhead boundary
   - `marine-engineering` — offshore-marine production-vessel operations
   - `engineering-standards` — API 11/14/17 series (artificial lift / production facilities / subsea production systems)
   - `asset-management` — well-integrity-during-production overlap
5. **V18 anti-rec #8 override**: 10th wiki creation under explicit user signal (same logic as drilling-engineering 9th-wiki founding). V19 audit (2026-06-09) accounting must reflect TWO new domains, not one.

**Cross-references:**

- `project_drilling_engineering_corpus_initiative.md` — sibling 9th-wiki founding earlier same day; the page that triggered this one
- `project_llm_wiki_external_post_ingest_workflow.md` — the per-ingest workflow that will execute future Phase 1-4 ingests
- `project_llm_wiki_strategic_role.md` — strategic frame; coverage gaps are first-class defects
- `project_llm_wiki_spunout.md` — repo location, license boundary; domain count now 10 (was 9 after drilling-engineering founding)
