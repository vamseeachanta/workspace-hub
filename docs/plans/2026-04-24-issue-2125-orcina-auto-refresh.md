# Plan for #2125: feat(llm-wiki): auto-refresh ingestion on new Orcina releases

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2125
> **Review artifacts:** scripts/review/results/2026-04-24-plan-2125-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/llm-wiki/ingest-orcina.py` — full crawler; `ingest_product()` writes `index.json` per product with `generated` timestamp but no upstream version field; `SUPPLEMENTARY_URLS` already contains `("releases", "https://www.orcina.com/releases/")` so release-page HTML is already fetched each run.
- Found: `scripts/knowledge/wiki-ingest-cron.sh` — nightly cron for the *engineering* wiki (classes 1-8 under `knowledge/wikis/engineering`); no branch currently invokes `ingest-orcina.py`. Cron pattern (marker file, lint, auto-commit, wiki-alert issue on page-count drop) is the reference for a new Orcina cron companion.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` (imported by `ingest-orcina.py` line 557) — path resolution already portable.
- Gap: no `--refresh` mode, no Last-Modified/ETag handling per topic, no per-topic content hash, no changelog emission, no upstream version parser.

### Standards
Not applicable — ingestion tooling, not engineering calculation.

### LLM Wiki pages consulted
- `data/llm-wiki/orcaflex/index.json` (per repo-memory note: current version OrcaFlex 11.6c) — structure is product-scoped; version string lives only in README/prose, not machine-readable metadata.
- No relevant wiki semantic pages — this plan touches the ingestion pipeline, not the rendered wiki.

### Documents consulted
- Parent issue #2088 (Orcina ingestion baseline) — referenced in the script docstring; established the 717-topic TOC-driven crawl.
- Sibling #2126 (markdown-conversion QA) — landed in parallel Lane H2; shares the `html_to_markdown` surface. #2125 changes crawl cadence; #2126 validates converter fidelity. No overlap in files touched.
- `scripts/knowledge/wiki-ingest-cron.sh` — establishes cron/lint/commit/alert pattern; Orcina refresh cron should mirror it (hostname guard, `git-safe`, marker file, GitHub issue on drop).
- Upstream: `https://www.orcina.com/releases/` — the only authoritative release-surface Orcina publishes; HTML page listing current + historical OrcaFlex/OrcaWave/OrcFxAPI versions. No public RSS/JSON feed exists (verified via #2088 source survey).

### Gaps identified
- No machine-readable upstream version detector exists anywhere in the repo.
- No per-topic HTTP-cache layer — every run re-fetches all 717 pages (~4 min crawl).
- `index.json` schema has no `upstream_version` or `per_topic_hash` fields — adding them is forward-compatible (new keys, old readers ignore).
- No `data/llm-wiki/changelog/` directory exists; needs to be created and added to `.gitkeep`.
- No Orcina-specific cron wrapper; the existing cron is engineering-wiki only.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2125` — OPEN — "feat(llm-wiki): auto-refresh ingestion on new Orcina releases"
- `#2126` — OPEN — sibling (markdown-conversion QA), different code path
- `#2088` — referenced in `ingest-orcina.py` docstring line 7 as the parent

**File existence** (verified 2026-04-24):
- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py` (637 lines)
- EXISTS: `scripts/data/llm-wiki/resolve_wiki_path.py`
- EXISTS: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` (185 lines — test pattern reference)
- EXISTS: `scripts/knowledge/wiki-ingest-cron.sh` (367 lines — cron pattern reference)
- MISSING (new — this plan creates): `scripts/data/llm-wiki/orcina_version.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_orcina_version.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py`
- MISSING (new — this plan creates): `scripts/cron/orcina-refresh-cron.sh`
- MISSING (new — this plan creates): `data/llm-wiki/changelog/.gitkeep`

**Line excerpts**:

From `scripts/data/llm-wiki/ingest-orcina.py` lines 48-54 (supplementary URLs already include releases):
```
SUPPLEMENTARY_URLS = [
    ("resources", "https://www.orcina.com/resources/"),
    ...
    ("releases", "https://www.orcina.com/releases/"),
]
```

From `scripts/data/llm-wiki/ingest-orcina.py` lines 384-394 (current index schema — version field absent):
```
product_index = {
    "product": info["label"],
    "base_url": info["base_url"],
    "generated": datetime.now(timezone.utc).isoformat(),
    "topic_count": len(entries),
    ...
}
```

**Gap proofs**:
- `ls data/llm-wiki/changelog/ 2>&1` → "No such file or directory" — confirms changelog dir does not exist.
- `grep -n "upstream_version\|--refresh\|Last-Modified" scripts/data/llm-wiki/ingest-orcina.py` → no matches — confirms refresh machinery absent.
- `grep -rn "ingest-orcina" scripts/cron/ 2>&1` → no matches — confirms no existing cron wrapper.

<!-- Source count: issue body + ingest-orcina.py + wiki-ingest-cron.sh + resolve_wiki_path tests + #2088 reference + Orcina releases URL = 6 distinct sources. Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-2125-orcina-auto-refresh.md |
| New module — version detector | scripts/data/llm-wiki/orcina_version.py |
| New tests — version detector | scripts/data/llm-wiki/tests/test_orcina_version.py |
| New tests — refresh mode | scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py |
| Modify — ingest script | scripts/data/llm-wiki/ingest-orcina.py |
| New cron wrapper | scripts/cron/orcina-refresh-cron.sh |
| Changelog directory | data/llm-wiki/changelog/.gitkeep |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-2125-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-2125-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-2125-gemini.md |

---

## Deliverable

An `ingest-orcina.py --refresh` mode that parses the upstream Orcina releases page, skips topics whose upstream Last-Modified/content hash is unchanged, writes a machine-readable `upstream_version` to each product `index.json`, and emits a diff report to `data/llm-wiki/changelog/YYYY-MM-DD-<version>.md` whenever the detected version differs from the stored one.

---

## Pseudocode

```
# orcina_version.py
function detect_current_version(releases_html):
    parse HTML, locate release rows (MadCap Flare release-table pattern)
    extract version strings matching r"OrcaFlex \d+\.\w+" (and OrcaWave/OrcFxAPI variants)
    return {"orcaflex": "11.6c", "orcawave": "X.Y", "orcfxapi": "X.Y",
            "detected_at": utcnow_iso(), "source_url": RELEASES_URL}

function load_stored_version(index_path):
    if index.json has "upstream_version", return it; else return None

function diff_versions(stored, current):
    return {product: (stored.get(p), current[p]) for p in current if stored.get(p) != current[p]}

# ingest-orcina.py additions
function fetch_page_conditional(url, cached_meta):
    # cached_meta: {"last_modified": "...", "etag": "...", "content_hash": "..."}
    request with If-Modified-Since / If-None-Match
    if 304: return ("unchanged", cached_meta)
    else: compute sha256(body); return ("changed", new_meta, body)

function ingest_product(..., refresh_mode):
    if refresh_mode and stored index exists:
        load per-topic cache from index.json.topics[*].http_meta
        for each toc_entry: call fetch_page_conditional
        only convert + write topics that changed
    else:
        full crawl (current behavior)

function write_changelog(old_index, new_index, out_dir):
    emit markdown: added / removed / modified topics, version delta
    path: data/llm-wiki/changelog/<iso-date>-<version>.md

# CLI
parser.add_argument("--refresh", action="store_true")
parser.add_argument("--force-full", action="store_true")  # override: ignore cache
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/orcina_version.py` | upstream-version parser; isolated for unit testability |
| Create | `scripts/data/llm-wiki/tests/test_orcina_version.py` | TDD — parse fixtures of the releases page |
| Create | `scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py` | TDD — exercises `--refresh` with mocked HTTP 304/200 |
| Modify | `scripts/data/llm-wiki/ingest-orcina.py` | add `--refresh` flag, conditional-GET helper, per-topic `http_meta`, changelog writer, `upstream_version` in index.json |
| Create | `scripts/cron/orcina-refresh-cron.sh` | nightly wrapper: hostname guard, git-safe commit, wiki-alert issue if version-change-without-ingest |
| Create | `data/llm-wiki/changelog/.gitkeep` | hold the changelog directory in git |
| Update | `docs/plans/README.md` | index this plan |

---

## TDD Test List

### `test_orcina_version.py`

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_detect_current_version_from_fixture | Parses canned Orcina releases HTML | fixture `tests/fixtures/orcina_releases_11_6c.html` | `{"orcaflex": "11.6c", ...}` |
| test_detect_handles_multiple_products | All 3 products extracted when present | fixture with OrcaFlex+OrcaWave+OrcFxAPI rows | all 3 keys non-None |
| test_detect_returns_none_when_missing | Product absent from HTML yields None | fixture missing OrcaWave row | `current["orcawave"] is None` |
| test_detect_tolerates_unexpected_version_format | Regex tolerates `11.6c`, `12.0`, `13.0a-beta` | 3 synthetic rows | all parse, none raise |
| test_load_stored_version_missing_key | Old index.json without upstream_version | `{"product": "OrcaFlex"}` | returns None, does not raise |
| test_load_stored_version_present | New index.json with upstream_version | `{"upstream_version": "11.6c"}` | returns `"11.6c"` |
| test_diff_versions_identical | Same version both sides | stored==current | empty dict |
| test_diff_versions_bump | Version bump detected | stored="11.6b", current="11.6c" | `{"orcaflex": ("11.6b", "11.6c")}` |

### `test_ingest_orcina_refresh.py`

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_skips_unchanged_topic | 304 response → topic file not rewritten | mocked `urlopen` returns 304 for topic A | `write` not called for A |
| test_refresh_rewrites_changed_topic | 200 + new body → topic re-converted | mocked 200 + different content-hash | A.md updated, index http_meta updated |
| test_refresh_without_stored_index_does_full_crawl | First-run `--refresh` falls back to full | no existing index.json | all topics fetched normally |
| test_refresh_writes_changelog_on_version_bump | Version bump triggers changelog file | stored 11.6b, live 11.6c | `data/llm-wiki/changelog/<date>-11.6c.md` exists, lists changed topics |
| test_refresh_no_changelog_when_version_stable | No changelog when nothing changes | stored==live, all 304s | no new changelog file, index `generated` still updated |
| test_force_full_overrides_refresh | `--force-full` ignores cache | `--refresh --force-full` with stored index | every topic re-fetched (no conditional headers) |
| test_http_meta_persisted_in_index | Per-topic etag/last-modified round-trips | run, re-run with `--refresh` | second run reads http_meta from index.json |
| test_version_persisted_in_index | `upstream_version` written to product index.json | refresh run | `json.load(index_path)["upstream_version"] == "11.6c"` |

All tests use `unittest.mock.patch` on `urllib.request.urlopen` (no real network). Fixture HTML files live under `scripts/data/llm-wiki/tests/fixtures/`.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_orcina_version.py -v` → all 8 tests pass.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py -v` → all 8 tests pass.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/` → existing `test_resolve_wiki_path.py` still passes (no regression).
- [ ] `ingest-orcina.py --refresh` against an existing index.json re-fetches zero topics when the live upstream is byte-identical (observable: script prints `0 changed, 717 cached` or similar, total wallclock < 60s).
- [ ] `ingest-orcina.py --refresh` writes `upstream_version` into every `<product>/index.json`.
- [ ] When `stored.upstream_version != live.upstream_version`, a markdown changelog appears at `data/llm-wiki/changelog/<date>-<new-version>.md` listing added/removed/modified topics.
- [ ] When versions are equal, no changelog file is created (verified in a live run).
- [ ] `scripts/cron/orcina-refresh-cron.sh --dry-run` on the full-variant machine runs to completion without errors, logs to `logs/wiki-ingest/orcina-<date>.log`, and does not create commits.
- [ ] Review artifacts posted to `scripts/review/results/` for Claude, Codex, Gemini.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | (pending) |
| Codex | (pending) | (pending) |
| Gemini | (pending) | (pending) |

**Overall result:** (pending)

---

## Risks and Open Questions

- **Risk:** Orcina releases page HTML structure may change without notice — the version parser must degrade gracefully (return None per product, not raise) so cron does not go red on an upstream cosmetic change.
- **Risk:** Upstream may not send `Last-Modified` or `ETag` headers consistently; fall back to SHA-256 of response body as the cache key.
- **Risk:** Partial-crawl failure (network blip mid-run) could leave `index.json` inconsistent. Mitigation: write index to `index.json.tmp` then atomic rename.
- **Risk:** `--refresh` against a very stale cache (months old, layout changes) may emit a changelog with hundreds of entries. Acceptable for the first post-upgrade run; surface via cron log size check.
- **Open:** Should cron auto-trigger on version bump, or only flag an issue and let a human run full crawl? Recommend: flag + auto-run on version bump (idempotent).
- **Open:** Changelog filename format `<date>-<version>.md` — confirm with user whether multiple changelogs per day are allowed (e.g. `<date>-<version>-<seq>.md`).

---

## Complexity: T2

**T2** — one new module (`orcina_version.py`), one modified module (`ingest-orcina.py`), one new shell cron wrapper, TDD required, no cross-repo changes. Scope is bounded and all interfaces are local; upstream integration is read-only HTTP.
