# Doris University training corpus — taxonomy and extraction routing

> Planning artifact for workspace-hub#2542 (overnight Elements wave Terminal 2).
> Generated 2026-04-28 from the metadata-only Elements ingest (#2535) and the
> deep-extraction candidate TSV. No raw-data extraction performed; this file
> is path/size/content-kind analysis only.

## Source of record

- Raw corpus: `/mnt/ace/doris/training` (read-only)
- Metadata page: `knowledge/wikis/engineering/wiki/sources/elements-doris-university.md`
- Candidate TSV: `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv` (322 doris-university rows out of 564 total files)
- Domain summary: `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md`

## Headline numbers (from #2535 catalog)

| Field | Value |
|---|---|
| Files | 564 |
| Bytes | 11,060,962,662 (~11.06 GB) |
| Extractable candidates (TSV) | 322 |
| Content kinds | pdf 159, presentation 148, other 128, image 113, tabular 11, document 4, archive 1 |
| Extension sample | .pdf 159, .bmp 108, .pptx 88, .ppt 60, .db 52, .vob 22, .mp4 12, .bup 12, .ifo 12, .xls 10, .jpg 5, .doc 4 |

The 128-file `other` bucket is dominated by `.db` (Windows `Thumbs.db`), `.vob`/`.ifo`/`.bup` (DVD video container), `.mp4` — these are media or filesystem cruft, not knowledge units, and are out of scope for any extraction tranche.

## Top-level grouping

| # | Group | Path pattern | Origin | Reuse value | IP risk | Routing |
|---|---|---|---|---|---|---|
| A | Doris University core curriculum | `1.0[0-3] - <Subject>/` | Doris-authored | **Highest** — defines the curriculum | Internal-only | Extract → `wiki/sources/` + `wiki/concepts/` |
| B | Doris-authored embedded calculations | `1.0?/Embedded Charts/` | Doris-authored | **Highest** — methodology with formulas | Internal-only | Extract → `wiki/concepts/` (methodology) + tie to `wiki/standards/<code-id>.md` via calc-citation contract |
| C | ADMIN-FORM-02 Lunch and Learn series | `ADMIN-FORM-02 - * Lunch and Learn, Part *.pdf` (root) | Doris-authored | High — bite-sized knowledge units | Internal-only | Extract → `wiki/concepts/` |
| D | Old/superseded versions of A/B/C | `*/Old Versions/`, `*/Old Revisions/`, `Superceeded/` (sic) | Doris-authored | Medium (history only) | Internal-only | Skip in first tranche; index syllabus only |
| E | Vendor reference standards | `*/References/{API,ISO,IEC,UMF-GN,*}*.pdf` | API, ISO, IEC, BS EN, FMC, Duco | High (already public) | **Vendor-derivative deny-list (#2482)** | **Do NOT extract.** Cite via `wiki/standards/<code-id>.md` per `.claude/rules/calc-citation-contract.md` |
| F | Client-delivered training packs | `DE Presentations/{SONANGOL,ENI,DSME,Operator}/`, `ENI Training/`, `Stat Presentations/` | Doris-authored for client engagement | High but **client-IP-bound** | **High** — client confidentiality, may embed client-private data | Hold pending IP/legal review; do NOT extract in tranche 1 |
| G | Project residue | `FieldLayout/`, `FreeSpan/`, `Flexible Pipe/`, `draft presentations/<project>/` | Doris-authored project work | Low–Medium | Project-confidential possible | Hold; case-by-case after curriculum is wiki'd |
| H | Draft / parallel staging | `draft presentations/...` mirroring root paths | Doris-authored | Duplicate | n/a | De-duplicate against canonical sibling; do NOT extract a second time |
| I | Curriculum index / scheduling | `Superceeded/Doris U Syllabus*`, `Superceeded/Doris Lunchtime University syllabus - *.xls` | Doris admin | Medium (taxonomy seed) | Internal-only | Extract one syllabus snapshot for taxonomy validation |
| J | Operational/admin scaffolding | `*/Questionnaire training *.doc`, `*/Training - Team-schedule.xls` | Doris admin | Low | Internal-only | Skip |
| K | Training media | `*.vob`, `*.ifo`, `*.bup`, `*.mp4`, `*.bmp` | DVD authoring | None for text wiki | n/a | Out of scope for text extraction; media-only |

## Group A: Curriculum module map (canonical decks)

The numbered modules form a coherent curriculum on **subsea production systems**, each with three artifact families: a current top-level deck, an `Old Versions/`/`Old Revisions/` archive, an `Embedded Charts/` folder of methodology calcs, and a `References/` folder of vendor standards (which we do not extract).

| Module | Topic | Canonical deck (latest version) |
|---|---|---|
| 1.00 | Subsea Production Systems — General Overview | `1.00 - .../Subsea Production Systems - Part 1, Introduction (V1.2).pptx` (16.9 MB) |
| 1.01 | Subsea Production Control Systems — System Overview and Major Components | `Part 1 V1` + `Part 2 V1` (.pptx) |
| 1.02 | Subsea Umbilical Systems — System Overview and Major Components | `Part 1 V1.3` + `Part 2 V1.3` + `Part 3 V1.3` (.pptx) |
| 1.03 | Installation and Workover Control Systems — System and Major Component Overview | `Part 1 V1.3` + `Part 2 V1.2` (.pptx) |

The 1.0x naming hints at additional modules (1.04+) that may exist deeper in the tree but did not surface in the top-100-by-size cut. Those should be enumerated during plan execution (line-count audit on the TSV).

## Group B: Embedded Charts (Doris-authored calc methodology)

Four artifacts confirmed via TSV:

| Path | Bytes | Why high-value |
|---|---:|---|
| `1.01/Embedded Charts/Methanol Analysis.xls` | 945,664 | Methanol injection sizing — embedded formulas |
| `1.02/Embedded Charts/Umbilical Tube Size Calculation per API 17E, Simplified (V0).pdf` | 70,282 | Tube sizing methodology — calc-citation candidate (cite API 17E in `wiki/standards/`) |
| `1.02/Embedded Charts/Hydrostatic Pressure.xlsx` | 16,426 | Pressure-depth conversion table; formula-bearing |
| `1.03/Embedded Charts/Subsea Accumulator Sizing, Simplified (V1.0).pdf` | 425,126 | Accumulator volume calc; calc-citation candidate (likely API 17G ref) |

These are the strongest match for the **calc-output citation contract** (`.claude/rules/calc-citation-contract.md`). When converted to wiki concept pages, every standards-derived constant must emit a `Citation` resolving to a `wiki/standards/<code-id>.md` page. If the relevant standards page does not yet exist, the rule says forward-adopt the #2471 frontmatter and create the page first.

## Group C: ADMIN-FORM-02 Lunch and Learn series (root)

Five PDFs at the corpus root, all 510–530 KB, dated 2018:

- Control Systems Lunch and Learn, Part 1 / Part 2
- Umbilical Systems Lunch and Learn, Part 1 / Part 2 / Part 3 (2018)
- Plus a "Part 3 Rescheduled" variant (treat as duplicate)

These look like internal teaching-distillation PDFs of the corresponding numbered modules. They are smaller and likely text-heavy → cheap, high-yield extraction.

## Vendor-derivative deny-list (Group E) — explicit do-not-extract

Confirmed instances of vendor standards under `*/References/`:

- API 16D (2005), API 17D (2013), API 17E, API 17E (2011), API 17G (2011), API 17H (2013), API 17I
- BS EN ISO 13628-5
- IEC 60502-1, IEC 60502-2
- Subsea Engineering Handbook (2010)
- UMF-GN01, UMF-GN05, UMF-GN07
- FMC vendor docs: `FMC Installation - EVDT.pdf`, `EHXT.pdf`, `Dual Bore.pdf`, `HCS Controls.pdf`
- Duco vendor docs: `Duco - Umbilical Manufacturing Overview.pdf`, `Duco - Hardware Design.pdf`
- OTC papers: `OTC-25320-MS.pdf`
- Generic: `INSTALLA.PDF`, `Introduction to Subsea Production System (2016).pdf`, `IN-0014 Subsea Technology Review.pdf`, `Operation manual.pdf`

Routing per #2482: cite via `wiki/standards/<code-id>.md` if the standard backs a calc; otherwise leave un-extracted with a metadata-only `wiki/sources/` reference if needed.

## Client-IP packs (Group F) — hold pending review

Confirmed instances:

| Sub-pack | Likely client | Files of note |
|---|---|---|
| `DE Presentations/SONANGOL Training/Day_1..3/` | Sonangol (Angolan NOC) | RISER, INSTALL, SPS-Umbilical, ANGOLA, DORIS_Topsides, Support_platform, Example_Basic |
| `DE Presentations/ENI Training/` and `ENI Training/` (root) | Eni (Italian operator) | ITSS_Subsea_Overview/Field_Planning/Distribution/Production_Control_Systems/Well_Control |
| `DE Presentations/DSME Training/` | DSME (Daewoo Shipbuilding) | Training content + team schedule |
| `Stat Presentations/` | Statoil/Equinor + IFP co-brand | Day 1–5 plus IFP-22June2015..26June2015 |
| `draft presentations/Operator Training/` | Azurite project (Total/Murphy) | Subsea operator training |

Each carries IP/legal risk distinct from the curriculum. **Out of tranche 1.** A future child issue (suggested name `feat(llm-wiki): IP-screen Doris training client-pack extraction`) should propose a screening protocol per client.

## Wiki target structure (for tranche 1 only)

Per `knowledge/wikis/engineering/SCHEMA.md`, ingest follows: source → entity/concept → index → log.

Proposed pages for the first tranche:

```
knowledge/wikis/engineering/wiki/
├── sources/
│   ├── doris-university-module-1-00-subsea-production-systems-overview.md
│   ├── doris-university-module-1-01-production-control-systems.md
│   ├── doris-university-module-1-02-umbilical-systems.md
│   ├── doris-university-module-1-03-installation-workover-control.md
│   ├── doris-university-lunch-and-learn-control-systems.md
│   ├── doris-university-lunch-and-learn-umbilical-systems.md
│   └── doris-university-syllabus-snapshot.md
├── concepts/
│   ├── subsea-production-system-overview.md
│   ├── subsea-production-control-system.md
│   ├── subsea-umbilical-system.md
│   ├── installation-workover-control-system.md
│   ├── umbilical-tube-sizing-api-17e.md           (calc — cite API 17E)
│   ├── subsea-accumulator-sizing.md               (calc — cite API 17G or applicable)
│   ├── hydrostatic-pressure-depth.md              (calc methodology)
│   └── methanol-injection-analysis.md             (calc methodology)
└── standards/  (created as needed by calc citations; only if not already present)
    ├── api-17e.md
    ├── api-17g.md
    └── ... (only if a tranche-1 calc references them)
```

The existing source page `wiki/sources/elements-doris-university.md` (catalog) stays as the parent metadata page; new sources cross-link to it via `parent: elements-doris-university` in frontmatter or a "See also" section.

Concept pages reference the canonical `wiki/standards/<code-id>.md` for any standards-derived constant per `.claude/rules/calc-citation-contract.md`. If a referenced standards page does not yet exist (e.g., API 17E does not appear in the existing wiki/standards tree), the executing phase **must** create it with #2471 frontmatter before emitting the calc page — fail-closed per #2481 D2.

## Risks and uncertainties

1. **Module 1.04+ may exist** — only `1.00`–`1.03` surfaced in the top-by-size cut. The plan must enumerate all `1.0?` directories before declaring tranche 1 complete.
2. **Embedded-image extraction inflates output**. Each .pptx has dozens of figures (the source page lists 113 .bmp). If figures are extracted into wiki/raw/, the wiki "raw bulk in git" line is crossed. Tranche 1 should extract slide *text* and *speaker notes* only; figures stay metadata-referenced.
3. **Deck duplicates between root and `draft presentations/`** are likely byte-identical but not verified. Plan must hash the candidate set to avoid double-ingest before extraction.
4. **API 17E version drift** — the corpus has both `API 17E - Specification for Subsea Umbilicals.pdf` and `API 17E (2011) - Specification for Subsea Umbilicals.pdf`. Before any standards-page creation, the citation must record `revision: 2011-or-later` per #2471.
5. **Lunch-and-Learn duplication** — `ADMIN-FORM-02 - Umbilical Systems Lunch and Learn, Part 3 (2018).pdf` and a "Part 3 Rescheduled" exist; the rescheduled one is likely re-delivery; treat as superseded.
6. **Client-IP scope is uncertain** — the SONANGOL/ENI/DSME/Stat decks may have been delivered to the client with explicit transfer of teaching rights, in which case Doris retains methodology and the client gets the pack. Without contract review, the safe stance is "hold". This belongs in a separate child issue.
7. **OCR is not generally needed** — most .pptx and .pdf items here have native text layers; OCR is only triggered if a per-file probe (pdftotext on first page, length check) finds no text.
8. **`Superceeded/` (sic) folder name** is a misspelling embedded in the source — preserve verbatim in any path references.

## What this taxonomy does NOT decide

- Whether the SONANGOL/ENI/DSME/Stat client packs can be extracted at all (separate IP review).
- Whether to build the matching `wiki/standards/<code-id>.md` pages for vendor PDFs in scope of this tranche or as a separate codification phase.
- Cleanup or deletion of source files (governed by #2534, retention before 2026-05-28).
- Promotion to `status:plan-approved` (user-in-loop, not in this terminal's scope).
