# Intelligence Accessibility Map

> **Issue:** [#2096](https://github.com/vamseeachanta/workspace-hub/issues/2096)
> **Parent:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) — LLM-Wiki + Resource/Document Intelligence Operating Model
> **Siblings:** [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207) (provenance contract), [#2209](https://github.com/vamseeachanta/workspace-hub/issues/2209) (durable/transient boundary)
> **Status:** Normative — approved intelligence accessibility inventory for weekly review consumption
> **Date:** 2026-04-11
> **Scope:** Inventory and accessibility analysis only. Canonical entry-point design is delegated to #2104; machine-readable registry implementation is delegated to #2136.

---

## 1. Purpose and Scope

### What this document defines

This is the **intelligence accessibility map** for the workspace-hub ecosystem. It establishes:

- A concrete inventory of the primary intelligence assets and their canonical locations
- How agents and humans currently discover each asset class
- Which assets are easily discoverable, partially discoverable, or hard to discover
- Broken or weak accessibility patterns (path drift, missing backlinks, trapped intelligence)
- A weekly accessibility checklist consumable by the weekly review process (#2089)
- Recommendations for improving retrieval and discoverability
- Clear boundaries with canonical entry-point design (#2104) and registry implementation (#2136)

### What this document does NOT define

| Out of scope | Owner |
|---|---|
| The parent pyramid model, layer ownership, or information flow rules | #2205 (parent operating model) |
| Provenance schema, `doc_key` definition, or reuse-vs-reparse rules | #2207 (provenance contract) |
| Durable-vs-transient boundary policy | #2209 (boundary policy) |
| Canonical entry-point page design or navigation structure | #2104 |
| Machine-readable registry implementation or reachability metadata schema | #2136 |
| Conformance validation scripts or linters | #2206 |
| Retrieval contract for issue workflows | #2208 |

This document is an **inventory and gap analysis** at Layer 4 (Entry-point). It identifies what needs to be navigable and where navigation is broken. It does not build the navigation system itself.

---

## 2. Relationship to Parent Operating Model (#2205)

This document operates at **Layer 4 (Entry-point)** of the [parent operating model](llm-wiki-resource-doc-intelligence-operating-model.md) pyramid. Per the parent:

| Parent rule | How this map applies it |
|---|---|
| **L4 — Entry-point** owns human/agent navigation surfaces into the intelligence system | This map is itself an L4 artifact: it inventories intelligence assets and identifies how they are (or aren't) navigable |
| **Entry-point docs must not invent new provenance facts** (#2205 Section 5) | This map references existing assets and their actual locations — it does not create provenance claims |
| **Accessibility maps (#2096)** are listed as L4 examples (#2205 Section 2) | This document fulfills that designation |
| **Issue tree dependency order** (#2205 Section 9) | #2096 is sequenced after #2207 and #2209, which are now present as sibling contracts |

---

## 3. Relationship to Sibling Contracts

### #2207 — Standards/Codes Provenance + Reuse Contract

The [provenance contract](standards-codes-provenance-reuse-contract.md) defines `doc_key` identity, provenance fields, and reuse-vs-reparse rules. This map consumes those definitions:

- Asset identity in the table below uses repo file paths (L4 navigation aliases), not `doc_key` values (L2 identity). The `doc_key` lookup is #2136's concern.
- Where this map notes "provenance linkage is weak," the fix lives in #2207's implementation surfaces — not in this document.

### #2209 — Durable vs Transient Knowledge Boundary

The [boundary policy](durable-vs-transient-knowledge-boundary.md) classifies artifact durability. This map applies those classifications:

- Assets marked "durable" in the table below correspond to L2 (registry) or L3 (wiki) artifacts per #2209 Section 5.2.
- Assets marked "transient" are execution-state (L5) or session (L6) artifacts that are not primary accessibility targets but are included when they trap intelligence that should be promoted.

---

## 4. Asset Classes

The intelligence ecosystem contains six asset classes, organized by the parent pyramid layers:

### 4.1 LLM-Wikis (L3 — Durable Knowledge)

Distilled, reusable domain knowledge synthesized from source documents, engineering experience, and validated findings.

**Domains and scale:**

| Wiki domain | Location | Page count | Index |
|---|---|---|---|
| engineering | `knowledge/wikis/engineering/wiki/` | ~78 pages | `wiki/index.md` |
| marine-engineering | `knowledge/wikis/marine-engineering/wiki/` | ~19,168 pages | `wiki/index.md` |
| maritime-law | `knowledge/wikis/maritime-law/wiki/` | ~22 pages | `wiki/index.md` |
| naval-architecture | `knowledge/wikis/naval-architecture/wiki/` | ~45 pages | `wiki/index.md` |
| personal | `knowledge/wikis/personal/wiki/` | ~5 pages | `wiki/index.md` |

**Supporting wiki infrastructure:**

| Asset | Location | Purpose |
|---|---|---|
| Cross-wiki link index | `knowledge/wikis/cross-links.md` | Bidirectional cross-references between wikis (25 links) |
| Wiki schemas | `knowledge/wikis/*/SCHEMA.md` | Frontmatter and page-structure rules |
| Wiki logs | `knowledge/wikis/*/wiki/log.md` | Ingest history |
| Knowledge seeds | `knowledge/seeds/*.yaml` | Pre-wiki domain knowledge (6 seed files) |
| CLAUDE.md per wiki | `knowledge/wikis/*/CLAUDE.md` | Agent entry point for each wiki domain |

### 4.2 Resource / Document Intelligence Docs (L2–L4)

Architecture, audit, planning, and mapping documents for the document-intelligence pipeline and resource-intelligence program.

| Asset | Location | Layer | Purpose |
|---|---|---|---|
| Parent operating model | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | L3-adjacent (normative) | Pyramid architecture, layer ownership, information flows |
| Provenance + reuse contract | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | L3-adjacent (normative) | `doc_key` identity, provenance fields, reuse rules |
| Durable/transient boundary | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` | L3-adjacent (normative) | Artifact classification and promotion rules |
| **This document** | `docs/document-intelligence/intelligence-accessibility-map.md` | L4 | Accessibility inventory and gap analysis |
| Data intelligence map | `docs/document-intelligence/data-intelligence-map.md` | L4 | Registry and index location reference |
| Engineering documentation map | `docs/document-intelligence/engineering-documentation-map.md` | L4 | Detailed inventory of engineering docs by domain |
| Holistic resource intelligence plan | `docs/document-intelligence/holistic-resource-intelligence.md` | L5 (plan) | Unified resource tracking architecture proposal |
| Document intelligence audit | `docs/assessments/document-intelligence-audit.md` | L5 (audit) | Pipeline infrastructure audit (7-phase, metrics) |
| Domain coverage report | `docs/document-intelligence/domain-coverage.md` | L4 | Standards coverage by engineering domain |
| Mount drive knowledge map | `docs/document-intelligence/mount-drive-knowledge-map.md` | L4 | Catalog of mount points and file inventories |

### 4.3 Registries, Ledgers, and Manifests (L2 — Registry/Provenance)

Machine-readable inventory and provenance tracking surfaces.

| Asset | Location | Records/Scale | Purpose |
|---|---|---|---|
| Corpus index | `data/document-index/index.jsonl` | ~1,033,933 records | Per-document index (path, SHA-256, size, extension, source) |
| Registry stats | `data/document-index/registry.yaml` | Aggregate | Counts by source, domain, repo |
| Standards transfer ledger | `data/document-index/standards-transfer-ledger.yaml` | 425 standards | Standard-to-repo/module mapping with status |
| Mounted source registry | `data/document-index/mounted-source-registry.yaml` | 8 sources | Source-root inventory with mount definitions |
| Summaries | `data/document-index/summaries/<sha>.json` | ~639,585 files | Per-document LLM/deterministic classification |
| Enhancement plan | `data/document-index/enhancement-plan.yaml` | 34,099 lines | Domain classification + gap analysis output |
| Online resource registry | `data/document-index/online-resource-registry.yaml` | ~247 resources | Tracked online data sources |
| Conference registries | `data/document-index/conference-*.yaml` | Multiple | Conference paper catalogs and indexes |
| Research literature index | `data/document-index/research-literature-index.jsonl` | Research papers | Literature tracking |
| Design code registry | `data/design-codes/code-registry.yaml` | ~30 codes | DNV, API, ASTM, ISO, BS edition tracking |
| Manifest index | `data/doc-intelligence/manifest-index.jsonl` | Extraction manifests | Cross-reference of all extraction outputs |
| Resource intelligence maturity | `data/document-index/resource-intelligence-maturity.yaml` | Maturity metrics | Docs read, calculations implemented |

### 4.4 Weekly Review Surfaces (Recurring-Operational)

| Asset | Location | Purpose |
|---|---|---|
| Weekly review template | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | Process definition + checklist for #2089 |
| Review results (per-run) | `scripts/review/results/` | Point-in-time review evidence |

### 4.5 Execution / Planning Surfaces That Consume Intelligence (L5)

| Asset | Location | Purpose |
|---|---|---|
| Plans | `docs/plans/` | Issue execution plans (transient) |
| GitHub issues | GitHub issue tracker | Scope, ownership, delivery tracking |
| Handoffs | `docs/handoffs/` | Session continuity context (transient) |
| Capabilities summary | `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` | High-level repo capabilities overview |

### 4.6 Control-Plane and Governance Surfaces

| Asset | Location | Purpose |
|---|---|---|
| Control-plane contract | `docs/standards/CONTROL_PLANE_CONTRACT.md` | Agent entry-point rules (AGENTS.md first) |
| Docs README | `docs/README.md` | Documentation index and navigation |
| Session governance | `docs/governance/SESSION-GOVERNANCE.md` | Session lifecycle checkpoint model |
| AI agent guidelines | `docs/modules/ai/AI_AGENT_GUIDELINES.md` | Agent workflow rules |
| Workspace hub structure | `docs/modules/ai-native/workspace-hub-structure.md` | Visual directory structure reference |

---

## 5. Accessibility Map Table

This is the core deliverable. Each row maps an asset to its current discoverability state.

**Discoverability ratings:**
- **Discoverable**: An agent or human following standard entry points (AGENTS.md → docs/README.md → relevant docs) will find this asset within 2-3 navigation hops.
- **Partially discoverable**: The asset exists and is referenced somewhere, but the path from standard entry points requires domain knowledge or lucky search terms.
- **Hard to discover**: The asset exists but is not referenced from any standard navigation surface, or is only reachable via grep/find.

### 5.1 LLM-Wiki Assets

| Asset | Layer | Canonical Location | Current Entry Point(s) | Intended Users | Discoverability | Gaps |
|---|---|---|---|---|---|---|
| Engineering wiki | L3 | `knowledge/wikis/engineering/wiki/` | `CLAUDE.md` per wiki, `wiki/index.md` | Agent + Human | **Discoverable** (from wiki CLAUDE.md) | Not linked from `docs/README.md`; no mention in `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` |
| Marine-engineering wiki | L3 | `knowledge/wikis/marine-engineering/wiki/` | `CLAUDE.md` per wiki, `wiki/index.md` | Agent + Human | **Discoverable** (from wiki CLAUDE.md) | Same gap as above; 19K pages with no curated entry beyond the index |
| Maritime-law wiki | L3 | `knowledge/wikis/maritime-law/wiki/` | `CLAUDE.md` per wiki, `wiki/index.md` | Agent + Human | **Discoverable** (from wiki CLAUDE.md) | Same gap as above |
| Naval-architecture wiki | L3 | `knowledge/wikis/naval-architecture/wiki/` | `CLAUDE.md` per wiki, `wiki/index.md` | Agent + Human | **Discoverable** (from wiki CLAUDE.md) | Same gap as above |
| Personal wiki | L3 | `knowledge/wikis/personal/wiki/` | `CLAUDE.md` per wiki | Agent + Human | **Partially discoverable** | No external references |
| Cross-wiki link index | L4 | `knowledge/wikis/cross-links.md` | None from docs/ | Agent + Human | **Hard to discover** | Only 25 links; no reference from `docs/README.md` or wiki indexes |
| Knowledge seeds | L3-input | `knowledge/seeds/*.yaml` | `data-intelligence-map.md` Section 6 | Agent | **Partially discoverable** | Mentioned in data-intelligence-map but not from main docs entry points |

### 5.2 Registry / Provenance Assets

| Asset | Layer | Canonical Location | Current Entry Point(s) | Intended Users | Discoverability | Gaps |
|---|---|---|---|---|---|---|
| Corpus index (`index.jsonl`) | L2 | `data/document-index/index.jsonl` | `data-intelligence-map.md` Section 1 | Agent (pipeline) | **Partially discoverable** | Referenced in data-intelligence-map but not from docs/README.md |
| Standards transfer ledger | L2 | `data/document-index/standards-transfer-ledger.yaml` | `data-intelligence-map.md` Section 1 | Agent + Human | **Partially discoverable** | Same |
| Mounted source registry | L2 | `data/document-index/mounted-source-registry.yaml` | `data-intelligence-map.md` Section 1 | Agent | **Partially discoverable** | Same |
| Summaries directory | L2 | `data/document-index/summaries/` | `data-intelligence-map.md` Section 1 | Agent (pipeline) | **Partially discoverable** | 639K files; no human-navigable summary of what's covered |
| Design code registry | L2 | `data/design-codes/code-registry.yaml` | `data-intelligence-map.md` Section 5 | Agent + Human | **Partially discoverable** | Not referenced from engineering wiki or standards wiki pages |
| Online resource registry | L2 | `data/document-index/online-resource-registry.yaml` | `data-intelligence-map.md` Section 1 | Agent | **Hard to discover** | Only referenced from data-intelligence-map |
| Enhancement plan | L2 | `data/document-index/enhancement-plan.yaml` | `data-intelligence-map.md` | Agent (pipeline) | **Hard to discover** | 34K lines; no human-navigable entry |
| Conference registries | L2 | `data/document-index/conference-*.yaml` | `data-intelligence-map.md` | Agent | **Hard to discover** | Multiple files, no unified conference entry point |
| Resource intelligence maturity | L2 | `data/document-index/resource-intelligence-maturity.yaml` | `data-intelligence-map.md` Section 1 | Human + Agent | **Hard to discover** | Key metric file with no link from weekly review template |

### 5.3 Document Intelligence Architecture Docs

| Asset | Layer | Canonical Location | Current Entry Point(s) | Intended Users | Discoverability | Gaps |
|---|---|---|---|---|---|---|
| Parent operating model (#2205) | L3-adj | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | Cross-links in #2207, #2209 docs | Human + Agent | **Partially discoverable** | Not linked from `docs/README.md`; no entry in `docs/document-intelligence/` index |
| Provenance contract (#2207) | L3-adj | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | Parent operating model cross-link table | Human + Agent | **Partially discoverable** | Only reachable via parent doc or grep |
| Boundary policy (#2209) | L3-adj | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` | Parent operating model cross-link table | Human + Agent | **Partially discoverable** | Same |
| Data intelligence map | L4 | `docs/document-intelligence/data-intelligence-map.md` | None from `docs/README.md` | Human + Agent | **Partially discoverable** | Best existing inventory, but not linked from main navigation |
| Engineering documentation map | L4 | `docs/document-intelligence/engineering-documentation-map.md` | None from `docs/README.md` | Human | **Hard to discover** | Detailed but isolated |
| Document intelligence audit | L5 | `docs/assessments/document-intelligence-audit.md` | None from standard paths | Human | **Hard to discover** | Point-in-time audit; no backlink from pipeline docs |

### 5.4 Control-Plane and Weekly Review

| Asset | Layer | Canonical Location | Current Entry Point(s) | Intended Users | Discoverability | Gaps |
|---|---|---|---|---|---|---|
| Weekly review template | Operational | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | `docs/README.md` Quick Links section | Human + Agent | **Discoverable** | Listed in docs/README.md |
| Control-plane contract | Governance | `docs/standards/CONTROL_PLANE_CONTRACT.md` | `docs/README.md` Standards section | Human + Agent | **Discoverable** | Listed in docs/README.md |
| Docs README index | L4 | `docs/README.md` | Repo root README → `docs/` | Human + Agent | **Discoverable** | Does not reference `knowledge/wikis/`, `data/document-index/`, or `docs/document-intelligence/` beyond a few links |
| Capabilities summary | L4 | `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` | `docs/README.md` | Human + Agent | **Discoverable** | Does not mention LLM-wikis or document-intelligence pipeline |

---

## 6. Current Broken and Weak Accessibility Patterns

### 6.1 The `docs/README.md` blind spot

**Problem:** `docs/README.md` is the primary human/agent documentation entry point but has **no links to**:
- `knowledge/wikis/` (19,000+ LLM-wiki pages)
- `data/document-index/` (1M+ indexed documents)
- `docs/document-intelligence/` (the entire intelligence architecture directory)
- `data/design-codes/` (design code registry)
- The parent operating model (#2205) or any sibling contracts

**Impact:** An agent or human entering via `docs/README.md` will not discover the intelligence ecosystem at all. They will find AI agent guidelines, workflow docs, and standards — but not the domain knowledge, provenance registries, or intelligence architecture documents.

**Classification:** **Broken — high severity.** This is the single biggest discoverability gap.

### 6.2 No unified intelligence entry point

**Problem:** There are multiple partial navigation surfaces, but none covers the full intelligence ecosystem:
- `data-intelligence-map.md` covers registries and indexes but not wikis or architecture docs
- `engineering-documentation-map.md` covers engineering documents by domain but not the intelligence architecture
- Wiki `index.md` files cover individual wiki domains but have no upward link to the intelligence ecosystem
- `holistic-resource-intelligence.md` is a plan (L5), not a navigation surface (L4)

**Impact:** To get a full picture of available intelligence, an agent must consult at least 3-4 separate documents and know they exist.

**Classification:** **Weak — medium severity.** This gap is precisely what #2104 (canonical entry points) is designed to resolve. This map inventories the gap; #2104 will design the solution.

### 6.3 `docs/document-intelligence/` has no index

**Problem:** The `docs/document-intelligence/` directory contains 30+ files (architecture docs, plans, audits, maps) but has no `README.md` or `INDEX.md` to help a visitor understand what's there and what to read first.

**Impact:** Finding the right document requires scanning file names or using grep. New arrivals to the intelligence ecosystem have no guided path.

**Classification:** **Broken — medium severity.**

### 6.4 Wiki domains are invisible from `docs/`

**Problem:** The `knowledge/wikis/` tree is the largest knowledge asset in the repo (19,000+ pages across 5 domains) but is referenced from zero documents under `docs/`. The only entry points are the per-wiki `CLAUDE.md` files (which agents load contextually) and the `wiki/index.md` pages (which require you to already know the wiki exists).

**Impact:** Humans navigating `docs/` will never discover the wikis. Agents that don't load a specific wiki's CLAUDE.md will also miss them.

**Classification:** **Broken — high severity.**

### 6.5 Machine-local knowledge accessibility

**Problem:** Key intelligence assets require mounted drives that are only available on specific machines:
- `/mnt/ace/` (standards PDFs, project files) — only on ace-linux-1 (local) and ace-linux-2 (NFS)
- DDE remote drive — requires specific mount
- Summaries in `data/document-index/summaries/` are git-tracked but large (639K files)

**Impact:** An agent running on a machine without mount access cannot reach source documents. The `mounted-source-registry.yaml` records source roots but doesn't advertise which machines can access what.

**Classification:** **Weak — low-medium severity.** The parent model (#2205 Section 7) defines the cross-machine access model. The registry implementation (#2136) will add machine-reachability metadata. This map just notes the current gap.

### 6.6 Missing backlinks from wikis to registries

**Problem:** Wiki pages in `knowledge/wikis/*/wiki/` reference source documents via frontmatter `sources` fields, but there is no reverse lookup: given a registry entry or `doc_key`, there is no way to find which wiki pages cite it without grep.

**Impact:** When a source document is updated or reclassified, there is no efficient way to find affected wiki pages.

**Classification:** **Weak — medium severity.** The provenance contract (#2207) recommends `wiki_refs` back-links on registry entries. Until implemented, this is a search problem.

### 6.7 Stale or orphaned navigation documents

**Problem:** Several documents in `docs/document-intelligence/` were created during specific sessions and may contain stale paths, counts, or status claims:
- `session-handoff-terminal5-2026-04-02*.md` — session handoffs in an architecture directory
- `dde-drive-catalog.md`, `mount-drive-audit.md` — point-in-time drive scans
- Various plan files that should be in `docs/plans/` per the boundary policy (#2209)

**Impact:** Visitors may encounter stale information presented as current. Session handoffs in a normative document directory blur the durable/transient boundary.

**Classification:** **Weak — low severity.** Per #2209, session handoffs should expire after 30 days. These files should be cleaned up or archived.

### 6.8 `WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` omits intelligence ecosystem

**Problem:** The capabilities summary describes the skills system (2,734 skills), multi-repo management, and agent orchestration — but does not mention:
- LLM-wikis (19K+ pages of domain knowledge)
- Document-intelligence pipeline (1M indexed documents, 639K summaries)
- Resource intelligence program
- Knowledge seeds

**Impact:** A human or agent reading the capabilities summary gets an incomplete picture of what the repo actually contains and can do.

**Classification:** **Weak — low severity.** This is a documentation freshness issue, not a structural problem.

### 6.9 Trapped intelligence in transient artifacts

**Problem:** Valuable intelligence findings may be trapped in:
- Session handoffs (`docs/handoffs/`) that will expire in 30 days
- Plan files (`docs/plans/`) that describe important architectural decisions
- Review results (`scripts/review/results/`) that contain findings worth promoting

Per #2209, these should be promoted to L3 (wikis) or allowed to expire. Until promotion processes are systematic, intelligence leaks from transient to oblivion.

**Classification:** **Weak — medium severity.** This is a process gap addressed by #2209's implementation surfaces (Section 10).

---

## 7. Weekly Accessibility Checklist for #2089

These checks are designed to be directly usable by the [weekly ecosystem execution and intelligence review](../modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md) under its "Section D: Intelligence Accessibility" scope.

### D.1 Wiki Accessibility

- [ ] Verify each wiki domain's `wiki/index.md` exists and is non-empty: `knowledge/wikis/{engineering,marine-engineering,maritime-law,naval-architecture,personal}/wiki/index.md`
- [ ] Verify `knowledge/wikis/cross-links.md` exists and frontmatter `total_cross_references` is > 0
- [ ] Verify each wiki domain's `CLAUDE.md` exists and references `SCHEMA.md` and `wiki/index.md`
- [ ] Spot-check 3 random wiki pages: confirm frontmatter has `title`, `tags`, `sources`, `last_updated`
- [ ] Check if any wiki `index.md` has a `page_count` that differs from actual file count by > 10%

### D.2 Registry Accessibility

- [ ] Verify `data/document-index/index.jsonl` exists and has > 0 bytes
- [ ] Verify `data/document-index/standards-transfer-ledger.yaml` exists
- [ ] Verify `data/document-index/mounted-source-registry.yaml` exists and lists at least 5 sources
- [ ] Verify `data/document-index/registry.yaml` exists
- [ ] Verify `data/design-codes/code-registry.yaml` exists
- [ ] Check `data/document-index/resource-intelligence-maturity.yaml` for last-updated date within 30 days

### D.3 Architecture Doc Accessibility

- [ ] Verify parent operating model exists: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- [ ] Verify provenance contract exists: `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- [ ] Verify boundary policy exists: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- [ ] Verify this accessibility map exists: `docs/document-intelligence/intelligence-accessibility-map.md`
- [ ] Verify `docs/document-intelligence/data-intelligence-map.md` exists

### D.4 Entry-Point Health

- [ ] Verify `docs/README.md` exists and contains links to intelligence ecosystem docs (once added)
- [ ] Verify `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` exists
- [ ] Verify `docs/standards/CONTROL_PLANE_CONTRACT.md` exists
- [ ] Check `docs/document-intelligence/` for session handoff files (should be zero; handoffs belong in `docs/handoffs/`)

### D.5 Cross-Machine Accessibility

- [ ] Record which intelligence-critical mounts are available on the review machine: `/mnt/ace/`, DDE remote
- [ ] Verify `data/document-index/mounted-source-registry.yaml` lists all expected mount points
- [ ] Note any mount failures or degraded access states

### D.6 Discoverability Regression Check

- [ ] From `docs/README.md`, can a reader reach `knowledge/wikis/` within 2 clicks/references?
- [ ] From `docs/README.md`, can a reader reach `data/document-index/` within 2 clicks/references?
- [ ] From `docs/README.md`, can a reader reach `docs/document-intelligence/` within 2 clicks/references?
- [ ] From a wiki domain's `CLAUDE.md`, can an agent reach the parent operating model?

---

## 8. Recommendations for Canonical Access Paths

These recommendations identify what should change to improve accessibility. They are **directional guidance**, not the full entry-point design — that work belongs to #2104.

### 8.1 Add intelligence ecosystem section to `docs/README.md`

**What:** Add a "Knowledge & Intelligence" section to `docs/README.md` linking to:
- `knowledge/wikis/` (with domain list)
- `docs/document-intelligence/` (with key documents)
- `data/document-index/` (with key registries)

**Why:** This is the single highest-impact change for discoverability. It makes the intelligence ecosystem visible from the standard navigation entry point.

**Scope note:** This is a backlink addition, not entry-point design. #2104 will design the full navigation structure.

### 8.2 Add `README.md` to `docs/document-intelligence/`

**What:** Create an index for the `docs/document-intelligence/` directory that lists key documents with reading-order guidance.

**Why:** Visitors to this directory currently face 30+ unsorted files with no guide.

### 8.3 Add upward links from wiki CLAUDE.md to intelligence architecture

**What:** Each wiki domain's `CLAUDE.md` should reference the parent operating model (`docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`) as the architectural authority for L3 scope.

**Why:** Agents loading a wiki's CLAUDE.md should know they are operating within a governed architecture.

### 8.4 Add wiki and intelligence links to `WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`

**What:** Add sections covering LLM-wikis (19K+ pages), document-intelligence pipeline (1M indexed, 639K summarized), and knowledge seeds.

**Why:** The capabilities summary is incomplete without the intelligence ecosystem.

### 8.5 Clean up transient artifacts from `docs/document-intelligence/`

**What:** Move session handoff files out of `docs/document-intelligence/` into `docs/handoffs/` per the boundary policy (#2209).

**Why:** Session handoffs in an architecture directory create confusion about what is normative.

### 8.6 Link `resource-intelligence-maturity.yaml` from weekly review

**What:** The weekly review template should reference `data/document-index/resource-intelligence-maturity.yaml` as a key metric surface for intelligence freshness checks.

**Why:** This maturity file is the best single indicator of intelligence pipeline health, but the weekly review template doesn't mention it.

---

## 9. Boundaries vs #2104 and #2136

### What this document does (and #2104 / #2136 do NOT yet)

| This document (#2096) | #2104 (canonical entry points) | #2136 (accessibility registry) |
|---|---|---|
| Inventories existing assets and their actual locations | Will **design** the navigation structure that makes these assets systematically findable | Will **implement** a machine-readable registry with reachability metadata |
| Identifies discoverability gaps in concrete terms | Will define the entry-point page format, content structure, and linking conventions | Will define the registry schema, query interface, and `doc_key` lookup model |
| Provides weekly checklist items for accessibility audits | Will provide the canonical pages that the weekly checklist validates | Will provide the registry that the weekly checklist queries for machine availability |
| Recommends directional improvements | Will implement those improvements as designed pages | Will implement those improvements as machine-readable data |

### Scope guardrails

This document MUST NOT:
- Define the entry-point page schema or format (that's #2104)
- Define the registry YAML/JSON schema (that's #2136)
- Implement `doc_key` lookups or machine-reachability queries (that's #2136)
- Design the navigation link structure between entry points (that's #2104)
- Redefine pyramid layers, ownership, or flow rules (that's #2205)

This document MAY:
- List actual file paths and their discoverability state
- Recommend where links should exist (even if the linked page doesn't exist yet)
- Note where #2104 or #2136 will need to address a gap
- Provide weekly checklist items that test for the presence of future entry points

---

## 10. Likely Implementation Surfaces

These are documentation-layer and workflow-surface changes needed to close the gaps identified in Section 6. No code changes are defined here.

| Surface | Current State | Recommended Change | Owner |
|---|---|---|---|
| `docs/README.md` | No intelligence ecosystem links | Add Knowledge & Intelligence section | #2096 follow-up or #2104 |
| `docs/document-intelligence/README.md` | Does not exist | Create directory index | #2096 follow-up or #2104 |
| `knowledge/wikis/*/CLAUDE.md` | No link to parent operating model | Add cross-reference to #2205 doc | #2096 follow-up |
| `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` | Missing intelligence ecosystem | Add LLM-wiki + doc-intel sections | #2096 follow-up |
| `docs/document-intelligence/session-handoff-*.md` | Session handoffs in architecture dir | Move to `docs/handoffs/` | Cleanup task |
| Weekly review template | No link to maturity metrics file | Add reference to `resource-intelligence-maturity.yaml` | #2089 |

---

## 11. Open Questions / Residual Risks

1. **Freshness of this map.** This accessibility map is a point-in-time inventory (2026-04-11). As assets are added, moved, or archived, this map will drift. The weekly checklist (Section 7) provides a partial hedge, but this document itself needs periodic refresh — recommend at least quarterly or on major intelligence ecosystem changes.

2. **Wiki page count reliability.** The marine-engineering wiki reports ~19,168 pages. This count includes `raw/` subdirectories (articles, papers, standards) that may contain ingested but unprocessed material. The actual curated wiki page count may be lower. The weekly checklist should flag `page_count` vs actual file count discrepancies.

3. **`data-intelligence-map.md` staleness.** This is currently the best single reference for where registries and indexes live, but its metrics and file counts may be stale. If it becomes authoritative, it needs a freshness mechanism.

4. **Cross-wiki link coverage.** Only 25 bidirectional cross-references exist across 19,000+ wiki pages. The `wiki-cross-links.py` script can regenerate them, but the coverage is very low. Whether this is a problem depends on how frequently cross-domain lookups are needed.

5. **Accessibility for non-Claude agents.** Wiki `CLAUDE.md` files are specific to Claude Code. Codex (`.codex/`) and Gemini (`.gemini/`) agents may not have equivalent wiki entry points. The control-plane contract (#1532) defines `AGENTS.md` as the universal entry point, but `AGENTS.md` at repo root does not reference wikis.

6. **Promotion pipeline gap.** Per #2209, valuable findings in transient artifacts should be promoted to L3. No systematic promotion process exists yet. Until one does, intelligence will continue to leak from sessions and plans into oblivion.

---

## 12. Recommended Follow-On Sequence

Based on the gaps identified in this map, work should proceed in this order:

| Order | Work item | Scope | Depends on | Related issue |
|---|---|---|---|---|
| 1 | Add intelligence ecosystem section to `docs/README.md` | Small — add ~20 lines of links | Nothing | #2096 follow-up |
| 2 | Create `docs/document-intelligence/README.md` index | Small — directory-level navigation | Nothing | #2096 follow-up |
| 3 | Add parent operating model cross-reference to wiki `CLAUDE.md` files | Small — edit 5 files | #1 (links exist to point to) | #2096 follow-up |
| 4 | Update `WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` with intelligence ecosystem | Small-medium | #1 | #2096 follow-up |
| 5 | Clean transient artifacts from `docs/document-intelligence/` | Small — move files | Nothing | Cleanup |
| 6 | Design canonical entry-point pages | Medium-large — full L4 navigation design | #1, #2, this map | #2104 |
| 7 | Implement machine-readable accessibility registry | Large — schema, query, reachability | #6, #2207 | #2136 |
| 8 | Add maturity metrics link to weekly review template | Small — edit template | Nothing | #2089 |

---

## Appendix: Asset Discoverability Summary

| Discoverability Level | Count | Examples |
|---|---|---|
| **Discoverable** | 6 | Weekly review template, control-plane contract, docs/README.md, wiki CLAUDE.md files (within wiki context) |
| **Partially discoverable** | 12 | Parent operating model, provenance contract, boundary policy, corpus index, standards ledger, mounted source registry, knowledge seeds, data-intelligence-map, wiki indexes (from outside wiki context) |
| **Hard to discover** | 8 | Cross-wiki link index, online resource registry, enhancement plan, conference registries, resource intelligence maturity, engineering documentation map, document intelligence audit, session handoffs in doc-intelligence dir |

**Overall assessment:** The intelligence ecosystem's most valuable assets — LLM-wikis and the document-intelligence architecture — are not reachable from standard navigation surfaces. The weekly review template and control-plane contract are well-placed, but the knowledge layer beneath them is effectively invisible to anyone not already familiar with the repo structure.
