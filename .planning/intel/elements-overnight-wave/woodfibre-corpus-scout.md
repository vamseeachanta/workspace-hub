# Woodfibre LNG corpus scout (issue #2544)

> Generated: 2026-04-28 (overnight wave Terminal 4)
> Source of record: `/mnt/ace/acma-projects/31522-woodfibre-lng/`
> Wiki domain target: `lng-projects`
> Method: metadata-first read of `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl` (5,364 records). No `/mnt/ace` walks; no raw content opened.

## Headline numbers

| Metric | Value |
|---|---:|
| Files in corpus | 5,364 |
| Total bytes | 1,879,405,139,855 (1.879 TB) |
| Bucket priority per #2535 | metadata-only |
| Wiki domain | lng-projects |
| Largest single subdir | `02.Mooring Analysis/03.Orcaflex` — 2,610 files / 1.800 TB |
| `.sim` time-history bytes | 1,854.7 GB across 1,383 files (98.7% of bucket) |

## Top-level structure (depth 1)

| Files | Bytes (GB) | Top-level |
|---:|---:|---|
| 2,658 | 1,800.45 | `02.Mooring Analysis` |
| 549 | 61.98 | `04.Model Test Correlation` |
| 296 | 11.85 | `03.Ansys FEA` |
| 500 | 3.39 | `05.Deliverables` |
| 1,344 | 1.73 | `orcaflex_no_sim` |
| 17 | 0.00 | `01.Stability` |

## Depth-2 structure — top 12 by bytes

| Files | Bytes (GB) | Path |
|---:|---:|---|
| 2,610 | 1,799.98 | `02.Mooring Analysis/03.Orcaflex` |
| 519 | 61.76 | `04.Model Test Correlation/02. Orcaflex` |
| 294 | 11.32 | `03.Ansys FEA/Local` |
| 162 | 2.30 | `05.Deliverables/DEMOLITION` |
| 378 | 1.04 | `orcaflex_no_sim/02-FST's_LNGC` |
| 375 | 0.60 | `orcaflex_no_sim/01-FST's Only` |
| 2 | 0.53 | `03.Ansys FEA/Global` |
| 48 | 0.47 | `02.Mooring Analysis/02.Hyd` |
| 49 | 0.40 | `05.Deliverables/CA_Analysis` |
| 28 | 0.18 | `04.Model Test Correlation/01. Hyd` |
| 21 | 0.18 | `05.Deliverables/XD_General arrangements` |
| 115 | 0.18 | `05.Deliverables/XG_Structural information` |

## Document-control structure inside `05.Deliverables/`

ACMA EDMS naming convention: `350106-SC-EN-003-SD-NNNNNN_<rev>.<ext>`. Folder codes:

| Code | Meaning | Files | High-value? |
|---|---|---:|---|
| `DB` | Design Briefs | 14 | yes |
| `RA` | Reports | 6 | yes |
| `FD` | Project design criteria & philosophies | 31 | yes |
| `SA` | Specifications & Standards | 9 | yes |
| `TN` | Technical Notes | 25 | yes |
| `WS` | Workshop Sessions | 4 | yes |
| `XA` | Flow Diagrams (P&IDs) | 21 | medium (drawings, large) |
| `XD` | General arrangements | 21 | medium |
| `XE` | Layout drawings | 6 | medium |
| `XG` | Structural information | 115 | medium |
| `LA` | Lists & Registers | 9 | low |
| `DS` | Data sheets | 25 | low |
| `CA` | Analysis | 49 | medium |
| `DEMOLITION/{TAURUS,CAPRICORN}` | Existing-vessel demolition record drawings | 162 | metadata-only (very large PDFs) |

## Extension histogram (top 12 by bytes)

| Files | Bytes (GB) | Extension | Notes |
|---:|---:|---|---|
| 1,383 | 1,854.72 | `.sim` | OrcaFlex time-history binaries — DO NOT extract |
| 144 | 4.10 | `.csv` | numerical results |
| 137 | 4.01 | `.dat` | OrcaFlex input data (mostly text) |
| 321 | 2.68 | `.pdf` | reports, drawings (HIGH VALUE for first tranche) |
| 9 | 2.43 | `.sldprt` | SolidWorks parts (binary CAD) |
| 5 | 1.35 | `.wbpz` | ANSYS Workbench archives |
| 7 | 1.15 | `.scdoc` | SpaceClaim CAD |
| 21 | 0.97 | `.r001` | ANSYS restart files (skip) |
| 68 | 0.88 | `.txt` | misc text — includes 8 readmes |
| 65 | 0.41 | `.docx` | Word documents (HIGH VALUE) |
| 81 | 0.31 | `.dwg` | AutoCAD drawings |
| 17 | 0.03 | `.pptx` | presentations |

## Content kind histogram (full)

| Files | Bytes (GB) | content_kind |
|---:|---:|---|
| 4,269 | 1,858.74 | engineering-data |
| 353 | 11.64 | other |
| 173 | 4.11 | tabular |
| 321 | 2.68 | pdf |
| 85 | 0.91 | cad |
| 68 | 0.88 | text |
| 77 | 0.41 | document |
| 17 | 0.03 | presentation |
| 1 | 0.00 | image |

## Risk assessment

### Confidentiality / IP risk: **HIGH** for all candidates

This is a live project corpus. EDMS prefix `350106-SC-EN-003-SD-XXXXXX` indicates ACMA Engineering's project artefact register, executed for what appears to be the **WoodfibreLNG floating storage tank (FST) detailed design** — the file/folder naming references `FST-1`, `FST-2`, `Capricorn`, `Taurus`, `LNGC` (LNG carrier), `FSTs CP System` (cathodic protection), `Loading Arm Motions`, `Permanent Mooring Interface Loads`, `Initial Scantling Evaluation`. Likely third-party stakeholders include Pacific Energy / WoodfibreLNG (owner), WSP (mentioned by folder name), and shipyard partners (Capricorn, Taurus naming).

**Implication:**
- Methodology summaries, scope outlines, code references — typically OK to abstract.
- Numerical values (loads, GA dimensions, scantling sizes, design heading angles) — likely confidential.
- Cannot copy raw PDFs/DOCX into git/wiki. Even abstracts must be reviewed by ACMA before publication.

**Action:** every candidate is marked `confidentiality_risk: high` in the first-tranche TSV. Plan acceptance requires explicit ACMA review checkpoint (see canonical plan).

### Volume risk

- 1.879 TB total. 1.8 TB sits in OrcaFlex `.sim` files. Any unbounded extraction script over the parent root will catastrophically read sim binaries unless a hard extension allowlist is enforced.
- Plan must enforce: `--allow-ext .pdf,.docx,.txt,.md,.rtf` and `--max-bytes 25_000_000` (25 MB per file ceiling) for the bounded extraction job.

### Demolition subdir risk

`05.Deliverables/DEMOLITION/{CAPRICORN,TAURUS}` holds 162 record drawings averaging 14 MB and reaching 100 MB. These are existing-vessel as-built drawings used for demolition planning. They are EDMS prefix `100XXX` (a separate scheme from project design `000XXX`), suggesting they originated from a prior CAPRICORN/TAURUS owner's drawing register. **Especially sensitive** — exclude from first tranche entirely.

## Recommended extraction strategy

1. **No raw copies.** Wiki pages are *metadata-and-abstract* sources, not file mirrors. Same policy as #2535.
2. **First tranche = 15 documents max**, total ≤ ~80 MB, all from `05.Deliverables/{DB,RA,FD,SA,TN}` plus the model-test correlation report and two readmes. See `woodfibre-first-tranche.tsv`.
3. **Extraction method per artifact:**
   - `.pdf` / `.docx` / `.pptx`: pdfplumber/textract → 1-page summary → wiki source page; keep absolute parent path as provenance pointer (link-only, do not copy bytes).
   - `.txt` (readmes): full inline quote permissible (already trivially small, no IP density).
4. **One wiki source page per document**, frontmatter sourced from EDMS doc number, latest revision letter only.
5. **Latest-revision rule:** for documents with multiple revs (e.g. Naval Architecture Design Brief is at Rev B / B1 / C / C1 / C2), the first tranche includes only the **highest published rev** (C1 here) and the planner must NOT silently include older revs.
6. **Confidentiality gate before any extraction:** PR description must list candidate set; merge waits on ACMA / project-lead approval, not just wiki maintainer review.

## Uncertainties (per prompt: documenting rather than asking)

- **Project sponsor identity** is inferred from filename patterns (`WoodfibreLNG`, `WSP Interface loads`, `FST-1/FST-2`, `Capricorn/Taurus`). Cannot be confirmed without opening a PDF — out of scope here. Plan-stage reviewer should sanity-check before dispatching extraction.
- **EDMS doc number meaning of trailing `_<letter>`** assumed to be the IFR/IFA revision letter (B = "Issued for Review", C = "Issued for Approval", per common ACMA convention). Suffix `1`, `2` (e.g. `_C1`, `_C2`) assumed to be sub-revisions within the lettered review cycle. Latest = highest rev letter, then highest sub-revision.
- **Sponsorship between ACMA, WoodfibreLNG, WSP, Pacific Energy:** not derivable from metadata. Must be clarified with the project owner before any extracted content lands publicly.
- **Whether `_from_elements/` staging exists for this corpus** is implied by the #2535 catalog (staging path is `/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements`) but not verified in this scout because the working directory is sandboxed away from `/mnt/ace`. Treat as a precondition, not a confirmation.

## Companion bucket cross-reference

`doris-62092-sesa` (also `lng-projects` domain, 418 files / 1.47 GB, scouted by Terminal 1) sits in the same wiki. Coordinate Woodfibre source-page naming with SESA's so neither overwrites the other (e.g., prefix `woodfibre-` vs `sesa-` on each `wiki/sources/*.md`).

## Files produced by this scout

- This file: `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md`
- Candidate tranche: `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv`
- Canonical plan: `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md`
- Result summary: `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md`
