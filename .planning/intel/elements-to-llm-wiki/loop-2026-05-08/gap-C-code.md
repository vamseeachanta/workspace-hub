# llm-wiki Lookup/Retrieval Code Inventory + Impromptu-Use Gap Analysis (Lane C)

Generated: 2026-05-08 — read-only scan, no commits.

## Executive summary (≈200 words)

**What works today.** Two non-overlapping retrieval surfaces exist. (1) `scripts/knowledge/llm_wiki.py query --wiki <domain>` runs a substring keyword scan over `knowledge/wikis/<domain>/wiki/{entities,concepts,sources,comparisons}/*.md` — strict per-domain, no scoring beyond match-count, no `standards/` or `workflows/` coverage. (2) `scripts/data/llm-wiki/search-wiki.py` builds a TF-IDF combined `search-index.json` over Orcina-only product trees (orcaflex/orcawave/orcfxapi/papers) using `resolve_wiki_path.py` to pick the data root. The two systems do NOT share an index, do NOT see the same files, and neither covers the 8-domain spinout repo (`llm-wiki/wikis/<domain>/wiki/`) which only ships a metadata scorecard generator (`llm_wiki_strengthening_scorecard.py`) — no search at all. A bash wrapper (`wiki-query-context.sh`) fans `llm_wiki.py query` over domains for agents.

**Biggest UX gap for impromptu lookup.** There is no single "find every page mentioning Y across the whole wiki ecosystem" entrypoint. A Claude subagent asking "where is OCIMF MEG4 documented?" must (a) know which of three retrieval paths to use, (b) loop the spinout 8 domains by hand because nothing indexes them, (c) fall back to grep. No MCP server exposes search; the e2e test stubs MCP via `pytest.skip("pending #2400")`. The hyphen-in-path smell (`scripts/data/llm-wiki/`) blocks normal `import` and forces `importlib.util` shims in tests.

## Inventory

| File / Dir | Type | Purpose | CLI? | Importable? | Tests? | Gaps |
|---|---|---|---|---|---|---|
| `scripts/data/llm-wiki/search-wiki.py` | Python | TF-IDF search over Orcina product index (orcaflex/orcawave/orcfxapi/papers + supplementary). Fast (titles+sections) and `--deep` (full-text) modes. | yes — `query [--product] [--deep] [--limit] [--rebuild] [--json]` | yes via `importlib.util` only — hyphen path blocks `import` | yes — `tests/test_e2e_smoke.py` invokes via subprocess (#2480) | Hard-coded `PRODUCTS = ["orcaflex","orcawave","orcfxapi","papers"]`; ignores all 8 spinout domains; no fuzzy matching; no incremental update; rebuilds whole combined index on demand. |
| `scripts/data/llm-wiki/resolve_wiki_path.py` | Python | Portable wiki-root resolver: env → config/llm-wiki.yaml → data/llm-wiki → knowledge/wikis. | yes (prints path) | yes via `importlib.util` shim (hyphen path) | yes — `tests/test_resolve_wiki_path.py` covers all four resolution branches (#2140) | Resolved root at `/mnt/local-analysis/workspace-hub/data/llm-wiki` is a **dangling symlink** to `/mnt/remote/ace-linux-1/...` — every search call silently falls back to `knowledge/wikis/`, which is not the same corpus as the Orcina ingest expects (no `orcaflex/index.json`). No env-var defaulted in agent harness. |
| `scripts/data/llm-wiki/ingest-orcina.py` | Python | Crawl Orcina MadCap Flare TOCs (3 products), HTML→MD, scrape papers PDFs, write per-product `index.json`. | yes — `[--output-dir] [--products]` | yes (importlib shim; `html_to_markdown` reused by e2e tests) | yes — fixtures + e2e smoke | Orcina-specific only; no parallel crawler for the 8 spinout domains. |
| `scripts/data/llm-wiki/tests/test_e2e_smoke.py` | pytest | Full-pipeline e2e: ingest fixture HTML → product index → combined index → search retrieves keyword in top-3. | n/a | n/a | self | MCP test (`test_mcp_wiki_search_retrieval`) is `pytest.skip("pending #2400")` — MCP is a *promised* surface, not a built one. |
| `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` | pytest | Path-resolution branch coverage (env / config / repo / fallback). | n/a | n/a | self | None notable. |
| `scripts/knowledge/llm_wiki.py` | Python (1479 lines) | Karpathy-pattern wiki CLI: `init / status / ingest / query / lint / batch-ingest`. `cmd_query` does substring count over entities/concepts/sources/comparisons. | yes — full subcommand surface, `--wiki <domain>` required | yes (clean module path under `scripts/knowledge/`) | yes — `scripts/knowledge/tests/test_llm_wiki.py`, `test_phase4_tools.py` | `cmd_query` only scans 4 hard-coded subdirs — **misses `wiki/standards/` and `wiki/workflows/`**. Substring-count ranking only (no IDF, no title/section weighting). Per-domain only — caller must loop domains. Hard-coded `WIKIS_DIR = REPO_ROOT/"knowledge/wikis"` ignores the spinout `llm-wiki/wikis/`. |
| `scripts/knowledge/wiki-query-context.sh` | bash | Fans `llm_wiki.py query` across multiple domains for agent consumption (#2123). | yes — `<query> [--domains d1,d2] [--limit N] [--json]` | n/a | none in bash test set | Inherits every `llm_wiki.py query` weakness (substring, 4 subdirs). Hard-coded `WIKIS_DIR=knowledge/wikis` — invisible to spinout `llm-wiki/wikis/`. No fuzzy. No reverse-lookup. |
| `scripts/knowledge/doc-key-lookup.py` | Python | Reverse lookup by `doc_key`/sha256/path/standard ID across `data/document-index/index.jsonl`, standards-transfer-ledger, and `knowledge/wikis/*` (#2207). | yes — `<query> [--by key|path|standard] [--json]` | yes | unknown (not surfaced in inventory) | Limited to 4 hard-coded domains: `engineering, marine-engineering, maritime-law, naval-architecture, personal` (literal list at L42). Missing: `acma-projects, asset-management, lng-projects, engineering-standards`. Depends on `data/document-index/index.jsonl` which may be absent. |
| `llm-wiki/scripts/llm_wiki_strengthening_scorecard.py` | Python | Domain-by-domain *scorecard generator* for the spinout (counts curated/source/orphan/etc., emits `docs/reports/...md+json`, generates a faceted `wiki/portal.md`). Dependency-free. | yes — `[--date] [--write] [--portal-domain]` | yes (clean path) | none | **Not a search tool.** This is the only Python in the spinout repo and it does NOT do retrieval. Scorecard depends on `WIKI_ROOT = Path("wikis")` relative-to-cwd — only works when run with cwd=`llm-wiki/`. |
| `llm-wiki/.claude/` | dir | Spinout's gitignored agent-context boundary (per spinout CLAUDE.md). | n/a | n/a | n/a | Empty except for `memory/` placeholder. No skills wired. The agent-context firewall actively prevents cross-importing workspace-hub skills. |
| `.claude/skills/research/llm-wiki/SKILL.md` | skill | Karpathy-pattern wiki authoring/curation skill; wires `scripts/knowledge/llm_wiki.py` for init/status/ingest/lint/batch-ingest. | n/a | n/a | n/a | Trigger words emphasize **authoring** (ingest, lint, audit) — does not strongly trigger on impromptu *lookup* phrasing. |
| `.claude/skills/research/wiki-context/SKILL.md` | skill | Pre-task context retrieval — calls `wiki-query-context.sh`. (#2123, #2208) | n/a | n/a | n/a | Trigger limited to "before engineering domain task / issue planning" — won't fire on bare "where is X documented?" |
| `.claude/skills/coordination/llm-wiki-roadmap-integration/SKILL.md` | skill | Integrate work into existing llm-wiki umbrella issue without dupes. | n/a | n/a | n/a | Not a retrieval skill — issue-management only. |
| `.claude/skills/workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues/SKILL.md` | skill | Convert ecosystem gap analysis → grounded GH issues. | n/a | n/a | n/a | Authoring/governance only. |
| `.claude/skills/workspace-hub-learned/parallel-llm-wiki-gap-to-issues/` | skill | Parallel subagent variant (already loaded by main session — not re-inventoried). | n/a | n/a | n/a | n/a |
| `.claude/skills/workspace-hub-learned/repair-legacy-llm-wiki-frontmatter-dates/SKILL.md` | skill | Repair `added`/`last_updated` frontmatter on legacy source pages. | n/a | n/a | n/a | Maintenance only — not retrieval. |

## E2E user-journey trace: "find every domain page mentioning Y"

**Today's path** (concrete: user asks Claude "where is OCIMF MEG4 documented?")

1. Claude must guess one of three surfaces:
   - `llm_wiki.py query "OCIMF MEG4" --wiki marine-engineering` (per-domain, substring, MISSES `wiki/standards/` because `cmd_query` hard-codes only 4 subdirs at L509).
   - `wiki-query-context.sh "OCIMF MEG4" --domains engineering,marine-engineering,...` — fans the same per-domain query; user must enumerate domains.
   - `search-wiki.py "OCIMF MEG4"` — silently returns nothing because `resolve_wiki_dir()` lands on `knowledge/wikis/` which has no `orcaflex/index.json`; or returns Orcina-only hits if the dangling-symlink corpus were healthy.
2. To cover the spinout repo (`llm-wiki/wikis/{acma-projects, asset-management, engineering, engineering-standards, lng-projects, marine-engineering, maritime-law, naval-architecture}`), Claude has zero search tool — must `Grep` 8 trees by hand or read each `wiki/index.md` (the marine-engineering one is ~20k+ lines per memory).
3. `doc-key-lookup.py` exists for reverse lookup by `doc_key`/standard ID, but its hard-coded domain list at L42 misses 4 of 8 spinout domains and the source-of-truth `data/document-index/index.jsonl` is brittle.

**Friction points**

- Three retrieval surfaces, three different rankings, three different scopes — no canonical answer to "search the wiki."
- Two of the eight spinout domains (`acma-projects`, `lng-projects`) have NO Python retrieval coverage anywhere.
- `cmd_query` in `llm_wiki.py` quietly omits `standards/` and `workflows/` — the very dirs that hold standard-ID lookups like the OCIMF example.
- Resolver returns dangling symlinks without warning; agent gets empty results and no diagnostic.
- No MCP server — main-session subagents cannot call retrieval as a tool; they must shell out.
- Hyphen-in-path (`scripts/data/llm-wiki/`) means `search-wiki.py` cannot be `from scripts.data.llm_wiki import search` — every importer needs `importlib.util` boilerplate (memory: `feedback_llm_wiki_hyphen_module_path_pattern`).
- No reverse lookup "where is `<topic>` documented?" beyond `doc_key`-keyed lookup.

**Ideal path**

`uv run scripts/knowledge/wiki_search.py "OCIMF MEG4" --json --limit 10` returns top-N hits across BOTH `knowledge/wikis/*` and `llm-wiki/wikis/*`, all subdirs (entities/concepts/sources/comparisons/standards/workflows), with TF-IDF scoring + section snippet, exposed identically as MCP tool `wiki_search` so subagents call it without ENV setup.

## Top 5 ranked code gaps with concrete fix shape

1. **No unified search entrypoint across 8 spinout domains.** `llm_wiki.py query` reads `REPO_ROOT/knowledge/wikis/`; spinout pages at `llm-wiki/wikis/<domain>/wiki/` are invisible. **Fix shape:** add a `--root` flag to `cmd_query` (default = current behavior) AND a new `scripts/knowledge/wiki_search_all.py` that walks both roots, applies TF-IDF (steal `search-wiki.py`'s scoring), exits with one ranked JSON list. Stop fanning per-domain via bash.

2. **`cmd_query` misses `standards/` and `workflows/`.** L509: `for category in ["entities", "concepts", "sources", "comparisons"]`. Standards pages — the highest-value lookup target — are silently excluded. **Fix shape:** change the literal list to glob `wiki/*/` minus `{visualizations, raw}`, OR drive it from a `WIKI_QUERY_DIRS` constant updated alongside `INIT_DIRS`. One-line bug, high impact.

3. **No MCP `wiki_search` server.** `test_e2e_smoke.py::test_mcp_wiki_search_retrieval` is a `pytest.skip` placeholder for "#2400 pending". Subagents cannot call retrieval as a typed tool — they must shell out and parse stdout. **Fix shape:** thin FastMCP server `scripts/mcp/wiki_search_server.py` that imports `search-wiki.py`'s `search()` function via the existing `importlib.util` shim, registers one tool `wiki_search(query, deep=False, limit=20)`, returns the same JSON shape as the CLI. Wires straight into the existing test scaffold.

4. **Resolver silently picks dangling symlink.** `data/llm-wiki -> /mnt/remote/ace-linux-1/...` does not exist on this host; `resolve_wiki_dir()` returns it anyway because `Path.exists()` on a broken symlink returns False but the resolver's #3 branch tests `.exists()` on the symlink target — when ace-linux-1 isn't mounted, search returns zero results with no error. **Fix shape:** in `resolve_wiki_path.py` branch #3, add `repo_data.is_symlink() and not repo_data.resolve(strict=False).exists()` → log a warning and skip to fallback. Plus a `--diagnose` flag that prints which branch fired.

5. **Hyphen-in-path forces `importlib.util` everywhere; no fuzzy/full-text inverted index.** `scripts/data/llm-wiki/` cannot be `import scripts.data.llm_wiki.search_wiki`. Every test, every potential MCP server, every reuser pays the boilerplate tax. Combined with the lack of any inverted index (each `--deep` call grep-reads every markdown file at query time), this is the second-largest scaling cliff after the missing unified entrypoint. **Fix shape:** rename to `scripts/data/llm_wiki/` (underscore) with a one-time `git mv` + symlink-back-for-compat for ~1 release, AND promote `search-index.json` to a per-token inverted index (token → list of (file, count)) so `--deep` becomes O(query-tokens × postings) instead of O(corpus). Together these unblock #2400 MCP work.
