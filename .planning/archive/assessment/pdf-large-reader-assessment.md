# pdf-large-reader vs Native AI Agent PDF Capabilities — Decision Assessment

**WRK-341** | Created: 2026-02-24 | Author: workspace-hub orchestrator

---

## 1. pdf-large-reader Capabilities (v1.3.0)

### Core Design

pdf-large-reader is a Python library built on PyMuPDF (fitz) for memory-efficient, headless
processing of large PDF files. It is not a wrapper around AI vision APIs — it performs
deterministic, programmatic text extraction directly from PDF structure.

### Feature Set

| Capability | Detail |
|---|---|
| File size handling | Designed for 100MB+ files; benchmarked to 200MB / 1000 pages |
| Memory model | Three strategies: `full_load` (<10MB), `stream_pages` (10–100MB), `chunk_batch` (≥100MB) |
| Streaming output | Generator mode processes 1000-page PDFs in under 300MB RAM |
| Chunk overlap | `chunk_pdf()` supports configurable overlap between chunks |
| Text extraction | Layout-preserving text via PyMuPDF; handles encoding issues and missing fonts |
| Image extraction | Extracts embedded images as PIL Image objects per page |
| Table extraction | Positional block analysis producing pandas DataFrames |
| Auto strategy | `assess_pdf()` inspects file size, page count, complexity score; selects strategy |
| Progress callbacks | `progress_callback(current, total)` for long batch operations |
| CLI tool | `pdf-large-reader <file> [options]` — scriptable in shell pipelines |
| AI fallback | Optional API-key-based fallback for scanned/unreadable pages |
| Test coverage | 93.58% coverage, 215 tests (170 unit + 45 integration) |
| Python compatibility | Python 3.8–3.12 |

### Processing Pipeline

```
File → assess_pdf() → select_strategy() → stream_pdf_pages() / chunk_pdf()
     → extract_page_full() [text + images + tables]
     → optional fallback (scanned pages)
     → generator / list / text output
```

### Performance Benchmarks (Ubuntu 22.04, Python 3.11, 16GB RAM)

| File Size | Pages | Time | Peak Memory | Strategy |
|---|---|---|---|---|
| 5 MB | 10 | < 5s | ~50 MB | full_load |
| 50 MB | 100 | < 30s | ~150 MB | chunked |
| 100 MB | 500 | < 60s | ~200 MB | stream_pages |
| 200 MB | 1000 | < 2min | ~250 MB | stream_pages |

---

## 2. Native AI Agent PDF Capabilities

### Claude (Anthropic)

- **File upload**: PDFs uploaded as base64 or files via the Files API
- **Page limit**: Approximately 100 pages per request (API and UI)
- **File size limit**: Approximately 32MB per document upload (API limit as of 2025)
- **Reading mode**: Vision-based rendering — reads PDFs as rendered page images
- **Scanned documents**: Handles scanned PDFs well due to vision approach
- **Structured extraction**: Returns natural language; no programmatic DataFrame output
- **Batch processing**: Requires manual upload per document; no headless batch mode
- **CLI integration**: None native — requires wrapper code around API calls
- **Progress tracking**: None — single blocking API call per document
- **Memory footprint**: Offloaded to Anthropic servers; no local memory management required
- **Interactivity**: Excellent for exploratory, conversational document analysis

### Codex / GPT-4.1 (OpenAI) — referenced as fallback in pdf-large-reader

- Similar API-upload model to Claude
- Page and size limits in the same range (~50–100 pages, ~20–50MB)
- Vision-based rendering
- No native headless batch or CLI mode

### Key Limitations of Native AI Agent PDF Reading

1. **File size cap**: Native agents cannot process files larger than ~32MB. A 200MB engineering
   standard or multi-volume report is out of scope for native API reading.
2. **Page count cap**: Approximately 100 pages per request. A 1000-page document requires either
   chunking (manual engineering work) or a purpose-built tool.
3. **No streaming**: Native APIs load the full document context before responding. There is no
   generator or incremental yield mode.
4. **No headless batch**: Batch processing a directory of PDFs requires custom scaffolding around
   the API. There is no built-in queue, resume-safe progress, or CLI.
5. **No structured output from tables**: Native agents return text descriptions of tables, not
   pandas DataFrames ready for downstream computation.
6. **No local/offline operation**: Requires internet, API keys, and incurs token cost per page.
   pdf-large-reader runs fully offline with no per-page cost.
7. **Non-deterministic**: AI vision results can vary between runs; programmatic extraction
   from PDF structure is deterministic.

---

## 3. Gap Analysis

| Use Case | pdf-large-reader | Native AI Agent | Gap Owner |
|---|---|---|---|
| Files > 32MB | Yes (up to 200MB+) | No | pdf-large-reader |
| Files > 100 pages | Yes (1000+ pages) | Limited (~100 pages) | pdf-large-reader |
| Streaming / generator output | Yes | No | pdf-large-reader |
| Headless batch processing | Yes (CLI + Python API) | No | pdf-large-reader |
| Programmatic table extraction (DataFrame) | Yes | No | pdf-large-reader |
| Offline / no-API-cost operation | Yes | No | pdf-large-reader |
| Deterministic extraction | Yes | No | pdf-large-reader |
| Progress callbacks for long jobs | Yes | No | pdf-large-reader |
| Resume-safe chunked processing | Yes | No | pdf-large-reader |
| Scanned PDF reading (OCR) | Partial (fallback only) | Yes | Native AI |
| Complex layout understanding | Limited | Yes | Native AI |
| Semantic comprehension and Q&A | No | Yes | Native AI |
| Single document < 50 pages (interactive) | Works but unnecessary | Yes (preferred) | Native AI |

---

## 4. Decision

### KEEP — pdf-large-reader retains a clear, non-duplicated value proposition.

**Rationale:**

Native AI agents (Claude, GPT-4.1) and pdf-large-reader do not compete in the same problem
space except for a narrow overlap on small documents. For the primary use case that motivated
this tool — processing large engineering standards and project documents stored on drives
containing 4.5TB of material — native AI agents are technically incapable:

- The O&G standards library at `/mnt/ace/O&G-Standards/` contains multi-volume documents
  that routinely exceed 100MB and 500 pages.
- Phase B of WRK-309 explicitly calls out pdf-large-reader as the correct tool for 100MB+
  files in the document intelligence pipeline.
- Automated batch indexing across thousands of documents cannot be done interactively via
  AI chat; it requires a scriptable, headless CLI tool.

Native AI reading is superior for interactive, exploratory analysis of individual documents
under 50 pages where semantic understanding and natural language Q&A are the goal.

**The tools are complementary, not competing.**

---

## 5. Recommended Boundary of Use

| Scenario | Recommended Tool |
|---|---|
| Single PDF < 50 pages, interactive Q&A | Native AI agent (Claude) |
| Single PDF 50–100 pages, Q&A | Native AI agent (Claude), consider pdf-large-reader for structured extraction |
| Single PDF > 100 pages or > 32MB | pdf-large-reader |
| Batch processing any volume of PDFs | pdf-large-reader CLI |
| Automated document indexing pipeline (WRK-309) | pdf-large-reader |
| Structured table extraction to DataFrame | pdf-large-reader |
| Scanned PDF (no embedded text) | Native AI agent or pdf-large-reader with OCR fallback |
| Offline / no API key available | pdf-large-reader |

---

## 6. Recommended Follow-On WRK Items

Given the KEEP decision, the following WRK items represent the highest-value next steps for
pdf-large-reader's unique position:

### WRK-A: OCR Pipeline — Tesseract Integration

Extend pdf-large-reader to handle scanned engineering drawings and reports without requiring
an external AI API. Currently the `fallback.py` module delegates to an external model API for
scanned pages. A Tesseract-based local OCR pipeline would:

- Remove API key dependency for scanned documents
- Enable offline batch OCR of the standards library
- Produce deterministic, reproducible extraction results

**Scope**: `src/fallback.py` — add `TesseractBackend` alongside existing API backend.

### WRK-B: Structured Table Extraction Enhancement

The current `extract_tables()` implementation in `src/extraction.py` uses basic positional
block analysis. Engineering PDFs contain complex multi-row, multi-column tables with merged
cells and header spanning. Upgrading to a proper table detection approach (camelot or
pdfplumber) would:

- Produce clean DataFrames from engineering standards tables
- Support the Phase B summarisation pipeline in WRK-309
- Enable structured extraction of data sheets, equipment specifications, regulatory tables

**Scope**: `src/extraction.py` — upgrade `extract_tables()` with library-backed detection.

### WRK-C: Standards Cross-Reference Extractor

Engineering standards contain dense internal and external clause references (e.g., "see
Section 4.3.2", "per API RP 2A clause 17.6"). An extractor that detects and maps these
references would:

- Build a cross-reference graph across the standards library
- Enable agents to trace regulatory chains without reading full documents
- Feed directly into the registry.yaml linking layer of WRK-309 Phase E

**Scope**: New module `src/cross_reference.py` — regex + structural analysis of extracted text.

---

## 7. Dependent Workflows

The following active WRK items depend on pdf-large-reader continuing:

| WRK Item | Dependency |
|---|---|
| WRK-309 (Document Intelligence) | Phase B extraction pipeline; explicitly calls out pdf-large-reader for 100MB+ files |

No deprecation migration is required.

---

## 8. Summary

pdf-large-reader occupies a well-defined technical niche that native AI agents cannot fill:
memory-efficient, headless, deterministic processing of large PDFs (>32MB, >100 pages) with
structured output (text, images, DataFrames) and CLI integration for automated batch
workflows. The tool is production-grade (v1.3.0, 93.58% test coverage, 215 tests) and
actively needed by WRK-309.

Native AI PDF reading is preferred for interactive, single-document work under 50 pages.
The two capabilities are complementary and both should be maintained.

**Decision: KEEP. Continue investment in pdf-large-reader with focus on OCR pipeline,
table extraction enhancement, and standards cross-reference extraction (WRK-A/B/C above).**
