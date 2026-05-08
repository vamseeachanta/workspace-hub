---
name: llm-wiki external-post ingest workflow
description: Reusable workflow for ingesting external engineering posts (LinkedIn, blog articles) into vamseeachanta/llm-wiki — domain routing, schema compliance, references grounding, commit hygiene
type: project
originSessionId: 714b2423-3b30-4ff5-8d73-dca937209407
---
Reusable workflow for ingesting external engineering posts (LinkedIn, blog articles) into the public llm-wiki repo at `vamseeachanta/llm-wiki` (nested at `/mnt/local-analysis/workspace-hub/llm-wiki`).

**Why:** llm-wiki is CC-BY-4.0 content + MIT code with a firewall barring workspace-hub private state from leaking into commits. External-post ingests recur (LinkedIn engineering essays from practitioners, blog posts) and follow the same rhythm each time. First execution ran 2026-05-07 with two ingests (Sherwood naval-arch role, Rötzer wave shoaling) committed as `4e50b1b2` and `533d3889`.

**How to apply** — eight-step workflow, write-only by default unless user authorizes commits:

1. **WebFetch the URL first.** Public LinkedIn returns full content via `og:description` (per `feedback_webfetch_first_for_linkedin.md`). Skip the chrome browser unless a "log in to view" gate appears.
2. **Identify the target domain wiki.** Routing: `naval-architecture/` (ship-design, stability, propulsion, hull form), `marine-engineering/` (offshore, metocean, mooring, LNG terminals), `engineering-standards/` (codes with `code_id`), `engineering/` (cross-domain physics, CFD), `maritime-law/`, `lng-projects/`, `acma-projects/`, `asset-management/`. Wrong-domain placement orphans cross-links.
3. **Read the target wiki's nested `CLAUDE.md` schema.** Confirm frontmatter fields (`title`, `tags`, `added`, `last_updated`, `sources`), directory structure, and ingest-workflow steps. Verify cross-link target paths exist before writing — broken cross-refs trip the lint workflow's missing-cross-references check.
4. **Write the source page** at `wiki/sources/<author>-<year>-<topic-slug>.md`. Slug convention is `<author-lastname>-<year>-<topic-slug>.md` per existing examples (e.g., `mctaggart-shipmo3d-maneuvering-2007.md`). Preserve URL on the page; sections: Relevance, key teachings, How this maps to existing wiki structure, Use as a wiki source.
5. **If the post fills a concept gap, write a concept page** at `wiki/concepts/<topic-slug>.md`. Ground it with a "Public references" section listing verified textbooks/standards/public-domain manuals — see `feedback_llm_wiki_concept_pages_need_public_references.md`.
6. **Update `wiki/index.md`**: bump `page_count` and `source_count`, update `last_updated`, insert/append rows in the right tables, and bump section-header pluralization (e.g., `## Concepts (19 pages)` → `(20 pages)`). For the marine-eng wiki specifically, the page_count/source_count are inflated phantom auto-counters — bump by literal +1 each anyway to follow convention.
7. **Append to `wiki/log.md`** with `## [YYYY-MM-DD] ingest | <Source Title>` followed by Processed / Pages created / Pages updated / Notes. Mirror existing firewall language verbatim ("No raw PDFs, private paths, vendor standards text, project specifications, clauses, tables, formulas, or source archive content copied").
8. **Commit per-ingest, not bundled.** Two ingests = two commits, each independently revertable. Use explicit-paths `git add` (not `-A` or `.`) — pre-existing untracked drift in this repo (`.gitignore`, `CLAUDE.md`, `docs/session-handoffs/`) must not ride along. HEREDOC commit messages, no workspace-hub issue refs (firewall), no `--amend`.

**Cross-domain anchor map (verified 2026-05-07):**

- Wave physics standards: `engineering-standards/wiki/standards/dnv-rp-c205.md`, `api-rp-2met.md`, `iso-19901-1.md`
- Wave-theory deep-water concept: `engineering/wiki/concepts/wave-theory-offshore.md`
- Naval-arch source spine already in wiki: `naval-architecture/wiki/sources/introduction-to-naval-architecture.md` (Tupper), the PNA series (multiple slugs, including `principles-of-naval-architecture-volume-i---stability-and-strength.md` and `-volume-ii---resistance-propulsion-and-vibration.md`)

**Don't apply when:** the source is a vendor-derivative PDF (those live at `/mnt/ace`, never in this repo per spinout governance) or the request would require restating proprietary clauses, tables, or formulas from DNV/API/ABS/etc. — link to the existing standards page instead.
