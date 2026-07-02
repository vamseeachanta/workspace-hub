# Plan for #3335: Drive-index: unified query CLI + index registry over heterogeneous catalogs (SQLite/JSONL/TSV/YAML)

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-07-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3335
> **Client:** N/A
> **Project:** (none — repo-internal data infrastructure)
> **Lane:** lane:codex   <!-- matches the issue's lane:codex label; heavy programming per epic #3333 provider routing. This plan was authored on lane:claude; implementation is lane:codex -->
> **Review artifacts:** scripts/review/results/2026-07-02-plan-3335-claude.md | scripts/review/results/2026-07-02-plan-3335-codex.md | scripts/review/results/2026-07-02-plan-3335-gemini.md

---

## Resource Intelligence Summary

<!-- Issue class: Data Pipeline / Harness-Infrastructure union.
     Consulted: issue body, epic body, prior plans, existing code in affected paths,
     data/document-index/registry.yaml, mounted-source-registry.yaml, pipeline config
     (scripts/data/document-index/config.yaml), live index artifacts, PR #3341. -->

### Existing repo code
- Found: `scripts/data/document-index/phase-a-index.py` + `scripts/data/document-index/config.yaml` — builds `data/document-index/index.jsonl` (the JSONL layer this CLI must query). `config.yaml` lists dde source roots under the stale alias `/mnt/remote/dev-secondary/dde/...` (lines 35–42).
- Found: `data/document-index/registry.yaml` — declares `total_docs: 1033933`, `dde_project: 495487` (lines 2, 8); the shipped `index.jsonl` has 649,564 lines, so registry doc counts and JSONL line counts diverge — the registry counts include shard/carryover layers, not only `index.jsonl`.
- Found: `data/document-index/mounted-source-registry.yaml` — existing per-source-root registry (source_id, mount_root, index_artifact_ref, availability_check_ref). It registers *source roots*, not *query-able indexes*; it is prior art for the YAML-registry shape but does not enumerate the SQLite/TSV indexes. `config/drive-index-registry.yml` (Layer 0) is a distinct, new artifact.
- Found: `data/document-index/dde-literature-catalog.yaml` (+ `dde-standards-inventory.yaml`, `dde-oil-gas-codes-scan.yaml`) — YAML catalogs with `source_dirs` under a *second* stale alias `/mnt/remote/ace-linux-2/dde/...` and per-item entries; these are the `yaml_catalog` adapter targets.
- Found (live, off-repo): `/mnt/ace/.ace-knowledge/index.db` — SQLite FTS5, `assets` 1,188,891 rows, `standards` 27,335, `code_patterns` 2,779; `assets_fts` FTS5 over (title, description, anonymized_title); `assets` already has a `canonical_path` column (partial prior normalization — adapter can prefer it when populated).
- Found (live, off-repo): `/mnt/ace/O&G-Standards/_inventory.db` — SQLite FTS5, `documents` 27,980, `text_chunks` 1,043,616; `documents_fts` over (filename, title, organization, doc_type, doc_number).
- Found (live, off-repo): `/mnt/ace/_cad-index/cad-readability-index.tsv` — 154 MB TSV, 464,170 data rows, header: `path format ecosystem readability read_tool glb name_description project size mtime`.
- Gap: **no unified query surface exists** — `scripts/data/drive-index-search/` and `config/drive-index-registry.yml` are both missing (gap proofs below). Nothing in the repo merges results across these formats.
- Gap: dde rows inside `index.jsonl` are stored under `/mnt/remote/ace-linux-2/dde/...` while the *builder config* now says `/mnt/remote/dev-secondary/dde/...` — **two distinct stale aliases** must both normalize to canonical `/mnt/dde`.

### Standards
Not applicable — data-infrastructure issue; no engineering standard governs it.

| Standard | Status | Source |
|---|---|---|
| — | not applicable | `data/document-index/standards-transfer-ledger.yaml` not relevant to CLI tooling |

### LLM Wiki pages consulted
No relevant wiki pages — this is harness/data infrastructure, not domain engineering knowledge. (Checked `knowledge/wikis/` scope per template; the FILE-level search skill that consumes this CLI is #3338, lane:claude.)

### Documents consulted
- Issue #3335 body — scope: registry + CLI + adapters + fast path + fixture tests; acceptance: merged ranked canonical-path results across ≥4 formats, graceful degradation, YAML-only extension.
- Epic #3333 body — architecture Layer 0 (`config/drive-index-registry.yml`) / Layer 1 (`scripts/data/drive-index-search/`); full index inventory table (2026-07-02); sibling boundaries: #3334 (dde SQLite index — future registry entry), #3337 (canonical-path normalization *across index contents*; #3335 only normalizes *output rows*), #3338 (skill consumer of `--json`).
- PR #3341 (OPEN) — adds `docs/standards/canonical-drive-references.md` + `scripts/setup/canonical-drive-links.sh`: canonical convention is `/mnt/<drive>` (`/mnt/ace`, `/mnt/dde`). The file is not on origin/main yet — cite the PR, and the implementation should re-check merge state at start.
- `docs/plans/` — no prior plan for #3334/#3335 or drive-index search exists (only `2026-04-20-inbox-drive-triage-session-design.md` matches "drive"; unrelated triage-session design).
- Repo rule (user memory `feedback_externalize_all_config_to_yaml.md` + template guidance): all work config (index paths, adapter params, thresholds) lives in reviewable YAML, never hardcoded — hence the registry is the single source of truth.
- `pyproject.toml` — `[tool.pytest.ini_options] testpaths = ["tests"]`; pytest ≥8.0 in dev deps; `uv run` is the repo Python convention on this machine.

### Gaps identified
- No `config/drive-index-registry.yml` — must be created from scratch (schema defined in this plan).
- No `scripts/data/drive-index-search/` package — CLI, registry loader, 4 adapters, ranking/merge, path normalization all built from scratch.
- No fixture indexes under `tests/data/drive_index_search/fixtures/` — must be created (tiny SQLite FTS5 DB, JSONL, TSV, YAML catalog).
- No shared path-alias map in code — alias table (`/mnt/remote/ace-linux-2/dde`, `/mnt/remote/dev-secondary/dde` → `/mnt/dde`) must be externalized in the registry YAML.
- `sqlite3` CLI binary is absent on this box (evidence below) — adapter must use Python stdlib `sqlite3` with read-only URI (`mode=ro`), never shell out.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-02T09:29Z via `gh issue view` / `gh pr view`):
- `#3335` — OPEN — "Drive-index: unified query CLI + index registry over heterogeneous catalogs (SQLite/JSONL/TSV/YAML)" (labels: cat:data, lane:codex, priority:high, status:needs-plan)
- `#3333` — OPEN — "EPIC: Context-aware drive-file search — skill + unified query layer over /mnt/ace + /mnt/dde file indexes"
- PR `#3341` — OPEN — "feat(setup): dde-drive NFS mount + canonical drive-reference convention" (files include `docs/standards/canonical-drive-references.md`)

**File existence** (`ls -la --time-style=long-iso`, 2026-07-02T09:30:00Z):
```
-rw-r--r-- 1 vamsee vamsee 1213304832 2026-03-26 06:03 /mnt/ace/.ace-knowledge/index.db
-rw-rw-r-- 1 vamsee vamsee  154109181 2026-06-26 06:05 /mnt/ace/_cad-index/cad-readability-index.tsv
-rw-r--r-- 1 vamsee vamsee 6838796288 2025-12-28 14:25 /mnt/ace/O&G-Standards/_inventory.db
-rwxrwxrwx 1 vamsee vamsee  623054407 2026-04-17 08:56 /mnt/local-analysis/workspace-hub/data/document-index/index.jsonl
```
- EXISTS: `scripts/data/document-index/config.yaml`, `data/document-index/registry.yaml`, `data/document-index/mounted-source-registry.yaml`, `data/document-index/dde-literature-catalog.yaml`
- MISSING (new — this plan creates): `config/drive-index-registry.yml`, `scripts/data/drive-index-search/` (whole package), `tests/data/drive-index-search/`

**Schema / row-count probes** (python3 stdlib sqlite3, read-only, 2026-07-02T09:30:15Z):
```
/mnt/ace/.ace-knowledge/index.db
  tables: ['assets','standards','formulas','methodologies','reference_data','code_patterns',
           'cross_references','asset_tags','assets_fts', ...fts shadow tables]
  assets 1188891 | standards 27335 | code_patterns 2779
  assets_fts: CREATE VIRTUAL TABLE assets_fts USING fts5(title, description, anonymized_title,
              content=assets, content_rowid=rowid)
  assets cols include: file_path, file_name, file_size, modified_date, engineering_domain, canonical_path
/mnt/ace/O&G-Standards/_inventory.db
  tables: ['documents','scan_history','documents_fts', 'document_text','text_chunks', ...]
  documents 27980 | text_chunks 1043616
  documents_fts: fts5(filename, title, organization, doc_type, doc_number, content='documents', ...)
```

**Line excerpts** (2026-07-02T09:30:53Z):
```
$ head -1 /mnt/ace/_cad-index/cad-readability-index.tsv
path	format	ecosystem	readability	read_tool	glb	name_description	project	size	mtime
$ wc -l < /mnt/ace/_cad-index/cad-readability-index.tsv
464171            # header + 464,170 data rows
$ wc -l data/document-index/index.jsonl
649564
$ head -2 data/document-index/index.jsonl   (truncated)
{"path": "/mnt/ace/O&G-Standards/Unknown/Codes_&_Standards_Database.xls", "host": "ace-linux-1",
 "source": "og_standards", "ext": "xls", "size_mb": 0.792, "mtime": "2013-12-05T14:39:20", ...}
$ grep -m1 'remote/ace-linux-2/dde' data/document-index/index.jsonl   (truncated)
{"path": "/mnt/remote/ace-linux-2/dde/documents/simulation/OrcaFlex/611 Mecor S Lay Installation/..."
$ grep -n "dev-secondary\|/mnt/" scripts/data/document-index/config.yaml | head
35:      - /mnt/remote/dev-secondary/dde/documents
36:      - /mnt/remote/dev-secondary/dde/0000 O&G
...
$ grep -n "dde_project\|total" data/document-index/registry.yaml | head -3
2:total_docs: 1033933
8:  dde_project: 495487
```
Finding: JSONL *contents* use alias `/mnt/remote/ace-linux-2/dde/...`; the *builder config* uses `/mnt/remote/dev-secondary/dde/...`. Both must map → `/mnt/dde`.

**Gap proofs** (2026-07-02T09:32:31Z):
- `ls scripts/data/drive-index-search config/drive-index-registry.yml` → "No such file or directory" (both) → confirms CLI package and registry do not exist.
- `ls docs/plans/ | grep -E '3334|3335|drive'` → only `2026-04-20-inbox-drive-triage-session-design.md` → no prior plan for this issue.
- `sqlite3` (CLI) → `command not found` (2026-07-02T09:30:02Z) → adapter must use Python stdlib `sqlite3`, not subprocess.

**Reproduction proofs** (performance ground truth for the two contested design decisions, per Step 1.5):

```
$ time grep -c -i "mooring" data/document-index/index.jsonl        # 623 MB streaming scan
811
real  0m0.224s   (warm page cache; cold ≈ disk read of 623 MB, est. 3–6 s on local SSD)
```
CAVEAT (review finding, re-measured): the 0.224 s is `grep -c` — a **lower bound** on any
scan, NOT the Python adapter. A live re-measure of the adapter loop (Python line iteration
+ substring prefilter over the same 623 MB, BEFORE json parsing/scoring of candidates) is
**2.18 s warm**. Benchmark table under "JSONL decision" carries both figures.

```
$ python3 (stdlib sqlite3, mode=ro)  2026-07-02T09:32:17Z
'mooring'             0.223s  3 rows  top: ('/mnt/ace/docs/disciplines/drilling/projects/3824_bp_
                                       macondo_.../Mooring Line.SLDPRT', bm25=-12.72)
'mooring OR fatigue'  0.055s  3 rows
_inventory.db 'mooring' MATCH: 0.041s  [(151, -7.62), (26581, -8.66), (26582, -8.66)]
NOTE: MATCH 'mooring fatigue' (implicit AND) returned [] on assets_fts — title/description are
sparsely populated; CLI must default multi-token queries to OR with AND-boost, not bare AND.
```

- Reproduced at: 2026-07-02T09:32:17Z
- Failure mode observed matches issue claim: YES — four live index formats, zero shared query surface; per-format probes each required bespoke code to answer one query.

<!-- Source count: issue #3335 body, epic #3333 body, PR #3341, phase-a-index.py+config.yaml,
     registry.yaml, mounted-source-registry.yaml, dde-literature-catalog.yaml, live DB/TSV/JSONL
     probes, docs/plans/ sweep, pyproject.toml = 10 distinct sources ≥ 3 required. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-02-issue-3335-drive-index-query-cli.md |
| Registry (Layer 0) | config/drive-index-registry.yml |
| CLI package (Layer 1) | scripts/data/drive-index-search/ (search.py, registry.py, pathnorm.py, merge.py, adapters/) — `pathnorm.py` name matches #3337's shared-helper naming |
| Tests | tests/data/drive_index_search/ (underscored; conftest.py inserts the hyphenated CLI dir on sys.path so tests import plain module names) |
| Test fixtures | tests/data/drive_index_search/fixtures/ (tiny sqlite/jsonl/tsv/yaml + fixture builder) |
| Plan review — Claude | scripts/review/results/2026-07-02-plan-3335-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-02-plan-3335-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-02-plan-3335-gemini.md |
| Wiki updates | none (no domain knowledge added) |
| Docs updates | docs/plans/README.md index row (at implementation/PR time — intentionally not edited in this authoring pass) |

---

## Deliverable

A registry-driven `drive-index-search` CLI (`uv run python scripts/data/drive-index-search/search.py "query" --domain X --drive Y --limit N --json`) that returns merged, ranked, canonical-path results across all four live index formats (SQLite FTS5, JSONL, TSV, YAML catalog) declared in a new `config/drive-index-registry.yml`, degrading gracefully (warning + partial results, exit 0) when an index is unreachable — with fixture-backed TDD coverage per adapter.

---

## Pseudocode

### Layer 0 — `config/drive-index-registry.yml` (schema, not code)

```yaml
version: 1
canonical_aliases:                      # shared alias → canonical map (output normalization)
  /mnt/remote/ace-linux-2/dde: /mnt/dde
  /mnt/remote/dev-secondary/dde: /mnt/dde
defaults:
  staleness_days: 90
indexes:
  - id: ace_knowledge
    adapter: sqlite_fts               # one of: sqlite_fts | jsonl | tsv | yaml_catalog
    path: /mnt/ace/.ace-knowledge/index.db
    coverage: {drives: [/mnt/ace], subtree: /mnt/ace}
    domains: [engineering, marine, drilling, cad, standards]
    freshness: {built_at: "2026-03-26", staleness_days: 120}
    builder: null                      # lost builder — see #3336
    adapter_params:
      fts_table: assets_fts
      base_table: assets
      path_column: file_path           # prefer canonical_path when non-null
      select_columns: [file_name, file_size, modified_date, engineering_domain]
  - id: og_standards_inventory
    adapter: sqlite_fts
    path: "/mnt/ace/O&G-Standards/_inventory.db"
    coverage: {drives: [/mnt/ace], subtree: "/mnt/ace/O&G-Standards"}
    adapter_params: {fts_table: documents_fts, base_table: documents, path_column: file_path,
                     select_columns: [filename, organization, doc_type, doc_number, title]}
  - id: cad_readability
    adapter: tsv
    path: /mnt/ace/_cad-index/cad-readability-index.tsv
    coverage: {drives: [/mnt/ace]}
    adapter_params: {path_column: path, search_columns: [path, name_description, project],
                     passthrough_columns: [format, readability, size, mtime]}
  - id: master_document_index
    adapter: jsonl
    path: data/document-index/index.jsonl        # repo-relative allowed; resolved vs repo root
    coverage: {drives: [/mnt/ace, /mnt/dde, /mnt/local-analysis]}
    adapter_params: {path_field: path, search_fields: [path, summary, domain, org, doc_number],
                     sidecar: null}               # optional SQLite sidecar path (accelerator)
  - id: dde_literature_catalog
    adapter: yaml_catalog
    path: data/document-index/dde-literature-catalog.yaml
    coverage: {drives: [/mnt/dde]}
    adapter_params: {items_key: auto, path_fields: [path, source_dir], text_fields: [title, domain, notes]}
```
Adding an index with an existing adapter type = append one `indexes:` entry. No code change.

### `registry.py` — load + validate

```
function load_registry(path=config/drive-index-registry.yml):
    parse YAML (yaml.safe_load); reject unknown top-level keys
    for each index entry:
        require: id (unique), adapter in ADAPTER_TYPES, path, coverage.drives
        resolve repo-relative paths against repo root
        validate adapter_params against the adapter's declared param schema (dataclass)
    return Registry(indexes, alias_map, defaults)   # raises RegistryError with entry id on failure
```

### `search.py` — CLI entry / orchestrator

```
function main(argv):
    args = parse: query, --domain, --drive, --limit(20), --json, --registry(path override),
                  --index(id filter, repeatable), --timeout-per-index(sec)
    registry = load_registry(args.registry)
    selected = [ix for ix in registry.indexes
                if intersects(ix.coverage, args.drive) and intersects(ix.domains, args.domain)]
                # `domains:` ABSENT on an entry ⇒ match-all: the entry is selected
                # under any --domain filter (only an explicit domains list restricts)
    if not selected:                          # all filtered out but registry valid:
        emit(empty results + note "no indexes match the given filters"); return 0
                                              # exit 2 is reserved for registry errors
                                              # / zero REACHABLE indexes, not filters
    results, gaps = [], []
    for ix in selected:                      # sequential; per-index wall-clock budget
        # --timeout-per-index mechanism (stdlib, no async): run reachable(ix.path) +
        # the adapter call in a worker thread; thread.join(timeout).
        #   on timeout: mark gap {id, reason: "timeout"}, continue to next index;
        #   for sqlite adapters additionally call sqlite3.Connection.interrupt()
        #   (documented thread-safe) so the query aborts instead of leaking a thread
        #   stuck forever; a thread hung in os.path.exists on a dead mount is left
        #   daemonized (cannot be killed — accepted, process exits anyway).
        # reachable() runs INSIDE the budget because os.path.exists itself blocks
        # on hung NFS/sshfs mounts.
        if not reachable(ix.path):           # os.path.exists (covers unmounted drive)
            warn(stderr, f"index {ix.id} unreachable at {ix.path} — skipping")
            gaps.append({id, path, reason: "unreachable"})
            continue
        try:
            rows = ADAPTERS[ix.adapter](ix).search(tokens(args.query), limit=args.limit)
        except AdapterError as e:            # corrupt db, bad header, parse error
            warn(stderr, ...); gaps.append({id, reason: str(e)}); continue
        results += [normalize_row(r, registry.alias_map, ix) for r in rows]
    merged = ranked_merge(results, limit=args.limit)
    emit(merged, gaps, selected, json=args.json)     # human table or JSON envelope
    return 0                                          # exit-code contract:
                                                      #   0 = success, incl. partial results,
                                                      #       empty results, empty selection
                                                      #   2 = registry error OR selected>0 but
                                                      #       zero indexes reachable
```

### `adapters/sqlite_fts.py`

```
function search(tokens, limit):
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)   # stdlib; sqlite3 CLI absent on box
    match = " OR ".join(quote_fts(t) for t in tokens)          # quote each token: '"mooring"'
                                                               # (evidence: bare AND over sparse
                                                               # title/description returns [])
    sql = SELECT base.{path_column}, {select_columns}, bm25({fts_table}) AS score
          FROM {fts_table} JOIN {base_table} base ON base.rowid = {fts_table}.rowid
          WHERE {fts_table} MATCH ? ORDER BY score LIMIT ?
    return rows with rank_basis="fts_bm25", raw_score=-bm25    # higher = better
```

### `adapters/jsonl.py` — streaming, never loads 623 MB into memory

```
function search(tokens, limit):
    if params.sidecar and exists(sidecar) and mtime(sidecar) >= mtime(path):
        return sqlite_fts_search(sidecar)              # accelerator path (optional, later)
    heap = min-heap of (score, line_no, row), size cap = limit * OVERSAMPLE(4)
    for line in open(path):                            # O(1) memory line iterator
        if not any(tok.lower() in line.lower() for tok in tokens): continue   # cheap prefilter
        row = json.loads(line)                         # parse candidates only (811/649k typical)
        score = token_score(row, tokens, params.search_fields)
        if score == 0: continue    # raw-line prefilter can match OUTSIDE search_fields
                                   # (e.g., token inside an unscored JSON value) —
                                   # zero-score rows are DROPPED, never surfaced
        heap.push_capped(score, row)
    return heap.sorted_desc()  with rank_basis="token_match"
```

### `adapters/tsv.py`

```
function search(tokens, limit):
    reader = csv.reader(open(path), delimiter="\t"); header = next(reader)  # validate expected cols
    stream rows; substring prefilter on raw line; token_score over search_columns
    capped min-heap as jsonl; rank_basis="token_match"
```

### `adapters/yaml_catalog.py`

```
function search(tokens, limit):
    doc = yaml.safe_load(open(path))                   # catalogs are small (~KB–MB)
    items = locate item lists (params.items_key or walk lists-of-dicts heuristically when "auto")
    score each item over path_fields + text_fields; return top-limit; rank_basis="token_match"
```

### `pathnorm.py` + `merge.py`

```
function normalize_row(row, alias_map, ix):
    p = row.raw_path
    for alias, canonical in alias_map (longest-prefix-first):
        if p.startswith(alias + "/") or p == alias: p = canonical + p[len(alias):]; break
    return Result(canonical_path=p, raw_path=row.raw_path, source_index=ix.id,
                  adapter=ix.adapter, raw_score, rank_basis, meta={...})

function ranked_merge(results, limit):
    # scores are not cross-comparable (bm25 vs token ratio) → anchor ABSOLUTELY per
    # rank_basis. (Per-index min-max was rejected in review: it makes every index's
    # best hit exactly 1.0 — round-robin winners across indexes, and singleton result
    # sets always score 1.0 regardless of relevance.)
    token_match rows: base = matched_query_tokens / total_query_tokens     # ∈ [0,1], absolute
                      + filename-hit bonus +0.25, all-tokens-present bonus +0.25
                      → clamp to [0,1]
    fts_bm25 rows:    score_norm = 1 / (1 + max(0.0, -bm25))   # fixed squash into (0,1];
                      # sqlite bm25() is more-negative-is-better, so -bm25 ≥ 0 for hits
    dedupe on canonical_path: keep max score_norm, record other sources in meta.also_in
    sort by (-score_norm, canonical_path, source_index)          # total order → deterministic
    return first `limit`
```

### `--json` output envelope (consumed by #3338 skill)

```
{ "query": str, "generated_at": iso8601, "indexes_queried": [ids], 
  "coverage_gaps": [{"id","path","reason"}],
  "results": [{"canonical_path","raw_path","source_index","adapter","score","rank_basis",
               "meta":{...per-adapter passthrough...}}] }
```

### JSONL decision — streaming scan vs SQLite sidecar (weighed; recommendation)

| Option | Latency | Build/maintenance | Freshness risk |
|---|---|---|---|
| A. Streaming scan (prefilter + parse candidates) | `grep -c` lower bound 0.22 s warm (NOT the adapter); measured Python adapter loop **2.18 s warm** before json parse/scoring of candidates; cold adds the 623 MB disk read (est. +3–6 s on local SSD ⇒ ~5–8 s cold) | zero — reads artifact in place | none (always reads current file) |
| B. Build SQLite FTS sidecar from JSONL | <0.1 s | new build step + ~0.5–1 GB artifact + staleness tracking (overlaps #3336's remit) | sidecar can silently go stale vs JSONL |

**Recommendation: ship Option A (streaming) in this issue.** Honest numbers (corrected in review): the adapter is ~2.2 s warm — an order of magnitude SLOWER than the SQLite indexes (0.04–0.2 s), not faster; the earlier "beats the SQLite indexes' 0.2 s" claim compared `grep`, not the adapter, and is withdrawn. 2.2 s warm still fits comfortably inside the 5 s acceptance bound; the COLD path (first query after boot/eviction, ~5–8 s) may exceed 5 s — the acceptance criterion is explicitly warm latency, and cold-start cost is accepted as a one-off per session. Memory stays O(limit) and Option A adds no freshness surface. Keep `adapter_params.sidecar` in the registry schema (nullable) and the mtime-guarded sidecar fast-path in the adapter as shown, so #3336 (freshness automation) can add a sidecar later as a YAML-only + builder change. Do not build the sidecar in #3335.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | config/drive-index-registry.yml | Layer 0 registry — single source of truth (5 initial entries: ace_knowledge, og_standards_inventory, cad_readability, master_document_index, dde_literature_catalog) |
| Create | scripts/data/drive-index-search/search.py | CLI entry point + orchestrator + output emitters |
| Create | scripts/data/drive-index-search/registry.py | registry load/validate (RegistryError with entry id) |
| Create | scripts/data/drive-index-search/pathnorm.py | alias→canonical path normalization |
| Create | scripts/data/drive-index-search/merge.py | per-index score normalization + deterministic ranked merge + dedupe |
| Create | scripts/data/drive-index-search/adapters/__init__.py | ADAPTER_TYPES dispatch table |
| Create | scripts/data/drive-index-search/adapters/base.py | Adapter ABC, param dataclasses, AdapterError, token_score helper |
| Create | scripts/data/drive-index-search/adapters/sqlite_fts.py | FTS5 bm25 adapter (stdlib sqlite3, mode=ro, quoted-token OR MATCH) |
| Create | scripts/data/drive-index-search/adapters/jsonl.py | streaming JSONL adapter (capped heap; optional sidecar fast-path) |
| Create | scripts/data/drive-index-search/adapters/tsv.py | streaming TSV adapter (csv module — quoted-field safe) |
| Create | scripts/data/drive-index-search/adapters/yaml_catalog.py | YAML catalog adapter |
| Create | tests/data/drive_index_search/conftest.py | inserts scripts/data/drive-index-search/ on sys.path (hyphenated dir is not importable as a package) |
| Create | tests/data/drive_index_search/test_registry.py | registry parse/validate tests |
| Create | tests/data/drive_index_search/test_adapters.py | per-format adapter tests against fixtures |
| Create | tests/data/drive_index_search/test_merge_and_normalize.py | ranked-merge determinism + path normalization tests |
| Create | tests/data/drive_index_search/test_cli.py | end-to-end CLI tests (degradation, --json schema, exit codes) |
| Create | tests/data/drive_index_search/fixtures/build_fixtures.py | generates fixture.db (FTS5, ~20 rows) deterministically; checked-in flat fixtures below |
| Create | tests/data/drive_index_search/fixtures/{fixture.jsonl, fixture.tsv, fixture-catalog.yaml, test-registry.yml} | tiny per-format fixture indexes + fixture registry (never the live DBs) |
| Update | docs/plans/README.md | add this plan to the index (at implementation/PR time — NOT edited in this plan-authoring pass) |

No existing file is modified; `mounted-source-registry.yaml` and `phase-a-index.py` are read-only inputs to registry content.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_registry_parses_valid_yaml | registry parsing | fixtures/test-registry.yml | Registry with 5 entries, alias_map populated |
| test_registry_rejects_unknown_adapter | validation | entry with `adapter: parquet` | RegistryError naming entry id |
| test_registry_rejects_duplicate_ids | validation | two entries id=x | RegistryError |
| test_registry_rejects_missing_required_key | validation | entry without `path` | RegistryError |
| test_registry_resolves_relative_paths | repo-relative path handling | `path: data/...` | absolute path under repo root |
| test_sqlite_fts_adapter_bm25_rank | sqlite_fts vs fixture.db | query "mooring" | ≥2 rows, rank_basis=fts_bm25, best-match first |
| test_sqlite_fts_multi_token_or_semantics | OR-not-AND default (evidence: bare AND → []) | query "mooring fatigue", fixture has docs with only one term each | both docs returned |
| test_sqlite_fts_query_token_quoting | FTS syntax injection safety | query `mooring" OR x` / `near(` | no sqlite3.OperationalError; treated as literals |
| test_sqlite_fts_readonly | live-DB safety | fixture.db opened by adapter | connection URI mode=ro; write attempt fails |
| test_jsonl_adapter_streaming_topk | jsonl vs fixture.jsonl | query "riser", limit=3 | top-3 by token score; memory stays O(limit) (no full-file list) |
| test_jsonl_adapter_skips_malformed_line | robustness | fixture with 1 bad JSON line | warning counted, other rows returned |
| test_tsv_adapter_columns | tsv vs fixture.tsv | query matching name_description | row with passthrough meta (format, readability, mtime) |
| test_tsv_adapter_rejects_bad_header | header validation | TSV missing `path` column | AdapterError |
| test_yaml_catalog_adapter | yaml_catalog vs fixture-catalog.yaml | query matching an item title | item with canonicalized path |
| test_ranked_merge_deterministic | merge determinism | same result set shuffled 10× | byte-identical ordered output (tie-break by canonical_path, source_index) |
| test_ranked_merge_dedupes_canonical_path | cross-index dedupe | same file from 2 indexes | one row, meta.also_in lists second source |
| test_merge_normalizes_scores_per_index | bm25 vs token scores comparable | mixed rank_basis rows | all scores in [0,1]; per-index minmax applied |
| test_normalize_dev_secondary_alias | path normalization | `/mnt/remote/dev-secondary/dde/Literature/x.pdf` | `/mnt/dde/Literature/x.pdf` |
| test_normalize_ace_linux2_alias | second stale alias (evidence: JSONL contents) | `/mnt/remote/ace-linux-2/dde/documents/y.xlsx` | `/mnt/dde/documents/y.xlsx` |
| test_normalize_longest_prefix_and_noop | non-aliased paths untouched; no partial-segment match | `/mnt/ace/docs/a.pdf`, `/mnt/remote/ace-linux-2/dde-extra/z` | unchanged |
| test_unreachable_index_degrades | graceful degradation | registry entry pointing at nonexistent path | stderr warning, coverage_gaps entry, partial results, **exit 0** |
| test_all_indexes_unreachable_exit_code | failure boundary | registry with only unreachable entries | exit 2, empty results, gaps listed |
| test_cli_domain_drive_fastpath | coverage filtering | --drive /mnt/dde against fixture registry | only dde-coverage indexes opened (assert via probe/monkeypatch) |
| test_cli_json_schema | --json contract for #3338 | fixture query --json | keys: query, generated_at, indexes_queried, coverage_gaps, results[]; result keys: canonical_path, raw_path, source_index, adapter, score, rank_basis, meta |
| test_cli_limit_respected | --limit | limit=2 across 4 fixtures | exactly 2 rows |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/data/drive_index_search/ -v`
- [ ] No regression: `uv run pytest tests/` passes (or matches pre-change failure baseline recorded at branch time)
- [ ] Live smoke (ace-linux-1, drives mounted): `uv run python scripts/data/drive-index-search/search.py "mooring fatigue" --limit 20 --json` returns results from ≥4 distinct `source_index` values (issue acceptance: ≥4 formats) with every `canonical_path` starting `/mnt/` and zero `/mnt/remote/` aliases in output
- [ ] Live degradation smoke: with one registry path temporarily pointed at a nonexistent mount, same command exits 0, prints stderr warning, and lists the index in `coverage_gaps`
- [ ] Registry-driven extension proven: adding a copy of the TSV fixture as a 6th registry entry (YAML-only diff) makes it appear in `indexes_queried` with no code change
- [ ] JSONL query does not load the file into memory: peak RSS of a live JSONL-only query stays < 200 MB (`/usr/bin/time -v`), and warm latency < 5 s
- [ ] Fixtures under `tests/data/drive_index_search/fixtures/` are < 100 KB total; no test touches `/mnt/ace` or `/mnt/dde`
- [ ] Docs: plan indexed in docs/plans/README.md at PR time
- [ ] Review artifacts posted to scripts/review/results/ (3 providers)

---

## Adversarial Review Summary

<!-- Review happens after plan authoring. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | 10 findings: JSONL benchmark misattributed (grep vs adapter — corrected to measured 2.18 s warm); --timeout-per-index lacked a mechanism (now thread+join + sqlite interrupt); per-index min-max merge pathology (replaced with absolute token-fraction base + fixed bm25 squash); registry freshness/--force-loss annotations; pathnorm.py naming + underscored test tree + conftest import strategy; smaller contract clarifications (domains absent = match-all, empty-selection exit 0, score==0 dropped, tracemalloc-bounded memory test) |
| Codex | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |
| Gemini | PENDING — dispatch deferred | — |

**Overall result:** PASS after revisions (Claude r1)

Revisions made based on review:
- F1 (HIGH): benchmark table corrected — grep 0.22 s labeled lower bound; measured Python adapter loop 2.18 s warm added; "beats SQLite" claim removed; cold-path estimate (~5–8 s) stated against the 5 s bound.
- F2: `--timeout-per-index` mechanism specified (worker thread + join(timeout); `sqlite3.Connection.interrupt()` for sqlite adapters).
- F3: per-index min-max normalization rejected; absolute token-fraction base + fixed bm25 squash; merge test pins multi-token hit above singleton winners.
- F4: `master_document_index` registry entry annotated `frozen 2026-04-17` + dde-rows-lost-on---force note (composition with #3334 F1); helper renamed `normalize.py` → `pathnorm.py` to match #3337.
- F5: test tree unified under `tests/data/drive_index_search/` (incl. fixtures); conftest.py sys.path import strategy stated.
- F6–F10: per-index known-hit smoke queries allowed; shard/carryover count claim labeled hypothesis; `domains:` absent = match-all + empty-selection exit 0 defined; score==0 rows dropped; memory test made objectively checkable.

---

## Risks and Open Questions

- **Risk — sibling scope collision (#3337):** #3337 normalizes canonical paths *inside index contents*; #3335 must only normalize *output rows* via the registry alias map. Keep `canonical_aliases` in the registry so #3337 can later shrink it to a no-op without CLI changes.
- **Risk — #3334 lands a dde SQLite index mid-flight:** designed for — it becomes one new `sqlite_fts` YAML entry. Implementation should re-check #3334 state at start (`gh issue view 3334`) and add the entry if the DB exists.
- **Risk — PR #3341 not yet merged:** canonical convention doc (`docs/standards/canonical-drive-references.md`) is on an open PR; `/mnt/dde` may not be mounted on this box yet. The CLI's unreachable-index degradation covers this, but the live dde smoke test may be deferred until the mount exists.
- **Risk — FTS AND-semantics trap (measured):** `MATCH 'mooring fatigue'` returns 0 rows on `assets_fts` because title/description are sparsely populated. Mitigated: quoted-token OR query + all-tokens-present bonus in merge. Reviewers should challenge the ranking weights (0.25/0.25 bonuses are initial guesses; tests pin behavior, constants live in one module).
- **Risk — `_inventory.db` is 6.84 GB on a mounted drive:** opening is cheap (probe: 0.041 s MATCH) since SQLite reads pages lazily, but a cold NFS-ish mount could stall; per-index wall-clock budget (`--timeout-per-index`, default generous) + degradation path bounds worst case.
- **Risk — registry doc counts vs JSONL line counts diverge** (1,033,933 vs 649,564): the CLI queries the JSONL artifact as-is; it does not promise registry-level counts. Shard/carryover layers (`data/document-index/shards/`) are out of scope; flag to #3336/#3340 whether shards need a registry entry.
- **Open:** should `standards` (27,335 rows) and `code_patterns` tables in `.ace-knowledge/index.db` be exposed as separate registry entries (same adapter, different `adapter_params`)? Plan says yes-capable but ships only `assets` in v1 — flag for user during approval.
- **Open:** result `meta` passthrough fields per adapter are heterogeneous by design; #3338 (skill) should confirm which fields it needs before v1 freeze.
- **Open:** exit-code contract chosen here (0 = success incl. partial; 2 = registry error or zero reachable indexes) — confirm acceptable to hook/skill consumers.

---

## Complexity: T2

**T2** — new multi-module CLI package + registry schema + 4 adapters + fixture suite (~15 files), TDD required, but no modification of existing code paths, no schema migration of live data, and all live artifacts consumed read-only.
