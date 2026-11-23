# Docling Evaluation — IBM Document Parsing Framework for Engineering Documents

**Date:** 2026-03-30
**Issue:** vamseeachanta/workspace-hub#1446
**Parent:** vamseeachanta/workspace-hub#1397
**Evaluated by:** Research agent (web research; installation and benchmarks pending Bash access)

---

## Summary

Docling (v2.82.0, 56k GitHub stars, MIT license) is IBM's open-source document parsing framework that converts PDF, DOCX, PPTX, XLSX, HTML, images, and more into structured output (Markdown, JSON, DoclingDocument). It uses DocLayNet for layout analysis and TableFormer for table structure recognition. The project was developed by IBM Research Zurich's AI for Knowledge team and has been donated to the Linux Foundation's Agentic AI Foundation (AAIF).

**Recommendation:** Adopt docling as the primary multi-format document parser and RAG integration layer. Use alongside marker for equation-heavy engineering PDFs where marker's surya-based LaTeX conversion excels. Docling's MIT license, broader format support, and native LangChain/LlamaIndex integration make it the better choice for pipeline infrastructure.

---

## Installation

**Venv target:** `/mnt/local-analysis/docling-env/` (Python 3.12, pip-managed)
**Install command:** `pip install docling`
**Note:** `uv` is not currently available on dev-primary; use pip or install uv first.
**Dependencies:** ~500 MB including AI models (DocLayNet, TableFormer, Granite-Docling-258M)
**Python requirement:** 3.10+ (3.9 support dropped in v2.70.0)

**Status:** Installation not yet performed (Bash access required).

### Python API

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("/path/to/document.pdf")

# Export formats
markdown = result.document.export_to_markdown()
json_doc = result.document.export_to_dict()
```

### CLI

```bash
docling /path/to/document.pdf              # single file
docling /path/to/documents/                # directory batch
docling --from pdf --to md document.pdf    # explicit format
```

### API Server (docling-serve)

```bash
pip install docling-serve
docling-serve --port 8000  # FastAPI at localhost:8000/docs
```

### Advanced Configuration (OCR)

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractOcrOptions()

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

---

## Supported Formats

| Format | Input | Notes |
|---|---|---|
| PDF | Yes | Native + OCR for scanned |
| DOCX | Yes | Microsoft Word |
| PPTX | Yes | Microsoft PowerPoint |
| XLSX | Yes | Microsoft Excel |
| HTML | Yes | Web pages |
| Images (PNG, JPEG, TIFF) | Yes | Via OCR pipeline |
| LaTeX | Yes | |
| Plain text | Yes | |
| WAV, MP3, WebVTT | Yes | Audio/subtitle transcription |
| EPUB | No | marker supports this; docling does not |

---

## Capability Assessment for Engineering Documents

### What docling handles well

| Feature | Quality | Notes |
|---|---|---|
| **Table extraction** | Very High | TableFormer model with FAST/ACCURATE modes; 94-97.9% accuracy on complex tables |
| **Layout analysis** | Very High | DocLayNet-trained; handles multi-column, figures, captions |
| **OCR (scanned docs)** | High | Multiple backends: EasyOCR, Tesseract, built-in |
| **Multi-format support** | Very High | Broadest format coverage among open-source tools |
| **Reading order** | High | AI-based reading order detection |
| **Figures** | Medium-High | Extracts and classifies figure regions |
| **Heading hierarchy** | High | Preserves document structure |
| **RAG chunking** | Very High | Native document-aware chunking via quackling |
| **LLM integrations** | Very High | First-class LangChain (DoclingLoader) + LlamaIndex (DoclingReader, DoclingNodeParser) |

### Known limitations

- **Equations:** Medium quality; does not match marker's LaTeX conversion capability
- **Speed:** ~4s/page on GPU, ~17+s for complex documents; slower than marker (~0.5s/page GPU) and pymupdf4llm (~0.12s/page)
- **Model download:** Requires ~500 MB of AI models on first use
- **GPU recommended:** Best performance with NVIDIA GPU; CPU mode is significantly slower
- **EPUB:** Not supported (marker handles EPUB)

---

## Head-to-Head: docling vs marker

| Dimension | docling | marker | Winner |
|---|---|---|---|
| **Stars** | 56k | 33k | docling |
| **License** | MIT | GPL-3.0 | **docling** (permissive) |
| **Format breadth** | PDF, DOCX, PPTX, XLSX, HTML, images, LaTeX, audio | PDF, DOCX, PPTX, XLSX, HTML, EPUB, images | **docling** (audio, LaTeX) |
| **Table extraction** | Very High (TableFormer, 94-97.9%) | High (surya detection) | **docling** |
| **Equation-to-LaTeX** | Medium | Medium-High | **marker** |
| **OCR quality** | High (EasyOCR, Tesseract) | High (surya, 90+ languages) | Tie |
| **Speed (GPU)** | ~0.49s/page (L4) | ~0.86s/page (L4); ~0.5s/page general | **docling** on L4 benchmarks |
| **Speed (CPU)** | Slow (~17s complex docs) | ~5s/page | **marker** |
| **RAG integration** | Native (LangChain, LlamaIndex, chunking) | Basic | **docling** |
| **Chunking** | Document-native (quackling) | Manual | **docling** |
| **Model size** | ~500 MB (258M param VLM) | ~2 GB (surya models) | **docling** (smaller) |
| **Community** | 196 contributors, IBM-backed, Linux Foundation | 27 contributors | **docling** |
| **Maturity** | Production (IBM, AAIF) | Production | Tie |
| **Multi-column** | High | High | Tie |

### Recommendation by use case

| Use Case | Best Tool | Rationale |
|---|---|---|
| RAG pipeline ingestion | **docling** | Native LangChain/LlamaIndex, document-aware chunking, MIT license |
| Engineering datasheets (equations) | **marker** | Superior LaTeX equation conversion |
| Multi-format batch processing | **docling** | Broadest format support including audio |
| Table-heavy documents | **docling** | TableFormer achieves 94-97.9% accuracy |
| Scanned/legacy PDFs | Either | Both have strong OCR |
| License-sensitive deployment | **docling** (MIT) | marker is GPL-3.0 |
| EPUB processing | **marker** | docling doesn't support EPUB |
| CPU-constrained environments | **marker** | Faster CPU-only performance |

---

## Granite-Docling Vision Language Model

IBM released **Granite-Docling-258M**, a compact vision-language model (Apache 2.0) that unifies document parsing into a single model:

- **Architecture:** 258M parameter VLM
- **Capability:** Parses PDFs, slides, and scanned pages directly into structured formats
- **License:** Apache 2.0 (even more permissive than docling's MIT)
- **Deployment:** Available via Docling, also runs standalone
- **Enterprise:** Docling OpenShift Operator launched with Red Hat for bank-grade deployment

---

## LangChain Integration Detail

```python
from langchain_docling import DoclingLoader

# Single document
loader = DoclingLoader(file_path="document.pdf")
docs = loader.load()  # returns List[Document]

# Chunked mode (default) for RAG
loader = DoclingLoader(
    file_path="document.pdf",
    export_type="DOC_CHUNKS"  # document-native chunking
)
chunks = loader.load()

# Use with any LangChain vectorstore
from langchain_chroma import Chroma
vectorstore = Chroma.from_documents(chunks, embedding_model)
```

## LlamaIndex Integration Detail

```python
from llama_index.readers.docling import DoclingReader
from llama_index.node_parser.docling import DoclingNodeParser

reader = DoclingReader()
documents = reader.load_data("document.pdf")

node_parser = DoclingNodeParser()
nodes = node_parser.get_nodes_from_documents(documents)
```

---

## Performance Benchmarks (from published sources)

| Hardware | docling | marker | pymupdf4llm | Source |
|---|---|---|---|---|
| NVIDIA L4 | 0.49s/page | 0.86s/page | 0.12s/page | Jimmy Song 2026 |
| NVIDIA H100 | ~1s/page | ~0.008s/page (122p/s, 22 workers) | N/A | Various |
| CPU | ~17s (complex) | ~5s/page | ~0.12s/page | Various |

**Note:** H100 numbers for marker reflect highly parallel multi-worker setup; single-worker comparison favors docling on L4 benchmarks. Real-world performance depends on document complexity, batch size, and hardware.

---

## Test Plan (Pending)

Three engineering PDFs identified in marker-eval.md for head-to-head comparison:

| Document | Size | Content Type | Test Focus |
|---|---|---|---|
| FEAM Theory Manual | 282 KB | FEA mooring theory | Equations, nomenclature tables |
| WAVE2 Document | 386 KB | Hydrodynamics | Equations, wave theory diagrams |
| Cable Model Development | 3.3 MB | Multi-column technical paper | Figures, tables, multi-column layout |

**Location:** `/mnt/remote/ace-linux-1/ace/openfast/docs/OtherSupporting/`

### Additional tests (docling-specific)

| Test | Format | Purpose |
|---|---|---|
| DOCX parsing | .docx | Validate Word document extraction (format marker also supports) |
| PPTX parsing | .pptx | Validate PowerPoint extraction |
| XLSX parsing | .xlsx | Validate Excel extraction |

**Status:** Installation and testing blocked -- requires Bash/shell access to create venv, install docling, and run conversions. See Next Steps.

---

## Integration with Existing Document Pipeline

The workspace-hub document-index system (`data/document-index/`) uses a JSONL-based index. Docling integration path:

1. **Primary extraction layer:** Use docling's DocumentConverter for multi-format ingestion into the document-index pipeline
2. **RAG pipeline:** Leverage LangChain DoclingLoader or LlamaIndex DoclingReader for chunked document ingestion
3. **Complement with marker:** Use marker for equation-heavy engineering PDFs where LaTeX conversion quality matters
4. **Batch processing script:** Create a wrapper in `scripts/` using docling CLI for batch conversion to `data/document-index/summaries/`

---

## Next Steps

1. **Install docling** in `/mnt/local-analysis/docling-env/` (requires Bash access; `pip install docling`)
2. **Run head-to-head PDF benchmark** on the 3 OpenFAST test documents against marker output
3. **Test DOCX/PPTX/XLSX parsing** on sample engineering documents
4. **Test LangChain integration** with a minimal RAG pipeline
5. **GPU benchmark** on ace-linux-2 for production throughput numbers
6. **Build unified extraction wrapper** that routes documents to marker or docling based on content type

---

## References

- [docling GitHub (docling-project/docling)](https://github.com/docling-project/docling) -- 56k stars, MIT
- [docling Documentation](https://docling-project.github.io/docling/) -- official docs
- [docling on PyPI](https://pypi.org/project/docling/) -- v2.82.0
- [docling Quickstart](https://docling-project.github.io/docling/getting_started/quickstart/)
- [IBM Granite-Docling Announcement](https://www.ibm.com/new/announcements/granite-docling-end-to-end-document-conversion)
- [Docling LangChain Integration](https://docs.langchain.com/oss/python/integrations/document_loaders/docling)
- [RAG with LlamaIndex + Docling](https://docling-project.github.io/docling/examples/rag_llamaindex/)
- [PDF Data Extraction Benchmark 2025](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/) -- docling vs Unstructured vs LlamaParse
- [Best Open Source PDF to Markdown Tools 2026](https://jimmysong.io/blog/pdf-to-markdown-open-source-deep-dive/) -- marker vs MinerU benchmark
- [PDF Table Extraction Showdown](https://boringbot.substack.com/p/pdf-table-extraction-showdown-docling) -- docling vs LlamaParse vs Unstructured
- [IBM Multimodal RAG Tutorial](https://www.ibm.com/think/tutorials/build-multimodal-rag-langchain-with-docling-granite)
- [Docling AAAI 2025 Paper](https://research.ibm.com/publications/docling-an-efficient-open-source-toolkit-for-ai-driven-document-conversion)
- [Marker Evaluation](docs/research/marker-eval.md) -- companion evaluation in this repo
