# Plan for #2363: feat(doc-intel): materialize wiki_refs reverse lookup from doc_key to citing wiki pages

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2363
> **Review artifacts (planned):** scripts/review/results/2026-04-26-plan-2363-claude.md | ...-codex.md | ...-gemini.md
> **Supersedes:** docs/plans/2026-04-23-issue-2363-wiki-refs-reverse-lookup.md (draft) — re-baselined 2026-04-26 to correct registry-surface targeting and tighten upstream-dependency framing.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` (1,465 lines) — canonical wiki CLI; the issue body explicitly names this as the location to emit `wiki_refs`. Constants `FRONTMATTER_REQUIRED = {"title","tags","added","last_updated"}` and `FRONTMATTER_RECOMMENDED = {"sources"}` already define the frontmatter contract this plan will read from. There is no `doc_key` field in the current required or recommended sets.
- Found: `scripts/knowledge/doc-key-lookup.py` — existing **forward**-lookup CLI (`doc_key → registry/path/wiki`). Implements `search_index_by_key()` against `data/document-index/index.jsonl` and walks `WIKI_DOMAINS = ["engineering","marine-engineering","maritime-law","naval-architecture","personal"]`. The new reverse CLI will mirror its argparse, exit-code, and `--json` shape so operators have a consistent surface.
- Found: `scripts/knowledge/tests/` directory with existing pytest harness pattern (e.g., `test_llm_wiki.py`).
- Found: `scripts/data/document-index/provenance.py` — L2 provenance merge/write semantics (atomic-merge into `provenance[]`); not modified by this plan but consulted as the precedent for "back-link is materialized at L2."
- Found: `data/document-index/standards-transfer-ledger.yaml` — 436-entry ledger; primary key is human-readable `id` (e.g., `5L`, `API-INSP-570`); fields include `doc_path: ''`, `doc_paths: []`, `status`, `repo`, `modules`. **Most rows have empty `doc_path` and no `doc_key` field.** Back-population of `doc_key` is the scope of the OPEN follow-on #2362.
- Found: `data/document-index/index.jsonl` — **the per-document L2 surface** (1,033,933 records per `registry.yaml`). Each line is one document keyed by `content_hash` (carrying a `doc_key` value per #2207 Section 3.1). This is the correct per-document materialization target — not `registry.yaml`.
- Found: `data/document-index/registry.yaml` — **aggregate statistics only** (`total_docs`, `by_source`, `by_domain`, `repos:`). It is NOT a per-document surface and therefore cannot host per-document `wiki_refs`. The prior plan (2026-04-23) named this surface in error; this revision corrects the target.
- Gap: `grep -rn 'wiki_refs' data/ scripts/knowledge/ scripts/data/` returns empty — no `wiki_refs` field is materialized anywhere today and no writer exists.
- Gap: no reverse-lookup CLI (`doc_key → wiki pages`).
- Gap: no wiki page currently carries a canonical `sha256:` `doc_key` in its frontmatter (verified: `grep -rln 'doc_key' knowledge/wikis/` returns empty for page bodies).

### Standards
Not applicable — this is a doc-intelligence data-pipeline concern. No standards-derived constants are emitted, so `.claude/rules/calc-citation-contract.md` does not bind. The plan does, however, honor the rule's deny-list: pages under `knowledge/wikis/*/wiki/sources/` are vendor-derivative; the reverse lookup will cite them in `wiki_refs` when their frontmatter cites a canonical `doc_key`, but the runbook will document that cleaner traceability comes from `wiki/standards/` and `wiki/concepts/` pages once #2360 ships `doc_key` into the L3 required-set.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/CLAUDE.md` — engineering wiki frontmatter authority. Required: `{title, tags, added, last_updated}`. Recommended: `sources` (slug list, e.g., `[dnv-rp-b401]`). No `doc_key` today.
- `knowledge/wikis/marine-engineering/wiki/sources/001.md` — example auto-generated source page. Frontmatter has `slug: 001`, `domain: marine-engineering`, `ingested: 2026-04-07 …`, `tags: []`. No `doc_key`. This is dominant in the 19,184-page domain.
- `knowledge/wikis/marine-engineering/wiki/sources/csa-z276-1-20-lng-marine-structures.md` — recently promoted standards page; verify whether its frontmatter exposes `doc_key` (if yes, this page is in scope for the first wave of materialization; if no, it is blocked behind #2360 like all others).
- `knowledge/wikis/maritime-law/wiki/index.md` — illustrates that the maritime-law domain's 22 pages are primarily case entities (`entities/torrey-canyon-1967.md`) where the underlying citation is a court opinion, not a `doc_key`-bearing standards PDF. Materialization for this domain will likely yield zero `wiki_refs` until #2360 lands and case-source PDFs are indexed.
- `knowledge/wikis/cross-links.md` — auto-generated cross-link index (16 entries on 2026-04-26). This is similarity-keyword cross-references, NOT the L3→L2 back-link the issue describes; the two artifacts are complementary, not overlapping.

### Documents consulted
- Issue body (`gh issue view 2363`) — deliverables: implementation plan, reverse-lookup CLI/helper, regression tests for add/update/delete, bounded backfill, docs explaining the L3→L2 rule. Acceptance criteria are stated in given/when/then form.
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` Section 4.2 (line 210) — `wiki_refs | list[string] | Paths to LLM-wiki pages that cite this document as a source. Back-link field — see Section 4.3. | Materialized at L2; originates from L3`. Section 4.3 (lines 212-225) is the binding contract: `wiki_refs` is a denormalized index at L2; L3 owns the authoritative citation, L2 owns the reverse index. Section 8.1 forbids "duplicate parsing" — the reverse lookup must read the citation already emitted by L3, never re-parse the source document.
- `docs/document-intelligence/intelligence-accessibility-map.md` Section 6.6 (lines 290-296) — names the gap explicitly: "given a registry entry or `doc_key`, there is no way to find which wiki pages cite it without grep." Classification: weak — medium severity.
- `docs/document-intelligence/README.md` — entry point per #2208. Confirms architecture-doc reading order and current page counts.
- `docs/plans/2026-04-23-issue-2363-wiki-refs-reverse-lookup.md` (prior draft) — superseded by this revision. Two corrections: (a) target `index.jsonl` (per-document) instead of `registry.yaml` (aggregate-stats only); (b) hard-couple this plan to #2360 since no wiki page carries `doc_key` today, so the v1 deliverable is "infrastructure plus zero-row materialization with documented blocker," not a populated registry.
- Related issues:
  - #2205 OPEN — parent operating model.
  - #2207 CLOSED — provenance contract; binds `wiki_refs` semantics.
  - #2360 OPEN — "update wiki CLAUDE.md files to declare `doc_key` in L3 frontmatter required-set." **Hard upstream dependency**: until this lands, the L3 emitter has nothing canonical to extract.
  - #2362 OPEN — "Phase E back-population — populate `doc_key` on pre-existing standards-transfer-ledger.yaml entries." **Hard upstream dependency for ledger-side materialization**: until ledger rows have `doc_key`, the emitter cannot find a row to back-link to from the ledger.
  - #2233 OPEN — adds frontmatter field to wiki schema; complements #2360.
  - #2068 OPEN — cross-link JSONL package for wiki-to-standard / wiki-to-module.
  - #2011 OPEN, #2044 OPEN — cross-link infrastructure.

### Gaps identified
- No `wiki_refs` field present anywhere in `data/` or `scripts/`.
- No reverse-lookup CLI (`doc_key → wiki pages`).
- No `doc_key` in wiki frontmatter on any current page (blocked by #2360).
- `registry.yaml` is aggregate-stats; no per-document surface other than `index.jsonl` exists today for materialization.
- `standards-transfer-ledger.yaml` rows largely lack `doc_key` (blocked by #2362).
- No regression tests covering add/update/delete of citing wiki pages.
- No bounded-backfill tool with a story for the 19,184-page marine-engineering domain.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26 via `gh issue view`):
- `#2363` — OPEN — "feat(doc-intel): materialize wiki_refs reverse lookup from doc_key to citing wiki pages"
- `#2205` — OPEN — parent operating model
- `#2207` — CLOSED — provenance contract (binds `wiki_refs`)
- `#2360` — OPEN — "feat(knowledge): update wiki CLAUDE.md files to declare doc_key in L3 frontmatter required-set"
- `#2362` — OPEN — "feat(data): Phase E back-population — populate doc_key on pre-existing standards-transfer-ledger.yaml entries"
- `#2233` — OPEN — frontmatter field for wiki schema
- `#2068` — OPEN — cross-link JSONL package for wiki-to-standard

**File existence** (`ls` 2026-04-26):
- EXISTS: `scripts/knowledge/llm_wiki.py` (51,131 bytes, 1,465 lines, mtime 2026-04-16)
- EXISTS: `scripts/knowledge/doc-key-lookup.py`
- EXISTS: `scripts/knowledge/tests/` (pytest harness)
- EXISTS: `data/document-index/standards-transfer-ledger.yaml` (436 entries)
- EXISTS: `data/document-index/registry.yaml` (aggregate-stats only)
- EXISTS: `data/document-index/index.jsonl` (~1.03M records per registry.yaml)
- EXISTS: `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (line 210 binds `wiki_refs`)
- EXISTS: `docs/plans/2026-04-23-issue-2363-wiki-refs-reverse-lookup.md` (prior draft, superseded)
- MISSING (this plan creates): `scripts/knowledge/wiki_refs_reverse_lookup.py`, `scripts/knowledge/wiki_refs_emitter.py`, `scripts/knowledge/backfill_wiki_refs.py`, `scripts/knowledge/tests/test_wiki_refs.py`, `scripts/knowledge/tests/fixtures/wiki-refs/`, `docs/document-intelligence/wiki-refs-reverse-lookup.md`, `data/document-index/wiki-refs-index.jsonl` (sidecar — see Pseudocode rationale).

**Line excerpts** (`standards-codes-provenance-reuse-contract.md`):
```
210:| `wiki_refs` | list[string] | Paths to LLM-wiki pages that cite this document as a source. Back-link field — see Section 4.3. | Materialized at L2; originates from L3 |
218:`wiki_refs` is a back-link field — it is **populated from** L3 (wiki pages emit their `doc_key` citations) and **materialized at** L2 (the registry keeps the list for reverse lookup).
```

**Line excerpts** (`intelligence-accessibility-map.md`):
```
292:**Problem:** Wiki pages in `knowledge/wikis/*/wiki/` reference source documents via frontmatter `sources` fields, but there is no reverse lookup: given a registry entry or `doc_key`, there is no way to find which wiki pages cite it without grep.
296:**Classification:** **Weak — medium severity.** The provenance contract (#2207) recommends `wiki_refs` back-links on registry entries. Until implemented, this is a search problem.
```

**Gap proofs**:
- `grep -rn 'wiki_refs' data/ scripts/knowledge/ scripts/data/` → empty → confirms no materialized back-links and no writer exist.
- `grep -rln 'doc_key' knowledge/wikis/` → engineering/SCHEMA.md and per-wiki CLAUDE.md only (the schema docs themselves), not page frontmatter → confirms no wiki page carries `doc_key` today.
- `head -40 data/document-index/registry.yaml` → shows `total_docs`, `by_source`, `by_domain`, `repos` keys only — no per-document rows → confirms `registry.yaml` cannot be a per-document materialization target.

**Source count verification:** Issue body + provenance contract (#2207) + accessibility map (#2096) + parent operating model (#2205) + prior plan (2026-04-23) + live registry files (`registry.yaml`, `index.jsonl`, `standards-transfer-ledger.yaml`) + 4 wiki sample pages = 10+ distinct sources. Minimum (≥3) far exceeded.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-26-issue-2363-wiki-refs-reverse-lookup.md` (when promoted from /tmp staging) |
| Forward emitter (helper module) | `scripts/knowledge/wiki_refs_emitter.py` (new — extracted as a module; invoked from `llm_wiki.py` ingest/update/delete paths) |
| `llm_wiki.py` integration | `scripts/knowledge/llm_wiki.py` — call `emit_wiki_refs(...)` from ingest/update; add a delete-aware path |
| Reverse-lookup CLI | `scripts/knowledge/wiki_refs_reverse_lookup.py` |
| Bounded backfill tool | `scripts/knowledge/backfill_wiki_refs.py` |
| Tests | `scripts/knowledge/tests/test_wiki_refs.py` (covers emitter, CLI, backfill end-to-end) |
| Test fixtures | `scripts/knowledge/tests/fixtures/wiki-refs/` (synthetic wiki pages + ledger rows + index.jsonl shard) |
| L2 surface — sidecar index (primary write target for v1) | `data/document-index/wiki-refs-index.jsonl` (new — JSONL sidecar; see rationale below) |
| L2 surface — ledger rows (secondary; gated on #2362) | `data/document-index/standards-transfer-ledger.yaml` (rows that already carry `doc_key` get a `wiki_refs:` field) |
| Runbook | `docs/document-intelligence/wiki-refs-reverse-lookup.md` |
| Plan index update | `docs/plans/README.md` (add row when plan is promoted from /tmp) |
| Plan review — Claude | `scripts/review/results/2026-04-26-plan-2363-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-26-plan-2363-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-26-plan-2363-gemini.md` |

**Why a JSONL sidecar instead of mutating `index.jsonl`:** `data/document-index/index.jsonl` is the dominant per-document surface but has 1.03M rows and is rewritten by the indexing pipeline (`phase-a-index.py` and friends). Mutating that file from a wiki ingest creates merge contention with the indexer and risks lost writes. A new `wiki-refs-index.jsonl` keyed by `doc_key` is (a) write-isolated from the indexer, (b) cheap to rebuild from wiki frontmatter, (c) trivially queryable line-by-line, and (d) consistent with the parent operating model's allowed information flows (parent #2205 Section 4: L2 owns provenance; the back-link is a denormalized L2 index, materialized separately from the canonical per-document registry). The runbook explicitly names this file as the canonical reverse-lookup surface; the ledger field is a secondary projection for human-navigable rows.

---

## Deliverable

A reverse-lookup path from `doc_key` → citing wiki pages, comprising:
1. A `wiki_refs_emitter` helper module that extracts canonical `sha256:` `doc_key` citations from wiki-page frontmatter and writes a denormalized `wiki-refs-index.jsonl` sidecar at L2.
2. Hooks in `scripts/knowledge/llm_wiki.py` that invoke the emitter on add / update / delete of wiki pages.
3. A `wiki_refs_reverse_lookup.py` CLI (mirroring `doc-key-lookup.py`'s shape) returning citing wiki pages for a given `doc_key` with deterministic exit codes.
4. A bounded `backfill_wiki_refs.py` tool that walks existing wiki pages with `--domains` and `--limit` flags and emits a report.
5. A runbook `docs/document-intelligence/wiki-refs-reverse-lookup.md` documenting the L3→L2 materialization rule, the `#2360`/#2362 upstream dependencies, the slug-style-out-of-scope carve-out, and the sources-deny-list per `.claude/rules/calc-citation-contract.md`.

---

## Scope boundaries (explicit)

- **In scope:** canonical `sha256:<hex>` (and read-only `md5:<hex>` for legacy `og_standards`, never joined across namespaces) `doc_key` citations extracted from wiki-page frontmatter.
- **In scope (first L2 surface):** `data/document-index/wiki-refs-index.jsonl` (new sidecar). This is the durable, queryable surface required by issue acceptance criterion 4.
- **In scope (second L2 surface, conditional):** `data/document-index/standards-transfer-ledger.yaml` rows that already carry `doc_key`. Rows without `doc_key` are skipped silently — the runbook documents that #2362 will widen this surface.
- **In scope (first wiki domain wave):** `engineering` (77-83 pages) and `naval-architecture` (45 pages) — small enough to backfill in one pass once #2360 lands `doc_key` in their frontmatter.
- **Bounded second wave:** `marine-engineering` (~19,184 pages) is backfilled in domain-specific bounded passes via `--domains marine-engineering --limit N`. Default `--limit` is 500. Full-domain backfill must be explicitly opted into with `--limit 0` (interpreted as unbounded). The runbook flags 19k as a freshness liability and recommends weekly incremental passes after first full sweep.
- **Out of scope:** slug-style `sources: [dnv-rp-b401]` legacy frontmatter — emitter logs and skips; resolution is #2360's job.
- **Out of scope:** creating `doc_key` rows in `index.jsonl` for documents the indexer has not yet seen.
- **Out of scope:** wiki-page generation from `wiki_refs`.
- **Out of scope:** real-time/sync invocation from a git pre-commit hook (deferred per "Open Questions").

---

## Pseudocode

### Emitter (extracts L3 citations, writes L2 sidecar)

```
SIDECAR = data/document-index/wiki-refs-index.jsonl     # one JSON object per line
LEDGER  = data/document-index/standards-transfer-ledger.yaml
LOCKDIR = data/document-index/.locks/                    # repo-local file locks

def extract_canonical_doc_keys(frontmatter):
    keys = set()
    # Read both required (when #2360 lands) and any current optional doc_key field.
    for value in frontmatter.get("doc_key", []) + frontmatter.get("doc_keys", []):
        if isinstance(value, str) and (value.startswith("sha256:") or value.startswith("md5:")):
            keys.add(value)
        else:
            log_warning(f"non-canonical citation skipped: {value!r}")
    # Slug-style sources are explicitly NOT extracted — see scope boundary.
    return keys

def emit_wiki_refs(wiki_page_path, action):  # action in {"add","update","delete"}
    with file_lock(LOCKDIR / "wiki-refs.lock"):
        # Read existing sidecar into memory keyed by doc_key (small index — back-links only).
        sidecar = load_jsonl_as_index(SIDECAR)        # {doc_key: sorted-set of repo-relative paths}

        if action == "delete":
            new_keys = set()
        else:
            fm = parse_frontmatter(wiki_page_path)
            new_keys = extract_canonical_doc_keys(fm)

        rel_path = repo_relative(wiki_page_path)
        old_keys = {k for k, paths in sidecar.items() if rel_path in paths}

        for key in new_keys - old_keys:        # added
            sidecar.setdefault(key, set()).add(rel_path)
        for key in old_keys - new_keys:        # removed
            sidecar[key].discard(rel_path)
            if not sidecar[key]:
                del sidecar[key]

        atomic_write_jsonl(SIDECAR, sidecar)   # temp file + rename, sorted output

        # Secondary projection: ledger rows that have doc_key get wiki_refs as a YAML field.
        update_ledger_wiki_refs(LEDGER, sidecar)
```

### Reverse-lookup CLI

```
def lookup(doc_key, json_out=False):
    # Reject malformed input (must be <algo>:<hex> per #2207 Section 3.1).
    if not re.match(r"^(sha256|md5):[0-9a-fA-F]+$", doc_key):
        sys.exit(2)
    sidecar = load_jsonl_as_index(SIDECAR)
    pages = sorted(sidecar.get(doc_key, []))
    # Optional: also surface citing pages from ledger rows for the same doc_key.
    ledger_pages = ledger_wiki_refs_for(LEDGER, doc_key)
    pages = sorted(set(pages) | set(ledger_pages))
    if not pages:
        sys.exit(3)
    print_pages(pages, json_out)
    sys.exit(0)
```

Exit codes (mirror `doc-key-lookup.py` conventions): `0` = ≥1 hit; `2` = malformed `doc_key`; `3` = valid but no hits.

### Bounded backfill

```
def backfill(domains=None, limit=500, dry_run=False):
    # Walk wiki pages in chosen domains; for each, run emit_wiki_refs(..., action="add").
    # --limit caps pages processed; --limit 0 = unbounded (gated behind explicit flag).
    # --dry-run: log only, no writes.
    counts = {"visited": 0, "added": 0, "slug_only_skipped": 0, "non_canonical_skipped": 0}
    for page in iter_wiki_pages(domains):
        counts["visited"] += 1
        if limit and counts["visited"] > limit:
            break
        emit_wiki_refs(page, action="add")
        # increment counters from emitter telemetry
    write_report(f"docs/reports/wiki-refs-backfill-{today}.md", counts)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/wiki_refs_emitter.py` | helper module: extract canonical `doc_key` citations + write sidecar + project to ledger |
| Modify | `scripts/knowledge/llm_wiki.py` | invoke `emit_wiki_refs(...)` from `ingest`, `batch-ingest`, and add a delete-aware code path (currently absent — see Risks) |
| Create | `scripts/knowledge/wiki_refs_reverse_lookup.py` | reverse query CLI |
| Create | `scripts/knowledge/backfill_wiki_refs.py` | bounded backfill |
| Create | `scripts/knowledge/tests/test_wiki_refs.py` | TDD coverage for emitter + CLI + backfill |
| Create | `scripts/knowledge/tests/fixtures/wiki-refs/` | synthetic registry + wiki pages |
| Create | `data/document-index/wiki-refs-index.jsonl` | sidecar; written by backfill on first run |
| Modify (gated) | `data/document-index/standards-transfer-ledger.yaml` | add `wiki_refs:` field on rows that already carry `doc_key`. No-op for the current state since ~all rows lack `doc_key`; becomes meaningful once #2362 ships. |
| Create | `docs/document-intelligence/wiki-refs-reverse-lookup.md` | runbook + L3→L2 rule + sources-deny-list note |
| Update | `docs/plans/README.md` | add this plan row when promoted from /tmp |

Tooling and data are committed in **separate** PRs to keep review surfaces clean: PR-A introduces the emitter/CLI/backfill/tests/runbook (no data mutation). PR-B runs the backfill on `engineering` + `naval-architecture` and commits the resulting sidecar deltas. PR-C runs the bounded marine-engineering backfill (split further if PR diff exceeds reviewer-friendly size).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_emit_adds_wiki_ref_on_page_creation` | new wiki page with `doc_key: sha256:abc...` → sidecar gains entry | fixture: page + empty sidecar | sidecar JSONL contains `{"doc_key":"sha256:abc...","wiki_refs":["…/page.md"]}` |
| `test_emit_removes_wiki_ref_on_page_deletion` | delete action prunes the page | fixture with prior ref | sidecar entry no longer lists this page; if list goes empty, key is dropped |
| `test_emit_updates_refs_when_doc_keys_change` | edited page swaps cited keys | fixture: page changes `doc_key` from A→B | A loses ref; B gains ref; sidecar atomic |
| `test_emit_is_idempotent` | running emitter twice yields identical sidecar | fixture | second invocation produces zero dirty writes (mtime/hash compare) |
| `test_emit_handles_concurrent_writes` | two emitter invocations serialize via file lock | fork two processes | sidecar contains both updates; no lost write |
| `test_emit_ignores_slug_style_sources` | legacy `sources: [dnv-rp-b401]` is not materialized | fixture | no sidecar mutation; warning logged with page path |
| `test_emit_ignores_bare_hex_doc_key` | bare-hex citation logs warning, skips | fixture: `doc_key: abc123…` (no prefix) | no mutation; warning logged |
| `test_emit_keeps_md5_separate_from_sha256` | namespaces are not joined | fixture: same hex under `md5:` and `sha256:` | two distinct sidecar entries |
| `test_emit_doc_key_with_no_registry_match` | wiki cites a `doc_key` not in `index.jsonl` | fixture: orphan `doc_key` | sidecar still records the back-link; warning surfaced; no error |
| `test_ledger_projection_skips_rows_without_doc_key` | ledger projection is gated on row-level `doc_key` | ledger fixture with mixed rows | only `doc_key`-bearing rows gain `wiki_refs:` |
| `test_reverse_lookup_returns_all_citing_pages` | CLI returns sorted, deduped list | fixture with 3 pages citing same `doc_key` | 3 paths, sorted lexicographically |
| `test_reverse_lookup_no_hits_exits_3` | unknown `doc_key` returns exit 3 | `sha256:0000…` | exit 3, empty stdout |
| `test_reverse_lookup_malformed_key_exits_2` | malformed input | `xyz123` | exit 2, error on stderr |
| `test_reverse_lookup_json_output` | `--json` returns parseable JSON | fixture | `json.loads(stdout)` succeeds; shape matches `doc-key-lookup.py` convention |
| `test_backfill_dry_run_writes_nothing` | `--dry-run` prints summary, no file changes | fixture | sidecar file unchanged (hash compare) |
| `test_backfill_bounded_by_limit` | `--limit 5` stops after 5 pages | fixture with 20 pages | exactly 5 processed; report records visited=5, total_in_domain=20 |
| `test_backfill_unbounded_only_with_explicit_zero` | `--limit 0` required for unbounded | default invocation on 30-page fixture | default runs at most 500; only `--limit 0` triggers full sweep |
| `test_backfill_report_has_counts` | report written with all telemetry | fixture | `docs/reports/wiki-refs-backfill-*.md` contains `visited`, `added_refs`, `slug_only_skipped`, `non_canonical_skipped`, `pages_with_orphan_doc_key` |
| `test_deterministic_order_in_sidecar` | sidecar JSONL is stable across runs | fixture | byte-identical output between two backfills |
| `test_truthfulness_under_rename` | wiki page renamed → old path removed, new path added | fixture | sidecar reflects new path; no dangling old path |

All tests run via `uv run pytest scripts/knowledge/tests/test_wiki_refs.py -v`. Full regression: `uv run pytest scripts/knowledge/tests/ -v`.

---

## Acceptance Criteria

Mirroring the issue body's given/when/then style:

- [ ] **Given** a canonical `sha256:` `doc_key`, **when** an operator runs `uv run scripts/knowledge/wiki_refs_reverse_lookup.py <doc_key>`, **then** all citing wiki pages are returned (one per line, lexicographically sorted) with exit 0, without invoking grep.
- [ ] **Given** a wiki page that adds, edits, or removes a canonical `doc_key`, **when** `llm_wiki.py` ingest/update/delete runs, **then** the L2 sidecar is updated to reflect the new citation set; covered by `test_emit_*` tests.
- [ ] **Given** the current 19k-page marine-engineering wiki, **when** an operator invokes the bounded backfill `uv run scripts/knowledge/backfill_wiki_refs.py --domains marine-engineering --limit 500`, **then** at most 500 pages are processed, a report is written to `docs/reports/wiki-refs-backfill-<date>.md`, and the operation completes in under one wall-clock minute on the reference machine; full-domain sweep requires `--limit 0`.
- [ ] **Given** the issue's "at least one L2 surface stores `wiki_refs` in a durable/queryable way" requirement, **then** `data/document-index/wiki-refs-index.jsonl` is created and stores the back-link list keyed by `doc_key`. Secondary projection to `standards-transfer-ledger.yaml` rows is exercised by tests for `doc_key`-bearing rows; current-state ledger rows without `doc_key` are documented as a #2362 follow-on.
- [ ] **Given** the runbook requirement, **then** `docs/document-intelligence/wiki-refs-reverse-lookup.md` documents (a) the L3→L2 back-link rule, (b) the slug-style carve-out, (c) the sources-deny-list per `.claude/rules/calc-citation-contract.md`, (d) the #2360 / #2362 upstream dependencies, and (e) the operational runbook for backfill cadence.
- [ ] All new tests pass: `uv run pytest scripts/knowledge/tests/test_wiki_refs.py -v`.
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` passes.
- [ ] Review artifacts present at `scripts/review/results/2026-04-26-plan-2363-{claude,codex,gemini}.md` with non-`MAJOR` final verdicts.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (cross-review dispatch follows plan promotion from `/tmp/overnight-plans/` to `docs/plans/`).

Revisions made vs. prior plan (`2026-04-23-issue-2363-wiki-refs-reverse-lookup.md`):
- Replaced `registry.yaml` (aggregate-stats) with `index.jsonl`-aligned `wiki-refs-index.jsonl` sidecar as the primary L2 write target.
- Hard-coupled the plan to `#2360` (wiki frontmatter `doc_key`) and `#2362` (ledger `doc_key` back-population) — until those land, the v1 deliverable yields zero materialized rows; that is the truthful current state, not a plan defect.
- Added explicit concurrency test (`test_emit_handles_concurrent_writes`) and namespace-separation test (`test_emit_keeps_md5_separate_from_sha256`).
- Added orphan-`doc_key` semantics (sidecar records back-link even if no `index.jsonl` row exists; warning logged).
- Made `--limit 0` the only path to an unbounded backfill (default 500), reducing the 19k-page risk.

---

## Risks and Open Questions — adversarial pre-emption

- **Risk: "What if a wiki page cites a `doc_key` that doesn't exist in `index.jsonl`?"** The sidecar records the back-link unconditionally (`doc_key → page`). The reverse-lookup CLI returns the page; consumers who need source resolution still call `doc-key-lookup.py`. The backfill report counts these as `pages_with_orphan_doc_key` so the latent gap is visible. The runbook documents this as expected behavior, not a defect.

- **Risk: "How do we keep `wiki_refs` truthful under concurrent updates?"** Mitigations: (a) emitter acquires a repo-local file lock (`data/document-index/.locks/wiki-refs.lock`) before reading or mutating the sidecar; (b) write is atomic (temp file + rename); (c) backfill respects the same lock; (d) tests include a concurrent-write fixture that forks two emitter invocations. This does not solve the multi-machine case — see "Open Question" on git-merge race below.

- **Risk: "Is 19k pages a backfill liability?"** Yes if unbounded. Mitigations: (a) default `--limit 500`; (b) `--limit 0` (unbounded) is opt-in; (c) per-domain partitioning via `--domains`; (d) backfill report records wall-clock time and pages-per-second so cadence can be tuned; (e) runbook recommends weekly incremental passes after first full sweep; (f) since current marine-engineering pages overwhelmingly use slug-style `sources:` and lack `doc_key` (blocked by #2360), the *effective* first-run surface is near-zero, so the 19k risk is theoretical until #2360 lands.

- **Risk: "What if the indexer rewrites `index.jsonl` while the emitter is mid-write to the sidecar?"** The sidecar is a *separate file* from `index.jsonl`. The emitter never mutates `index.jsonl`. The sidecar lock is independent of the indexer's process-level coordination. Cross-file consistency (sidecar entry referencing a `doc_key` that the indexer simultaneously evicted) is bounded — the sidecar still resolves to the wiki page, which is the deliverable; consumers re-resolve to `index.jsonl` separately.

- **Risk: "What happens when a wiki page is deleted via `git rm` rather than via `llm_wiki.py`?"** The emitter's delete path is invoked only when `llm_wiki.py` mediates the deletion. For raw `git rm`, the sidecar will retain a stale entry until the next backfill detects the missing file. Mitigation: backfill includes a "stale entries" pass that drops sidecar entries whose `wiki_refs` paths no longer exist on disk. Test: `test_truthfulness_under_rename` covers this transition.

- **Risk: "The ledger projection is dead code today."** Acknowledged. The plan ships the projection logic and tests it against fixtures with `doc_key`-bearing rows; live mutation is gated on #2362 ledger back-population. The runbook explicitly notes the projection becomes useful only after #2362 lands.

- **Risk: "Plan describes proposed work as committed artifacts."** Per memory `feedback_plan_past_tense_artifact_claims.md`, this plan is written in future tense throughout. Verification: re-read the plan and confirm there are no claims like "the emitter has been added" or "the sidecar contains" — the plan only describes what *will* exist.

- **Risk: "Sources-deny-list violation."** Pages under `knowledge/wikis/*/wiki/sources/` are vendor-derivative per `.claude/rules/calc-citation-contract.md`. The emitter does NOT discriminate by path — it materializes any wiki page that cites a canonical `doc_key`. The runbook documents that **consumers** of the reverse lookup should prefer `wiki/standards/*` and `wiki/concepts/*` pages for citation traceability, since `wiki/sources/*` pages are derivative summaries. The deny-list is a citation-emission rule (digitalmodel calc modules), not a back-link-materialization rule; conflating the two would silently drop legitimate L3→L2 evidence.

- **Risk: "Mock vs. live invocation divergence."** Per memory `feedback_mock_vs_live_invocation_divergence.md`. The TDD fixtures use synthetic wiki pages and a synthetic mini-`index.jsonl`. Before plan-approval close-out, run a live invocation: pick one engineering-wiki page, manually add a `doc_key: sha256:<known-hex>` line, run `llm_wiki.py update` on it, verify the sidecar mutates as expected, then revert. Capture the live shell session in the runbook.

- **Open: scheduled vs. manual backfill.** Proposal: manual for v1; flag for user during approval. Once #2360 lands `doc_key` into the L3 required-set, scheduling weekly incremental backfills via the existing wiki-cron (`scripts/knowledge/wiki-ingest-cron.sh`) becomes attractive.

- **Open: pre-commit-hook integration.** Proposal: CLI-only for v1; flag for user. A hook would catch raw `git rm` deletions but adds latency to every commit; the periodic stale-entries pass is sufficient for v1.

- **Open: behavior when the L3 page declares `doc_key` but the `doc_key` form is invalid (e.g., truncated hex).** Proposal: log warning, skip emission, count under `non_canonical_skipped` in the report. Flag for user.

- **Open: do we materialize `wiki_refs` for the cross-wiki link index (`knowledge/wikis/cross-links.md`)?** That index is auto-generated and lacks `doc_key` citations. Proposal: out of scope; the cross-link index is keyword-similarity, not provenance. Flag for user.

- **Open: git-merge-race when two branches each touch the sidecar.** YAML/JSONL merge with disjoint `doc_key` keys is structurally clean; same-`doc_key` divergence requires conflict-marker resolution. Proposal: document in runbook; rebuild the sidecar from scratch via backfill if a merge produces conflicts. Flag for user.

---

## Complexity: T2

Adds one helper module + one CLI + one backfill tool + one runbook + ~20 TDD tests; modifies one existing module (`llm_wiki.py`) to call the helper; creates one new sidecar data file. No architecture/schema invention — `wiki_refs` is already defined in #2207 Section 4.2; this plan materializes it. Not T3 because there is no new data-model surface beyond a denormalized index of an already-contracted field, no migration of the 1M-row `index.jsonl`, and no public interface change to `doc-key-lookup.py`. The 19k-page domain is bounded by `--limit` rather than re-architected, so scale risk is operational not architectural.
