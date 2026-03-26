# Schema Comparison Report: index.db vs _inventory.db

Generated: 2026-03-25

## Database Overview

| Property | index.db (Knowledge) | _inventory.db (Inventory) |
|---|---|---|
| Path | `/mnt/ace/.ace-knowledge/index.db` | `/mnt/ace/O&G-Standards/_inventory.db` |
| Size | 1.2 GB | 6.4 GB |
| Primary table | `assets` (1,188,891 rows) | `documents` (27,980 rows) |
| Focus | Broad asset catalog (all file types) | O&G standards with extracted text + embeddings |

## Schema Comparison

### Overlapping Columns (assets vs documents)

These columns exist in both primary tables and serve the same purpose:

| Knowledge (`assets`) | Inventory (`documents`) | Notes |
|---|---|---|
| `file_path` (TEXT UNIQUE) | `file_path` (TEXT UNIQUE) | **Primary join key** -- 27,343 rows overlap |
| `file_name` | `filename` | Same data, different column name |
| `file_extension` | `extension` | Same data |
| `file_size` (INTEGER) | `file_size` (INTEGER) | Same data |
| `content_hash` (TEXT) | `content_hash` (TEXT) | Knowledge: 27,343 populated; Inventory: 27,980 populated |
| `modified_date` (TEXT) | `modified_date` (TEXT) | Same data |
| `title` (TEXT) | `title` (TEXT) | Same data |
| `scan_date` (TEXT) | `scan_date` (TEXT) | Same data |

### Standards-related columns (both databases)

| Knowledge (`assets` + `standards`) | Inventory (`documents`) |
|---|---|
| `standards.organization` | `documents.organization` |
| `standards.doc_type` | `documents.doc_type` |
| `standards.doc_number` | `documents.doc_number` |

Knowledge stores these in a separate `standards` table (27,335 rows) joined via `asset_id`.
Inventory stores them inline on the `documents` table.

### Columns unique to Knowledge DB

On `assets`:
- `id` (TEXT UUID primary key)
- `asset_type` -- document/spreadsheet/simulation/data/code
- `source_root` -- root directory grouping
- `discipline`, `project_code`, `folder_phase` -- project taxonomy
- `description`, `content_category`, `engineering_domain` -- classification metadata
- `extraction_status`, `anonymized_title`, `language`, `page_count`, `word_count`, `last_extracted`

On `standards`:
- `edition`, `year`, `superseded_by`

### Columns unique to Inventory DB

On `documents`:
- `id` (INTEGER AUTOINCREMENT primary key)
- `source_dir` -- immediate parent directory
- `is_duplicate`, `duplicate_of` -- deduplication tracking
- `target_path` -- normalized target path
- `processed` -- processing flag

### Tables unique to Knowledge DB

| Table | Rows | Purpose |
|---|---|---|
| `asset_tags` | 0 | Tag/category system for assets |
| `standards` | 27,335 | Standards metadata (org, doc_number, edition, year) |
| `formulas` | 0 | Engineering formulas with variables |
| `code_patterns` | 2,779 | Code templates by language/domain |
| `cross_references` | 0 | Asset-to-asset relationships |
| `methodologies` | 0 | Step-by-step engineering methodologies |
| `reference_data` | 0 | Lookup data (materials, constants) |
| `assets_fts` | FTS5 | Full-text search on title, description, anonymized_title |

### Tables unique to Inventory DB

| Table | Rows | Purpose |
|---|---|---|
| `document_text` | 26,982 | Extracted full text (pymupdf: 26,674; no_text: 273; error: 35) |
| `text_chunks` | 1,043,616 | Chunked text with `all-MiniLM-L6-v2` embeddings (avg 199 words/chunk) |
| `scan_history` | 1 | Scan run metadata |
| `documents_fts` | FTS5 | Full-text search on filename, title, organization, doc_type, doc_number |

## Overlap Analysis

| Metric | Count |
|---|---|
| Records sharing `file_path` | 27,343 |
| Knowledge-only records | 1,161,548 |
| Inventory-only records | 637 |
| Overlapping files with extracted text | 26,674 |
| Overlapping files with embeddings | 978,819 (chunks, not files) |

### Key finding

The inventory DB is essentially a **subset** of the knowledge DB's standards documents (27,343 of 27,980 inventory docs appear in knowledge). The inventory adds substantial value through:
1. **Extracted full text** (26,674 documents via pymupdf)
2. **Semantic embeddings** (1,043,616 chunks with all-MiniLM-L6-v2 vectors)

The knowledge DB contributes broader asset coverage (1.16M additional records) plus richer classification metadata (engineering_domain, discipline, project_code, asset_type).

## Query Interface

See `cross_db_query.py` in the same directory. Commands:

```
python3 tools/cross_db_query.py search "API 650"           # FTS across both
python3 tools/cross_db_query.py search "riser" --db inventory  # single DB
python3 tools/cross_db_query.py joined "pipeline design"    # enriched cross-DB
python3 tools/cross_db_query.py overlap                     # overlap analysis
python3 tools/cross_db_query.py overlap --by-hash           # by content hash
python3 tools/cross_db_query.py stats                       # summary statistics
python3 tools/cross_db_query.py sql "SELECT ..."            # arbitrary SQL
```

The SQL interface ATTACHes inventory as `inv`, so use `inv.documents`, `inv.document_text`, `inv.text_chunks` for inventory tables, and unqualified names for knowledge tables.
