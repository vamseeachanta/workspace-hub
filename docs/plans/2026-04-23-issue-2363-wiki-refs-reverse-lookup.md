# Plan for #2363: feat(doc-intel): materialize wiki_refs reverse lookup from doc_key to citing wiki pages

> **Status:** draft (v2 — addresses r1 findings)
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2363
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2363-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` (1,465 lines) — canonical wiki CLI. Issue body explicitly names this as the location for emitting `wiki_refs`. `FRONTMATTER_REQUIRED = {"title","tags","added","last_updated"}` and `FRONTMATTER_RECOMMENDED = {"sources"}` govern the fields the reverse-lookup extractor will read.
- Found: `scripts/knowledge/doc-key-lookup.py` — existing `doc_key` lookup CLI; same helper approach will work for reverse direction.
- Found: `scripts/knowledge/tests/test_llm_wiki.py` — test harness pattern for wiki-side helpers.
- Found: `scripts/data/document-index/provenance.py` — L2 provenance merge/write semantics; the locus where `wiki_refs` values are materialized onto registry entries.
- Found: `data/document-index/standards-transfer-ledger.yaml` — one of the two L2 surfaces the issue names as first recipient of `wiki_refs`.
- Found: `data/document-index/registry.yaml` — second L2 surface named in issue scope.
- Gap: no `wiki_refs` field present in live registries — verified: `grep -rn "wiki_refs" data/ scripts/knowledge/ scripts/data/` returns empty.
- Gap: no reverse-lookup CLI (`doc_key → wiki pages`).

### Standards
Not applicable — this is a doc-intel data-pipeline concern, not an engineering standard.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/entities/anode.md` — sample wiki page with `sources: [dnv-rp-b401]` slug-style citation, NOT canonical `doc_key`. This is the dominant reality right now.
- `knowledge/wikis/marine-engineering/wiki/sources/001.md` — sample auto-generated source page; frontmatter has `slug`, `title`, `domain`, `ingested`, no `doc_key`.
- Domain counts (from `docs/document-intelligence/README.md` lines 28-33): engineering 77, marine-engineering 19,186, maritime-law 22, naval-architecture 45, personal 5. The issue body states "engineering 83, marine-engineering 19184, maritime-law 22, naval-architecture 45, personal 5" — slight drift reflects recent ingests; both counts illustrate the same scale reality.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — binding frontmatter schema for this domain.
- `knowledge/wikis/engineering/CLAUDE.md` — binding frontmatter schema for engineering domain.

### Documents consulted
- Issue body — deliverables: reverse-lookup CLI; `wiki_refs` emission in `llm_wiki.py`; add/update/delete tests; backfill path; at least one L2 surface stores `wiki_refs` durably.
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` Section 4.2 line 210: `wiki_refs | list[string] | Paths to LLM-wiki pages that cite this document as a source. Back-link field — see Section 4.3.` Section 4.3 (lines 212-225) is the binding contract: `wiki_refs` is an L2 back-link field populated from L3 citations.
- `docs/document-intelligence/intelligence-accessibility-map.md` lines 292-296: "no reverse lookup ... Until implemented, this is a search problem." This is the symptom that motivates #2363.
- Related issues (from issue body): #2205 parent operating model (OPEN), #2207 provenance contract (CLOSED), #2011/#2044/#2068 cross-link infrastructure, #2233/#2360/#2362 frontmatter/doc_key follow-ons (OPEN).

### Gaps identified
- No `wiki_refs` writer in any script.
- No reverse-lookup CLI.
- No backfill strategy for existing wiki pages (most of which use slug-style `sources:`, not canonical `doc_key`).
- No regression tests covering add/update/delete of citing wiki pages.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23):
- `#2363` — OPEN — "feat(doc-intel): materialize wiki_refs reverse lookup from doc_key to citing wiki pages"
- `#2205` — **CLOSED** — parent operating model (re-verified 2026-04-23 via `gh issue view 2205 --json state` → `CLOSED`). Supersedes earlier v1 assertion of OPEN.
- `#2360` — OPEN — doc_key in wiki required-set
- `#2362` — OPEN — back-population of doc_key on ledger
- `#2389` — OPEN — source_doc_key threading

**File existence** (2026-04-23):
- EXISTS: `scripts/knowledge/llm_wiki.py`, `scripts/knowledge/doc-key-lookup.py`, `scripts/knowledge/tests/test_llm_wiki.py`
- EXISTS: `data/document-index/standards-transfer-ledger.yaml`, `data/document-index/registry.yaml`
- EXISTS: `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (line 210 binds `wiki_refs` L2 ownership)
- MISSING (this plan creates): `scripts/knowledge/wiki_refs_reverse_lookup.py`, `scripts/knowledge/tests/test_wiki_refs_reverse_lookup.py`, `scripts/knowledge/backfill_wiki_refs.py`
- MISSING (in registries — this plan populates): `wiki_refs` field entries

**Line excerpts** (standards-codes-provenance-reuse-contract.md):
```
210:| `wiki_refs` | list[string] | Paths to LLM-wiki pages that cite this document as a source. Back-link field — see Section 4.3. | Materialized at L2; originates from L3 |
218:`wiki_refs` is a back-link field — it is **populated from** L3 (wiki pages emit their `doc_key` citations) and **materialized at** L2 (the registry keeps the list for reverse lookup).
```

**Gap proofs**:
- `grep -rn "wiki_refs" data/` → empty → confirms no materialized back-links live yet.
- `grep -rn "wiki_refs" scripts/knowledge/ scripts/data/` → empty → confirms no writer.

**Source count verification:** 4 distinct sources (issue body + provenance contract + accessibility map + live registry files) — minimum met.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2363-wiki-refs-reverse-lookup.md` |
| Forward emitter (materialize on ingest) | changes to `scripts/knowledge/llm_wiki.py` (new helper `emit_wiki_refs()`) |
| Reverse-lookup CLI | `scripts/knowledge/wiki_refs_reverse_lookup.py` |
| Backfill tool | `scripts/knowledge/backfill_wiki_refs.py` |
| Tests (emitter) | `scripts/knowledge/tests/test_llm_wiki.py` (extend) |
| Tests (reverse lookup + backfill) | `scripts/knowledge/tests/test_wiki_refs_reverse_lookup.py` |
| Registry surface 1 (L2) | `data/document-index/standards-transfer-ledger.yaml` (receives `wiki_refs:` entries on impacted rows) |
| Registry surface 2 (L2) | `data/document-index/registry.yaml` (receives `wiki_refs:` entries on impacted rows) |
| Runbook/doc | `docs/document-intelligence/wiki-refs-reverse-lookup.md` (how to use + L3→L2 back-link rule) |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2363-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2363-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2363-gemini.md` |

---

## Deliverable

A reverse-lookup path from `doc_key` → citing wiki pages, composed of (a) an emitter in `llm_wiki.py` that writes `wiki_refs:` back onto L2 registry rows when wiki pages are created/updated/deleted, (b) a query CLI `wiki_refs_reverse_lookup.py` that returns citing wiki pages for a given `doc_key` deterministically, (c) a bounded backfill tool, and (d) a documented runbook describing the L3→L2 materialization rule.

---

## Scope boundaries (explicit)

- **In scope:** canonical `sha256:` `doc_key` citations. Slug-style `sources:` frontmatter (e.g. `- dnv-rp-b401`) is NOT a canonical citation and is not materialized by this plan. A slug→`doc_key` resolver is tracked separately (soft dep: #2360/#2362).
- **In scope (first wave):** two L2 surfaces — `standards-transfer-ledger.yaml` and `registry.yaml`. Additional registries are follow-ups.
- **Out of scope:** creating missing `doc_key` entries on wiki pages (that is #2360's job).
- **Out of scope:** automatic wiki-page generation from `wiki_refs`.

### Acceptance-vs-scope reconciliation (v2)

v1's acceptance criterion "At least one L2 surface stores `wiki_refs`" is narrower than the scope bullet "two L2 surfaces". Reconciled in v2: **implementation will target both surfaces (standards-transfer-ledger.yaml AND registry.yaml) in the tooling PR; acceptance criterion is tightened to "both L2 surfaces" to match scope.** The "at least one" phrasing was a safety-margin hedge that is no longer needed — the forward emitter naturally touches both.

---

## Design Decisions (v2, added per r1)

### Side-cache design

The emitter's `read_cached_keys_for_page()` / `update_cached_keys_for_page()` helpers require a durable side-cache so that `old_keys − new_keys` diff is accurate across runs.

- **Path**: `data/document-index/wiki-refs-cache.jsonl` (git-tracked; one JSON line per wiki page).
- **Schema** (one record per line):
  ```json
  {"page_path": "knowledge/wikis/<domain>/wiki/<sub>/<slug>.md",
   "doc_keys": ["sha256:abc...", "sha256:def..."],
   "page_content_hash": "sha256:<hex>",
   "last_seen": "2026-04-23T12:34:56Z"}
  ```
- **Missing-cache semantics**: if `wiki-refs-cache.jsonl` is absent or a given page is not present in it, the emitter treats `old_keys = set()`. The `action="add"` path then adds every canonical `doc_key` found on the page. This matches backfill semantics (first-run-is-full-add) and means the cache is always repopulable from scratch by running the backfill tool once with `--limit None`.
- **Write semantics**: the cache is rewritten atomically (temp + rename) after each emitter invocation. Corruption recovery: delete the cache, run backfill with no limit.

### Locking mechanism

- **Library**: `portalocker` (PyPI — cross-platform advisory file locking, used elsewhere in the Python ecosystem for exactly this pattern). Pinned via `pyproject.toml` dependency row.
- **Semantics**: emitter acquires an exclusive lock on `<registry_path>.lock` (sibling sentinel file) before reading, mutating, and atomically writing the registry. Lock released in `finally`. Backfill uses the same lock so concurrent emitter + backfill are serialized.
- **Why portalocker and not `fcntl`**: portalocker works on Windows too, which is relevant for dev workflows on #2205-parent machines.

### Cross-registry atomicity strategy

The emitter writes to TWO L2 surfaces per emit call. Strict two-phase commit is overkill for YAML files; instead:

1. Lock surface A, mutate, atomic-write, release.
2. Lock surface B, mutate, atomic-write, release.
3. If step 2 fails after step 1 succeeds, surface A is now ahead of surface B. Recovery: emit a reconciliation warning to stderr with the page path and the doc_key(s) that made it only to surface A. Operator re-runs the emitter or the bounded backfill to re-align. This is acceptable because `wiki_refs` is a materialized derivative — the source of truth is the wiki frontmatter, so any drift is self-healing on the next emit for the same page.
4. Reconciliation is attestable: `backfill_wiki_refs.py --reconcile` re-reads all wiki pages and flags any `wiki_refs` entry in either registry that does not correspond to a live citation. Reported; not auto-deleted (human in the loop for deletions).

### YAML round-trip preservation

- **Library**: `ruamel.yaml` (not `PyYAML`). Reason: ruamel preserves comments, key ordering, and flow style across load→mutate→dump, which is required for registries that humans author and review via git diff.
- **Mode**: `YAML(typ="rt")` (round-trip) with `indent(mapping=2, sequence=4, offset=2)` to match existing file conventions. Smoke-tested: load `standards-transfer-ledger.yaml`, dump unchanged → git diff must be empty.
- Pinned via `pyproject.toml`.

### Exit codes (Unix convention, revised v2)

Per Unix convention (0=success; 1=generic failure; 2=usage/format error; conventions vary for "expected negative result"):

| Code | Meaning |
|---|---|
| 0 | Success AND at least one hit (for lookup), or no gaps (for --reconcile) |
| 1 | Gaps found during --reconcile (exit non-zero so CI can gate), OR runtime error |
| 2 | Malformed `doc_key` argument, missing required input, or usage error |

Note: v1 proposed `3 = no hits`. This is non-standard and breaks CI gating. v2 reverts to: lookup with zero hits returns exit 0 (no hits is not a FAILURE of the tool, it is a valid answer). If callers want to gate on hits, they pipe through `grep .` or check stdout length. This matches `grep`, which exits 0 on match, 1 on no-match, and 2 on error — but here "no hits" is a legitimate answer, not a tool failure, so we diverge deliberately.

### `--batch` mode for bulk ingestion

- **Flag**: `emit_wiki_refs()` CLI wrapper gains `--batch <file>` where `<file>` is a newline-delimited list of `<action>\t<page_path>` rows.
- **Semantics**: batch reads all rows first; groups mutations by registry; acquires each registry lock once; applies all grouped mutations; releases. This bounds lock contention to one acquire-release cycle per registry per batch, making nightly bulk re-ingest viable without lock storms.
- **Fallback**: if `--batch` fails mid-batch, the rows that succeeded are durable (atomic write); the rows that failed are printed to stderr so the operator can retry or inspect.

---

## Pseudocode

### Forward emitter (on wiki ingest/update/delete)

```
def emit_wiki_refs(wiki_page_path, action):  # action in {"add","update","delete"}
    fm = parse_frontmatter(wiki_page_path)
    old_keys = read_cached_keys_for_page(wiki_page_path)  # from a small side-cache index
    new_keys = extract_canonical_doc_keys(fm)             # only sha256:<hex>
    added   = new_keys - old_keys
    removed = old_keys - new_keys

    for registry_path in L2_REGISTRIES:
        registry = yaml_load(registry_path)
        dirty = False
        for doc_key in added:
            row = registry_row_for_doc_key(registry, doc_key)
            if row is not None:
                row.setdefault("wiki_refs", [])
                if repo_relative(wiki_page_path) not in row["wiki_refs"]:
                    row["wiki_refs"].append(repo_relative(wiki_page_path))
                    row["wiki_refs"].sort()  # deterministic output
                    dirty = True
        for doc_key in removed:
            row = registry_row_for_doc_key(registry, doc_key)
            if row is not None and "wiki_refs" in row:
                if repo_relative(wiki_page_path) in row["wiki_refs"]:
                    row["wiki_refs"].remove(repo_relative(wiki_page_path))
                    if not row["wiki_refs"]:
                        del row["wiki_refs"]
                    dirty = True
        if dirty:
            atomic_yaml_write(registry_path, registry)

    update_cached_keys_for_page(wiki_page_path, new_keys)
```

### Reverse-lookup CLI

```
def lookup(doc_key):
    hits = []
    for registry_path in L2_REGISTRIES:
        row = find_row(registry_path, doc_key)
        if row and "wiki_refs" in row:
            for p in row["wiki_refs"]:
                hits.append((registry_path, p))
    return sorted(set(hits))
```

Exit codes (Unix convention — see Design Decisions above): 0 on success (including "no hits"); 1 on runtime error or gaps-found during `--reconcile`; 2 on malformed `doc_key` / usage error.

### Bounded backfill

```
def backfill(domains=None, limit=None):
    # Walk wiki pages; for each page, run emit_wiki_refs(..., action="add") with empty old_keys.
    # Limit bounded by --limit N and --domains for cost control.
    # At end, write a report docs/reports/wiki-refs-backfill-<date>.md with counts.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/knowledge/llm_wiki.py` | add `emit_wiki_refs()` helper + invoke from ingest/update/delete paths; import `portalocker` + `ruamel.yaml` |
| Create | `scripts/knowledge/wiki_refs_reverse_lookup.py` | query CLI (exit codes per Design Decisions) |
| Create | `scripts/knowledge/backfill_wiki_refs.py` | bounded backfill tool; supports `--batch <file>` and `--reconcile` |
| Create | `data/document-index/wiki-refs-cache.jsonl` | side-cache; initial file empty or first-run-populated; git-tracked |
| Modify | `pyproject.toml` | pin `portalocker` (advisory file locking) and `ruamel.yaml` (YAML round-trip) |
| Modify | `scripts/knowledge/tests/test_llm_wiki.py` | tests for emitter add/update/delete semantics |
| Create | `scripts/knowledge/tests/test_wiki_refs_reverse_lookup.py` | tests for CLI and backfill |
| Create | `scripts/knowledge/tests/fixtures/wiki-refs/` | synthetic registry + wiki pages |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | receives `wiki_refs:` entries (populated by backfill) |
| Modify | `data/document-index/registry.yaml` | receives `wiki_refs:` entries (populated by backfill, bounded) |
| Create | `docs/document-intelligence/wiki-refs-reverse-lookup.md` | runbook + L3→L2 back-link rule |
| Update | `docs/plans/README.md` | add plan row |

Registry mutations in `data/document-index/*.yaml` are produced by the backfill tool, reviewed, and committed as a separate PR from the tooling PR so review surface is clean.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_emit_adds_wiki_ref_on_page_creation` | new wiki page → registry row gains ref | fixture: page with `doc_key: sha256:abc...` | row `wiki_refs` includes the page path |
| `test_emit_removes_wiki_ref_on_page_deletion` | deleted page → registry row loses ref | fixture with existing ref | row `wiki_refs` loses the page path; empty list dropped |
| `test_emit_updates_refs_when_doc_keys_change` | edited page swaps cited `doc_key` | fixture: page changes `doc_key` from A to B | row A loses ref; row B gains ref |
| `test_emit_is_idempotent` | running emitter twice yields same registry | fixture | second invocation produces zero dirty writes |
| `test_emit_ignores_slug_style_sources` | legacy `sources: [dnv-rp-b401]` is not materialized | fixture | no registry mutation |
| `test_emit_ignores_non_canonical_doc_key` | bare hex or `md5:` citation ignored | fixture | no registry mutation; warning logged |
| `test_reverse_lookup_returns_all_citing_pages` | CLI returns sorted, deduped list | fixture with 3 pages citing same `doc_key` | 3 paths, sorted |
| `test_reverse_lookup_no_hits_exits_0` | unknown `doc_key` returns exit 0 (no-hits is a valid answer) | `sha256:0000...` | exit 0, empty stdout |
| `test_reverse_lookup_malformed_key_exits_2` | `xyz123` malformed input | — | exit 2, error on stderr |
| `test_reconcile_exits_1_on_gaps` | `--reconcile` detects stale `wiki_refs` rows | fixture with registry pointing at deleted page | exit 1; warning printed |
| `test_batch_mode_groups_locks` | `--batch` acquires each registry lock once | fixture with 10 mixed-action rows | single lock acquire per registry verified via fake-lock instrumentation |
| `test_portalocker_serializes_concurrent_writers` | two emitter processes against same registry | fork twice; assert both complete without corruption | registry YAML round-trips cleanly afterwards |
| `test_ruamel_roundtrip_preserves_comments` | load→dump of registry preserves comments + key order | fixture registry with comments | `diff` between load→dump output and original is empty |
| `test_missing_side_cache_triggers_full_add` | cache absent; emitter treats old_keys=∅ | delete cache fixture | every canonical doc_key on page becomes an added ref |
| `test_backfill_dry_run_writes_nothing` | `--dry-run` prints summary, no file changes | fixture | registry unchanged |
| `test_backfill_bounded_by_limit` | `--limit 5` stops after 5 pages | fixture with 20 pages | exactly 5 processed |
| `test_backfill_report_has_counts` | report written with `added_refs`, `pages_visited` | fixture | `docs/reports/wiki-refs-backfill-*.md` present |
| `test_deterministic_order_in_registry` | `wiki_refs` list is sorted | fixture | list is sorted lexicographically |

All tests run via `uv run pytest scripts/knowledge/tests/ -v`.

---

## Acceptance Criteria

- [ ] Given a canonical `sha256:` `doc_key`, `uv run scripts/knowledge/wiki_refs_reverse_lookup.py <doc_key>` returns all citing wiki pages (one per line, sorted) without any grep
- [ ] Back-links stay correct when a wiki page changes cited sources (add/update/delete) — covered by tests
- [ ] Pre-existing wiki pages have a bounded backfill path via `scripts/knowledge/backfill_wiki_refs.py --domains <name> --limit <N>`; default invocation is bounded, not unbounded
- [ ] BOTH L2 surfaces (`standards-transfer-ledger.yaml` AND `registry.yaml`) store `wiki_refs` as a durable sorted list of repo-relative page paths (tightened in v2 to match scope)
- [ ] `portalocker` and `ruamel.yaml` are pinned in `pyproject.toml`; `uv run python -c "import portalocker, ruamel.yaml"` succeeds
- [ ] Side-cache at `data/document-index/wiki-refs-cache.jsonl` is created/updated by the emitter and is repopulable from scratch via `--reconcile`
- [ ] `docs/document-intelligence/wiki-refs-reverse-lookup.md` documents the L3→L2 back-link rule and the slug-style-out-of-scope carve-out
- [ ] All tests pass: `uv run pytest scripts/knowledge/tests/test_wiki_refs_reverse_lookup.py -v`
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` passes
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (r1 cross-review dispatch follows plan push)

Revisions made based on review: none yet.

---

## Risks and Open Questions

- **Risk:** Most current wiki pages use slug-style `sources:`, not canonical `doc_key`. First-pass backfill will therefore materialize very few `wiki_refs`. Mitigation: plan explicitly carves this out of scope and references #2360 as the upstream fix. Backfill report will count slug-only pages so the latent backlog is visible.
- **Risk:** Two processes writing the same `registry.yaml` concurrently (emitter + backfill + any other tool) could race. Mitigation: emitter uses atomic write (temp + rename) and a repo-local file-lock alongside the target YAML. Documented in the runbook.
- **Risk:** `marine-engineering` has 19K+ pages. Even a small fraction citing canonical `doc_key` could produce large `wiki_refs` lists. Mitigation: lists are sorted and deduplicated; YAML output size is monitored in the backfill report.
- **Risk:** Registry PR review surface could be noisy. Mitigation: tooling PR and data PR are separated; data PR is reviewed by eyeballing the report counts plus YAML line-diff spot-checks.
- **Open:** Should backfill be added as a scheduled task (e.g., weekly), or remain manual for v1? Proposal: manual for v1; flag for user.
- **Open:** Should the emitter hook into a Git hook (pre-commit) as well, or stay CLI-invoked only? Proposal: CLI-invoked only for v1; flag for user.
- **Open:** When `doc_key` is present in frontmatter but the L2 registry has no matching row, should the emitter (a) skip silently, (b) log a warning, or (c) create a stub row? Proposal: (b) — log and skip. Flag for user during approval.

---

## Complexity: T2

Adds one helper function to an existing module, one new CLI, one new backfill tool, one runbook, multiple TDD tests, and touches two L2 registry YAMLs with tightly bounded mutations. Not T3 because no architecture/schema change — `wiki_refs` is already defined in the provenance contract (Section 4.2); this plan just materializes it.
