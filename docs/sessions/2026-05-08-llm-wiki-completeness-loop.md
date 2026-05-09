# 2026-05-08 — LLM-Wiki Completeness Loop (Iteration 2)

**Loop input:** `/loop complete the llm-wiki repo ecosystem without gaps; the steps to no gaps are: a/ raw-data audit, b/ online-resource analysis, c/ piece together existing code for impromptu lookup, d/ piece together results/databases, e/ suggestions/improvements`

**Method:** 4 background general-purpose research agents dispatched in parallel (read-only scopes), main session synthesizes (e). Prior loop session log: `docs/sessions/2026-05-02-llm-wiki-completeness-loop.md`.

**Durable archive of agent reports:** `.planning/intel/elements-to-llm-wiki/loop-2026-05-08/{gap-A-rawdata,gap-B-online,gap-C-code,gap-D-databases}.md`

---

## TL;DR

Eight wiki domains exist; four are scaffold-stage. The ecosystem has ~25 registries (only ~40% with live consumers), three non-overlapping retrieval surfaces (none cover the spinout repo at `llm-wiki/wikis/`), and ~5+ TB of relevant uncovered raw data in `/mnt/ace`. The single highest-leverage internal target is `O&G-Standards/` (43 GB, 54,916 PDFs, **already pre-OCR'd with `_inventory.db`/`_catalog.json`**). The single highest-leverage external target is **BSEE Data Center** (data.bsee.gov), which feeds 4 of 8 domains. The single highest-leverage code gap is the silent miss at `scripts/knowledge/llm_wiki.py:509` where `cmd_query` hardcodes 4 subdirs and excludes `wiki/standards/` and `wiki/workflows/` from search. The single most under-utilized data asset is `deep-extraction-candidates.tsv` (671 records, zero consumers).

---

## Cross-cutting findings

1. **Two-root drift.** Workspace-hub has retrieval at `scripts/knowledge/llm_wiki.py` over `knowledge/wikis/`; the spinout repo at `llm-wiki/wikis/` only ships a scorecard generator. Three retrieval scripts, three rankings, three scopes — none unifies. **The spinout has no search at all.**

2. **Hyphen-path smell recurrence.** `scripts/data/llm-wiki/` blocks `import scripts.data.llm_wiki.*` and forces `importlib.util` shims. `query-knowledge.sh` scans `knowledge/seeds/` but `llm-wiki/seeds/naval-architecture-resources.yaml` is silently dead because the path-naming doesn't match. Memory note: `feedback_llm_wiki_hyphen_module_path_pattern` — third recurrence.

3. **Registry-without-enforcer.** `freshness-cadences.yaml` declares per-asset cadences with no scheduled runner. `intelligence-accessibility-registry.yaml` parent-model link points to `config/document-intelligence/` which is empty (`.gitkeep` only). Elements ingest (1.92 TB, 41,561 files) is durable on the wiki side, transient on the registry side.

4. **Many small gaps that compound.** Not one big gap — ~40 little ones. Most fixable in tens-of-lines each.

5. **Internal pre-indexing is uncashed.** `O&G-Standards/_inventory.db` + OCR text and `digitalmodel/docs/`'s 86 hand-curated topical subdirs already mirror the wiki taxonomy. Lift cost is much lower than online crawls.

---

## Sub-task (a) — Raw-data audit summary [`gap-A-rawdata.md`]

**Top 8 highest-leverage uncovered `/mnt/ace` targets:**

| Rank | Path | Size | Files | Wiki | Why |
|---:|---|---:|---:|---|---|
| 1 | `O&G-Standards/` | 43 GB | 54,916 PDFs | engineering-standards | Pre-OCR'd, has `_inventory.db` + `_catalog.json` — consume the index |
| 2 | `digitalmodel/docs/` | (subset of 106 GB) | many | engineering + marine-engineering + naval-architecture | 86 topical subdirs map 1-to-1 with wiki taxonomy |
| 3 | `acma-codes/` | 7.1 GB | 4,897 | maritime-law + engineering-standards | Clean split: regulatory bodies vs. class-society codes |
| 4 | `2H/` | 42 MB | 32 | marine-engineering | Tiny but every dir is a deepwater riser/wellhead client report |
| 5 | `client_projects/energy_*` + numbered dirs | (subset of 250 GB) | many | marine + lng-projects + engineering | High-value cherrypick (drilling-riser, metocean, mrv, pipeline-installation, subseafirst) |
| 6 | `frontierdeepwater/` | 6.5 GB | 6,281 | marine-engineering | Deepwater client archive with structured Engineering/, REFERENCES/ |
| 7 | `doris/{61850_zama, 61863_lakach, orcaflex, models, calculations}` | (subset of 38 GB) | many | lng-projects + marine-engineering | Finishes the 3-bucket Elements ingest |
| 8 | Hydro/CFD tool cluster (capytaine, gmsh, HAMS, MoorDyn, MoorPy, openfast, WEC-Sim, opm-common) | <1 GB each | each ~100s-1000s | engineering + marine-engineering | Bundle as one open-source-solvers rollup page |

**Surprises:** `client_projects/` and `docs/` reuse project numbers (dedup needed); `_inventory.db` for O&G-Standards is a free-money win; `Production/` (29 GB) is mostly mp3/mov training media (out of scope without transcription).

**Out of scope:** `aceengineer-admin`, `kaggle-rogii-2026`, `data` (vendor lake), `worldenergydata` (separate GTM).

---

## Sub-task (b) — Online-resource gaps summary [`gap-B-online.md`]

**Sparsity ranking:** `acma-projects` (8 pages, 2 sources) → `lng-projects` (15 pages, no standards/) → `maritime-law` (33 pages, 2 sources) → `engineering-standards` (82 pages, missing regulator surfaces) → `naval-architecture` (74 pages, missing live data feeds). `engineering` is mature (skip). `marine-engineering` needs only narrow strategic adds, not bulk.

**Cross-domain top 10 (impact = breadth × authority × access ease, all verified 2026-05-08):**

| Rank | Source | Domains served | Access |
|---:|---|---|---|
| 1 | **BSEE Data Center** (data.bsee.gov) | engineering-standards, lng-projects, naval-architecture, acma-projects | Free / queryable |
| 2 | **UN DOALOS UNCLOS** | maritime-law, lng-projects, engineering-standards | Free PDF + HTML |
| 3 | **NAVFAC DM-26.5/26.6 + UFC 4-159-03** | acma-projects, naval-architecture, engineering-standards | Free, public release |
| 4 | **ITTC Recommended Procedures register** | naval-architecture, marine-engineering | Free PDFs |
| 5 | **PHMSA Pipeline Incident dataset** | engineering-standards, lng-projects | Free CSV |
| 6 | **IGU World LNG Report 2025** | lng-projects, marine-engineering | Free PDF |
| 7 | **IMO GISIS public modules** | maritime-law, engineering-standards, naval-architecture | Free w/ registration |
| 8 | **NTSB CAROL marine docket** | acma-projects, naval-architecture, maritime-law | Free |
| 9 | **FERC LNG terminal page + eLibrary** | lng-projects, engineering-standards | Free, deep dockets hard |
| 10 | **USACE EM 1110-2-1100 Coastal Engineering Manual** | engineering-standards, naval-architecture, acma-projects | Free PDFs (~350 MB) |

Honorable mentions: NOAA NCEI/GEBCO_2026 bathymetry, CMI Rotterdam Rules + CML database, IAM Subject-Specific Guidelines.

**Excluded** (already covered or in-flight): API design, DNV-OS-E301/F101, ASME B31.4/B31.8, ABS rules, ISO 19900, naval-arch foundations, riser sub-domain, NACE/AMPP (W4-A drafted), BSI subset (W4-B drafted), maritime-law foundations, engineering audit. Issues #2586-#2597 cover prior W1-W3.

---

## Sub-task (c) — Code surface for impromptu lookup [`gap-C-code.md`]

**Three non-overlapping retrieval surfaces, none unify:**

1. `scripts/knowledge/llm_wiki.py query --wiki <domain>` — substring scan over **only** `entities/concepts/sources/comparisons` subdirs of `knowledge/wikis/<domain>/wiki/`. **Silent bug at L509:** misses `standards/` and `workflows/`, the highest-value lookup target.
2. `scripts/data/llm-wiki/search-wiki.py` — TF-IDF over Orcina-only product trees (orcaflex, orcawave, orcfxapi, papers). Hardcoded products. Resolver lands on a **dangling symlink** to ace-linux-1 in this environment, so calls silently return zero results with no diagnostic.
3. `scripts/knowledge/wiki-query-context.sh` — bash fan-out over `llm_wiki.py query` per domain. Inherits all weaknesses of (1).

**Spinout repo (`llm-wiki/wikis/`) has zero search code.** Only ships `llm_wiki_strengthening_scorecard.py`. A subagent asking "where is OCIMF MEG4 documented?" must `Grep` the 8 spinout trees by hand because nothing indexes them.

**No MCP server.** `test_e2e_smoke.py::test_mcp_wiki_search_retrieval` is `pytest.skip("pending #2400")`. Subagents cannot call retrieval as a typed tool.

**Top 5 code gaps with concrete fix shape:**

1. **No unified search across the two roots** — add `scripts/knowledge/wiki_search_all.py` walking both `knowledge/wikis/` and `llm-wiki/wikis/`, TF-IDF scored, single ranked JSON output. Stop fanning per-domain via bash.
2. **`cmd_query` 4-subdir hardcode at L509** — change literal list to `glob("wiki/*/")` minus `{visualizations, raw}`, OR drive from a `WIKI_QUERY_DIRS` constant aligned with `INIT_DIRS`. **One-line fix, high impact.**
3. **No MCP `wiki_search` server** — thin FastMCP wrapper at `scripts/mcp/wiki_search_server.py` over the unified search function; one tool `wiki_search(query, deep=False, limit=20)`.
4. **Resolver picks dangling symlink without warning** — add `is_symlink() and not resolve(strict=False).exists()` check in `resolve_wiki_path.py` branch #3, plus `--diagnose` flag.
5. **Hyphen-path tax + no inverted index** — rename `scripts/data/llm-wiki/` → `scripts/data/llm_wiki/` (`git mv` + compat symlink for one release); promote `search-index.json` from on-demand grep to per-token inverted index.

---

## Sub-task (d) — Registries/databases ecosystem [`gap-D-databases.md`]

**~25 registries across 6 surfaces; ~40% have live consumers.** Most-consumed: `standards-transfer-ledger.yaml` (7+ scripts) and `online-resource-registry.yaml` (5 scripts). Most under-utilized: `deep-extraction-candidates.tsv` (671 rows, zero consumers).

**Top 5 integration gaps:**

| # | Gap | Fix shape |
|---|---|---|
| 1 | `deep-extraction-candidates.tsv` rots — 671-row queue with no consumer | Small dispatcher `scripts/data/elements/next-extraction-candidate.py` that pops next high-priority row, opens/updates a child issue under #2536, surfaces from `/whats-next` |
| 2 | `config/document-intelligence/` empty (only `.gitkeep`) — registry parent-model link points there but the directory is unpopulated | Either populate (scoring weights, cadence overrides, profile defaults) **or** drop the directory and remove parent-model references |
| 3 | Elements ingest (1.92 TB, 41,561 files) invisible to registry | Add 3 rows to `intelligence-accessibility-registry.yaml`: ingest-manifest, extraction-queue, classification |
| 4 | `freshness-cadences.yaml` declares cadences with no enforcer | Wire nightly job (existing `scripts/cron/external-doc-reingest.sh`) that loads cadences, emits stale-asset report into daily-readiness issue |
| 5 | `llm-wiki/seeds/naval-architecture-resources.yaml` silently dead | Patch `query-knowledge.sh` to also scan `llm-wiki/seeds/*.yaml`; verify hyphen-path with grep before fix |

**Significant orphans (no in-tree consumer):** `elements-ingested-files.jsonl` (44 MB), `online-resource-registry-patch-2026-05-03.yaml`, `freshness-cadences.yaml`, `resource-intelligence-maturity.yaml`, `enhancement-plan.yaml` (1.7 MB, archive candidate), `index.jsonl.backup-2026-04-17` (604 MB backup).

**Significant duplicates:** conference-registry vs. conference-paper-catalog (95% overlap); priority-queue YAML vs. MD twin; resource-intelligence-maturity YAML vs. MD twin.

---

## Sub-task (e) — Suggestions / improvements

Organized in 5 tiers from cheapest-and-most-reversible to most-strategic:

### Tier 1 — Stop the hemorrhage (small reversible fixes, hours each)

- **E1.** Fix `cmd_query` L509 (4-subdir hardcode → glob). One line. Highest-value lookups (`standards/`, `workflows/`) become reachable.
- **E2.** Fix `query-knowledge.sh` to also scan `llm-wiki/seeds/`. Resurrects naval-architecture-resources.yaml.
- **E3.** Fix `resolve_wiki_path.py` to detect dangling symlinks + `--diagnose` flag. Eliminates silent zero-result failures.
- **E4.** Resolve `config/document-intelligence/` ambiguity: either populate or remove + update `intelligence-accessibility-registry.yaml` parent-model link.
- **E5.** Add 3 registry rows for the Elements ingest (ingest-manifest / extraction-queue / classification asset_types).

### Tier 2 — Build the missing retrieval surface (medium effort, days)

- **E6.** Unified `wiki_search_all.py` over both `knowledge/wikis/` and `llm-wiki/wikis/`. Steal `search-wiki.py` TF-IDF; expand to all subdirs.
- **E7.** Promote `search-index.json` to per-token inverted index. Sub-second `--deep` queries.
- **E8.** MCP server `wiki_search` per #2400 (currently `pytest.skip`). Thin FastMCP wrapper. Subagents call retrieval as typed tool.
- **E9.** Rename `scripts/data/llm-wiki/` → `scripts/data/llm_wiki/` to retire the hyphen-path tax. `git mv` + compat symlink for one release; remove `importlib.util` shims everywhere.

### Tier 3 — Wire orphans to consumers (small to medium, days)

- **E10.** Build `next-extraction-candidate.py` dispatcher for the 671-row queue (gap #1 above).
- **E11.** Wire `freshness-cadences.yaml` to nightly cron; emits stale-asset report.
- **E12.** Sweep duplicates: archive `conference-paper-catalog.yaml` (twin), `enhancement-plan.yaml` (1.7 MB, 2026-03-15), `index.jsonl.backup-2026-04-17` (604 MB), `weekly-utilization.json` (superseded). Reclaims ~2.5 GB of dead state.

### Tier 4 — Fill the highest-leverage data gaps (medium to large, days to weeks)

- **E13. `O&G-Standards/` ingest** → engineering-standards. Consume existing `_inventory.db` + OCR text. **Lowest cost / highest coverage win** because the heavy work is already done.
- **E14. `digitalmodel/docs/` ingest** (86 topical subdirs) → engineering + marine-engineering + naval-architecture. Per-subdir mapping table needed first.
- **E15. BSEE Data Center pipeline** → 4 domains simultaneously. Free, queryable. Build a domain-aware fetch+classify+page-emit script.
- **E16. `acma-codes/` split** → maritime-law + engineering-standards. Pre-classify by directory name (regulatory body vs. class society vs. national code).
- **E17. NAVFAC DM-26.x suite** → acma-projects (closes the standards gap on the sparsest domain).

### Tier 5 — Architectural improvements (larger, decision-required)

- **E18. Decide the canonical wiki location.** Currently both `knowledge/wikis/` and `llm-wiki/wikis/` exist with partial overlap. Either deprecate `knowledge/wikis/` in favor of the spinout, OR formalize the dual-root model with a single retrieval layer in front of both. Without resolution, every retrieval/index/lint script needs both-root awareness forever.
- **E19. Wiki-health KPI dashboard.** A daily-readiness section that reports: orphan-registry count, broken-reference count, missing-standards-per-domain, days-since-last-update-per-domain, scorecard delta. Surfaces drift automatically rather than waiting for the next ad-hoc audit.
- **E20. Per-domain completeness scorecard on schedule.** Extend the spinout's `llm_wiki_strengthening_scorecard.py` to run nightly and emit a single delta line into the daily-readiness issue (or hermes work queue).
- **E21. Promote intel→durable for Elements assets.** Move `elements-ingested-files.jsonl`, `deep-extraction-candidates.tsv`, classification.tsv into `data/document-index/` with proper registry rows, per `durable-vs-transient-knowledge-boundary.md`. Stops them aging out as one-shot intel.
- **E22. Anti-recurrence enforcement.** Add a Level-2 script (per `.claude/rules/patterns.md`) that fails if any new wiki-search-style script hardcodes a path list — drives discoverability through a single `WIKI_QUERY_DIRS` constant. Promote to pre-commit hook only after the existing scripts converge.
- **E23. Codify external-source ingest path** (already partial per `feedback_llm_wiki_external_post_ingest_workflow`). Generalize the LinkedIn/blog → wiki workflow to apply to BSEE/PHMSA/USACE/NAVFAC pipelines so non-text sources (CSV, FGDB, GIS) have a defined adapter rather than ad-hoc per-source code.

---

## Top-N consolidated next actions (ranked by leverage × reversibility)

| Rank | Action | Tier | Estimated effort | Risk |
|---:|---|---|---|---|
| 1 | E1: `cmd_query` 4-subdir hardcode fix (one line) | T1 | minutes | none — additive |
| 2 | E13: ingest `O&G-Standards/` consuming pre-built index → engineering-standards | T4 | hours-day | low — already-OCR'd; pure additive content |
| 3 | E2: `query-knowledge.sh` seeds path fix | T1 | minutes | none — additive |
| 4 | E10: deep-extraction dispatcher (drains 671-row queue) | T3 | hours | low |
| 5 | E5: Elements registry rows (3 entries) | T1 | minutes | none |
| 6 | E6+E8: unified `wiki_search_all.py` + MCP wrapper (closes #2400) | T2 | day-2 days | medium — touches multiple call sites |
| 7 | E15: BSEE Data Center pipeline (4-domain feed) | T4 | day-2 days | low — pure content add |
| 8 | E18: canonical-wiki-location decision | T5 | discussion | requires user direction |
| 9 | E19: wiki-health dashboard | T5 | days | medium — new surface |
| 10 | E22: anti-hardcoded-paths enforcement script | T5 | hours | low |

---

## Loop status

**Iteration 1** (2026-05-08 17:43): dispatched 4 parallel research agents.
**Iteration 2** (2026-05-08 17:53): synthesized + archived findings + composed sub-task (e).
**Iteration 3** (2026-05-08 18:01): user re-invoked `/loop`; applied **E1** — replaced the 4-subdir hardcode in `scripts/knowledge/llm_wiki.py` `cmd_query` (was `["entities", "concepts", "sources", "comparisons"]`) with `sorted(d for d in wiki_dir.iterdir() if d.is_dir())`. All 40 non-pre-broken tests pass; `.glob("*.md")` filter keeps image-only `visualizations/` harmless. Uncommitted (Hermes TUI active). **New finding** discovered while testing: `TestStatus::test_status_counts_engineering_wiki_standards` was already failing — it asserts `engineering/wiki/standards/` has ≥7 pages but workspace-hub `knowledge/wikis/*/wiki/standards/` is empty (content moved to spinout). Should be retracked alongside E18 (canonical-wiki decision) — the test needs to either point at the spinout or be skipped/removed.
**Iteration 4** (2026-05-08 18:46): applied **E2** — extended `scripts/knowledge/query-knowledge.sh` to scan both `knowledge/seeds/` and `llm-wiki/seeds/` for `entries[]`-style yamls (added `WIKI_SEEDS_DIR` env var, expanded the mtime cache to include all discovered seed yamls, replaced the `career-learnings.yaml` hardcode with sorted-discovery). Smoke tests now resurface 40 mooring-failure entries, 19 maritime-law-cases entries, and maritime-liabilities seeds; career-learnings regression guard passed. **E5 deferred** to iteration 5 — surfaced a hidden cost: `scripts/data/document-index/validate-accessibility-registry.py` has an `ASSET_TYPE_ENUM` that rejects unknown values, so adding `ingest-manifest`/`extraction-queue`/`classification` rows requires extending the enum in two places (registry header comment + validator constant), not just appending the 3 entries.

**Iteration 5** (2026-05-08 19:15): applied **E5** — extended `ASSET_TYPE_ENUM` in `scripts/data/document-index/validate-accessibility-registry.py` with 3 new values (`ingest-manifest`, `extraction-queue`, `classification`); bumped registry `schema_version` 1.1.2 → 1.1.3 with history-note; appended 3 rows for the Elements-ingest assets in a new "L4 — Elements → LLM-Wiki Ingest Artifacts" section. Validator confirms all 3 new rows valid (paths exist, enum values accepted), bringing registry from 26 → 29 entries. **Surfaced finding**: 4 pre-existing validator errors discovered, ALL pre-dating E5: `wiki-engineering`/`wiki-maritime-law`/`wiki-naval-architecture` rows point at `knowledge/wikis/<domain>/wiki/` paths that no longer exist (content moved to spinout); `knowledge-seeds` row points at `knowledge/seeds/` which has been replaced by `llm-wiki/seeds/`. **This is the third consecutive iteration to find latent breakage tied to E18** (canonical-wiki decision) — iter-3 found a test failure, iter-4 a silently dead naval-arch seed, iter-5 four dead registry references. E18 has graduated from "architectural improvement" to load-bearing for downstream-consumer correctness.

**Iteration 6** (2026-05-08 19:44): applied **E3** — `scripts/data/llm-wiki/resolve_wiki_path.py` now detects dangling symlinks at branch #3 and emits an actionable stderr warning (with the symlink target and recovery suggestions) before falling through to `knowledge/wikis/`. Stdout contract unchanged so existing pipes/callers keep working. Test suite: original 10 + 2 new `TestDanglingSymlink` cases (warn-on-broken, no-warn-on-absent), all 12 pass. **Live verification**: ran the script against the actual repo state where `data/llm-wiki -> /mnt/remote/ace-linux-1/ace/digitalmodel/llm-wiki` is dangling (remote unmounted post-spinout); warning fires with the specific target. `--diagnose` flag from gap-C deferred — minimal fix shipped without it.

**Iteration 7** (2026-05-08 20:12): **E4 dissolves to a no-op.** Gap-D's claim of an empty-with-`.gitkeep` `config/document-intelligence/` was a fabrication — that path has never existed in git history; no references anywhere in `scripts/`, `data/`, `.claude/rules/`, `CLAUDE.md`, or `AGENTS.md`. The closest real paths are `config/doc-intelligence/` (populated, 2 yamls) and `docs/document-intelligence/` (policy-doc surface, populated). Nothing to fix or remove. Lesson: research-agent filesystem assertions must be independently verified — gap-D was mostly correct but had this one hallucinated claim. Pattern-adjacent to `feedback_subagent_write_phantom`.

**Tier-1 status: COMPLETE.** E1 ✓ E2 ✓ E3 ✓ E5 ✓ E4 ✓ (no-op). Net delivered: 4 real fixes (`cmd_query` iterdir, `query-knowledge.sh` dual-root seeds, registry-3-rows + enum extension, resolver dangling-symlink warning), 1 verified no-op, 4 documented latent-breakage findings tied to E18.

**Loop ending here.** Reasoning: continuing autonomously means either Tier-2 architectural lift (E6 unified `wiki_search_all.py`, E7 inverted index, E8 MCP wrapper, E9 hyphen-path rename) which is multi-iteration architecture work needing user input on shape, OR Tier-3 destructive cleanup (archive ~2.5GB of duplicate registries) which needs explicit authorization. Both are larger than fits in autonomous iteration. The accumulated evidence for E18 (4 latent-breakage findings) suggests it's time for that architectural decision regardless.

**To resume:** re-invoke `/loop` with a more specific scope, e.g.:
- `/loop pivot to E18: sweep all 'knowledge/wikis/' references and produce a canonical-wiki migration plan` — addresses the recurring root cause
- `/loop apply E6+E8: build unified wiki_search_all.py + thin MCP wrapper closing #2400` — biggest UX gain for impromptu lookup
- `/loop apply E10: build deep-extraction-candidates.tsv dispatcher` — drains the 671-row queue now that the registry rows exist
- `/loop apply E13: ingest O&G-Standards/ (43GB pre-OCR'd) into engineering-standards` — biggest single-shot content fill
- `/loop apply E12: archive duplicate registries (enhancement-plan.yaml, conference-paper-catalog.yaml, index.jsonl.backup)` — destructive cleanup, ~2.5GB reclaim

To resume execution: re-invoke `/loop` with a more specific instruction, e.g. *"now apply E1+E2+E3 (Tier-1 cheap fixes)"* or *"now ingest O&G-Standards into engineering-standards"*. Each is small enough to fit one iteration.

---

## References

- Prior loop: `docs/sessions/2026-05-02-llm-wiki-completeness-loop.md` (12 issues #2586-#2597 + W4 drafted-but-blocked)
- Loop state from prior round: `.claude/state/llm-wiki-completeness-loop/state.json`
- Skills: `parallel-llm-wiki-gap-to-issues`, `llm-wiki-ecosystem-gap-to-issues`, `llm-wiki-roadmap-integration`, `repair-legacy-llm-wiki-frontmatter-dates`
- Detailed agent reports: `.planning/intel/elements-to-llm-wiki/loop-2026-05-08/{gap-A,gap-B,gap-C,gap-D}-*.md`
- Relevant memory feedback: `feedback_llm_wiki_hyphen_module_path_pattern`, `feedback_llm_wiki_external_post_ingest_workflow`, `feedback_subagent_write_phantom`, `feedback_hermes_active_preflight_check`

---

## Iteration 3 — E1 (2026-05-08 18:01)

Re-invoked `/loop` (same prompt). Applied **E1** at `scripts/knowledge/llm_wiki.py:505-518` — replaced the 4-element subdir hardcode `["entities", "concepts", "sources", "comparisons"]` with `sorted(d for d in wiki_dir.iterdir() if d.is_dir())`. The `.glob("*.md")` filter keeps image-only `visualizations/` harmless. All 40 non-pre-broken tests pass.

**New finding while testing**: `TestStatus::test_status_counts_engineering_wiki_standards` was already failing (asserts `engineering/wiki/standards/` ≥ 7 pages but workspace-hub `knowledge/wikis/*/wiki/standards/` is empty — content moved to spinout). Pre-existing, not caused by E1. **First piece of E18 evidence** (canonical-wiki-decision becomes load-bearing).

## Iteration 4 — E2 (2026-05-08 18:46)

Applied **E2** at `scripts/knowledge/query-knowledge.sh` via three atomic edits:
1. Added `WIKI_SEEDS_DIR="${WIKI_SEEDS_DIR:-${REPO_ROOT}/llm-wiki/seeds}"`.
2. Passed `wiki_seeds_dir` into the python heredoc.
3. Replaced the `career-learnings.yaml` hardcode with sorted-discovery across both seed roots; expanded the mtime cache to include all discovered seed yamls so a stale `index.jsonl` can't mask new seeds.

Smoke tests: mooring/MV-Prestige queries surface 40+ entries previously invisible; `--category mooring-failures` works; career-learnings regression-guard passes. **`naval-architecture-resources.yaml` remains silently dead** — its `textbooks[]/online_portals[]` schema lacks the `entries[]` key that this loader handles. Out-of-scope by design; needs a separate normalizer or parallel reference-lookup path. **Second piece of E18 evidence**.

## Iteration 5 — E5 (2026-05-08 19:15)

Applied **E5**: extended `ASSET_TYPE_ENUM` in `scripts/data/document-index/validate-accessibility-registry.py` with three new values (`ingest-manifest`, `extraction-queue`, `classification`). Bumped registry `schema_version` 1.1.2 → 1.1.3 with history-note. Appended 3 rows in a new "L4 — Elements → LLM-Wiki Ingest Artifacts" section before Recurring-Operational. Validator confirms all 3 new rows clean; registry 26 → 29 entries.

**Surfaced finding**: 4 pre-existing validator errors discovered: `wiki-engineering`/`wiki-maritime-law`/`wiki-naval-architecture` rows point at `knowledge/wikis/<domain>/wiki/` paths that no longer exist (content moved to spinout); `knowledge-seeds` row points at `knowledge/seeds/` which is now `llm-wiki/seeds/`. **Third piece of E18 evidence** — every consumer that points at `knowledge/wikis/<domain>/wiki/` is now broken after the 2026-05-05 spinout.

## Iteration 6 — E3 (2026-05-08 19:44)

Applied **E3** at `scripts/data/llm-wiki/resolve_wiki_path.py` branch #3: dangling-symlink detection + actionable stderr warning naming the symlink target and recovery suggestions (`LLM_WIKI_DATA_DIR` env var or symlink repair). Stdout contract unchanged so existing pipes/callers keep working. Test suite expanded by 2 cases (`TestDanglingSymlink::test_dangling_symlink_at_data_llm_wiki_warns_and_falls_through` + `test_no_warning_when_data_llm_wiki_simply_absent`); all 12 resolver tests green.

**Live verification**: ran the script against actual repo state where `data/llm-wiki -> /mnt/remote/ace-linux-1/ace/digitalmodel/llm-wiki` is dangling (remote unmounted post-spinout); warning fires with the specific target. Converts a class of silent zero-result failures into actionable feedback. `--diagnose` flag from gap-C deferred — minimal fix without it.

## Iteration 7 — E4 (no-op) + Tier-1 closeout (2026-05-08 20:12)

**E4 dissolves to a no-op.** Gap-D's claim of an empty-with-`.gitkeep` `config/document-intelligence/` was a fabrication — that path has never existed in git history; no references anywhere in `scripts/`, `data/`, `.claude/rules/`, `CLAUDE.md`, or `AGENTS.md`. The closest real paths are `config/doc-intelligence/` (populated, 2 yamls) and `docs/document-intelligence/` (policy-doc surface, populated). Lesson: research-agent filesystem assertions must be independently verified — pattern-adjacent to `feedback_subagent_write_phantom` (read-side analog).

**Tier-1 status: COMPLETE.** E1 ✓ E2 ✓ E3 ✓ E5 ✓ E4 ✓ (no-op). Net delivered: 4 real fixes, 1 verified no-op, 4 documented latent-breakage findings tied to E18.

## Iteration 8 — E13 first wave, parallelized (2026-05-09 07:00–07:10)

User direction: "use subagents or agent teams to run additional loops as necessary to get the work done". Pivoted E13 from sequential per-publisher iteration to 5-way parallel agent fan-out. Constraint check: spinout `llm-wiki/` is MIT/CC-BY-4.0 with vendor-PDF firewall — ingest is **metadata-first** (publisher facts only, no PDF content).

**Deliverables (9 source pages, ~95 KB, all in `llm-wiki/wikis/engineering-standards/wiki/sources/`)**:

| Page | Author | Size | Docs covered | Notable |
|---|---|---:|---:|---|
| `og-standards-dnv.md` | main | 6.4 KB | 100 | Pilot; full topical coverage map (38 codes incl. OS-F101 ×6 ed, RP-C203 ×4 ed) |
| `og-standards-abs.md` | W1 | 5.7 KB | 6 (catalog) | Catalog gap: ABS not in `organization` enum; folder has 29 PDFs but only 6 in catalog |
| `og-standards-asce.md` | W1 | 7.0 KB | 32 (catalog) | Only 4 of 32 are real standards; rest are COPRI-MRE 2011-2015 meeting minutes |
| `og-standards-asme.md` | W2 | 8.3 KB | 88 (filesystem) | Catalog skipped ASME entirely; built via direct filesystem walk (BPVC + B31 + B16 + Tada/Paris/Irwin) |
| `og-standards-bsi.md` | W2 | 9.3 KB | 80 | 25% bucket impurity (4 ABS, 11 FAOS, 7 corrigenda mis-tagged) |
| `og-standards-api.md` | W3 | 21.0 KB | 574 | Largest pilot; 8 series surfaced; zero DRM; 43% OCR coverage; 6+ codes flagged for standards/ promotion |
| `og-standards-iso.md` | W4 | 12.6 KB | 308→112 (filtered) | 64% bucket impurity; 196 personal/legal docs misclassified as ISO; real ISO covers 19900/13628/15156/14224 |
| `og-standards-onepetro.md` | W4 | 12.0 KB | 94 | Reframed as paper-catalog (not standards); OTC submission-pipeline working files dominant |
| `og-standards-minor-publishers.md` | W5 | 12.4 KB | 41 | Bundled AWS/NEMA/MIL/NACE/IEC/HSE/Norsok/SNAME; 20-doc split-out trigger; surveyed Unknown bucket |

**Vendor-PDF firewall honored across all 9 pages**.

**Multi-source-confirmed catalog finding (5 of 5 agents independently)**: `_catalog.json`'s consolidator has structural classification gaps:
- ABS, ASCE, ASME, AWS, NACE, IEC, HSE absent from `statistics.by_organization` enum.
- 196 personal/legal docs misclassified as ISO.
- ~20 of 80 BSI docs are ABS / FAOS / corrigenda.
- 125 structural-fragment artefacts inflate API's "Unclassified" bucket.
- 629 Unknown bucket holds ASME B16/B31 + ASCE 7 standards that should reclassify cleanly.

This is a high-confidence, multi-source-validated production defect in the upstream catalog tool. **Worth filing as a separate issue against the O&G-Standards-Consolidation-System** as the iteration's most-valuable surfaced gap.

**Deferred from E13**:
- ASTM (25,537 docs) — too big without sub-cat batching by ASTM committee letter (A/B/C/D/E/F/G + Standards/Forms/etc.). Future iteration with 6-8 parallel agents.
- Unknown bucket (629 docs) — needs reclassification first; future iteration.

## Hermes Recovery Incident (2026-05-09 07:15-07:30)

Iteration 8 narrative (and iterations 3-7's session-log additions) appeared lost when Hermes performed a memory-bridge commit + state snapshot overnight. Investigation found:

- **All 4 Tier-1 code fixes (E1/E2/E3/E5)** were committed to git history by Hermes's earlier auto-sync (`0746b2111 chore(sync): auto-sync 2026-05-08 20:02`) — **safe in git history all along**, my initial diagnosis was wrong.
- **9 spinout source pages** intact as untracked files in spinout's separate `.git` (the agent-context firewall is also a state-isolation firewall — Hermes can't see across the spinout boundary).
- **Iter-2 baseline of this session log + 4 gap-* reports** captured by Hermes's `pre-bridge-stash` (`stash@{0}`); recovered via `git show 'stash@{0}:<path>' > <path>` (avoiding `index.lock` contention with concurrent Hermes git operations — direct `git show` writes to stdout and bypasses the index entirely).
- **The only true content loss**: iter-3-through-7 narrative additions to this session log made via Edit tool between iterations. Hermes's stash captured an iter-2-baseline snapshot, not the most-recent on-disk version. Iteration sections above are reconstructed from this conversation's context.

**Lessons preserved for memory**:
- `feedback_hermes_active_preflight_check` was correct but its second clause ("use a worktree+feature-branch if active") was ignored. A single Hermes preflight at session start is insufficient when Hermes runs auto-sync and memory-bridge operations between iterations. **Multi-iteration session-log work must commit between iterations OR live in a Hermes-safe location** (the spinout, a feature branch, a worktree).
- Hermes's auto-sync IS protective: it commits working-tree changes to git, which is why the code edits survived. But its `pre-bridge-stash` captures earlier snapshots that don't include intermediate Edit-tool updates to the same file.
- `feedback_stash_caret_3_for_untracked` doesn't apply when Hermes uses `git add -A && git stash` (no `-u` flag); files are accessible directly via `git show stash@{0}:<path>`.
- Trying `git checkout stash@{0} -- <path>` requires the index lock and races with Hermes; `git show stash@{0}:<path> > <path>` is the lock-free recovery primitive.

## Next-iteration recommended scopes (post-recovery)

- **Iteration 9 — ASTM batch**: 25,537 docs in 6 sub-trees; sub-cat batching by ASTM committee letter; 6-8 parallel agents.
- **Iteration 10 — wiki sweep**: update spinout `engineering-standards/wiki/index.md` and `log.md` with the 9 new source-page entries; update overview.md with the publisher coverage matrix.
- **Iteration 11 — catalog reclassification follow-up**: file an issue against the O&G-Standards-Consolidation-System tool to enumerate the 7 missing publishers + reclassify the 629-doc Unknown bucket.
- **Iteration 12 — standards/ promotion**: per W3's recommendation, promote API Spec 6A/6D/17D/17E + Std 579/650/1104 to `wiki/standards/<code-id>.md` first-class pages. Per DNV pilot, OS-F101/RP-C203/RP-B401 multi-edition codes deserve same treatment.
