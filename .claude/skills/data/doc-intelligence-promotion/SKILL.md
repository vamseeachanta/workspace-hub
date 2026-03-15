---
name: doc-intelligence-promotion
description: Post-processing pipeline for document extraction — tables to CSV, worked examples to pytest, charts to calibration metadata
version: 1.0.0
category: data
type: skill
trigger: manual
auto_execute: false
tools: [Read, Write, Edit, Bash, Grep, Glob]
related_skills: [doc-extraction, dark-intelligence-workflow, document-batch]
---

# Document Intelligence Promotion

> Single-pass extraction + multi-stage post-processing pipeline.

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

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/data/doc_intelligence/deep_extract.py` | Post-processing orchestrator |
| `scripts/data/doc_intelligence/table_exporter.py` | Manifest tables → CSV |
| `scripts/data/doc_intelligence/worked_example_parser.py` | Enhanced example parsing |
| `scripts/data/doc_intelligence/chart_extractor.py` | PDF image extraction + metadata |
| `scripts/data/doc-intelligence/deep-extract.py` | CLI entry point |
