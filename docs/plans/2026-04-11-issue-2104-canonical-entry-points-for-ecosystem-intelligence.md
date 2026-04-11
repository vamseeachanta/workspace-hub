# Plan for #2104: Define Canonical Entry Points for Ecosystem Intelligence

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2104
> **Review artifacts:** scripts/review/results/2026-04-11-plan-2104-claude.md | scripts/review/results/2026-04-11-plan-2104-final.md

---

## Resource Intelligence Summary

### Existing repo docs and entry points consulted

| Entry surface | Path | Current role | Intelligence coverage |
|---|---|---|---|
| Docs README | `docs/README.md` | Primary human/agent documentation entry | **Zero** intelligence ecosystem links — no wikis, registries, architecture docs |
| Capabilities summary | `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` | High-level repo overview | **Omits** LLM-wikis (19K+ pages), doc-intelligence pipeline (1M indexed), knowledge seeds |
| Control-plane contract | `docs/standards/CONTROL_PLANE_CONTRACT.md` | Agent entry-point rules | Defines AGENTS.md → CLAUDE.md → README.md → docs/ reading order; does not reference intelligence layer |
| Data intelligence map | `docs/document-intelligence/data-intelligence-map.md` | Registry & index reference | Best existing registry inventory but **isolated** — not linked from docs/README.md |
| Engineering docs map | `docs/document-intelligence/engineering-documentation-map.md` | Domain inventory by engineering discipline | Detailed but **isolated** — not linked from any standard navigation surface |
| Wiki indexes | `knowledge/wikis/*/wiki/index.md` | Per-domain wiki navigation | **Discoverable within wiki context** but invisible from docs/ |
| Wiki CLAUDE.md | `knowledge/wikis/*/CLAUDE.md` | Agent entry per wiki domain | Works for agents loading a specific wiki; no upward link to intelligence architecture |
| Cross-wiki links | `knowledge/wikis/cross-links.md` | Bidirectional cross-references | **Hard to discover** — only 25 links, not referenced from any navigation surface |
| Weekly review template | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | Operational review process | Has Section D (Intelligence Accessibility) but lacks specific entry-point validation checks |
| Workspace structure | `docs/modules/ai-native/workspace-hub-structure.md` | Visual directory reference | Shows "Data & Knowledge" section but no drill-down into intelligence assets |
| Holistic resource intel | `docs/document-intelligence/holistic-resource-intelligence.md` | Resource tracking architecture proposal | L5 plan, not L4 navigation surface — should not be treated as an entry point |
| Domain coverage | `docs/document-intelligence/domain-coverage.md` | Standards coverage by engineering domain | L4 reference but not linked from navigation |
| Mount drive knowledge map | `docs/document-intelligence/mount-drive-knowledge-map.md` | Catalog of mount points and files | L4 reference but not linked from navigation |

### Parent/sibling artifacts consulted

| Artifact | Issue | Status | Key takeaways for #2104 |
|---|---|---|---|
| Parent operating model | #2205 | Normative | L4 (Entry-point) owns human/agent navigation; must not invent provenance; must not own execution state |
| Provenance contract | #2207 | Normative | `doc_key` identity, provenance fields — #2104 must not redefine; entry points reference but don't create provenance |
| Boundary policy | #2209 | Normative | Entry-point docs are durable (L3-adjacent); plans/reviews are transient (L5) |
| Accessibility map | #2096 | Normative | Concrete inventory of 26 assets across 3 discoverability tiers; identifies 8 broken/weak patterns; provides directional recommendations |

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/index.md` — engineering wiki entry point
- `knowledge/wikis/marine-engineering/wiki/index.md` — marine-engineering wiki entry point (19K+ pages)
- `knowledge/wikis/cross-links.md` — cross-domain reference index

### Gaps identified

1. **No intelligence section in `docs/README.md`** — the single biggest discoverability gap (#2096 Section 6.1, rated broken/high severity)
2. **No index for `docs/document-intelligence/`** — 35+ files with no reading guide (#2096 Section 6.3, rated broken/medium severity)
3. **Wiki domains invisible from `docs/`** — 19K+ pages unreachable from standard navigation (#2096 Section 6.4, rated broken/high severity)
4. **No upward links from wikis to intelligence architecture** — agents in a wiki domain don't know they're in a governed ecosystem
5. **Capabilities summary incomplete** — omits entire intelligence ecosystem
6. **Stale session handoffs in `docs/document-intelligence/`** — transient artifacts blurring normative directory
7. **Weekly review template lacks entry-point validation checks** — Section D is skeletal
8. **Resource intelligence maturity file not linked from weekly review** — key metric file invisible

---

## Current Entry Points and Their Strengths/Weaknesses

### Strengths

| Entry point | Why it works |
|---|---|
| `AGENTS.md` → `CLAUDE.md` reading order | Control-plane contract ensures agents load context in a predictable sequence |
| Per-wiki `CLAUDE.md` + `wiki/index.md` | Agents entering a specific wiki domain get immediate context |
| `docs/standards/CONTROL_PLANE_CONTRACT.md` | Well-linked from `docs/README.md`; defines the agent reading order |
| Weekly review template | Linked from `docs/README.md` Quick Links; has Intelligence Accessibility section |
| `data-intelligence-map.md` | Best single reference for registries and indexes; well-structured |

### Weaknesses

| Entry point | Why it fails |
|---|---|
| `docs/README.md` | Zero links to intelligence ecosystem — the 19K-page wiki layer and 1M-document registry layer are invisible |
| `WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` | Describes skills system and multi-repo management but omits the largest knowledge asset |
| `docs/document-intelligence/` (directory) | 35+ files, no README or index — visitors must grep to find what they need |
| Wiki `CLAUDE.md` files | No upward link to parent operating model; agents don't know about L4/L2 context |
| `holistic-resource-intelligence.md` | L5 plan being used as if it were L4 navigation — creates confusion |
| Cross-wiki links | Exists but is not referenced from any navigation surface |

---

## Redundant, Conflicting, or Dead-End Entry Points

| Asset | Classification | Evidence | Recommended action |
|---|---|---|---|
| `docs/document-intelligence/holistic-resource-intelligence.md` | **Conflicting** — L5 plan masquerading as L4 navigation | Listed as L5 by #2096; contains architectural proposals that are now superseded by #2205 operating model | Demote: add header noting superseded status; do not link as a navigation entry point |
| `docs/document-intelligence/session-handoff-terminal5-2026-04-02.md` | **Dead-end** — transient artifact in normative directory | Identified by #2096 Section 6.7; violates #2209 boundary policy | Move to `docs/handoffs/` per #2209 retention rules |
| `docs/document-intelligence/session-handoff-terminal5-2026-04-02-execution.md` | **Dead-end** — same as above | Same evidence | Same action |
| `docs/document-intelligence/resource-intelligence-action-plan.md` | **Potentially stale** — action plan from prior session | L5 execution artifact in L4/L3 directory | Review for staleness; archive if superseded by #2205 child issues |
| `.agent-os/` directory | **Legacy** — per control-plane contract | CONTROL_PLANE_CONTRACT.md marks as legacy; present in some starter repos | Already scheduled for migration; not an entry point |
| `docs/document-intelligence/CLAUDE-CODE-EXCEL-CONVERSION-PROMPT.md` | **Misplaced** — prompt template in architecture directory | Not an intelligence entry point; task-specific | Move to `docs/handoffs/` or `.claude/` prompt storage |
| `docs/document-intelligence/EXCEL-CONVERSION-PRIORITY.md` | **Misplaced** — same as above | Task-specific priority list | Same action |
| `docs/document-intelligence/EXCEL-CONVERSION-REGISTRY.md` | **Misplaced** — same as above | Task-specific registry | Same action |

---

## Proposed Canonical Entry-Point Model

### Design principles

1. **Minimum viable navigation surface** — add the fewest new pages/sections needed to make existing intelligence discoverable
2. **Link, don't duplicate** — entry points reference existing assets; they do not re-inventory or create new provenance facts
3. **≤3-hop rule** — every major intelligence asset must be reachable from `docs/README.md` within 3 navigation hops
4. **Layer-respecting** — entry points live at L4; they do not own L2 provenance, L3 wiki content, or L5 execution state
5. **Agent + human parity** — the same navigation surface works for both audiences; agent-specific shortcuts (CLAUDE.md) supplement but don't replace

### Three-tier entry-point architecture

```
Tier 1: Root navigation
  docs/README.md
    └─ New section: "Knowledge & Intelligence Ecosystem"
       ├─ Link: docs/document-intelligence/README.md  (Tier 2)
       ├─ Link: knowledge/wikis/  (wiki domain list)
       ├─ Link: data-intelligence-map.md  (registry reference)
       └─ Link: WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md

Tier 2: Intelligence landing page
  docs/document-intelligence/README.md  (NEW — central intelligence navigation)
    ├─ Architecture section
    │   ├─ Parent operating model (#2205)
    │   ├─ Provenance contract (#2207)
    │   ├─ Boundary policy (#2209)
    │   └─ This accessibility map (#2096)
    ├─ Knowledge assets section
    │   ├─ Wiki domains (5 domains, links to each index)
    │   ├─ Knowledge seeds
    │   └─ Cross-wiki link index
    ├─ Registry & provenance section
    │   ├─ Link: data-intelligence-map.md (detailed reference)
    │   ├─ Standards transfer ledger
    │   └─ Mounted source registry
    ├─ Maps & inventories section
    │   ├─ Intelligence accessibility map (#2096)
    │   ├─ Engineering documentation map
    │   ├─ Domain coverage report
    │   └─ Mount drive knowledge map
    └─ Reading order guidance
        "New here? Start with the parent operating model."

Tier 3: Domain-specific entry points (existing, to be linked)
  knowledge/wikis/*/wiki/index.md  — individual wiki domains
  data-intelligence-map.md  — detailed registry/index reference
  engineering-documentation-map.md  — engineering domain inventory
  domain-coverage.md  — standards coverage
```

### Canonical human entry point

**Primary:** `docs/README.md` → "Knowledge & Intelligence Ecosystem" section → `docs/document-intelligence/README.md`

**Rationale:** `docs/README.md` is already the standard human entry per the control-plane reading order (`AGENTS.md` → provider config → `README.md` → `docs/`). Adding an intelligence section here makes the largest knowledge assets visible in the first navigation hop.

### Canonical agent entry points

**For general context:** `AGENTS.md` → `CLAUDE.md` → `docs/README.md` → intelligence section

**For wiki-domain work:** `knowledge/wikis/<domain>/CLAUDE.md` → `wiki/index.md` (already works)

**Enhancement:** Add one line to each wiki `CLAUDE.md` referencing the parent operating model, so agents know they're operating within a governed architecture.

### What about `docs/document-intelligence/README.md` as the intelligence landing page?

**Yes** — this should become the canonical Tier 2 intelligence landing page. Reasons:

1. `docs/document-intelligence/` already contains all the architecture docs, maps, and plans for the intelligence ecosystem
2. Creating a `README.md` here is the standard convention for directory navigation
3. It avoids bloating `docs/README.md` with detailed intelligence navigation
4. The #2096 accessibility map (Section 6.3) explicitly identified this as a broken pattern (no index for 35+ files)

**Required content:**
- Brief purpose statement (1-2 sentences)
- Reading order for newcomers
- Grouped links to architecture docs, maps, and inventories
- Clear labeling of which docs are normative (architecture) vs. operational (maps, audits)
- Link back to `docs/README.md`

### How should wiki domains surface upward?

Wiki domains should be linked from **two places**:

1. **`docs/README.md`** intelligence section — one-line per domain with page count and purpose
2. **`docs/document-intelligence/README.md`** — expanded listing with links to each `wiki/index.md` and `CLAUDE.md`

Wiki `CLAUDE.md` files should gain one upward link to the parent operating model to complete the bidirectional navigation.

---

## Recommended Linking/Navigation Standards

### Standard 1: Relative paths from the linking document

All intelligence entry-point links must use relative paths from the linking document's location. No absolute paths in documentation.

```markdown
<!-- From docs/README.md -->
[Intelligence Landing](document-intelligence/README.md)
[Engineering Wiki](../knowledge/wikis/engineering/wiki/index.md)

<!-- From docs/document-intelligence/README.md -->
[Parent Operating Model](llm-wiki-resource-doc-intelligence-operating-model.md)
[Back to docs/](../README.md)
```

### Standard 2: Section format for L4 navigation pages

Every L4 navigation page (README, index, map) must include:
- **Header** with purpose and last-updated date
- **Reading order** guidance for newcomers (if the page links to 5+ documents)
- **Grouped links** organized by concern (architecture, knowledge, registry, maps)
- **Back-link** to the parent navigation page
- **Scope note** clarifying what this page covers and what it delegates

### Standard 3: ≤3-hop reachability

Every intelligence asset in the #2096 accessibility map must be reachable from `docs/README.md` in ≤3 hops:

| Asset class | Hop 1 | Hop 2 | Hop 3 |
|---|---|---|---|
| Wiki domains | docs/README.md → intelligence section | → wiki domain link | → wiki/index.md |
| Architecture docs | docs/README.md → intelligence section | → doc-intel/README.md | → specific doc |
| Registries | docs/README.md → intelligence section | → data-intelligence-map.md | → specific file |
| Maps/inventories | docs/README.md → intelligence section | → doc-intel/README.md | → specific map |
| Weekly review | docs/README.md → Quick Links | → weekly review template | (1 hop) |

### Standard 4: No provenance invention

Per #2205 Section 5: "Entry-point docs inventing new provenance facts not backed by L2 registry/provenance layer" is a forbidden flow. Entry-point pages must:
- Link to existing assets at their canonical locations
- Quote page counts, record counts, and dates from the assets themselves (not invent new metrics)
- Include a `Last Updated` date so readers can judge freshness

### Standard 5: Normative vs. operational labeling

In `docs/document-intelligence/README.md`, each linked document must be labeled:
- **Normative** — approved architecture/contract (operating model, provenance contract, boundary policy)
- **Operational** — inventory, map, or audit artifact that reflects point-in-time state
- **Transient** — plans, reviews, session handoffs (should generally not appear in L4 navigation)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md` |
| Plan review — Claude | `scripts/review/results/2026-04-11-plan-2104-claude.md` |
| Plan review — Final | `scripts/review/results/2026-04-11-plan-2104-final.md` |
| **Implementation targets (deferred):** | |
| Docs README update | `docs/README.md` — add "Knowledge & Intelligence Ecosystem" section |
| Intelligence landing page | `docs/document-intelligence/README.md` — new file |
| Wiki CLAUDE.md updates | `knowledge/wikis/*/CLAUDE.md` — add parent operating model cross-reference (5 files) |
| Capabilities summary update | `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` — add intelligence ecosystem section |
| Weekly review template update | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — add entry-point validation checks |
| Transient artifact cleanup | Move session handoffs out of `docs/document-intelligence/` |

---

## Deliverable

A canonical entry-point navigation surface for the workspace-hub intelligence ecosystem, comprising: (1) a "Knowledge & Intelligence Ecosystem" section added to `docs/README.md`, (2) a new `docs/document-intelligence/README.md` intelligence landing page, (3) upward links from wiki `CLAUDE.md` files to the parent operating model, (4) updated capabilities summary, (5) entry-point validation checks in the weekly review template, and (6) cleanup of misplaced transient artifacts from the intelligence architecture directory.

---

## Pseudocode / Navigation Logic Sketch

The entry-point system follows a directed graph with no cycles:

```
# Human discovery path
docs/README.md
  └─ section: "Knowledge & Intelligence Ecosystem"
     ├─ [Intelligence Landing] → docs/document-intelligence/README.md
     │   ├─ [Architecture: Operating Model] → llm-wiki-...-operating-model.md
     │   ├─ [Architecture: Provenance] → standards-codes-provenance-reuse-contract.md
     │   ├─ [Architecture: Boundary] → durable-vs-transient-knowledge-boundary.md
     │   ├─ [Inventory: Accessibility Map] → intelligence-accessibility-map.md
     │   ├─ [Registry Reference] → data-intelligence-map.md
     │   ├─ [Engineering Docs] → engineering-documentation-map.md
     │   ├─ [Domain Coverage] → domain-coverage.md
     │   └─ [Back to docs/] → ../README.md
     ├─ [Wiki: Engineering] → ../../knowledge/wikis/engineering/wiki/index.md
     ├─ [Wiki: Marine Engineering] → ../../knowledge/wikis/marine-engineering/wiki/index.md
     ├─ [Wiki: Maritime Law] → ../../knowledge/wikis/maritime-law/wiki/index.md
     ├─ [Wiki: Naval Architecture] → ../../knowledge/wikis/naval-architecture/wiki/index.md
     └─ [Registries] → document-intelligence/data-intelligence-map.md

# Agent discovery path (supplementary to control-plane reading order)
AGENTS.md → CLAUDE.md → docs/README.md → intelligence section → same graph above

# Per-wiki agent path (supplementary)
knowledge/wikis/<domain>/CLAUDE.md
  ├─ [Wiki Index] → wiki/index.md
  └─ [Architecture Context] → ../../docs/document-intelligence/llm-wiki-...-operating-model.md
```

### Content sketch for `docs/document-intelligence/README.md`

```markdown
# Document Intelligence — Navigation Index

> Entry point for the workspace-hub intelligence ecosystem architecture,
> inventories, and knowledge assets.
> Last Updated: YYYY-MM-DD

## Reading Order for Newcomers

1. **Start here:** [Parent Operating Model](llm-wiki-...-operating-model.md) — pyramid, layers, flows
2. **Identity rules:** [Provenance Contract](standards-codes-provenance-reuse-contract.md) — doc_key, reuse
3. **Durability rules:** [Boundary Policy](durable-vs-transient-knowledge-boundary.md) — durable vs transient
4. **Current state:** [Accessibility Map](intelligence-accessibility-map.md) — what exists, what's broken

## Architecture (Normative)

| Document | Issue | Purpose |
|---|---|---|
| [Operating Model](llm-wiki-...-operating-model.md) | #2205 | Six-layer pyramid, ownership, flows |
| [Provenance Contract](standards-codes-provenance-reuse-contract.md) | #2207 | doc_key identity, reuse rules |
| [Boundary Policy](durable-vs-transient-knowledge-boundary.md) | #2209 | Durable vs transient classification |
| [Conformance Checks](pyramid-conformance-checks.md) | #2206 | Validation design |

## Knowledge Assets

| Domain | Location | Scale |
|---|---|---|
| Engineering | [knowledge/wikis/engineering/wiki/index.md](../../knowledge/wikis/engineering/wiki/index.md) | ~78 pages |
| Marine Engineering | [knowledge/wikis/marine-engineering/wiki/index.md](...) | ~19,168 pages |
| Maritime Law | [knowledge/wikis/maritime-law/wiki/index.md](...) | ~22 pages |
| Naval Architecture | [knowledge/wikis/naval-architecture/wiki/index.md](...) | ~45 pages |
| Personal | [knowledge/wikis/personal/wiki/index.md](...) | ~5 pages |
| Cross-wiki references | [knowledge/wikis/cross-links.md](...) | 25 links |
| Knowledge seeds | [knowledge/seeds/](../../knowledge/seeds/) | 6 seed files |

## Registries & Provenance (L2)

See: [Data Intelligence Map](data-intelligence-map.md) for comprehensive registry reference.

Key surfaces:
- Corpus index: `data/document-index/index.jsonl` (1M+ records)
- Standards ledger: `data/document-index/standards-transfer-ledger.yaml` (425 standards)
- Design codes: `data/design-codes/code-registry.yaml` (~30 codes)
- Maturity tracking: `data/document-index/resource-intelligence-maturity.yaml`

## Maps & Inventories (Operational)

| Document | Purpose |
|---|---|
| [Accessibility Map](intelligence-accessibility-map.md) | Asset discoverability inventory (#2096) |
| [Engineering Documentation Map](engineering-documentation-map.md) | Domain-by-domain document inventory |
| [Domain Coverage](domain-coverage.md) | Standards coverage by engineering domain |
| [Mount Drive Knowledge Map](mount-drive-knowledge-map.md) | Mount point and file catalog |

## Back

← [docs/README.md](../README.md)
```

### Content sketch for `docs/README.md` intelligence section

```markdown
## Knowledge & Intelligence Ecosystem

The workspace-hub contains a large-scale intelligence ecosystem spanning domain knowledge,
document registries, and engineering documentation.

| Asset | Location | Scale |
|---|---|---|
| **Intelligence landing page** | [docs/document-intelligence/](document-intelligence/README.md) | Architecture, inventories, maps |
| **LLM-Wikis** | [knowledge/wikis/](../knowledge/wikis/) | 19,300+ pages across 5 domains |
| **Document registries** | [data-intelligence-map](document-intelligence/data-intelligence-map.md) | 1M+ indexed documents, 639K summaries |
| **Design code registry** | [data/design-codes/code-registry.yaml](../data/design-codes/code-registry.yaml) | ~30 engineering codes |
| **Weekly intelligence review** | [WEEKLY_ECOSYSTEM_...](modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md) | Operational health review |

For architecture and reading order, start at [docs/document-intelligence/](document-intelligence/README.md).
```

---

## Files to Change (Planning Scope Only)

These are the implementation targets. **None of these changes should be made during planning.**

| Action | Path | Reason |
|---|---|---|
| **Modify** | `docs/README.md` | Add "Knowledge & Intelligence Ecosystem" section after Quick Links |
| **Create** | `docs/document-intelligence/README.md` | New intelligence landing page / directory index |
| **Modify** | `knowledge/wikis/engineering/CLAUDE.md` | Add parent operating model cross-reference |
| **Modify** | `knowledge/wikis/marine-engineering/CLAUDE.md` | Same |
| **Modify** | `knowledge/wikis/maritime-law/CLAUDE.md` | Same |
| **Modify** | `knowledge/wikis/naval-architecture/CLAUDE.md` | Same |
| **Modify** | `knowledge/wikis/personal/CLAUDE.md` | Same |
| **Modify** | `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` | Add intelligence ecosystem section |
| **Modify** | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | Add entry-point validation checks to Section D |
| **Move** | `docs/document-intelligence/session-handoff-terminal5-2026-04-02.md` → `docs/handoffs/` | Transient artifact in normative directory |
| **Move** | `docs/document-intelligence/session-handoff-terminal5-2026-04-02-execution.md` → `docs/handoffs/` | Same |
| **Modify** | `docs/document-intelligence/holistic-resource-intelligence.md` | Add superseded-by header noting #2205 |
| **Update** | `docs/plans/README.md` | Add this plan to the index |

### Likely future implementation surfaces (separate from this issue)

| Surface | Owner issue |
|---|---|
| Machine-readable accessibility registry | #2136 |
| Workflow retrieval contract | #2208 |
| Conformance validation scripts | #2206 |
| Weekly review automation | #2089 |

---

## TDD / Verification List for Future Implementation

Since this is a documentation/navigation issue (not code), verification is link-based rather than test-based:

| Check | What it verifies | Method |
|---|---|---|
| `docs/README.md` intelligence section exists | Tier 1 entry point is present | Grep for "Knowledge & Intelligence Ecosystem" heading |
| `docs/document-intelligence/README.md` exists and is non-empty | Tier 2 landing page is present | File existence check |
| Architecture docs linked from README.md | Operating model, provenance, boundary reachable in ≤2 hops | Verify links resolve to existing files |
| Wiki domains linked from README.md | All 5 domains reachable in ≤3 hops | Verify links resolve to existing wiki/index.md files |
| Wiki CLAUDE.md files have upward link | Agents in wiki context know about architecture | Grep each CLAUDE.md for "operating-model" reference |
| Capabilities summary includes intelligence | Overview is complete | Grep for "LLM-wiki" or "document-intelligence" in capabilities doc |
| Weekly review has entry-point checks | Section D validates navigation health | Grep for entry-point validation checkboxes |
| Session handoffs moved out of doc-intelligence | Boundary policy enforced | Verify no `session-handoff-*` files in `docs/document-intelligence/` |
| No broken links in new navigation | All links resolve | Script to check relative link targets exist |
| ≤3-hop reachability for all #2096 assets | Navigation design goal met | Manual trace from docs/README.md to each asset class |

---

## Acceptance Criteria

- [ ] `docs/README.md` contains a "Knowledge & Intelligence Ecosystem" section with links to intelligence landing page, wiki domains, and registry reference
- [ ] `docs/document-intelligence/README.md` exists with reading order, architecture links, knowledge assets, registry reference, and maps/inventories
- [ ] All 5 wiki `CLAUDE.md` files contain a cross-reference to the parent operating model
- [ ] `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` includes an intelligence ecosystem section mentioning LLM-wikis and document-intelligence pipeline
- [ ] `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` Section D includes entry-point validation checks
- [ ] Session handoff files moved out of `docs/document-intelligence/`
- [ ] `holistic-resource-intelligence.md` has a superseded-by note
- [ ] All new links resolve to existing files (no broken links)
- [ ] No new provenance facts invented by entry-point pages
- [ ] Plan index updated in `docs/plans/README.md`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-review) | APPROVE with MINOR notes | See `scripts/review/results/2026-04-11-plan-2104-claude.md` |

**Overall result:** PASS — plan is review-ready

Revisions made based on review:
- Added explicit "What about `docs/document-intelligence/README.md`?" answer to address whether it should become the landing page
- Strengthened scope boundary with #2136 and #2208
- Added "No provenance invention" as acceptance criterion
- Added broken-link verification to TDD list

---

## Risks and Open Questions

1. **Risk: `docs/README.md` is already long (285 lines).** Adding an intelligence section may make it unwieldy. Mitigation: keep the section brief (10-15 lines) and delegate detail to `docs/document-intelligence/README.md`.

2. **Risk: Wiki page counts may be stale.** The marine-engineering wiki reports ~19,168 pages but this includes `raw/` subdirectories. Mitigation: use approximate counts ("19K+ pages") and note that exact counts come from the wiki indexes themselves.

3. **Risk: Stale file cleanup may affect other in-flight work.** Session handoffs being moved may be referenced by active sessions. Mitigation: check for active references before moving; leave a forwarding note if needed.

4. **Open: Should `AGENTS.md` at repo root also reference the intelligence ecosystem?** Currently `AGENTS.md` focuses on workflow contract. Adding intelligence links there would make them visible to all agents before they even reach `docs/`. Recommendation: defer to user decision — the control-plane contract doesn't currently include intelligence navigation, and changing it has broader implications.

5. **Open: Should existing documents in `docs/document-intelligence/` that are L5 (plans, action plans) be moved to `docs/plans/`?** The boundary policy (#2209) says plans belong in `docs/plans/`. Several planning documents exist in the intelligence directory. Recommendation: flag for a follow-on cleanup issue rather than expanding this issue's scope.

6. **Boundary: Registry implementation (#2136).** This plan designs the navigation surface. The machine-readable registry (programmatic `doc_key` lookups, reachability metadata) is #2136's scope. The navigation pages link to registry files but do not implement query interfaces.

7. **Boundary: Workflow retrieval (#2208).** This plan designs how humans and agents find intelligence. How issue workflows programmatically consume intelligence during planning/execution is #2208's scope.

8. **What implementation should remain deferred to #2136 and #2208?**
   - **#2136:** Machine-readable registry schema, `doc_key` lookup interface, machine-reachability metadata, programmatic access API
   - **#2208:** Issue planning retrieval hooks, evidence requirements for plans, automated intelligence injection into issue workflows

---

## Complexity: T2

**T2** — Multiple documentation files modified/created, no code changes, requires careful navigation design and coordination with 4+ sibling issues. Not T1 because it involves creating a new navigation page and updating 10+ existing files. Not T3 because the changes are documentation-only with no multi-module code architecture.
