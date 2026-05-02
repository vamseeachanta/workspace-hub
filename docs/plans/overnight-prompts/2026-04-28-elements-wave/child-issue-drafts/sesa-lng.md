# Child issue draft — SESA LNG corpus

> **Status:** draft (file as a new issue ONLY if user instructs; existing tracker is [#2541](https://github.com/vamseeachanta/workspace-hub/issues/2541))
> **Wave:** 2026-04-28 Elements overnight planning wave (umbrella [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540))
> **Corpus:** `/mnt/ace/doris/62092_sesa` — 1.7 GB / 889 files (excluding `_from_elements/` provenance staging)

## Title

`feat(llm-wiki): plan curated SESA LNG corpus extraction from Elements`

## Recommended labels

- `priority:medium`
- `cat:data-pipeline`
- `domain:knowledge-management`
- `domain:marine`

## Background

Predecessors [#2535](https://github.com/vamseeachanta/workspace-hub/issues/2535) and [#2536](https://github.com/vamseeachanta/workspace-hub/issues/2536) established the metadata-first / bounded-summary pattern. The SESA bucket was indexed at catalog level only and remains metadata-only after the deep-extraction first pass. This issue plans (does NOT execute) a curated extraction tranche.

## Scope

### In-scope (planning only)
- Inventory the SESA top-level subdirs (`000 Client Supplied`, `999 Work Space`, `data/`, `analysis/`, `002 Project Filing`) and produce a candidate dossier ≤ 20 artifacts.
- Group candidates by theme: reference studies, free-span / metocean, material specs / data sheets, subsea valves / TBE, logistics / project deliverables.
- Draft a canonical plan file under `docs/plans/` describing approach, TDD/validation, and approval gates.
- Identify which candidates require client / project-owner clearance before any wiki write.

### Out-of-scope
- Raw bulk copy of any SESA file into git, wiki `raw/`, or `_from_elements/` mirroring.
- Broad OCR / full-text extraction.
- Wiki page authoring beyond `wiki/sources/elements-doris-62092-sesa.md` (already present from #2535).
- Any deletion or movement under `/mnt/ace/doris/62092_sesa`.
- Any retention-cleanup activity ([#2534](https://github.com/vamseeachanta/workspace-hub/issues/2534) remains gated until 2026-05-28).

## Allowed paths (read-only)

- `/mnt/ace/doris/62092_sesa/**` — read-only inspection (`ls`, `find`, `stat`, `du`)
- `.planning/intel/elements-to-llm-wiki/**` — predecessor inventory
- `.planning/intel/elements-deep-extraction/**` — predecessor extraction report
- `knowledge/wikis/lng-projects/**` — reference for naming conventions

## Forbidden paths (extraction or write)

- Any write under `/mnt/ace/**` — source drive is immutable for this work
- Any write under `knowledge/wikis/**/raw/` or `knowledge/wikis/**/sources/` beyond the existing Elements page
- Any persisted full-text dump under `.planning/`, `docs/`, or `knowledge/`
- Any cross-stream artifact path (Doris University, DORIS Codes, Woodfibre)

## Deliverable (planning artifact, not raw extraction)

- A bounded extraction dossier at `.planning/intel/elements-overnight-wave/sesa-candidate-dossier.md`
- A first-tranche TSV at `.planning/intel/elements-overnight-wave/sesa-first-tranche.tsv` (≤ 20 rows; columns: priority, theme, content_kind, bytes, absolute_path, rationale, extraction_method, target_wiki_page, risk_note)
- A canonical plan at `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md`
- A wave result summary at `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-1-sesa.md`

## Acceptance criteria (planning-only)

- [ ] Dossier evidence-back every theme grouping (file count + bytes per theme)
- [ ] First-tranche TSV ≤ 20 rows, all paths resolvable on `/mnt/ace`
- [ ] Plan file populates the resource-intelligence section per `docs/plans/_template-issue-plan.md`
- [ ] SESA client / project-owner clearance gate is explicit in the plan
- [ ] Vendor / TBE rows carry an explicit risk note (no leak of bidder confidentiality)
- [ ] Plan flags the `lng-projects` index/log shared-write contention with the Woodfibre stream
- [ ] Issue ends with `status:plan-review` (no `status:plan-approved`)

## Hard rules

- Planning-only. No extraction, no wiki writes, no `/mnt/ace` writes.
- No self-approval. Approval is a separate user-in-loop gate after adversarial review.
- Frontmatter contract from [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) applies if any `wiki/standards/` page is later proposed.
