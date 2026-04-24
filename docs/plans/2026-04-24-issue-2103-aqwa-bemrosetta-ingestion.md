# Plan for #2103: Extend llm-wiki ingestion to AQWA and BEMRosetta documentation

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2103
> **Review artifacts:** scripts/review/results/2026-04-24-plan-2103-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/llm-wiki/ingest-orcina.py` — canonical prior-art ingester (#2088). Provides `parse_toc_xml()`, `html_to_markdown()`, `_convert_element()`, `_convert_table()`, `fetch_page()` (with URL-encode retry), `ingest_product()`, `ingest_supplementary()`, and `ingest_papers()` (PDF via `pdftotext`). Writes to `<output_root>/<product>/topics/*.md` plus `<product>/index.json` and master `index.json`.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — portable output-root resolver (#2140); honors env var → config → `data/llm-wiki/` → `knowledge/wikis/`. Both new ingesters will reuse this.
- Found: `scripts/data/llm-wiki/search-wiki.py` — search CLI that reads master `index.json`; new tools must merge into the same master so search surfaces AQWA / BEMRosetta topics.
- Found: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` — existing pytest scaffold; new unit tests land alongside.
- Gap: no `ingest-bemrosetta.py` or `ingest-aqwa.py` exists.
- Gap: no `knowledge/wikis/marine-engineering/wiki/tools/aqwa/` or `.../bemrosetta/` scaffolding for cross-referencing diffraction-tool entries.

### Standards
Not applicable — this is a documentation-pipeline issue, not an engineering-standards deliverable.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/` — existing marine-engineering wiki tree; OrcaFlex/OrcaWave topics currently live under the llm-wiki output (`data/llm-wiki/orcaflex/…`) rather than inside this curated wiki. New AQWA/BEMRosetta output will follow the same boundary (ingested bulk content in `data/llm-wiki/`; curated cross-references in `marine-engineering/wiki/tools/`).
- `knowledge/wikis/marine-engineering/CLAUDE.md` — governance guardrails for what is durable-curated vs transient-ingested content.

### Documents consulted
- Issue body #2103 — deliverables: `ingest-bemrosetta.py`, `ingest-aqwa.py`, outputs at `data/llm-wiki/bemrosetta/` and `data/llm-wiki/aqwa/`, master index update. Priority: BEMRosetta first (open-source, GitHub wiki/docs), AQWA second (ANSYS help may require manual extraction).
- Parent issue #2088 — CLOSED; defined the MadCap-Flare TOC + `html_to_markdown` pattern used by Orcina. Serves as the reference implementation contract.
- `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md` — ecosystem roadmap listing AQWA/BEMRosetta as the remaining diffraction-tool gap.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — operating model governing where llm-wiki outputs land and how master `index.json` is consumed.
- Upstream: https://github.com/BEMRosetta/BEMRosetta — open-source repo with `doc/` directory + GitHub wiki; public raw content served via `raw.githubusercontent.com` and rendered wiki via `github.com/.../wiki`.
- Upstream: ANSYS AQWA help — public help URLs are gated behind ansyshelp.ansys.com login. Ingester must degrade gracefully: fetch what is publicly reachable, record unreachable URLs to an errors file, and emit zero-topic index without crashing.

### Gaps identified
- No BEMRosetta ingester (must be built).
- No AQWA ingester (must be built; must tolerate partial accessibility).
- No master-index merge path — current `ingest-orcina.py` overwrites `index.json`. Must extend to merge (or a new `update-master-index.py`) so AQWA/BEMRosetta entries coexist with Orcina entries.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2103` — OPEN — feat(llm-wiki): extend ingestion to AQWA and BEMRosetta documentation
- `#2088` — CLOSED — feat(llm-wiki): ingest OrcaFlex, OrcaWave, and OrcFxAPI online help into llm-wiki
- `#2140` — CLOSED — Replace tracked absolute llm-wiki symlink with portable path resolution and smoke tests

**File existence** (`ls` 2026-04-24):
- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py`
- EXISTS: `scripts/data/llm-wiki/resolve_wiki_path.py`
- EXISTS: `scripts/data/llm-wiki/search-wiki.py`
- EXISTS: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py`
- EXISTS: `knowledge/wikis/marine-engineering/wiki/`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/ingest-bemrosetta.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/ingest-aqwa.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_ingest_aqwa.py`
- MISSING (data dir; runtime-created): `data/llm-wiki/` (resolver default)

**Gap proofs**:
- `ls scripts/data/llm-wiki/ingest-bemrosetta.py 2>&1` → "No such file or directory" → confirms ingester must be built.
- `ls scripts/data/llm-wiki/ingest-aqwa.py 2>&1` → "No such file or directory" → confirms ingester must be built.

Distinct sources consulted: 7 (issue body, #2088, #2140, `ingest-orcina.py`, `resolve_wiki_path.py`, marine-engineering wiki, ecosystem-strengthening plan).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-2103-aqwa-bemrosetta-ingestion.md` |
| BEMRosetta ingester | `scripts/data/llm-wiki/ingest-bemrosetta.py` |
| AQWA ingester | `scripts/data/llm-wiki/ingest-aqwa.py` |
| BEMRosetta tests | `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py` |
| AQWA tests | `scripts/data/llm-wiki/tests/test_ingest_aqwa.py` |
| Master-index updater | `scripts/data/llm-wiki/update-master-index.py` (new) |
| Ingested output (runtime) | `data/llm-wiki/bemrosetta/`, `data/llm-wiki/aqwa/` |
| Master index | `data/llm-wiki/index.json` (merged) |
| Plan reviews | `scripts/review/results/2026-04-24-plan-2103-{claude,codex,gemini}.md` |

---

## Deliverable

Two new ingesters — `ingest-bemrosetta.py` (GitHub wiki + `doc/` Markdown) and `ingest-aqwa.py` (ANSYS help with graceful degradation for gated pages) — plus a master-index merger so the Orcina, AQWA, and BEMRosetta corpora all surface through `search-wiki.py`.

---

## Pseudocode

```
# ingest-bemrosetta.py
SOURCES = {
    "github_wiki": "https://github.com/BEMRosetta/BEMRosetta/wiki",   # HTML-rendered wiki pages
    "repo_docs":   "https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/doc",  # .md files via raw
    "readme":      "https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/README.md",
}

function ingest_bemrosetta(output_root):
    product_dir = output_root / "bemrosetta" / "topics"
    # 1. Wiki: enumerate pages from /wiki sidebar, fetch each, reuse html_to_markdown
    wiki_entries = crawl_github_wiki(SOURCES.github_wiki)
    # 2. Docs: fetch directory listing via GitHub API tree endpoint, download each .md raw
    doc_entries  = fetch_repo_markdown_tree(owner="BEMRosetta", repo="BEMRosetta", subdir="doc")
    # 3. README
    readme_entry = fetch_raw_markdown(SOURCES.readme)
    write entries + build per-product index.json

# ingest-aqwa.py
AQWA_SEEDS = [
    "https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/Aqwa/v251/en/wb_aqwa/wb_aqwa.html",
    # add known public help landing pages discovered during run
]

function ingest_aqwa(output_root):
    product_dir = output_root / "aqwa" / "topics"
    errors = []
    for url in AQWA_SEEDS:
        html = fetch_page(url)
        if html is None or is_login_wall(html):
            errors.append({"url": url, "reason": "gated_or_unreachable"})
            continue
        title, md = html_to_markdown(html, url)
        write md
    write index.json with errors[] populated (zero-topic indexes permitted)

# update-master-index.py
function merge_master_index(output_root):
    master = load output_root/index.json if exists else {products: {}}
    for product_key in ["orcaflex","orcawave","orcfxapi","bemrosetta","aqwa"]:
        p = output_root / product_key / "index.json"
        if p exists: master["products"][product_key] = summary_from(p)
    write master
```

Implementation rule: both new scripts import `parse_toc_xml` is N/A (no MadCap TOC); they reuse `html_to_markdown`, `fetch_page`, and `_convert_element` by factoring those helpers into a shared `llm_wiki_common.py` module OR via `from ingest_orcina import ...` (decision-point — see Risks).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/ingest-bemrosetta.py` | BEMRosetta GitHub wiki + repo `doc/` ingester |
| Create | `scripts/data/llm-wiki/ingest-aqwa.py` | AQWA help ingester with graceful-degrade |
| Create | `scripts/data/llm-wiki/update-master-index.py` | merge per-product indexes into master |
| Create | `scripts/data/llm-wiki/llm_wiki_common.py` | extract shared helpers (`html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`) |
| Modify | `scripts/data/llm-wiki/ingest-orcina.py` | import helpers from `llm_wiki_common.py` (no behavioral change) |
| Create | `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py` | unit tests using fixture HTML / raw MD |
| Create | `scripts/data/llm-wiki/tests/test_ingest_aqwa.py` | unit tests covering login-wall detection + zero-topic index |
| Create | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_wiki_page.html` | captured offline fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/aqwa_login_wall.html` | captured offline fixture |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_bemrosetta_wiki_page_converts` | GitHub-wiki HTML fixture renders to markdown with `<!-- source: ... -->` comment and H1 | fixture HTML | markdown string containing `# <title>` + source comment |
| `test_bemrosetta_raw_md_passthrough` | a `.md` fetched from raw.githubusercontent passes through with source header added | raw md bytes + URL | md begins with `<!-- source: ... -->` |
| `test_bemrosetta_writes_product_index` | index.json emitted at `<out>/bemrosetta/index.json` with `topic_count` matching files | mocked fetcher yields 3 topics | index.json `topic_count == 3`, `topics[]` has 3 entries |
| `test_aqwa_login_wall_recorded_not_crashed` | login-wall HTML is flagged and added to `errors[]`; run completes exit 0 | fixture login HTML | index.json `errors[]` length ≥ 1; `topic_count == 0`; process exit 0 |
| `test_aqwa_zero_topic_index_valid_json` | zero-topic run still writes a valid JSON index | all seeds return login walls | `json.load(index.json)` succeeds |
| `test_update_master_index_merges_all_products` | merger combines orcaflex/orcawave/orcfxapi/bemrosetta/aqwa if each per-product index exists | 5 fake per-product indexes | master `index.json` `products` dict has all 5 keys |
| `test_update_master_index_partial_ok` | merger runs when only a subset of per-product indexes exist | only bemrosetta index present | master has only `bemrosetta`; no KeyError |
| `test_llm_wiki_common_import_parity` | `ingest-orcina.py` still runs after helper extraction (import smoke) | run `python -c "import ingest_orcina"` after refactor | exit 0, no ImportError |

Fixtures: saved HTML snapshots captured once from upstream; tests never hit the network.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_aqwa.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` (full suite) passes — no regression on `test_resolve_wiki_path.py`.
- [ ] `uv run python scripts/data/llm-wiki/ingest-bemrosetta.py --output-dir /tmp/wiki-smoke` exits 0 and produces `/tmp/wiki-smoke/bemrosetta/index.json` with `topic_count ≥ 5`.
- [ ] `uv run python scripts/data/llm-wiki/ingest-aqwa.py --output-dir /tmp/wiki-smoke` exits 0 (even if all seeds are gated); `/tmp/wiki-smoke/aqwa/index.json` is valid JSON.
- [ ] `uv run python scripts/data/llm-wiki/update-master-index.py --output-dir /tmp/wiki-smoke` emits `/tmp/wiki-smoke/index.json` with `products.bemrosetta` present.
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "hydrodynamic"` (pointed at the smoke dir) returns at least one hit from the BEMRosetta corpus.
- [ ] Plan review artifacts present at `scripts/review/results/2026-04-24-plan-2103-{claude,codex,gemini}.md`.

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

- **Risk — helper extraction scope creep:** factoring shared helpers into `llm_wiki_common.py` requires touching `ingest-orcina.py`. Mitigation: keep refactor mechanical (imports only, no signature change); `test_llm_wiki_common_import_parity` pins no-regression.
- **Risk — AQWA public accessibility unknown at plan time:** ANSYS help is largely gated. Mitigation: design ingester to succeed with zero topics + populated `errors[]` rather than fail. Issue explicitly flags "may require manual doc extraction" — partial coverage is acceptable.
- **Risk — BEMRosetta GitHub API rate limits:** crawling via unauthenticated GitHub API may hit 60 req/hr. Mitigation: use `raw.githubusercontent.com` (no rate limit for most practical volumes) and scrape the `/wiki` HTML sidebar rather than the Wiki API.
- **Open:** Should the AQWA ingester accept a user-supplied local tarball of help HTML (manual extraction escape hatch)? Flag for user during approval — leaving out for v1 to keep scope tight; follow-up issue if needed.
- **Open:** Should master-index merging be done automatically at the end of each ingester run, or only via the standalone `update-master-index.py`? Current plan: standalone only (simpler, idempotent). Confirm during approval.

---

## Complexity: T2

**T2** — two new ingesters + one small refactor of an existing file + one new merger script + test suite with offline fixtures. Single domain, bounded surface.
