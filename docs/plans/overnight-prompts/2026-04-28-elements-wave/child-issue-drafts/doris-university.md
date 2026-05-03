# Child issue draft — Doris University training corpus

> **Status:** draft (existing tracker is [#2542](https://github.com/vamseeachanta/workspace-hub/issues/2542); CLOSED 2026-04-29 after bounded execution; this draft documents the original planning scope and serves as a template for any successor cycle)
> **Wave:** 2026-04-28 Elements overnight planning wave (umbrella [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540))
> **Corpus:** `/mnt/ace/doris/training` — 11 GB / 1,129 files (excluding `_from_elements/` provenance staging)

## Title

`feat(llm-wiki): plan curated Doris University training corpus extraction from Elements`

## Recommended labels

- `priority:medium`
- `cat:documentation`
- `domain:knowledge-management`
- `domain:training`

## Background

The Doris University catalog covers subsea production systems training. Top-level themed directories (`1.00`–`1.03 Subsea Production / Control / Umbilical / Installation`, plus `Corrosion`, `FreeSpan`, `FieldLayout`, `Flexible Pipe`, `Rigid Jumper`, `ENI Training`, `DE Presentations`, `draft presentations`) suggest a structured curriculum amenable to a metadata-first taxonomy.

## Scope

### In-scope (planning only)
- Build a taxonomy mapping training tracks to wiki concepts under the `engineering` wiki domain.
- Propose a first tranche of ≤ 20 artifacts as concept-shell anchors and source pointer pages.
- Draft canonical plan with TDD-style validation (lint pass on touched domain, test additions).

### Out-of-scope
- OCR or full-text extraction of slide decks / movies / PDFs.
- Embedded chart / figure / movie copy into wiki or git.
- Standards excerpts (training material may quote standards — those clauses are NOT republished).
- Any write to `/mnt/ace/doris/training/**`.

## Allowed paths (read-only)

- `/mnt/ace/doris/training/**`
- `.planning/intel/elements-to-llm-wiki/**`
- `knowledge/wikis/engineering/**` — reference layout for concept / source pages

## Forbidden paths (extraction or write)

- Any write under `/mnt/ace/**`
- `knowledge/wikis/**/raw/`
- Any persisted full-text deck extraction
- Cross-stream artifact paths (SESA, DORIS Codes, Woodfibre)

## Deliverable

- Taxonomy at `.planning/intel/elements-overnight-wave/doris-university-taxonomy.md`
- First-tranche TSV at `.planning/intel/elements-overnight-wave/doris-university-first-tranche.tsv`
- Canonical plan at `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md`
- Wave result at `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md`

## Acceptance criteria (planning-only)

- [ ] Taxonomy maps every top-level training subdir to either a target concept page or an explicit deferral
- [ ] First-tranche rows resolvable on `/mnt/ace` and small enough for metadata-only treatment
- [ ] Plan defines RED test that fails before pages exist and GREEN test after
- [ ] Plan respects standards-namespace contract (standards-quoted slides do NOT produce `engineering-standards/` pages from this stream)
- [ ] Issue ends `status:plan-review`

## Hard rules

- No OCR. No full-text. No figures. No movies.
- Concept pages are *shells* with provenance pointers — the plan describes scaffolding, not content.
- Pre-existing frontmatter warnings on legacy `engineering` wiki pages are out of scope (#2535 surfaced them).
