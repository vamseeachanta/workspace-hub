# Adversarial Review — #2096 Intelligence Accessibility Map

> **Reviewer:** Claude Code (Adversarial Reviewer role)
> **Date:** 2026-04-11
> **Document under review:** `docs/document-intelligence/intelligence-accessibility-map.md`
> **Review against:** #2205 (parent operating model), #2207 (provenance contract), #2209 (boundary policy)

---

## Review Criteria

| # | Criterion | Verdict | Notes |
|---|---|---|---|
| 1 | Consistency with #2205 pyramid model | **PASS** | Map correctly positions itself at L4 (Entry-point). Does not redefine layer ownership, information flows, or the `doc_key` rule. References the parent model as authoritative. |
| 2 | Non-overlap with #2207 provenance contract | **PASS** | Map explicitly states it uses file paths (L4 navigation aliases) rather than `doc_key` values. Notes that `doc_key` lookup is #2136's concern. Does not define provenance fields or reuse rules. |
| 3 | Non-overlap with #2209 boundary policy | **PASS** | Map applies #2209's durable/transient classifications correctly. Identifies transient artifacts in normative directories as a gap (Section 6.7). Does not redefine classification rules. |
| 4 | Clear boundary with #2104 | **PASS** | Section 9 explicitly delineates what this map does vs what #2104 will design. Recommendations in Section 8 are directional, not design specifications. |
| 5 | Clear boundary with #2136 | **PASS** | Section 9 explicitly separates inventory (this map) from machine-readable registry (for #2136). Does not define registry schemas. |
| 6 | Concrete usefulness for humans | **PASS with note** | The accessibility table (Section 5) maps real assets to real paths. Discoverability ratings are grounded in navigation-hop analysis. **Note:** The table is long; a future summary view might be needed for quick reference. |
| 7 | Concrete usefulness for agents | **PASS with note** | Weekly checklist items (Section 7) are file-existence checks that an agent can execute directly. **Note:** Some checks are subjective ("spot-check 3 random wiki pages") — acceptable for human-run weekly reviews but not automatable without additional work. |
| 8 | Weekly accessibility checks complete | **PASS** | 6 checklist sections covering wikis, registries, architecture docs, entry-point health, cross-machine access, and discoverability regression. |
| 9 | Real discoverability gaps (not generic) | **PASS** | Section 6 identifies 9 specific gaps with concrete file paths and severity ratings. The `docs/README.md` blind spot (Section 6.1) is verifiable — `docs/README.md` indeed has zero links to `knowledge/wikis/` or `docs/document-intelligence/`. |
| 10 | Does not step into implementation | **PASS** | Section 10 identifies documentation surfaces, not code changes. Recommendations stay at the doc/link level. |

---

## Issues Found

### Minor Issues

**M1: Marine-engineering wiki page count may be inflated.**
The map reports ~19,168 pages for marine-engineering, but the `knowledge/wikis/marine-engineering/` tree includes `raw/` subdirectories (articles, papers, standards) that contain source material, not curated wiki pages. The actual L3 wiki page count (under `wiki/`) may be significantly lower.

**Action:** The map already notes this in Open Question #2. The weekly checklist includes a page-count discrepancy check. **Acceptable as-is** — the note in Section 11.2 covers it.

**M2: No explicit versioning or freshness signal.**
The map has a `Date: 2026-04-11` header but no mechanism for signaling when it becomes stale. Other architecture docs in the family (#2205, #2207, #2209) also lack version fields but they are more stable by nature — an accessibility map is more likely to drift.

**Action:** The map addresses this in Open Question #1 (recommending quarterly refresh). **Acceptable as-is** — adding a `last_verified` date would be a nice improvement but is not a blocker.

**M3: Some "hard to discover" assets may be acceptable.**
The enhancement plan (`enhancement-plan.yaml`, 34K lines) and extraction manifests are pipeline-internal artifacts. Rating them "hard to discover" implies they should be more visible, but their intended audience is pipeline code, not humans.

**Action:** The discoverability rating is still accurate (they ARE hard to discover), and the map's "intended users" column marks them as "Agent (pipeline)." The severity is correctly rated as low. **Acceptable as-is.**

### No Major Issues Found

The document is internally consistent, correctly scoped, and produces actionable deliverables for #2089.

---

## Verdict

**APPROVED — no revisions required.**

The intelligence accessibility map:
- Stays within its L4 scope
- Does not redefine parent-level contracts
- Provides concrete, verifiable accessibility data
- Produces an actionable weekly checklist for #2089
- Clearly delineates boundaries with #2104 and #2136
- Identifies real gaps backed by repo inspection

Minor issues noted above are informational and do not require changes to the document.
