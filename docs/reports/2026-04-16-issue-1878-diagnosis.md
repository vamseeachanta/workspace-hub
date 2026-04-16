# Issue #1878 Diagnosis: Document Index Metadata Broken

**Date:** 2026-04-16
**Investigator:** Claude agent (automated diagnosis)
**Status:** Root cause identified, fix plan proposed

---

## 1. Root Cause Analysis

### The Issue Description Is Partially Misleading

The issue states "647K records showing `content_type: unknown` and `summary_done: false`."
In reality, **neither `content_type` nor `summary_done` fields exist in any of the 649,564 records**.
These fields were never part of the `index.jsonl` schema. The GOTCHA warnings in
`engineering-issue-workflow/SKILL.md` reference these fields, but they describe a
**conceptual gap** rather than a field-value regression.

### What Actually Happened

1. **Phase A** (`phase-a-index.py`) generates `index.jsonl` with structural metadata only:
   `path, host, source, ext, size_mb, mtime, content_hash, is_cad, domain, summary, org,
   doc_number, provenance, readability, path_category, path_subcategory, status, target_repos`.

2. **Phase B** (`phase-b-extract.py`, `summarise-worker.py`) generates summary files in
   `data/document-index/summaries/<hash>.json` on the ace drive, **separate from index.jsonl**.
   These contain: `title, discipline, summary, keywords, extraction_method, org, source`.

3. **Phase C** (`phase-c-classify.py`) reads index + summaries to classify domains, but writes
   results back **only to `enhancement-plan.yaml`** in default mode. The bounded writeback mode
   updates `domain/status/target_repos` in index.jsonl but adds no `content_type` or
   `summary_done` fields.

4. **No pipeline step ever merges summary metadata back into index.jsonl.** The summary data
   lives in 717,141 separate JSON files on the ace drive at
   `/mnt/ace/data/document-index/summaries/`, not in the index itself.

5. The `summary` field in index.jsonl is always `null` for every record. It was initialized
   as `null` by Phase A and never updated.

### Why the GOTCHA Warnings Exist

Agents searching `index.jsonl` for metadata (title, discipline, content type) find nothing
useful because the index only has file-system metadata. The actual intelligence is in the
717K summary files on the ace drive, which are not consulted by agents doing standard
index.jsonl queries.

---

## 2. Where the Metadata Actually Lives

| Data | Location | Records | Coverage |
|------|----------|---------|----------|
| File metadata (path, ext, size, hash) | `index.jsonl` | 649,564 | 100% |
| Readability classification | `index.jsonl` (readability field) | 627,154 of 649,564 | 96.5% |
| Domain classification | `index.jsonl` (domain field) | 627,154 of 649,564 | 96.5% |
| LLM summaries (title, discipline, keywords) | `/mnt/ace/data/document-index/summaries/` | 717,141 files | See below |
| Standards ledger (curated metadata) | `standards-transfer-ledger.yaml` | 425 standards | 61.9% done |
| Online resources (curated) | `online-resource-registry.yaml` | 247 entries | Current |

### Summary File Matching Rates

| Index Segment | Records | Matching Summaries | Rate |
|---------------|---------|-------------------|------|
| Records with `content_hash` (sha256-prefixed summaries) | 169,815 | 78,268 | 46.1% |
| Records without `content_hash` (path-derived short-hash summaries) | 479,749 | 465,726 | 97.1% |
| **Total recoverable** | **649,564** | **543,994** | **83.7%** |

### Unrecoverable Records (105,570 = 16.3%)

- ~91,547: Records with `content_hash` but no matching summary file (mostly ace_standards
  with 44% coverage, ace_conferences)
- ~14,023: `riser_eng_job` .dat files (binary OrcaFlex data, not summarizable)

### Summary File Quality

- **sha256-prefixed summaries** (78K files, from og_standards/ace_standards): High quality.
  100% have discipline, summary, keywords. ~78% have non-empty summary text.
- **Short-hash summaries** (639K files, from ace_project/dde_project): Low quality.
  ~75% are `extraction_method: skipped` (CAD files). Only ~2.5% have non-empty summary.
  Most have title and word_count but no discipline or org.

---

## 3. Proposed Fix Approach

### Phase 1: Add `summary_available` and `content_type` Fields to index.jsonl (Estimated: 2-3 hours)

Write a new enrichment script `scripts/data/document-index/enrich-summary-metadata.py` that:

1. Reads `index.jsonl` (649K records)
2. For each record, looks up the matching summary file on the ace drive:
   - If `content_hash` exists: check `summaries/{content_hash}.json`
   - If no `content_hash`: check `summaries/{sha256(path)[:16]}.json`
3. Extracts and merges these fields into the index record:
   - `summary_done: true/false` (summary file exists AND has non-empty summary text)
   - `content_type`: derived from `ext` field using a simple mapping:
     - pdf/doc/docx -> "document"
     - xls/xlsx/csv -> "spreadsheet"
     - pptx -> "presentation"
     - dwg/dxf -> "cad"
     - dat/inp/mac -> "simulation-input"
     - py/m/f/for/bas -> "script"
     - md/txt/yaml/yml -> "text"
     - htm/html -> "web"
   - `summary_title`: from summary file `title` field (if available)
   - `summary_discipline`: from summary file `discipline` field (if available)
4. Writes enriched index.jsonl (with backup)

This is a **read-only operation on summaries** and a single-pass enrichment of the index.

### Phase 2: Fix Phase A to Preserve Metadata on Re-index (Estimated: 1 hour)

Modify `phase-a-index.py` to:

1. When `--force` is used, still load existing index metadata into a side dict
2. After scanning new records, carry forward `summary_done`, `content_type`,
   `summary_title`, `summary_discipline` from the prior index for matching paths
3. Add a `--preserve-metadata` flag (default: true) with explicit `--no-preserve-metadata`
   to opt out

### Phase 3: Add Validation Guard (Estimated: 30 minutes)

Write `scripts/data/document-index/validate-index-metadata.py` that:

1. Rejects index files where `content_type` is missing for >10% of records
2. Rejects index files where `summary_done` is populated for <50% of records
   (when summaries are known to exist)
3. Add to pre-commit or CI as a check before any index.jsonl commit/deployment

### Phase 4: Update GOTCHA Warnings (Estimated: 15 minutes)

Once the enrichment is complete, update:
- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` (line 80)
- `.claude/skills/coordination/workflow-compliance-audit/SKILL.md` (line 60)
- `docs/standards/engineering-issue-workflow-skill.md` (line 85)

Remove the BROKEN warnings and replace with guidance on using the enriched fields.

---

## 4. Expected Outcomes

| Metric | Before Fix | After Fix |
|--------|-----------|-----------|
| `content_type` populated | 0% (field absent) | 100% (derived from ext) |
| `summary_done` populated | 0% (field absent) | 100% (83.7% true, 16.3% false) |
| `summary_title` populated | 0% | ~83.7% |
| `summary_discipline` populated | 0% | ~12% (sha256 summaries only have it) |
| Agent index queries useful | No | Yes |

---

## 5. Estimated Total Effort

| Phase | Effort | Dependency |
|-------|--------|------------|
| Phase 1: Enrichment script | 2-3 hours | Ace drive accessible |
| Phase 2: Re-index metadata preservation | 1 hour | Phase 1 complete |
| Phase 3: Validation guard | 30 min | Phase 1 complete |
| Phase 4: Update warnings | 15 min | Phase 1 verified |
| **Total** | **4-5 hours** | |

---

## 6. Key Risk

The ace drive (`/mnt/ace/data/document-index/summaries/`) must be mounted and accessible
when running the enrichment. Current check confirms it IS accessible (717,141 files present).
If the drive becomes unavailable, the enrichment cannot proceed.

## 7. Notes on the Maturity YAML Discrepancy

`resource-intelligence-maturity.yaml` claims:
- `total_index_records: 1,033,933` and `total_index_summaries: 639,585` (61.9%)

The current index has 649,564 records. The 1M figure likely refers to the combined
count across `index.jsonl` (649K) + `conference-index-batch.jsonl` (the conference
pipeline's separate index). The 639K summaries figure aligns with the 638K short-hash
summary files + some sha256 ones. These numbers are consistent but refer to a
different measurement scope than the current index alone.
