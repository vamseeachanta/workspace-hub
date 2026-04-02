# Terminal 5 — Document Intelligence: Marine Standards + Conference Indexing

Provider: **Claude/Hermes** (pipeline/tool building, high-context synthesis)
Issues: #1621, #1622, #1608, #1613

---

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare python3. Commit to main and push after each task.
Do not branch. TDD: write tests before implementation.
Do NOT ask the user any questions. Run `git pull origin main` before every push.

IMPORTANT: Do NOT write to scripts/solver/, scripts/analysis/, scripts/quality/,
scripts/docs/, docs/architecture/, docs/roadmaps/, docs/dashboards/test-health-dashboard.md,
digitalmodel/src/digitalmodel/structural/, digitalmodel/src/digitalmodel/subsea/,
digitalmodel/src/digitalmodel/asset_integrity/, digitalmodel/tests/orcaflex/,
digitalmodel/tests/solver/, digitalmodel/tests/reservoir/ — those are owned by other
terminals. Only write to: scripts/document-intelligence/, tests/document-intelligence/,
docs/document-intelligence/, data/document-index/.

---

## TASK 1: Marine Standards Batch Processor (GH issue #1621)

**Context**: The standards-transfer-ledger tracks marine standards at only 12% completion
(26 reference standards). We need a batch processing script to read each standard's
metadata and update the ledger status to "done".

The existing ledger is at `data/document-index/` and the standards are described in
the document intelligence pipeline.

**Acceptance criteria**:
1. Write tests first: `tests/document-intelligence/test_marine_standards_batch.py`
   - Test YAML ledger reading/writing
   - Test status transition logic (pending → processing → done)
   - Test batch progress tracking
   - Test dry-run mode
   - At least 8 test functions
   - Mock all file I/O — no real standards files needed
2. Create `scripts/document-intelligence/batch-process-standards.py`:
   - Reads standards-transfer-ledger YAML
   - Filters for marine domain standards with status != "done"
   - For each: validates file exists, extracts basic metadata (title, page count, file size)
   - Updates status to "done" with timestamp
   - Writes updated ledger back
   - Supports --dry-run, --domain filter, --limit N flags
   - Reports progress: "Processed 26/30 marine standards"
3. Tests pass: `uv run pytest tests/document-intelligence/test_marine_standards_batch.py -v`

**Commit message**: `feat(doc-intel): marine standards batch processor — 12% → 91% target (#1621)`

---

## TASK 2: Marine Sub-Domain Taxonomy (GH issue #1622)

**Context**: Marine domain has 32K documents that need subcategorization into 7+
categories: hydrodynamics, mooring, structural, subsea, naval architecture,
marine operations, environmental.

**Acceptance criteria**:
1. Write tests first: `tests/document-intelligence/test_marine_taxonomy.py`
   - Test keyword-based classification rules
   - Test taxonomy hierarchy structure
   - Test document-to-subdomain mapping
   - At least 6 test functions
2. Create `scripts/document-intelligence/marine-taxonomy-classifier.py`:
   - Define taxonomy: 7+ marine sub-domains with keyword lists
   - Keyword-based classifier (filename + path analysis, no LLM needed)
   - Reads document-index entries for marine domain
   - Assigns sub-domain tag to each
   - Outputs `docs/document-intelligence/marine-taxonomy-report.md`:
     - Sub-domain distribution table
     - Sample files per category
     - Unclassified files list
   - Also outputs `data/document-index/marine-subdomain-tags.yaml`
3. Tests pass: `uv run pytest tests/document-intelligence/test_marine_taxonomy.py -v`

**Commit message**: `feat(doc-intel): marine sub-domain taxonomy — 7+ categories (#1622)`

---

## TASK 3: Cross-Reference Resource Registry with Standards Transfer Ledger (GH issue #1613)

**Context**: Two separate indices exist:
- `data/document-index/online-resource-registry.yaml` (247 entries — online resources)
- `data/document-index/registry.yaml` (local document registry)
We need a cross-reference tool that finds overlaps, gaps, and complementary entries.

**Acceptance criteria**:
1. Write tests first: `tests/document-intelligence/test_cross_reference.py`
   - Test matching algorithm (title similarity, URL matching)
   - Test gap detection logic
   - Test report generation
   - At least 6 test functions
2. Create `scripts/document-intelligence/cross-reference-registries.py`:
   - Load both registries
   - Find matches by title fuzzy matching (use difflib.SequenceMatcher, no external deps)
   - Identify: matched pairs, online-only entries, local-only entries
   - Generate `docs/document-intelligence/registry-cross-reference-report.md`:
     - Match count and match rate
     - Top 20 online resources without local copies (download candidates)
     - Top 20 local docs without online references (upload/publish candidates)
     - Domain-level coverage comparison
3. Tests pass: `uv run pytest tests/document-intelligence/test_cross_reference.py -v`

**Commit message**: `feat(doc-intel): cross-reference online + local registries (#1613)`

---

Post a brief progress comment on GH issues #1621, #1622, #1613 when complete.
