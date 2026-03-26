# WRK-5037: extract-document.py + Document Parse Layer

## Context

The doc-intelligence platform needs a parse layer that converts raw documents (PDF, DOCX, XLSX) into extraction manifest YAML files. This is the foundation — downstream tools (indexer WRK-5038, query WRK-5039, promote WRK-5040) all consume these manifests. The doc-extraction skill (WRK-5036, done) defines the AI-guided extraction protocol; this WRK builds the deterministic parsing infrastructure around it.

First target domain: naval architecture (145 PDFs at `/mnt/ace/docs/_standards/SNAME/`).

## Design Spec Reference

`docs/superpowers/specs/2026-03-12-doc-intelligence-platform-design.md` — canonical schema.

## File Structure

```
scripts/data/doc-intelligence/
  extract-document.py          # CLI entry point
  lib/
    __init__.py
    parser_base.py             # ABC + ParseResult dataclass + factory
    parser_pdf.py              # pdfplumber
    parser_docx.py             # python-docx
    parser_xlsx.py             # openpyxl
    manifest.py                # ExtractionManifest dataclass + YAML serialization + validation
    utils.py                   # atomic_write, generate_doc_ref, check_source_available

tests/data/doc-intelligence/
  __init__.py
  conftest.py
  fixtures/
    sample.pdf                 # 2-page: title+table, paragraph+figure ref
    sample.docx                # heading hierarchy + table + hyperlinks
    sample.xlsx                # 3 sheets: Summary, Data, Metadata (merged cells)
    corrupt.pdf                # invalid header bytes
  test_parser_pdf.py
  test_parser_docx.py
  test_parser_xlsx.py
  test_manifest.py
  test_cli.py
  test_integration.py
```

## Architecture

### Pipeline (stages from design spec)
```
1. Fetch    — resolve path, check existence
2. Parse    — pdfplumber/python-docx/openpyxl → ParseResult
3-5.        — (out of scope: AI-guided extraction via doc-extraction skill)
6. Legal    — stub call to scripts/legal/legal-sanity-scan.sh
7. Save     — atomic write (tempfile → os.rename) to data/doc-intelligence/manifests/<domain>/
```

### Key classes

**ParseResult** (dataclass):
- `text: str` — full extracted text
- `sections: list[Section]` — heading + content pairs
- `tables: list[Table]` — column headers + rows
- `figures: list[Figure]` — figure refs (label, page, bounding box)
- `metadata: dict` — title, author, page_count, etc.
- `warnings: list[str]`

**ExtractionManifest** (dataclass):
- All fields per design spec schema (doc_ref, doc_title, doc_type, domain, source, etc.)
- `document_map` populated from ParseResult
- 8 content arrays start empty (filled by AI extraction, not this script)
- `from_parse_result()` class method creates skeleton
- `to_yaml()` serializer, `validate()` returns errors list

**Parser** (ABC):
- `parse(file_path) -> ParseResult`
- `get_parser(file_path) -> Parser` factory

### CLI interface
```bash
uv run --no-project python scripts/data/doc-intelligence/extract-document.py \
  --input /path/to/doc.pdf \
  --output data/doc-intelligence/manifests/naval-architecture/doc-ref.yaml \
  --domain naval-architecture \
  [--doc-ref custom-ref] [--title "Override Title"] [--version "Rev 1"] \
  [--dry-run] [--verbose]
```

Exit codes: 0=success, 1=file not found, 2=unsupported type, 3=parse error, 4=legal blocked, 5=validation error.

### Dependencies (installed via uv)
- pdfplumber >= 0.10.0
- python-docx >= 0.8.11
- openpyxl >= 3.10.0
- pyyaml >= 6.0

## Implementation Order (TDD)

### Step 1: Fixtures + conftest
Create test fixture files (sample.pdf, sample.docx, sample.xlsx, corrupt.pdf).
Write `conftest.py` with fixture path helpers.

### Step 2: ParseResult + Parser base (RED → GREEN)
- Test: `test_parser_base_factory_returns_correct_parser`
- Test: `test_parser_base_unsupported_raises`
- Implement: `parser_base.py` with ABC, ParseResult, Section, Table, Figure dataclasses

### Step 3: PDF parser (RED → GREEN)
- Tests: text extraction, section detection, table extraction, figure detection, corrupt file error, metadata
- Implement: `parser_pdf.py` using pdfplumber

### Step 4: DOCX parser (RED → GREEN)
- Tests: heading hierarchy, tables, embedded objects, metadata
- Implement: `parser_docx.py` using python-docx

### Step 5: XLSX parser (RED → GREEN)
- Tests: multi-sheet, merged cells, sheet metadata
- Implement: `parser_xlsx.py` using openpyxl

### Step 6: Manifest schema (RED → GREEN)
- Tests: required fields, from_parse_result skeleton, to_yaml roundtrip, validation errors
- Implement: `manifest.py`

### Step 7: Utils (RED → GREEN)
- Tests: atomic write, doc-ref generation, source availability check
- Implement: `utils.py`

### Step 8: CLI + integration (RED → GREEN)
- Tests: arg parsing, missing input exit code, dry-run, end-to-end PDF/DOCX/XLSX
- Implement: `extract-document.py` main

## Verification

```bash
# Run all tests
uv run --no-project python -m pytest tests/data/doc-intelligence/ -v

# Manual end-to-end with a real naval arch PDF
uv run --no-project python scripts/data/doc-intelligence/extract-document.py \
  --input /mnt/ace/docs/_standards/SNAME/textbooks/Introduction-to-Naval-Architecture-Tupper-1996.pdf \
  --output data/doc-intelligence/manifests/naval-architecture/tupper-1996.yaml \
  --domain naval-architecture --verbose

# Verify manifest written
cat data/doc-intelligence/manifests/naval-architecture/tupper-1996.yaml | head -30
```

## Existing Code to Reuse

### HIGH priority — adapt directly

| Source | Path | What to reuse |
|--------|------|---------------|
| doc-to-context | `scripts/utilities/doc-to-context/src/doc_to_context.py` | `DocumentMetadata` dataclass (lines 64-83), lazy import pattern (`HAS_PDF_SUPPORT` etc.), `PDFParser` pdfplumber logic (lines 112-234), `WordParser` DOCX heading/table extraction (lines 236-325), `ExcelParser` sheet iteration + formula detection (lines 328-427), `_compute_checksum()` helper |
| phase-b-extract | `scripts/data/document-index/phase-b-extract.py` | File extension routing pattern (`extract_text()` lines 148-187), proven PDF/DOCX/XLSX extraction with error handling |
| pipeline manifest | `scripts/data/pipeline/manifest.py` | `ManifestManager` atomic write pattern: `tmp.write_text() → os.replace(tmp, path)` (lines 43-46) |

### Adaptation notes
- doc-to-context parsers output `DocumentContent` (markdown-oriented) — we need to adapt to output `ParseResult` (structure-oriented for manifest generation)
- Reuse the proven pdfplumber table extraction, DOCX heading detection, and XLSX sheet iteration logic
- Copy the atomic write pattern from ManifestManager verbatim
- Keep lazy imports (`HAS_PDF_SUPPORT` etc.) for graceful error messages
- doc-to-context uses `python-magic` for MIME detection — we can use simpler extension-based routing (like phase-b-extract)

### Other references
- Legal scan: `scripts/legal/legal-sanity-scan.sh`
- Doc-extraction skill: `.claude/skills/engineering/doc-extraction/SKILL.md`
- Naval arch catalogue: `knowledge/seeds/naval-architecture-resources.yaml`
- Test structure pattern: `tests/data/pipeline/`
