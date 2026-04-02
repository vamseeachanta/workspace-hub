# Knowledge Persistence Architecture — Issue #894

> Created: 2026-04-01
> Tracking issue: #894
> Feature group: Group 7 — Knowledge Persistence & Workflow Integration (P2)
> Parent plan: [data-intelligence-feature-plan.md](2026-04-01-data-intelligence-feature-plan.md)

## Problem Statement

Work-done summaries currently live in two disconnected places:

1. **MEMORY.md** — a terse 18-line pointer file at the repo root, constrained to ≤20 lines
   by repo policy. It cannot hold any substantive work history.
2. **`~/.claude/projects/.../memory/`** — ephemeral Claude session memory files that are
   gitignored, machine-local, and lost when context windows rotate.

Completed WRK items were historically recorded as free-text bullet points inside session
memory, then evicted by `scripts/memory/compact-memory.py` once marked done. A one-time
migration extracted 420 of these into `knowledge-base/wrk-completions.jsonl` (source:
`memory-migration`), but the records are raw markdown strings — not structured, not
queryable by field, and disconnected from the resource-intelligence maturity tracker.

The result: **zero institutional memory** of what was built, what was learned, and what
documents were read — unless you grep a 332KB JSONL file of opaque strings.

## Current State

### Knowledge Stores (5 distinct systems, poorly connected)

| Store | Format | Location | Records | Queryable? | Structured? |
|-------|--------|----------|---------|-----------|-------------|
| WRK completions | JSONL (raw markdown) | `knowledge-base/wrk-completions.jsonl` | 420 | keyword grep only | ❌ raw `"raw"` field |
| Career learnings | YAML (entries[]) | `knowledge/seeds/career-learnings.yaml` | 11 | category + keyword | ✅ id, category, subcategory, patterns, follow_ons |
| Maritime law cases | YAML (entries[]) | `knowledge/seeds/maritime-law-cases.yaml` | 10 | category + keyword | ✅ same schema |
| Maritime liabilities | YAML (entries[]) | `knowledge/seeds/maritime-liabilities.yaml` | 6 | category + keyword | ✅ same schema |
| Mooring failures | YAML (entries[]) | `knowledge/seeds/mooring-failures-lng-terminals.yaml` | ~25 | category + keyword | ✅ same schema |
| Naval arch resources | YAML (resource catalog) | `knowledge/seeds/naval-architecture-resources.yaml` | ~45 items | manual browse | ✅ different schema (schema.md) |
| Dark intelligence | YAML (gitignored) | `knowledge/dark-intelligence/**/*.yaml` | many | ❌ | ✅ extraction-specific |
| Resource intelligence | YAML (maturity tracker) | `data/document-index/resource-intelligence-maturity.yaml` | 5 docs tracked | ❌ | ✅ but only tracking, no content |
| Merged index | JSONL | `knowledge-base/index.jsonl` | ~47 | mtime-gated | ✅ (rebuilt from wrk + seeds) |
| MEMORY.md | Markdown | `MEMORY.md` | N/A (pointers only) | ❌ | ❌ |

### Query Infrastructure

- `scripts/knowledge/query-knowledge.sh` — single query script that:
  - Reads `knowledge-base/index.jsonl` (if fresh) or rebuilds from JSONL + career YAML
  - Only indexes `wrk-completions.jsonl` + `career-learnings.yaml`
  - Does NOT index maritime-law-cases, maritime-liabilities, mooring-failures, naval-architecture-resources
  - Keyword scoring is naive `text.count(query)` — no stemming, no fuzzy
  - Output is markdown to stdout

### Resource Intelligence Maturity

- Tracker at `data/document-index/resource-intelligence-maturity.yaml` (schema v1.0.0)
- Tracks 5 documents in scope, 0 read (0%)
- Target: 80% read within 3 months of 2026-03-01
- No connection to work-done records — completing a WRK that reads a document does not
  update the maturity tracker
- Markdown summary at `resource-intelligence-maturity.md` is generated from YAML (YAML is
  authoritative)

### Seed Schema (from `knowledge/seeds/schema.md`)

Two distinct schemas exist:

**1. Entries schema** (career-learnings, maritime-law, mooring-failures):
```yaml
entries:
  - id: PREFIX-category-slug
    type: career
    category: <domain>
    subcategory: <subdomain>
    title: "..."
    learned_at: "ISO8601"
    source: <filename>
    context: >
      Multi-line description
    patterns:
      - "Pattern 1"
      - "Pattern 2"
    follow_ons:
      - type: reference|training|person
        title: "..."
        url: "..."
        added_at: "YYYY-MM-DD"
        note: "..."
```

**2. Resource catalog schema** (naval-architecture-resources):
```yaml
category: <domain-slug>
subcategory: references
created_at: "YYYY-MM-DD"
textbooks:
  - title: "..."
    author: "..."
    year: YYYY
    local_path: "..."
    source_url: "..."
    size_mb: N
    topics: [...]
    notes: "..."
online_portals:
  - title: "..."
    url: "..."
    notes: "..."
pending_manual:
  - title: "..."
    url: "..."
    notes: "..."
```

---

## Proposed Target State

### Design Principles

1. **YAML is authoritative** — matches existing convention (resource-intelligence-maturity.yaml note: "YAML is the source of truth")
2. **JSONL is the query cache** — rebuilt from YAML sources, never edited directly
3. **One schema for work-done** — extend the entries[] schema with a `type: wrk` variant
4. **Bidirectional links** — WRK completions link to resource-intelligence documents they read; maturity tracker auto-updates
5. **No MEMORY.md content** — MEMORY.md remains a pointer file (≤20 lines); all substance lives in structured stores
6. **Append-only seeds, rebuilt index** — knowledge/seeds/ files are append-only; index.jsonl is rebuilt on demand

### Proposed Schema: `knowledge/seeds/wrk-completions.yaml`

Migrate the 420 raw JSONL records into a structured YAML file using the entries[] schema:

```yaml
---
# wrk-completions.yaml — Structured archive of completed work items
# Queried by: bash scripts/knowledge/query-knowledge.sh --category wrk
# Migrated from: knowledge-base/wrk-completions.jsonl (420 records, memory-migration source)
entries:

  - id: WRK-637
    type: wrk
    category: infrastructure
    subcategory: memory-management
    title: "Memory compaction — 5-rule eviction with atomic writes"
    completed_at: "2026-03-10T00:00:00Z"
    commit: a9057331
    source: wrk-completions.yaml
    context: >
      scripts/memory/compact-memory.py — 5-rule eviction pipeline:
      done-WRK → stale-path(--check-paths) → stale-cmd(--check-commands)
      → dedup 90% → trim. Atomic writes. scripts/memory/curate-memory.py
      (read-only classifier → memory-promotion-candidates.md).
    artifacts:
      - scripts/memory/compact-memory.py
      - scripts/memory/curate-memory.py
    tests: 21
    patterns:
      - "5-rule eviction: done-WRK → stale-path → stale-cmd → dedup → trim"
      - "# keep comment exempts entries from trim/dedup only"
    documents_read: []
    follow_ons: []
```

### Extended Fields (type: wrk additions to entries schema)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | `"wrk"` (vs `"career"` for learnings) |
| `completed_at` | ISO8601 | ✅ | When the WRK was archived (replaces `learned_at`) |
| `commit` | string | ❌ | Git commit hash of completion |
| `artifacts` | string[] | ❌ | Files created/modified by this WRK |
| `tests` | integer | ❌ | Number of TDD tests written |
| `documents_read` | string[] | ❌ | Paths or IDs of documents read (links to resource-intelligence) |
| `gh_issue` | integer | ❌ | GitHub issue number if applicable |

The existing fields (`id`, `category`, `subcategory`, `title`, `source`, `context`,
`patterns`, `follow_ons`) remain identical to the entries schema.

### Resource Intelligence Maturity Integration

Add a `documents[]` array to the maturity tracker that links to WRK IDs:

```yaml
# data/document-index/resource-intelligence-maturity.yaml (proposed v2.0.0)
generated: "2026-04-01T00:00:00Z"
version: "2.0.0"
schema_version: "2.0.0"
target_window: "3 months"
target_start: "2026-03-01"
metric:
  documents_read_threshold_percent: 80
  key_calculations_implemented_required: true
  measurement_owner: orchestrator
  measurement_process: >
    Auto-updated by scripts/knowledge/update-maturity.sh when WRK completions
    reference documents_read entries matching documents[].id
tracking:
  canonical_markdown_ref: data/document-index/resource-intelligence-maturity.md
  wrk_completions_ref: knowledge/seeds/wrk-completions.yaml
documents:
  - id: DOC-001
    title: "Document title"
    path: "/mnt/ace/docs/..."
    status: unread          # unread | in-progress | read
    read_by_wrk: ~          # WRK ID that marked it read (null if unread)
    read_at: ~              # ISO8601 when marked read
  # ... repeat for all tracked documents
status:
  documents_in_scope: 5
  documents_marked_read: 0       # auto-calculated from documents[].status
  documents_marked_read_percent: 0
  key_calculations_implemented: []
  followup_wrks: []
notes:
  - "YAML is the source of truth."
  - "Markdown summary must link here and must not diverge."
  - "documents[].read_by_wrk links to knowledge/seeds/wrk-completions.yaml entries."
```

### Updated Index Builder

Extend `scripts/knowledge/query-knowledge.sh` (or create `scripts/knowledge/rebuild-index.sh`):

```
Sources indexed:
  knowledge/seeds/career-learnings.yaml        (entries[], type=career)
  knowledge/seeds/maritime-law-cases.yaml      (entries[], type=career)
  knowledge/seeds/maritime-liabilities.yaml    (entries[], type=career)
  knowledge/seeds/mooring-failures-lng-terminals.yaml (entries[], type=career)
  knowledge/seeds/wrk-completions.yaml         (entries[], type=wrk)    ← NEW

Output:
  knowledge-base/index.jsonl  (one JSON object per line, all fields flattened)

Index rebuild trigger:
  Any source YAML mtime > index.jsonl mtime → full rebuild
  Atomic write (tmp + mv) with flock
```

### Maturity Auto-Update Script

New script: `scripts/knowledge/update-maturity.sh`

```
Trigger: post-WRK-completion hook (or manual)
Logic:
  1. Read all entries from wrk-completions.yaml
  2. Collect all documents_read[] values
  3. For each document in resource-intelligence-maturity.yaml documents[]:
     - If document.id or document.path matches any documents_read entry → mark read
     - Set read_by_wrk and read_at
  4. Recalculate status.documents_marked_read and percent
  5. Regenerate resource-intelligence-maturity.md from YAML
```

---

## Migration Steps

### Phase 1: Schema & Structure (week 5, ~2 hours)

1. **Create `knowledge/seeds/wrk-completions.yaml`** with the extended entries schema
2. **Write migration script** `scripts/knowledge/migrate-wrk-completions.py`:
   - Read 420 records from `knowledge-base/wrk-completions.jsonl`
   - Parse the `raw` field to extract: commit hash, title, artifacts, test count
   - Classify into category/subcategory (regex on known patterns: infrastructure,
     quality, testing, documentation, security, etc.)
   - Output structured YAML
   - Manual review pass for misclassified records
3. **Bump resource-intelligence-maturity.yaml** to schema v2.0.0 with `documents[]` array
4. **Update `knowledge/seeds/schema.md`** to document `type: wrk` fields

### Phase 2: Index & Query (week 5, ~2 hours)

5. **Extend `query-knowledge.sh`** to index ALL seed YAMLs (not just career-learnings)
6. **Create `scripts/knowledge/rebuild-index.sh`** as a standalone index rebuilder
7. **Add `--type wrk` and `--type career` filters** to query-knowledge.sh
8. **TDD tests** for migration script and index builder

### Phase 3: Maturity Integration (week 6, ~2 hours)

9. **Create `scripts/knowledge/update-maturity.sh`**
10. **Wire into WRK completion workflow** — when `start_stage.py` moves a WRK to `done/`,
    call update-maturity.sh
11. **Regenerate `resource-intelligence-maturity.md`** from updated YAML
12. **Verify** maturity percentage increases as WRKs are completed

### Phase 4: Deprecation (week 6, ~1 hour)

13. **Deprecate `knowledge-base/wrk-completions.jsonl`** — add header comment pointing to
    YAML source, stop writing new records to JSONL
14. **Update MEMORY.md** to reference the new query path:
    ```
    ## Quick Refs
    - Knowledge query: `scripts/knowledge/query-knowledge.sh --category wrk`
    ```
15. **Remove raw JSONL from index rebuild path** once YAML is authoritative

---

## File Inventory (what changes)

| File | Action | Notes |
|------|--------|-------|
| `knowledge/seeds/wrk-completions.yaml` | **CREATE** | 420 migrated + future WRKs |
| `knowledge/seeds/schema.md` | **UPDATE** | Document type: wrk fields |
| `scripts/knowledge/migrate-wrk-completions.py` | **CREATE** | One-time migration script |
| `scripts/knowledge/rebuild-index.sh` | **CREATE** | Standalone index rebuilder |
| `scripts/knowledge/update-maturity.sh` | **CREATE** | Maturity auto-updater |
| `scripts/knowledge/query-knowledge.sh` | **UPDATE** | Index all seed YAMLs, add --type filter |
| `data/document-index/resource-intelligence-maturity.yaml` | **UPDATE** | v2.0.0 with documents[] |
| `data/document-index/resource-intelligence-maturity.md` | **REGENERATE** | From updated YAML |
| `knowledge-base/wrk-completions.jsonl` | **DEPRECATE** | Keep for reference, stop appending |
| `knowledge-base/index.jsonl` | **REGENERATE** | From all YAML sources |
| `MEMORY.md` | **UPDATE** | Add knowledge query quick ref |

---

## Architecture Diagram

```
                    YAML Sources (authoritative)
                    ─────────────────────────────
                    knowledge/seeds/
                    ├── career-learnings.yaml      (type: career)
                    ├── maritime-law-cases.yaml     (type: career)
                    ├── maritime-liabilities.yaml   (type: career)
                    ├── mooring-failures-lng-terminals.yaml (type: career)
                    ├── naval-architecture-resources.yaml   (resource catalog)
                    ├── wrk-completions.yaml        (type: wrk)  ← NEW
                    └── schema.md

                              │
                    rebuild-index.sh (mtime-gated, flock, atomic)
                              │
                              ▼

                    JSONL Query Cache
                    ─────────────────
                    knowledge-base/index.jsonl
                              │
                    query-knowledge.sh --category X --type Y --query Z
                              │
                              ▼
                    Markdown output to stdout


    WRK Completion                        Resource Intelligence
    ──────────────                        ──────────────────────
    .claude/work-queue/done/WRK-*.md      data/document-index/
                    │                     resource-intelligence-maturity.yaml
    start_stage.py (stage=done)                     │
                    │                               │
                    ├──→ append to wrk-completions.yaml
                    │         │
                    │         └── documents_read: [DOC-001, DOC-002]
                    │                     │
                    └──→ update-maturity.sh ──→ mark DOC-001 read
                                          │
                                          └──→ regenerate maturity.md
```

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| WRK completions in structured YAML | 0 | 420+ |
| Seed files indexed by query script | 1 (career only) | 6 (all seeds) |
| Resource intelligence maturity | 0% | auto-tracking |
| MEMORY.md content burden | N/A (pointers only) | unchanged (by design) |
| Time to find "what WRK built script X" | grep 332KB JSONL | `query-knowledge.sh --query "script X"` |

---

## Open Questions

1. **Should wrk-completions.yaml be split by year?** 420 records is manageable in one file
   (~100KB YAML), but at the current completion rate (~20 WRKs/week) it will reach ~1,500
   records by end of 2026. Consider splitting at 500 records:
   `wrk-completions-2026-h1.yaml`, `wrk-completions-2026-h2.yaml`.

2. **Auto-extraction fidelity**: The 420 raw records have inconsistent formatting. The
   migration script will need manual review for ~10-15% of records where the regex parser
   cannot reliably extract commit hash, artifacts, or test count.

3. **Dark intelligence integration**: Should `knowledge/dark-intelligence/` YAML files
   (gitignored, private) be indexed into the same query system? Currently excluded.
   Recommendation: index on machines where the files exist, skip gracefully where they don't.

4. **Session report → WRK completion hook**: The `gsd-session-report` skill generates
   session reports. Should these automatically append to wrk-completions.yaml? This would
   close the loop between session work and persistent knowledge. Recommendation: yes, as a
   follow-on to this architecture work.
