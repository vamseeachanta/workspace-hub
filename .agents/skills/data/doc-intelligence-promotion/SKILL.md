---
name: doc-intelligence-promotion
description: "Post-processing pipeline for document extraction \u2014 tables to CSV,\
  \ calc reports from extracted data, charts to calibration metadata. Includes table\u2192\
  YAML\u2192code\u2192calc-report workflow."
version: 1.1.0
category: data
type: skill
trigger: manual
auto_execute: false
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
related_skills:
- doc-extraction
- dark-intelligence-workflow
---

# Document Intelligence Promotion

> Single-pass extraction + multi-stage post-processing pipeline.
>
> **Note**: This pipeline uses pdfplumber for single-document extraction (not batch).
> For batch text extraction across the corpus, use pdftotext via subprocess — see
> `pdf/pdftotext-poppler` sub-skill.

## Architecture

```
PDF/DOCX → parser (single read) → manifest.yaml
                                       ↓
                            deep_extract.py (post-processors):
                            ├── table_exporter.py → CSV files
                            ├── worked_example_parser.py → pytest files
                            └── chart_extractor.py → images + metadata YAML
```

## CLI Commands

```bash
# Single document — deep extraction with report
uv run --no-project python scripts/data/doc-intelligence/deep-extract.py \
    --input <file.pdf> --domain naval-architecture --report --verbose

# From existing manifest
uv run --no-project python scripts/data/doc-intelligence/deep-extract.py \
    --manifest <manifest.yaml> --report

# Batch extraction with deep post-processing
uv run --no-project python scripts/data/doc-intelligence/batch-extract.py \
    --queue <queue.yaml> --deep --verbose

# Promote extracted artifacts to code
uv run --no-project python scripts/data/doc-intelligence/promote-to-code.py \
    --types tables worked_examples curves
```

## Post-Processor Details

### Tables (`table_exporter.py`)
- Reads `ExtractedTable` from manifest → writes CSV with header + rows
- Idempotent (content-hash check)
- Generates JSONL records for promoter integration

### Worked Examples (`worked_example_parser.py`)
- Parses "Example N.N:" title + "Given:" inputs + "Solution:" output
- Extracts: symbol, value, unit for each input parameter
- Generates real pytest files with `pytest.approx(expected, rel=1e-3)`

### Charts (`chart_extractor.py`)
- Extracts embedded images from PDFs via PyMuPDF
- Filters icons/logos (min 100x80px)
- Links images to figure references by page number
- Generates calibration metadata YAML for manual digitization

## Extraction Yield Reality (WRK-1246 Assessment)

Proven yield across 420K+ corpus:

| Content type | Yield | Notes |
|-------------|-------|-------|
| tables | 69-93% | Primary extraction target |
| figure_refs | 1-52% | Metadata only; varies by stratum |
| equations | 0% | Not reliably detectable by current parsers |
| constants | 0% | Not reliably detectable by current parsers |
| procedures | 0% | Not reliably detectable by current parsers |
| worked_examples | 0% | Not reliably detectable by current parsers |

Focus extraction effort on tables. Other content types exist in the manifest schema but
produce no usable output from the current pipeline.

## Table Quality Gate

Before promoting extracted tables, apply three quality filters:

1. **Content-hash dedup**: Remove identical repeated tables. IHS watermark tables and
   repeated header/footer tables appear across many pages — hash each table's content
   (header + rows) and deduplicate.
2. **Min-content threshold**: Skip tables with fewer than 3 data rows or fewer than 2
   numeric columns. These are typically formatting artifacts, not engineering data.
3. **LLM quality rating**: Rate each surviving table as `usable` / `partial` / `junk`
   via Haiku. Usable tables have clear headers, consistent units, and meaningful data.
   Partial tables may need manual cleanup. Junk tables are formatting noise.

## Chart Extraction Note

Chart extraction is metadata-only — the pipeline captures figure references, captions,
and page locations but does not extract the image content itself. Image extraction
requires PyMuPDF (fitz) and is tracked under WRK-1257.

## Table → YAML → Code → Calc Report (WRK-1188 Learning)

**Primary workflow for engineering standards** (not textbook example parsing):

```
Extracted tables (CSV)
    ↓ promote to data/standards/promoted/<standard>/
YAML calc report inputs (from table data)
    ↓ validate against existing Python code
Code-validated outputs
    ↓ generate-calc-report.py
HTML calculation report
```

### Steps

1. **Deep-extract** the PDF: `deep-extract.py --input <pdf> --domain <domain> --report`
2. **Review tables**: identify high-value reference data (constants, coefficients, safety factors)
3. **Promote tables**: copy to `data/standards/promoted/<standard>/` with clean names
4. **Check existing code**: does `digitalmodel/` or `assetutilities/` already implement this?
5. **Create calc report YAML**: map extracted table values to inputs, compute outputs
6. **Validate**: run Python code with same inputs, compare outputs
7. **Generate HTML**: `generate-calc-report.py <calc-report>.yaml`

### Proven Examples

| Calc Report | Standard | Tables Used |
|-------------|----------|-------------|
| `cp-anode-design-dnv-rp-b401.yaml` | DNV-RP-B401 | Tables 10-1 to 10-8 |
| `pipeline-stability-dnv-rp-f109.yaml` | DNV-RP-F109 | Table 3-5 |
| `fatigue-sn-curve-dnv-rp-c203.yaml` | DNV-RP-C203 | Table 2-1 (14 S-N curves) |

### Why Not Worked Examples?

Engineering standards don't use textbook "Example N.N: Given: Solution:" format.
Calculation procedures are inline in numbered sections. The table→YAML→code pipeline
extracts the reference data and validates against implemented code — more reliable
than text parsing.

**WRK-1188 finding**: 0 worked examples found across 9 major engineering standards
(DNV-RP-B401, C203, F109, API RP 2A, 579-1, etc.). Deprioritize worked_example
extraction for standards; focus extraction effort on tables.

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/data/doc_intelligence/deep_extract.py` | Post-processing orchestrator |
| `scripts/data/doc_intelligence/table_exporter.py` | Manifest tables → CSV |
| `scripts/data/doc_intelligence/worked_example_parser.py` | Enhanced example parsing (textbooks) |
| `scripts/data/doc_intelligence/chart_extractor.py` | PDF image extraction + metadata |
| `scripts/data/doc-intelligence/deep-extract.py` | CLI entry point |
| `scripts/reporting/generate-calc-report.py` | YAML → HTML calc report |

## Promoted Table Locations

```
data/standards/promoted/
├── dnv-rp-b401/    # 8 CP design tables
├── dnv-rp-c203/    # 2 S-N curve tables (air + seawater)
└── dnv-rp-f109/    # 3 stability tables
```
