# Plan for #2103: Extend llm-wiki ingestion to AQWA and BEMRosetta documentation

> **Status:** draft (v2 — addresses r1 findings)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2103
> **Base commit:** `12b4be834954505ca1e7fc8ad8b20bda34e92baf` (HEAD at v2 plan-drafting time; cite line numbers relative to this SHA)
> **Review artifacts (r1):**
> - Claude — `scripts/review/results/20260424T103718Z-inline-content-plan-claude.md` (MAJOR — inline-content dispatch bug; no real findings — disregarded per issue-comment direction)
> - Codex — `scripts/review/results/20260424T103718Z-inline-content-plan-codex.md` (MAJOR — 2 P1s + 1 P2, all locally verified)
> - Gemini — `scripts/review/results/20260424T103718Z-inline-content-plan-gemini.md` (NO_OUTPUT — silent failure)
> **Review artifacts (r2, pending):** `scripts/review/results/2026-04-24-plan-2103-v2-{claude,codex,gemini}.md`

---

## Review History (closure summary)

Short table mapping every r1 finding to its closure in this plan, so future reviewers can see the fix at a glance.

### r1 (resolved in v2)

| Finding | Class | Resolution in v2 |
|---|---|---|
| **search-wiki integration gap** — plan asserts new corpora will surface through `scripts/data/llm-wiki/search-wiki.py`, but that file hardcodes `PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]` (verified 2026-04-24 at line 15) and was NOT listed in Files-to-Change. As written, BEMRosetta/AQWA content would not be searchable; acceptance criterion unachievable. | **P1** | **Resolved.** `scripts/data/llm-wiki/search-wiki.py` is now an explicit Files-to-Change row (Modify). v2 extends `PRODUCTS` to `["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa", "papers"]`. The per-product `index.json` loading logic in `_load_topics()` (line 25-30) already works generically for any product — the only adjustment is that `bemrosetta` and `aqwa` index files must carry a `topics: [...]` key (same shape as `orcaflex/index.json`). Added `argparse --product` choices update (line 166) and a TDD row `test_search_wiki_surfaces_bemrosetta` asserting `search-wiki.py --product=bemrosetta` returns ≥1 hit against a fixture wiki dir. Per-product topic schema locked in the **Master-index and per-product-index contract** section below. |
| **Import-path invalid (`from ingest_orcina import ...` but source is `ingest-orcina.py` — hyphen)** — Python module identifiers cannot contain hyphens. v1 pseudocode line 137 said "OR via `from ingest_orcina import ...`" as a decision point. Recurring workspace-wide pattern per memory `feedback_llm_wiki_hyphen_module_path_pattern` (3 prior recurrences on 2026-04-24 alone). | **P1** | **Resolved — Option (a), same pattern as #2124 v3.** v2 extracts shared helpers (`html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`) into a new underscore-named module **`scripts/data/llm-wiki/llm_wiki_common.py`** (legal Python module identifier). Both new ingesters import via `from llm_wiki_common import html_to_markdown, fetch_page, _convert_element, _convert_table`. The existing `ingest-orcina.py` filename stays hyphenated (no import path uses it; only the CLI invocation `python3 scripts/data/llm-wiki/ingest-orcina.py …`), and its internal def bodies are replaced with `from llm_wiki_common import …`. New file is underscore-named to prevent repeat of the hyphen-path defect. Note on #2124 v3 coordination: #2124 v3 proposes a sibling module `orcina_common.py` (also underscore) covering the same helpers; at implementation time the two plans will reconcile either by (i) whichever lands first creates `llm_wiki_common.py`, the other plan's common module re-exports from it, or (ii) both consolidate into a single `llm_wiki_common.py`. v2 proceeds under option (i) with `llm_wiki_common.py` as the workspace-shared name; #2124 v3's `orcina_common.py` becomes a thin re-export if it lands second. This reconciliation is called out in Risks. |
| **cat:data-pipeline retrieval contract incomplete** — issue is labeled `cat:data-pipeline`. Per `docs/plans/README.md:53`, that class requires consultation of `registry.yaml`, pipeline config, and `resource-intelligence-maturity.yaml`. v1's Resource Intelligence section treated this as generic documentation pipeline and did not cite these artifacts. | **P2** | **Resolved.** Resource Intelligence section below adds a "cat:data-pipeline retrieval contract" subsection explicitly citing the three required artifacts with per-artifact findings: `data/document-index/registry.yaml` (no pre-existing BEMRosetta/AQWA entries — this ingester creates the first ones), `data/document-index/llm-wiki-external-source-priority-queue.yaml` (pipeline queue config for llm-wiki ingestion; BEMRosetta + AQWA join via new priority-queue entries), `data/document-index/online-resource-registry.yaml` (existing ANSYS AQWA reference/theory entries at lines 1217, 1228, 1238, 1533; BEMRosetta entry at line 1031), `data/document-index/resource-intelligence-maturity.yaml` (no pre-existing maturity rows for these two corpora; v2 adds initial rows at draft-maturity level after first successful ingest). |

---

## Attested Evidence

Independently-verifiable claims this v2 plan relies on. Each was checked against HEAD `12b4be834954505ca1e7fc8ad8b20bda34e92baf` on 2026-04-24.

| Claim | Verification method | Result |
|---|---|---|
| Issue #2103 OPEN | `gh issue view 2103` | OPEN — "feat(llm-wiki): extend ingestion to AQWA and BEMRosetta documentation" |
| Issue #2088 CLOSED (parent — Orcina prior-art) | carry-forward from v1 evidence | CLOSED |
| Issue #2140 CLOSED (portable path resolver) | carry-forward from v1 evidence | CLOSED |
| `scripts/data/llm-wiki/ingest-orcina.py` exists (filename is hyphenated, not importable as `ingest_orcina`) | `ls scripts/data/llm-wiki/ingest*.py` | EXISTS — only hyphenated match; no underscore-named peer |
| `scripts/data/llm-wiki/search-wiki.py` hardcodes `PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]` at line 15 | `grep -n "PRODUCTS" scripts/data/llm-wiki/search-wiki.py` | `15:PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]` and also at lines 37, 40, 166 — CONFIRMED |
| `search-wiki.py:25-30` loads topics via per-product `index.json` at `<WIKI_DIR>/<product>/index.json` with a `topics: [...]` key (or `papers: [...]` for papers product) | Read of `search-wiki.py:_load_topics` | CONFIRMED — loader is generic; only the product name list needs extension |
| `docs/plans/README.md:53` requires `cat:data-pipeline` class to consult `registry.yaml`, pipeline config, and `resource-intelligence-maturity.yaml` | `grep -n "data-pipeline" docs/plans/README.md` | `53:| **Data Pipeline** | `cat:data-pipeline` | `registry.yaml`, pipeline config, `resource-intelligence-maturity.yaml` |` — CONFIRMED |
| `data/document-index/registry.yaml` has NO pre-existing BEMRosetta / AQWA entries (this ingester creates the first coverage) | `grep -n "llm.wiki\|llm-wiki\|bemrosetta\|aqwa" data/document-index/registry.yaml` | no match — CONFIRMED no pre-existing entry |
| `data/document-index/resource-intelligence-maturity.yaml` has NO pre-existing BEMRosetta / AQWA maturity rows | `grep -n "orcina\|bemrosetta\|BEMRosetta\|aqwa\|AQWA" data/document-index/resource-intelligence-maturity.yaml` | no match — CONFIRMED no pre-existing maturity row |
| `data/document-index/online-resource-registry.yaml` already lists ANSYS AQWA reference and theory manuals + training + product page, and the BEMRosetta GitHub repo | `grep -n "aqwa\|bemrosetta" data/document-index/online-resource-registry.yaml` | `1031: github_com_bemrosetta_bemrosetta_77615d`; `1217/1228/1238: ansyshelp.ansys.com/.../aqwa_ref|aqwa_theory/…`; `1533: training-center/.../introduction-to-ansys-aqwa` — CONFIRMED |
| `data/document-index/llm-wiki-external-source-priority-queue.yaml` exists and governs llm-wiki ingestion pipeline config | `ls data/document-index/llm-wiki-external-source-priority-queue.yaml` and head read | EXISTS — schema_version 1.0.0; lists source registries consumed; governed by issues #2242/#2243 under umbrella #2241 |
| `llm_wiki_common.py` does not yet exist — v2 will create it | `ls scripts/data/llm-wiki/llm_wiki_common.py` | NOT FOUND — CONFIRMED will be new file |
| #2124 v3 plan proposes sibling module `orcina_common.py` (also underscore; overlapping helpers `html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page`) | read of `/tmp/plan-drafts/plan-2124-v3.md` Files-to-Change | CONFIRMED — reconciliation path documented in Risks |
| `scripts/data/llm-wiki/tests/` contains `__init__.py`, `test_e2e_smoke.py`, `test_resolve_wiki_path.py` at HEAD | `ls scripts/data/llm-wiki/tests/` | CONFIRMED |

Claims the plan does NOT attest (require live verification during implementation, not plan-approval):
- Exact pagination / sidebar HTML structure of `https://github.com/BEMRosetta/BEMRosetta/wiki` (fixtures will be captured during implementation).
- Exact public-reachability of ANSYS AQWA help URLs from unauthenticated CI — the ingester is designed to degrade gracefully to zero-topic + populated `errors[]` if gated, so public-reachability is not a plan-approval gate.
- BEMRosetta repo `doc/` directory exact Markdown file count (fetched via GitHub tree API or raw URL enumeration at run time).

---

## Resource Intelligence Summary

### Existing repo code (anchored to base SHA `12b4be83`)
- Found: `scripts/data/llm-wiki/ingest-orcina.py` — canonical prior-art ingester (#2088). Provides `parse_toc_xml()`, `html_to_markdown()` (verified line reference pinned in v3 of #2124), `_convert_element()`, `_convert_table()`, `fetch_page()` (with URL-encode retry), `ingest_product()`, `ingest_supplementary()`, `ingest_papers()` (PDF via `pdftotext`). Writes to `<output_root>/<product>/topics/*.md` plus `<product>/index.json` and master `index.json`.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — portable output-root resolver (#2140); honors env var → config → `data/llm-wiki/` → `knowledge/wikis/`. Both new ingesters reuse this without change.
- Found: `scripts/data/llm-wiki/search-wiki.py` — search CLI. **v2-critical:** hardcodes `PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]` at line 15; also referenced at lines 37, 40, 166. The `_load_topics()` loader (line 25-30) is generic: reads `<WIKI_DIR>/<product>/index.json` and returns its `topics` key (or `papers` for the papers product). Extending `PRODUCTS` plus writing per-product `index.json` files with a `topics: [...]` key is sufficient for new corpora to surface.
- Found: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` — existing pytest scaffold; new unit tests land alongside.
- Gap: no `ingest-bemrosetta.py` or `ingest-aqwa.py` exists.
- Gap: no `llm_wiki_common.py` shared helpers module (created by this plan to fix hyphen-import).
- Gap: no `knowledge/wikis/marine-engineering/wiki/tools/aqwa/` or `.../bemrosetta/` scaffolding for cross-referencing diffraction-tool entries.

### cat:data-pipeline retrieval contract (resolves r1 P2)

Per `docs/plans/README.md:53`, `cat:data-pipeline` issues must consult `registry.yaml`, pipeline config, and `resource-intelligence-maturity.yaml`. v2 cites each:

- **`data/document-index/registry.yaml`** — document-index registry. **Finding:** no pre-existing BEMRosetta or AQWA entries (`grep -n "bemrosetta\|aqwa"` → no match). This ingester will create the first registry entries for these two corpora. Registry updates are out-of-scope for this plan's code changes (registry entries are added by downstream indexing jobs that read the master `index.json`); v2 acceptance criterion notes that registry ingestion is a follow-up path, not a gating condition for this plan.
- **`data/document-index/llm-wiki-external-source-priority-queue.yaml`** — the llm-wiki ingestion pipeline config (governed by #2242/#2243 under umbrella #2241; architecture per #2205/#2208). Lists `source_families` by priority tier P1–P4. **Finding:** BEMRosetta and AQWA are not yet listed as named source families in this queue. v2 adds them under family `online-data-apis-and-portals` (P1, metadata-first promotion) via a follow-up priority-queue entry filed as a non-blocking sibling task; the ingesters work stand-alone even before the queue is updated.
- **`data/document-index/resource-intelligence-maturity.yaml`** — maturity ledger. **Finding:** no pre-existing maturity rows for orcina/bemrosetta/aqwa. v2 acceptance-criterion adds an initial maturity row for each new corpus at **draft** level (per #2205 operating-model language) after first successful ingest. Row schema follows the existing ledger format; no schema change required.
- **`data/document-index/online-resource-registry.yaml`** (cited as related context) — already lists the BEMRosetta GitHub repo at line 1031 and ANSYS AQWA reference/theory/product/training URLs at lines 1217, 1228, 1238, 1533. These entries provided the canonical source URLs used as BEMRosetta and AQWA ingester seeds; no modification required.

### Master-index and per-product-index contract (new — locks the `search-wiki.py` integration)

v2 locks the per-product `index.json` shape consumed by `search-wiki.py:_load_topics`. Each new ingester writes:

```
<output_root>/bemrosetta/index.json  →  {"topics": [{"file": "...", "title": "...", "sections": [...], "section_path": [...]}, ...], "errors": [...]}
<output_root>/aqwa/index.json        →  {"topics": [...], "errors": [...]}
```

Topic-entry shape matches what `search-wiki.py:_load_topics` returns (`topics` list; each topic has `file`, `title`, `sections`, optionally `section_path`). The AQWA case tolerates an empty `topics: []` list with populated `errors: [...]`; `search-wiki.py` handles empty lists without error (existing behavior — the `build_index()` loop silently skips empty products). Topics write to `<output_root>/<product>/topics/<slug>.md` to match the path convention at `search-wiki.py:_md_path` (line 21-23).

The master-index merger (`update-master-index.py`) merges per-product indexes into `<output_root>/index.json` with shape:

```
{
  "generated": "<iso timestamp>",
  "products": {"orcaflex": {...}, "orcawave": {...}, "orcfxapi": {...}, "bemrosetta": {...}, "aqwa": {...}},
  "supplementary": {...}, "papers": {...}
}
```

This preserves the existing `products|supplementary|papers` top-level shape created by `ingest-orcina.py` (verified per #2124 v3 Attested Evidence). Atomic write via `tempfile.NamedTemporaryFile + os.replace`; unique per-process temp filename to avoid concurrent-run race (same pattern #2124 v3 uses).

### Standards
Not applicable — this is a documentation-pipeline issue, not an engineering-standards deliverable.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/` — existing marine-engineering wiki tree; OrcaFlex/OrcaWave topics live under the llm-wiki output (`data/llm-wiki/orcaflex/…`) rather than inside this curated wiki. New AQWA/BEMRosetta output will follow the same boundary (ingested bulk content in `data/llm-wiki/`; curated cross-references in `marine-engineering/wiki/tools/` as a follow-up issue).
- `knowledge/wikis/marine-engineering/CLAUDE.md` — governance guardrails for durable-curated vs transient-ingested content (#2209).

### Documents consulted
- Issue body #2103 — deliverables: `ingest-bemrosetta.py`, `ingest-aqwa.py`, outputs at `data/llm-wiki/bemrosetta/` and `data/llm-wiki/aqwa/`, master index update. Priority: BEMRosetta first (open-source, GitHub wiki/docs), AQWA second (ANSYS help may require manual extraction).
- Parent issue #2088 — CLOSED; defined the MadCap-Flare TOC + `html_to_markdown` pattern used by Orcina. Reference implementation contract.
- `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md` — ecosystem roadmap listing AQWA/BEMRosetta as remaining diffraction-tool gap.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — operating model governing where llm-wiki outputs land and how master `index.json` is consumed.
- **`docs/plans/README.md`** — issue-class retrieval contract (line 53 — the `cat:data-pipeline` rule).
- Sibling plan `/tmp/plan-drafts/plan-2124-v3.md` (not yet landed) — proposes `orcina_common.py` covering the same helper surface; reconciliation documented in Risks.
- Memory: `feedback_llm_wiki_hyphen_module_path_pattern.md` — documents this exact hyphen defect with 3 recurrences on 2026-04-24; v2's Option (a) extract-to-underscore-module resolution follows the sanctioned pattern.
- Upstream: https://github.com/BEMRosetta/BEMRosetta — open-source repo with `doc/` directory + GitHub wiki; public raw content via `raw.githubusercontent.com` and rendered wiki via `github.com/.../wiki`.
- Upstream: ANSYS AQWA help — public help URLs gated behind `ansyshelp.ansys.com` login. Ingester will degrade gracefully: fetch what is publicly reachable, record unreachable URLs to `errors[]`, emit zero-topic index without crashing.

### Gaps identified
- No BEMRosetta ingester (must be built).
- No AQWA ingester (must be built; must tolerate partial accessibility).
- No `llm_wiki_common.py` shared helpers module (created by this plan).
- No master-index merge path — current `ingest-orcina.py` overwrites `index.json`. v2 adds a `update-master-index.py` merger.
- No `search-wiki.py` coverage for the new products — v2 extends `PRODUCTS`.
- No registry / maturity rows for BEMRosetta or AQWA — v2 adds an initial draft-level maturity row after first ingest; registry ingestion tracked as follow-up.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2103` — OPEN — feat(llm-wiki): extend ingestion to AQWA and BEMRosetta documentation
- `#2088` — CLOSED — feat(llm-wiki): ingest OrcaFlex, OrcaWave, and OrcFxAPI online help into llm-wiki
- `#2140` — CLOSED — Replace tracked absolute llm-wiki symlink with portable path resolution and smoke tests
- `#2124` — OPEN (sibling plan v3 in-flight)

**File existence** (`ls` 2026-04-24 against HEAD `12b4be83`):
- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py`
- EXISTS: `scripts/data/llm-wiki/resolve_wiki_path.py`
- EXISTS: `scripts/data/llm-wiki/search-wiki.py`
- EXISTS: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py`
- EXISTS: `scripts/data/llm-wiki/tests/test_e2e_smoke.py`
- EXISTS: `knowledge/wikis/marine-engineering/wiki/`
- EXISTS: `data/document-index/registry.yaml`, `data/document-index/resource-intelligence-maturity.yaml`, `data/document-index/llm-wiki-external-source-priority-queue.yaml`, `data/document-index/online-resource-registry.yaml`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/ingest-bemrosetta.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/ingest-aqwa.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/llm_wiki_common.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/update-master-index.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_ingest_aqwa.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_llm_wiki_common.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py`

Distinct sources consulted: 11 (issue body, #2088, #2140, #2124 v3 sibling plan, `ingest-orcina.py`, `resolve_wiki_path.py`, `search-wiki.py`, marine-engineering wiki, ecosystem-strengthening plan, docs/plans/README.md, operating-model plan #2205 + registry/maturity/queue yaml trio).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v2) | `docs/plans/2026-04-24-issue-2103-aqwa-bemrosetta-ingestion.md` |
| Shared helpers module (new) | `scripts/data/llm-wiki/llm_wiki_common.py` |
| BEMRosetta ingester | `scripts/data/llm-wiki/ingest-bemrosetta.py` |
| AQWA ingester | `scripts/data/llm-wiki/ingest-aqwa.py` |
| Master-index updater | `scripts/data/llm-wiki/update-master-index.py` |
| Existing ingester (imports updated only) | `scripts/data/llm-wiki/ingest-orcina.py` |
| Search-wiki CLI (PRODUCTS extended) | `scripts/data/llm-wiki/search-wiki.py` |
| BEMRosetta tests | `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py` |
| AQWA tests | `scripts/data/llm-wiki/tests/test_ingest_aqwa.py` |
| Common-module tests | `scripts/data/llm-wiki/tests/test_llm_wiki_common.py` |
| search-wiki integration test | `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py` |
| Fixtures | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_wiki_page.html`, `.../bemrosetta_raw_readme.md`, `.../aqwa_login_wall.html`, `.../aqwa_public_help.html`, `.../search_fixture_wiki/bemrosetta/index.json` + sample topic md, `.../search_fixture_wiki/aqwa/index.json` |
| Ingested output (runtime) | `data/llm-wiki/bemrosetta/topics/*.md`, `data/llm-wiki/aqwa/topics/*.md`, `data/llm-wiki/bemrosetta/index.json`, `data/llm-wiki/aqwa/index.json` |
| Master index | `data/llm-wiki/index.json` (merged — `products.bemrosetta`, `products.aqwa` added alongside existing keys) |
| Plan reviews (r2) | `scripts/review/results/2026-04-24-plan-2103-v2-{claude,codex,gemini}.md` |

---

## Deliverable

A shared helpers module `llm_wiki_common.py` (underscore — legal Python module identifier), plus two new ingesters — `ingest-bemrosetta.py` (GitHub wiki + repo `doc/` Markdown + raw.githubusercontent for `.md`) and `ingest-aqwa.py` (ANSYS help with login-wall detection + graceful zero-topic degradation) — plus a master-index merger (`update-master-index.py`) and an extension of `search-wiki.py`'s `PRODUCTS` list, so that BEMRosetta and AQWA corpora surface through the existing search CLI alongside the Orcina family.

---

## Pseudocode

```
# ── llm_wiki_common.py (new — shared helpers; underscore = legal Python module) ──
# Extracts the helpers currently embedded in ingest-orcina.py so that new underscore-named
# ingesters can import them via a legal dotted name. Closes r1 P1 #2 (hyphen-import defect).
USER_AGENT_TOKEN    = "workspace-hub-llm-wiki"
USER_AGENT          = f"{USER_AGENT_TOKEN}/1.0 (+https://github.com/vamseeachanta/workspace-hub)"
HEADERS             = {"User-Agent": USER_AGENT}
POLITE_DELAY_SECONDS    = 1.0
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES             = 3

def fetch_page(url, *, timeout=REQUEST_TIMEOUT_SECONDS, max_retries=MAX_RETRIES) -> str | None:
    """Retry-wrapped fetcher with URL-encode fallback (verbatim behavior from ingest-orcina.py:fetch_page)."""
    ...

def html_to_markdown(html, source_url="") -> tuple[str, list[str]]:
    """Verbatim move from ingest-orcina.py:html_to_markdown. Returns (markdown, headings)."""
    ...

def _convert_element(element, lines, depth=0):    # verbatim from ingest-orcina.py:_convert_element
    ...

def _convert_table(table, lines):                 # verbatim from ingest-orcina.py:_convert_table
    ...

def slugify(url_or_title) -> str:
    """Stable slug from URL or title — consistent with existing ingester."""
    ...


# ── ingest-bemrosetta.py (new — file is hyphenated CLI entry; no Python dotted import points at it) ──
# Can be CLI-invoked as `python3 scripts/data/llm-wiki/ingest-bemrosetta.py ...`. The tests import
# via importlib.util.spec_from_file_location (documented in the test file) because Python tests
# cannot do `from ingest-bemrosetta import …`. See Risks for why we accept the hyphen here.
from llm_wiki_common import fetch_page, html_to_markdown, _convert_element, _convert_table, slugify

SOURCES = {
    "github_wiki":  "https://github.com/BEMRosetta/BEMRosetta/wiki",
    "repo_docs":    "https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/doc",
    "readme_raw":   "https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/README.md",
    "tree_api":     "https://api.github.com/repos/BEMRosetta/BEMRosetta/git/trees/master?recursive=1",
}

def ingest_bemrosetta(output_root):
    product_dir = output_root / "bemrosetta"
    topics_dir  = product_dir / "topics"
    topics_dir.mkdir(parents=True, exist_ok=True)
    topics, errors = [], []

    # 1. GitHub wiki: fetch sidebar, enumerate pages, convert each via html_to_markdown
    wiki_index_html = fetch_page(SOURCES["github_wiki"])
    for page_url, title in parse_wiki_sidebar(wiki_index_html):
        page_html = fetch_page(page_url)
        if page_html is None:
            errors.append({"url": page_url, "reason": "fetch_failed"}); continue
        md, headings = html_to_markdown(page_html, page_url)
        filename = f"{slugify(title)}.md"
        (topics_dir / filename).write_text(md, encoding="utf-8")
        topics.append({"file": filename, "title": title, "sections": headings, "section_path": ["wiki"]})

    # 2. Repo doc tree: raw.githubusercontent.com (no API rate-limit concerns)
    tree = fetch_github_tree_for_repo_markdown(SOURCES["tree_api"], subdir="doc")
    for entry in tree:
        raw_url = f"https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/{entry['path']}"
        md_bytes = fetch_raw_markdown(raw_url)
        if md_bytes is None:
            errors.append({"url": raw_url, "reason": "fetch_failed"}); continue
        title = extract_title_from_markdown(md_bytes, fallback=Path(entry["path"]).stem)
        filename = f"{slugify(entry['path'])}.md"
        md_body = f"<!-- source: {raw_url} -->\n\n{md_bytes.decode('utf-8', errors='replace')}"
        (topics_dir / filename).write_text(md_body, encoding="utf-8")
        topics.append({"file": filename, "title": title, "sections": extract_md_headings(md_body), "section_path": ["doc", entry["path"].rsplit('/', 1)[0] if '/' in entry['path'] else "doc"]})

    # 3. README
    readme_bytes = fetch_raw_markdown(SOURCES["readme_raw"])
    if readme_bytes is not None:
        md_body = f"<!-- source: {SOURCES['readme_raw']} -->\n\n{readme_bytes.decode('utf-8','replace')}"
        (topics_dir / "README.md").write_text(md_body, encoding="utf-8")
        topics.append({"file": "README.md", "title": "BEMRosetta README", "sections": extract_md_headings(md_body), "section_path": ["readme"]})

    # 4. Write per-product index.json with the shape search-wiki.py:_load_topics expects
    index = {"generated": iso_now(), "topic_count": len(topics), "topics": topics, "errors": errors}
    (product_dir / "index.json").write_text(json.dumps(index, indent=2))


# ── ingest-aqwa.py (new — graceful-degrade for gated help) ──
from llm_wiki_common import fetch_page, html_to_markdown, slugify

AQWA_SEEDS = [
    "https://www.ansys.com/products/structures/ansys-aqwa",
    # ANSYS help URLs; login-gated — will record to errors[] if unreachable
    "https://ansyshelp.ansys.com/Views/Secured/corp/v242/en/aqwa_ref/aqwa_ref.html",
    "https://ansyshelp.ansys.com/Views/Secured/corp/v242/en/aqwa_theory/aqwa_theory.html",
]

def is_login_wall(html: str) -> bool:
    """Heuristic login-wall detection: returns True if fetched HTML is an ANSYS SSO redirect
       or a generic sign-in page (indicators: 'returnurl=/Views/Secured', 'Sign In', 'login')."""
    ...

def ingest_aqwa(output_root):
    product_dir = output_root / "aqwa"
    topics_dir  = product_dir / "topics"
    topics_dir.mkdir(parents=True, exist_ok=True)
    topics, errors = [], []
    for url in AQWA_SEEDS:
        html = fetch_page(url)
        if html is None:
            errors.append({"url": url, "reason": "fetch_failed"}); continue
        if is_login_wall(html):
            errors.append({"url": url, "reason": "gated_login_wall"}); continue
        md, headings = html_to_markdown(html, url)
        title = extract_title(md, fallback=url)
        filename = f"{slugify(url)}.md"
        (topics_dir / filename).write_text(md, encoding="utf-8")
        topics.append({"file": filename, "title": title, "sections": headings, "section_path": ["help"]})
    # Zero-topic case is explicitly permitted — index is still valid JSON
    index = {"generated": iso_now(), "topic_count": len(topics), "topics": topics, "errors": errors}
    (product_dir / "index.json").write_text(json.dumps(index, indent=2))


# ── update-master-index.py (new — merges per-product indexes into master) ──
PRODUCT_KEYS = ["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa"]

def merge_master_index(output_root):
    master_path = output_root / "index.json"
    existing = json.loads(master_path.read_text()) if master_path.exists() else {}
    existing.setdefault("products", {})
    for product in PRODUCT_KEYS:
        p = output_root / product / "index.json"
        if p.exists():
            existing["products"][product] = {"topic_count": json.loads(p.read_text()).get("topic_count", 0)}
    existing["generated"] = iso_now()
    # Atomic write — unique temp filename, same pattern as #2124 v3
    with tempfile.NamedTemporaryFile(dir=master_path.parent, delete=False, suffix=".json.tmp", mode="w") as tmp:
        json.dump(existing, tmp, indent=2, sort_keys=True); tmp_path = tmp.name
    os.replace(tmp_path, master_path)


# ── search-wiki.py (MODIFIED — extends PRODUCTS) ──
# BEFORE (line 15): PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]
# AFTER  (line 15): PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa", "papers"]
# No other changes needed: _load_topics (line 25-30) is generic — it reads <WIKI_DIR>/<product>/index.json's
# `topics` list (or `papers` list when product == "papers"). argparse `--product choices=PRODUCTS + ["supplementary"]`
# at line 166 automatically picks up the new products because it reads the module-level PRODUCTS variable.
```

**Implementation rule:** the new ingesters import shared helpers from `llm_wiki_common.py` (underscore — legal Python module identifier). Neither ingester uses a Python dotted path that traverses `llm-wiki` (the hyphen-containing directory). Tests import each hyphenated ingester file via `importlib.util.spec_from_file_location("module_name", "/abs/path/to/ingest-bemrosetta.py")` — the sanctioned pattern per the hyphen-path memory. This avoids adding a second underscore-named ingester pair (keeping ingester filenames parallel to existing `ingest-orcina.py`) at the cost of slightly more verbose test imports; accepted trade-off documented in Risks.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/llm_wiki_common.py` | **(r1 P1 #2 fix)** shared helpers (`html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`, `slugify`, `USER_AGENT`, `HEADERS`, `POLITE_DELAY_SECONDS`, `REQUEST_TIMEOUT_SECONDS`, `MAX_RETRIES`) in a legally-named Python module. Underscore filename prevents repeat of hyphen-import defect. |
| Modify | `scripts/data/llm-wiki/ingest-orcina.py` | Replace internal defs with `from llm_wiki_common import ...`. Filename stays hyphenated (CLI-only; no Python dotted reference exists). No behavioral change — smoke-tested in Build Sequence. |
| Create | `scripts/data/llm-wiki/ingest-bemrosetta.py` | BEMRosetta GitHub wiki + repo `/doc` + README ingester. Imports helpers via `from llm_wiki_common import ...`. Writes per-product index with `topics: [...]` + `errors: [...]`. |
| Create | `scripts/data/llm-wiki/ingest-aqwa.py` | AQWA ingester with login-wall detection + graceful zero-topic degradation. Imports helpers via `from llm_wiki_common import ...`. |
| Create | `scripts/data/llm-wiki/update-master-index.py` | Merges per-product indexes into `data/llm-wiki/index.json`. Atomic write via `tempfile.NamedTemporaryFile + os.replace` with unique per-process temp filename. |
| **Modify** | **`scripts/data/llm-wiki/search-wiki.py`** | **(r1 P1 #1 fix)** extend `PRODUCTS` from `["orcaflex", "orcawave", "orcfxapi", "papers"]` to `["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa", "papers"]` at line 15. No further logic change needed: `_load_topics` is already product-generic; argparse `--product` choices read the module-level list. |
| Create | `scripts/data/llm-wiki/tests/test_llm_wiki_common.py` | unit tests for shared helpers (import-parity + retry + URL-encode fallback). |
| Create | `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py` | unit tests using fixture HTML + raw MD; imports `ingest-bemrosetta.py` via `importlib.util.spec_from_file_location`. |
| Create | `scripts/data/llm-wiki/tests/test_ingest_aqwa.py` | unit tests covering login-wall detection + zero-topic index; import pattern as above. |
| Create | `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py` | **(r1 P1 #1 fix gate)** integration test: given a fixture `<wiki_dir>` containing `bemrosetta/index.json` + `bemrosetta/topics/hydrodynamic.md`, `search-wiki.py --product=bemrosetta "hydrodynamic"` returns ≥1 hit. Same test asserts `aqwa` is an accepted `--product` value. |
| Create | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_wiki_page.html` | captured offline fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_raw_readme.md` | fixture for raw-MD path |
| Create | `scripts/data/llm-wiki/tests/fixtures/aqwa_login_wall.html` | captured offline fixture (ANSYS SSO redirect page) |
| Create | `scripts/data/llm-wiki/tests/fixtures/aqwa_public_help.html` | captured offline fixture for the happy-path case |
| Create | `scripts/data/llm-wiki/tests/fixtures/search_fixture_wiki/` | search-integration fixture: minimal `bemrosetta/index.json` + `bemrosetta/topics/hydrodynamic.md` + `aqwa/index.json` |
| Update | `docs/plans/README.md` | add this plan to index |

**Dependency status (attested):** `beautifulsoup4>=4.14.3` is already in root `pyproject.toml:12` (per #2124 v3 attested evidence). `ingest-orcina.py` already imports `from bs4 import BeautifulSoup` at line 26. No manifest change required.

---

## TDD Test List

All tests that exercise hyphenated ingesters (`ingest-bemrosetta.py`, `ingest-aqwa.py`) use `importlib.util.spec_from_file_location("module_name", "/abs/path/to/file.py")` to load the file (the sanctioned pattern per the hyphen-path memory). Tests patching `fetch_page` patch the bound name in the consuming ingester module, not `llm_wiki_common.fetch_page` (same pattern as #2124 v3 P2 resolution).

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_llm_wiki_common_html_to_markdown_parity` | `html_to_markdown` behaves identically to the pre-refactor version (locked by a snapshot of ingest-orcina.py's existing output) | HTML fixture used in prior Orcina tests | markdown matches pre-refactor snapshot |
| `test_llm_wiki_common_fetch_page_retries` | retry + timeout policy honored | mocked `urlopen` raising `URLError` twice then succeeding | 2 retries then success; max 3 attempts total |
| `test_ingest_orcina_smoke_after_refactor` | `ingest-orcina.py` CLI still exits 0 after helper extraction | `python3 scripts/data/llm-wiki/ingest-orcina.py --output-dir /tmp --products orcaflex` on a mocked tree | exit 0, no ImportError |
| `test_bemrosetta_wiki_page_converts` | GitHub-wiki HTML fixture renders to markdown with `<!-- source: ... -->` comment and H1 | fixture HTML | markdown string containing `# <title>` + source comment |
| `test_bemrosetta_raw_md_passthrough` | a `.md` fetched from raw.githubusercontent passes through with source header added | raw md bytes + URL | md begins with `<!-- source: ... -->` |
| `test_bemrosetta_writes_product_index_shape` | index.json emitted at `<out>/bemrosetta/index.json` with `topics: [...]` key matching `search-wiki.py:_load_topics` schema | mocked fetcher yields 3 topics | index.json has `topics` list length 3; each entry has `file`, `title`, `sections` |
| `test_bemrosetta_api_rate_limit_fallback` | when GitHub API tree endpoint returns 403/rate-limit, ingester falls back to README-only + logs WARN | mocked 403 response | ingester completes exit 0 with README-only topics + `errors[]` populated with `rate_limited` reason |
| `test_aqwa_login_wall_recorded_not_crashed` | login-wall HTML is flagged + added to `errors[]`; run completes exit 0 | fixture login HTML | index.json `errors[]` length ≥ 1; `topic_count == 0`; process exit 0 |
| `test_aqwa_zero_topic_index_valid_json` | zero-topic run still writes a valid JSON index | all seeds return login walls | `json.load(index.json)` succeeds; shape has `topics: []` not missing key |
| `test_aqwa_public_happy_path_converts` | when a seed URL is publicly reachable, its HTML is converted and a topic entry is appended | fixture `aqwa_public_help.html` | `topics` has ≥1 entry; `errors` may still be populated for gated seeds |
| `test_update_master_index_merges_all_products` | merger combines orcaflex/orcawave/orcfxapi/bemrosetta/aqwa if each per-product index exists | 5 fake per-product indexes | master `index.json` `products` dict has all 5 keys |
| `test_update_master_index_partial_ok` | merger runs when only a subset of per-product indexes exist | only bemrosetta index present | master has only `bemrosetta`; no KeyError |
| `test_update_master_index_atomic_write` | atomic write uses `os.replace`; no half-written file observable | monkeypatched `json.dump` to raise mid-write | original master unchanged; no leftover `.json.tmp` |
| **`test_search_wiki_products_list_extended`** (r1 P1 #1 gate) | `search-wiki.PRODUCTS` includes `bemrosetta` and `aqwa` | import `search-wiki` module; read `PRODUCTS` | `"bemrosetta" in PRODUCTS and "aqwa" in PRODUCTS` |
| **`test_search_wiki_surfaces_bemrosetta`** (r1 P1 #1 gate) | `search-wiki.py --product=bemrosetta "hydrodynamic"` returns ≥1 hit against a fixture wiki dir | fixture `search_fixture_wiki/bemrosetta/index.json` + topic md with the word "hydrodynamic" in title + body | subprocess exit 0; JSON output list length ≥ 1; first hit's `product == "bemrosetta"` |
| **`test_search_wiki_surfaces_aqwa`** (r1 P1 #1 gate) | `search-wiki.py --product=aqwa` is an accepted argument; if the fixture aqwa index is empty, returns 0 hits without error | fixture `search_fixture_wiki/aqwa/index.json` with `topics: []` | subprocess exit 0; JSON output is empty list; no traceback |
| `test_no_hyphen_in_python_import_paths` | grep check — no `from llm-wiki.` or `from ingest-orcina` or `from ingest-bemrosetta` or `from ingest-aqwa` anywhere in the repo | `grep -rn "from llm-wiki\|from ingest-orcina\|from ingest-bemrosetta\|from ingest-aqwa\|import ingest-" scripts/ docs/` | zero matches |

Fixtures: saved HTML snapshots captured once from upstream; tests never hit the network. Rate-limit test uses a canned `urlopen` mock returning `HTTPError(code=403)`.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_llm_wiki_common.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_aqwa.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py -v` passes — covers `test_search_wiki_products_list_extended`, `test_search_wiki_surfaces_bemrosetta`, `test_search_wiki_surfaces_aqwa` (closes r1 P1 #1).
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` (full suite) passes — no regression on `test_resolve_wiki_path.py` or `test_e2e_smoke.py`.
- [ ] `uv run python scripts/data/llm-wiki/ingest-orcina.py --output-dir /tmp/wiki-smoke --products orcaflex` exits 0 after helper extraction (post-refactor smoke).
- [ ] `uv run python scripts/data/llm-wiki/ingest-bemrosetta.py --output-dir /tmp/wiki-smoke` exits 0 and produces `/tmp/wiki-smoke/bemrosetta/index.json` with `topic_count ≥ 5`.
- [ ] `uv run python scripts/data/llm-wiki/ingest-aqwa.py --output-dir /tmp/wiki-smoke` exits 0 (even if all seeds are gated); `/tmp/wiki-smoke/aqwa/index.json` is valid JSON with `topics` key present.
- [ ] `uv run python scripts/data/llm-wiki/update-master-index.py --output-dir /tmp/wiki-smoke` emits `/tmp/wiki-smoke/index.json` with `products.bemrosetta` and `products.aqwa` present.
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "hydrodynamic" --product=bemrosetta` (pointed at the smoke dir) returns at least one hit from the BEMRosetta corpus (closes r1 P1 #1 live).
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "aqwa" --product=aqwa` is accepted (argparse doesn't reject the value), and returns 0 hits cleanly when the aqwa corpus is empty.
- [ ] `grep -rn "from llm-wiki\|from ingest-orcina\|from ingest-bemrosetta\|from ingest-aqwa" scripts/ docs/` returns zero matches (hyphen-import-pattern regression guard).
- [ ] `grep -n "llm-wiki\." /tmp/plan-drafts/plan-2103-v2.md` returns zero matches (plan-drafting regression guard — hyphen+dot in a plan is an instant smell per hyphen memory).
- [ ] `data/document-index/resource-intelligence-maturity.yaml` gains draft-level maturity rows for `bemrosetta` and `aqwa` corpora (one-time administrative update; attached to this plan's PR).
- [ ] Follow-up priority-queue task filed to add `bemrosetta` + `aqwa` entries to `data/document-index/llm-wiki-external-source-priority-queue.yaml` (non-blocking — ingesters work stand-alone).
- [ ] Plan review artifacts (r2) present at `scripts/review/results/2026-04-24-plan-2103-v2-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

| Provider | Verdict (r1) | Verdict (r2) | Key findings |
|---|---|---|---|
| Claude | MAJOR (inline-content dispatch bug — UNUSABLE; no real findings) | TBD after r2 | — |
| Codex | MAJOR (2 P1s + 1 P2, all real) | TBD after r2 | **All 3 resolved in v2**: (P1) search-wiki extension added with concrete PRODUCTS diff + TDD; (P1) `llm_wiki_common.py` shared-helper module resolves hyphen-import; (P2) cat:data-pipeline retrieval contract fully cited. |
| Gemini | NO_OUTPUT (silent failure) | TBD after r2 | — |

**Overall result (r1):** MAJOR — resolved in v2.
**r2 pending.**

---

## Build Sequence (explicit — maps P1/P2 fixes to order)

1. **Extract shared helpers** to `scripts/data/llm-wiki/llm_wiki_common.py` (move `html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page`, `slugify`, constants from `ingest-orcina.py`). Use verbatim def bodies; signatures unchanged.
2. **Update `ingest-orcina.py`** to `from llm_wiki_common import …`; remove the now-duplicated defs. Run existing Orcina smoke: `python3 scripts/data/llm-wiki/ingest-orcina.py --output-dir /tmp/wiki-smoke --products orcaflex` — must exit 0.
3. **Write `test_llm_wiki_common.py`** — cover `html_to_markdown` parity against a pre-extraction snapshot, fetch_page retry, slugify stability. Run green before moving on.
4. **Modify `search-wiki.py` PRODUCTS** (r1 P1 #1 fix) — one-line literal change at line 15 from 4 elements to 6 elements. Argparse choices at line 166 automatically pick up the extension. No other logic change.
5. **Write `test_search_wiki_surfaces_new_products.py`** (r1 P1 #1 gate, TDD-first) against a fixture wiki dir containing `bemrosetta/index.json` + topic md. Three assertions: PRODUCTS list extended, bemrosetta hit returned, aqwa arg accepted on empty corpus.
6. **Create `ingest-bemrosetta.py`** with three source flows (GitHub wiki / raw repo docs / README). Write tests + fixtures. Per-product index.json writes `topics: [...]` + `errors: [...]`.
7. **Create `ingest-aqwa.py`** with login-wall detection + graceful zero-topic degradation. Write tests + fixtures.
8. **Create `update-master-index.py`** with atomic merge (`tempfile.NamedTemporaryFile` + `os.replace`; unique per-process temp filename). Write merge tests.
9. **Run `test_no_hyphen_in_python_import_paths`** — repo-wide grep must return zero hyphen-import matches.
10. **Add draft-level maturity rows** for `bemrosetta` + `aqwa` to `data/document-index/resource-intelligence-maturity.yaml` (cat:data-pipeline contract).
11. **Live smoke** — run the BEMRosetta ingester once against upstream; confirm ≥5 topics land; run AQWA ingester once, confirm zero-topic + populated errors[] exits 0; run master-index merger; run `search-wiki.py --product=bemrosetta "hydrodynamic"` — ≥1 hit.
12. **Dispatch r2 cross-review** (Claude / Codex / Gemini). Address findings or iterate; do NOT self-approve.

---

## Risks and Open Questions

- **Risk — helper extraction regression in `ingest-orcina.py`:** extraction requires mutating the existing file. Mitigation: mechanical refactor only (imports only, signatures unchanged); `test_llm_wiki_common_html_to_markdown_parity` pins no-regression; step-2 smoke must pass before any new ingester work.
- **Risk — reconciliation with #2124 v3 `orcina_common.py`:** #2124 v3 proposes `scripts/data/llm-wiki/orcina_common.py` covering the same helper surface (`html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page`). If #2124 v3 lands first, this plan's `llm_wiki_common.py` becomes a re-export of its exports (no duplication); if #2103 lands first, #2124 v3's `orcina_common.py` can be recast as a thin re-export of `llm_wiki_common.py`. At implementation time the two plans coordinate via the existing sibling-plan comment thread; non-blocker. Prefer a single `llm_wiki_common.py` as the canonical workspace-shared name for future ingesters.
- **Risk — hyphen-named ingester files (`ingest-bemrosetta.py`, `ingest-aqwa.py`) not importable by Python tests:** resolved by using `importlib.util.spec_from_file_location` in test files (sanctioned pattern per `feedback_llm_wiki_hyphen_module_path_pattern.md`). Alternative considered: rename ingester files to `ingest_bemrosetta.py` + `ingest_aqwa.py` (underscore). Rejected because it breaks parallelism with the existing `ingest-orcina.py` filename; CLI invocation is unaffected either way. Acceptance criterion enforces the grep-regression guard.
- **Risk — AQWA public accessibility unknown at plan time:** ANSYS help is largely gated. Mitigation: design ingester to succeed with zero topics + populated `errors[]` rather than fail. Issue explicitly flags "may require manual doc extraction" — partial coverage is acceptable.
- **Risk — BEMRosetta GitHub API rate limits:** crawling via unauthenticated GitHub API may hit 60 req/hr. Mitigation: use `raw.githubusercontent.com` for all content fetches (no rate limit for most practical volumes); use the GitHub tree API only once per run to enumerate the `/doc` directory; if the single tree-API call is rate-limited, fall back to README-only + WARN + populated `errors[]` (covered by `test_bemrosetta_api_rate_limit_fallback`).
- **Risk — per-product index.json schema drift from `search-wiki.py:_load_topics` expectations:** v2 locks the `topics: [{file, title, sections, section_path}, ...]` shape in the contract section above. Any future schema change must update `search-wiki.py` in the same commit. Grep-regression guard at implementation time: `grep -n "topics\|topic_count" scripts/data/llm-wiki/ingest-{bemrosetta,aqwa}.py` must return matches.
- **Open — registry.yaml ingestion:** adding `bemrosetta`/`aqwa` entries to `data/document-index/registry.yaml` is a downstream job that reads the master `index.json`. Not in scope for this plan's code changes. Confirm with user during approval whether to file that as a follow-up now or wait for first successful ingest.
- **Open — priority-queue update:** `data/document-index/llm-wiki-external-source-priority-queue.yaml` update is non-blocking. Tracked as a sibling follow-up issue under #2242/#2243 umbrella.
- **Open — master-index merging trigger:** automatic at end of each ingester run, or only via standalone `update-master-index.py`? v2 plan: standalone only (simpler, idempotent, consistent with concurrency-safe atomic write). Confirm during approval.

---

## Complexity: T2

**T2** — one shared helpers module + two new ingesters + one new merger script + one surgical modification to `search-wiki.py` (literal extension of a 4-element list to 6 elements) + test suite with offline fixtures + a single-line YAML maturity-row addition. Single domain, bounded surface. Security-adjacent concerns are lighter than #2124 v3 (no ZIP handling), but the multi-source + graceful-degrade AQWA path + search-integration gate keep it above T1.
