---
title: "Woodfibre LNG corpus pointer (ACMA project 31522)"
tags: ["woodfibre", "lng", "fst", "mooring", "acma-31522", "metadata-only"]
added: 2026-05-01
last_updated: 2026-05-01
sources:
  - /mnt/ace/acma-projects/31522-woodfibre-lng
  - .planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md
  - .planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv
  - docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md
domain: lng-projects
cross_links:
  - wiki/sources/elements-acma-projects-31522-woodfibre.md
---

# Woodfibre LNG corpus pointer (ACMA project 31522)

> Metadata-only pointer page emitted under issue #2544 after plan approval.
> This page does **not** authorize or contain document abstracts, direct quotes, tables, figures, or full-text extraction.

## Source of record

- Corpus root: `/mnt/ace/acma-projects/31522-woodfibre-lng`
- Existing ingest catalog: [Elements ingest catalog — acma-projects-31522-woodfibre](elements-acma-projects-31522-woodfibre.md)
- Approved scout artifacts:
  - `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md`
  - `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv`
- Governing plan: `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md`

## Confidentiality and approval boundary

This is a live ACMA project corpus with high confidentiality/IP risk. Under the 2026-04-29 addendum to #2544:

- only metadata pointer/scout output is approved here;
- no document abstract extraction, technical summary extraction, direct quote extraction, table extraction, or figure extraction may occur under this issue;
- any post-scout extraction remains blocked pending a dedicated follow-up plan and `docs/governance/woodfibre-extraction-clearance-2026.md` with row-level approval from an explicitly named ACMA project owner, client-authorized reviewer, or legal/IP delegate.

## Corpus shape summary

| Metric | Value |
|---|---:|
| Files in corpus | 5,364 |
| Total bytes | 1,879,405,139,855 (1.879 TB) |
| Bucket priority | metadata-only |
| Largest single subdir | `02.Mooring Analysis/03.Orcaflex` — 2,610 files / 1.800 TB |
| `.sim` time-history bytes | 1,854.7 GB across 1,383 files |

## Top-level structure

| Files | Bytes (GB) | Top-level |
|---:|---:|---|
| 2,658 | 1,800.45 | `02.Mooring Analysis` |
| 549 | 61.98 | `04.Model Test Correlation` |
| 296 | 11.85 | `03.Ansys FEA` |
| 500 | 3.39 | `05.Deliverables` |
| 1,344 | 1.73 | `orcaflex_no_sim` |
| 17 | 0.00 | `01.Stability` |

## Deliverables register structure (`05.Deliverables/`)

| Code | Meaning | Files | Pointer note |
|---|---|---:|---|
| `DB` | Design Briefs | 14 | high-value family for future clearance review |
| `RA` | Reports | 6 | high-value family for future clearance review |
| `FD` | Project design criteria & philosophies | 31 | high-value family for future clearance review |
| `SA` | Specifications & Standards | 9 | metadata only unless separate standards-safe handling is approved |
| `TN` | Technical Notes | 25 | high-value family for future clearance review |
| `WS` | Workshop Sessions | 4 | metadata only for now |
| `XA` | Flow Diagrams (P&IDs) | 21 | drawing-heavy; no extraction here |
| `XD` | General arrangements | 21 | drawing-heavy; no extraction here |
| `XE` | Layout drawings | 6 | drawing-heavy; no extraction here |
| `XG` | Structural information | 115 | metadata only for now |
| `LA` | Lists & Registers | 9 | metadata only for now |
| `DS` | Data sheets | 25 | metadata only for now |
| `CA` | Analysis | 49 | metadata only for now |
| `DEMOLITION/{CAPRICORN,TAURUS}` | Existing-vessel demolition record drawings | 162 | explicitly excluded from extraction planning |

## Explicit no-extraction / no-copy boundary

Do **not** copy raw bytes from the Woodfibre corpus into git. Do **not** extract or summarize these file classes under #2544:

- `.sim` OrcaFlex time-history binaries
- ANSYS restart/archive/CAD families such as `.r001`, `.r002`, `.r003`, `.wbpz`, `.scdoc`, `.sldprt`
- demolition record drawings under `05.Deliverables/DEMOLITION/{CAPRICORN,TAURUS}`

## Planned follow-up inputs

The bounded candidate list remains tracked only as metadata in `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv`.
Any later implementation must enforce latest-revision selection, no persisted full-text intermediates, and row-level clearance before producing document pages.
