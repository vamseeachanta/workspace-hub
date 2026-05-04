---
name: wiki/standards/ subtree as first-class page type (partial — #2471 is CSA-only; general substrate now scoped to aces-#4)
description: 2026-04-23 routing principle (`wiki/standards/<code-id>.md` for standards pages) is sanctioned as a pattern, but workspace-hub #2471 is scoped strictly to CSA Z276; general offshore/marine substrate populate is now scoped to aceengineer-strategy aces-#4 (created 2026-04-25)
type: project
originSessionId: 3415d1dc-e37e-4069-a1eb-a2a3a2c2ca83
---

Standards-overview pages in llm-wikis are routed to a `wiki/standards/` subtree (e.g., `knowledge/wikis/marine-engineering/wiki/standards/csa-z276.md`), not reused under `wiki/sources/` or `wiki/entities/`. The routing principle is sanctioned across the three standards-touching wikis (marine-engineering, engineering, naval-architecture).

**Why:** Reusing `sources/` (one page per ingested doc) would mix raw-source summaries with cross-standard overview pages, muddying lint rules. `entities/` semantics don't fit standards cleanly (entities are tangible things / software). First-class `wiki/standards/` lets standards carry their own frontmatter contract (`code_id`, `publisher`, `revision`, `jurisdiction`) and stays lint-distinguishable.

**How to apply:**
- When someone asks where a code/standard overview page should live in an llm-wiki, answer `wiki/standards/<code-id>.md` (lowercase, hyphen-separated). The principle holds.
- The principle applies to: marine-engineering, engineering, naval-architecture. Maritime-law, personal, health-reports are out of scope.
- Frontmatter required: `code_id`, `publisher`, `revision`. Optional: `jurisdiction`, `supersedes`. (Locked separately by workspace-hub #2481 calc-citation contract — completed 2026-04-24.)
- Raw standards PDFs continue under `raw/standards/`; `wiki/standards/` is for LLM-maintained overview markdown only.

**Current implementation status (verified 2026-04-25):**
- **Workspace-hub #2471** is OPEN with title "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — scoped **strictly to CSA Z276**, not the general substrate. Earlier framing in this memory described it as a general codification; that framing is stale.
- **Codification plan** (filename `docs/plans/2026-04-23-issue-2471-standards-wiki-path-sanction.md` referenced in earlier memory body) **does not exist** in the repo. The plan was either never written or used a different filename. Verify with `ls docs/plans/2026-04-23-issue-2471*` before citing.
- **General offshore/marine standards substrate** (DNV-OS-E301, API RP 2SK, ISO/ABS) is now scoped to aceengineer-strategy issue **aces-#4** ([https://github.com/vamseeachanta/aceengineer-strategy/issues/4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4)) created 2026-04-25 in the cradle-to-grave engineering flywheel tree (epic [aces-#1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1)). aces-#4's plan (`docs/plans/2026-04-25-aces-4-flywheel-standards-canonical-home.md`) is two-phase: Phase 1 decides the canonical durable home (audits the `wiki/standards/` proposal here against the actual dispersion), Phase 2 populates DNV-OS-E301 + API RP 2SK with frontmatter + crosswalk + digitalmodel cross-repo citations.
- **Unblocks:** CSA portion of #2227 (#2471 specifically) and the aceengineer-strategy mooring vertical wedge (aces-#4).

**Reconcile note:** before recommending the `wiki/standards/` subtree as canonical for any new standard, verify (a) #2471 has actually landed for CSA, (b) aces-#4 Phase 1 hasn't superseded the path with a different decision (e.g., promoting standards to a higher-level subtree), and (c) the frontmatter schema matches the current state of #2481 calc-citation contract (which may have added fields like `license_class` per aces-#4 v2 patch).

## Amendment 2026-05-03 (sanctioned via #2615)

The `wiki/standards/<code-id>.md` routing principle is formally extended via workspace-hub umbrella sanction issue **#2615** (W5-D) to include two additional wikis:

- **engineering-standards** — formally sanctioned 2026-05-03 (W3-C re-anchor target for W1-A, #2586). `Sanctioned-by: #2615` reference appended to `knowledge/wikis/engineering-standards/CLAUDE.md`.
- **asset-management** — formally sanctioned 2026-05-03 (W3-C re-anchor target for W1-B, #2587). `Sanctioned-by: #2615` reference appended to `knowledge/wikis/asset-management/CLAUDE.md`.

**Status of remaining out-of-principle wikis (as of 2026-05-03):**
- **lng-projects** and **acma-projects** — auto-generated `wiki/standards/` schema via `llm-wiki init` exists, but user did NOT separately approve formal codification at #2615 approval time; status remains *pending user decision*. Do NOT cite #2615 as sanction for these two wikis.
- **maritime-law, personal, health-reports** — reaffirmed OUT OF SCOPE per the original memory body above; no `Sanctioned-by` reference applies.

**Enforcement:** governance test `tests/governance/test_2471_citation_scope.py::test_out_of_principle_wiki_routing_requires_sanction_citation` flags any plan that cites `wiki/standards/<code-id>.md` routing for a wiki outside {marine-engineering, engineering, naval-architecture, engineering-standards, asset-management} without an explicit sanction-issue (`#NNNN`) reference in the plan body.
