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
8. **Sidecar must declare source sibling** (per [`.claude/rules/wiki-sibling-routing.md`](wiki-sibling-routing.md) Layer 4, #2778). Every `Citation` sidecar carries:
   - `source_sibling:` **(required)** — `"generic"` (sourced from `vamseeachanta/llm-wiki`) or a client slug (e.g., `"acma"` when sourced from `vamseeachanta/llm-wiki-acma`).
   - `source_project:` **(optional)** — populated when the citation is project-scoped (e.g., `"sirocco"` for content under `llm-wiki-acma/projects/sirocco/`); `null` for client-level or generic citations.
   Default during digitalmodel cross-repo migration: `source_sibling: "generic"`. Resolver raises `CitationResolutionError` when `source_sibling` mismatches the wiki target the resolver actually reaches (e.g., citation claims `generic` but slug resolves under `llm-wiki-acma/`).

**Sidecar schema (extended for #2778):**

```yaml
citations:
  - code_id: DNV-OS-E301
    publisher: DNV
    revision: 2018-07
    section: §2.2
    source_sibling: generic            # required — 'generic' or <client-slug>
    source_project: null               # optional — project-scoped if non-null
```

**Do NOT apply when:** the constant is derived from the code itself (not a standard), is a convention-only numeric (e.g., array size), or is already in a scope where the caller has wired citations upstream. Don't double-cite.

**Pilot reference (LIVE — [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685)):** `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py:check_mbl_with_safety_factor` is the live DNV-OS-E301 mooring safety factor citation pilot (plan dated 2026-05-13, landed 2026-05-15). The method consumes `digitalmodel.citations.registry.get_mooring_safety_factor()` and returns a sidecar dict including a `citations` list with the DNV-OS-E301 `Citation`. Standalone-package mode (no `knowledge/wikis/` overlay) degrades gracefully with a one-shot `RuntimeWarning`; workspace-hub context fails closed on missing or mismatched frontmatter. The legacy `check_mbl()` method remains for backward compatibility and intentionally does NOT apply safety factors — caller opts into citation emission by name. Wiki target: [`knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`](../../knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md). Tests: `digitalmodel/tests/orcaflex/test_mooring_design_citations.py` (12 cases) + `digitalmodel/tests/citations/` (14 cases).
