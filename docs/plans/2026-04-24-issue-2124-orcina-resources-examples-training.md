# Plan for #2124: Extend llm-wiki ingestion to Orcina resources, examples, and training materials

> **Status:** draft (v3 — addresses r2 findings)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2124
> **Base commit:** `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` (HEAD at v3 plan-drafting time; cite line numbers relative to this SHA)
> **Review artifacts (r1):** `scripts/review/results/20260424T151824Z-plan-2124.md-plan-claude.md` (MAJOR), `scripts/review/results/20260424T152024Z-plan-2124.md-plan-gemini.md` (MINOR)
> **Review artifacts (r2):** `scripts/review/results/20260424T184113Z-plan-2124-v2.md-plan-claude.md` (MAJOR), `scripts/review/results/20260424T184343Z-plan-2124-v2.md-plan-gemini.md` (MINOR)
> **Review artifacts (r3, pending):** `scripts/review/results/2026-04-24-plan-2124-v3-{claude,codex,gemini}.md`

---

## Review History (closure summary)

Short table mapping every r1/r2 finding to its resolution in this plan, so future reviewers can see closure at a glance.

### r1 (resolved in v2)
| Finding | Class | Resolution |
|---|---|---|
| `from ingest_orcina import …` impossible because source is `ingest-orcina.py` (hyphenated) | P1 | Resolved in v2: shared helpers extracted into legally-named `orcina_common.py` (underscore). Carried forward in v3. |
| No decompression-bomb cap on training-zip extraction | P1 | Resolved in v2: added `MAX_EXTRACTED_BYTES = 500 MB` with pre-extract declared-total check AND mid-extract streamed cumulative-bytes check. Carried forward in v3. |
| Retry / timeout / rate-limit policy unspecified | P2 | Resolved in v2: `POLITE_DELAY_SECONDS = 1.0`, `REQUEST_TIMEOUT_SECONDS = 30`, `MAX_RETRIES = 3` with exponential backoff. Carried forward in v3. |
| No Attested Evidence block | P2 | Resolved in v2; re-attested and extended in v3 for `_convert_element`/`_convert_table` and `beautifulsoup4` dep. |
| Misnamed top-level `orcaflex` key assumption | P2 | Resolved in v2 via actual-shape verification against `ingest-orcina.py:581-612`. Carried forward in v3. |

### r2 (resolved in v3)
| Finding | Class | Resolution in v3 |
|---|---|---|
| **Hyphenated filename recurrence** — v2 created a NEW `ingest-orcina-extended.py` that `test_ingest_orcina_extended.py` cannot import | **P1** | **Resolved (Option A):** new file is `scripts/data/llm-wiki/ingest_orcina_extended.py` (underscore). All references updated: Files-to-Change, pseudocode, TDD list, Build Sequence, Acceptance Criteria, Attested Evidence commands. Explicit note added: "underscore form is a legal Python module identifier; prevents repeat of r1 import failure." No hyphen remains in ANY new Python module path or import. |
| **CATEGORIES dict eagerly crawls at import time** — `CATEGORIES = {"resources": crawl_resources_sub_pages(...), ...}` in v2 literally invokes crawlers at module top level, bypassing robots.txt gate and breaking monkeypatched tests | **P1** | **Resolved:** CATEGORIES is now a **bare callable mapping** — keys to function references, NOT invocations. Crawlers are called only from inside `ingest_extended()` after `respect_robots()` returns. New TDD row `test_import_ingest_orcina_extended_does_not_fetch_network` monkeypatches `urllib.request.urlopen` and `socket.socket` to raise, then imports the module to prove no network call. Explicit sentence added in pseudocode comment: "CATEGORIES is a bare function mapping; crawlers are NOT invoked at import time. The robots.txt gate runs before any crawler is called." |
| `_convert_element` / `_convert_table` existence not attested | P2 | **Resolved:** live-checked against HEAD `8c235f5e`; both exist at exact names — `_convert_element` at line 135, `_convert_table` at line 261. Added to Attested Evidence block with grep-output line numbers. Extraction plan confirmed unchanged. |
| `BeautifulSoup` new-dep claim not in Files-to-Change | P2 | **Resolved via live check:** `beautifulsoup4>=4.14.3` is ALREADY declared in root `pyproject.toml:12`, and `ingest-orcina.py` already imports `from bs4 import BeautifulSoup` at line 26. Therefore `bs4` is NOT a new dep for this plan. Attested Evidence block updated to document this; no Files-to-Change row needed for dep addition. Gemini's related question also answered. |
| `fetch_page` monkeypatch-target ambiguity | P2 | **Resolved:** pseudocode and TDD list both now specify that tests patch `ingest_orcina_extended.fetch_page` (the consuming module's bound name), NOT `orcina_common.fetch_page`. An explicit test-pattern example is shown in the TDD notes. |
| No cross-page dedup in `parse_release_notes` | P2 | **Resolved:** `parse_release_notes` now carries a `seen_releases: set[str]` across pagination iterations and skips already-seen versions. New TDD row `test_parse_release_notes_dedupes_across_pages` verifies no duplicate fetch occurs when the same version link appears on two index pages. |
| Idempotency / rerun policy undefined | P3 | Addressed in Risks section: "always re-fetch" is the explicit policy for v3; incremental-skip is deferred to a follow-up issue. |
| `crawl_resources_sub_pages` signature unspecified | P3 | Addressed: pseudocode now includes a minimal signature + fan-out behavior + stop conditions. |
| `robots.txt` UA token-match | P3 | Addressed: `respect_robots()` now passes the short UA token `"workspace-hub-llm-wiki"` to `rp.can_fetch()`, not the full UA-with-contact string. |
| **Robots.txt exception for training-zip endpoint** (Gemini P3) | P3 | **Resolved:** explicit sentence added — if robots.txt disallows `/wp-content/uploads/training/` specifically, log WARNING and skip (do NOT proceed). Listed in Don't-Fetch guidance. |
| **Master-index merge idempotency under concurrency** (Gemini P3) | P3 | **Resolved:** pseudocode `merge_into_master_index` now uses `tempfile.NamedTemporaryFile(dir=master_path.parent, delete=False)` (Gemini's exact suggestion) — unique per-process temp filename, so concurrent runs cannot clobber each other's staging file before `os.replace`. Confirmed in Risks section. |

---

## Attested Evidence

Independently-verifiable claims this v3 plan relies on. Each was checked against HEAD `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` on 2026-04-24. New checks marked (v3).

| Claim | Verification method | Result |
|---|---|---|
| Issue #2124 OPEN | `gh issue view 2124` (per v1 evidence, not re-run in v2/v3 drafting) | OPEN — carry-forward |
| Issue #2088 CLOSED (parent) | carry-forward from v1 | CLOSED |
| Issue #2140 CLOSED (path resolver) | carry-forward from v1 | CLOSED |
| `scripts/data/llm-wiki/ingest-orcina.py` exists | `ls scripts/data/llm-wiki/ingest*.py` | EXISTS (only hyphenated match) |
| `ingest-orcina.py` defines `html_to_markdown` at line 98, `fetch_page` at line 286 | `grep -n "^def " scripts/data/llm-wiki/ingest-orcina.py` | CONFIRMED (line numbers anchored to base SHA) |
| **(v3) `ingest-orcina.py` defines `_convert_element` at line 135 and `_convert_table` at line 261** | `grep -n "def _convert_element\|def _convert_table" scripts/data/llm-wiki/ingest-orcina.py` → `135:def _convert_element(element, lines, depth=0):` and `261:def _convert_table(table, lines):` | **CONFIRMED — both exist at the exact names the extraction plan assumes** |
| **(v3) `beautifulsoup4` is ALREADY a declared dep** | `grep -n "beautifulsoup\|bs4" pyproject.toml` → `pyproject.toml:12: "beautifulsoup4>=4.14.3",`; `grep -n "bs4" scripts/data/llm-wiki/ingest-orcina.py` → `26:from bs4 import BeautifulSoup` and `137:from bs4 import NavigableString, Tag` | **CONFIRMED — bs4 is already declared in root `pyproject.toml:12` and already imported in `ingest-orcina.py:26`. Not a new dep; no Files-to-Change row needed for dependency addition.** |
| `ingest-orcina.py` master-index top-level keys are `generated`, `generator`, `issue`, `products`, `supplementary`, `papers` | Read of `ingest-orcina.py:581-612` | CONFIRMED — no top-level `orcaflex` key; products are nested under `master_index["products"]` |
| No Python-level importers of `ingest-orcina` exist | `grep -rn "ingest.orcina\|ingest_orcina" scripts/ docs/` returns only CLI-invocation docstring, self-reference in master index, and doc-plan prose citations | CONFIRMED — rename safe w.r.t. Python imports |
| No runtime `data/llm-wiki/index.json` exists on this machine | `find /mnt/local-analysis/workspace-hub -path '*/llm-wiki/index.json'` returns empty | CONFIRMED — master index is a generated artifact, not committed |
| `scripts/data/llm-wiki/tests/` currently contains `__init__.py` + `test_resolve_wiki_path.py` only | `ls scripts/data/llm-wiki/tests/` | CONFIRMED |

Claims the plan does NOT attest (require live verification during implementation, not plan-approval):
- Orcina's `robots.txt` policy toward `/resources/`, `/releases/`, `/news/`, `/resources/documentation/examples/`, and `/wp-content/uploads/training/` (plan specifies consultation step + per-path skip; contents not pre-fetched).
- Exact pagination structure of Orcina's `/releases/` and `/news/` indexes (plan assumes HTML `rel="next"` or numeric query pagination with a depth cap; fixture-test covers both).
- Exact size of the training ZIP (plan uses compressed ≤ 50 MB and decompressed ≤ 500 MB as policy ceilings; actual bundle is expected to be well under both).

---

## Resource Intelligence Summary

### Existing repo code (anchored to base SHA `8c235f5e`)
- Found: `scripts/data/llm-wiki/ingest-orcina.py` (636 lines) — handles OrcaFlex/OrcaWave/OrcFxAPI help + a `SUPPLEMENTARY_URLS` list (resources page, papers page, papers-and-technical-notes, documentation, releases) via `ingest_supplementary()` and a PDF ingester `ingest_papers()` using `pdftotext`. Defines `html_to_markdown()` (line 98), `_convert_element()` (line 135), `_convert_table()` (line 261), and `fetch_page()` (line 286). Already imports `from bs4 import BeautifulSoup` at line 26 and `from bs4 import NavigableString, Tag` at line 137. Gap: supplementary coverage is shallow (landing pages only), examples are not enumerated, the Python training ZIP is not downloaded/unpacked, release notes are not parsed version-by-version, and the blog/news feed is not ingested.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — portable output-root resolver (#2140); this plan reuses it without change.
- Found: `scripts/data/llm-wiki/search-wiki.py` — reads master `index.json`; new categories (examples, training, releases, news) must register under the same master schema.
- Found: `scripts/data/llm-wiki/tests/` — contains only `__init__.py` and `test_resolve_wiki_path.py` at HEAD; no pre-existing Orcina-ingestion tests.
- Found: `pyproject.toml:12` declares `"beautifulsoup4>=4.14.3"` — already a workspace dep; new code can freely use `bs4` without a manifest change.
- Gap: no ZIP-download + safe-extract path (training material is a zipped bundle of Python notebooks + readme).
- Gap: no version-aware release-notes parser — each release is a separate page with its own changelog section.
- Gap: no examples-catalog scraper — ~54 OrcaFlex examples, each with a description page.

### Import-boundary decision (resolves r1 P1 #1 and r2 P1 #1)
The v1 plan's pseudocode `from ingest_orcina import html_to_markdown, fetch_page` was broken because the source file is `ingest-orcina.py` (hyphenated, not a legal Python module identifier). v2 resolved that by extracting shared helpers into a new legally-named module `scripts/data/llm-wiki/orcina_common.py`.

**v3 tightening (resolves r2 P1 #1):** the new extended ingester — which v2 named `ingest-orcina-extended.py` — is renamed to **`ingest_orcina_extended.py`** (underscore). This is **Option A** from the r2 review: for a new file we control end-to-end, the underscore name is the clean fix. Rationale:
- **Chosen — Option A (underscore):** `scripts/data/llm-wiki/ingest_orcina_extended.py` is a legal Python module identifier; `test_ingest_orcina_extended.py` can do `import ingest_orcina_extended` or `from ingest_orcina_extended import …` directly with no import-machinery workaround. No precedent/compat concerns — this is a new file.
- **Rejected — Option B (hyphenated CLI shim + `orcina_extended.py` library):** keeping a thin `ingest-orcina-extended.py` shim as `if __name__ == "__main__": runpy.run_module("orcina_extended", …)` is valid but adds a second file with no functional benefit, and risks future contributors adding logic back into the shim. The underscore-filename option is strictly simpler.
- **Rejected — dynamic `importlib.util.spec_from_file_location`:** same "permanent implicit-import surface" objection that was applied to the v2 extraction decision.

**Why underscore:** legal Python module identifier; prevents repeat of r1 import failure on a new-file path we control.

The existing `ingest-orcina.py` (hyphenated) filename is **not changed** — its `def` bodies were extracted to `orcina_common.py` in v2 so the filename no longer matters for import. Only the CLI invocation path `python3 scripts/data/llm-wiki/ingest-orcina.py ...` uses that filename, and hyphens are fine there.

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

**There is no top-level `orcaflex` key.** Products are nested under `products`. v3 locks the merge contract accordingly: this plan adds a new top-level `extended` key (sibling to `products`, `supplementary`, `papers`). The extended key has shape:

```
"extended": {
  "generator": "ingest_orcina_extended.py",
  "categories": {
    "resources": { "page_count": N, "pages": [...] },
    "examples":  { "example_count": N, "examples": [...] },
    "training":  { "file_count": N, "files": [...], "source_zip_url": "..." },
    "releases":  { "version_count": N, "versions": [...] },
    "news":      { "post_count": N, "posts": [...] }
  }
}
```

The merge is additive: `ingest_orcina_extended.py` reads the existing master `index.json` (if present), adds/overwrites the `extended` key, and writes atomically via unique-named `tempfile.NamedTemporaryFile + os.replace`. Existing keys (`products`, `supplementary`, `papers`, etc.) are preserved unchanged.

### Standards
Not applicable — documentation-pipeline issue.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/` — curated-wiki boundary. New extended-Orcina content continues to live under `data/llm-wiki/orcina/extended/…` (bulk ingest) rather than the curated wiki.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — durable-vs-transient boundary (#2209).

### Documents consulted
- Issue body #2124 — five named sources (resources, example descriptions, training ZIP, release notes, blog/news).
- Parent issue #2088 — CLOSED; defines the master `index.json` contract that v3 extends.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — operating model for llm-wiki outputs.
- `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md` — ecosystem roadmap.
- Upstream: https://www.orcina.com/resources/
- Upstream: https://www.orcina.com/resources/documentation/examples/
- Upstream: https://www.orcina.com/wp-content/uploads/training/An%20introduction%20to%20the%20Python%20interface%20to%20OrcaFlex.zip
- Upstream: https://www.orcina.com/releases/
- Upstream: https://www.orcina.com/news/

### Gaps identified (same as v1/v2 — unchanged)
- No extended-resources scraper.
- No examples-catalog enumerator + description scraper.
- No ZIP downloader + safe extractor with decompression-bomb defense + per-file markdown conversion.
- No release-notes crawler with version-awareness and pagination.
- No news/blog crawler with pagination.

Distinct sources consulted: 10 (issue body, #2088, #2140, `ingest-orcina.py`, `resolve_wiki_path.py`, `#2205` plan, ecosystem-strengthening plan, marine-engineering wiki governance, `search-wiki.py`, root `pyproject.toml`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v3) | `docs/plans/2026-04-24-issue-2124-orcina-resources-examples-training.md` |
| Shared helpers module (new, extracted) | `scripts/data/llm-wiki/orcina_common.py` |
| Extended ingester (underscore — legal Python module) | `scripts/data/llm-wiki/ingest_orcina_extended.py` |
| Existing ingester (updated import only) | `scripts/data/llm-wiki/ingest-orcina.py` |
| Tests — extended ingester | `scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py` |
| Tests — common module | `scripts/data/llm-wiki/tests/test_orcina_common.py` |
| Test fixtures | `scripts/data/llm-wiki/tests/fixtures/orcina_example_page.html`, `.../orcina_release_notes_v11_4.html`, `.../orcina_news_post.html`, `.../training_bundle.zip`, `.../training_bombfixture.zip`, `.../releases_index_page1.html`, `.../releases_index_page2.html`, `.../releases_index_dup_page1.html`, `.../releases_index_dup_page2.html`, `.../news_index_page1.html`, `.../news_index_page2.html`, `.../orcina_robots.txt` |
| Output (runtime) | `data/llm-wiki/orcina/extended/{resources,examples,training,releases,news}/` |
| Master index | `data/llm-wiki/index.json` (gains top-level `extended` key; `products`/`supplementary`/`papers` preserved) |
| Plan reviews (r3) | `scripts/review/results/2026-04-24-plan-2124-v3-{claude,codex,gemini}.md` |

---

## Deliverable

A shared helpers module `orcina_common.py` plus a new **`ingest_orcina_extended.py`** (underscore — legal Python module identifier) that extends the existing Orcina ingestion to cover five new content classes — resources/videos/webinars, examples catalog (all ~54), Python-API training ZIP (downloaded with streamed-size enforcement, decompression-bomb-safe extraction, each file converted to markdown), per-version release notes with pagination AND cross-page deduplication, and news/blog posts with pagination — plus explicit polite-scraping policy (robots.txt consultation with per-path skip including training-zip path, short UA token for `can_fetch`, User-Agent with contact, inter-request delay, retry+timeout), offline-fixture pytest coverage including an import-time-network-abstinence test, and an atomically-merged `extended` section in the master `data/llm-wiki/index.json` with concurrency-safe unique-temp-filename writes.

---

## Pseudocode

```
# ── orcina_common.py (new — extraction of shared helpers) ────────────────
USER_AGENT_TOKEN   = "workspace-hub-llm-wiki"      # short token — passed to rp.can_fetch()
USER_AGENT         = f"{USER_AGENT_TOKEN}/1.1 (+https://github.com/vamseeachanta/workspace-hub; contact: vamsee.achanta@aceengineer.com)"
HEADERS            = {"User-Agent": USER_AGENT}
POLITE_DELAY_SECONDS    = 1.0      # min inter-request delay (was 0.3 in ingest-orcina; bumped for the broader crawl)
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES             = 3
BACKOFF_BASE_SECONDS    = 2        # exponential: 2, 4, 8

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

def _convert_element(element, lines, depth=0):  # moved verbatim from ingest-orcina.py:135
    ...

def _convert_table(table, lines):               # moved verbatim from ingest-orcina.py:261
    ...

def respect_robots(base="https://www.orcina.com", paths=[...]) -> dict[str, bool]:
    """Consult robots.txt once per run; return {path: allowed}. Cache in module-level dict.
       Uses short UA token `USER_AGENT_TOKEN` (not full UA with contact email) for can_fetch
       to avoid first-whitespace-token match pitfalls in some robots parsers."""
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{base}/robots.txt")
    rp.read()
    return {p: rp.can_fetch(USER_AGENT_TOKEN, f"{base}{p}") for p in paths}

def polite_sleep():
    time.sleep(POLITE_DELAY_SECONDS)


# ── ingest_orcina_extended.py (new — underscore form is a legal Python ───
# ──   module identifier; prevents repeat of r1 import failure) ───────────
from orcina_common import (
    USER_AGENT, USER_AGENT_TOKEN, HEADERS, POLITE_DELAY_SECONDS, REQUEST_TIMEOUT_SECONDS,
    fetch_page, html_to_markdown, respect_robots, polite_sleep,
)
# NOTE: tests monkeypatch `ingest_orcina_extended.fetch_page` (the bound name in THIS module),
#       NOT `orcina_common.fetch_page`. The `from …` import copies the reference at import time;
#       patching the source module after import has no effect on this module's binding.

MAX_COMPRESSED_BYTES  = 50 * 1024 * 1024     # 50 MB compressed ceiling
MAX_EXTRACTED_BYTES   = 500 * 1024 * 1024    # 500 MB decompressed ceiling (10× compressed, justified below)
MAX_PAGINATION_DEPTH  = 20
EXAMPLES_MIN_EXPECTED = 40                   # tightened from v1's 20; see P3 resolution

# ── CATEGORIES: a BARE FUNCTION MAPPING — crawlers are NOT invoked at import time. ──
#    The robots.txt gate runs in ingest_extended() BEFORE any crawler is called.
#    (Resolves r2 P1 #2: v2's `"resources": crawl_resources_sub_pages(...)` would have
#    executed the crawlers at module top level, bypassing robots and breaking monkeypatched tests.)
CATEGORIES = {
    "resources":     crawl_resources_sub_pages,
    "examples":      enumerate_examples,
    "training":      download_and_extract_zip,
    "releases":      parse_release_notes,
    "news":          crawl_news_feed,
}

# Per-category URL / target arguments — bound at call time inside ingest_extended().
CATEGORY_ARGS = {
    "resources":  {"landing":  "https://www.orcina.com/resources/"},
    "examples":   {"index_url": "https://www.orcina.com/resources/documentation/examples/"},
    "training":   {"url":       "https://www.orcina.com/wp-content/uploads/training/"
                                "An%20introduction%20to%20the%20Python%20interface%20to%20OrcaFlex.zip"},
    "releases":   {"index_url": "https://www.orcina.com/releases/"},
    "news":       {"index_url": "https://www.orcina.com/news/"},
}

# Map category → robots.txt path used for the allow/skip decision.
CATEGORY_ROBOTS_PATH = {
    "resources": "/resources/",
    "examples":  "/resources/documentation/examples/",
    "training":  "/wp-content/uploads/training/",       # Gemini P3 — training zip has its own path
    "releases":  "/releases/",
    "news":      "/news/",
}

def ingest_extended(output_root):
    robots_decisions = respect_robots(paths=list(CATEGORY_ROBOTS_PATH.values()))
    for path, allowed in robots_decisions.items():
        if not allowed:
            log.warning(f"robots.txt DISALLOWS {path} — category will be skipped")
    base = output_root / "orcina" / "extended"
    summary = {}
    for cat, crawler in CATEGORIES.items():
        path = CATEGORY_ROBOTS_PATH[cat]
        if not robots_decisions.get(path, True):
            # Explicit Don't-Fetch guidance — training path specifically may be disallowed
            # (Gemini P3). Do NOT proceed on any disallowed path.
            summary[cat] = {"skipped": True, "reason": f"robots.txt disallow {path}"}
            continue
        (base / cat).mkdir(parents=True, exist_ok=True)
        kwargs = dict(CATEGORY_ARGS[cat], dest=base / cat)
        summary[cat] = crawler(**kwargs)   # ← lazy invocation; first time any crawler runs
    merge_into_master_index(output_root, summary)     # atomic write with unique temp filename
    return summary

def crawl_resources_sub_pages(landing, dest):
    """Fetch the /resources/ landing page, enumerate in-scope sub-page links
       (descendant URLs under /resources/ EXCLUDING /resources/documentation/examples/
       which is handled by enumerate_examples), fetch each once, convert to markdown.
       Fan-out cap: first 50 unique sub-page links (guard against runaway crawl).
       Stop conditions: all links fetched, cap hit (WARN), or robots disallow (already gated)."""
    html = fetch_page(landing); polite_sleep()
    if html is None: return {"page_count": 0, "pages": []}
    soup = BeautifulSoup(html, "html.parser")
    links, seen = [], set()
    for a in soup.select("a[href*='/resources/']"):
        href = a.get("href", "")
        if not href or href in seen: continue
        if "/resources/documentation/examples/" in href: continue   # owned by examples category
        seen.add(href); links.append(href)
        if len(links) >= 50:
            log.warning(f"resources fan-out cap 50 hit on {landing}; potential under-enumeration"); break
    pages = []
    for link in links:
        page_html = fetch_page(link); polite_sleep()
        if page_html is None: continue
        md, _ = html_to_markdown(page_html, link)
        write_file(dest / f"{slugify(link)}.md", md)
        pages.append(link)
    return {"page_count": len(pages), "pages": pages}

def download_and_extract_zip(url, dest):
    # (1) HEAD-style check if Content-Length is present
    req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            declared = int(resp.headers.get("Content-Length", "0") or 0)
            content_type = resp.headers.get("Content-Type", "")
            if declared and declared > MAX_COMPRESSED_BYTES:
                raise ValueError(f"size guard: Content-Length {declared} > {MAX_COMPRESSED_BYTES}")
            if content_type and "zip" not in content_type.lower() and "octet-stream" not in content_type.lower():
                log.warning(f"unexpected Content-Type={content_type}; will verify magic bytes")
    except urllib.error.HTTPError as e:
        if e.code != 405:   # HEAD not allowed — fall through to streamed GET
            raise

    # (2) Streamed GET with bytes-accumulator enforcement (Content-Length is advisory)
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

    # (3) Magic-bytes validation — first 2 bytes of a ZIP are PK
    with open(tmp, "rb") as f:
        magic = f.read(4)
    if magic[:2] != b"PK":
        tmp.unlink(missing_ok=True)
        raise ValueError(f"not a zip file: magic bytes {magic!r}")

    # (4) Decompression-bomb-safe extraction
    total_extracted = 0
    with zipfile.ZipFile(tmp) as zf:
        declared_total = sum(info.file_size for info in zf.infolist())
        if declared_total > MAX_EXTRACTED_BYTES:
            tmp.unlink(missing_ok=True)
            raise ValueError(f"decompression guard: declared total {declared_total} > {MAX_EXTRACTED_BYTES}")
        for info in zf.infolist():
            safe_path = dest / info.filename
            if not str(safe_path.resolve()).startswith(str(dest.resolve())):
                raise ValueError(f"path traversal: {info.filename}")
            if info.filename.startswith("/") or ".." in Path(info.filename).parts:
                raise ValueError(f"path traversal: {info.filename}")
            with zf.open(info) as src, open(safe_path, "wb") as dst:
                while chunk := src.read(65536):
                    total_extracted += len(chunk)
                    if total_extracted > MAX_EXTRACTED_BYTES:
                        dst.close(); safe_path.unlink(missing_ok=True); tmp.unlink(missing_ok=True)
                        raise ValueError(f"decompression bomb: extracted {total_extracted} > {MAX_EXTRACTED_BYTES}")
                    dst.write(chunk)
    tmp.unlink(missing_ok=True)

    # (5) Convert extracted files to markdown
    files = []
    for extracted_file in dest.rglob("*"):
        if not extracted_file.is_file(): continue
        if extracted_file.suffix == ".md":            copy_with_source_header(extracted_file, url)
        elif extracted_file.suffix == ".ipynb":       convert_notebook_to_md(extracted_file, url)
        elif extracted_file.suffix == ".py":          wrap_py_in_fenced_md(extracted_file, url)
        elif extracted_file.suffix in (".txt", ".rst"): copy_as_md(extracted_file, url)
        else: log.info(f"skip {extracted_file.suffix}: {extracted_file}"); continue
        files.append(str(extracted_file.relative_to(dest)))
    return {"file_count": len(files), "files": files, "source_zip_url": url}

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

def parse_release_notes(index_url, dest):
    versions = []
    seen_releases: set[str] = set()    # (v3) cross-page dedup — resolves r2 P2
    for page_url, html in iter_paginated(index_url):
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.select("a[href*='/releases/']"):
            version = extract_version_token(link["href"])   # e.g. "11.4" from "/releases/11.4/"
            if not version: continue
            if version in seen_releases:
                log.debug(f"release-notes dedup: skipping already-seen version {version}")
                continue
            seen_releases.add(version)
            version_html = fetch_page(link["href"]); polite_sleep()
            md, _ = html_to_markdown(version_html, link["href"])
            section = extract_section(md, patterns=["What's new", "New features", "Bug fixes", "Fixes"])
            if section is None:
                log.warning(f"expected release-notes headings absent in {link['href']}; writing full page")
                section = md
            write_file(dest / f"v{version.replace('.','_')}.md", section)
            versions.append(version)
    return {"version_count": len(versions), "versions": versions}

def crawl_news_feed(index_url, dest):
    posts = []
    for page_url, html in iter_paginated(index_url):
        for article in BeautifulSoup(html, "html.parser").find_all("article"):
            a = article.find("a"); post_url = a["href"] if a else None
            if not post_url: continue
            post_html = fetch_page(post_url); polite_sleep()
            if post_html is None: continue
            md, _ = html_to_markdown(post_html, post_url)
            write_file(dest / f"{slugify(post_url)}.md", md)
            posts.append(post_url)
    return {"post_count": len(posts), "posts": posts}

def enumerate_examples(index_url, dest):
    html = fetch_page(index_url); polite_sleep()
    if html is None: return {"example_count": 0, "examples": []}
    soup = BeautifulSoup(html, "html.parser")
    example_links = [a["href"] for a in soup.select("a[href*='/examples/']") if looks_like_example(a)]
    examples = []
    for link in example_links:
        page_html = fetch_page(link); polite_sleep()
        if page_html is None: continue
        md, _ = html_to_markdown(page_html, link)
        write_file(dest / f"{slugify(link)}.md", md)
        examples.append(link)
    if len(examples) < EXAMPLES_MIN_EXPECTED:
        log.warning(f"examples count {len(examples)} < expected min {EXAMPLES_MIN_EXPECTED}; catalog may be under-enumerated")
    return {"example_count": len(examples), "examples": examples}

def merge_into_master_index(output_root, extended_summary):
    master_path = output_root / "index.json"
    existing = json.loads(master_path.read_text()) if master_path.exists() else {}
    existing["extended"] = {
        "generator": "ingest_orcina_extended.py",
        "generated": datetime.now(timezone.utc).isoformat(),
        "categories": extended_summary,
    }
    # Concurrency-safe atomic write — unique temp filename per process (Gemini r2 P3).
    # tempfile.NamedTemporaryFile(delete=False) returns a unique path so two concurrent
    # runs can't clobber each other's staging file before os.replace runs.
    with tempfile.NamedTemporaryFile(
        dir=master_path.parent, delete=False, suffix=".json.tmp", mode="w"
    ) as tmp:
        json.dump(existing, tmp, indent=2, sort_keys=True)
        tmp_path = tmp.name
    os.replace(tmp_path, master_path)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/orcina_common.py` | extract shared helpers (`html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page`, `HEADERS`, `USER_AGENT`, `USER_AGENT_TOKEN`) into legally-named module; add retry/timeout/polite-delay/robots helpers. All four helper names verified present in `ingest-orcina.py` at lines 98/135/261/286 (see Attested Evidence). |
| Update | `scripts/data/llm-wiki/ingest-orcina.py` | replace internal defs with `from orcina_common import ...`; bump `User-Agent` version string; remove duplicated constants. No behavioral change to existing ingest. Filename stays hyphenated — no import path uses it. |
| Create | **`scripts/data/llm-wiki/ingest_orcina_extended.py`** | new ingester for the five categories with streamed size enforcement, decompression-bomb cap, pagination with cross-page dedup (releases), polite scraping, atomic master-index merge. **Underscore filename: legal Python module identifier; prevents repeat of r1 import failure (closes r2 P1 #1).** |
| Create | `scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py` | unit tests with offline fixtures; all `monkeypatch.setattr` targets are the CONSUMING module `ingest_orcina_extended.<name>`, not the source module `orcina_common.<name>` (closes r2 P2). |
| Create | `scripts/data/llm-wiki/tests/test_orcina_common.py` | covers retry/timeout, robots-cache, fetch_page failure paths |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_example_page.html` | offline example-page fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_release_notes_v11_4.html` | offline release-notes fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_news_post.html` | offline news-post fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/releases_index_page1.html` | pagination fixture — contains `<link rel="next" href="…page2">` |
| Create | `scripts/data/llm-wiki/tests/fixtures/releases_index_page2.html` | terminal pagination page |
| Create | `scripts/data/llm-wiki/tests/fixtures/releases_index_dup_page1.html` | dedup fixture — page1 lists v11.4, v11.3 |
| Create | `scripts/data/llm-wiki/tests/fixtures/releases_index_dup_page2.html` | dedup fixture — page2 re-lists v11.4 (must not refetch) |
| Create | `scripts/data/llm-wiki/tests/fixtures/news_index_page1.html` | pagination fixture — news variant |
| Create | `scripts/data/llm-wiki/tests/fixtures/news_index_page2.html` | terminal news-pagination page |
| Create | `scripts/data/llm-wiki/tests/fixtures/orcina_robots.txt` | robots.txt fixture for `respect_robots` tests (incl. UA-token match path + training-zip allow/disallow) |
| Create | `scripts/data/llm-wiki/tests/fixtures/training_bundle.zip` | tiny synthetic ZIP (readme.md + sample.ipynb + sample.py + one `../evil.sh` entry for traversal test) |
| Create | `scripts/data/llm-wiki/tests/fixtures/training_bombfixture.zip` | crafted zip whose per-member declared `file_size` sums exceed MAX_EXTRACTED_BYTES, OR whose streamed extraction exceeds the cap mid-run |
| Update | `docs/plans/README.md` | add this plan to index |

**Dependency status (attested — no manifest change required):** `beautifulsoup4>=4.14.3` is ALREADY in root `pyproject.toml:12` (verified 2026-04-24 against HEAD `8c235f5e`). `ingest-orcina.py` already imports `bs4` at lines 26 and 137. v3 therefore needs NO Files-to-Change row for dep addition and NO new version pin in AC. `jupytext`/`nbconvert` remain optional runtime deps for the `.ipynb → .md` fallback chain; the raw-JSON cell-source parser provides a zero-dep fallback.

---

## TDD Test List

All tests monkeypatch `ingest_orcina_extended.fetch_page` (the CONSUMING module's bound name), NOT `orcina_common.fetch_page`. Example pattern in `test_ingest_orcina_extended.py`:

```python
# CORRECT — patches the name the extended ingester actually uses
monkeypatch.setattr("ingest_orcina_extended.fetch_page", fake_fetch)
# WRONG — does NOT affect the binding inside ingest_orcina_extended
# monkeypatch.setattr("orcina_common.fetch_page", fake_fetch)
```

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| **`test_import_ingest_orcina_extended_does_not_fetch_network`** (v3) | **Importing the module performs NO network I/O; CATEGORIES is a lazy callable mapping** | monkeypatched `urllib.request.urlopen` → raise `AssertionError`; monkeypatched `socket.socket.__init__` → raise `AssertionError`; then `import ingest_orcina_extended` | import succeeds; no raise; `type(ingest_orcina_extended.CATEGORIES["resources"]) is callable` (function reference, not a dict of results) |
| `test_example_page_converts` | example HTML → markdown with source header | fixture HTML | md contains `# <title>` and `<!-- source: …-->` |
| `test_enumerate_examples_finds_all` | catalog-page parser finds expected count | fixture catalog w/ 3 example links | list of 3 `(slug, url)` tuples |
| `test_enumerate_examples_warns_under_threshold` | logs WARN when count < `EXAMPLES_MIN_EXPECTED` | fixture with 2 links | caplog contains "under-enumerated" |
| `test_release_notes_capture_version_heading` | release-notes page parser writes per-version file and extracts version string | fixture v11.4 page | output file named `v11_4.md`, contains `## What's new` |
| `test_release_notes_graceful_when_headings_absent` | falls back to full-page write + WARN | fixture with no known heading | md written, caplog contains "full page" |
| `test_release_notes_pagination_follows_rel_next` | crawler walks 2 pages | `releases_index_page1.html` has `rel=next` → `..._page2.html` | fetches both pages; depth cap not hit |
| `test_release_notes_pagination_cap_enforced` | crawler stops at `MAX_PAGINATION_DEPTH`, emits WARN | fake 25-page chain | exactly 20 pages fetched; WARN logged |
| **`test_parse_release_notes_dedupes_across_pages`** (v3) | **Cross-page dedup: when same version link appears on multiple index pages, only fetched once** | `releases_index_dup_page1.html` lists v11.4 + v11.3; `releases_index_dup_page2.html` re-lists v11.4 | `fetch_page` called exactly 2 times for version pages (v11.4, v11.3); `seen_releases == {"11.4","11.3"}`; output contains exactly 2 `v*.md` files |
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
| `test_respect_robots_ua_token_match` (v3 new) | `can_fetch` is passed the short UA token, not the full UA with contact-email | fixture robots.txt disallowing the short token only | `respect_robots` returns `{path: False}`; confirms token-match semantics |
| `test_respect_robots_disallow_skips_category` | category skipped + summary `{"skipped": true, "reason": "robots.txt disallow <path>"}` when disallowed | fixture robots.txt disallowing `/news/` | news category not crawled; summary marks skipped |
| `test_respect_robots_disallow_skips_training_zip` (v3 new, Gemini P3) | training-zip path specifically can be disallowed and causes skip-with-WARN | fixture robots.txt disallowing `/wp-content/uploads/training/` | training category skipped; WARN logged; no download attempted |
| `test_extended_index_json_schema` | per-category index.json has required keys | run with mocked fetcher | `{"resources":{...},"examples":{...},"training":{...},"releases":{...},"news":{...}}` |
| `test_master_index_merge_extended_real_shape` | master `index.json` gains `extended` key alongside real top-level keys (`products`, `supplementary`, `papers`) without dropping them | pre-existing master with `products` (dict with `orcaflex`/`orcawave`/`orcfxapi`), `supplementary`, `papers` | merged master has ALL original keys PLUS `extended` |
| `test_master_index_merge_atomic_write` | atomic write uses `os.replace` — no half-written file observable | monkeypatched `json.dump` to raise mid-write | original master unchanged; no `.json.tmp` left behind |
| `test_master_index_merge_unique_temp_filename` (v3 new, Gemini P3) | `NamedTemporaryFile` is used — two simulated concurrent writers do not collide on the same temp-file path | two writers invoked in sequence with a sentinel inspection of `mkstemp`/`NamedTemporaryFile` | distinct temp paths observed; both runs complete without overwriting each other's stage |

Tests never hit the network — all via fixtures + `monkeypatch` of `ingest_orcina_extended.fetch_page` / `urllib.request.urlopen` (patched as `ingest_orcina_extended.urllib.request.urlopen` where imported).

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_orcina_common.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` (full suite) passes — no regression on `test_resolve_wiki_path.py`.
- [ ] `test_import_ingest_orcina_extended_does_not_fetch_network` passes — importing the module with `urllib.request.urlopen` monkeypatched to raise performs NO network I/O (proves CATEGORIES is lazy).
- [ ] `test_parse_release_notes_dedupes_across_pages` passes — same version appearing on 2 index pages results in 1 fetch, not 2.
- [ ] `uv run python scripts/data/llm-wiki/ingest-orcina.py --output-dir /tmp/wiki-smoke-base --products orcaflex` still exits 0 after helper extraction (post-refactor smoke).
- [ ] `uv run python scripts/data/llm-wiki/ingest_orcina_extended.py --output-dir /tmp/wiki-smoke --categories examples` exits 0 and produces `≥ 40` markdown files under `/tmp/wiki-smoke/orcina/extended/examples/`.
- [ ] `uv run python scripts/data/llm-wiki/ingest_orcina_extended.py --output-dir /tmp/wiki-smoke --categories releases` exits 0 and produces at least one `vX_Y.md` file; log-summary reports version-count.
- [ ] Running the full script with `--categories all` (default) exits 0 on a machine with `pdftotext` + `jupyter` (or `jupytext`) available.
- [ ] ZIP path-traversal test refuses to extract `../evil.sh` (verified by test).
- [ ] ZIP Content-Length header-guard test refuses `Content-Length` > 50 MB (verified by test).
- [ ] ZIP streamed-size-guard test refuses 60 MB body with missing `Content-Length` (verified by test).
- [ ] ZIP decompression-bomb test refuses declared `file_size` total > 500 MB (verified by test).
- [ ] ZIP streamed-bomb test refuses archive whose actual extracted bytes exceed cap mid-run (verified by test).
- [ ] ZIP non-zip-content test raises `ValueError` on HTML-masquerading-as-zip (verified by test).
- [ ] Pagination test demonstrates 2-page walk via `rel="next"` for both release-notes and news (verified by test).
- [ ] `data/llm-wiki/index.json` gains `extended` section with per-category counts after run; `products`, `supplementary`, `papers` preserved unchanged (verified by merge test against real shape).
- [ ] Master-index merge uses `tempfile.NamedTemporaryFile(dir=master_path.parent, delete=False)` — verified by `test_master_index_merge_unique_temp_filename`.
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "example"` against smoke dir returns at least one hit from examples corpus.
- [ ] `robots.txt` consultation happens once per run (visible in log) and disallowed categories — including the training-zip path `/wp-content/uploads/training/` — are skipped-with-reason (verified by tests).
- [ ] Plan review artifacts (r3) present at `scripts/review/results/2026-04-24-plan-2124-v3-{claude,codex,gemini}.md`.
- [ ] No file created or referenced by this plan contains a hyphen in its Python module name. (grep check: `find scripts/data/llm-wiki -name '*-*.py' -newer <v3-landing-sha>` returns zero new files.)

---

## Build Sequence (explicit, P1/P2 fixes step-by-step)

1. **Extract shared helpers.** Create `scripts/data/llm-wiki/orcina_common.py`. Move `html_to_markdown` (line 98), `_convert_element` (line 135), `_convert_table` (line 261), `fetch_page` (line 286) from `ingest-orcina.py` verbatim — all four exist at those exact names (attested). Move `HEADERS`, `USER_AGENT`, `DELAY_SECONDS` (rename to `POLITE_DELAY_SECONDS`, bump to 1.0). Add new `USER_AGENT_TOKEN` (short form for `rp.can_fetch`). Add new helpers: `respect_robots`, `polite_sleep`, retry-wrapped `fetch_page`.
2. **Update existing ingester.** Replace internal defs in `ingest-orcina.py` with `from orcina_common import ...`. Run existing smoke: `python3 scripts/data/llm-wiki/ingest-orcina.py --output-dir /tmp/wiki-smoke-base --products orcaflex` must still exit 0.
3. **Write `test_orcina_common.py`.** Cover retry/timeout, robots cache (including UA-token match), fetch_page failure paths. Run green before moving on.
4. **Verify live master-index shape.** Run `ingest-orcina.py` once locally; `jq 'keys' data/llm-wiki/index.json` — confirm shape matches the `generated|generator|issue|products|supplementary|papers` contract documented above.
5. **Create `ingest_orcina_extended.py` (underscore filename — the r2 P1 #1 fix).** Add constants (`MAX_COMPRESSED_BYTES`, `MAX_EXTRACTED_BYTES`, `MAX_PAGINATION_DEPTH`, `EXAMPLES_MIN_EXPECTED`). Declare CATEGORIES as a BARE CALLABLE MAPPING (names → functions, no invocations). Declare CATEGORY_ARGS and CATEGORY_ROBOTS_PATH. Stub `ingest_extended()` with `respect_robots` → per-category lazy invocation. Stub `merge_into_master_index` with `tempfile.NamedTemporaryFile + os.replace`.
6. **Write `test_import_ingest_orcina_extended_does_not_fetch_network` FIRST** — the r2 P1 #2 fix-in-test-form. With `urllib.request.urlopen` and `socket.socket.__init__` monkeypatched to raise, `import ingest_orcina_extended` must succeed. This test locks the lazy-CATEGORIES contract for all future work.
7. **Implement `download_and_extract_zip`** with ALL four guards in order: (a) HEAD Content-Length pre-check, (b) streamed GET with running-bytes abort, (c) magic-bytes + content-type validation, (d) pre-extract declared-total `file_size` cap, (e) mid-extract cumulative-extracted-bytes cap. Write tests for each guard before the next guard lands.
8. **Implement pagination helper `iter_paginated`** with `MAX_PAGINATION_DEPTH`. Use it in `parse_release_notes` and `crawl_news_feed`. Write pagination tests against fixtures before exercising the live crawl.
9. **Implement `parse_release_notes` with cross-page dedup (the r2 P2 fix).** `seen_releases: set[str]` tracked across pagination iterations. Write `test_parse_release_notes_dedupes_across_pages` against `releases_index_dup_page{1,2}.html` fixtures.
10. **Implement `enumerate_examples`** with `EXAMPLES_MIN_EXPECTED = 40` and under-threshold WARN.
11. **Implement `crawl_resources_sub_pages`** (fan-out capped at 50 unique sub-page links; stop conditions documented).
12. **Implement `crawl_news_feed`** using `iter_paginated`.
13. **Wire up `respect_robots`** — call once at `ingest_extended` entry. Per-category skip logic routes through `CATEGORY_ROBOTS_PATH`. Training-zip path (`/wp-content/uploads/training/`) is gated identically to other paths; disallow → WARN + skip (Gemini P3).
14. **Implement `merge_into_master_index`** using `tempfile.NamedTemporaryFile(dir=master_path.parent, delete=False)` (Gemini P3) + `os.replace`. Write `test_master_index_merge_extended_real_shape`, `test_master_index_merge_atomic_write`, and `test_master_index_merge_unique_temp_filename`.
15. **Verify monkeypatch targets in all tests** — every `monkeypatch.setattr` for `fetch_page` must target `ingest_orcina_extended.fetch_page`, NOT `orcina_common.fetch_page` (r2 P2 #3 resolution). A short grep in the PR checklist: `grep -n 'orcina_common\.fetch_page' scripts/data/llm-wiki/tests/test_ingest_orcina_extended.py` must return zero lines.
16. **Run full test suite + smoke the CLI** with `--categories examples` (live), then `--categories all`. Confirm `≥ 40` examples captured, master index has all original keys plus `extended`, no hyphen-named Python file created.
17. **Dispatch r3 cross-review** (Claude / Codex / Gemini). Address findings or iterate; do NOT self-approve.

---

## Risks and Open Questions

- **Risk — ZIP path-traversal:** explicit pre-extract validation + dedicated test. Unchanged.
- **Risk — ZIP compressed-size DoS:** mitigated by BOTH header pre-check AND streamed running-bytes abort.
- **Risk — ZIP decompression-bomb:** mitigated by pre-extract declared-total cap + mid-extract cumulative-bytes cap at 500 MB. Justification: training bundle is expected < 10 MB; 500 MB ceiling is 50× expected-size margin and 10× compressed ceiling.
- **Risk — ZIP content masquerade:** mitigated by Content-Type check + magic-bytes probe.
- **Risk — `jupyter nbconvert` dependency:** fallback chain is `nbconvert` → `jupytext` → raw-JSON cell-source parse. No category is silently skipped.
- **Risk — upstream page shape drift:** fixtures pin expected shape; release-notes heading-match has graceful-degradation fallback.
- **Risk — pagination truncation:** mitigated by `iter_paginated` with cap + WARN when cap hit.
- **Risk — release-notes duplicate fetch (r2 P2 #4):** mitigated by `seen_releases: set[str]` carried across pagination iterations; test covers this.
- **Risk — polite-scraping / rate-limiting:** explicit User-Agent with contact email, `robots.txt` consultation once per run using the short UA token, `POLITE_DELAY_SECONDS = 1.0` between each fetch, retry with exponential backoff (2→4→8s), 30s per-request timeout, max 3 attempts.
- **Risk — training-zip path robots disallow (Gemini P3):** `/wp-content/uploads/training/` is checked alongside other paths. If robots.txt disallows it, WARN and skip — do NOT proceed.
- **Risk — concurrent-run race on master `index.json` (Gemini r2 P3):** atomic write via `tempfile.NamedTemporaryFile(dir=master_path.parent, delete=False)` + `os.replace`. Unique per-process temp filename — two concurrent writers cannot clobber each other's stage file. Test locks the behavior.
- **Risk — import-time side effects (r2 P1 #2):** CATEGORIES is a bare callable mapping; crawlers run only from inside `ingest_extended()` after the robots gate. `test_import_ingest_orcina_extended_does_not_fetch_network` locks this contract.
- **Risk — helper extraction regression:** `ingest-orcina.py` is mutated (import rewrite). Mitigation: step-2 smoke must pass before any new ingester work; no behavioral change to existing functions.
- **Risk — dependency interaction with #2103:** if #2103 lands `llm_wiki_common.py` first, this plan's `orcina_common.py` may become duplicative. Reconciliation: #2103's common module can re-export from `orcina_common` or vice versa; pick at implementation time. Not a blocker.
- **Risk — monkeypatch target drift (r2 P2 #3):** tests must patch the consuming module's bound name. Build-sequence step 15 enforces this with a grep check.
- **Open — news date-cutoff:** ingest-all for now; revisit if corpus size becomes unwieldy. Flag for user during approval.
- **Open — training-ZIP retention:** deleted after extraction; originals are reachable via the `source_zip_url` field on each training file's header.
- **Open — rerun policy:** v3 adopts "always re-fetch, overwrite markdown files" (closure of r2 P3 idempotency question). Incremental-skip with on-disk content-hash side table is deferred to a follow-up issue if repeated-run polite-scraping etiquette becomes a concern.
- **Open — partial-failure policy:** if one example fails to download, log WARN and continue; a single failure does not abort the whole category. Log summary reports per-category failure count.
- **Deferred (tracked as follow-up):** `--dry-run` flag for CI smoke-checks. Nice-to-have; not a P1/P2. Filed as a follow-up issue if this plan ships without it.
- **Deferred (tracked as follow-up):** reproducible-output ordering (sorted keys in `index.json`). `merge_into_master_index` uses `sort_keys=True` so the top-level is stable; per-category list order follows crawl order. If bit-identical reruns become a requirement, sort category lists by a stable key (e.g. URL).

---

## Adversarial Review Summary

| Provider | Verdict (r1) | Verdict (r2) | Verdict (r3) | Key findings |
|---|---|---|---|---|
| Claude | MAJOR (2 P1s, 5 P2s, 4 P3s) | MAJOR (2 new P1s, 5 P2s, 3 P3s) | TBD after r3 | **r2 P1s resolved in v3:** (1) new module renamed to `ingest_orcina_extended.py` (underscore — legal Python identifier); (2) CATEGORIES converted to bare callable mapping, with `test_import_…_does_not_fetch_network` locking import-time-network-abstinence. All r2 P2s resolved (see Review History). |
| Codex | not run (sandbox-blocked dispatch) | not run (upstream stdin-hang per `feedback_codex_cli_0_124_upstream_regression`) | TBD — dispatch if CLI regression resolved, else skip with provenance note | — |
| Gemini | MINOR (1 P2, 1 P3) | MINOR (1 P3 concurrent-temp-filename) | TBD after r3 | **r2 P3 resolved in v3:** `tempfile.NamedTemporaryFile(dir=master_path.parent, delete=False)` used per Gemini's exact suggestion; training-zip robots exception added. |

**Overall result (r1):** MAJOR — resolved in v2.
**Overall result (r2):** MAJOR — v3 addresses all r2 P1s and P2s; Gemini r2 P3 also closed.
**r3 pending.**

---

## Complexity: T2

**T2** — one extracted helpers module + one new ingester script (underscore-named, legal Python module) with five category handlers + bare callable CATEGORIES mapping, two test files with offline fixtures, small import-rewrite in the existing ingester. Security-sensitive ZIP handling (two independent size guards) + multi-category crawl + atomic-merge with unique-temp-filename + cross-page dedup + import-time-network-abstinence test bumps it above T1 but remains well under T3. No cross-repo changes; no schema migration of already-written data; no new runtime deps (bs4 already in `pyproject.toml:12`).
