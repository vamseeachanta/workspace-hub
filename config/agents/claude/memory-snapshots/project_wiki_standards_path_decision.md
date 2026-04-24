---
name: wiki/standards/ sanctioned as first-class page type
description: Decision 2026-04-23 on #2471 — standards get a dedicated `wiki/standards/` subtree, not reused sources/ or entities/. Applies across eng/marine/naval wikis.
type: project
originSessionId: 3415d1dc-e37e-4069-a1eb-a2a3a2c2ca83
---
Standards-overview pages in llm-wikis are routed to a new sanctioned `wiki/standards/` subtree (e.g., `knowledge/wikis/marine-engineering/wiki/standards/csa-z276.md`), not reused under `wiki/sources/` or `wiki/entities/`.

**Why:** Reusing `sources/` (one page per ingested doc) would mix raw-source summaries with cross-standard overview pages, muddying lint rules. `entities/` semantics don't fit standards cleanly (entities are tangible things / software). First-class `wiki/standards/` lets standards carry their own frontmatter contract (`code_id`, `publisher`, `revision`, `jurisdiction`) and stays lint-distinguishable.

**How to apply:**
- When someone asks where a code/standard overview page should live in an llm-wiki, answer `wiki/standards/<code-id>.md` (lowercase, hyphen-separated).
- The sanction applies to the three standards-touching wikis: marine-engineering, engineering, naval-architecture. Maritime-law, personal, health-reports are out of scope for now.
- Codification plan is `docs/plans/2026-04-23-issue-2471-standards-wiki-path-sanction.md`; it must land (schema + pyramid-conformance + lint recognition) before large-scale promotion under `#2227` proceeds.
- Frontmatter required fields for standards pages: `code_id`, `publisher`, `revision` (in addition to base schema). Optional: `jurisdiction`, `supersedes`.
- Raw standards PDFs continue to live under `raw/standards/`; the new `wiki/standards/` subtree is for LLM-maintained overview markdown, not raw docs.
- Unblocks: CSA portion of #2227 and ACMA-codes umbrella #2216.
