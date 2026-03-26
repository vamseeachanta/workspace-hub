# Riser Engineering Job -- Document Catalog Summary

Source: `/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/`

## Overview

Four subsea riser engineering projects, totaling 9,672 PDFs across 93 GB of mixed files (PDFs + native engineering files). All projects are BP-client deepwater riser design work.

| Project | Name | PDFs | PDF Size | Total Files | Total Size |
|---------|------|-----:|----------|------------:|------------|
| 2100 | BLK31 SLOR Design | 7,125 | 4.0 GB | 56,154 | 53 GB |
| 3824 | Containment Riser | 2,158 | 1.6 GB | 47,453 | 30 GB |
| 3836 | HP1 Riser | 88 | 62 MB | 11,898 | 7.4 GB |
| 3837 | CDP2 Freestanding Riser | 301 | 169 MB | 1,712 | 3.7 GB |
| **Total** | | **9,672** | **5.9 GB** | **117,217** | **93 GB** |

## Document Numbering Scheme

Standard pattern: `{project}-{doc_type}-{sequence}-{revision}`

- `2100-DDL-3207-04` = project 2100, detail drawing, sequence 3207, revision 04
- `3824-RPT-2103-3` = project 3824, report, sequence 2103, revision 3
- `3836-RES-1003-02` = project 3836, analysis results, sequence 1003, revision 02

External documents (HMC, Intec) use vendor schemes, e.g. `AA000.W00.C1.TRI300.RP02`.

## Top Document Types (across all projects)

| Code | Type | Count |
|------|------|------:|
| DGA | General Arrangement Drawing | 1,874 |
| DDL | Detail Drawing | 1,591 |
| RPT | Report | 494 |
| CSH | Calculation Sheet | 432 |
| CTR | Calculation / Technical Report | 251 |
| DFG | Design File Guide | 225 |
| DTS | Data Sheet | 221 |
| PAF | Project Administration File | 201 |
| TNE | Technical Note | 134 |
| PRG | Progress Report | 143 |
| SPC | Specification | 112 |
| MTO | Material Takeoff | 85 |
| PRS | Presentation | 71 |
| CAL | Calculation | 59 |
| DBA | Design Basis | 40 |

## Index Quality

- 76.3% of PDFs have an extracted `doc_type` (7,222 / 9,461)
- 71.1% have a parsed `doc_number` (6,725 / 9,461)
- Unclassified files are mostly vendor/external docs without the standard naming convention

Note: index.jsonl has 9,461 records vs 9,672 total PDFs; the 211 difference is `.PDF` (uppercase extension) and files in the `llm-classifications` subfolder which are outside the four project folders.

## Project Descriptions

**2100 -- BLK31 SLOR Design**: Block 31 (Angola) Steel Lazy-Wave Riser detailed design. Largest project by far. Covers package engineering (flexible jumpers, driven piles, support frames), lifting/seafastening, HMC T&I engineering, and BP documents.

**3824 -- Containment Riser**: MC252 Macondo CDP riser modification. Emergency containment riser with upper/lower assemblies, CVA (Certified Verification Agent) documentation, subsea jumper analysis. Most diverse folder structure (40+ top-level folders).

**3836 -- HP1 Riser**: MC252 CDP1-HP1 flexible riser system analysis. Smaller scope: riser analysis reports, disconnected analysis, MOC2 design assurance, umbilical assessment. Bulk of data is native analysis model files, not PDFs.

**3837 -- CDP2 Freestanding Riser**: MC252 CDP2 freestanding containment riser. PIP (Pipe-in-Pipe) design, installation storyboards, SIT procedures. Includes NCRs, lessons learnt, and offshore load-out documentation.

## Outputs

| File | Format | Purpose |
|------|--------|---------|
| `catalog.yaml` | YAML | Per-project metadata, doc type counts, sizing |
| `index.jsonl` | JSONL | Flat per-PDF index for search tools and LLM pipelines |
| This file | Markdown | Human-readable summary |
