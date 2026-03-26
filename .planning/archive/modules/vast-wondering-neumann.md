# WRK-5041: extract-url.py — Internet Document Extraction Pipeline

## Context

The doc-intelligence pipeline (`extract-document.py`) currently handles local files only. Engineering references exist online (MIT OCW lectures, classification society rules, Aalto CC BY notes) catalogued in `knowledge/seeds/naval-architecture-resources.yaml`. This WRK extends the pipeline to fetch and extract from URLs, reusing ~80% of existing infrastructure.

## Architecture Decision

**Extend the existing parser registry** — add an `HtmlParser` alongside existing PDF/DOCX/XLSX parsers. For URL PDFs, download to cache then delegate to existing `PdfParser`. This avoids duplicating extraction logic.

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/data/doc-intelligence/extract-url.py` | CLI entry point (~90 lines) |
| `scripts/data/doc_intelligence/parsers/html.py` | HTML parser using BeautifulSoup (~100 lines) |
| `scripts/data/doc_intelligence/fetcher.py` | URL fetcher with caching, robots.txt, rate limit (~120 lines) |
| `scripts/data/doc-intelligence/run-extract-url.sh` | Shell wrapper with `--with` deps |
| `tests/data/doc_intelligence/test_html_parser.py` | HTML parser unit tests |
| `tests/data/doc_intelligence/test_fetcher.py` | Fetcher unit tests |
| `tests/data/doc_intelligence/test_extract_url_cli.py` | CLI integration tests |

## Files to Modify

| File | Change |
|------|--------|
| `scripts/data/doc_intelligence/utils.py` | Add `generate_doc_ref_from_url(url, title)` — SHA256(url)[:8] + kebab(title) |
| `scripts/data/doc_intelligence/parsers/__init__.py` | Register `HtmlParser` in `PARSERS` list |

## Implementation Steps (TDD)

### Step 1: `utils.py` — URL doc-ref generation
- **Test**: `test_generate_doc_ref_from_url` — URL hash + title → kebab-case ref
- **Impl**: `generate_doc_ref_from_url(url: str, title: str | None) -> str`
- Format: `{sha256(url)[:8]}-{kebab(title)[:60]}` (e.g., `a3f1b2c4-mit-ocw-marine-hydrodynamics-lecture-1`)

### Step 2: `fetcher.py` — URL fetcher with cache + robots.txt
- **Test**: `test_fetcher.py` — cache hit/miss, content-type detection, robots.txt check
- **Impl**: `UrlFetcher` class
  - `fetch(url) -> FetchResult(content_bytes, content_type, cached, status_code)`
  - Cache dir: `data/doc-intelligence/cache/{domain}/{sha256(url)[:16]}.{ext}`
  - `robots.txt` check via `urllib.robotparser`
  - Rate limit: 1 req/sec per domain (simple `time.sleep`)
  - User-Agent: `workspace-hub-doc-intelligence/1.0`

### Step 3: `parsers/html.py` — HTML text + table extraction
- **Test**: `test_html_parser.py` — fixture HTML with headings, paragraphs, tables
- **Impl**: `HtmlParser(BaseParser)`
  - `can_handle()` checks `.html`/`.htm` extension
  - `parse()` uses BeautifulSoup to extract:
    - `<h1>`–`<h6>` → `ExtractedSection` (with heading level)
    - `<p>`, `<div>` text → `ExtractedSection` (level=0)
    - `<table>` → `ExtractedTable` (first `<tr>` = columns)
  - `SourceLocation.document` = URL (not filename)

### Step 4: `extract-url.py` — CLI entry point
- **Test**: `test_extract_url_cli.py` — exit codes, dry-run, HTML vs PDF URL routing
- **Impl**: CLI args: `--url`, `--output`, `--domain`, `--doc-ref`, `--dry-run`, `--verbose`, `--no-cache`
- Flow:
  1. Fetch URL via `UrlFetcher`
  2. Detect content type (HTML vs PDF)
  3. If PDF: save to temp file → delegate to `PdfParser`
  4. If HTML: save to temp file → delegate to `HtmlParser`
  5. Set `doc_ref` via `generate_doc_ref_from_url()`
  6. Set `tool: "extract-url/1.0.0"` in manifest
  7. Write manifest to output path
- Exit codes: 0=success, 1=fetch failed, 2=robots.txt blocked, 3=extraction failed

### Step 5: `run-extract-url.sh` — shell wrapper
- Mirror `run-extract.sh` pattern, add `--with requests --with beautifulsoup4`

### Step 6: Register HtmlParser
- Add `HtmlParser` to `parsers/__init__.py` PARSERS list

## Reusable Components (no duplication)

- `DocumentManifest`, `ExtractedSection`, `ExtractedTable`, `SourceLocation` — as-is from `schema.py`
- `write_manifest()` — as-is from `schema.py`
- `PdfParser.parse()` — delegate PDF URLs to existing parser after download
- `generate_doc_ref()` — existing function remains for file-based refs
- `_compute_checksum()` — reuse from `orchestrator.py` (or extract to utils)

## Dependencies

- `requests` — HTTP fetching (stdlib `urllib` lacks session/retry ergonomics)
- `beautifulsoup4` — HTML parsing (robust against malformed HTML)
- All injected via `uv run --with` in shell wrapper (no pyproject.toml change needed)

## Verification

```bash
# Run unit tests
uv run --no-project --with pyyaml --with pdfplumber --with python-docx --with openpyxl \
  --with requests --with beautifulsoup4 --with fpdf2 \
  python -m pytest tests/data/doc_intelligence/ -v

# CLI smoke test (dry-run, no network)
bash scripts/data/doc-intelligence/run-extract-url.sh \
  --url "https://ocw.mit.edu/courses/2-20-marine-hydrodynamics-13-021-spring-2005/pages/lecture-notes/" \
  --domain naval-architecture --dry-run --verbose
```
