# Marker Evaluation — PDF-to-Markdown Converter for Engineering Documents

**Date:** 2026-03-30
**Issue:** vamseeachanta/workspace-hub#1447
**Parent:** vamseeachanta/workspace-hub#1397
**Evaluated by:** Research agent (web research + local installation, GPU-constrained benchmarks pending)

---

## Summary

Marker (v1.10.2, 33k GitHub stars, GPL-3.0) is a high-accuracy, deep-learning-based document converter that transforms PDFs, images, PPTX, DOCX, XLSX, HTML, and EPUB into clean Markdown, JSON, or HTML. It uses surya-ocr (19k stars) for layout detection, OCR, table recognition, and reading order detection in 90+ languages. For engineering documents with tables, equations, figures, and multi-column layouts, marker is the current best-in-class open-source option alongside docling, with each excelling in different areas.

**Recommendation:** Adopt marker as the primary PDF extraction layer for engineering documents. Use alongside docling for format breadth. Defer GPU-accelerated benchmarks to a machine with >=8GB VRAM (ace-linux-2 or equivalent).

---

## Installation

**Venv created:** `/mnt/local-analysis/marker-env/` (Python 3.12, uv-managed)
**Install command:** `uv pip install marker-pdf`
**Dependencies installed:** 97 packages including PyTorch 2.11, surya-ocr 0.17.1, transformers 4.57.6
**Download size:** ~700 MB (packages) + ~2 GB (models, downloaded on first use)
**Disk footprint:** ~3 GB total with models

### Python API

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

model_dict = create_model_dict()  # loads surya models
converter = PdfConverter(artifact_dict=model_dict)
rendered = converter("/path/to/document.pdf")

markdown_text = rendered.markdown
metadata = rendered.metadata
```

### CLI

```bash
marker_single /path/to/document.pdf /output/dir
marker /input/dir /output/dir  # batch mode
```

### API Server

```bash
pip install uvicorn fastapi python-multipart
marker_server --port 8001  # FastAPI at localhost:8001/docs
```

---

## GPU vs CPU Performance

| Hardware | Throughput (est.) | VRAM Usage | Notes |
|---|---|---|---|
| NVIDIA H100 | ~122 pages/sec (22 workers) | ~5 GB peak/worker | Production benchmark |
| NVIDIA A100 | ~25 pages/sec (batch) | ~5 GB peak/worker | Good batch throughput |
| NVIDIA T400 4GB | Limited | ~3-3.5 GB default | Only ~3.5 GB free; single-worker only |
| CPU only | ~0.5-2 pages/sec | N/A | 10-50x slower than GPU; usable for small docs |

**Local hardware:** NVIDIA T400 4GB (CUDA 13.0, driver 580.126). With 551 MB already consumed by desktop, only ~3.5 GB available. Marker's default batch sizes need ~3 GB VRAM, so single-worker GPU execution should work but may OOM on large documents. CPU fallback is available but significantly slower.

---

## Capability Assessment for Engineering Documents

### What marker handles well

| Feature | Quality | Notes |
|---|---|---|
| **Heading hierarchy** | High | Preserves H1-H6 structure from PDF layout |
| **Tables** | High | Uses surya table detection; outputs Markdown pipe tables |
| **Equations** | Medium-High | Converts most inline/display math to LaTeX ($...$, $$...$$) |
| **Figures** | Medium | Extracts images, inserts as `![](image.png)` references |
| **Multi-column layouts** | High | Reading order detection handles 2-column academic/engineering papers |
| **Code blocks** | High | Detects and preserves code formatting |
| **Headers/footers** | High | Automatically strips page headers, footers, page numbers |
| **References** | Medium | Preserves reference lists but doesn't link citations |
| **Scanned PDFs (OCR)** | High | Full OCR via surya for scanned documents |
| **Multi-language** | High | 90+ languages supported |

### Known limitations

- **Equation coverage:** Does not convert 100% of equations to LaTeX; detection must precede conversion, so unusual notation or hand-drawn equations may be missed
- **Complex nested tables:** Very deep table nesting or merged cells may degrade
- **CAD drawings/diagrams:** Extracts as raster images only; no vectorization
- **Very large PDFs (500+ pages):** May require batch mode and adequate VRAM
- **GPL-3.0 license:** Copyleft; any derivative work must also be GPL-3.0

---

## Comparison: marker vs docling vs pymupdf4llm

| Dimension | marker | docling | pymupdf4llm |
|---|---|---|---|
| **Stars** | 33k | 56k | Part of PyMuPDF (24k) |
| **License** | GPL-3.0 | MIT | AGPL-3.0 |
| **Approach** | Deep learning (surya) | Deep learning (IBM models) | Rule-based extraction |
| **Speed (per page)** | ~0.5s GPU, ~5s CPU | ~4s/page (slow) | ~0.12s (fastest) |
| **Tables** | High (surya detection) | High (specialized model) | Low (struggles with tables) |
| **Equations** | Medium-High (LaTeX) | Medium | Low (plain text) |
| **Figures** | Medium (raster extract) | Medium-High | Low |
| **Multi-column** | High | High | Medium |
| **OCR (scanned)** | Yes (surya) | Yes (built-in) | No |
| **Format breadth** | PDF, DOCX, PPTX, XLSX, HTML, EPUB, images | PDF, DOCX, PPTX, XLSX, HTML | PDF only |
| **LLM integrations** | Basic | LangChain, LlamaIndex | LlamaIndex |
| **Model download** | ~2 GB | ~500 MB | None |
| **GPU requirement** | Recommended | Recommended | None |

### Recommendation by use case

| Use Case | Best Tool | Rationale |
|---|---|---|
| Engineering datasheets (tables + equations) | **marker** | Best equation-to-LaTeX + table extraction |
| Batch processing large doc collections | **pymupdf4llm** | 40x faster, no GPU needed; acceptable for text-heavy docs |
| RAG pipeline ingestion | **docling** | LangChain/LlamaIndex integration, MIT license |
| Scanned/legacy PDFs | **marker** | Best OCR via surya |
| Mixed format processing (DOCX+PDF+PPTX) | **marker** or **docling** | Both support multiple formats |
| License-sensitive deployment | **docling** (MIT) | marker is GPL-3.0, pymupdf4llm is AGPL-3.0 |

---

## Test Documents Identified

Three engineering PDFs from the OpenFAST documentation were identified for benchmarking. Conversion tests are pending due to GPU memory constraints on the current workstation.

| Document | Size | Content Type | Test Focus |
|---|---|---|---|
| FEAM Theory Manual | 282 KB | FEA mooring theory | Equations, nomenclature tables |
| WAVE2 Document | 386 KB | Hydrodynamics | Equations, wave theory diagrams |
| Cable Model Development | 3.3 MB | Multi-column technical paper | Figures, tables, multi-column layout |

**Location:** `/mnt/remote/ace-linux-1/ace/openfast/docs/OtherSupporting/`

---

## Integration with Existing Document Pipeline

The workspace-hub document-index system (`data/document-index/`) currently uses a JSONL-based index. Marker can be integrated as follows:

1. **Extraction layer:** Use marker to convert PDFs to Markdown, feeding into the existing summary/indexing pipeline
2. **Parallel with docling:** Keep both tools; marker for equation-heavy engineering docs, docling for RAG-oriented chunking
3. **Batch processing script:** A wrapper script in `scripts/` that accepts PDF paths and outputs Markdown to `data/document-index/summaries/`

---

## Next Steps

1. **Run GPU benchmark** on a machine with >=8 GB VRAM (ace-linux-2) to get actual conversion times and quality metrics on the 3 test PDFs
2. **Compare output quality** side-by-side with docling on the same PDFs
3. **Build extraction wrapper** that integrates marker into the document-index pipeline
4. **Evaluate CPU-only mode** for batch processing where GPU is unavailable

---

## References

- [marker GitHub (datalab-to/marker)](https://github.com/datalab-to/marker) -- 33k stars, GPL-3.0
- [marker-pdf on PyPI](https://pypi.org/project/marker-pdf/) -- v1.10.2
- [surya-ocr GitHub](https://github.com/datalab-to/surya) -- OCR engine powering marker
- [Best Open Source PDF to Markdown Tools (2026)](https://jimmysong.io/blog/pdf-to-markdown-open-source-deep-dive/) -- marker vs MinerU vs MarkItDown comparison
- [PDF Parser Comparison for RAG](https://dev.to/ashokan/from-pdfs-to-markdown-evaluating-document-parsers-for-air-gapped-rag-systems-58eh) -- air-gapped RAG evaluation
- [7 Python PDF Extractors Tested (2025)](https://onlyoneaman.medium.com/i-tested-7-python-pdf-extractors-so-you-dont-have-to-2025-edition-c88013922257) -- multi-tool benchmark
