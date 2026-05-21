# Plan for llm-wiki#103: [corpus-ingest] marine-engineering — class societies + IMO regulatory

> **Status:** draft (pending adversarial review)
> **Complexity:** T3 (multi-publisher corpus ingest; 13 publishers; 50+ projected subissues; cross-repo citation dependencies)
> **Date:** 2026-05-20
> **Issue:** [llm-wiki#103](https://github.com/vamseeachanta/llm-wiki/issues/103)
> **Umbrella:** [workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774) — private llm-wiki corpus-ingest program (post-2026-05-20 privacy flip)
> **Review artifacts (to be created):** `scripts/review/results/2026-05-20-plan-103-claude.md` | `...-codex.md` | `...-gemini.md`
> **Authorization scope:** llm-wiki-side writes ONLY after user approves this plan + applies `status:plan-approved` to [llm-wiki#103](https://github.com/vamseeachanta/llm-wiki/issues/103). Per-publisher subissues will spawn their own per-subissue plans before any per-publisher ingest begins; this epic plan does NOT authorize any per-publisher writes by itself.

---

## Goal

Bulk-ingest the 13 marine-engineering publishers from `/mnt/ace/acma-codes/` into the private `vamseeachanta/llm-wiki` repo at the same fidelity demonstrated by the OCIMF MEG3/MEG4 Annex A pilot (llm-wiki commit `707af307`). "Ingest complete" for this epic means:

1. Each publisher in scope has at least one canonical standards page under `wikis/marine-engineering/wiki/standards/<code-id>.md` with the required frontmatter (`code_id`, `publisher`, `revision`, `visibility: private-llm-wiki`, `sources:`) per [.claude/rules/codes-standards-data-routing.md](https://github.com/vamseeachanta/workspace-hub/blob/main/.claude/rules/codes-standards-data-routing.md).
2. Where the publisher PDFs contain digitizable tabular data (coefficient tables, scantling tables, equipment-number tables, sign-convention figures), that data lands as CSV (or YAML where appropriate) under `wikis/marine-engineering/wiki/datasets/<code-id>/` with a per-dataset `README.md`.
3. Verbatim convention/clause text quoted with attribution where it anchors interpretive guidance (the MEG3/MEG4 §A2 pattern).
4. Each publisher has at least one per-publisher subissue spawned off this epic with its own plan-review/plan-approved gate; publishers with multiple distinct standards have one subissue per standard (or per coherent standard-family).
5. Citation slugs from the standards pages are usable as resolver targets by `digitalmodel.citations.registry` per the calc-citation contract.

This epic plan does NOT ingest content. It defines phases, prioritization, per-publisher subissue spawning rules, acceptance criteria, and risks. Per-publisher implementation is deferred to subissue plans (one per standard / standard-family).

---

## Resource Intelligence Summary

### Existing repo code

This is a content-ingest epic, not a code-change epic. Relevant existing surfaces:

- **EXISTS** `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg3.md` and `ocimf-meg4.md` — standards-page pattern reference (frontmatter + verbatim §A2 sign convention + dataset cross-link).
- **EXISTS** `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/TEMPLATE.md` — standards-page skeleton.
- **EXISTS** `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/datasets/ocimf-meg4-annex-a/` — 3 CSVs (`data-5a-9a.csv`, `data-10a-14a.csv`, `data-16a-19a.csv`) + `README.md` — the dataset-page pattern reference (108×26, 110×35, 82×45 wide-block layout).
- **EXISTS** `/mnt/local-analysis/digitalmodel/src/digitalmodel/citations/registry.py` — citation resolver. Standards pages from this epic become resolver targets.
- **EXISTS** `/mnt/local-analysis/digitalmodel/src/digitalmodel/orcaflex/mooring_design.py:check_mbl_with_safety_factor` — live DNV-OS-E301 citation pilot per [workspace-hub#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685). DNV-OS-E301 is in the DNV Rules folder (`/mnt/ace/acma-codes/DNV Rules/`); the standards page for it must align with this pilot's slug expectations.

### Standards

Verified existing wiki coverage at `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/`:

| Standard | Status | Source |
|---|---|---|
| OCIMF MEG3 | done (pilot, 2026-05-20) | `wikis/marine-engineering/wiki/standards/ocimf-meg3.md` |
| OCIMF MEG4 | done (pilot, 2026-05-20) | `wikis/marine-engineering/wiki/standards/ocimf-meg4.md` |
| OCIMF MEG4 Annex A | done (pilot, 2026-05-20) | `wikis/marine-engineering/wiki/datasets/ocimf-meg4-annex-a/` |
| DNV-OS-E301 (mooring) | citation slug live in digitalmodel | [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685); **wiki page may not exist yet** — gap to confirm in Phase 1 |
| All other marine-engineering publisher standards | **GAP** — no wiki coverage | (this epic's scope) |

### Documents consulted

- [llm-wiki#103](https://github.com/vamseeachanta/llm-wiki/issues/103) issue body — defines publisher list and target wiki structure.
- [workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774) — umbrella corpus-ingest program; this epic is one of ~8 domain epics under it.
- [.claude/rules/codes-standards-data-routing.md](https://github.com/vamseeachanta/workspace-hub/blob/main/.claude/rules/codes-standards-data-routing.md) — post-2026-05-20 routing rule; private llm-wiki is canonical target; PDFs stay at `/mnt/ace/`.
- [.claude/rules/calc-citation-contract.md](https://github.com/vamseeachanta/workspace-hub/blob/main/.claude/rules/calc-citation-contract.md) — citation emission for standards-derived constants; wiki pages from this epic are the resolver targets.
- `docs/plans/2026-05-20-issue-616-ocimf-polar-vessel-force-overlay.md` (digitalmodel) — structural reference for plans that touch OCIMF-class data.
- `docs/plans/2026-05-20-issue-2746-llm-wiki-acma.md` (workspace-hub) — sibling plan in the same 2026-05-20 corpus-ingest wave.
- `docs/plans/2026-05-20-issue-2768-epic-ocimf-meg3-meg4-closeout.md` — OCIMF closeout plan (downstream consumer of the OCIMF pilot).

### Resource intel — publisher inventory at `/mnt/ace/acma-codes/`

Verified 2026-05-20 via `find /mnt/ace/acma-codes/<publisher>/ -type f | wc -l`:

| Publisher | Files | Top-level shape | Digitizable tables/figures? | Notes |
|---|---:|---|---|---|
| **ABS Rules** | 531 | 82 subdirectories (Accommodation, Ballast Water, Bulk Carriers, Coating, Conditions of Classification, …) + 17 top-level PDFs | YES — scantling tables, IMO Regulatory Matrix, equipment-number tables | Largest publisher. ABS publishes 100+ distinct Rule documents; will require careful sub-scoping. |
| **DNV Rules** | 2892 | 10 subdirectories (`2001-2002 DNV FPSO Rules`, `2002 Light Craft`, `2010 DNV`, …) + thousands of OS/RP/CN PDFs by year | YES — OS-* standards have coefficient tables, charts, equation tables (OS-E301 mooring, OS-C301 stability, RP-E303 suction anchors, etc.) | **Largest count by far.** Needs decomposition by document class (OS / RP / CN / Ship Rules) before per-document subissue spawning. |
| **Bureau Veritas** | 8 | Flat directory | LIMITED — mostly bound rule volumes ("Classification of Steel Ships", "Offshore Units"); few digitizable tables visible at the top-level PDF set | Small surface; one or two per-document subissues likely sufficient. |
| **Germanischer Lloyd** | 8 | Flat directory | LIMITED — historical (pre-2013 merger with DNV); mostly TOCs and section excerpts | Small. Mostly historical; GL was merged into DNV GL in 2013, so most current GL-as-publisher work is legacy. Worth one publisher-overview page + per-document subissues only where content is non-superseded. |
| **Lloyd's Register** | 40 | 3 subdirectories + 37 PDFs (2002–2013 Ship Rules Parts 3/4/7, FOIFL, Code for Lifting Appliances, shipbuilding+repair quality standard, errata, Classification News) | YES — Ship Rules have scantling/section-modulus tables, Code for Lifting Appliances has load-factor tables | Medium. |
| **IACS** | 11 | Flat directory + 1 `Thumbs.db` | YES — CSR Common Structural Rules for Double Hull Oil Tankers and Bulk Carriers have extensive parametric tables; UR (Unified Requirements) PDFs contain digitizable equation tables | Medium. CSR is the high-value content; UR documents are short and dense. |
| **MARPOL** | 2 | Flat directory | LIMITED — only 2 PDFs (Oil Fuel Tank Protection §12A; EIAPP Certification Fact Sheet) | **THIN at `/mnt/ace/`.** Real MARPOL corpus (Annexes I–VI) is not present; must be sourced from IMO publication catalogue or treated as a gap. Flag as a Phase 2 blocker. |
| **IMO** | 463 | 40 subdirectories (Automated Identification System, Ballast Water Management, Bulk Carriers, …) + top-level Assembly Resolution / MSC Circular PDFs | YES — Resolution numerical tables, MSC Circular performance standards, Assembly Resolution amendments | Large surface, well-organized. Includes SOLAS-adjacent material indirectly via MSC Resolutions. |
| **MSC** | 1 | Flat directory | NO — single PDF is a US Navy MSC (Military Sealift Command) general technical requirements doc, **not IMO MSC** | **MISLABELED in `/mnt/ace/`.** The folder named "MSC" is US Navy MSC, not IMO MSC. Real IMO MSC Resolutions/Circulars live under `/mnt/ace/acma-codes/IMO/` (top-level PDFs and `Annex` subdirectories). Note this in the plan; treat "IMO MSC circulars" as IMO-folder content, not MSC-folder content. |
| **IMCA** | 2 | Flat directory | LIMITED — workboat inspection template + Common Marine Inspection Document | THIN. May need supplemental sourcing from IMCA publication index for guidance documents (M-series, D-series). |
| **SIGTTO** | 14 | Flat directory | YES — guidance documents (Quick Release Hooks, LNG rollover prevention, Purging Hard Arms, HM-fibre mooring lines, etc.); LSA Hand Book is a `.doc` file (not PDF) | Small but high-value. SIGTTO covers LNG/LPG operational guidance. |
| **USCG** | 520 | 13 subdirectories (`ADA Rules`, `CFR`, `Load Lines`, `Manuals & Plans`, `Marine Safety Manual`, `Military Standards`, `MSC Guidelines`, `MTN`, `Nav Rules`, `NVIC's`, `Reports & Miscellaneous`, `Small Boat regulations`) + 2 top-level PDFs | YES — CFR cites are tabular, NVIC's have numerical tables, MSC Guidelines have stability and load-line tables | Large. **Routing nuance:** USCG NVICs post-2010 and CFR 33/46 are arguably public-domain per [routing rule §6](https://github.com/vamseeachanta/workspace-hub/blob/main/.claude/rules/codes-standards-data-routing.md); confirm visibility tier per-document during the USCG subissue plan rather than blanket private. |
| **Bahamas Maritime Auth** | 4 | Flat directory | LIMITED — 4 bulletins (Minimum Safe Manning, EU Passenger Registration, Ballast Water Mgmt, National Requirements 2016) | THIN. One publisher-overview page + minimal per-bulletin pages. |

**Total files in scope:** ≈4,496 files across 13 publishers. Real "standards documents in scope" is much smaller (many of those files are session-of-rule TOCs, errata, indexes, datasheets); per-publisher inventory work in each Phase 1 subissue will collapse the file count to a standards count.

### Gaps identified

1. **DNV-OS-E301 wiki page** likely missing (the pilot citation slug at [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685) may bind to a non-yet-existing wiki page). **Verify in Phase 1 first action; if missing, the DNV subissue's first deliverable is creating it to backfill the live citation resolver.**
2. **MARPOL corpus is thin at `/mnt/ace/`** (2 files only). Real MARPOL Annexes I-VI are not present; either source from IMO publication catalogue (which is in `/mnt/ace/acma-codes/IMO/`) or treat as a Phase 2 publisher-gap that needs supplemental PDF acquisition before ingest.
3. **IMO MSC folder mislabel** — `/mnt/ace/acma-codes/MSC/` is US Navy MSC, not IMO MSC. IMO MSC content lives at `/mnt/ace/acma-codes/IMO/`. Don't ingest the MSC folder under marine-engineering — route the single USN MSC doc to maritime-regulatory (issue #105 territory) or out-of-scope.
4. **IMCA and Bahamas Maritime Auth are sparse** at `/mnt/ace/`. Acceptance for these publishers will be "everything at `/mnt/ace/` is ingested; further coverage is out-of-scope-for-this-epic and flagged as supplemental-source gaps for future enhancement."
5. **Edition drift:** several DNV/ABS PDFs in `/mnt/ace/` are years out of date (e.g., DNV 2003 hull structures, ABS 2013 IMO Regulatory Matrix). Standards pages must record the `revision:` frontmatter for the edition of the PDF actually on disk, NOT the current latest edition. Per-document subissue plans need to flag known-stale editions and decide whether to seek a current edition before ingest.
6. **No existing per-publisher subissues yet.** This epic spawns them; they currently do not exist on the llm-wiki repo.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-20T22:30:00Z via `gh issue view`):

- [llm-wiki#103](https://github.com/vamseeachanta/llm-wiki/issues/103) — OPEN — `documentation`, `priority:medium`, `cat:data` — title confirms scope.
- [workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774) — OPEN — `documentation` — umbrella.
- [workspace-hub#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685) — DNV-OS-E301 citation pilot (referenced; live).
- [digitalmodel#616](https://github.com/vamseeachanta/digitalmodel/issues/616) — OPEN — OCIMF polar overlay (downstream consumer of OCIMF pilot pattern).

**File existence** (`ls -la` 2026-05-20T22:30:00Z):

- EXISTS: `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg3.md`
- EXISTS: `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/ocimf-meg4.md`
- EXISTS: `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/standards/TEMPLATE.md`
- EXISTS: `/mnt/local-analysis/llm-wiki/wikis/marine-engineering/wiki/datasets/ocimf-meg4-annex-a/` (4 files: 3 CSVs + README.md)
- EXISTS: `/mnt/ace/acma-codes/{ABS Rules, DNV Rules, Bureau Veritas, Germanischer Lloyd, Lloyds Register, IACS, MARPOL, IMO, MSC, IMCA, SIGTTO, USCG, Bahamas Maritime Auth}/` (13 publisher directories — file counts above)
- MISSING (this epic does NOT create directly — spawned subissues create): `wikis/marine-engineering/wiki/standards/dnv-os-e301.md`, `…/abs-*.md`, `…/dnv-*.md`, …
- MISSING (spawned per per-publisher subissue): `wikis/marine-engineering/wiki/datasets/<code-id>/` directories.

**Reproduction proofs:** N/A — this is a corpus-ingest planning epic with no runtime failure to reproduce. The closest equivalent is the OCIMF pilot itself, which already shipped (llm-wiki `707af307`) and demonstrates the ingest pattern works against at least one marine-engineering publisher.

**Reproduce step for THIS epic** (planning-time sanity check, executed during adversarial review, not during planning):

Pick the smallest non-OCIMF marine publisher with non-trivial digitizable content and walk through the ingest steps end-to-end as a verification of the pattern's portability. **Recommended pilot-target-2: SIGTTO** (14 files, high-value LNG/LPG content, modest enough to fully process inside one subissue without overrunning a single review cycle). If SIGTTO ingest goes through cleanly end-to-end during Phase 1, it demonstrates the OCIMF pattern is publisher-agnostic. Acceptance for this reproduce step: at least one SIGTTO standards page lands with full frontmatter + verbatim quote + at least one digitized table where applicable, with a per-document subissue plan reviewed and approved.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-20-issue-103-llm-wiki-marine-engineering-corpus.md` |
| Plan review — Claude | `scripts/review/results/2026-05-20-plan-103-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-20-plan-103-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-20-plan-103-gemini.md` |
| Per-publisher subissue plans (spawned during execution) | `llm-wiki:docs/plans/2026-MM-DD-issue-<sub-NNN>-<publisher>-<scope>.md` |
| Per-publisher standards pages (created by subissues) | `llm-wiki:wikis/marine-engineering/wiki/standards/<code-id>.md` |
| Per-publisher datasets (created by subissues) | `llm-wiki:wikis/marine-engineering/wiki/datasets/<code-id>/` |
| Index/landing update | `llm-wiki:wikis/marine-engineering/wiki/index.md` (one row per landed publisher) |

---

## Deliverable

A phased corpus-ingest plan for 13 marine-engineering publishers, with per-publisher subissues spawned in priority order, each subissue producing a standards page (or pages) and any digitizable dataset under the private llm-wiki, in alignment with the OCIMF MEG3/MEG4 Annex A pilot pattern.

---

## Phased plan

**Phasing rationale:** Phase by leverage (citation-resolver-binding) and operational closure (downstream consumers waiting), NOT alphabetical. Phase 1 targets the publishers whose data is already being consumed by live digitalmodel calc modules (DNV-OS-E301 mooring) and the pattern-validation target (SIGTTO). Phase 2 closes the class-society set. Phase 3 closes IMO regulatory. Phase 4 closes industry guidance and flag-state.

### Phase 1 — High-leverage class society + pattern-validation (sequence: DNV → SIGTTO)

Publishers: **DNV Rules** (priority 1 — citation-resolver backfill), **SIGTTO** (priority 2 — pattern-validation, smallest publisher with non-trivial content).

- Per-publisher subissue spawn rule (Phase 1): one subissue per standard-family. For DNV, this means at least one subissue per OS-family (OS-E301, OS-C301, OS-C101, RP-E303, RP-C205) — projected 5–10 Phase-1 DNV subissues. For SIGTTO, one subissue covering the publisher's full 14-document `/mnt/ace/` set (it's small enough).
- Subissue title pattern: `[corpus-ingest] marine-engineering/<publisher> — <standard-family-or-doc>` (e.g., `[corpus-ingest] marine-engineering/dnv — OS-E301 position mooring`).
- Subissue body must reference: this epic ([llm-wiki#103](https://github.com/vamseeachanta/llm-wiki/issues/103)), umbrella ([workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774)), routing rule, calc-citation contract, and (for DNV-OS-E301) the live citation pilot [workspace-hub#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685).
- Phase 1 acceptance gate: DNV-OS-E301 wiki page lives at `wikis/marine-engineering/wiki/standards/dnv-os-e301.md` AND `digitalmodel.citations.registry.get_mooring_safety_factor()` resolves against it without `CitationResolutionError` when run inside workspace-hub context. SIGTTO standards page(s) demonstrate the OCIMF pattern works on a non-OCIMF publisher end-to-end.

### Phase 2 — Class society sweep (parallel-eligible, alphabetical within phase): ABS → Bureau Veritas → Germanischer Lloyd → IACS → Lloyd's Register

- Per-publisher subissue spawn rule (Phase 2): one subissue per coherent publisher segment. ABS has 82 subdirectories — Phase 2 ABS subissues are scoped by subdirectory cluster (e.g., "ABS Bulk Carriers", "ABS Tankers", "ABS Mooring & Equipment"), not per-PDF. Bureau Veritas, GL, Lloyd's, IACS are small enough that 1–3 subissues per publisher suffice.
- Subissues in Phase 2 are eligible for parallel-readonly planning (multiple per-publisher plans can be drafted concurrently by different providers/sessions) but each subissue's implementation still gates on its own `status:plan-approved` per the standard workflow.
- **GL caveat:** GL was merged into DNV GL (2013) — record this in the GL publisher-overview page and note that current GL-as-publisher work is mostly legacy. Don't replicate DNV content under a GL slug.
- **CSR caveat:** IACS Common Structural Rules for Double Hull Oil Tankers and Bulk Carriers are jointly authored with class societies; the CSR PDFs in `/mnt/ace/acma-codes/IACS/` are the authoritative IACS-slug source. If those CSRs also live under ABS/DNV/BV trees, cross-link from each class-society page to the IACS CSR page; don't duplicate the content.

### Phase 3 — IMO regulatory (sequence: IMO → MARPOL [if sourceable])

Publishers: **IMO** (priority — large, well-organized, contains SOLAS-adjacent MSC Resolutions), **MARPOL** (THIN at `/mnt/ace/` — Phase 3 second priority).

- Per-publisher subissue spawn rule (Phase 3): one subissue per IMO publication class. IMO has 40 subdirectories — scope subissues by topical cluster: "IMO SOLAS-MSC Resolutions", "IMO Ballast Water Management", "IMO Bulk Carriers", etc.
- MARPOL is thin at `/mnt/ace/`; Phase 3 MARPOL subissue first deliverable is a publisher-overview page that flags the source gap explicitly and proposes either (a) using IMO publication catalogue (already at `/mnt/ace/acma-codes/IMO/`) for the MARPOL Annex resolutions, or (b) treating MARPOL as a corpus-gap to be closed in a future enhancement issue.

### Phase 4 — Industry guidance + flag-state (sequence: USCG marine portions → IMCA → Bahamas Maritime Auth)

- **USCG**: large surface (520 files, 13 subdirs). Scope subissues by subdirectory: "USCG NVICs", "USCG CFR 33/46 marine portions", "USCG MSC Guidelines", "USCG Marine Safety Manual". **Visibility-tier nuance:** per [routing rule §6](https://github.com/vamseeachanta/workspace-hub/blob/main/.claude/rules/codes-standards-data-routing.md), some USCG content (federal regulations) may be public-domain; per-subissue plan decides visibility tier with the `visibility: private-llm-wiki` default and explicit public-domain confirmation needed to deviate.
- **IMCA** + **Bahamas Maritime Auth**: small surfaces; one publisher-overview page each + per-document standards pages with full acknowledgment that `/mnt/ace/` coverage is partial.

### Phase 5 — Cross-link audit and citation-resolver integration (after Phases 1–4)

- Audit `wikis/marine-engineering/wiki/index.md` for completeness; one entry per landed publisher.
- Audit the digitalmodel citation registry for slug collisions/resolution failures across all newly-landed wiki pages.
- Close [llm-wiki#103](https://github.com/vamseeachanta/llm-wiki/issues/103) only after all 13 publishers have at least one landed standards page AND citation resolution is verified.

---

## Per-publisher subissue spawning rules

- Subissues are spawned **at the start of each phase**, NOT all at once at the start of the epic. Spawning all 50+ at planning time would create a stale-subissue backlog and freeze design decisions before later-phase publishers' inventories have been validated.
- Each subissue created from this epic gets:
  - `[corpus-ingest] marine-engineering/<publisher>` prefix in the title (so they're filterable as a set under llm-wiki)
  - Body references back to this epic ([llm-wiki#103](https://github.com/vamseeachanta/llm-wiki/issues/103)) AND umbrella ([workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774))
  - Body cites the routing rule and the OCIMF pilot pattern (`wikis/marine-engineering/wiki/datasets/ocimf-meg4-annex-a/`) as the reference shape
  - Labels: `documentation`, `cat:data`, `priority:medium` (or higher if downstream-consumer-blocking)
  - Initial state: `status:needs-plan` (not `status:plan-review` — each subissue gets its own plan drafted before review)
- Per-publisher subissue plans live at `llm-wiki:docs/plans/2026-MM-DD-issue-<sub-NNN>-<publisher>-<scope>.md`. They are **not** in workspace-hub; they're in the llm-wiki repo where the writes will land.
- This epic does NOT enumerate every subissue title in advance — projected count is ~50, but the actual count emerges from per-phase publisher-inventory passes. **Estimated subissue counts per publisher:** DNV 5–10, SIGTTO 1, ABS 6–10, BV 1–2, GL 1–2, IACS 2–4, Lloyd's 2–4, IMO 6–10, MARPOL 1, USCG 4–6, IMCA 1, Bahamas 1. Total ≈30–50.

---

## TDD Test List

Most of this epic's work is content-ingest, not code; standard pytest-based TDD does not apply directly. The corresponding "test surface" is:

| Test name | What it verifies | How |
|---|---|---|
| `test_standards_page_frontmatter_<code-id>` | Each new standards page has the required frontmatter fields (`code_id`, `publisher`, `revision`, `visibility: private-llm-wiki`, `sources:`) | YAML-parse the frontmatter; assert field presence and type. Implementation pattern from `digitalmodel/tests/citations/` if a similar harness exists in llm-wiki repo — otherwise establish a small `tests/test_standards_pages.py` in llm-wiki as part of Phase 1. |
| `test_citation_resolves_<code-id>` | `digitalmodel.citations.registry.get_<slug>()` returns a value without `CitationResolutionError` against the new wiki page | Workspace-hub-tracked test that calls the resolver with `LLM_WIKI_PATH` pointing to the local llm-wiki clone. |
| `test_dataset_csv_schema_<code-id>` | Each landed CSV under `datasets/<code-id>/` parses cleanly and the per-dataset README's "Schema" section's claimed row/col counts match the actual CSV. | pandas-read assertions; runs in CI on the llm-wiki repo. |
| `test_no_raw_pdf_in_repo` | No raw vendor PDF lands in the llm-wiki repo (PDFs must stay at `/mnt/ace/`) | Pre-commit hook or CI grep for `*.pdf` under `wikis/marine-engineering/`. |

Per-publisher subissue plans inherit this test surface and add publisher-specific assertions (e.g., for DNV-OS-E301: assert the safety factor 1.67 matches the citation registry value).

---

## Acceptance Criteria

- [ ] Each of the 13 publishers in scope has at least one standards page under `wikis/marine-engineering/wiki/standards/` with full frontmatter (`code_id`, `publisher`, `revision`, `visibility: private-llm-wiki`, `sources:`).
- [ ] Each publisher with digitizable tabular data has at least one dataset directory under `wikis/marine-engineering/wiki/datasets/<code-id>/` containing CSV (or YAML) files and a `README.md` describing the schema and provenance.
- [ ] Verbatim convention/clause text quoted (with attribution to publisher + section) wherever an interpretive section depends on the standard's exact wording (OCIMF §A2 pattern).
- [ ] DNV-OS-E301 wiki page exists and resolves correctly against the live citation pilot at [workspace-hub#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685) — i.e., `digitalmodel.citations.registry.get_mooring_safety_factor()` does not raise `CitationResolutionError` when `LLM_WIKI_PATH` points to a clone of llm-wiki.
- [ ] No raw vendor PDF has been committed to the llm-wiki repo. PDFs remain canonical at `/mnt/ace/acma-codes/<publisher>/`.
- [ ] `wikis/marine-engineering/wiki/index.md` lists one entry per landed publisher with a brief topical summary.
- [ ] All per-publisher subissues spawned by this epic are either closed (landed) or explicitly deferred with a Phase 5 note.
- [ ] Adversarial review of THIS plan has APPROVE / MINOR verdicts (no unresolved MAJOR) across Claude / Codex / Gemini before user approval.
- [ ] User approves THIS plan via `gh issue edit 103 --add-label status:plan-approved` on the llm-wiki repo.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | (to be populated after r1 review dispatched) |
| Codex | PENDING | (to be populated after r1 review dispatched) |
| Gemini | PENDING | (to be populated after r1 review dispatched) |

**Overall result:** PENDING — not yet reviewed.

### Pre-emptive defect surface (self-review before dispatch)

These are defects the plan author has already considered and addressed inline so adversarial reviewers can focus on what's missed:

1. **Over-ingestion risk:** the 13-publisher × multi-standard surface could explode to 100+ subissues if one-per-PDF is the default. Mitigation: per-publisher subissue spawn rule scopes by standard-family / subdirectory cluster, NOT per-PDF. Projected total: ~30–50 subissues.
2. **Citation-slug collision:** if multiple per-publisher subissues land standards pages with the same `code_id` (e.g., a hypothetical `dnv-os-e301` slug collision with an existing slug somewhere in the wiki), the citation resolver will silently bind to the first-found page. Mitigation: pre-Phase-1, do a `grep -r code_id: wikis/` audit; the canonical slug schema is `<publisher>-<doc-id>` (e.g., `dnv-os-e301`, `abs-mooring-equipment-1996`).
3. **Frontmatter drift:** the routing rule's frontmatter contract (drop `extraction_policy: metadata-only` + `raw_copy_allowed: false`; add `visibility: private-llm-wiki`) means OLDER existing wiki pages (pre-privacy-flip) carry stale fields. Mitigation: out-of-scope for this epic; tracked separately as a frontmatter-migration cleanup. Per-publisher subissue plans should NOT silently fix older pages; flag them.
4. **Missing cross-references:** OCIMF MEG4 §A2 sign convention is identical to MEG3 §A1; the MEG4 page cross-links to MEG3. The same cross-link discipline must apply to other publishers' edition-pairs (e.g., ABS Rules editions year-over-year). Per-publisher subissue plans must enumerate edition cross-links explicitly.
5. **Edition mismatch between `/mnt/ace/` PDFs and the citation resolver expectations:** if `digitalmodel.citations.registry` expects a 2018 DNV-OS-E301 but `/mnt/ace/` has only a 2008 copy, the resolver test fails. Mitigation: each per-publisher subissue's first action is `pdfinfo` on the source PDF to record the edition, and the standards page's `revision:` frontmatter must match exactly.
6. **MARPOL/IMCA/Bahamas thin coverage** is acknowledged explicitly as a gap rather than fabricating coverage from absent PDFs. Per-publisher subissue plans must close-as-incomplete with a supplemental-source follow-on issue rather than hallucinating content.
7. **`/mnt/ace/acma-codes/MSC/` mislabel:** the folder is US Navy MSC, not IMO MSC. This epic does NOT ingest the MSC folder under marine-engineering. The single USN MSC PDF either routes to maritime-regulatory (issue #105) or is treated as out-of-scope.

---

## Risks and Open Questions

- **Risk — copyright posture per publisher:** most publishers in scope are vendor-licensed (DNV, ABS, BV, GL, Lloyd's, IACS, OCIMF). USCG and Bahamas Maritime Auth content includes federal/flag-state regulatory material that may be public-domain in part. Per routing rule §6, per-document visibility tier decisions go in per-publisher subissue plans — default `private-llm-wiki`, deviate only with explicit public-domain confirmation.
- **Risk — edition drift between `/mnt/ace/` PDFs and digitized tables:** the OCIMF pilot cross-validated MEG3 figures against the MEG4 reprint and recorded the cross-validation in the dataset README. The same discipline must apply per publisher; per-subissue plans must explicitly record which edition's data is digitized when multiple editions exist.
- **Risk — scale:** 13 publishers × multiple standards = projected 30–50 subissues. Realistic completion horizon is months, not days. This epic should NOT have a single completion deadline; close-by-phase.
- **Risk — pattern-portability untested for non-tabular publishers:** the OCIMF pilot tested the pattern against a highly-tabular publisher. Publishers like SIGTTO or IMCA are mostly prose-guidance; the digitization step may not apply. SIGTTO is the Phase 1 portability test (recommended above). If SIGTTO ingest reveals the pattern is genuinely tabular-only, the plan must revise to a "tabular publishers" path and a "prose-only publishers" path.
- **Open — DNV-OS-E301 wiki page existence:** does the page already exist under some other slug? Verify in Phase 1 first action via `find /mnt/local-analysis/llm-wiki/wikis -name "*e301*" -o -name "*OS-E301*"`. If found, the DNV subissue's first deliverable is migrating/normalizing the slug, not creating a new page.
- **Open — IACS CSR routing:** the IACS Common Structural Rules are jointly authored with class societies. Should the CSR live as IACS-slug only (with class-society pages cross-linking), or also under each class society's tree? Defer decision to the IACS Phase 2 subissue plan.
- **Open — workspace-hub-side citation-resolver tests:** the `test_citation_resolves_<code-id>` tests can live either in workspace-hub (current home of citation registry tests) or in llm-wiki (where the pages land). Default to workspace-hub but flag for user decision during plan review.
- **Open — should the index.md update land per-phase or at Phase 5?** Per-phase is more visible incrementally but creates merge-conflict surface across parallel subissues. Defer to per-subissue plan decision; the safer default is "update index.md as part of each subissue's closeout."

---

## Out of scope

- Per-publisher implementation details — deferred to subissue plans (one plan per subissue, gated by `status:plan-approved` independently).
- Non-marine publishers — those have their own domain epics (civil-structural [llm-wiki #104], drilling-engineering [#107], etc., per [workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774) subissue tree).
- Raw vendor PDF redistribution — PDFs ALWAYS stay at `/mnt/ace/acma-codes/<publisher>/`.
- Client-project content — handled separately under client-engagement issues (B1528, SIROCCO, acma-projects).
- Frontmatter migration of pre-privacy-flip existing wiki pages — out of scope; tracked separately if surfaced during this epic.
- The single US Navy MSC PDF at `/mnt/ace/acma-codes/MSC/` — folder is mislabeled; routes to maritime-regulatory ([llm-wiki #105](https://github.com/vamseeachanta/llm-wiki/issues/105)) or out-of-scope entirely.
- Supplemental sourcing of missing MARPOL Annexes from non-`/mnt/ace/` sources — flagged as a gap, not closed in this epic.

---

## Related

- Umbrella: [workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774) — private llm-wiki corpus-ingest program
- OCIMF pilot reference (already shipped): [digitalmodel#616](https://github.com/vamseeachanta/digitalmodel/issues/616) — OCIMF polar overlay; downstream consumer of OCIMF pilot
- OCIMF pilot landing: llm-wiki commit `707af307` — Annex A corpus + boundary drop
- DNV-OS-E301 citation pilot (LIVE): [workspace-hub#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685) — calc-citation contract pilot
- Routing rule: [.claude/rules/codes-standards-data-routing.md](https://github.com/vamseeachanta/workspace-hub/blob/main/.claude/rules/codes-standards-data-routing.md)
- Calc-citation contract: [.claude/rules/calc-citation-contract.md](https://github.com/vamseeachanta/workspace-hub/blob/main/.claude/rules/calc-citation-contract.md)
- Sibling plan (same 2026-05-20 wave): `docs/plans/2026-05-20-issue-2746-llm-wiki-acma.md`
- OCIMF closeout: `docs/plans/2026-05-20-issue-2768-epic-ocimf-meg3-meg4-closeout.md`
- Structural reference plan: `digitalmodel/docs/plans/2026-05-20-issue-616-ocimf-polar-vessel-force-overlay.md`
- Memory: `project_llm_wiki_privacy_flip`, `feedback_codes_standards_data_in_private_wiki`

---

## Complexity: T3

**T3** — multi-publisher corpus ingest with ~30–50 projected subissues, cross-repo citation-resolver dependencies, edition-drift handling, copyright posture per-publisher, and a 5-phase rollout. Each per-publisher subissue is independently T2 (medium); the epic's coordination surface across 13 publishers + 5 phases + downstream consumers is T3.
