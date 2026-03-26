# WRK-5037: extract-document.py + document parse layer

## Context

WRK-5036 (doc-extraction skill) established a 3-layer extraction taxonomy with 8 content types. WRK-5037 builds the **runtime parse layer** — a CLI tool that converts raw documents (PDF, DOCX, XLSX) into structured extraction manifests. First target domain: naval architecture (145 PDFs at `/mnt/ace/docs/_standards/SNAME/`).

**Scope boundary:** This WRK extracts raw structural elements (text blocks, tables, headings, figure references). Content type classification (mapping to the 8 Layer 1 types) is a downstream WRK.

## Architecture

Modular Python package (400-line-per-file limit requires splitting):

```
scripts/data/doc_intelligence/           # Python package (underscore for import)
    __init__.py                          # Package marker
    schema.py                            # Manifest dataclasses + validation (~100 lines)
    orchestrator.py                      # Format detection + parser dispatch (~80 lines)
    parsers/
        __init__.py                      # Parser registry
        base.py                          # BaseParser ABC (~40 lines)
        pdf.py                           # PdfParser via pdfplumber (~120 lines)
        docx_parser.py                   # DocxParser via python-docx (~100 lines)
        xlsx.py                          # XlsxParser via openpyxl (~100 lines)

scripts/data/doc-intelligence/
    extract-document.py                  # CLI entry point (~100 lines)
    run-extract.sh                       # Shell wrapper (PYTHONPATH + uv run)

tests/data/doc_intelligence/
    conftest.py                          # Synthetic fixture generators (fpdf2, python-docx, openpyxl)
    test_schema.py                       # 6 tests
    test_pdf_parser.py                   # 5 tests
    test_docx_parser.py                  # 5 tests
    test_xlsx_parser.py                  # 5 tests
    test_orchestrator.py                 # 4 tests
    test_cli.py                          # 4 tests
```

## Manifest Schema (schema.py)

```python
@dataclass
class SourceLocation:
    document: str                        # filename
    section: Optional[str] = None        # heading/section name
    page: Optional[int] = None           # page number (PDF)
    sheet: Optional[str] = None          # sheet name (XLSX)

@dataclass
class ExtractedSection:
    heading: Optional[str]
    level: int                           # 0=body, 1-6=heading level
    text: str
    source: SourceLocation

@dataclass
class ExtractedTable:
    title: Optional[str]
    columns: List[str]
    rows: List[List[str]]
    source: SourceLocation

@dataclass
class ExtractedFigureRef:
    caption: Optional[str]
    figure_id: Optional[str]            # "Figure 3.2"
    source: SourceLocation

@dataclass
class DocumentManifest:
    version: str                         # "1.0.0"
    tool: str                            # "extract-document/1.0.0"
    domain: str                          # --domain flag value
    metadata: DocumentMetadata           # filename, format, size, pages, checksum, timestamp
    sections: List[ExtractedSection]
    tables: List[ExtractedTable]
    figure_refs: List[ExtractedFigureRef]
    extraction_stats: Dict[str, int]     # {sections: N, tables: N, figure_refs: N}
    errors: List[str]                    # non-fatal warnings
```

Output path: `data/doc-intelligence/manifests/<domain>/<filename>.manifest.yaml` (gitignored).

## Reusable Code

| What | Source | How |
|------|--------|-----|
| DocumentMetadata dataclass | `scripts/utilities/doc-to-context/src/doc_to_context.py` | Copy fields, adapt |
| Checksum (SHA-256) | `doc_to_context.py:_compute_checksum()` | Reuse pattern |
| Atomic YAML writes | `scripts/data/pipeline/manifest.py` | `os.replace(tmp, target)` |
| PDF extraction | `doc_to_context.py` + `phase-b-extract.py` | pdfplumber patterns |
| DOCX extraction | `phase-b-extract.py:extract_docx()` | `Document(path).paragraphs` |
| XLSX extraction | `phase-b-extract.py:extract_xlsx()` | `load_workbook(read_only=True)` |

## Dependencies

PEP 723 inline metadata for `extract-document.py`:
- `pyyaml`, `pdfplumber`, `python-docx`, `openpyxl`

Test-only: `fpdf2` (synthetic PDF fixture generation, pure Python)

NOT in scope: `python-magic` (system dep), OCR (`pytesseract`), `PyPDF2` (pdfplumber suffices).

## TDD Sequence

| Phase | Tests | Then Implement |
|-------|-------|----------------|
| 1 | `test_schema.py` (6 tests): round-trip YAML, validate valid/invalid, atomic write | `schema.py` |
| 2 | `test_pdf_parser.py` (5 tests): can_handle, text extraction, table extraction, corrupt file | `parsers/base.py` + `parsers/pdf.py` |
| 3 | `test_docx_parser.py` (5 tests): can_handle, headings+body, tables, heading hierarchy, corrupt | `parsers/docx_parser.py` |
| 4 | `test_xlsx_parser.py` (5 tests): can_handle, sheet→table, multi-sheet, skip empty rows, corrupt | `parsers/xlsx.py` |
| 5 | `test_orchestrator.py` (4 tests): format detection, parser dispatch, manifest write, unsupported | `orchestrator.py` |
| 6 | `test_cli.py` (4 tests): missing --input, valid input, --domain propagation, missing file | `extract-document.py` + `run-extract.sh` |

**Total: 29 tests, 6 phases**

Fixtures generated programmatically in `conftest.py` (no binary files committed).

## Execution

```bash
# Run tests
PYTHONPATH=scripts uv run --no-project --with fpdf2 --with pdfplumber --with python-docx --with openpyxl --with pyyaml \
    python -m pytest tests/data/doc_intelligence/ -v

# Smoke test on real PDF
bash scripts/data/doc-intelligence/run-extract.sh \
    --input /mnt/ace/docs/_standards/SNAME/textbooks/<file>.pdf \
    --domain naval-architecture
```

## Verification

1. All 29 tests pass
2. Smoke test produces valid manifest YAML for a real SNAME PDF
3. Manifest contains sections, tables, and figure_refs with correct source locations
4. Corrupt file handling returns manifest with errors list populated, exit 0
5. `--output` flag writes to specified path; default auto-generates path under `data/doc-intelligence/manifests/`
