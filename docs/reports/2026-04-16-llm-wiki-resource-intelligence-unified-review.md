# LLM-Wiki + Resource/Document Intelligence: Unified Review

> **Date:** 2026-04-16
> **Scope:** All GitHub issues, codebase state, and industry research for the llm-wiki and resource/document intelligence ecosystem
> **Purpose:** Improve llm-wiki knowledge usage and group it with the entire resource/document intelligence system
> **Method:** 4 parallel research agents (GitHub issues, codebase x2, online research) + document analysis

---

## 1. Executive Summary

The workspace-hub intelligence ecosystem has **three systems** that evolved semi-independently over 10 days (since 2026-04-06):

| System | Scale | Maturity |
|--------|-------|----------|
| **LLM-Wiki** (L3 Durable Knowledge) | 19,325+ pages across 5 domains | Production — ingest, search, lint, cron all working |
| **Document Intelligence** (L1-L2 Pipeline) | 1M+ index records, 425 standards, 38K conference papers | Production — Phase A/B/C pipeline operational |
| **Resource Intelligence** (L2 Registries) | 247 online resources, mounted source registry | Early — registry exists but download/cross-ref unbuilt |

A normative 6-layer pyramid architecture (#2205) governs them, with three approved child policies (#2206, #2207, #2209). **The architecture is sound.** The gaps are in the **connective tissue** between layers:

- **Cross-wiki linking** (0 of 4 issues done) — the knowledge graph glue is unbuilt
- **Agent auto-search** (#2123) — agents can't query wiki at runtime
- **Unified registry convergence** — `doc_key` lookup model exists in design but not implementation
- **Nightly ingest reliability** (#2293) — idempotency bug undermines trust
- **647K unknown content_type** (#1878) — L2 registry has major metadata gap

---

## 2. Current State by Pyramid Layer

### L1 — Source Documents (Raw files)
**Status: Strong foundation, expanding**

| Source | Scale | Coverage |
|--------|-------|----------|
| `/mnt/ace` standards | 3.6M+ files across 4 mount points | Indexed |
| Conference papers | 38,526 across 30 collections | Phase A indexed, Phase B 62% summarized |
| DDE remote drive | 14.6 GB / 5,456 PDFs | Indexed |
| Online resources | 247 tracked in registry | Metadata only |
| Knowledge seeds | 6 YAML files (mooring failures, career, maritime law) | Fully ingested |
| Dark intelligence (Excel) | 6 xlsx extractions | Ingested |

### L2 — Registry / Provenance
**Status: Large but has a critical metadata bug**

| Registry | Records | Health |
|----------|---------|--------|
| `index.jsonl` (master) | 1,033,933 | 647K records with `unknown` content_type (#1878) |
| `conference-index.jsonl` | 38,526 | Healthy |
| `standards-transfer-ledger.yaml` | 425+ standards | 6.8% marked as read |
| `mounted-source-registry.yaml` | Multi-mount tracking | Operational |
| `online-resource-registry.yaml` | 247 resources | Metadata only, no download pipeline |
| `intelligence-accessibility-registry.yaml` | 26+ assets | Operational |

**Key gap:** The `doc_key`-based unified lookup model (#2207) is defined in the provenance contract but not yet implemented as a queryable service.

### L3 — Durable Knowledge (LLM-Wiki)
**Status: Production, the strongest layer**

| Wiki Domain | Pages | Source Quality |
|-------------|-------|---------------|
| marine-engineering | 19,172 | Orcina docs, standards, conference papers |
| engineering | 81 | Methodology, compound patterns, standards |
| naval-architecture | 45 | Ship design, seakeeping, structures |
| maritime-law | 22 | Legal frameworks, cases |
| personal | 5 | Career learnings |

**CLI operations:** init, ingest, batch-ingest, query, lint, status — all functional.
**Automation:** Nightly cron ingest (6 source classes), health monitoring, cross-link discovery.
**Search:** TF-IDF with fast (index) and deep (full-text) modes via `search-wiki.py`.

**Key gaps:**
- Cross-wiki links: only 21 discovered (all title/slug similarity), no semantic or provenance-based linking
- Agent auto-search (#2123) not wired — agents can see wiki paths in SKILL.md but can't query at runtime
- Domain promotions queued but not executed: CSA Z276, OCIMF MEG, API RP 2SK, SIGTTO

### L4 — Entry-Point Surfaces
**Status: Designed, partially implemented**

- Accessibility map (#2096): done
- Canonical entry points (#2104): done
- Accessibility registry (#2136): done
- All 5 wiki `index.md` files serve as navigation
- `cross-links.md` auto-generated but only 21 links

**Key gap:** Wikis not linked from `docs/README.md`. Discoverability is "partially-discoverable" for all wiki assets.

### L5 — Execution State
**Status: Active, well-governed**

- 75 issues across 14 themes (40 open, 35 closed)
- Retrieval contract (#2208) approved — minimum 3 consulted sources per plan
- Planning template includes "Resource Intelligence Summary" section
- Post-closure promotion step (#2236) still open

### L6 — Transient Session
**Status: Policy defined, enforcement pending**

- Durable-vs-transient boundary (#2209) approved as policy
- Promotion rules defined but no automated enforcement
- `.planning/` and session artifacts exist but no automated expiration

---

## 3. Gap Analysis: What's Missing Between Layers

### Gap 1: L2→L3 Promotion Pipeline (Cross-Layer Bridge)
**Severity: High — This is the primary bottleneck**

The provenance contract (#2207) defines *how* L2 registry outputs should promote into L3 wiki pages, but no automated pipeline exists. Today, promotion is manual:
1. Document gets indexed (L1→L2) ✅
2. Summary/classification generated (Phase B/C) ✅
3. **Manual step:** Someone must decide to create/update wiki pages from these outputs ❌

**What industry research suggests:** The Karpathy pattern explicitly calls for automated "ingest → update relevant wiki pages" where a single source touches 10-15 pages. The workspace has batch-ingest for metadata but not for semantic content promotion.

### Gap 2: Cross-Wiki Knowledge Graph (L3 Internal)
**Severity: High — Blocks compounding returns**

The 21 auto-discovered cross-links use slug/title similarity only. No links exist based on:
- Shared `doc_key` provenance (two wiki pages citing the same source)
- Semantic similarity (embedding-based)
- Standards chain (DNV-RP-C205 used in both hydrodynamic and structural analysis)
- Entity co-occurrence (OrcaFlex appears in engineering, marine-engineering, naval-architecture)

**Issues:** #2011, #2044, #2068, #2233 — all OPEN, zero progress.

**What industry research suggests:** Knowledge graphs with 3-7 node types and 5-15 relationship types are the critical success factor for scaling beyond ~1,000 files. The marine-engineering wiki alone has 19,172 pages — well past this threshold.

### Gap 3: Agent Runtime Query (L3→L5 Consumption)
**Severity: High — Agents can't use the knowledge they helped create**

- Wiki paths wired into SKILL.md files (#2102 done) ✅
- `search-wiki.py` exists with TF-IDF scoring ✅
- **No mechanism for agents to auto-query wiki during issue planning/execution** ❌
- #2123 is open: "add llm-wiki search to OrcaFlex/OrcaWave agent skill invocation"

**What industry research suggests:** The "Playbook for Coding Assistants" pattern (from The New Stack's 6 agentic KB patterns) provides context-aware knowledge bases to AI coding agents via MCP. This is exactly what's missing — an MCP or skill-level hook that auto-queries wiki before agent actions.

### Gap 4: Unified `doc_key` Lookup (L2 Internal)
**Severity: Medium — Prevents deduplication at scale**

The provenance contract (#2207) defines `doc_key` as SHA-256 content hash, but:
- No single lookup command maps doc_key → source paths + registry entries + wiki pages + related issues
- The 647K `unknown` content_type records (#1878) undermine trust in the L2 layer
- Cross-machine path aliasing exists in design but not in a queryable service

### Gap 5: Standards Promotion Backlog (L2→L3 Specific)
**Severity: Medium — Queued work, not architectural gap**

4 sweep waves (OCIMF, API/LR/SIGTTO, ISO/ASTM/IACS, DNV/ABS/IMO/USCG) completed metadata-only passes. But specific promotions are queued:
- #2283: CSA Z276.2-19 → LNG wiki
- #2284: OCIMF MEG3/MEG4 → mooring wiki
- #2285: API RP 2SK 3rd ed. → mooring wiki
- #2286: SIGTTO LNG/mooring publications → batch

Plus 12 ASTM implementation WRK items (#168-179) from March 2026.

### Gap 6: Nightly Ingest Reliability (Operational)
**Severity: Medium — Undermines compounding cadence**

- #2293: nightly ingest not idempotent, push-status not truthful
- #2066: `build-knowledge-index` multiline pattern bug
- Without reliable nightly ingest, the "compounding knowledge" promise degrades

---

## 4. Issue Grouping: Unified Work Streams

Regrouping all 40 open issues into 6 work streams by architectural function rather than by creation chronology:

### Work Stream A: Cross-Wiki Knowledge Graph (Priority 1)
*The glue layer that enables compounding returns across all 5 domains*

| Issue | Title | Dependency |
|-------|-------|------------|
| #2011 | Cross-wiki link discovery and infrastructure | Foundation |
| #2044 | Engineering wiki cross-link discovery with domain wikis | Needs #2011 |
| #2068 | Cross-link JSONL package for wiki-to-standard and wiki-to-module | Needs #2011 |
| #2233 | Frontmatter field to wiki schema and validation guidance | Schema change |

**Recommended approach:** Extend `wiki-cross-links.py` beyond slug/title similarity to include:
1. `doc_key` provenance links (two pages citing the same source document)
2. Tag co-occurrence links (shared frontmatter tags above threshold)
3. Entity co-reference links (same entity name in different domains)
4. Standards chain links (standard X references standard Y)

Output: JSONL cross-link store per wiki pair, consumed by agents and wiki index pages.

### Work Stream B: Agent Auto-Search Integration (Priority 1)
*Make the knowledge accessible to agents at runtime*

| Issue | Title | Dependency |
|-------|-------|------------|
| #2123 | Add llm-wiki search to OrcaFlex/OrcaWave agent skill invocation | Core |
| #2126 | Validate markdown conversion quality across all 717 topics | Quality gate |
| #2141 | Fixture-backed tests for llm-wiki ingest and search scripts | Test coverage |
| #2042 | Ingest skill metadata as wiki pages | Content expansion |

**Recommended approach:** Add a `wiki-lookup` step to the skill invocation flow:
1. Before agent executes a domain task, auto-query relevant wiki domain(s)
2. Inject top-3 relevant wiki excerpts into agent context
3. Log which wiki pages were consulted (for provenance)

### Work Stream C: L2 Registry Health & Unified Lookup (Priority 2)
*Fix the foundation layer so promotion flows work correctly*

| Issue | Title | Dependency |
|-------|-------|------------|
| #1878 | Fix 647K unknown content_type in document index | Critical bug |
| #2207 | Standards/codes provenance + reuse contract (implementation) | Needs #1878 |
| #2140 | Replace tracked absolute llm-wiki symlink with portable resolution | Portability |
| #1613 | Cross-reference resource registry with standards transfer ledger | Cross-ref |
| #1614 | Registry freshness checker — periodic URL validation | Freshness |

**Recommended approach:**
1. Fix #1878 first (classify the 647K unknown records)
2. Build `doc_key` lookup script: given a doc_key, return all paths + registry entries + wiki pages + issues
3. Wire freshness checker into weekly review cron

### Work Stream D: Standards & Domain Promotion (Priority 2)
*Execute the queued L2→L3 promotions*

| Issue | Title | Domain |
|-------|-------|--------|
| #2283 | Promote CSA Z276.2-19 to LNG wiki | LNG |
| #2284 | Promote OCIMF MEG3/MEG4 to mooring wiki | Mooring |
| #2285 | Promote API RP 2SK 3rd ed. to mooring wiki | Mooring |
| #2286 | Promote SIGTTO publications as batch | LNG/Mooring |
| #2227 | Promote OCIMF Tandem Mooring and CSA Z276 into LLM-wikis | Cross-domain |
| #2103 | Extend ingestion to AQWA and BEMRosetta documentation | Hydrodynamics |
| #2124 | Extend ingestion to Orcina resources/examples/training | Solver tools |
| #2125 | Auto-refresh ingestion on new Orcina releases | Automation |
| #168-179 | ASTM standards implementation (12 issues) | Structural |

### Work Stream E: Nightly Automation & Governance (Priority 2)
*Make the compounding loop reliable and self-policing*

| Issue | Title | Function |
|-------|-------|----------|
| #2293 | Make nightly ingest idempotent and push-status truthful | Reliability |
| #2066 | Fix build-knowledge-index multiline pattern bug | Reliability |
| #2036 | Engineering wiki incremental ingest cron | Automation |
| #2040 | Cronize engineering wiki incremental ingest | Automation |
| #2105 | Define freshness cadences and staleness signals | Governance |
| #2206 | Validate pyramid conformance across intelligence assets | Governance |
| #2209 | Define durable-vs-transient knowledge boundary (enforcement) | Governance |
| #2279 | Codify support-artifact defer/reject policy | Governance |

### Work Stream F: Ingestion Expansion & Research Pipeline (Priority 3)
*Grow the knowledge surface area*

| Issue | Title | Source |
|-------|-------|-------|
| #2039 | Ingest remaining high-value sources (skills metadata, closed issues) | Internal |
| #2067 | Wire .planning/research into engineering wiki nightly ingest | Research |
| #2010 | Career-learnings seed migration (pipeline, OrcaFlex VIV, FEA, CFD) | Seeds |
| #2216 | Integrate /mnt/ace/acma-codes into llm-wiki and repo intelligence | ACMA |
| #2287 | Assess LR and Noble Denton corpus for downstream repo routing | External |
| #1609 | Automated resource download pipeline | Infrastructure |
| #1610 | Add opm-common to open-source-engineering-catalog | Content |
| #57 | Collect and download electrical engineering resources | Content |

---

## 5. Industry-Aligned Recommendations

### Recommendation 1: Build Cross-Wiki Link Store as JSONL Knowledge Graph
**Maps to:** Work Stream A | **Industry pattern:** Knowledge graph as structural backbone

Instead of building a full graph database, extend the existing JSONL pattern:

```yaml
# cross-links.jsonl (one entry per discovered link)
{
  "source_wiki": "engineering",
  "source_page": "concepts/pipeline-integrity-assessment",
  "target_wiki": "marine-engineering",
  "target_page": "entities/pipeline-integrity",
  "link_type": "provenance",        # provenance | semantic | tag | entity | standards-chain
  "evidence": "shared doc_key abc123",
  "score": 0.85,
  "discovered": "2026-04-16"
}
```

This preserves the git-backed, markdown-first philosophy while adding the structural glue that the industry research identifies as critical beyond ~1,000 files.

### Recommendation 2: MCP-Style Wiki Lookup for Agent Skills
**Maps to:** Work Stream B | **Industry pattern:** Playbook for coding assistants

Add a `wiki-context` section to skill SKILL.md files that agents auto-execute:

```markdown
## Wiki Context (auto-queried)
- domains: [marine-engineering, engineering]
- query: "{task_keywords}"
- max_results: 3
- inject_as: background_context
```

The skill loader would call `search-wiki.py --wiki <domain> --query <keywords> --format json --limit 3` and inject results into the agent's context window before execution.

### Recommendation 3: Fix L2 Before Expanding L3
**Maps to:** Work Stream C | **Industry pattern:** Schema-driven extraction with quality measurement

The 647K unknown content_type records (#1878) represent 62.5% of the master index. Promoting more content to L3 wiki while L2 is unreliable risks the forbidden anti-pattern: "L3 reparsing raw documents because L2 evidence is insufficient."

Priority: #1878 → #2207 implementation → automated promotion pipeline.

### Recommendation 4: Separate "Wiki Strengthening" from "Wiki Expansion"
**Maps to:** Work Streams D vs F | **Industry pattern:** Depth before breadth

The current issue backlog mixes two distinct activities:
- **Strengthening:** Improving existing wiki pages with additional sources and cross-references (e.g., #2241-2243, done)
- **Expansion:** Adding new domains, new source types, new wiki pages (e.g., #2103, #2124)

These should be tracked separately because strengthening compounds existing value while expansion adds new surface area that itself needs strengthening.

### Recommendation 5: Implement Conformance Checks Before Adding More Governance Docs
**Maps to:** Work Stream E | **Industry pattern:** Enforcement gradient (from CLAUDE.md rules)

Three governance documents exist (#2206, #2207, #2209) but none have automated enforcement. Per the repo's own patterns.md enforcement gradient:

```
Level 0 (Prose) → Level 1 (Micro-skill) → Level 2 (Script) → Level 3 (Hook)
```

All three are at Level 0. The conformance-check design (#2206) defines 20+ checks, many of which are automatable today. Implement the top-5 automatable checks as scripts before creating more governance prose.

### Recommendation 6: Add `llm-wiki` GitHub Label
**Maps to:** Organization | **No issue exists yet**

Currently 75 wiki-related issues are scattered across `domain:knowledge`, `domain:knowledge-management`, `cat:document-intelligence`, and title prefixes. A single `llm-wiki` label would enable:
- Dashboard filtering
- Automated triage
- Progress tracking across all work streams

---

## 6. Maturity Assessment

### Current Maturity by Dimension

| Dimension | Score | Evidence |
|-----------|-------|----------|
| **Architecture** | 9/10 | 6-layer pyramid is well-designed, normative, with clear ownership |
| **L1 Source Coverage** | 7/10 | 3.6M+ files indexed, but 247 online resources are metadata-only |
| **L2 Registry Health** | 5/10 | 1M+ records but 647K unknown types; only 6.8% of standards "read" |
| **L3 Wiki Production** | 8/10 | 19K+ pages, CLI+cron+search working, 5 domains active |
| **L3 Cross-Linking** | 2/10 | Only 21 slug-similarity links; no provenance/semantic/entity links |
| **L4 Entry Points** | 6/10 | Registry and maps exist, but wikis not linked from docs/README |
| **Agent Integration** | 3/10 | Paths in SKILL.md but no runtime query capability |
| **Automation Reliability** | 5/10 | Cron exists but idempotency bug (#2293) and multiline bug (#2066) |
| **Governance Enforcement** | 3/10 | 3 policies approved but all at Level 0 (prose only) |
| **Compounding Rate** | 6/10 | Nightly ingest runs but 0 files ingested on 2026-04-16 |

### Target Maturity (3-month horizon)

| Dimension | Target | Key Enabler |
|-----------|--------|-------------|
| L2 Registry Health | 8/10 | Fix #1878, implement doc_key lookup |
| L3 Cross-Linking | 7/10 | JSONL knowledge graph (Work Stream A) |
| Agent Integration | 7/10 | MCP-style wiki lookup (Work Stream B) |
| Automation Reliability | 8/10 | Fix #2293, #2066, add conformance scripts |
| Governance Enforcement | 6/10 | Top-5 automatable checks as scripts |

---

## 7. Issue Statistics

| Category | Open | Closed | Total |
|----------|------|--------|-------|
| LLM-Wiki (core, ingestion, automation, agent, reconciliation, strengthening) | ~25 | ~25 | ~50 |
| Document Intelligence (pipeline, standards, ACMA, triage) | ~18 | ~12 | ~30 |
| Resource Intelligence (registry, downloads, cross-ref) | ~5 | ~1 | ~6 |
| **Combined (deduplicated)** | **~40** | **~35** | **~75** |

**Velocity:** 35 issues closed in 10 days (3.5/day average). At this rate, the 40 open issues represent ~12 days of work — but the remaining issues are harder (cross-linking, governance enforcement, agent integration).

---

## 8. Recommended Execution Order

```
Phase 1 (Week 1-2): Foundation Fixes
├── Fix #1878 (647K unknown content_type)
├── Fix #2293 (nightly ingest idempotency)
├── Fix #2066 (multiline pattern bug)
├── Add llm-wiki GitHub label
└── Fix #2140 (symlink portability)

Phase 2 (Week 2-3): Cross-Wiki Knowledge Graph
├── Extend wiki-cross-links.py (#2011)
│   ├── Provenance-based links (shared doc_key)
│   ├── Tag co-occurrence links
│   ├── Entity co-reference links
│   └── Standards chain links
├── Build JSONL cross-link store (#2068)
├── Add frontmatter schema field (#2233)
└── Wire cross-links into wiki index pages (#2044)

Phase 3 (Week 3-4): Agent Auto-Search
├── Build wiki-lookup skill step (#2123)
├── Validate markdown quality (#2126)
├── Add fixture-backed tests (#2141)
└── Ingest skill metadata as wiki pages (#2042)

Phase 4 (Week 4-6): Promotion Pipeline & Governance
├── Execute standards promotions (#2283-2286, #2227)
├── Implement top-5 conformance checks from #2206
├── Build doc_key unified lookup (#2207 impl)
├── Expand ingestion sources (#2039, #2067, #2103, #2124)
└── Wire freshness checker (#2105, #1614)
```

---

## Appendix A: Research Sources

### Online Research (6 topics investigated)
1. **Karpathy LLM Wiki pattern** — gist.github.com/karpathy, VentureBeat, Frank's World
2. **Document Intelligence** — Databricks, Klippa, BizData360, Snowflake, Azure AI
3. **Resource Intelligence** — arXiv (LLM-powered KGs), DataCamp, LLM-TEXT2KG workshop
4. **RAG + Wiki Convergence** — NStarX, LangWatch, Squirro, RAGFlow
5. **Knowledge Taxonomy** — Enterprise Knowledge (3 articles), MatrixFlows
6. **Agentic Knowledge Management** — The New Stack, ValueStreamAI, OneReach, KPMG, SearchUnify

### Key Industry Insight
> "The LLM Wiki pattern is the personal/small-team sweet spot. RAG is becoming a knowledge runtime. Knowledge graphs are the bridge. Agentic orchestration is the execution model. Taxonomy still needs humans."

### Codebase Artifacts Reviewed
- Operating model: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- Provenance contract: `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- Boundary policy: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- Conformance design: `docs/document-intelligence/pyramid-conformance-checks.md`
- Accessibility registry: `data/document-index/intelligence-accessibility-registry.yaml`
- Maturity tracker: `data/document-index/resource-intelligence-maturity.yaml`
- Cross-links: `knowledge/wikis/cross-links.md`
- Holistic plan: `docs/document-intelligence/holistic-resource-intelligence.md`
- Wiki CLI: `scripts/knowledge/llm_wiki.py`
- Search script: `scripts/knowledge/search-wiki.py`
- Cross-link script: `scripts/knowledge/wiki-cross-links.py`
