# Terminal 3: #1862 + #1863 — Conference Paper Indexing + DDE Literature Migration
# Agent: Gemini (data pipeline work, batch I/O)
# Estimated: 6-8 hours total
# Repo: workspace-hub (commit to main, push)
# Both tasks write to workspace-hub data/ — no overlap with digitalmodel

We are in /mnt/local-analysis/workspace-hub.
Execute these tasks in order. Use `uv run` for all Python. Do NOT ask the user any questions.
Commit to main and push after each logical unit.
Run `git pull origin main` before every push to avoid conflicts with Terminal 1.

## PART A: Conference Paper Indexing (#1862)

### Context

- conference-paper-catalog.yaml has 30 conferences, 38,526 total files, 21,996 PDFs
- conference-index-batch.jsonl has 21,346 lines (partial — only file listing, no extraction)
- All 30 conferences show indexing_status: not_indexed
- Source: /mnt/ace/docs/conferences/
- prep-conference-index.py exists at scripts/data/document-index/prep-conference-index.py
- Priority conferences: OTC, OMAE, DOT, ISOPE, SPE (the big 5 venues)

### TASK A1: Rebuild conference-index-batch.jsonl with full coverage

The existing JSONL has 21,346 entries but the catalog says 38,526 files.
Run the prep script to regenerate with full coverage:

```bash
cd /mnt/local-analysis/workspace-hub
uv run python scripts/data/document-index/prep-conference-index.py --output data/document-index/conference-index-batch.jsonl
```

If the script fails, read it and fix. The goal is a complete JSONL with one entry per
indexable file (.pdf, .doc, .docx) across all 30 conferences.

Verify: `wc -l data/document-index/conference-index-batch.jsonl` should be > 21,346

Commit: "data(conference): rebuild full conference-index-batch.jsonl (#1862)"

### TASK A2: Create conference summary statistics

Write a Python script at scripts/data/document-index/conference-stats.py that:
1. Reads conference-index-batch.jsonl
2. Produces per-conference stats: file count, PDF count, size estimate
3. Outputs to data/document-index/conference-index-stats.yaml
4. Includes: total_indexed, per_conference breakdown, priority ranking

Run it and commit the output:
Commit: "data(conference): add conference index statistics (#1862)"

### TASK A3: Phase A batch — extract titles and metadata from PDFs

For the top-priority conferences (OTC, OMAE, DOT first), write a batch script at
scripts/data/document-index/batch-conference-phase-a.py that:

1. Reads conference-index-batch.jsonl filtered to PDF files only
2. For each PDF, extracts:
   - Title (from first page text or filename parsing)
   - Year (from directory path or filename)
   - Conference name (from JSONL entry)
   - Page count
   - File size
3. Writes results to data/document-index/conference-phase-a-results.jsonl
4. Processes in batches of 100, with checkpoint saves
5. Uses only standard library + PyPDF2/pypdf (no AI API calls)
6. Handles corrupt/unreadable PDFs gracefully (log and skip)

NOTE: This is text extraction only — no LLM summarization. Speed target: ~1000 PDFs/hour.
Start with OTC (highest priority, ~5000 PDFs), then OMAE, then DOT.

Run it: `uv run python scripts/data/document-index/batch-conference-phase-a.py --conferences OTC OMAE DOT`

Commit progress periodically (every 1000 PDFs processed):
"data(conference): Phase A metadata extraction — N/M PDFs (#1862)"

### TASK A4: Update conference-paper-catalog.yaml

After Phase A completes (or as far as it gets), update the catalog:
- Change indexing_status from not_indexed to phase_a_complete for processed conferences
- Add indexed_count and phase_a_date fields

Commit: "data(conference): update catalog indexing status (#1862)"

### TASK A5: Post progress comment

```bash
gh issue comment 1862 --repo vamseeachanta/workspace-hub --body "Overnight Phase A indexing:
- Rebuilt conference-index-batch.jsonl: N entries (was 21,346)
- Phase A metadata extracted: N PDFs across M conferences
- Priority conferences processed: OTC, OMAE, DOT
- Results: data/document-index/conference-phase-a-results.jsonl
- Next: ISOPE, SPE, remaining conferences"
```

---

## PART B: DDE Literature Migration (#1863)

### Context

- DDE remote mounted at /mnt/remote/ace-linux-2/dde/Literature/
- Two main dirs: Engineering (8,640 MB, 823 PDFs) and Oil and Gas (5,980 MB, 4,633 PDFs)
- Total: 14,620 MB, 5,456 PDFs
- Local target: /mnt/ace/ has 2.3 TB free
- dde-literature-catalog.yaml exists with 87 items cataloged
- Migration target: /mnt/ace/docs/literature/dde/ (create if needed)

### TASK B1: Create migration target and verify connectivity

```bash
mkdir -p /mnt/ace/docs/literature/dde/Engineering
mkdir -p "/mnt/ace/docs/literature/dde/Oil-and-Gas"
# Test: can we read from remote?
ls "/mnt/remote/ace-linux-2/dde/Literature/Engineering/" | head -5
# Test: can we write to local?
touch /mnt/ace/docs/literature/dde/.migration-test && rm /mnt/ace/docs/literature/dde/.migration-test
```

### TASK B2: Priority migration — reservoir engineering textbooks

Copy the highest-value items first from the DDE catalog and directory listing.
Use rsync for resumability. Adapt filenames based on what you find:

```bash
mkdir -p /mnt/ace/docs/literature/dde/reservoir-engineering
rsync -av --progress \
  "/mnt/remote/ace-linux-2/dde/Literature/Engineering/Fundamentals of reservoir engineering.pdf" \
  /mnt/ace/docs/literature/dde/reservoir-engineering/
```

Look for reservoir engineering, petroleum engineering, and field development textbooks
in both Engineering and Oil and Gas directories.

### TASK B3: Bulk migration — Engineering directory

```bash
rsync -av --progress \
  "/mnt/remote/ace-linux-2/dde/Literature/Engineering/" \
  /mnt/ace/docs/literature/dde/Engineering/
```

This is ~8.6 GB over the network. Let it run.

### TASK B4: Bulk migration — Oil and Gas directory

```bash
rsync -av --progress \
  "/mnt/remote/ace-linux-2/dde/Literature/Oil and Gas/" \
  "/mnt/ace/docs/literature/dde/Oil-and-Gas/"
```

This is ~6.0 GB. Let it run after Engineering completes.

### TASK B5: Generate migration report

After rsync completes, write a script at scripts/data/document-index/dde-migration-report.py:
1. Walk /mnt/ace/docs/literature/dde/ and count files by type
2. Compare against dde-literature-catalog.yaml source counts
3. Output: data/document-index/dde-migration-report.yaml with:
   - files_migrated, bytes_migrated, by_type breakdown
   - comparison vs source (any missing files)
   - migration_date timestamp

Run it. Commit: "data(dde): migration report — N files, M GB migrated (#1863)"

### TASK B6: Update mounted-source-registry.yaml

Add a new entry for the migrated DDE literature:
```yaml
- source_id: dde_literature_local
  document_intelligence_bucket: dde_literature
  mount_root: /mnt/ace/docs/literature/dde
  local_or_remote: local
  canonical_storage_policy: migrated from DDE remote drive
  provenance_rule: local copy of /mnt/remote/ace-linux-2/dde/Literature
  dedup_rule: prefer local copy, DDE remote is archival
  migration_date: "2026-04-05"
```

Commit: "data(registry): add DDE literature local source (#1863)"

### TASK B7: Post progress comment

```bash
gh issue comment 1863 --repo vamseeachanta/workspace-hub --body "Overnight DDE migration:
- Engineering: X files, Y GB migrated to /mnt/ace/docs/literature/dde/Engineering/
- Oil and Gas: X files, Y GB migrated to /mnt/ace/docs/literature/dde/Oil-and-Gas/
- Migration report: data/document-index/dde-migration-report.yaml
- Source registry updated
- Next: run doc-intelligence Phase A on new arrivals"
```

## IMPORTANT BOUNDARIES

Do NOT write to:
- digitalmodel/ (any directory — owned by Terminals 1 and 2)
- data/document-index/standards-transfer-ledger.yaml (owned by Terminal 1)

Only write to:
- data/document-index/conference-* files
- data/document-index/dde-* files
- data/document-index/mounted-source-registry.yaml (append only)
- scripts/data/document-index/ (new scripts)
- /mnt/ace/docs/literature/dde/ (migration target)
