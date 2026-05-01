---
title: "SESA candidate dossier (issue #2541)"
domain: lng-projects
bucket: doris-62092-sesa
parent_root: /mnt/ace/doris/62092_sesa
generated: 2026-04-28
generator: terminal-1 overnight Elements wave (planning-only)
inputs:
  - .planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md
  - .planning/intel/elements-to-llm-wiki/elements-wiki-classification.tsv
  - .planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv
  - .planning/intel/elements-deep-extraction/elements-deep-extraction-report.md
  - knowledge/wikis/lng-projects/wiki/sources/elements-doris-62092-sesa.md
related_issues:
  - workspace-hub#2541 (this plan)
  - workspace-hub#2540 (umbrella)
  - workspace-hub#2526 (ingest)
  - workspace-hub#2534 (cleanup/retention)
  - workspace-hub#2535 (metadata-first wiki page)
  - workspace-hub#2536 (first-pass deep extraction — Suction-pile / Riser-toolbox / QGIS only)
---

# SESA FLNG Terminal — curated extraction dossier

> Planning-only artifact. No raw bulk data is copied into git or wiki by this dossier.
> All paths reference `/mnt/ace/doris/62092_sesa` and are read-only for this terminal.

## 1. Corpus shape (from intel)

| Metric | Value | Source |
|---|---:|---|
| Files in bucket | 418 | domain-summary, classification.tsv |
| Bytes in bucket | 1,465,267,463 (~1.46 GB) | domain-summary |
| Deep-extraction candidates flagged | 347 | deep-extraction-candidates.tsv (filtered on bucket) |
| Top-level node sample | `999 Work Space` (192), `000 Client Supplied` (168), `002 Project Filing` (31), `001 Transfer` (2), `DNV-ST-F101.pdf` (1) | source-page metadata |
| Content-kind histogram | pdf 187, document 80, tabular 77, other 39, cad 18, image 7, archive 6, presentation 2 | source-page metadata |
| Extension histogram | .pdf 187, .xlsx 77, .docx 59, [no-ext] 24, .doc 21, .dwg 18, .db 6, .zip 6, .jpg 5, .msg 4 | source-page metadata |
| Verification | missing=0; size_mismatch=0; not_hardlinked=0 | classification.tsv |

## 2. Project context (inferred from path tokens — to confirm in plan review)

- **SESA** = San Antonio Este, Argentine Patagonia FLNG terminal proposal under DORIS engineering.
- Two FLNG vessel options surface in path tokens: `Hilli`, `MKII`, plus a third `LYOS` referent.
- DORIS document numbering: `GSM-AO-<discipline>-<doc-type>-NNNNN-<seq>-<rev>`.
  Discipline letters seen: `G` (general), `L` (logistics/marine), `C` (civil/structural), `M` (maritime), `Q` (quality).
  Document type codes seen: `ITE` (engineering technical report / "informe técnico"), `MCA` (marine/method calc analysis), `LYO` (layout), `HDS` (hydrostatic data sheet), `ETC` (engineering technical communication), `PRO` (procedure).
- CTR (Change/Task Request) decomposition under `999 Work Space/`:
  - CTR-01 — Subsea Valves
  - CTR-03 — Free-span calcs
  - CTR-04 — Flanges / HDS
  - CTR-05 — L-ETC documents
  - CTR-08 — Procedures (Q-PRO)
  - CTR-09 — Civil ITE
  - CTR-10 — Marine MCA
  - CTR-11 — Maritime PRO
- Path tokens are bilingual Spanish/English (`Estudios de referencia`, `Metaoceánicos`, `Válvulas Offshore`, `Envío a DORIS`); UTF-8 round-trip is required.

## 3. Theme groups (with evidence)

### 3.1 Reference studies — `Estudios de referencia`
**Folder:** `000 Client Supplied/08 - Documents to Review CTR-08/19-Dec-25/Estudios de referencia/`
**Pattern:** `GSM-AO-G-ITE-100xx-0000-0-A[ Rev JRA].pdf`
**Why high value:** large general-engineering technical reports underpinning the FLNG technical case. Likely contain metocean inputs, design basis, and conceptual layouts.
**Notable artifacts:** GSM-AO-G-ITE-10046 (99.6 MB — flagship); -10008 (33.4 MB, with Rev JRA); -10010 (18.4 MB, with Rev JRA); -10024 (10.9 MB, also reused under Free-Span/Hilli/Metaoceánicos); -10033 (19.9 MB); -10042 (5.86 MB).
**Risk:** -10046 at ~100 MB may need page-batched `pdftotext` to avoid memory blow-ups; bilingual content must round-trip UTF-8. Several reports appear to embed scanned plates — OCR fallback may be required for figure-heavy pages, deferred beyond first tranche.

### 3.2 Free-span / metocean
**Folder:** `000 Client Supplied/02-Free Span Analysis/` and `999 Work Space/CTR-03-Free Span Calcs/`
**Pattern:** vessel-keyed subfolders (`Hilli/`, `MKII/`, `LYOS/`) carrying both metocean inputs and span-calc outputs.
**Why high value:** the canonical free-span analysis methodology bundle for a working FLNG project — directly reusable into `wiki/concepts/free-span-analysis-flng-flowline.md` as a cross-vessel comparison.
**Notable artifacts:** GSM-AO-L-MCA-10025-0000-A (.docx 5.79 MB editable + .pdf 4.19 MB final calc, MKII vessel); GSM-AO-G-ITE-10029 (9.28 MB, Metaoceánicos/MKII); GSM-AO-L-LYO-10033/-10032 (LYOS layouts, ~3.5–3.9 MB); GSM-AO-L-MCA-10022-0000-A (13.18 MB, latest 2026-01-06 transmittal).
**Risk:** The .docx and .pdf for -10025 are not byte-identical — extraction should treat them as a paired source (text via .docx, figures via .pdf) rather than redundant copies.

### 3.3 Material specs / datasheets
**Folder:** `000 Client Supplied/03-Material Specs and DS/Flanges/` and `999 Work Space/CTR-04/`
**Pattern:** flange data sheets with two parallel tracks — client-supplied baseline vs. DORIS markup ("w comments CODE B").
**Why high value:** client-supplied flange HDS plus DORIS engineering review comments form a natural "baseline + verification" pair that maps directly into a `wiki/concepts/flange-data-sheet-review-codes.md` and a vendor cross-walk.
**Notable artifacts:** GSM-AO-L-HDS-10016-0000 - B.pdf (4.95 MB, client-supplied baseline); GSM-AO-L-HDS-10016-0000 Flange Data Sheets w comments CODE B.pdf (6.07 MB, DORIS review markup).
**Risk:** The "w comments CODE B" PDFs use overlay annotations — `pdftotext` will dump comments inline but may collide with body text; consider pdfminer.six layout mode as fallback.

### 3.4 Subsea valves TBE
**Folder:** `000 Client Supplied/01-Subsea Valves TBE/AT Válvulas Offshore/3) Oferentes/`
**Pattern:** vendor-keyed subfolders (`PIETRO/`, `RMT VALVOMECCANICA/`, `ATP SOLUTIONS/`) containing technical brochures, QCPs, and painting procedures + `999 Work Space/CTR-01-Valves/FSosa/` engineer working materials with ASTM crosswalks.
**Why high value:** a real-world TBE (Technical Bid Evaluation) bundle for subsea valves — comparison-ready vendor data plus an internal ASTM compliance matrix. Maps to a `wiki/comparisons/subsea-valve-tbe-pietro-rmt-atp.md` cross-vendor table.
**Notable artifacts:** Trunnion technical brochure (PIETRO, 6.89 MB); RMT VM Technical Catalogue (6.59 MB); ATP SOLUTIONS preliminary painting procedure (4.59 MB); ASTM compliance matrix .pptx (FSosa, 8.57 MB).
**Risk:** Vendor brochures often contain marketing+spec mixed content; first-pass extraction should keep brochure-derived facts clearly attributed to the vendor and not re-mix them as standards. Standards directly referenced (API 6DSS, ASTM A351 CF8M, A182 F316, A276 T316) belong in `wiki/standards/` and must NOT be re-extracted as if SESA-specific.

### 3.5 Logistics / project deliverables
**Folders:** `999 Work Space/cwhite/` (logistics author) and `002 Project Filing/Deliverables/`, `002 Project Filing/100 Project Management/190 Project Records/Presentations/`
**Pattern:** logistics base description (San Antonio Este port/yard) and final deliverables with project-management records.
**Why high value:** logistics base description is a one-shot project narrative not derivable from technical reports. KOM presentation is a kickoff snapshot useful for project-context wiki page.
**Notable artifacts:** San Antonio Este — Logistics Base Description 18.11.2025-cew updated.docx (4.39 MB, latest cew-updated revision); GSM-AO-Q-PRO-10066-0000-A.pdf (canonical Deliverables copy 9.21 MB); 61912-190-PRN-20251114_KOM.pdf (1.40 MB).
**Risk:** Three near-byte-identical .docx revisions exist for the logistics base description (raw → cew → cew updated); only the latest goes in the tranche.

## 4. Deduplication observations

The most expensive cross-cut for the future implementation phase is canonical-path selection. Observed patterns:

| Duplication shape | Example | Heuristic for canonical pick |
|---|---|---|
| Same artifact in client transmittal + work folder + JWhipple personal copy | GSM-AO-Q-PRO-10066-0000-A.doc appears in 3 paths at byte-identical 23,694,848 | Prefer `002 Project Filing/Deliverables/` (final), else `000 Client Supplied/` newest dated subfolder, else first `999 Work Space/CTR-NN/` |
| Same artifact across format triplet .doc/.docx/.pdf | GSM-AO-Q-PRO-10066-0000-A in all three | Extract from .pdf (final-form) for content, retain .docx as editable provenance link only |
| Rev variants `Rev JRA`, `Rev JW`, `Rev JW JRA` | GSM-AO-Q-PRO-10066-0000-A Rev JW JRA.pdf | Keep `Rev JRA` (DORIS senior reviewer markup) when present; treat as separate page only if comments add engineering content |
| `Old/` shadow copies | `999 Work Space/CTR-09/Old/GSM-AO-C-ITE-10011-0000-A Rev JRA.pdf` | Always exclude `Old/` from the tranche |
| Dated transmittal folders for the same doc | `2025-12-18-DORIS/`, `19-Dec-25/`, `2026-01-06/` | Pick most recent dated folder for the canonical path |

The first-tranche TSV applies these rules; the implementation phase will need a scripted path-canonicalization pass before extraction begins.

## 5. Out-of-scope / risk notes

1. **Standards** sitting at the project root (`DNV-ST-F101.pdf`) and in CTR-04 (`asme-b16-5-2013-flanged-fittings.pdf`) and CTR-01 (`API 6DSS.pdf`) must NOT be extracted as SESA-specific content. They belong in `knowledge/wikis/<engineering-standards|marine-engineering>/wiki/standards/` per the calc-citation contract (`.claude/rules/calc-citation-contract.md`). The first tranche excludes them; a separate cross-reference task should record the SESA-side reference link.
2. **CAD (.dwg) — 18 files** are not in the first tranche. CAD extraction needs a different toolchain (e.g. `dwg2dxf` + DXF entity summary, as already prototyped under `.planning/intel/elements-deep-extraction/gis/dxf-entity-summary.json`). Defer to a follow-up tranche.
3. **Email archives (.msg) and .db** files (4 + 6 files) are not in the first tranche; they likely need a separate retention/PII review before any extraction.
4. **OCR fallback**: at least one large reference study is suspected to contain scanned plates. First-pass extraction is `pdftotext -layout` only; OCR (`tesseract`) is deferred and explicitly out-of-scope for the first tranche.
5. **Bilingual content**: extracted text must preserve Spanish accents and ñ. Validation step in the implementation phase should grep extracted output for replacement-character `?` or `�` to flag encoding loss.
6. **Vendor confidentiality**: TBE vendor brochures may carry NDA-style markings. Wiki source pages should link `/mnt/ace` paths but avoid uploading brochure text wholesale until a redistribution policy is confirmed. Open question for plan review.
7. **#2534 retention boundary**: this dossier and the future implementation phase do NOT delete or move anything under `/mnt/ace/doris/62092_sesa/_from_elements`. That cleanup remains gated by #2534.
8. **Bytes selected vs total**: the proposed first tranche covers ~276 MB of raw source — roughly 19% of bucket size, ~5% of file count, but is expected to capture the majority of high-signal engineering content because the tail is dominated by working-folder duplicates and CAD.

## 6. Uncertainties to surface in plan review (do not resolve in dossier)

- Are LYOS / MKII / Hilli the three competing FLNG vessel candidates, or is one of them a topside identifier? (Affects whether free-span pages are `entities/` or `comparisons/`.)
- Is the SESA project still active and confidential, or freely citeable inside the wiki? (Affects vendor-text policy in §5.6.)
- Should the `Rev JRA` markup-only PDFs be merged into the base-rev source page, or kept as separate review pages? (Affects extracted-page count and dedup rules.)
- Is there a ratified project-document-ID convention page elsewhere in DORIS internal wikis that should be cross-linked rather than redocumented? (Affects whether the GSM-AO numbering scheme gets its own concept page.)

These uncertainties are intentionally written here rather than asked of the user mid-overnight, per the run boundary.
