# Docling Evaluation

**Issue:** #1446
**Date:** 2026-03-31
**Version tested:** 2.83.0
**License:** MIT

## Overview

[docling](https://github.com/docling-project/docling) is an IBM-backed document parsing framework (56k+ stars) that converts PDF, DOCX, PPTX, XLSX, and HTML to structured Markdown, JSON, and Python dicts. It includes OCR, table extraction, and layout understanding, with LangChain/LlamaIndex integration for RAG pipelines.

## Installation

```bash
# As optional dependency
uv sync --extra docling

# Standalone
pip install docling
```

**Install size:** ~5 GB (includes PyTorch and model weights). No GPU required — CPU fallback works.

## Evaluation Results

### HTML Conversion

| Metric | Value |
|--------|-------|
| Conversion time | 0.40s |
| Output length | 773 chars / 24 lines |
| Headings preserved | Yes (h1, h2) |
| Tables preserved | Yes (Markdown pipe tables, aligned) |
| Lists preserved | Yes (bold items, descriptions) |
| Structured dict keys | schema_name, version, body, texts, tables, pages, etc. |

### Output Quality

- Headings correctly mapped to Markdown `#`/`##`
- Tables rendered as pipe-delimited Markdown with numeric alignment
- Bold text and list items preserved
- Engineering content (stress values, equipment tags) intact

### Structured Output

`export_to_dict()` returns rich structure with separate `texts`, `tables`, `pictures`, `pages` arrays — suitable for downstream RAG chunking.

## Integration Fit

**Rating: very-high**

- MIT license (no copyleft concerns)
- Broadest format support among evaluated tools
- Clean Python API: `DocumentConverter().convert(path)`
- Output formats: Markdown, JSON dict, HTML
- LangChain `DoclingLoader` and LlamaIndex `DoclingReader` available

## Comparison with marker-pdf

| Feature | docling | marker-pdf |
|---------|---------|------------|
| License | MIT | GPL-3.0 |
| Formats | PDF, DOCX, PPTX, XLSX, HTML | PDF only |
| Stars | 56k | 19k |
| Install size | ~5 GB | ~3 GB |
| Equation support | Basic | LaTeX conversion |
| RAG integration | LangChain + LlamaIndex | LangChain |

**Recommendation:** Use docling as the default parser for multi-format documents. Use marker-pdf for equation-heavy engineering PDFs where LaTeX output matters.

## Test Coverage

7 tests in `tests/test_docling_integration.py`:
- DocumentConverter initialization
- HTML-to-Markdown conversion
- Heading extraction
- Table data extraction
- Dict export structure
- Conversion timing (<30s)

## Files

- `pyproject.toml` — `[project.optional-dependencies.docling]`
- `scripts/integrations/docling_evaluation.py` — evaluation script
- `tests/test_docling_integration.py` — integration tests
- `data/oss-engineering-catalog.yaml` — catalog entry updated
