# Child issue draft — Woodfibre LNG corpus

> **Status:** draft (existing tracker is [#2544](https://github.com/vamseeachanta/workspace-hub/issues/2544); CLOSED 2026-04-29 after bounded planning execution; this draft documents the original planning scope and serves as a template for any successor cycle)
> **Wave:** 2026-04-28 Elements overnight planning wave (umbrella [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540))
> **Corpus:** `/mnt/ace/acma-projects/31522-woodfibre-lng` — 1.8 TB / 10,729 files (largest corpus by bytes)

## Title

`feat(llm-wiki): scout Woodfibre LNG corpus for bounded extraction candidates from Elements`

## Recommended labels

- `priority:medium`
- `cat:data-pipeline`
- `domain:knowledge-management`
- `domain:marine`

## Background

Woodfibre LNG is the largest remaining metadata-only corpus from Elements ingest. The dominant directory is `02.Mooring Analysis` at 1.7 TB (predominantly OrcaFlex `.sim` simulation outputs). `05.Deliverables` (3.2 GB) holds the curated client-facing deliverables. ACMA project — confidentiality / project-owner clearance required before any wiki write.

## Scope

### In-scope (scout-only / pointer-only)
- Tree inventory at depth ≤ 3 for `05.Deliverables`, `01.Stability`, `04.Model Test Correlation`.
- Pointer / scout candidate list ≤ 15 artifacts (NOT extraction targets — these are pointers for a future plan).
- Confidentiality gate explicit in plan: extraction blocked until project-owner clearance recorded.
- Plan flags shared `lng-projects` index/log contention with the SESA stream.

### Out-of-scope
- Any inspection of `02.Mooring Analysis/**` `.sim` files (binary, large, low planning value).
- Any extraction whatsoever — Woodfibre is scout/pointer only this wave.
- Any wiki write before clearance recorded.
- Any abstract / quote / figure copy.
- Cross-stream paths (SESA, Doris University, DORIS Codes).

## Allowed paths (read-only)

- `/mnt/ace/acma-projects/31522-woodfibre-lng/05.Deliverables/**` — listings only
- `/mnt/ace/acma-projects/31522-woodfibre-lng/01.Stability/**` — listings only
- `/mnt/ace/acma-projects/31522-woodfibre-lng/04.Model Test Correlation/**` — listings only

## Forbidden paths (extraction or write)

- Any write under `/mnt/ace/**`
- `02.Mooring Analysis/**` content reads (binary `.sim` files; size-prohibitive)
- Any wiki write before clearance gate
- Cross-stream artifact paths

## Deliverable

- Scout plan at `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md`
- Candidates TSV at `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv` (≤ 15 rows; pointer-only, no extraction promise)
- Canonical plan at `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md`
- Wave result at `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md`

## Acceptance criteria (planning-only)

- [ ] Scout list ≤ 15 candidates, all from `05.Deliverables` / `01.Stability` / `04.Model Test Correlation`
- [ ] Plan explicitly partitions "scout pointer-only" (this issue) from "extraction" (separate future issue)
- [ ] Confidentiality / project-owner clearance recorded as hard prerequisite for any wiki write
- [ ] `02.Mooring Analysis/**` carries explicit no-touch banner
- [ ] Plan flags `lng-projects` index/log contention vs SESA stream — sequential execution required
- [ ] Issue ends `status:plan-review`

## Hard rules

- Pointer-only. No extraction. No abstracts. No quotes. No figures.
- 1.7 TB `02.Mooring Analysis` is OUT — do not even enumerate file lists for that subtree.
- Wiki writes require explicit ACMA / project-owner clearance recorded *before* any plan-approved label is applied.
