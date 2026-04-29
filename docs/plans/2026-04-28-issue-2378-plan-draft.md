# Plan for #2378: feat(knowledge): chunk and paginate the canonical marine-engineering wiki index

> **Status:** PLAN DRAFT — NOT APPROVED
> **Complexity:** T2
> **Date:** 2026-04-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2378
> **Review artifacts:** scripts/review/results/2026-04-28-plan-2378-claude-feed3.md | ...-codex.md | ...-gemini.md (pending)
> **Prior draft:** `docs/plans/2026-04-26-issue-2378-marine-wiki-chunked-index.md` (this file supersedes with refreshed evidence)

---

## Resource Intelligence Summary

<!-- RETRIEVAL CONTRACT (per #2208):
     Issue class: Knowledge/Intelligence (labels: cat:documentation, domain:knowledge-management)
     Required bundles: Universal + Knowledge/Intelligence
     Sources consulted: 10 (minimum 3 required) -->

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` line 1147 `def _update_index_md(` — current writer that appends new source rows directly to `wiki/index.md` and updates `page_count` / `source_count` / `last_updated` frontmatter. This is the interception point: the chunked-writer must replace this in-place append.
- Found: `scripts/knowledge/llm_wiki.py` line 839 `def _check_index_consistency(` — lint hook that checks `index.md` existence and frontmatter validity only (22-line function: verifies file exists and starts with `---`). Does NOT do orphan detection or source enumeration. No modification needed for chunking.
- Found: `scripts/knowledge/llm_wiki.py` — `cmd_batch_ingest()` defined at line 1248; it calls `_update_index_md()` via `_flush_batch()` at line 1322. The regeneration trigger lives at the call site.
- Found: `scripts/knowledge/wiki-ingest-cron.sh` — nightly ingest for the **engineering** wiki only (hardcoded `WIKI_ROOT="${REPO_ROOT}/knowledge/wikis/engineering"` at line 23). No existing nightly cron for marine-engineering. Chunker invocation for marine-engineering must be defined as a new cron entry or standalone script.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` (`wiki-ingest-nightly`) — runs `wiki-ingest-cron.sh` with no domain parameter; only the engineering wiki is covered. Marine-engineering chunking requires a new scheduled entry or standalone trigger.
- Found (sibling plan): `docs/plans/2026-04-23-issue-2368-faceted-portal-pages.md` — companion plan introducing portal pages. Sets precedent for "scripted, idempotent, committed-but-regenerated" wiki artifacts. Chunking adopts the same idempotency contract.
- Gap: no chunk/pagination subcommand or standalone script exists. Verified: `ls scripts/knowledge/ | grep -i -E 'chunk|paginate|page-'` returns empty (2026-04-28).
- Gap: no chunk-page filename convention, no `next`/`prev`/jump-link pattern, no chunk frontmatter schema in any of the five domain wikis.

### Standards
Not applicable — `cat:documentation, domain:knowledge-management` issue. No engineering standards exercised.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/index.md` — verified 21,622 lines (`wc -l`, 2026-04-28). Frontmatter: `page_count: 19197`, `source_count: 19166`, `last_updated: 2026-04-28`. Sources section dominates.
- `knowledge/wikis/marine-engineering/wiki/sources/` — verified 19,166 source pages (`ls | wc -l`, 2026-04-28).
- `knowledge/wikis/marine-engineering/wiki/concepts/` — 14 files.
- `knowledge/wikis/marine-engineering/wiki/entities/` — 15 files.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — domain frontmatter contract: `title`, `tags`, `added`, `last_updated` required. Chunk pages must satisfy this schema or be explicitly exempt as derived artifacts.
- Other domain indexes (cross-checked): `engineering/wiki/index.md` 121 lines, `naval-architecture/wiki/index.md` 77 lines, `maritime-law/wiki/index.md` 54 lines, `personal/wiki/index.md` 39 lines. Marine-engineering is the sole domain exceeding any chunking threshold.

### Documents consulted
- Issue [#2378](https://github.com/vamseeachanta/workspace-hub/issues/2378) body — explicit requirements: keep one canonical `index.md`, generate bounded chunk pages for Sources, add stable `next`/`prev`/jump links, scripted regeneration, reusable policy.
- Parent [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) — operating model for llm-wiki; chunking is an L4 entry-point concern.
- Sibling [#2368](https://github.com/vamseeachanta/workspace-hub/issues/2368) (faceted portal pages) — **currently `status:plan-approved`, `status:working`, `agent:codex`** (verified 2026-04-28). Portal work is in flight. `portal.md` does not yet exist in repo. Chunking and portal must coexist on the top-level page.
- Sibling [#2372](https://github.com/vamseeachanta/workspace-hub/issues/2372) (source-title aliasing) — OPEN. Title aliasing changes content of source rows, not count/layout. Chunker consumes whatever titles exist.
- Sibling [#2366](https://github.com/vamseeachanta/workspace-hub/issues/2366) (strengthening scorecard) — OPEN. Downstream consumer.
- `docs/document-intelligence/intelligence-accessibility-map.md` — explicitly flags marine-engineering "19K pages with no curated entry beyond the index" as the L3 weakness #2378 closes.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — L4 entry-point surface owned by index/portal/chunk pages.
- Prior draft: `docs/plans/2026-04-26-issue-2378-marine-wiki-chunked-index.md` — comprehensive T2 plan, status:draft, adversarial review PENDING. Line references are stale (14-line shift in `llm_wiki.py`; +4 sources since then).

### Gaps identified
- No chunk generator script. Must build.
- No chunk-page filename or layout convention. Must define and document.
- No chunking-key decision. Must select (alphabetical-by-slug recommended; see Pseudocode).
- No `next`/`prev`/jump-link rendering convention. Must define.
- No regeneration-trigger contract. Must define.
- No reusable-policy doc for "future large wikis". Must author.
- No test for "chunked layout preserves all existing source-page hyperlinks". Must add.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-28T04:30:00Z via `gh issue view --json`):
- `#2378` — OPEN — "feat(knowledge): chunk and paginate the canonical marine-engineering wiki index"
- `#2205` — CLOSED — parent operating model
- `#2368` — OPEN, `status:plan-approved`, `status:working`, `agent:codex` — sibling faceted portal (implementation in flight)
- `#2372` — OPEN — sibling source-title aliasing
- `#2366` — OPEN — strengthening scorecard (downstream consumer)

**File existence** (verified 2026-04-28):
- EXISTS: `knowledge/wikis/marine-engineering/wiki/index.md` (21,622 lines)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/sources/` (19,166 *.md files)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/concepts/` (14 files)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/entities/` (15 files)
- EXISTS: `knowledge/wikis/marine-engineering/CLAUDE.md`
- EXISTS: `scripts/knowledge/llm_wiki.py` (with `_update_index_md` line 1147, `_check_index_consistency` line 839)
- EXISTS: `scripts/knowledge/tests/test_llm_wiki.py`
- EXISTS: `scripts/knowledge/wiki-ingest-cron.sh`
- EXISTS: `config/scheduled-tasks/schedule-tasks.yaml`
- EXISTS: `docs/plans/2026-04-23-issue-2368-faceted-portal-pages.md`
- MISSING (new — portal.md): `knowledge/wikis/marine-engineering/wiki/portal.md` — #2368 in flight, not yet landed
- MISSING (this plan creates): `scripts/knowledge/chunk_wiki_index.py`
- MISSING (this plan creates): `scripts/knowledge/tests/test_chunk_wiki_index.py`
- MISSING (this plan creates): `knowledge/wikis/marine-engineering/wiki/sources/_chunks/` (directory)
- MISSING (this plan creates): `knowledge/wikis/marine-engineering/wiki/sources/_chunks/index.md` (chunk manifest)
- MISSING (this plan creates): `docs/document-intelligence/llm-wiki-chunking-policy.md`

**Gap proofs**:
- `ls scripts/knowledge/ | grep -iE 'chunk|paginate|page-'` → empty → no prior chunk script (2026-04-28)
- `find knowledge/wikis -name '_chunks' -type d` → empty → no chunk directory exists (2026-04-28)

**Source count verification:** 10 distinct sources consulted: (1) issue #2378 body, (2) parent #2205, (3) sibling #2368 plan + live state, (4) #2372 state, (5) #2366 state, (6) intelligence-accessibility-map.md, (7) llm-wiki operating model, (8) `llm_wiki.py` codebase, (9) live `index.md`/sources/ tree, (10) prior draft plan `2026-04-26`. Minimum 3 — exceeded.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-28-issue-2378-plan-draft.md` |
| Implementation | `scripts/knowledge/chunk_wiki_index.py` |
| Tests | `scripts/knowledge/tests/test_chunk_wiki_index.py` |
| Chunk manifest | `knowledge/wikis/marine-engineering/wiki/sources/_chunks/index.md` |
| Chunk pages (generated) | `knowledge/wikis/marine-engineering/wiki/sources/_chunks/sources-<rangelo>--<rangehi>.md` |
| Chunking policy doc | `docs/document-intelligence/llm-wiki-chunking-policy.md` |
| Plan review — Claude | `scripts/review/results/2026-04-28-plan-2378-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-28-plan-2378-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-28-plan-2378-gemini.md` |
| Top-level index (modified) | `knowledge/wikis/marine-engineering/wiki/index.md` |
| Chunk cron script | `scripts/knowledge/wiki-chunk-cron.sh` |
| Chunk scheduled task | `config/scheduled-tasks/schedule-tasks.yaml` (`wiki-chunk-nightly` entry) |
| Hooked writer | `scripts/knowledge/llm_wiki.py` (`_update_index_md` at line 1147) |

---

## Deliverable

A `scripts/knowledge/chunk_wiki_index.py` generator (plus integration into `llm_wiki.py:_update_index_md`) that replaces the in-line 21K-row Sources table inside `knowledge/wikis/marine-engineering/wiki/index.md` with (a) a bounded chunk manifest summarising N chunk pages, and (b) chunk pages under `wiki/sources/_chunks/` with stable `prev`/`next`/`up` navigation, generated reproducibly and re-runnable — accompanied by a reusable chunking-policy doc that other oversized wikis can later adopt without code changes.

---

## Pseudocode

```
# chunk_wiki_index.py — main entry

CONSTANTS:
    DEFAULT_CHUNK_SIZE = 500              # source rows per chunk page
    DEFAULT_TRIGGER_THRESHOLD = 2_000     # chunk only if source count >= this
    CHUNK_KEY = "alphabetical_by_slug"    # rationale in design-choice table below
    CHUNK_DIRNAME = "_chunks"             # underscore-prefixed: lint-ignored

function chunk_wiki_index(domain, chunk_size=DEFAULT_CHUNK_SIZE, threshold=DEFAULT_TRIGGER_THRESHOLD, dry_run=False):
    wiki_root  = REPO_ROOT / "knowledge" / "wikis" / domain / "wiki"
    sources_dir = wiki_root / "sources"
    chunks_dir = sources_dir / CHUNK_DIRNAME
    index_md   = wiki_root / "index.md"

    # NOTE: glob("*.md") matches only immediate children — excludes _chunks/*.md by construction.
    # Guard test `test_source_count_excludes_chunks` prevents accidental future rglob regression.
    sources = sorted(sources_dir.glob("*.md"), key=lambda p: p.stem.lower())
    if len(sources) < threshold and not force:
        print(f"{domain}: {len(sources)} sources < threshold {threshold}; skipping")
        return 0

    chunks = partition(sources, size=chunk_size)   # alphabetical contiguous ranges
    manifest_rows = []
    for i, chunk in enumerate(chunks):
        lo, hi = chunk[0].stem, chunk[-1].stem
        chunk_path = chunks_dir / f"sources-{slugify(lo)}--{slugify(hi)}.md"
        prev_link = chunk_filename(chunks, i-1) if i > 0 else None
        next_link = chunk_filename(chunks, i+1) if i < len(chunks)-1 else None
        rendered = render_chunk(
            domain=domain, page_index=i+1, page_count=len(chunks),
            range_lo=lo, range_hi=hi,
            entries=[parse_frontmatter_lite(p) for p in chunk],
            prev=prev_link, next=next_link, up="../../index.md",
            generated_at=utcnow(),
        )
        write_atomic(chunk_path, rendered)        # tempfile + rename
        manifest_rows.append((i+1, lo, hi, len(chunk), chunk_path.name))

    manifest_md = render_manifest(domain, chunks, generated_at=utcnow())
    write_atomic(chunks_dir / "index.md", manifest_md)

    rewrite_top_level_index_sources_section(index_md, manifest_rows, total=len(sources))
    return {"chunks": len(chunks), "rows_total": len(sources)}


function rewrite_top_level_index_sources_section(index_md, manifest_rows, total):
    # NON-DESTRUCTIVE for Entities / Concepts / Comparisons / Topics Covered.
    # Only the "## Sources" block is replaced.
    text = read(index_md)
    new_block = render_sources_summary(manifest_rows, total)
    text = replace_block_between("## Sources", next_h2_or_eof, with=new_block)
    text = update_frontmatter(text, last_updated=utcnow_date())
    write_atomic(index_md, text)


function render_sources_summary(manifest_rows, total):
    return f"""
## Sources

> **{total:,} sources are paginated.** See the [chunk manifest](sources/_chunks/index.md).
> Per-letter range chunks of ~{CHUNK_SIZE} entries. Existing `sources/<slug>.md` links unchanged.

| # | Range | Entries | Page |
|---|---|---|---|
{rows as: i | lo--hi | count | [link](sources/_chunks/<file>.md)}

{"**Curated facets:** see [portal.md](portal.md) (companion per #2368)." if portal_path.exists() else "**Curated facets:** portal page pending ([#2368](https://github.com/vamseeachanta/workspace-hub/issues/2368))."}
"""


# Hook into llm_wiki.py:_update_index_md for chunk-aware live ingest:
function _update_index_md_chunked_aware(index_path, new_entries, domain, now):
    if domain has chunking active (chunks/index.md exists):
        # 1. write sources/<slug>.md page (existing, untouched)
        # 2. append rows to LAST chunk page (or open new one if size > CHUNK_SIZE)
        # 3. update chunks/index.md manifest counts
        # 4. update top-level index.md frontmatter only (page_count/source_count/last_updated)
        # 5. do NOT append rows to top-level ## Sources section
    else:
        legacy path (current _update_index_md behavior)
```

**Chunking-key rationale (load-bearing design choice):**

| Candidate | Pros | Cons | Verdict |
|---|---|---|---|
| **Alphabetical-by-slug** (chosen) | Stable across ingests; deterministic regeneration; predictable chunk identities so links stay valid; humans/agents can jump by first letter | Bias toward early letters when ingest is uneven | **Selected** — stability dominates |
| Topic / tag | Aligns with portal facets (#2368) | ~95% of source pages have empty `tags: []`; would create one giant "untagged" bucket | Rejected |
| By-size (rolling-bucket) | Even sizes | Contents shift with every ingest → link instability | Rejected |
| By-source-type | Coarse split | Only 5-7 types; each still 1K-5K rows | Rejected for v1 |

Defaults: `CHUNK_SIZE=500` yields ~39 chunks for 19,166 sources. `THRESHOLD=2000` ensures the four sub-100-line sibling indexes are never auto-chunked.

**Idempotency contract:** re-running the chunker against the same `sources/` tree produces byte-identical chunk pages except for `last_generated:` frontmatter lines. Enforced by a "run twice, diff" test.

**Link-preservation contract:** existing in-repo links `sources/<slug>.md` and `[[<slug>]]` remain valid. Chunker does NOT move source pages; it only adds `sources/_chunks/`. Note: `_check_index_consistency` (line 839) only checks `index.md` existence and frontmatter prefix — it has no orphan-detection logic, so chunk pages are invisible to it and require no lint modification.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/chunk_wiki_index.py` | Main implementation (CLI + library functions) |
| Create | `scripts/knowledge/tests/test_chunk_wiki_index.py` | TDD test suite |
| Create | `knowledge/wikis/marine-engineering/wiki/sources/_chunks/index.md` | Chunk manifest (generated, committed) |
| Create | `knowledge/wikis/marine-engineering/wiki/sources/_chunks/sources-*.md` | ~39 chunk pages (generated, committed) |
| Create | `docs/document-intelligence/llm-wiki-chunking-policy.md` | Reusable policy doc |
| Modify | `knowledge/wikis/marine-engineering/wiki/index.md` | Replace 21K-line Sources table with bounded chunk-manifest summary |
| Modify | `scripts/knowledge/llm_wiki.py` (`_update_index_md` line 1147) | Route Sources-row appends to last chunk when chunking active |
| Create | `scripts/knowledge/wiki-chunk-cron.sh` | Standalone cron script that invokes `chunk_wiki_index.py` for domains exceeding threshold (marine-engineering initially). **User decision:** alternatively, `wiki-ingest-cron.sh` could be generalized to accept `--wiki <domain>` — record as explicit scope choice, not an implementation assumption. |
| Create | `config/scheduled-tasks/schedule-tasks.yaml` entry `wiki-chunk-nightly` | New scheduled-task entry invoking `wiki-chunk-cron.sh`; does not modify the existing `wiki-ingest-nightly` engineering task |
| Update | `docs/plans/README.md` | Add this plan's row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_skips_domain_below_threshold` | Small wikis (engineering, 121 lines) not chunked | `domain=engineering` | exit 0, `_chunks/` not created |
| `test_chunks_marine_engineering_count` | Marine-engineering chunks into ~39 pages | fixture mirroring real source count | manifest has N rows; `_chunks/sources-*.md` count == N |
| `test_alphabetical_partition_stable` | Re-running with same inputs yields same chunk filenames | run twice on fixture | filenames + row order identical |
| `test_idempotent_byte_identical` | Re-run produces byte-identical files except `last_generated:` line | run twice, diff | only `last_generated` lines differ |
| `test_top_level_index_sources_replaced` | After run, `index.md` Sources section <= ~80 lines | initial 21K-line index | new index < 500 lines total; manifest link present |
| `test_top_level_other_sections_unchanged` | Entities / Concepts / Comparisons sections byte-identical pre vs post | run on fixture | diff outside `## Sources` block is empty |
| `test_existing_source_links_unbroken` | Every `[[<slug>]]` and `sources/<slug>.md` ref resolves after chunking | scan all *.md under `wiki/` | each target file still exists |
| `test_chunk_page_has_prev_next_up` | Middle chunk has correct prev (N-1), next (N+1), up links | inspect any middle chunk | links match expected slugs |
| `test_first_chunk_no_prev` | First chunk has only next + up | inspect chunk 1 | `prev:` absent or null |
| `test_last_chunk_no_next` | Last chunk has only prev + up | inspect chunk N | `next:` absent or null |
| `test_lint_passes_post_chunk` | `llm_wiki.py lint --wiki marine-engineering` returns 0 with chunks | run lint after chunker | exit code 0 |
| `test_live_ingest_appends_to_last_chunk` | New rows go to last chunk, not top-level index | simulate ingest of 3 new sources | last chunk row count +3; top-level unchanged except frontmatter |
| `test_live_ingest_rolls_to_new_chunk` | When last chunk fills past CHUNK_SIZE, new chunk created | simulate overflow ingest | new chunk file + manifest row |
| `test_portal_link_conditional` | Portal link emitted only when `portal.md` exists | Run with and without `portal.md` present | Link present when file exists; pending note emitted when absent |
| `test_source_count_excludes_chunks` | `source_count` frontmatter does not include `_chunks/*.md` files | Run chunker, read frontmatter | `source_count` == count of `sources/*.md` only (excludes `_chunks/`). Guards against future `rglob` regression. |
| `test_threshold_cli_override` | CLI overrides allow chunking small fixture domains | `--threshold 100 --chunk-size 50` | chunks created for small fixture |

All tests run via `uv run pytest scripts/knowledge/tests/test_chunk_wiki_index.py -v`.

---

## Acceptance Criteria

- [ ] `scripts/knowledge/chunk_wiki_index.py` exists, invoked as `uv run scripts/knowledge/chunk_wiki_index.py marine-engineering`
- [ ] All new tests pass: `uv run pytest scripts/knowledge/tests/test_chunk_wiki_index.py -v`
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` passes
- [ ] `knowledge/wikis/marine-engineering/wiki/index.md` is < 500 total lines after chunking (down from 21,622) AND remains the sole canonical entry point
- [ ] `knowledge/wikis/marine-engineering/wiki/sources/_chunks/index.md` exists and lists all chunk pages with row counts and ranges
- [ ] All chunk pages have `prev`/`next`/`up` links forming a valid chain (verified by test)
- [ ] Lint passes: `uv run scripts/knowledge/llm_wiki.py lint --wiki marine-engineering` exits 0
- [ ] No existing `sources/<slug>.md` link in any *.md under `knowledge/wikis/marine-engineering/wiki/` is broken (verified by test)
- [ ] `docs/document-intelligence/llm-wiki-chunking-policy.md` documents threshold, chunk-size, chunk-key, regeneration trigger, and adoption rule for future domains
- [ ] `_update_index_md` routes new ingest rows into last chunk when domain is chunked (verified by test)
- [ ] Idempotency: re-running chunker yields byte-identical output except `last_generated` lines
- [ ] A cron entry or scripted mechanism (`wiki-chunk-cron.sh` + `wiki-chunk-nightly` scheduled task) exists that invokes the chunker for marine-engineering post-ingest; it does not break the existing engineering `wiki-ingest-nightly` flow
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (feed3) | MAJOR → addressed by plan patch (feed4) | 2 MAJOR (cron scope, `_check_index_consistency` over-scope) + 6 MINOR resolved. Review: `scripts/review/results/2026-04-28-plan-2378-claude-feed3.md` |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** MAJOR findings addressed by feed4 plan patch. Awaiting fresh cross-review to confirm resolution. Plan is NOT approved.

**Pre-empted critiques:**

1. *"Why not delete Sources rows from index.md and rely on portal (#2368)?"* — Issue #2378 explicitly requires the canonical index remain authoritative for exhaustive navigation. Portal (#2368) is curated; chunked pages are exhaustive. Both required.
2. *"Alphabetical chunking is suboptimal — by-topic would be better."* — ~95% of sources have empty `tags: []` (verified empirically). Topic chunking creates one giant "untagged" bucket. Alphabetical-by-slug is also stable under re-ingest, unlike topic-based.
3. *"You're committing ~39 generated files — noisy."* — Sibling #2368 plan already commits `portal.md` on same rationale (reviewability of generated artifacts).
4. *"Why intercept `_update_index_md` instead of regenerating from scratch?"* — Full-regen is O(N) on 19K files every nightly. Append-to-last-chunk is O(1). Full-regen exposed as `--rebuild` for rare schema bumps.
5. *"What about #2368 coordination?"* — #2368 is currently `status:working` but `portal.md` has not landed yet. Both scripts write to the top of `index.md`. They must share a single "Generated navigation" anchor block. If #2368 lands first, this plan's implementation must detect and preserve the portal link. If this lands first, #2368 implementation must do the same. This is tracked as a coordination risk below.
6. *"`_chunks/` directory collision with source namespace?"* — Verified: `find knowledge/wikis -name '_chunks' -type d` returns empty. Underscore prefix matches existing lint-ignore patterns.

---

## Risks and Open Questions

- **Risk: #2368 coordination** — #2368 is actively being implemented (`status:working`, `agent:codex`). Both this plan and #2368 modify `knowledge/wikis/marine-engineering/wiki/index.md` top-level content. Mitigation: define a shared "Generated navigation" anchor block in the index that both scripts operate on idempotently. Whichever lands second must detect and preserve the other's content. Implementation should coordinate by checking if portal artifacts exist before writing.
- **Risk: `_update_index_md` patch** in a 1,400-line file with multiple writers. Mitigation: targeted single-site edit with TDD test coverage on both chunked and legacy paths.
- **Note: Wiki cross-link generator** (`scripts/knowledge/wiki-cross-links.py`) only scans `CONTENT_SUBDIRS = ("concepts", "entities", "standards", "workflows")` (line 37, verified 2026-04-28). It never touches `sources/` or `_chunks/`. No modification needed.
- **Risk: `last_generated` frontmatter drift** pollutes git history nightly. Mitigation: documented in policy as expected; dropping it makes regen-failures invisible.
- **Risk: Source-title aliasing (#2372)** landing later changes title strings → next chunker run rewrites every chunk page → noisy diff. Mitigation: expected and acceptable; content-driven, not structural.
- **Risk: Auto-trigger for future domains** — if another domain crosses threshold (e.g., post-Batch Pack 2 ingest), nightly silently chunks it. Mitigation: chunker logs trigger; policy doc states intentional behavior.
- **Open question:** Should top-level `## Sources` summary include per-chunk row counts inline? (Adds signal but expands summary.) Flag for user approval.
- **Open question:** Should chunker emit `report.json` for #2366 strengthening scorecard? Default: defer until #2366 defines consumer contract.
- **Open question:** Should chunk pages carry full source-page frontmatter schema or be exempt as derived artifacts? Recommend: derived-artifact frontmatter `{title, kind: chunk-page, generated_at, prev, next, up, page_index, page_count}` with explicit lint exemption. Flag for user.

---

## Complexity: T2

New module + 16 tests + one writer-function patch + one new cron script + one new scheduled-task entry + one policy doc + ~39 generated artifacts. No `_check_index_consistency` modification needed (trivial function, no orphan detection). Not architectural (no schema migration; reads existing `sources/<slug>.md` unchanged; preserves all existing links). TDD required: output is committed and must be deterministic; live-ingest hook has regression risk on legacy path.

---

## Changelog vs prior draft (2026-04-26)

| Item | 2026-04-26 value | 2026-04-28 value | Impact |
|---|---|---|---|
| `_update_index_md` line | 1133 | 1147 | Line reference corrected |
| `_check_index_consistency` line | 825 | 839 | Line reference corrected |
| Index line count | 21,616 | 21,622 | +6 lines, trivial |
| Source page count | 19,162 | 19,166 | +4 pages, chunk count stays ~39 |
| Frontmatter page_count | 19,189 | 19,197 | +8 pages |
| #2368 status | OPEN, status:plan-approved | OPEN, status:plan-approved + status:working + agent:codex | **New coordination risk added** |
| `portal.md` existence | Not checked | Verified MISSING | Confirms #2368 not yet landed |
| Artifact map path | Doubled prefix typo | Corrected | Cosmetic |
| Concept pages | 12 | 14 | +2 concept pages added since 4/26 |
| Entity pages | 15 | 15 | Unchanged |
