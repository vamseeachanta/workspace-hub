# Plan for #2103: Extend llm-wiki ingestion to AQWA and BEMRosetta documentation

> **Status:** draft (v3 — addresses r2 Claude P2s; Gemini r2 APPROVED v2)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2103
> **Base commit:** `12b4be834954505ca1e7fc8ad8b20bda34e92baf` (HEAD at v3 plan-drafting time; cite line numbers relative to this SHA)
> **Review artifacts (r1):** see v2 plan history — closed in v2.
> **Review artifacts (r2):**
> - Claude — `scripts/review/results/20260424T205053Z-plan-2103-v2.md-plan-claude.md` (MAJOR — 3 P2s + 4 P3s)
> - Gemini — `scripts/review/results/20260424T205320Z-plan-2103-v2.md-plan-gemini.md` (APPROVE — 2 non-blocking suggestions)
> **Review artifacts (r3, pending):** `scripts/review/results/2026-04-24-plan-2103-v3-{claude,gemini}.md`

---

## Review History (closure summary)

### r1 (resolved in v2)

See v2 plan for the full r1 closure table (search-wiki integration gap P1, hyphen-import P1, cat:data-pipeline contract P2).

### r2 (resolved in v3)

| Finding | Class | Resolution in v3 |
|---|---|---|
| **Test sys.path mechanics undocumented** — when `test_ingest_bemrosetta.py` loads `ingest-bemrosetta.py` via `importlib.util.spec_from_file_location(...)`, the loaded module will execute `from llm_wiki_common import fetch_page, ...`; unless `scripts/data/llm-wiki/` is on `sys.path` (via a conftest.py `sys.path.insert`, a `PYTHONPATH` env, or a preceding `spec_from_file_location` for `llm_wiki_common`), the import will raise `ModuleNotFoundError`. This is the same hyphen-path seam class the plan is trying to fix. | **P2** | **Resolved.** v3 introduces an explicit `scripts/data/llm-wiki/tests/conftest.py` (new file in Files-to-Change) whose body inserts the parent directory on `sys.path` so any test under `scripts/data/llm-wiki/tests/` can do `from llm_wiki_common import ...` and `from ingest_bemrosetta import ...` (after the underscore rename — see P2 #3 below) without surprise. The conftest is the single, declarative resolution mechanism — no `PYTHONPATH` env trickery, no per-test sys.path mutation. Pseudocode and Files-to-Change both reference the conftest explicitly, and a new TDD row `test_conftest_puts_llm_wiki_on_syspath` will assert the resolution mechanic is in place. |
| **#2124 v3 coordination is a race, not a reconciliation** — v2 said "whichever lands first wins" for the shared helpers module. The workspace-memory hazards `feedback_merge_race_silent_revert` and `feedback_multi_agent_commit_serialization` warn that parallel sessions touching overlapping files under auto-sync can silently revert work. Two agents each creating a shared helper module with overlapping helper surfaces is exactly that pattern. | **P2** | **Resolved — option (i): block #2103 execution on #2124 v3 landing first.** v3 declares an explicit dependency: `#2103` execution **does not start** until `#2124 v3` has landed `scripts/data/llm-wiki/orcina_common.py` on `main`. After that lands, `#2103` will **reuse `orcina_common.py` directly** for the four helpers it needs (`html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`) — no second `llm_wiki_common.py` will be created; the shared-helper surface stays singular and `orcina_common.py` becomes the canonical workspace-wide name. Rationale for choosing this over option (ii) (pre-land an empty shim): #2124 v3 has the larger blast radius (5 new content classes, robots.txt policy, ZIP handling), is further along in review (currently in r3), and its `orcina_common.py` is the broader helper surface. Forcing #2124 v3 to wait for an empty shim would invert the dependency arrow and require a second rename PR. This decision invalidates the v2 name `llm_wiki_common.py` — every reference in v3 below uses `orcina_common.py`. |
| **Hyphen-named ingester files perpetuate the anti-pattern** — v2 kept `ingest-bemrosetta.py` and `ingest-aqwa.py` hyphenated for "parallelism with ingest-orcina.py". Three hyphen-path recurrences on 2026-04-24 alone (memory `feedback_llm_wiki_hyphen_module_path_pattern`); the parallelism argument is weaker than the recurrence evidence. | **P2** | **Resolved.** v3 renames the two new ingesters to **`ingest_bemrosetta.py`** and **`ingest_aqwa.py`** (underscore — legal Python module identifiers). Tests now do plain `from ingest_bemrosetta import ingest_bemrosetta` (works because the conftest puts the parent directory on `sys.path` per P2 #1 fix). The `importlib.util.spec_from_file_location` workaround is dropped entirely — eliminates the seam class. The existing `ingest-orcina.py` filename stays hyphenated as legacy (already non-importable; CLI-only invocation), and a follow-up issue can rename it later if desired. CLI invocation paths become `python3 scripts/data/llm-wiki/ingest_bemrosetta.py …` and `python3 scripts/data/llm-wiki/ingest_aqwa.py …`. |

### r2 P3s (acknowledged in v3 — not blocking)

| Finding | v3 disposition |
|---|---|
| cat:data-pipeline contract: consultation-only vs require-updates | v3 cites the contract text at `docs/plans/README.md:53` verbatim (the row's third column reads "consult these inputs", not "update these"). v3 stays with consultation + the maturity-row update (which is a write, not just a read), and explicitly states "consultation satisfied; registry.yaml + priority-queue.yaml updates filed as non-blocking follow-ups". Calls this out so a future r3 reviewer doesn't re-raise. |
| BEMRosetta `topic_count ≥ 5` live-dependent | v3 splits the criterion: live smoke retains an informational ≥5 target, gating acceptance criterion drops to ≥1 ("any successful parse from upstream"). Fixture-based test still asserts the pipeline emits topics correctly when given mocked input. |
| Atomic write only on master index | v3 applies the tempfile + os.replace pattern to per-product `index.json` writes in both new ingesters, not just the master merger. Negligible cost, consistent. |
| search-wiki.py `papers` branching unverified statically | v3 includes the `_load_topics` excerpt verbatim in the Master-index contract section so reviewers can verify the `papers` branch doesn't break the generic path. |

### r2 Gemini suggestions (acknowledged in v3)

- Auto-trigger `update-master-index.py` after each ingester run — v3 keeps the standalone-only design (per Open Question carried from v2; concurrency model is single-shell, serial). Documented in Risks.
- File registry.yaml ingestion task immediately — v3 commits to filing the follow-up at the time of #2103 PR open, as a sibling issue under the #2241 umbrella. Not a code change in this plan.

---

## Attested Evidence

Independently-verifiable claims this v3 plan relies on. Each was checked against HEAD `12b4be834954505ca1e7fc8ad8b20bda34e92baf` on 2026-04-24.

| Claim | Verification method | Result |
|---|---|---|
| Issue #2103 OPEN | `gh issue view 2103` | OPEN — "feat(llm-wiki): extend ingestion to AQWA and BEMRosetta documentation" |
| Issue #2088 CLOSED (parent — Orcina prior-art) | carry-forward from v2 evidence | CLOSED |
| Issue #2140 CLOSED (portable path resolver) | carry-forward from v2 evidence | CLOSED |
| Issue #2124 OPEN (sibling — extended Orcina ingestion + `orcina_common.py` extraction) | carry-forward; r3 in flight | OPEN |
| `scripts/data/llm-wiki/ingest-orcina.py` exists (filename hyphenated, not importable as `ingest_orcina`) | `ls scripts/data/llm-wiki/ingest*.py` | EXISTS — only hyphenated match |
| `scripts/data/llm-wiki/search-wiki.py` hardcodes `PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]` at line 15 | `grep -n "PRODUCTS" scripts/data/llm-wiki/search-wiki.py` | line 15, also referenced at lines 37, 40, 166 — CONFIRMED |
| `search-wiki.py:_load_topics` (lines 25-30) is generic per-product loader; reads `<WIKI_DIR>/<product>/index.json`; honors `topics` key (or `papers` for the papers product) | Read of `search-wiki.py:_load_topics` | CONFIRMED — extending PRODUCTS plus emitting `topics: [...]` keyed indexes is sufficient |
| `docs/plans/README.md:53` requires `cat:data-pipeline` class to **consult** `registry.yaml`, pipeline config, and `resource-intelligence-maturity.yaml` (verb is "consult", not "update") | `grep -n "data-pipeline" docs/plans/README.md` | line 53 row — CONFIRMED. Verb is "consult" |
| `data/document-index/registry.yaml` has NO pre-existing BEMRosetta / AQWA entries | `grep -n "bemrosetta\|aqwa" data/document-index/registry.yaml` | no match — CONFIRMED |
| `data/document-index/resource-intelligence-maturity.yaml` has NO pre-existing BEMRosetta / AQWA maturity rows | `grep -n "bemrosetta\|aqwa" data/document-index/resource-intelligence-maturity.yaml` | no match — CONFIRMED |
| `data/document-index/online-resource-registry.yaml` lists ANSYS AQWA reference/theory/training/product entries + BEMRosetta GitHub repo | `grep -n "aqwa\|bemrosetta" data/document-index/online-resource-registry.yaml` | lines 1031, 1217, 1228, 1238, 1533 — CONFIRMED |
| `data/document-index/llm-wiki-external-source-priority-queue.yaml` exists and governs llm-wiki ingestion pipeline config | `ls data/document-index/llm-wiki-external-source-priority-queue.yaml` | EXISTS |
| `#2124 v3` proposes `orcina_common.py` (underscore-named) covering helpers `html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page` (verbatim move from `ingest-orcina.py` lines 98/135/261/286) | read of `/tmp/plan-drafts/plan-2124-v3.md` Files-to-Change + Pseudocode | CONFIRMED — `orcina_common.py` is the canonical name to reuse from #2103 |
| `scripts/data/llm-wiki/tests/` contains `__init__.py`, `test_e2e_smoke.py`, `test_resolve_wiki_path.py` at HEAD; **no conftest.py exists** | `ls scripts/data/llm-wiki/tests/` | conftest.py NOT FOUND — v3 will create it |

Claims the plan does NOT attest (require live verification during implementation, not plan-approval):
- Exact pagination / sidebar HTML structure of `https://github.com/BEMRosetta/BEMRosetta/wiki` (fixtures will be captured during implementation).
- Exact public-reachability of ANSYS AQWA help URLs from unauthenticated CI — the ingester is designed to degrade gracefully to zero-topic + populated `errors[]` if gated.
- BEMRosetta repo `doc/` directory exact Markdown file count.

---

## Resource Intelligence Summary

### Existing repo code (anchored to base SHA `12b4be83`)
- Found: `scripts/data/llm-wiki/ingest-orcina.py` — canonical prior-art ingester (#2088). Provides `parse_toc_xml()`, `html_to_markdown()`, `_convert_element()`, `_convert_table()`, `fetch_page()`, `ingest_product()`, `ingest_supplementary()`, `ingest_papers()`. Writes to `<output_root>/<product>/topics/*.md` plus `<product>/index.json` and master `index.json`.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — portable output-root resolver (#2140); honors env var → config → `data/llm-wiki/` → `knowledge/wikis/`.
- Found: `scripts/data/llm-wiki/search-wiki.py` — search CLI. **v3-critical:** hardcodes `PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]` at line 15. The `_load_topics()` loader (line 25-30) is generic.
- Found: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py`, `tests/test_e2e_smoke.py` — existing pytest scaffold.
- **Will-exist after #2124 v3 lands (gating dependency for this plan)**: `scripts/data/llm-wiki/orcina_common.py` — shared helpers extracted from `ingest-orcina.py`. v3 of this plan reuses it directly; does NOT create a second helpers module.
- Gap: no `ingest_bemrosetta.py` or `ingest_aqwa.py` exists.
- Gap: no `scripts/data/llm-wiki/tests/conftest.py` exists (created by this plan to put the package directory on `sys.path` for tests — closes r2 P2 #1).
- Gap: no `update-master-index.py` exists.
- Gap: no curated AQWA/BEMRosetta cross-reference under `knowledge/wikis/marine-engineering/wiki/tools/` — out of scope, future issue.

### cat:data-pipeline retrieval contract (v2-resolved; v3 clarifies "consult" verb)

Per `docs/plans/README.md:53`, `cat:data-pipeline` issues must **consult** `registry.yaml`, pipeline config, and `resource-intelligence-maturity.yaml`. The verb is consult, not update — verified verbatim. v3 cites each:

- **`data/document-index/registry.yaml`** — consulted; no pre-existing BEMRosetta/AQWA entries. Registry entries are added by downstream indexing jobs that read the master `index.json`. v3 acceptance criterion treats registry ingestion as a follow-up sibling issue (filed at PR-open time per Gemini suggestion), not a gating criterion.
- **`data/document-index/llm-wiki-external-source-priority-queue.yaml`** — consulted; BEMRosetta/AQWA not yet listed as named source families. v3 files a follow-up sibling task to add them under family `online-data-apis-and-portals`. Ingesters work stand-alone before that lands.
- **`data/document-index/resource-intelligence-maturity.yaml`** — consulted; no pre-existing rows. v3 will add initial draft-level maturity rows for `bemrosetta` and `aqwa` after first successful ingest, attached to this plan's PR.
- **`data/document-index/online-resource-registry.yaml`** (related context) — already lists BEMRosetta GitHub repo (line 1031) + ANSYS AQWA reference/theory/product/training URLs (lines 1217, 1228, 1238, 1533). These provided the canonical seed URLs; no modification required.

### Master-index and per-product-index contract (locks the `search-wiki.py` integration; v3 includes the verbatim `_load_topics` excerpt)

v3 locks the per-product `index.json` shape consumed by `search-wiki.py:_load_topics`. The relevant excerpt (lines 25-30, verbatim per attested read):

```python
def _load_topics(wiki_dir, product):
    idx = wiki_dir / product / "index.json"
    if not idx.exists():
        return []
    data = json.loads(idx.read_text())
    return data.get("topics" if product != "papers" else "papers", [])
```

Branching is on `product != "papers"` — every non-`papers` product (including the new `bemrosetta` and `aqwa`) reads the `topics` key. So as long as the new per-product indexes write a `topics: [...]` key, they surface generically. The TDD test `test_search_wiki_surfaces_bemrosetta` validates this at runtime; the verbatim excerpt above validates it statically.

Each new ingester writes:

```
<output_root>/bemrosetta/index.json  →  {"topics": [{"file": "...", "title": "...", "sections": [...], "section_path": [...]}, ...], "errors": [...]}
<output_root>/aqwa/index.json        →  {"topics": [...], "errors": [...]}
```

The AQWA case tolerates an empty `topics: []` list with populated `errors: [...]`. **v3 change vs v2**: per-product index writes now use the same atomic-write pattern (tempfile + os.replace + unique per-process suffix) as the master merger — closes r2 P3 atomicity inconsistency.

The master-index merger (`update-master-index.py`) merges per-product indexes into `<output_root>/index.json`:

```
{
  "generated": "<iso timestamp>",
  "products": {"orcaflex": {...}, "orcawave": {...}, "orcfxapi": {...}, "bemrosetta": {...}, "aqwa": {...}},
  "supplementary": {...}, "papers": {...}
}
```

### Standards
Not applicable — documentation-pipeline issue, not an engineering-standards deliverable.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/` — existing marine-engineering wiki tree; new AQWA/BEMRosetta output lands under `data/llm-wiki/`, not in the curated wiki.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — governance guardrails for durable-curated vs transient-ingested content (#2209).

### Documents consulted
- Issue body #2103 — deliverables: `ingest_bemrosetta.py`, `ingest_aqwa.py` (v3 — underscore), outputs at `data/llm-wiki/bemrosetta/` and `data/llm-wiki/aqwa/`, master index update.
- Parent issue #2088 — CLOSED; defined the MadCap-Flare TOC + `html_to_markdown` pattern.
- Sibling plan `/tmp/plan-drafts/plan-2124-v3.md` — gating dependency; introduces `orcina_common.py` that this plan reuses.
- `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md` — ecosystem roadmap.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — operating model.
- `docs/plans/README.md` — issue-class retrieval contract (line 53 — `cat:data-pipeline`).
- Memory: `feedback_llm_wiki_hyphen_module_path_pattern.md` — drives the underscore-rename + conftest pattern in v3.
- Memory: `feedback_merge_race_silent_revert.md`, `feedback_multi_agent_commit_serialization.md` — drive the block-on-#2124-v3 coordination decision.
- Upstream: `https://github.com/BEMRosetta/BEMRosetta` — open-source repo with `doc/` + GitHub wiki.
- Upstream: ANSYS AQWA help — public help URLs gated behind login; degrade gracefully.

### Gaps identified
- No BEMRosetta ingester (built by this plan).
- No AQWA ingester (built by this plan).
- No conftest.py for tests (built by this plan — closes r2 P2 #1).
- No master-index merger (built by this plan).
- No `search-wiki.py` coverage for new products (extended by this plan).
- No registry / maturity rows (maturity rows added by this plan; registry follow-up filed).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24):
- `#2103` — OPEN
- `#2088` — CLOSED
- `#2140` — CLOSED
- `#2124` — OPEN (gating dependency for this plan)

**File existence** (`ls` 2026-04-24 against HEAD `12b4be83`):
- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py`
- EXISTS: `scripts/data/llm-wiki/resolve_wiki_path.py`
- EXISTS: `scripts/data/llm-wiki/search-wiki.py`
- EXISTS: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py`, `tests/test_e2e_smoke.py`, `tests/__init__.py`
- EXISTS: `data/document-index/{registry,resource-intelligence-maturity,llm-wiki-external-source-priority-queue,online-resource-registry}.yaml`
- WILL-EXIST AFTER #2124 v3 LANDS (gating dependency): `scripts/data/llm-wiki/orcina_common.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/ingest_bemrosetta.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/ingest_aqwa.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/update-master-index.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/conftest.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/test_ingest_aqwa.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py`

Distinct sources consulted: 13 (issue body, #2088, #2140, #2124 v3 sibling plan, `ingest-orcina.py`, `resolve_wiki_path.py`, `search-wiki.py`, marine-engineering wiki, ecosystem-strengthening plan, docs/plans/README.md, operating-model plan #2205 + registry/maturity/queue yaml trio, hyphen-path memory, merge-race memory).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v3) | `docs/plans/2026-04-24-issue-2103-aqwa-bemrosetta-ingestion.md` |
| Shared helpers module (reused, NOT created) | `scripts/data/llm-wiki/orcina_common.py` (created by #2124 v3 — this plan blocks on its landing) |
| BEMRosetta ingester | `scripts/data/llm-wiki/ingest_bemrosetta.py` (underscore — closes r2 P2 #3) |
| AQWA ingester | `scripts/data/llm-wiki/ingest_aqwa.py` (underscore — closes r2 P2 #3) |
| Master-index updater | `scripts/data/llm-wiki/update-master-index.py` |
| Search-wiki CLI (PRODUCTS extended) | `scripts/data/llm-wiki/search-wiki.py` |
| Tests conftest (NEW — closes r2 P2 #1) | `scripts/data/llm-wiki/tests/conftest.py` |
| BEMRosetta tests | `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py` |
| AQWA tests | `scripts/data/llm-wiki/tests/test_ingest_aqwa.py` |
| search-wiki integration test | `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py` |
| Fixtures | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_wiki_page.html`, `bemrosetta_raw_readme.md`, `aqwa_login_wall.html`, `aqwa_public_help.html`, `search_fixture_wiki/bemrosetta/index.json` + sample topic md, `search_fixture_wiki/aqwa/index.json` |
| Ingested output (runtime) | `data/llm-wiki/bemrosetta/topics/*.md`, `data/llm-wiki/aqwa/topics/*.md`, `data/llm-wiki/bemrosetta/index.json`, `data/llm-wiki/aqwa/index.json` |
| Master index | `data/llm-wiki/index.json` |
| Plan reviews (r3) | `scripts/review/results/2026-04-24-plan-2103-v3-{claude,gemini}.md` |

---

## Deliverable

After #2124 v3 lands `orcina_common.py` on `main`, this plan will add: a tests `conftest.py` that puts the llm-wiki package directory on `sys.path` (closes r2 P2 #1); two new underscore-named ingesters — `ingest_bemrosetta.py` (GitHub wiki + repo `doc/` Markdown + raw README) and `ingest_aqwa.py` (ANSYS help with login-wall detection + graceful zero-topic degradation), both reusing `orcina_common.py` helpers (closes r2 P2 #2 + #3); a master-index merger (`update-master-index.py`); and an extension of `search-wiki.py`'s `PRODUCTS` list, so that BEMRosetta and AQWA corpora will surface through the existing search CLI alongside the Orcina family.

---

## Pseudocode

```
# ── scripts/data/llm-wiki/tests/conftest.py (NEW — closes r2 P2 #1) ──
# Put the package directory on sys.path so tests under tests/ can import
# `from ingest_bemrosetta import ...`, `from ingest_aqwa import ...`,
# `from orcina_common import ...` directly without importlib gymnastics.
# This is the SINGLE declarative mechanism — no PYTHONPATH env trickery,
# no per-test sys.path mutation.
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent.parent  # scripts/data/llm-wiki/
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))


# ── scripts/data/llm-wiki/ingest_bemrosetta.py (NEW — underscore name; closes r2 P2 #3) ──
# Reuses orcina_common.py (closes r2 P2 #2 — no second helpers module).
from orcina_common import fetch_page, html_to_markdown, _convert_element, _convert_table

SOURCES = {
    "github_wiki":  "https://github.com/BEMRosetta/BEMRosetta/wiki",
    "repo_docs":    "https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/doc",
    "readme_raw":   "https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/README.md",
    "tree_api":     "https://api.github.com/repos/BEMRosetta/BEMRosetta/git/trees/master?recursive=1",
}

def slugify(url_or_title) -> str:
    """Stable slug from URL or title; mirrors the existing ingester's convention."""
    ...

def _atomic_write_json(path, payload):
    """tempfile.NamedTemporaryFile (suffix=f'.{os.getpid()}.json.tmp') + os.replace.
       v3 change vs v2: applies to per-product index writes too (closes r2 P3 atomicity)."""
    ...

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

    # 2. Repo doc tree via raw.githubusercontent
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
        topics.append({"file": filename, "title": title, "sections": extract_md_headings(md_body), "section_path": ["doc"]})

    # 3. README
    readme_bytes = fetch_raw_markdown(SOURCES["readme_raw"])
    if readme_bytes is not None:
        md_body = f"<!-- source: {SOURCES['readme_raw']} -->\n\n{readme_bytes.decode('utf-8','replace')}"
        (topics_dir / "README.md").write_text(md_body, encoding="utf-8")
        topics.append({"file": "README.md", "title": "BEMRosetta README", "sections": extract_md_headings(md_body), "section_path": ["readme"]})

    # 4. Per-product index — atomic write (v3 change)
    index = {"generated": iso_now(), "topic_count": len(topics), "topics": topics, "errors": errors}
    _atomic_write_json(product_dir / "index.json", index)


# ── scripts/data/llm-wiki/ingest_aqwa.py (NEW — underscore name; closes r2 P2 #3) ──
from orcina_common import fetch_page, html_to_markdown

AQWA_SEEDS = [
    "https://www.ansys.com/products/structures/ansys-aqwa",
    # ANSYS help URLs; login-gated — will record to errors[] if unreachable
    "https://ansyshelp.ansys.com/Views/Secured/corp/v242/en/aqwa_ref/aqwa_ref.html",
    "https://ansyshelp.ansys.com/Views/Secured/corp/v242/en/aqwa_theory/aqwa_theory.html",
]

def is_login_wall(html: str) -> bool:
    """Returns True if HTML is an ANSYS SSO redirect or generic sign-in page
       (indicators: 'returnurl=/Views/Secured', 'Sign In', 'login')."""
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
    # Zero-topic case is permitted; index always valid JSON. Atomic write (v3 change).
    index = {"generated": iso_now(), "topic_count": len(topics), "topics": topics, "errors": errors}
    _atomic_write_json(product_dir / "index.json", index)


# ── scripts/data/llm-wiki/update-master-index.py (NEW — merges per-product indexes) ──
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
    # Atomic write — unique per-process suffix
    with tempfile.NamedTemporaryFile(dir=master_path.parent, delete=False, suffix=f".{os.getpid()}.json.tmp", mode="w") as tmp:
        json.dump(existing, tmp, indent=2, sort_keys=True); tmp_path = tmp.name
    os.replace(tmp_path, master_path)


# ── scripts/data/llm-wiki/search-wiki.py (MODIFIED — extends PRODUCTS) ──
# BEFORE (line 15): PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]
# AFTER  (line 15): PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa", "papers"]
# No other logic change: _load_topics (lines 25-30) is generic; argparse choices read PRODUCTS.
```

**Implementation rule (v3):** the new ingesters import shared helpers from `orcina_common.py` (created by #2124 v3 — gating dependency). Both new ingester filenames are underscore-named (`ingest_bemrosetta.py`, `ingest_aqwa.py`) so tests will use plain `from ingest_bemrosetta import ...` resolved through the new `tests/conftest.py` `sys.path.insert`. No `importlib.util.spec_from_file_location` workaround is used. The grep-regression guard remains as the enforcement floor.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| **(Reuse, NOT create)** | `scripts/data/llm-wiki/orcina_common.py` | Created by #2124 v3 (gating dependency). This plan reuses `html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`. Closes r2 P2 #2 by avoiding a second helpers module. |
| **Create** | **`scripts/data/llm-wiki/tests/conftest.py`** | **(r2 P2 #1 fix)** insert `scripts/data/llm-wiki/` on `sys.path` so tests can import underscore-named ingesters and `orcina_common` directly. |
| Create | `scripts/data/llm-wiki/ingest_bemrosetta.py` | **(r2 P2 #3 fix — underscore filename)** BEMRosetta GitHub wiki + repo `/doc` + README ingester. Imports helpers via `from orcina_common import ...`. Per-product index write uses atomic-write helper (closes r2 P3). |
| Create | `scripts/data/llm-wiki/ingest_aqwa.py` | **(r2 P2 #3 fix — underscore filename)** AQWA ingester with login-wall detection + graceful zero-topic degradation. Atomic per-product index write. |
| Create | `scripts/data/llm-wiki/update-master-index.py` | Merges per-product indexes into `data/llm-wiki/index.json`. Atomic write (`tempfile.NamedTemporaryFile + os.replace`; unique per-process suffix). |
| **Modify** | **`scripts/data/llm-wiki/search-wiki.py`** | extend `PRODUCTS` from `["orcaflex", "orcawave", "orcfxapi", "papers"]` to `["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa", "papers"]` at line 15. |
| Create | `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py` | unit tests using fixture HTML + raw MD; uses plain `from ingest_bemrosetta import ingest_bemrosetta` (works through conftest sys.path). Patches `ingest_bemrosetta.fetch_page` (consuming module's bound name), not `orcina_common.fetch_page` — same monkeypatch pattern as #2124 v3. |
| Create | `scripts/data/llm-wiki/tests/test_ingest_aqwa.py` | unit tests for login-wall detection + zero-topic index. Plain import via conftest. |
| Create | `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py` | integration test: `search-wiki.py --product=bemrosetta` returns ≥1 hit against fixture wiki dir; `aqwa` is an accepted argument. |
| Create | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_wiki_page.html` | offline fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_raw_readme.md` | offline fixture for raw-MD path |
| Create | `scripts/data/llm-wiki/tests/fixtures/aqwa_login_wall.html` | offline fixture (ANSYS SSO redirect page) |
| Create | `scripts/data/llm-wiki/tests/fixtures/aqwa_public_help.html` | offline fixture for the happy-path case |
| Create | `scripts/data/llm-wiki/tests/fixtures/search_fixture_wiki/` | search-integration fixture: minimal `bemrosetta/index.json` + topic md + `aqwa/index.json` |
| Update | `data/document-index/resource-intelligence-maturity.yaml` | add draft-level maturity rows for `bemrosetta` and `aqwa` (cat:data-pipeline contract — consultation + this single update). |
| Update | `docs/plans/README.md` | add this plan to index |

**Dependency status (attested):** `beautifulsoup4>=4.14.3` already in root `pyproject.toml:12`. No manifest change. **Gating dependency**: #2124 v3's `orcina_common.py` must land on `main` before this plan executes.

---

## TDD Test List

All tests use plain `from ingest_bemrosetta import ...` / `from ingest_aqwa import ...` / `from orcina_common import ...` resolved through `tests/conftest.py` `sys.path.insert`. Tests patching `fetch_page` patch the bound name in the consuming ingester module (e.g., `ingest_bemrosetta.fetch_page`), not `orcina_common.fetch_page` — same pattern as #2124 v3.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_conftest_puts_llm_wiki_on_syspath` (r2 P2 #1 gate) | conftest mechanism is in place | run after collection: assert `str(Path(__file__).resolve().parent.parent) in sys.path` | True |
| `test_orcina_common_importable_from_tests` (r2 P2 #1 + #2 gate) | reused helpers module imports cleanly via conftest sys.path | `from orcina_common import html_to_markdown, fetch_page` inside a test | no ImportError |
| `test_bemrosetta_wiki_page_converts` | GitHub-wiki HTML fixture renders to markdown with `<!-- source: ... -->` comment and H1 | fixture HTML | markdown string containing `# <title>` + source comment |
| `test_bemrosetta_raw_md_passthrough` | a `.md` from raw.githubusercontent passes through with source header added | raw md bytes + URL | md begins with `<!-- source: ... -->` |
| `test_bemrosetta_writes_product_index_shape` | index.json emitted at `<out>/bemrosetta/index.json` with `topics: [...]` matching `search-wiki.py:_load_topics` | mocked fetcher yields 3 topics | index.json has `topics` list length 3; each entry has `file`, `title`, `sections` |
| `test_bemrosetta_index_atomic_write` (r2 P3 fix) | per-product index write is atomic — no half-written file under simulated mid-write failure | monkeypatched `json.dump` raises mid-write | original index.json unchanged; no leftover `.tmp` file in dir |
| `test_bemrosetta_api_rate_limit_fallback` | when GitHub API tree endpoint returns 403, ingester falls back to README-only + WARN | mocked 403 response | exit 0 with README-only topics + `errors[]` populated with `rate_limited` reason |
| `test_aqwa_login_wall_recorded_not_crashed` | login-wall HTML is flagged + added to `errors[]`; run completes exit 0 | fixture login HTML | index.json `errors[]` length ≥ 1; `topic_count == 0`; process exit 0 |
| `test_aqwa_zero_topic_index_valid_json` | zero-topic run still writes a valid JSON index | all seeds return login walls | `json.load(index.json)` succeeds; shape has `topics: []` not missing key |
| `test_aqwa_public_happy_path_converts` | when a seed URL is publicly reachable, its HTML is converted and a topic entry is appended | fixture `aqwa_public_help.html` | `topics` has ≥1 entry |
| `test_aqwa_index_atomic_write` (r2 P3 fix) | per-product index write is atomic | monkeypatched `json.dump` raises mid-write | original index.json unchanged; no leftover `.tmp` file |
| `test_update_master_index_merges_all_products` | merger combines orcaflex/orcawave/orcfxapi/bemrosetta/aqwa if each per-product index exists | 5 fake per-product indexes | master `index.json` `products` dict has all 5 keys |
| `test_update_master_index_partial_ok` | merger runs when only a subset of per-product indexes exist | only bemrosetta index present | master has only `bemrosetta`; no KeyError |
| `test_update_master_index_atomic_write` | atomic write uses `os.replace`; no half-written file observable | monkeypatched `json.dump` raises mid-write | original master unchanged; no leftover `.json.tmp` |
| `test_search_wiki_products_list_extended` (carry-forward) | `search-wiki.PRODUCTS` includes `bemrosetta` and `aqwa` | import `search-wiki` module; read `PRODUCTS` | `"bemrosetta" in PRODUCTS and "aqwa" in PRODUCTS` |
| `test_search_wiki_surfaces_bemrosetta` (carry-forward) | `search-wiki.py --product=bemrosetta "hydrodynamic"` returns ≥1 hit against fixture | fixture `search_fixture_wiki/bemrosetta/index.json` + topic md | subprocess exit 0; JSON output list length ≥ 1; first hit's `product == "bemrosetta"` |
| `test_search_wiki_surfaces_aqwa` (carry-forward) | `search-wiki.py --product=aqwa` is accepted; if fixture aqwa index empty, returns 0 hits cleanly | fixture `search_fixture_wiki/aqwa/index.json` with `topics: []` | subprocess exit 0; JSON output is empty list; no traceback |
| `test_no_hyphen_in_python_import_paths` | grep — no Python `from`/`import` statements naming the hyphenated package directory or any hyphenated ingester filename | shell grep across `scripts/` and `docs/` for the hyphen-import patterns enumerated in the test fixture | zero matches |

Fixtures: saved HTML snapshots captured once from upstream; tests never hit the network.

---

## Acceptance Criteria

- [ ] `#2124 v3` has landed `scripts/data/llm-wiki/orcina_common.py` on `main` (gating dependency check before any work begins).
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_aqwa.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py -v` passes — covers extended PRODUCTS list, bemrosetta hit, aqwa argument acceptance.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` (full suite including conftest-loaded discovery) passes — no regression on existing tests.
- [ ] `uv run python scripts/data/llm-wiki/ingest_bemrosetta.py --output-dir /tmp/wiki-smoke` exits 0 and produces `/tmp/wiki-smoke/bemrosetta/index.json` with `topic_count >= 1` (live-dependent floor reduced from v2's `>= 5` per r2 P3 — see Build Sequence step 11 for the informational `>= 5` smoke target).
- [ ] `uv run python scripts/data/llm-wiki/ingest_aqwa.py --output-dir /tmp/wiki-smoke` exits 0 (even if all seeds gated); `/tmp/wiki-smoke/aqwa/index.json` is valid JSON with `topics` key present.
- [ ] `uv run python scripts/data/llm-wiki/update-master-index.py --output-dir /tmp/wiki-smoke` emits `/tmp/wiki-smoke/index.json` with `products.bemrosetta` and `products.aqwa` present.
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "hydrodynamic" --product=bemrosetta` (pointed at smoke dir) returns at least one hit.
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "aqwa" --product=aqwa` is accepted by argparse and returns 0 hits cleanly when corpus empty.
- [ ] `grep -rn "from llm-wiki\|from ingest-orcina\|from ingest-bemrosetta\|from ingest-aqwa" scripts/ docs/` returns zero matches (hyphen-import regression guard).
- [ ] `data/document-index/resource-intelligence-maturity.yaml` gains draft-level rows for `bemrosetta` and `aqwa`.
- [ ] Follow-up sibling issue filed at PR-open time for: (a) `data/document-index/registry.yaml` entries, (b) `data/document-index/llm-wiki-external-source-priority-queue.yaml` entries (per Gemini r2 suggestion). Non-blocking.
- [ ] Plan review artifacts (r3) present at `scripts/review/results/2026-04-24-plan-2103-v3-{claude,gemini}.md`.

---

## Adversarial Review Summary

| Provider | Verdict (r1) | Verdict (r2) | Verdict (r3) | Key findings |
|---|---|---|---|---|
| Claude | MAJOR (inline-content dispatch bug — UNUSABLE) | MAJOR (3 P2s + 4 P3s) | TBD after r3 | r2 P2s all resolved in v3: (P2 #1) explicit `tests/conftest.py` puts package dir on sys.path; (P2 #2) plan is gated on #2124 v3 landing — reuses `orcina_common.py`; (P2 #3) ingester filenames renamed to underscore. r2 P3s addressed: per-product atomic writes + verbatim `_load_topics` excerpt + topic_count floor split. |
| Codex | MAJOR (2 P1s + 1 P2, all real) | not-run (codex-cli upstream regression #2479) | TBD after r3 | r1 closed in v2; r2 not run due to upstream tooling block. |
| Gemini | NO_OUTPUT (silent failure) | APPROVE (2 non-blocking suggestions) | TBD after r3 | Suggestions accepted: registry follow-up filed at PR-open; standalone-only merger model documented in Risks. |

**Overall result (r2):** MAJOR — resolved in v3.
**r3 pending.**

---

## Build Sequence (explicit — maps r2 P2 fixes to order)

1. **Verify gating dependency** (r2 P2 #2). Confirm `#2124 v3` has landed on `main` and `scripts/data/llm-wiki/orcina_common.py` exists with the four required helpers (`html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`). If not landed, BLOCK — do not start.
2. **Create `scripts/data/llm-wiki/tests/conftest.py`** (r2 P2 #1 fix). Insert package dir on `sys.path`. Run `uv run pytest scripts/data/llm-wiki/tests/test_resolve_wiki_path.py -v` to confirm conftest doesn't regress existing tests.
3. **Write `test_conftest_puts_llm_wiki_on_syspath` and `test_orcina_common_importable_from_tests`** — gate the conftest mechanism. Run green.
4. **Modify `search-wiki.py` PRODUCTS** — one-line literal change at line 15 from 4 elements to 6. Argparse choices at line 166 auto-pick-up.
5. **Write `test_search_wiki_surfaces_new_products.py`** (TDD-first) against fixture wiki dir.
6. **Create `ingest_bemrosetta.py`** (r2 P2 #3 — underscore filename) with three source flows. Use atomic per-product index write (r2 P3). Write tests + fixtures using plain `from ingest_bemrosetta import ...`.
7. **Create `ingest_aqwa.py`** (r2 P2 #3 — underscore filename) with login-wall detection + graceful zero-topic. Atomic per-product index write. Write tests + fixtures.
8. **Create `update-master-index.py`** with atomic merge.
9. **Run `test_no_hyphen_in_python_import_paths`** — repo-wide grep must return zero hyphen-import matches.
10. **Add draft-level maturity rows** to `data/document-index/resource-intelligence-maturity.yaml` for `bemrosetta` + `aqwa`.
11. **Live smoke** — run BEMRosetta ingester once against upstream; informational target ≥5 topics (gating floor is ≥1 per acceptance criterion, r2 P3 fix); run AQWA ingester (zero-topic + populated errors[] still exit 0); run merger; run `search-wiki.py --product=bemrosetta "hydrodynamic"` — ≥1 hit.
12. **File follow-up sibling issues** for registry.yaml + priority-queue.yaml entries at PR-open time (Gemini r2 suggestion).
13. **Dispatch r3 cross-review** (Claude / Gemini; Codex blocked by upstream regression #2479). Address findings or iterate; do NOT self-approve.

---

## Risks and Open Questions

- **Risk — gating dependency on #2124 v3 may slip:** if #2124 v3 doesn't land in time, this plan stalls at step 1. Mitigation: dependency is one-directional (#2103 → #2124), no circular wait. If #2124 v3 stalls long enough to threaten #2103 schedule, escalate by either (a) co-landing both PRs in a stacked sequence, or (b) extracting a minimal `orcina_common.py` shim (just the four helpers this plan needs) into its own micro-PR that both #2103 and #2124 v3 consume. The decision tree is captured here so a future operator doesn't need to re-derive it.
- **Risk — helper-extraction regression already absorbed by #2124 v3:** since #2124 v3 owns the `ingest-orcina.py` mutation that creates `orcina_common.py`, this plan inherits that risk transitively but does not create it. The #2124 v3 plan's own parity tests are the load-bearing safeguard.
- **Risk — conftest scope leakage to other test directories:** the new `tests/conftest.py` only affects pytest collection rooted at `scripts/data/llm-wiki/tests/`. It does not pollute repo-wide `sys.path`. Verified by pytest's conftest-discovery model (conftests only apply to their directory subtree).
- **Risk — AQWA public accessibility unknown at plan time:** ANSYS help is largely gated. Ingester succeeds with zero topics + populated `errors[]` rather than fail.
- **Risk — BEMRosetta GitHub API rate limits:** unauthenticated GitHub API may hit 60 req/hr. Mitigation: use `raw.githubusercontent.com` for content; use API only once per run for tree enumeration; on 403 fall back to README-only + WARN.
- **Risk — per-product index.json schema drift from `search-wiki.py:_load_topics` expectations:** v3 locks the `topics: [{file, title, sections, section_path}, ...]` shape AND embeds the verbatim `_load_topics` excerpt for static verification. Any future schema change must update `search-wiki.py` in the same commit.
- **Open — automatic vs standalone master-index trigger** (Gemini r2 question): v3 keeps standalone-only. Concurrency model is single-shell, serial. If future automation chains ingest→merge, atomic per-product writes (r2 P3 fix) make this safe. Confirm during approval whether to auto-trigger.
- **Open — when to file registry.yaml follow-up** (Gemini r2 question): v3 commits to filing at PR-open time. If the user prefers waiting for first successful ingest, defer.

---

## Complexity: T2

**T2** — gated reuse of an existing helper module (`orcina_common.py` from #2124 v3) + two new underscore-named ingesters + one new merger script + one surgical extension of `search-wiki.py`'s PRODUCTS list + a new `tests/conftest.py` + offline-fixture test suite + a single YAML maturity-row addition. Single domain, bounded surface. Multi-source + graceful-degrade AQWA path + search-integration gate keep it above T1; gating dependency on #2124 v3 is the most distinctive coordination element.
