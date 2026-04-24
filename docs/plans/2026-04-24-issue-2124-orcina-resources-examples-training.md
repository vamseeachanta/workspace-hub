# Plan for #2124: Extend llm-wiki ingestion to Orcina resources, examples, and training materials

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2124
> **Review artifacts:** scripts/review/results/2026-04-24-plan-2124-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/llm-wiki/ingest-orcina.py` — already handles OrcaFlex/OrcaWave/OrcFxAPI help + a `SUPPLEMENTARY_URLS` list (resources page, papers page, papers-and-technical-notes, documentation, releases) via `ingest_supplementary()` and a PDF ingester `ingest_papers()` using `pdftotext`. Gap: supplementary coverage is shallow (landing pages only), examples are not enumerated, the Python training ZIP is not downloaded/unpacked, release notes are not parsed version-by-version, and the blog/news feed is not ingested.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — portable output-root resolver (#2140); this plan reuses it without change.
- Found: `scripts/data/llm-wiki/search-wiki.py` — reads master `index.json`; new categories (examples, training, releases, news) must register under the same master schema.
- Found: `scripts/data/llm-wiki/tests/` — existing pytest scaffolding for wiki tooling.
- Gap: no ZIP-download + extract path (training material is a zipped set of Python notebooks + readme).
- Gap: no version-aware release-notes parser — each release is a separate page with its own changelog section.
- Gap: no examples-catalog scraper — 54 OrcaFlex examples, each with a description page.

### Standards
Not applicable — documentation-pipeline issue.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/` — curated-wiki boundary. New extended-Orcina content continues to live under `data/llm-wiki/orcina/…` (bulk ingest) rather than the curated wiki; cross-links into curated wiki only for topics the user later promotes.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — durable-vs-transient boundary (#2209) governs where the ingested output may mutate vs where it must not.

### Documents consulted
- Issue body #2124 — five named sources (resources, example descriptions, training ZIP, release notes, blog/news). Flags release notes as especially valuable for behavioral-change tracking.
- Parent issue #2088 — CLOSED; defines the master `index.json` contract extended here.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — operating model for llm-wiki outputs.
- `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md` — ecosystem roadmap lists "Orcina resources + examples + training" as a gap line-item.
- Upstream: https://www.orcina.com/resources/ (videos, webinars, case studies).
- Upstream: https://www.orcina.com/resources/documentation/examples/ (54 examples, each a sub-page).
- Upstream: https://www.orcina.com/wp-content/uploads/training/An%20introduction%20to%20the%20Python%20interface%20to%20OrcaFlex.zip (Python-API training bundle — ZIP with `.ipynb` + `.md` + `.py` + readme).
- Upstream: https://www.orcina.com/releases/ (release list; each version links to its own release-notes page).
- Upstream: https://www.orcina.com/news/ (blog/news posts).

### Gaps identified
- No extended-resources scraper: existing `ingest_supplementary()` only fetches the landing page, not the linked sub-pages.
- No examples-catalog enumerator + description scraper.
- No ZIP downloader + safe extractor (must prevent path-traversal) + per-file markdown conversion.
- No release-notes crawler that walks the release index and captures each version's changelog.
- No news/blog crawler.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2124` — OPEN — feat(llm-wiki): extend ingestion to Orcina resources, examples, and training materials
- `#2088` — CLOSED — feat(llm-wiki): ingest OrcaFlex/OrcaWave/OrcFxAPI online help (parent)
- `#2140` — CLOSED — portable llm-wiki path resolver

**File existence** (`ls` 2026-04-24):
- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py` (lines 48-54 define `SUPPLEMENTARY_URLS` — 5 landing pages only)
- EXISTS: `scripts/data/llm-wiki/resolve_wiki_path.py`
- EXISTS: `scripts/data/llm-wiki/search-wiki.py`
- EXISTS: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/ingest-orcina-extended.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py`
- MISSING (runtime): `data/llm-wiki/orcina/extended/{resources,examples,training,releases,news}/`

**Line excerpt** (`ingest-orcina.py` lines 48-54, the supplementary list being extended):
```
SUPPLEMENTARY_URLS = [
    ("resources", "https://www.orcina.com/resources/"),
    ("papers", "https://www.orcina.com/resources/papers/"),
    ("papers-and-technical-notes", "https://www.orcina.com/resources/papers-and-technical-notes/"),
    ("documentation", "https://www.orcina.com/resources/documentation/"),
    ("releases", "https://www.orcina.com/releases/"),
]
```

**Gap proof:**
- `ls scripts/data/llm-wiki/ingest-orcina-extended.py 2>&1` → "No such file or directory".

Distinct sources consulted: 8 (issue body, #2088, #2140, `ingest-orcina.py`, `resolve_wiki_path.py`, `#2205` plan, ecosystem-strengthening plan, marine-engineering wiki governance).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-2124-orcina-resources-examples-training.md` |
| Extended ingester | `scripts/data/llm-wiki/ingest-orcina-extended.py` |
| Tests | `scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py` |
| Test fixtures | `scripts/data/llm-wiki/tests/fixtures/orcina_example_page.html`, `.../orcina_release_notes_v11_4.html`, `.../orcina_news_post.html`, `.../training_bundle.zip` (tiny synthetic) |
| Output (runtime) | `data/llm-wiki/orcina/extended/{resources,examples,training,releases,news}/` |
| Master index | `data/llm-wiki/index.json` (extended section appended) |
| Plan reviews | `scripts/review/results/2026-04-24-plan-2124-{claude,codex,gemini}.md` |

---

## Deliverable

A single `ingest-orcina-extended.py` that extends the existing Orcina ingestion to cover five new content classes — resources/videos/webinars, examples catalog (all 54), Python-API training ZIP (downloaded, safely extracted, each file converted to markdown), per-version release notes, and news/blog posts — with offline-fixture pytest coverage and a merged entry in the master `data/llm-wiki/index.json`.

---

## Pseudocode

```
CATEGORIES = {
  "resources": crawl_resources_sub_pages(landing="https://www.orcina.com/resources/"),
  "examples":  enumerate_examples(index="https://www.orcina.com/resources/documentation/examples/"),
  "training":  download_and_extract_zip("…An%20introduction%20to%20the%20Python%20interface%20to%20OrcaFlex.zip"),
  "releases":  parse_release_notes(index="https://www.orcina.com/releases/"),
  "news":      crawl_news_feed(index="https://www.orcina.com/news/"),
}

function ingest_extended(output_root):
    base = output_root / "orcina" / "extended"
    summary = {}
    for cat, items in CATEGORIES.items():
        (base / cat).mkdir(parents=True, exist_ok=True)
        summary[cat] = run_category(cat, items, base / cat)
    write base / "index.json"
    return summary

function download_and_extract_zip(url, dest):
    download to /tmp
    verify content-length < 50 MB (DoS guard)
    for member in zipfile.ZipFile(path).infolist():
        reject_if_absolute_or_dotdot(member.filename)   # path-traversal guard
        extract to dest/
    for each extracted file:
        if .md: copy with <!-- source: url --> header
        if .ipynb: convert to md via `jupyter nbconvert --to markdown` (or jupytext fallback)
        if .py: wrap in ```python fenced block
        if .txt/.rst: copy
        else: skip + log

function parse_release_notes(index_url):
    fetch index, find each version link (regex vX.Y), for each:
        fetch page, reuse html_to_markdown(), write releases/vX_Y.md
        extract "What's new" / "Bug fixes" headings into per-version sections

function crawl_news_feed(index_url):
    fetch index, find all <article> or post links, iterate pages, reuse html_to_markdown

function enumerate_examples(index_url):
    fetch catalog page, collect each example link (~54),
    for each: fetch → html_to_markdown → write examples/<slug>.md
    also capture category tags from catalog structure
```

Shared helpers (`html_to_markdown`, `fetch_page`) are imported from `ingest-orcina.py` or (preferred) `llm_wiki_common.py` if #2103 lands first. This plan does not mandate the extraction — if `llm_wiki_common.py` exists at implementation time, use it; otherwise `from ingest_orcina import html_to_markdown, fetch_page`.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/ingest-orcina-extended.py` | new ingester for the five categories |
| Create | `scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py` | unit tests with offline fixtures |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_example_page.html` | offline example-page fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_release_notes_v11_4.html` | offline release-notes fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_news_post.html` | offline news-post fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/training_bundle.zip` | tiny synthetic ZIP (readme.md + sample.ipynb + sample.py + ../evil.sh traversal test case) |
| Update | `docs/plans/README.md` | add this plan to index |

Notably **not** modifying `ingest-orcina.py` — the core-help ingester is unchanged; this is additive.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_example_page_converts` | example HTML → markdown with source header | fixture HTML | md contains `# <title>` and `<!-- source: ...`-->` |
| `test_enumerate_examples_finds_all` | catalog-page parser finds expected count | fixture catalog w/ 3 example links | list of 3 `(slug, url)` tuples |
| `test_release_notes_capture_version_heading` | release-notes page parser writes per-version file and extracts version string | fixture v11.4 page | output file named `v11_4.md`, contains `## What's new` |
| `test_news_post_converts` | news post HTML → markdown | fixture news HTML | md contains `# <title>` |
| `test_training_zip_extract_rejects_path_traversal` | zip with `../evil.sh` entry is refused | fixture zip containing traversal entry | raises `ValueError`; evil file NOT written to dest |
| `test_training_zip_extract_converts_ipynb_to_md` | `.ipynb` inside zip is converted to markdown | fixture zip with valid notebook | output file has `.md` extension and `#` headings |
| `test_training_zip_size_guard` | zip > 50 MB rejected before extract | fake content-length header > 50 MB | raises `ValueError` with "size guard" message |
| `test_extended_index_json_schema` | per-category index.json has required keys | run with mocked fetcher | `{"resources":{...},"examples":{...},"training":{...},"releases":{...},"news":{...}}` |
| `test_master_index_merge_extended` | master `index.json` gains `orcina.extended` section without dropping existing keys | pre-existing master with `orcaflex` | merged master has both `orcaflex` AND `orcina.extended` |

Tests never hit the network — all via fixtures + `monkeypatch` of `fetch_page`/`urllib.request.urlopen`.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` (full suite) passes — no regression on `test_resolve_wiki_path.py` or any sibling tests.
- [ ] `uv run python scripts/data/llm-wiki/ingest-orcina-extended.py --output-dir /tmp/wiki-smoke --categories examples` exits 0 and produces `≥ 20` markdown files under `/tmp/wiki-smoke/orcina/extended/examples/`.
- [ ] `uv run python scripts/data/llm-wiki/ingest-orcina-extended.py --output-dir /tmp/wiki-smoke --categories releases` exits 0 and produces at least one `vX_Y.md` file.
- [ ] Running the full script with `--categories all` (the default) exits 0 on a machine with `pdftotext` + `jupyter` (or `jupytext`) available.
- [ ] `ZipFile` path-traversal test case refuses to extract `../evil.sh` (verified by test).
- [ ] ZIP size-guard test refuses content-length > 50 MB (verified by test).
- [ ] `data/llm-wiki/index.json` gains `orcina.extended` section with per-category counts after run.
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "example"` against smoke dir returns at least one hit from examples corpus.
- [ ] Plan review artifacts present at `scripts/review/results/2026-04-24-plan-2124-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | filled after review |
| Codex | TBD | filled after review |
| Gemini | TBD | filled after review |

**Overall result:** TBD

---

## Risks and Open Questions

- **Risk — ZIP path-traversal:** untrusted archive extraction is a known security class. Mitigation: explicit pre-extract validation (`zipfile.Path` or manual `os.path.abspath` + `startswith(dest)` check) with dedicated test. Pinned as acceptance criterion.
- **Risk — ZIP size DoS:** large archive could exhaust disk. Mitigation: `Content-Length` pre-check (50 MB ceiling; training bundle is well below) + hard cap on total extracted bytes.
- **Risk — `jupyter nbconvert` dependency:** may not be installed. Mitigation: fallback to `jupytext` (lighter dep); if both missing, convert notebook JSON manually (pull `source` from each cell). Test: skip when neither tool available, emit WARN.
- **Risk — upstream page shape drift:** Orcina may reshape resources/examples/news pages, breaking selectors. Mitigation: fixtures pin the expected shape; plan-review should call out that this is a documented fragility.
- **Risk — 54 examples changes over time:** acceptance criterion uses `≥ 20` (not `== 54`) to avoid brittleness; actual count logged to summary.
- **Risk — dependency interaction with #2103:** if #2103 lands `llm_wiki_common.py` first, this ingester should import from it. Plan explicitly tolerates either order.
- **Open:** Should news/blog ingestion have a date-cutoff (only last N years) or ingest-all? Current plan: ingest-all; revisit if corpus size becomes unwieldy. Flag for user during approval.
- **Open:** Should training-ZIP extraction keep the original ZIP archive on disk (for audit) or delete after conversion? Current plan: delete; keep only the per-file markdown outputs.

---

## Complexity: T2

**T2** — single new ingester script with five category handlers, one test suite with offline fixtures, no mutation of existing ingester. Security-sensitive ZIP handling bumps it above T1 but remains well under T3.
