# Child issue draft — DORIS codes & specs standards corpus

> **Status:** draft (existing tracker is [#2543](https://github.com/vamseeachanta/workspace-hub/issues/2543); CLOSED 2026-04-29 after bounded execution; this draft documents the original planning scope and serves as a template for any successor cycle)
> **Wave:** 2026-04-28 Elements overnight planning wave (umbrella [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540))
> **Corpus:** `/mnt/ace/doris/codes` — 25 GB / 70,400 files (largest by file count; high copyright sensitivity)

## Title

`feat(llm-wiki): plan DORIS codes/specs standards metadata promotion from Elements`

## Recommended labels

- `priority:medium`
- `cat:documentation`
- `domain:standards-tooling`
- `domain:knowledge-management`

## Background

The DORIS codes drop is dominated by licensed publisher families: API (2.5 GB), ASME (577 MB), DnV (507 MB), BV Ship and Offshore Rules (800 MB), DeepStar (916 MB), TechStreet Drop (760 KB but 12,266 files of licensed-aggregator content), Company Specs (7.6 GB / NDA-bound), Perry's Chemical Engineers Handbook (52 KB / McGraw-Hill copyright). Vendor-derivative deny-list per [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) and frontmatter contract per [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) govern wiki authoring boundaries.

## Scope

### In-scope (planning only)
- Faceted index covering all top-level publisher families.
- Pointer pages for the highest-risk families (TechStreet Drop, Company Specs, DeepStar) with explicit no-extraction banner.
- License-risk classification (CRITICAL / HIGH / LOW) per family.
- Optional standards-page stub *only* if a verified `revision` value is in hand.

### Out-of-scope
- Any clause / paragraph / table / figure extraction from any standard.
- Any wiki page under `wiki/standards/<code-id>.md` without a verified revision.
- Republishing licensed-aggregator content (TechStreet inventory listings).
- Republishing client / NDA Company Specs folder names that disclose customer identity.
- OCIMF and CSA pages (governed by `acma-codes` / [#2227](https://github.com/vamseeachanta/workspace-hub/issues/2227) / [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471)).

## Allowed paths (read-only)

- `/mnt/ace/doris/codes/**` — directory listings only; no file content reads
- `.claude/rules/calc-citation-contract.md`
- `docs/standards/calc-output-citation.md`
- `knowledge/wikis/engineering-standards/**` — reference layout

## Forbidden paths (extraction or write)

- Any write under `/mnt/ace/**`
- Any standard file content read (PDF page extraction, OCR, grep into PDF text)
- Any wiki write under `knowledge/wikis/**/raw/`
- Any vendor-derivative content under `knowledge/wikis/**/sources/` per [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482)
- Cross-stream artifact paths (SESA, Doris University, Woodfibre)

## Deliverable

- Inventory plan at `.planning/intel/elements-overnight-wave/doris-codes-standards-inventory-plan.md`
- Families TSV at `.planning/intel/elements-overnight-wave/doris-codes-standards-families.tsv` (columns: family, count, paths_pattern, wiki_target_namespace, license_risk, extraction_policy)
- Canonical plan at `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md`
- Wave result at `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md`

## Acceptance criteria (planning-only)

- [ ] Every top-level family (~30 publisher dirs) classified CRITICAL / HIGH / LOW
- [ ] CRITICAL families carry explicit no-extraction policy
- [ ] Plan forward-adopts [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) frontmatter (`code_id`, `publisher`, `revision`) for any future standards page
- [ ] Plan honors [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) deny-list — no `wiki/sources/` cite of vendor-derivative content
- [ ] Issue ends `status:plan-review`

## Hard rules

- Metadata-only. No standards content text. No clause excerpts. No tables. No figures.
- Frontmatter is *required* on any future standards page; no revision → no page.
- Pointer pages name the family (e.g., "TechStreet Drop") but never enumerate licensed inventory.
