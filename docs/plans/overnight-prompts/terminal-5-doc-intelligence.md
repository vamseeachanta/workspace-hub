# Terminal 5 — Claude/Hermes — Document Intelligence Pipeline Hardening

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to main and push after each task. Do not branch.
Run `git pull origin main` before every push.
TDD: write tests before implementation.
Do NOT ask the user any questions — make reasonable decisions and document them.

IMPORTANT: Do NOT write to docs/architecture/, docs/roadmaps/, docs/dashboards/,
scripts/docs/, scripts/analysis/, digitalmodel/tests/orcawave/, digitalmodel/tests/solver/,
digitalmodel/tests/field_development/, digitalmodel/tests/geotechnical/,
digitalmodel/tests/nde/, digitalmodel/tests/reservoir/, digitalmodel/tests/web/,
docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md, docs/SKILLS_INDEX.md,
docs/modules/tiers/TIER2_REPOSITORY_INDEX.md.
Only write to: scripts/document-intelligence/, tests/document-intelligence/,
docs/document-intelligence/.

## TASK 1: OCR Parser for Scanned PDFs (GH #1617)

### Context
Issue #1617: The doc-intelligence extraction pipeline cannot handle scanned PDFs.
Many engineering documents (standards, drawings, legacy reports) are scanned image PDFs.
Need an OCR parser that integrates with the existing extraction pipeline.

The existing pipeline likely uses PyPDF2, pdfplumber, or similar for text extraction.
Check scripts/document-intelligence/ and scripts/data/ for existing extractors.

### What to do
1. Survey existing extraction scripts:
   - Search for pdf extraction code in scripts/ and digitalmodel/
   - Understand the current extraction pipeline API (input/output format)
2. Write tests first: tests/document-intelligence/test_ocr_parser.py
   - test_detects_scanned_pdf (a PDF with no extractable text → triggers OCR)
   - test_ocr_text_extraction (mock OCR engine, verify text output format)
   - test_mixed_pdf_handling (PDF with some text pages + some scanned pages)
   - test_output_format_matches_pipeline (output matches existing pipeline format)
   - test_handles_corrupt_pdf (graceful error handling)
3. Implement scripts/document-intelligence/ocr-parser.py:
   - Use pytesseract + pdf2image (or Pillow) for OCR
   - Install dependencies: `uv pip install pytesseract pdf2image Pillow` (check if tesseract is available)
   - If tesseract is not installed, document the requirement and make the script
     gracefully skip with a clear message
   - Input: path to PDF file
   - Output: extracted text in same format as existing pipeline
   - Handle mixed PDFs (text pages → direct extract, scanned pages → OCR)
4. Run: `uv run pytest tests/document-intelligence/test_ocr_parser.py -v`

### Acceptance criteria
- scripts/document-intelligence/ocr-parser.py exists with clear docstring
- tests/document-intelligence/test_ocr_parser.py has at least 5 tests
- All tests pass (mock OCR where tesseract not available)
- Script handles both text and scanned PDFs
- Clear error message if tesseract not installed

### Commit message
feat(doc-intel): OCR parser for scanned PDF extraction (#1617)

---

## TASK 2: XLSX Formula Extraction Size Limit Increase (GH #1619)

### Context
Issue #1619: The current XLSX formula extraction has a 15MB size limit.
Large engineering spreadsheets (structural calculations, cost models) exceed this.
Need to raise the limit to 50MB and optimize memory usage for large files.

### What to do
1. Find the existing XLSX extraction code:
   - Search for xlsx, openpyxl, formula extraction in scripts/ and digitalmodel/
2. Write tests: tests/document-intelligence/test_xlsx_extractor.py
   - test_extracts_formulas_from_small_file
   - test_handles_large_file_up_to_50mb (mock — create test XLSX in memory)
   - test_memory_efficient_streaming (verify streaming/chunked approach)
   - test_error_on_corrupt_xlsx
3. If existing extractor found:
   - Modify the size limit from 15MB to 50MB
   - Add streaming/chunked reading for large files (openpyxl read_only mode)
4. If no existing extractor:
   - Create scripts/document-intelligence/xlsx-formula-extractor.py
   - Use openpyxl in read_only mode for memory efficiency
   - Extract all formulas (cells starting with =) with sheet/cell references
   - Output: JSON with formula inventory
5. Run: `uv run pytest tests/document-intelligence/test_xlsx_extractor.py -v`

### Acceptance criteria
- XLSX extractor handles files up to 50MB
- Uses memory-efficient approach (streaming/read_only mode)
- Tests pass
- Clear documentation of the size limit change

### Commit message
feat(doc-intel): raise XLSX formula extraction limit to 50MB with streaming (#1619)

---

## TASK 3: Conference Index Plan (GH #1608)

### Context
Issue #1608: /mnt/ace/docs/conferences/ contains 38,526 files across 30 collections.
These need to be indexed into the document-index. This is too large for overnight
execution, so this task produces the PLAN, not the execution.

### What to do
1. If /mnt/ace/docs/conferences/ is accessible, survey it:
   - Count files by extension (pdf, docx, pptx, etc.)
   - List the 30 collection directories
   - Sample 3 files per collection to understand naming conventions
2. If /mnt/ace is not mounted/accessible, create the plan based on issue description
3. Write docs/document-intelligence/conference-index-plan.md:
   - Scope: 38,526 files, 30 collections
   - Approach: batch indexing with parallel workers
   - Estimated time per batch (based on existing pipeline throughput if known)
   - File type breakdown and extraction strategy per type
   - Priority ordering (which collections first)
   - Quality checks (sample validation after each batch)
   - Risks: disk space, memory for large files, OCR needs for scanned docs
4. Create a companion script outline: scripts/document-intelligence/index-conferences.sh
   - Stub script that shows the batch processing loop
   - Parameterized: collection name, batch size, output directory

### Acceptance criteria
- docs/document-intelligence/conference-index-plan.md exists with full plan
- scripts/document-intelligence/index-conferences.sh exists (can be stub/outline)
- Plan covers all 30 collections with priority ordering
- Realistic time estimates included

### Commit message
docs(doc-intel): conference collection indexing plan for 38K files (#1608)

---

## After all tasks
Post a brief progress comment on GitHub issues #1617, #1619, #1608 in repo vamseeachanta/workspace-hub:
"Overnight agent run (2026-04-01): [artifact] committed. See [path]."
