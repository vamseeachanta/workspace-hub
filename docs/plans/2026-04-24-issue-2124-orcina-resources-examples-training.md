# Plan for #2124: Extend llm-wiki ingestion to Orcina resources, examples, and training materials

> **Status:** draft (v2 — addresses r1 findings: Claude=MAJOR, Gemini=MINOR)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2124
> **Base commit:** `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` (HEAD at plan-drafting time; cite line numbers relative to this SHA)
> **Review artifacts (r1):** `scripts/review/results/20260424T151824Z-plan-2124.md-plan-claude.md` (MAJOR), `scripts/review/results/20260424T152024Z-plan-2124.md-plan-gemini.md` (MINOR)
> **Review artifacts (r2, pending):** `scripts/review/results/2026-04-24-plan-2124-v2-{claude,codex,gemini}.md`

---

## Attested Evidence

Independently-verifiable claims this v2 plan relies on. Each was checked against HEAD `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` on 2026-04-24:

| Claim | Verification method | Result |
|---|---|---|
| Issue #2124 OPEN | `gh issue view 2124` (per v1 evidence, not re-run in v2 drafting) | OPEN — carry-forward from v1 |
| Issue #2088 CLOSED (parent) | carry-forward from v1 | CLOSED |
| Issue #2140 CLOSED (path resolver) | carry-forward from v1 | CLOSED |
| `scripts/data/llm-wiki/ingest-orcina.py` exists | `ls scripts/data/llm-wiki/ingest*.py` | EXISTS (only hyphenated match) |
| `ingest-orcina.py` defines `html_to_markdown` at line 98, `fetch_page` at line 286 | `grep -n "^def " scripts/data/llm-wiki/ingest-orcina.py` | CONFIRMED (line numbers anchored to base SHA) |
| `ingest-orcina.py` master-index top-level keys are `generated`, `generator`, `issue`, `products`, `supplementary`, `papers` | Read of `ingest-orcina.py:581-612` | CONFIRMED — there is NO top-level `orcaflex`/`orcawave`/`orcfxapi` key; products are nested under `master_index["products"]` |
| No Python-level importers of `ingest-orcina` exist | `grep -rn "ingest.orcina\|ingest_orcina" scripts/ docs/` returns only CLI-invocation docstring (line 10), self-reference in master index (line 583), and doc-plan prose citations | CONFIRMED — rename safe w.r.t. Python imports |
| No runtime `data/llm-wiki/index.json` exists on this machine | `find /mnt/local-analysis/workspace-hub -path '*/llm-wiki/index.json'` returns empty | CONFIRMED — master index is a generated artifact, not committed |
| `scripts/data/llm-wiki/tests/` currently contains `__init__.py` + `test_resolve_wiki_path.py` only | `ls scripts/data/llm-wiki/tests/` | CONFIRMED |

Claims the plan does NOT attest (require live verification during implementation, not plan-approval):
- Orcina's `robots.txt` policy toward `/resources/`, `/releases/`, `/news/` (plan specifies consultation step; contents not pre-fetched).
- Exact pagination structure of Orcina's `/releases/` and `/news/` indexes (plan assumes HTML `rel="next"` or numeric query pagination with a depth cap; fixture-test covers both).
- Exact size of the training ZIP (plan uses compressed ≤ 50 MB and decompressed ≤ 500 MB as policy ceilings; actual bundle is expected to be well under both).

---

## Resource Intelligence Summary

### Existing repo code (anchored to base SHA `8c235f5e`)
- Found: `scripts/data/llm-wiki/ingest-orcina.py` (636 lines) — handles OrcaFlex/OrcaWave/OrcFxAPI help + a `SUPPLEMENTARY_URLS` list (resources page, papers page, papers-and-technical-notes, documentation, releases) via `ingest_supplementary()` and a PDF ingester `ingest_papers()` using `pdftotext`. Defines `html_to_markdown()` (line 98) and `fetch_page()` (line 286). Gap: supplementary coverage is shallow (landing pages only), examples are not enumerated, the Python training ZIP is not downloaded/unpacked, release notes are not parsed version-by-version, and the blog/news feed is not ingested.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — portable output-root resolver (#2140); this plan reuses it without change.
- Found: `scripts/data/llm-wiki/search-wiki.py` — reads master `index.json`; new categories (examples, training, releases, news) must register under the same master schema.
- Found: `scripts/data/llm-wiki/tests/` — contains only `__init__.py` and `test_resolve_wiki_path.py` at HEAD; no pre-existing Orcina-ingestion tests.
- Gap: no ZIP-download + safe-extract path (training material is a zipped bundle of Python notebooks + readme).
- Gap: no version-aware release-notes parser — each release is a separate page with its own changelog section.
- Gap: no examples-catalog scraper — ~54 OrcaFlex examples, each with a description page.

### Import-boundary decision (resolves r1 P1 #1)
The v1 plan's pseudocode `from ingest_orcina import html_to_markdown, fetch_page` is **broken** because the source file is `ingest-orcina.py` (hyphenated, not a legal Python module identifier). v2 resolves this by **Option A — extracting shared helpers into a new legally-named module `scripts/data/llm-wiki/orcina_common.py`**.

Rationale for Option A over the two alternatives:
- (Rejected) Option B: `importlib.util.spec_from_file_location` dynamic load — works but adds permanent implicit-import surface that is hard to static-analyze and friction for future tooling (mypy, import-linters).
- (Rejected) Option C: duplicate `html_to_markdown` + `fetch_page` into the new script — creates a drift-prone second copy of ~200 lines; any fix to the shared HTML parser would need to land twice.
- (Chosen) Option A: extract the two helpers (`html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page`) plus shared constants (`HEADERS`, `DELAY_SECONDS`) into `orcina_common.py`. Update `ingest-orcina.py` to `from orcina_common import ...`. New `ingest-orcina-extended.py` imports from the same module. Both scripts remain invokable as CLI via `python3 scripts/data/llm-wiki/<name>.py`.

**Breaking-change blast radius (investigated at plan-drafting time):**
- `grep -rn "ingest.orcina\|ingest-orcina\|ingest_orcina" scripts/ docs/` shows only: (a) the docstring line 10 `python3 scripts/data/llm-wiki/ingest-orcina.py ...`, (b) the self-reference `"generator": "ingest-orcina.py"` at line 583, (c) doc-plan prose citations. No CI workflow, cron, or other Python module imports the ingester.
- Therefore: **no breaking change to external callers from the helper extraction.** `ingest-orcina.py` filename itself stays hyphenated; only internal `def html_to_markdown` etc. move to `orcina_common.py`.

### Master-index merge contract (resolves r1 P2)
The v1 plan assumed a top-level `orcaflex` key sibling to `orcina.extended`. **Reading the actual `ingest-orcina.py:581-612` shows the real shape differs.** The master index produced by `ingest-orcina.py` has these top-level keys (verified at base SHA):

```
{
  "generated": "<iso timestamp>",
  "generator": "ingest-orcina.py",
  "issue": "https://github.com/vamseeachanta/workspace-hub/issues/2088",
  "products": { "orcaflex": {...}, "orcawave": {...}, "orcfxapi": {...} },
  "supplementary": { "page_count": N, "pages": [...] },
  "papers": { "paper_count": N, "total_words": N, "papers": [...] }
}
```

**There is no top-level `orcaflex` key.** Products are nested under `products`. v2 locks the merge contract accordingly: this plan adds a new top-level `extended` key (sibling to `products`, `supplementary`, `papers`). The extended key has shape:

```
"extended": {
  "generator": "ingest-orcina-extended.py",
  "categories": {
    "resources": { "page_count": N, "pages": [...] },
    "examples":  { "example_count": N, "examples": [...] },
    "training":  { "file_count": N, "files": [...], "source_zip_url": "..." },
    "releases":  { "version_count": N, "versions": [...] },
    "news":      { "post_count": N, "posts": [...] }
  }
}
```

The merge is additive: `ingest-orcina-extended.py` reads the existing master `index.json` (if present), adds/overwrites the `extended` key, and writes atomically via `tempfile + os.replace`. Existing keys (`products`, `supplementary`, `papers`, etc.) are preserved unchanged.

### Standards
Not applicable — documentation-pipeline issue.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/` — curated-wiki boundary. New extended-Orcina content continues to live under `data/llm-wiki/orcina/extended/…` (bulk ingest) rather than the curated wiki.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — durable-vs-transient boundary (#2209).

### Documents consulted
- Issue body #2124 — five named sources (resources, example descriptions, training ZIP, release notes, blog/news).
- Parent issue #2088 — CLOSED; defines the master `index.json` contract that v2 extends.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — operating model for llm-wiki outputs.
- `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md` — ecosystem roadmap.
- Upstream: https://www.orcina.com/resources/
- Upstream: https://www.orcina.com/resources/documentation/examples/
- Upstream: https://www.orcina.com/wp-content/uploads/training/An%20introduction%20to%20the%20Python%20interface%20to%20OrcaFlex.zip
- Upstream: https://www.orcina.com/releases/
- Upstream: https://www.orcina.com/news/

### Gaps identified (same as v1 — unchanged)
- No extended-resources scraper.
- No examples-catalog enumerator + description scraper.
- No ZIP downloader + safe extractor with decompression-bomb defense + per-file markdown conversion.
- No release-notes crawler with version-awareness and pagination.
- No news/blog crawler with pagination.

Distinct sources consulted: 9 (issue body, #2088, #2140, `ingest-orcina.py`, `resolve_wiki_path.py`, `#2205` plan, ecosystem-strengthening plan, marine-engineering wiki governance, `search-wiki.py`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v2) | `docs/plans/2026-04-24-issue-2124-orcina-resources-examples-training.md` |
| Shared helpers module (new, extracted) | `scripts/data/llm-wiki/orcina_common.py` |
| Extended ingester | `scripts/data/llm-wiki/ingest-orcina-extended.py` |
| Existing ingester (updated import only) | `scripts/data/llm-wiki/ingest-orcina.py` |
| Tests | `scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py` |
| Common-module tests | `scripts/data/llm-wiki/tests/test_orcina_common.py` |
| Test fixtures | `scripts/data/llm-wiki/tests/fixtures/orcina_example_page.html`, `.../orcina_release_notes_v11_4.html`, `.../orcina_news_post.html`, `.../training_bundle.zip`, `.../training_bombfixture.zip`, `.../releases_index_page1.html`, `.../releases_index_page2.html`, `.../news_index_page1.html`, `.../news_index_page2.html` |
| Output (runtime) | `data/llm-wiki/orcina/extended/{resources,examples,training,releases,news}/` |
| Master index | `data/llm-wiki/index.json` (gains top-level `extended` key; `products`/`supplementary`/`papers` preserved) |
| Plan reviews (r2) | `scripts/review/results/2026-04-24-plan-2124-v2-{claude,codex,gemini}.md` |

---

## Deliverable

A shared helpers module `orcina_common.py` plus a new `ingest-orcina-extended.py` that extends the existing Orcina ingestion to cover five new content classes — resources/videos/webinars, examples catalog (all ~54), Python-API training ZIP (downloaded with streamed-size enforcement, decompression-bomb-safe extraction, each file converted to markdown), per-version release notes with pagination, and news/blog posts with pagination — plus explicit polite-scraping policy (robots.txt consultation, User-Agent with contact, inter-request delay, retry+timeout), offline-fixture pytest coverage, and an atomically-merged `extended` section in the master `data/llm-wiki/index.json`.

---

## Pseudocode

```
# ── orcina_common.py (new — extraction of shared helpers) ────────────────
USER_AGENT = "workspace-hub-llm-wiki/1.1 (+https://github.com/vamseeachanta/workspace-hub; contact: vamsee.achanta@aceengineer.com)"
HEADERS = {"User-Agent": USER_AGENT}
POLITE_DELAY_SECONDS = 1.0      # min inter-request delay (was 0.3 in ingest-orcina; bumped for the broader crawl)
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 2        # exponential: 2, 4, 8

def fetch_page(url, *, timeout=REQUEST_TIMEOUT_SECONDS, max_retries=MAX_RETRIES) -> str | None:
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, socket.timeout) as e:
            if attempt == max_retries - 1:
                return None
            sleep(BACKOFF_BASE_SECONDS ** (attempt + 1))

def html_to_markdown(html, source_url=""):   # moved verbatim from ingest-orcina.py:98
    ...

def respect_robots(base="https://www.orcina.com", paths=[...]) -> dict[str, bool]:
    """Consult robots.txt once per run; return {path: allowed}. Cache in module-level dict."""
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{base}/robots.txt")
    rp.read()
    return {p: rp.can_fetch(USER_AGENT, f"{base}{p}") for p in paths}

def polite_sleep():
    time.sleep(POLITE_DELAY_SECONDS)


# ── ingest-orcina-extended.py (new) ───────────────────────────────────────
from orcina_common import (
    USER_AGENT, HEADERS, POLITE_DELAY_SECONDS, REQUEST_TIMEOUT_SECONDS,
    fetch_page, html_to_markdown, respect_robots, polite_sleep,
)

MAX_COMPRESSED_BYTES  = 50 * 1024 * 1024     # 50 MB compressed ceiling
MAX_EXTRACTED_BYTES   = 500 * 1024 * 1024    # 500 MB decompressed ceiling (10× compressed, justified below)
MAX_PAGINATION_DEPTH  = 20
EXAMPLES_MIN_EXPECTED = 40                   # tightened from v1's 20; see P3 resolution

CATEGORIES = {
  "resources": crawl_resources_sub_pages(landing="https://www.orcina.com/resources/"),
  "examples":  enumerate_examples(index="https://www.orcina.com/resources/documentation/examples/"),
  "training":  download_and_extract_zip("…An%20introduction%20to%20the%20Python%20interface%20to%20OrcaFlex.zip"),
  "releases":  parse_release_notes(index="https://www.orcina.com/releases/"),
  "news":      crawl_news_feed(index="https://www.orcina.com/news/"),
}

def ingest_extended(output_root):
    robots_decisions = respect_robots(paths=["/resources/", "/releases/", "/news/",
                                             "/resources/documentation/examples/",
                                             "/wp-content/uploads/training/"])
    for path, allowed in robots_decisions.items():
        if not allowed:
            log.warning(f"robots.txt DISALLOWS {path} — category will be skipped")
    base = output_root / "orcina" / "extended"
    summary = {}
    for cat, items in CATEGORIES.items():
        if not_allowed_by_robots(cat, robots_decisions):
            summary[cat] = {"skipped": True, "reason": "robots.txt"}
            continue
        (base / cat).mkdir(parents=True, exist_ok=True)
        summary[cat] = run_category(cat, items, base / cat)
    merge_into_master_index(output_root, summary)     # atomic write; see below
    return summary

def download_and_extract_zip(url, dest):
    # (1) HEAD-style check if Content-Length is present
    req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            declared = int(resp.headers.get("Content-Length", "0") or 0)
            content_type = resp.headers.get("Content-Type", "")
            if declared and declared > MAX_COMPRESSED_BYTES:
                raise ValueError(f"size guard: Content-Length {declared} > {MAX_COMPRESSED_BYTES}")
            # (P3) content-type probe — warn if not zip-ish; magic-bytes check after download confirms
            if content_type and "zip" not in content_type.lower() and "octet-stream" not in content_type.lower():
                log.warning(f"unexpected Content-Type={content_type}; will verify magic bytes")
    except urllib.error.HTTPError as e:
        if e.code != 405:   # HEAD not allowed — fall through to streamed GET
            raise

    # (2) Streamed GET with bytes-accumulator enforcement (P2: Content-Length is advisory)
    tmp = Path(tempfile.mkstemp(suffix=".zip")[1])
    bytes_read = 0
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS),
                                 timeout=REQUEST_TIMEOUT_SECONDS) as resp, open(tmp, "wb") as out:
        while chunk := resp.read(65536):
            bytes_read += len(chunk)
            if bytes_read > MAX_COMPRESSED_BYTES:
                out.close(); tmp.unlink(missing_ok=True)
                raise ValueError(f"size guard: streamed read exceeded {MAX_COMPRESSED_BYTES} bytes")
            out.write(chunk)

    # (3) Magic-bytes validation (P3) — first 4 bytes of a ZIP are PK\x03\x04
    with open(tmp, "rb") as f:
        magic = f.read(4)
    if magic[:2] != b"PK":
        tmp.unlink(missing_ok=True)
        raise ValueError(f"not a zip file: magic bytes {magic!r}")

    # (4) Decompression-bomb-safe extraction (P1 #2 fix)
    total_extracted = 0
    with zipfile.ZipFile(tmp) as zf:
        # Pre-extract: sum declared file_size fields; reject if already over cap
        declared_total = sum(info.file_size for info in zf.infolist())
        if declared_total > MAX_EXTRACTED_BYTES:
            tmp.unlink(missing_ok=True)
            raise ValueError(f"decompression guard: declared total {declared_total} > {MAX_EXTRACTED_BYTES}")
        for info in zf.infolist():
            # Path-traversal guard (existing from v1)
            safe_path = dest / info.filename
            if not str(safe_path.resolve()).startswith(str(dest.resolve())):
                raise ValueError(f"path traversal: {info.filename}")
            if info.filename.startswith("/") or ".." in Path(info.filename).parts:
                raise ValueError(f"path traversal: {info.filename}")
            # Streaming extract with running-bytes check (mid-extract enforcement)
            with zf.open(info) as src, open(safe_path, "wb") as dst:
                while chunk := src.read(65536):
                    total_extracted += len(chunk)
                    if total_extracted > MAX_EXTRACTED_BYTES:
                        dst.close(); safe_path.unlink(missing_ok=True); tmp.unlink(missing_ok=True)
                        raise ValueError(f"decompression bomb: extracted {total_extracted} > {MAX_EXTRACTED_BYTES}")
                    dst.write(chunk)
    tmp.unlink(missing_ok=True)

    # (5) Convert extracted files to markdown
    for extracted_file in dest.rglob("*"):
        if extracted_file.suffix == ".md":    copy_with_source_header(extracted_file, url)
        elif extracted_file.suffix == ".ipynb": convert_notebook_to_md(extracted_file, url)  # nbconvert → jupytext → raw-JSON fallback
        elif extracted_file.suffix == ".py":    wrap_py_in_fenced_md(extracted_file, url)
        elif extracted_file.suffix in (".txt", ".rst"): copy_as_md(extracted_file, url)
        else: log.info(f"skip {extracted_file.suffix}: {extracted_file}")

def iter_paginated(index_url, max_pages=MAX_PAGINATION_DEPTH):
    """Yield successive pages of an index by following rel='next' or ?paged=N.
       Caps at max_pages; logs WARN if cap is hit to signal potential truncation."""
    url = index_url
    for i in range(max_pages):
        html = fetch_page(url); polite_sleep()
        if html is None: return
        yield url, html
        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.find("a", rel="next") or soup.find("link", rel="next")
        if not next_link: return
        url = next_link.get("href")
        if not url: return
    log.warning(f"pagination cap {max_pages} hit at {index_url}; possible truncation")

def parse_release_notes(index_url):
    versions = []
    for page_url, html in iter_paginated(index_url):
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.select("a[href*='/releases/']"):
            version = extract_version_token(link["href"])   # e.g. "11.4" from "/releases/11.4/"
            if not version: continue
            version_html = fetch_page(link["href"]); polite_sleep()
            md, _ = html_to_markdown(version_html, link["href"])
            # Heading-match with graceful degradation (P3): try known headings, fall back to full-page
            section = extract_section(md, patterns=["What's new", "New features", "Bug fixes", "Fixes"])
            if section is None:
                log.warning(f"expected release-notes headings absent in {link['href']}; writing full page")
                section = md
            write_file(f"releases/v{version.replace('.','_')}.md", section)
            versions.append(version)
    return versions

def crawl_news_feed(index_url):
    posts = []
    for page_url, html in iter_paginated(index_url):
        for article in BeautifulSoup(html, "html.parser").find_all("article"):
            post_url = article.find("a")["href"]
            post_html = fetch_page(post_url); polite_sleep()
            md, _ = html_to_markdown(post_html, post_url)
            write_file(f"news/{slugify(post_url)}.md", md)
            posts.append(post_url)
    return posts

def enumerate_examples(index_url):
    html = fetch_page(index_url); polite_sleep()
    soup = BeautifulSoup(html, "html.parser")
    example_links = [a["href"] for a in soup.select("a[href*='/examples/']") if looks_like_example(a)]
    examples = []
    for link in example_links:
        page_html = fetch_page(link); polite_sleep()
        md, _ = html_to_markdown(page_html, link)
        write_file(f"examples/{slugify(link)}.md", md)
        examples.append(link)
    if len(examples) < EXAMPLES_MIN_EXPECTED:
        log.warning(f"examples count {len(examples)} < expected min {EXAMPLES_MIN_EXPECTED}; catalog may be under-enumerated")
    return examples

def merge_into_master_index(output_root, extended_summary):
    master_path = output_root / "index.json"
    existing = json.loads(master_path.read_text()) if master_path.exists() else {}
    existing["extended"] = {
        "generator": "ingest-orcina-extended.py",
        "generated": datetime.now(timezone.utc).isoformat(),
        "categories": extended_summary,
    }
    # Atomic concurrent-run-safe write (P3)
    tmp = master_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(existing, indent=2, sort_keys=True))
    os.replace(tmp, master_path)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/orcina_common.py` | extract shared helpers (`html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page`, `HEADERS`, `USER_AGENT`) into legally-named module; add retry/timeout/polite-delay/robots helpers |
| Update | `scripts/data/llm-wiki/ingest-orcina.py` | replace internal defs with `from orcina_common import ...`; bump `User-Agent` version string; remove duplicated constants. No behavioral change to existing ingest |
| Create | `scripts/data/llm-wiki/ingest-orcina-extended.py` | new ingester for the five categories with streamed size enforcement, decompression-bomb cap, pagination, polite scraping, atomic master-index merge |
| Create | `scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py` | unit tests with offline fixtures |
| Create | `scripts/data/llm-wiki/tests/test_orcina_common.py` | covers retry/timeout, robots-cache, fetch_page failure paths |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_example_page.html` | offline example-page fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_release_notes_v11_4.html` | offline release-notes fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_news_post.html` | offline news-post fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/releases_index_page1.html` | pagination fixture — contains `<link rel="next" href="…page2">` |
| Create | `scripts/data/llm-wiki/tests/fixtures/releases_index_page2.html` | terminal pagination page |
| Create | `scripts/data/llm-wiki/tests/fixtures/news_index_page1.html` | pagination fixture — news variant |
| Create | `scripts/data/llm-wiki/tests/fixtures/news_index_page2.html` | terminal news-pagination page |
| Create | `scripts/data/llm-wiki/tests/fixtures/training_bundle.zip` | tiny synthetic ZIP (readme.md + sample.ipynb + sample.py + one `../evil.sh` entry for traversal test) |
| Create | `scripts/data/llm-wiki/tests/fixtures/training_bombfixture.zip` | crafted zip whose per-member declared `file_size` sums exceed MAX_EXTRACTED_BYTES, OR whose streamed extraction exceeds the cap mid-run |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_example_page_converts` | example HTML → markdown with source header | fixture HTML | md contains `# <title>` and `<!-- source: …-->` |
| `test_enumerate_examples_finds_all` | catalog-page parser finds expected count | fixture catalog w/ 3 example links | list of 3 `(slug, url)` tuples |
| `test_enumerate_examples_warns_under_threshold` | logs WARN when count < `EXAMPLES_MIN_EXPECTED` | fixture with 2 links | caplog contains "under-enumerated" |
| `test_release_notes_capture_version_heading` | release-notes page parser writes per-version file and extracts version string | fixture v11.4 page | output file named `v11_4.md`, contains `## What's new` |
| `test_release_notes_graceful_when_headings_absent` | falls back to full-page write + WARN | fixture with no known heading | md written, caplog contains "full page" |
| `test_release_notes_pagination_follows_rel_next` | crawler walks 2 pages | `releases_index_page1.html` has `rel=next` → `..._page2.html` | fetches both pages; depth cap not hit |
| `test_release_notes_pagination_cap_enforced` | crawler stops at `MAX_PAGINATION_DEPTH`, emits WARN | fake 25-page chain | exactly 20 pages fetched; WARN logged |
| `test_news_post_converts` | news post HTML → markdown | fixture news HTML | md contains `# <title>` |
| `test_news_pagination_follows_rel_next` | news crawler walks 2 pages | `news_index_page1.html` + `_page2.html` | both pages processed |
| `test_training_zip_extract_rejects_path_traversal` | zip with `../evil.sh` entry refused | fixture zip containing traversal entry | raises `ValueError`; no evil file written |
| `test_training_zip_extract_converts_ipynb_to_md` | `.ipynb` inside zip converted to md | fixture zip with valid notebook | `.md` file produced with `#` headings |
| `test_training_zip_ipynb_fallback_raw_json_parse` | when neither nbconvert nor jupytext is available, raw-JSON cell-source fallback runs | fixture + monkeypatched-missing tools | md file produced from cell sources |
| `test_training_zip_compressed_size_header_guard` | pre-check rejects Content-Length > 50 MB | mocked HEAD response with large Content-Length | raises `ValueError` with "size guard" |
| `test_training_zip_compressed_size_streamed_guard` | streamed GET aborts when bytes exceed cap even if header is missing | mocked response with no Content-Length, 60 MB body | raises `ValueError` after 50 MB read; no zip written |
| `test_training_zip_extract_rejects_decompression_bomb` | cumulative-decompressed-bytes cap enforced | `training_bombfixture.zip` with declared `file_size` > 500 MB | raises `ValueError` with "decompression guard" |
| `test_training_zip_extract_rejects_streamed_bomb` | mid-extract cap catches archives that lie about `file_size` | fixture with small declared `file_size` but large actual content | raises `ValueError` with "decompression bomb" mid-extract |
| `test_training_zip_rejects_non_zip_content_type` | content-type + magic-bytes validation | fixture serving HTML with `.zip` URL | raises `ValueError` with "not a zip file" |
| `test_fetch_page_retries_and_times_out` | retry + timeout policy honored | mocked `urlopen` raising `URLError` then succeeding | 2 retries then success; max 3 attempts total |
| `test_fetch_page_returns_none_after_max_retries` | returns None when all retries exhausted | always-failing mock | None returned; no exception propagated |
| `test_polite_delay_between_requests` | `polite_sleep` invoked between fetches | monkeypatched `time.sleep` | at least N-1 sleep calls for N fetches |
| `test_respect_robots_caches_and_consults` | robots.txt read once per run | fixture robots.txt + N `can_fetch` calls | only one HTTP read; per-path decisions correct |
| `test_respect_robots_disallow_skips_category` | category skipped + summary `{"skipped": true, "reason": "robots.txt"}` when disallowed | fixture robots.txt disallowing `/news/` | news category not crawled; summary marks skipped |
| `test_extended_index_json_schema` | per-category index.json has required keys | run with mocked fetcher | `{"resources":{...},"examples":{...},"training":{...},"releases":{...},"news":{...}}` |
| `test_master_index_merge_extended_real_shape` | master `index.json` gains `extended` key alongside real top-level keys (`products`, `supplementary`, `papers`) without dropping them | pre-existing master with `products` (dict with `orcaflex`/`orcawave`/`orcfxapi`), `supplementary`, `papers` | merged master has ALL original keys PLUS `extended` |
| `test_master_index_merge_atomic_write` | atomic write uses `os.replace` — no half-written file observable | monkeypatched `json.dumps` to raise mid-write | original master unchanged; no `.json.tmp` left behind |

Tests never hit the network — all via fixtures + `monkeypatch` of `fetch_page`/`urllib.request.urlopen`.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_orcina_common.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` (full suite) passes — no regression on `test_resolve_wiki_path.py`.
- [ ] `uv run python scripts/data/llm-wiki/ingest-orcina.py --output-dir /tmp/wiki-smoke-base --products orcaflex` still exits 0 after helper extraction (post-refactor smoke).
- [ ] `uv run python scripts/data/llm-wiki/ingest-orcina-extended.py --output-dir /tmp/wiki-smoke --categories examples` exits 0 and produces `≥ 40` markdown files under `/tmp/wiki-smoke/orcina/extended/examples/` (tightened from v1's `≥ 20`).
- [ ] `uv run python scripts/data/llm-wiki/ingest-orcina-extended.py --output-dir /tmp/wiki-smoke --categories releases` exits 0 and produces at least one `vX_Y.md` file; log-summary reports version-count.
- [ ] Running the full script with `--categories all` (default) exits 0 on a machine with `pdftotext` + `jupyter` (or `jupytext`) available.
- [ ] ZIP path-traversal test refuses to extract `../evil.sh` (verified by test).
- [ ] ZIP Content-Length header-guard test refuses `Content-Length` > 50 MB (verified by test).
- [ ] ZIP streamed-size-guard test refuses 60 MB body with missing `Content-Length` (verified by test).
- [ ] ZIP decompression-bomb test refuses declared `file_size` total > 500 MB (verified by test).
- [ ] ZIP streamed-bomb test refuses archive whose actual extracted bytes exceed cap mid-run (verified by test).
- [ ] ZIP non-zip-content test raises `ValueError` on HTML-masquerading-as-zip (verified by test).
- [ ] Pagination test demonstrates 2-page walk via `rel="next"` for both release-notes and news (verified by test).
- [ ] `data/llm-wiki/index.json` gains `extended` section with per-category counts after run; `products`, `supplementary`, `papers` preserved unchanged (verified by merge test against real shape).
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "example"` against smoke dir returns at least one hit from examples corpus.
- [ ] `robots.txt` consultation happens once per run (visible in log) and disallowed categories are skipped-with-reason (verified by test).
- [ ] Plan review artifacts (r2) present at `scripts/review/results/2026-04-24-plan-2124-v2-{claude,codex,gemini}.md`.

---

## Build Sequence (explicit, P1/P2 fixes step-by-step)

1. **Extract shared helpers (P1 #1 resolution).** Create `scripts/data/llm-wiki/orcina_common.py`. Move `html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page` from `ingest-orcina.py` verbatim. Move `HEADERS`, `USER_AGENT`, `DELAY_SECONDS` (rename to `POLITE_DELAY_SECONDS`, bump to 1.0). Add new helpers: `respect_robots`, `polite_sleep`, retry-wrapped `fetch_page`.
2. **Update existing ingester.** Replace internal defs in `ingest-orcina.py` with `from orcina_common import ...`. Run existing smoke: `python3 scripts/data/llm-wiki/ingest-orcina.py --output-dir /tmp/wiki-smoke-base --products orcaflex` must still exit 0.
3. **Write `test_orcina_common.py`.** Cover retry/timeout, robots cache, fetch_page failure paths. Run green before moving on.
4. **Verify live master-index shape (P2 resolution).** Run `ingest-orcina.py` once locally; `jq 'keys' data/llm-wiki/index.json` — confirm shape matches the `generated|generator|issue|products|supplementary|papers` contract documented above. If shape differs, update v2 plan and re-review.
5. **Write `ingest-orcina-extended.py` core.** Add constants (`MAX_COMPRESSED_BYTES`, `MAX_EXTRACTED_BYTES`, `MAX_PAGINATION_DEPTH`, `EXAMPLES_MIN_EXPECTED`). Stub out `merge_into_master_index` with atomic write.
6. **Implement `download_and_extract_zip` with ALL four guards in order (P1 #2 + P2 resolutions):** (a) HEAD content-length pre-check, (b) streamed GET with running-bytes abort, (c) magic-bytes + content-type validation, (d) pre-extract declared-total `file_size` cap, (e) mid-extract cumulative-extracted-bytes cap. Write tests for each guard before the next guard lands.
7. **Implement pagination helper `iter_paginated`** with `MAX_PAGINATION_DEPTH`. Use it in `parse_release_notes` and `crawl_news_feed`. Write pagination tests against fixtures before exercising the live crawl.
8. **Implement `enumerate_examples`** with `EXAMPLES_MIN_EXPECTED = 40` tightening and under-threshold WARN.
9. **Implement `parse_release_notes`** with graceful-degradation fallback when known headings are absent.
10. **Implement `crawl_resources_sub_pages`** (walks the landing page for sub-pages, fetches each).
11. **Implement `crawl_news_feed`** using `iter_paginated`.
12. **Wire up `respect_robots`** — call once at `ingest_extended` entry, thread allow/disallow decisions into each category.
13. **Implement `merge_into_master_index`** with `tempfile + os.replace` atomic write. Write `test_master_index_merge_extended_real_shape` against the real pre-existing master produced in step 4. Write `test_master_index_merge_atomic_write`.
14. **Run full test suite + smoke the CLI** with `--categories examples` (live), then `--categories all`. Confirm `≥ 40` examples captured, master index has all original keys plus `extended`.
15. **Dispatch r2 cross-review** (Claude / Codex / Gemini). Address findings or iterate; do NOT self-approve.

---

## Risks and Open Questions

- **Risk — ZIP path-traversal:** explicit pre-extract validation + dedicated test. Unchanged from v1.
- **Risk — ZIP compressed-size DoS:** now mitigated by BOTH header pre-check AND streamed running-bytes abort (P2 resolution).
- **Risk — ZIP decompression-bomb:** NEW in v2. Mitigated by pre-extract declared-total cap + mid-extract cumulative-bytes cap at 500 MB. Justification: training bundle is expected < 10 MB; 500 MB ceiling is 50× expected-size margin and 10× compressed ceiling. Sized to accommodate any reasonable training expansion without permitting a gigabyte-scale runaway.
- **Risk — ZIP content masquerade:** mitigated by Content-Type check + magic-bytes probe (P3 resolution).
- **Risk — `jupyter nbconvert` dependency:** fallback chain is `nbconvert` → `jupytext` → raw-JSON cell-source parse. No category is silently skipped.
- **Risk — upstream page shape drift:** fixtures pin expected shape; release-notes heading-match now has graceful-degradation fallback (P3 resolution).
- **Risk — pagination truncation:** mitigated by `iter_paginated` with cap + WARN when cap hit (P2 resolution).
- **Risk — polite-scraping / rate-limiting:** explicit User-Agent with contact email, `robots.txt` consultation once per run, `POLITE_DELAY_SECONDS = 1.0` between each fetch, retry with exponential backoff (2→4→8s), 30s per-request timeout, max 3 attempts (P2 resolutions, addresses Gemini and Claude P2s).
- **Risk — concurrent-run race on master `index.json`:** atomic write via `tempfile + os.replace` (P3 resolution). No file locking — convention is single-writer; concurrent invocations will last-writer-wins, which is acceptable for a generated artifact.
- **Risk — helper extraction regression:** `ingest-orcina.py` is mutated (import rewrite). Mitigation: step-2 smoke must pass before any new ingester work; no behavioral change to existing functions.
- **Risk — dependency interaction with #2103:** if #2103 lands `llm_wiki_common.py` first, this plan's `orcina_common.py` may become duplicative. Reconciliation: #2103's common module can re-export from `orcina_common` or vice versa; pick at implementation time based on which lands first. Not a blocker.
- **Open — news date-cutoff:** ingest-all for now; revisit if corpus size becomes unwieldy. Flag for user during approval.
- **Open — training-ZIP retention:** deleted after extraction; originals are reachable via the `source_zip_url` field on each training file's header.
- **Open — partial-failure policy (Gemini question):** if one example fails to download, log WARN and continue; a single failure does not abort the whole category. Log summary reports per-category failure count.
- **Deferred (tracked as follow-up):** `--dry-run` flag for CI smoke-checks. Nice-to-have; not a P1/P2. Filed as a follow-up issue if this plan ships without it.
- **Deferred (tracked as follow-up):** reproducible-output ordering (sorted keys in `index.json`). `merge_into_master_index` uses `sort_keys=True` so the top-level is stable; per-category list order follows crawl order. If bit-identical reruns become a requirement, sort category lists by a stable key (e.g. URL).

---

## Adversarial Review Summary

| Provider | Verdict (r1) | Verdict (r2) | Key findings |
|---|---|---|---|
| Claude | MAJOR (2 P1s, 5 P2s, 4 P3s) | TBD after r2 | Both P1s resolved in v2: (1) helper-extraction via `orcina_common.py`; (2) decompression-bomb cap + dedicated test. All P2s resolved. |
| Codex | not run in r1 (sandbox-blocked dispatch) | TBD | — |
| Gemini | MINOR (1 P2, 1 P3) | TBD after r2 | Both resolved: (1) retry+timeout+rate-limit policy in `orcina_common.py`; (2) Attested Evidence block added above. |

**Overall result (r1):** MAJOR — blocked on P1 fixes. **v2 addresses all P1s and P2s.** r2 review pending.

---

## Complexity: T2

**T2** — one extracted helpers module + one new ingester script with five category handlers, two test files with offline fixtures, small import-rewrite in the existing ingester. Security-sensitive ZIP handling (now with two independent size guards) + multi-category crawl + atomic-merge bumps it above T1 but remains well under T3. No cross-repo changes; no schema migration of already-written data.
