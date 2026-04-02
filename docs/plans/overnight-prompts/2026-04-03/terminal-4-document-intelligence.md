# Terminal 4 — Document Intelligence Pipeline (Gemini)

We are in /mnt/local-analysis/workspace-hub. Execute these 4 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to `main` and push after each task. Do not branch.
TDD: write tests before implementation; mock file system access and external tools.
Run `git pull origin main` before every push.
Do NOT ask the user any questions. Make reasonable decisions autonomously.

IMPORTANT: Do NOT write to any of the following paths — they are owned by other terminals:
- digitalmodel/src/digitalmodel/orcawave/, digitalmodel/tests/orcawave/ (Terminal 1)
- digitalmodel/tests/parametric_hull/, digitalmodel/tests/orcaflex/, digitalmodel/tests/hydrodynamics/ (Terminal 2)
- digitalmodel/tests/web/, digitalmodel/tests/field_development/, digitalmodel/tests/geotechnical/, digitalmodel/tests/nde/, digitalmodel/tests/reservoir/ (Terminal 3)
- digitalmodel/src/digitalmodel/{web,reservoir,infrastructure,marine_ops,solvers,hydrodynamics,specialized,signal_processing}/ (Terminal 5 docstrings)
- config/cron/, scripts/cron/ (Terminal 5)

Only write to:
- scripts/document-intelligence/ (new files only — do not modify existing batch-process-standards.py, marine-taxonomy-classifier.py, cross-reference-registries.py)
- tests/document-intelligence/
- docs/document-intelligence/
- data/document-index/ (only new index files, not existing registries)

---

## TASK 1: Execute Conference Indexing Phase 1 (GH issue #1641)

### Context
- 38,526 conference files across 30 collections in `/mnt/ace/docs/conferences/`
- Phase 1 targets high-priority SMALL collections (1,032 files)
- The indexing plan is at `docs/document-intelligence/conference-indexing-plan.md`
- Existing indexing script: `scripts/document-intelligence/index-conferences.sh`

### Steps
1. Read `docs/document-intelligence/conference-indexing-plan.md` to understand Phase 1 collections
2. Read `scripts/document-intelligence/index-conferences.sh` to understand the indexing approach
3. Write tests first: `tests/document-intelligence/test_conference_indexer.py`
   - Test: indexer produces valid YAML output with required fields (title, path, collection, file_type)
   - Test: handles missing/unreadable files gracefully
   - Test: deduplication by file hash
   - Test: collection-level summary statistics
4. Build/extend: `scripts/document-intelligence/conference-indexer.py`
   - Python indexer that scans conference directories
   - Extracts metadata: filename, extension, size, collection name, date if parseable
   - Outputs YAML index at `data/document-index/conference-index-phase1.yaml`
   - Include collection summary (file count, size, types)
5. If `/mnt/ace/docs/conferences/` is accessible, run Phase 1 on the small collections
   - If NOT accessible, generate the indexer and test with mock data, document the run command
6. Run tests: `uv run pytest tests/document-intelligence/test_conference_indexer.py -v`

### Commit message
```
feat(doc-intel): conference indexer Phase 1 — 1,032 files across small collections (#1641)
```

---

## TASK 2: Expand ASTM Standards-Transfer-Ledger Coverage (GH issue #1612)

### Context
- Current standards-transfer-ledger covers 0.4% of 25,537 ASTM files
- Files are at `/mnt/ace/docs/standards/` (or similar path)
- Existing ledger is at `data/document-index/standards-transfer-ledger.yaml` (or similar)

### Steps
1. Find the existing standards transfer ledger: search for `standards-transfer-ledger` in data/
2. Read it to understand the schema (fields per entry)
3. Write tests: `tests/document-intelligence/test_standards_ledger_expansion.py`
   - Test: new scanner finds files not in existing ledger
   - Test: output follows existing ledger schema exactly
   - Test: handles nested directory structures
   - Test: generates domain classification from filename patterns (ASTM E*, ASTM A*, etc.)
4. Build: `scripts/document-intelligence/expand-standards-ledger.py`
   - Scan standards directories for files not yet in ledger
   - Classify by ASTM designation pattern (A=ferrous metals, B=nonferrous, C=concrete, D=petroleum, E=misc, F=materials, G=corrosion)
   - Output incremental ledger entries (append-safe YAML)
   - Report: total files scanned, new entries found, coverage %
5. If `/mnt/ace/docs/standards/` is accessible, run a scan
6. Write results report: `docs/document-intelligence/standards-ledger-expansion-report.md`

### Commit message
```
feat(doc-intel): ASTM standards-ledger expansion — scanner + domain classification (#1612)
```

---

## TASK 3: Install tesseract-ocr and Validate OCR Parser (GH issue #1640)

### Context
- 474K documents are unextractable because they're scanned PDFs
- tesseract-ocr is needed for OCR text extraction
- An OCR parser stub exists at `scripts/document-intelligence/ocr-parser.py`

### Steps
1. Check if tesseract is already installed: `which tesseract` and `tesseract --version`
2. If not installed: `sudo apt-get install -y tesseract-ocr tesseract-ocr-eng`
   - If sudo is not available, document the install command and proceed with mock tests
3. Check if pytesseract is available: `uv run python -c "import pytesseract"`
   - If not: add pytesseract to dependencies or install it
4. Read existing `scripts/document-intelligence/ocr-parser.py`
5. Write tests: `tests/document-intelligence/test_ocr_parser.py`
   - Test: OCR parser initializes correctly
   - Test: handles a test image with known text (create a simple test fixture)
   - Test: handles non-image files gracefully
   - Test: output format matches doc-intelligence pipeline schema
   - Use `pytest.importorskip("pytesseract")` for graceful skipping
6. Validate OCR on a real scanned PDF if one exists at /mnt/ace/
7. Run tests: `uv run pytest tests/document-intelligence/test_ocr_parser.py -v`

### Commit message
```
feat(doc-intel): install tesseract-ocr + validate OCR parser on real scans (#1640)
```

---

## TASK 4: Register OCR Parser in Parser Registry (GH issue #1643)

### Context
- Doc-intelligence has a parser registry that routes files to the right parser
- OCR parser needs to be registered for scanned PDF handling

### Steps
1. Find the parser registry: search for `parser` or `registry` in scripts/document-intelligence/
2. Read the registry to understand how parsers are registered
3. Write tests: `tests/document-intelligence/test_ocr_registry.py`
   - Test: OCR parser is registered for MIME types image/tiff, image/png, application/pdf (scanned)
   - Test: registry routes a scanned PDF to OCR parser
   - Test: registry still routes normal PDFs to text extractor
4. Implement the registration in the parser registry
5. Run tests: `uv run pytest tests/document-intelligence/test_ocr_registry.py -v`

### Commit message
```
feat(doc-intel): register OCR parser in doc-intelligence registry (#1643)
```

---

Post a brief progress comment on GH issues #1641, #1612, #1640, #1643 when each task completes.
