# Calculation-output citation contract — agent rule

**When a calc module (digitalmodel, assetutilities, or sibling) uses a standards-derived constant or formula, emit a Citation matching the schema.**

**Why:** engineering outputs must be defensible to reviewers and regulators. Wiki is the audit-trail surface; citations turn retrieval into traceability. Per-incident precedent: #2481 recorded the memory-level user requirement that calcs in professional-practice repos should not silently ship without provenance.

**How to apply:**

1. Schema and operational contract: `docs/standards/calc-output-citation.md`
2. Citation target: a wiki page with #2471 frontmatter (`code_id`, `publisher`, `revision`). Forward-adopt these fields if the specific page you need doesn't yet carry them.
3. Emit a `Citation` instance (see pilot at `digitalmodel/src/digitalmodel/citations/schema.py`) alongside every standards-derived numeric constant you introduce.
4. Validation is **fail-closed at calc time** per #2481 D2: a missing wiki page or frontmatter mismatch raises `CitationResolutionError` with the `code_id` in the message so operators can retarget.
5. Resolver is **direct file read** for v1 per #2481 D3. Migrate to MCP `wiki_search` when [#2400](https://github.com/vamseeachanta/workspace-hub/issues/2400) ships; the schema doesn't change.
6. Citations emit to a **sidecar**, not the primary numeric payload — preserves downstream-consumer compatibility.
7. Do NOT cite wiki pages under `knowledge/wikis/*/wiki/sources/` — those are vendor-derivative deny-list per the governance doc #2482. Cite the standards-page (under `standards/`) the sources-page references, or the methodology/concept page under `concepts/`.

**Do NOT apply when:** the constant is derived from the code itself (not a standard), is a convention-only numeric (e.g., array size), or is already in a scope where the caller has wired citations upstream. Don't double-cite.

**Pilot reference:** `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` demonstrates citation emission for DNV-OS-E301 mooring safety factors.
