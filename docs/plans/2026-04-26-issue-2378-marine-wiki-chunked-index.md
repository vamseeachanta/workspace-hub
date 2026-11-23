# Plan for #2378: feat(knowledge): chunk and paginate the canonical marine-engineering wiki index

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2378
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2378-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` line 1133 `_update_index_md()` — current writer that appends new source rows directly to `wiki/index.md` and updates `page_count` / `source_count` / `last_updated` frontmatter fields. This is the precise interception point for chunking: the chunked-writer must replace this in-place append.
- Found: `scripts/knowledge/llm_wiki.py` line 825 `_check_index_consistency()` — lint hook that checks `wiki/index.md` consistency. Must be updated to follow chunk pages, not just `index.md`.
- Found: `scripts/knowledge/llm_wiki.py` line 1234 `cmd_batch_ingest()` — bulk-ingest entry point that drives `_update_index_md()`; the regeneration trigger lives here.
- Found: `scripts/knowledge/wiki-ingest-cron.sh` line 145 — nightly ingest already calls `llm_wiki.py lint`; chunked output must remain lint-clean.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` line 587 (`wiki-ingest-nightly`) — existing nightly cadence; chunk regeneration plugs in here without a new cron.
- Found (sibling): `docs/plans/2026-04-23-issue-2368-faceted-portal-pages.md` — companion plan introducing `scripts/knowledge/generate_wiki_portal.py` and `wiki/portal.md`. Sets the precedent for "scripted, idempotent, committed-but-regenerated" wiki artifacts. Chunking will adopt the same idempotency contract.
- Gap: no chunk/pagination subcommand or standalone script exists. Verified: `ls scripts/knowledge/ | grep -i -E 'chunk|paginate|page-'` returns empty.
- Gap: no chunk-page filename convention, no `next`/`prev`/jump-link pattern, no chunk frontmatter schema in any of the five domain wikis.

### Standards
Not applicable — `cat:documentation, domain:knowledge-management` issue. No engineering standards exercised. Adheres to `.claude/rules/coding-style.md` (relative paths via `REPO_ROOT`) and `.claude/rules/calc-citation-contract.md` non-applicability (no standards-derived constants emitted).

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/index.md` — verified 21,616 lines (`wc -l`), 21,568 page-row lines (`grep -c '^| \[\['`), section headers at lines 13/33/50/62/68 (`grep -nE '^## '`). Sources section dominates: rows 50→62 contain the bulk; Sources alone is ~21,500 rows.
- `knowledge/wikis/marine-engineering/wiki/sources/` — verified 19,162 source pages (`ls | wc -l`).
- `knowledge/wikis/marine-engineering/wiki/index.md` frontmatter — `page_count: 19189`, `source_count: 19161` (verified by grep on file). Total *.md count under `knowledge/wikis/marine-engineering` is 19,194 (`find ... | wc -l`).
- `knowledge/wikis/marine-engineering/CLAUDE.md` — domain frontmatter contract: `title`, `tags`, `added`, `last_updated` required; `sources`, `domain`, `cross_links` recommended/optional. Chunk pages must satisfy this schema or be explicitly exempt.
- Other domain indexes (cross-checked): `engineering/wiki/index.md` 121 lines, `naval-architecture/wiki/index.md` 77 lines, `maritime-law/wiki/index.md` 54 lines, `personal/wiki/index.md` 39 lines. Marine-engineering is the *sole* domain that exceeds any reasonable chunking threshold; the policy must therefore be domain-agnostic but only triggers for marine-engineering today.
- Sample source pages verified for frontmatter shape: `sources/22035.md` (filename-style title, populated path/year), `concepts/sour-service.md` (semantic title, tags, sources list), `entities/anode.md` (semantic title, tags, sources list).

### Documents consulted
- Issue #2378 body — explicit requirements: keep one canonical top-level `index.md`, generate bounded chunk pages especially for Sources, add stable `next`/`prev`/jump links without breaking current links, scripted regeneration, define a reusable policy for other oversized wikis.
- Parent issue #2205 — operating model for llm-wiki + resource/document intelligence; chunking is an L4 entry-point concern; canonical `index.md` remains the L4 surface, chunk pages are derived L4 sub-surfaces.
- Sibling #2368 (faceted portal pages) — explicitly states portals "do not replace the canonical index"; #2378 is the complement (chunk the canonical), so portal and chunked-index must coexist on the top-level page.
- Sibling #2372 (source-title aliasing) — title aliasing changes the *content* of source rows, not their *count or layout*. Chunker must consume whatever titles `llm_wiki.py` writes today; aliasing landing later does not invalidate the chunk layout.
- Sibling #2366 (strengthening scorecard, referenced by issue body) — downstream consumer; chunked layout becomes an input signal, not a blocker.
- `docs/document-intelligence/intelligence-accessibility-map.md` line 180 — explicitly flags marine-engineering "19K pages with no curated entry beyond the index" as the L3 weakness #2378 (with #2368) closes.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — entry-point layer (L4) is the surface owned by index/portal/chunk pages; chunking does not change layer boundaries.

### Gaps identified
- No chunk generator. Must build.
- No chunk-page filename or layout convention. Must define and document.
- No chunking-key decision (alphabetical vs topic vs size). Must select with rationale.
- No `next`/`prev`/jump-link rendering convention. Must define.
- No regeneration-trigger contract (when, how, by whom). Must define.
- No reusable-policy doc for "future large wikis". Must author.
- No test for "chunked layout preserves all existing source-page hyperlinks". Must add.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26 via `gh issue view`):
- `#2378` — OPEN — "feat(knowledge): chunk and paginate the canonical marine-engineering wiki index"
- `#2205` — CLOSED — parent operating model (status:plan-approved label retained on closed issue)
- `#2368` — OPEN, status:plan-approved — sibling faceted-portal plan
- `#2372` — OPEN — sibling source-title aliasing
- `#2366` — referenced in issue body (downstream consumer)

**File existence** (`ls`/`wc` 2026-04-26):
- EXISTS: `knowledge/wikis/marine-engineering/wiki/index.md` (21,616 lines)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/sources/` (19,162 *.md files)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/concepts/` (12 files)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/entities/` (15 files)
- EXISTS: `knowledge/wikis/marine-engineering/CLAUDE.md`
- EXISTS: `scripts/knowledge/llm_wiki.py` (with `_update_index_md` line 1133, `_check_index_consistency` line 825)
- EXISTS: `scripts/knowledge/tests/test_llm_wiki.py` (test pattern reference)
- EXISTS: `scripts/knowledge/wiki-ingest-cron.sh` (nightly ingest hook)
- EXISTS: `config/scheduled-tasks/schedule-tasks.yaml` (line 587 — `wiki-ingest-nightly`)
- EXISTS: `docs/plans/2026-04-23-issue-2368-faceted-portal-pages.md` (sibling precedent)
- MISSING (this plan creates): `scripts/knowledge/chunk_wiki_index.py`
- MISSING (this plan creates): `scripts/knowledge/tests/test_chunk_wiki_index.py`
- MISSING (this plan creates): `knowledge/wikis/marine-engineering/wiki/sources/_chunks/` (directory)
- MISSING (this plan creates): `knowledge/wikis/marine-engineering/wiki/sources/_chunks/index.md` (chunk manifest)
- MISSING (this plan creates): `docs/document-intelligence/llm-wiki-chunking-policy.md`

**Line excerpts** (`sed -n` against verified files):
- `knowledge/wikis/marine-engineering/wiki/index.md` line 50 (`## Sources`) → confirms the section to chunk.
- `knowledge/wikis/marine-engineering/wiki/index.md` lines 1-7 (frontmatter) → confirms `page_count: 19189`, `source_count: 19161`, `domain: marine-engineering`.
- `scripts/knowledge/llm_wiki.py` line 1133 (`def _update_index_md`) → confirms the writer that must be redirected.

**Gap proofs**:
- `ls scripts/knowledge/ | grep -i -E 'chunk|paginate|page-'` → empty → no prior chunk script.
- `grep -nE 'next|prev|chunk|page [0-9]' knowledge/wikis/marine-engineering/wiki/index.md | head` → no chunk navigation present.
- `find knowledge/wikis -name '_chunks' -type d` → empty → no chunk directory pattern in any wiki yet.

**Source count verification:** Distinct sources consulted: (1) issue #2378 body, (2) parent #2205, (3) sibling #2368 plan + issue, (4) sibling #2372 issue, (5) `intelligence-accessibility-map.md`, (6) `llm-wiki-resource-doc-intelligence-operating-model.md`, (7) `llm_wiki.py` codebase, (8) live `index.md`/sources/ tree, (9) `wiki-ingest-cron.sh` + `schedule-tasks.yaml`, (10) marine-engineering `CLAUDE.md`. Minimum of 3 — exceeded.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-26-issue-2378-2026-04-26-issue-2378-marine-wiki-chunked-index.md` |
| Implementation | `scripts/knowledge/chunk_wiki_index.py` |
| Tests | `scripts/knowledge/tests/test_chunk_wiki_index.py` |
| Chunk manifest | `knowledge/wikis/marine-engineering/wiki/sources/_chunks/index.md` |
| Chunk pages (generated) | `knowledge/wikis/marine-engineering/wiki/sources/_chunks/sources-<rangelo>-<rangehi>.md` |
| Chunking policy doc | `docs/document-intelligence/llm-wiki-chunking-policy.md` |
| Plan review — Claude | `scripts/review/results/2026-04-26-plan-2378-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-26-plan-2378-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-26-plan-2378-gemini.md` |
| Top-level index — modified | `knowledge/wikis/marine-engineering/wiki/index.md` (Sources section becomes a chunk-manifest summary, not an enumerated table) |
| Hooked writer | `scripts/knowledge/llm_wiki.py` (`_update_index_md` redirects to chunk writer when chunking is active) |
| Index updated | `docs/plans/README.md` (add row for `2026-04-26-issue-2378-marine-wiki-chunked-index`) |

---

## Deliverable

A `scripts/knowledge/chunk_wiki_index.py` generator (plus integration into `llm_wiki.py:_update_index_md`) that will replace the in-line 21K-row Sources table inside `knowledge/wikis/marine-engineering/wiki/index.md` with (a) a bounded chunk manifest summarising N chunk pages, and (b) chunk pages under `wiki/sources/_chunks/` with stable `prev`/`next`/`up` navigation, generated reproducibly and re-runnable from current ingest state — accompanied by a reusable chunking-policy doc that other oversized wikis can later adopt without code changes.

---

## Pseudocode

```
# chunk_wiki_index.py — main entry

CONSTANTS:
    DEFAULT_CHUNK_SIZE = 500              # source rows per chunk page
    DEFAULT_TRIGGER_THRESHOLD = 2_000     # if Sources row count >= this, chunk
    CHUNK_KEY = "alphabetical_by_slug"    # selected key (rationale below)
    CHUNK_DIRNAME = "_chunks"             # underscore-prefixed: lint-ignored already

function chunk_wiki_index(domain, chunk_size=DEFAULT_CHUNK_SIZE, threshold=DEFAULT_TRIGGER_THRESHOLD, dry_run=False):
    wiki_root  = REPO_ROOT / "knowledge" / "wikis" / domain / "wiki"
    sources_dir = wiki_root / "sources"
    chunks_dir = sources_dir / CHUNK_DIRNAME
    index_md   = wiki_root / "index.md"

    sources = sorted(sources_dir.glob("*.md"), key=lambda p: p.stem.lower())
    if len(sources) < threshold and not force:
        print(f"{domain}: {len(sources)} sources < threshold {threshold}; skipping")
        return 0

    chunks = partition(sources, size=chunk_size)             # alphabetical contiguous ranges
    manifest_rows = []
    for i, chunk in enumerate(chunks):
        lo, hi = chunk[0].stem, chunk[-1].stem
        chunk_path = chunks_dir / f"sources-{slugify(lo)}--{slugify(hi)}.md"
        prev_link = chunk_filename(chunks, i-1) if i > 0 else None
        next_link = chunk_filename(chunks, i+1) if i < len(chunks)-1 else None
        rendered = render_chunk(
            domain=domain,
            page_index=i+1,
            page_count=len(chunks),
            range_lo=lo, range_hi=hi,
            entries=[parse_frontmatter_lite(p) for p in chunk],
            prev=prev_link, next=next_link, up="../../index.md",
            generated_at=utcnow(),
        )
        write_atomic(chunk_path, rendered)                   # tempfile + rename
        manifest_rows.append((i+1, lo, hi, len(chunk), chunk_path.name))

    manifest_md = render_manifest(domain, chunks, generated_at=utcnow())
    write_atomic(chunks_dir / "index.md", manifest_md)

    rewrite_top_level_index_sources_section(index_md, manifest_rows, total=len(sources))

    return {"chunks": len(chunks), "rows_total": len(sources), "manifest": str(chunks_dir / "index.md")}


function rewrite_top_level_index_sources_section(index_md, manifest_rows, total):
    # NON-DESTRUCTIVE for Entities / Concepts / Comparisons / Topics Covered.
    # Only the "## Sources" block is replaced.
    text = read(index_md)
    new_block = render_sources_summary(manifest_rows, total)   # <= ~50 lines, links to _chunks/index.md
    text = replace_block_between("## Sources", next_h2_or_eof, with=new_block)
    text = update_frontmatter(text, last_updated=utcnow_date())
    write_atomic(index_md, text)


function render_sources_summary(manifest_rows, total):
    return f"""
## Sources

> **{total:,} sources are paginated.** See the [chunk manifest](sources/_chunks/index.md).
> Per-letter range chunks of ~{CHUNK_SIZE} entries. Existing `sources/<slug>.md` links remain unchanged.

| # | Range | Entries | Page |
|---|---|---|---|
{rows formatted as: i | lo--hi | count | [link](sources/_chunks/<file>.md)}

**Curated facets:** see [portal.md](portal.md) (companion to this paginated index — produced by #2368).
"""

# Hook into llm_wiki.py:_update_index_md so live ingest does NOT re-bloat the top-level index:
function _update_index_md_chunked_aware(index_path, new_entries, domain, now):
    if domain has chunking active (chunks/index.md exists):
        # 1. write the new sources/<slug>.md page (existing behavior, untouched)
        # 2. append rows to the LAST chunk page (or open a new one if size>CHUNK_SIZE)
        # 3. update chunks/index.md manifest counts
        # 4. update top-level index.md frontmatter (page_count/source_count/last_updated) ONLY
        # 5. do NOT append rows to top-level index.md ## Sources section
    else:
        legacy path (current _update_index_md behavior)
```

**Chunking-key rationale (the load-bearing design choice):**

| Candidate | Pros | Cons | Verdict |
|---|---|---|---|
| Alphabetical-by-slug (chosen) | Stable across ingests; deterministic regeneration; predictable chunk identities so links stay valid; humans/agents can jump by knowing first letter | Bias toward early letters when ingest is uneven | **Selected** — stability dominates aesthetic balance |
| Topic / tag | Aligns with portal facets (#2368) | Most source pages have empty `tags: []` (verified on `sources/22035.md`); would dump 95% into "untagged"; duplicates portal job | Rejected |
| By-size (rolling-bucket of N) | Even bucket sizes | Bucket contents shift with every ingest → link instability | Rejected — violates "stable navigation" acceptance criterion |
| By-source-type (PDF/Web/Programme/etc.) | Coarse split | Only 5-7 types; each still 1K-5K rows | Insufficient on its own (could compose with alphabetical, but adds complexity for marginal gain) — Rejected for v1 |

Defaults: `CHUNK_SIZE=500` (yields ~38 chunks for 19,162 sources, each ≈500 rows ≈ 600 lines). `THRESHOLD=2000` ensures the four sub-100-line sibling indexes (engineering, naval-architecture, maritime-law, personal) never get auto-chunked.

**Idempotency contract:** re-running the chunker against the same `sources/` tree produces byte-identical chunk pages, manifest, and top-level summary except for `last_generated:` frontmatter lines. Enforced by an explicit "run twice, diff" test.

**Link-preservation contract:** existing in-repo links of the form `sources/<slug>.md` and `[[<slug>]]` MUST remain valid. The chunker does NOT move source pages; it only adds a derived directory `sources/_chunks/`. The `_check_index_consistency` lint must be extended to recognise chunk pages without flagging them as orphans.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/chunk_wiki_index.py` | Main implementation (CLI + library functions) |
| Create | `scripts/knowledge/tests/test_chunk_wiki_index.py` | TDD test suite |
| Create | `knowledge/wikis/marine-engineering/wiki/sources/_chunks/index.md` | Chunk manifest (generated, committed) |
| Create | `knowledge/wikis/marine-engineering/wiki/sources/_chunks/sources-*.md` | ~38 chunk pages (generated, committed) |
| Create | `docs/document-intelligence/llm-wiki-chunking-policy.md` | Reusable policy + threshold + key + regeneration contract |
| Modify | `knowledge/wikis/marine-engineering/wiki/index.md` | Replace 21K-line Sources table with bounded chunk-manifest summary |
| Modify | `scripts/knowledge/llm_wiki.py` (`_update_index_md` line 1133) | Route Sources-row appends to last chunk page when chunking active |
| Modify | `scripts/knowledge/llm_wiki.py` (`_check_index_consistency` line 825) | Recognise `_chunks/` pages; do not flag as orphan/empty |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` (`wiki-ingest-nightly` line 587) | Append `chunk_wiki_index.py marine-engineering` post-ingest step |
| Modify | `scripts/knowledge/wiki-ingest-cron.sh` | Invoke the chunker after ingest, before lint |
| Update | `docs/plans/README.md` | Add this plan's row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_skips_domain_below_threshold` | engineering (121-line index, ~few sources) is not chunked | `domain=engineering` | exit 0, `_chunks/` not created |
| `test_chunks_marine_engineering_count` | marine-engineering chunks into N=ceil(19162/500)=39 pages (allowing for actual count drift) | fixture mirroring real `sources/` count | manifest has N rows; `_chunks/sources-*.md` count == N |
| `test_alphabetical_partition_stable` | re-running with same inputs yields same chunk filenames and same row order | run twice on fixture | filenames + row order identical |
| `test_idempotent_byte_identical` | re-run produces byte-identical files except `last_generated:` line | run twice, diff | only `last_generated` lines differ |
| `test_top_level_index_sources_replaced` | after run, `index.md` Sources section ≤ ~80 lines and links to `sources/_chunks/index.md` | initial 21K-line index | new index < 200 lines total; manifest link present |
| `test_top_level_other_sections_unchanged` | Entities / Concepts / Comparisons / Topics Covered sections are byte-identical pre vs post | run on fixture | diff outside `## Sources` block is empty |
| `test_existing_source_links_unbroken` | every `[[<slug>]]` and `sources/<slug>.md` reference in the wiki resolves after chunking | scan all *.md under `wiki/` for these patterns | each target file still exists |
| `test_chunk_page_has_prev_next_up` | chunk N has correct prev (N-1), next (N+1), up (`../../index.md`) | inspect any middle chunk | links match expected slugs |
| `test_first_chunk_no_prev` | first chunk has only next + up | inspect chunk 1 | `prev:` field absent or null |
| `test_last_chunk_no_next` | last chunk has only prev + up | inspect chunk N | `next:` field absent or null |
| `test_lint_passes_post_chunk` | `llm_wiki.py lint --wiki marine-engineering` returns 0 with chunks present | run lint after chunker | exit code 0 |
| `test_live_ingest_appends_to_last_chunk` | when `_update_index_md` runs on a chunked domain, new rows go to last chunk, not top-level index | simulate batch-ingest of 3 new sources | last chunk row count increases by 3; top-level Sources block unchanged except frontmatter counters |
| `test_live_ingest_rolls_to_new_chunk` | when last chunk fills past `CHUNK_SIZE`, a new chunk page is created and manifest updated | simulate ingest that pushes last chunk over 500 | new chunk file exists; manifest row added |
| `test_threshold_cli_override` | `--threshold 100 --chunk-size 50` lets a small fixture domain be chunked for testing | small fixture | chunks created |

All tests run via `uv run pytest scripts/knowledge/tests/test_chunk_wiki_index.py -v`.

---

## Acceptance Criteria

- [ ] `scripts/knowledge/chunk_wiki_index.py` exists, invoked as `uv run scripts/knowledge/chunk_wiki_index.py marine-engineering`
- [ ] All new tests pass: `uv run pytest scripts/knowledge/tests/test_chunk_wiki_index.py -v`
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` passes
- [ ] `knowledge/wikis/marine-engineering/wiki/index.md` is < 500 total lines after chunking (down from 21,616) AND remains the sole canonical entry point
- [ ] `knowledge/wikis/marine-engineering/wiki/sources/_chunks/index.md` exists and lists all chunk pages with row counts and ranges
- [ ] All chunk pages exist with `prev`/`next`/`up` links forming a valid chain (verified by `test_chunk_page_has_prev_next_up`)
- [ ] Lint passes: `uv run scripts/knowledge/llm_wiki.py lint --wiki marine-engineering` exits 0
- [ ] No existing `sources/<slug>.md` link in any *.md under `knowledge/wikis/marine-engineering/wiki/` is broken (verified by `test_existing_source_links_unbroken`)
- [ ] `docs/document-intelligence/llm-wiki-chunking-policy.md` documents threshold, chunk-size, chunk-key, regeneration trigger, and the rule for adopting chunking on a future domain
- [ ] `_update_index_md` routes new ingest rows into the last chunk when the domain is chunked (verified by `test_live_ingest_appends_to_last_chunk`)
- [ ] Idempotency: re-running the chunker yields byte-identical output except for `last_generated` lines
- [ ] Nightly cron (`wiki-ingest-nightly`) invokes the chunker without breaking the existing ingest+lint+commit flow
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (r1 cross-review will be dispatched after this plan is pushed and an attestation block is generated per #2405).

**Pre-empted critiques (not filler — these are the live attack surfaces):**

1. *"Why not just delete the Sources rows from index.md and rely on the portal (#2368)?"* — Issue #2378 explicitly says the canonical index must remain authoritative for exhaustive navigation. The portal is a *curated* surface; chunked pages are the *exhaustive* surface. Both are required by their parent issues.
2. *"Alphabetical chunking is dumb — by-topic would be more useful."* — Verified empirically: `sources/22035.md` and similar conference-paper pages have empty `tags: []`. ~95% of sources have no tag signal. Topic chunking would create one giant "untagged" bucket. Alphabetical-by-slug is also stable under re-ingest, which by-topic is not (a tag added later would silently move a row across chunks → link drift).
3. *"You're committing 38 generated files — that's noisy."* — Yes, but the sibling #2368 plan already committed `portal.md` on the same rationale (reviewability of generated artifacts). Cross-cutting drift CI is tracked as a follow-on, not in scope here.
4. *"Why intercept `_update_index_md` instead of regenerating from scratch each ingest?"* — Full-regenerate would be O(N) on 19K files every nightly batch. Append-to-last-chunk is O(1) and matches the existing batch-ingest model. Full-regen is exposed as `--rebuild` for the rare schema-bump case.
5. *"What about race conditions when batch-ingest runs concurrently with chunker?"* — The cron sequences ingest → chunker → lint serially; concurrent invocation is out of scope (matches the existing single-cron contract). If a user runs the chunker manually mid-ingest, the worst case is a partial chunk page; the next nightly converges.
6. *"`_chunks/` directory may collide with the existing 19K source-page namespace."* — Verified: `find knowledge/wikis -name '_chunks' -type d` returns empty. The underscore prefix also matches existing lint-ignore patterns for non-page directories.
7. *"You haven't shown the chunk page actually loads — what if 500 rows × N renders too slow in GH preview?"* — Standard GitHub markdown rendering handles tables of 500 rows fine; the current 19K rendering is the failure mode. 500 is one order below the GH-issue/wiki-preview practical ceiling.
8. *"Tests rely on a fixture, not the real 19K corpus."* — Right. `test_chunks_marine_engineering_count` uses fixture mirroring real counts; an optional `--live` integration test runs against the real corpus locally but is excluded from CI to keep test runtime bounded.

---

## Risks and Open Questions

- **Risk:** `_update_index_md` patch is in a 1,400-line file with multiple writers. Mitigation: targeted single-site edit; test `test_live_ingest_appends_to_last_chunk` covers the new path; existing `test_llm_wiki.py` covers regression on legacy non-chunked path.
- **Risk:** Wiki cross-link generator (`scripts/knowledge/wiki-cross-links.py`) may not understand chunk pages. Mitigation: chunk pages live under `_chunks/`; verify cross-link generator skips underscore-prefixed dirs (existing convention) — open follow-up if not.
- **Risk:** `last_generated` frontmatter line drifts diff every nightly run, polluting git history. Mitigation: documented in policy as expected; the alternative (drop `last_generated`) makes regen-failures invisible.
- **Risk:** Sibling #2368 portal generator and this chunker both want to add a top-of-`index.md` link block. Mitigation: define a single "Generated navigation" block managed by both scripts via idempotent insert-or-update; both plans must agree on this anchor (tracked in this plan; #2368 may need a follow-up patch).
- **Risk:** Source-title aliasing (#2372) lands later and changes the title strings inside chunk rows → next chunker run rewrites every chunk page → noisy diff. Mitigation: expected and acceptable; the diff is content-driven, not structural.
- **Risk:** If a domain other than marine-engineering crosses the threshold later (e.g., post-#2369 Batch Pack 2 ingest into engineering), nightly will silently start chunking it. Mitigation: chunker logs the trigger event; policy doc states the intentional auto-trigger behavior; nightly log review (existing `wiki-ingest-cron.sh` log path) catches it.
- **Risk:** Reviewers may reject the 500/2000 defaults as arbitrary. Mitigation: rationale in policy doc with line-count math; numbers are CLI-overridable.
- **Open:** Should the top-level `## Sources` summary include the per-chunk row counts inline, or only the range labels? (Inline counts add useful signal but expand the summary block.) Flag for user during approval.
- **Open:** Should the chunker emit a `report.json` for #2366 strengthening-scorecard consumption, or wait for #2366 to define its consumer contract? Default: defer until #2366 specifies.
- **Open:** Should chunk pages carry the *full* source-page frontmatter schema (`title`, `tags`, `added`, `last_updated`) or be exempt as derived/generated? Recommend: derived-artifact frontmatter shape `{title, kind: chunk-page, generated_at, prev, next, up, page_index, page_count}` with explicit lint exemption. Flag for user.

---

## Complexity: T2

New module + 13 tests + one writer-function patch + one consistency-check patch + one cron edit + one policy doc + ~40 generated artifacts. Not architectural (no schema migration; reads existing `sources/<slug>.md` files unchanged; preserves all existing links). TDD required because the output is committed and must be deterministic, and because the live-ingest hook into `_update_index_md` has a regression risk on the legacy non-chunked path.
