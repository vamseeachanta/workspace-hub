# Plan for #2369: Execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs

> **Status:** draft
> **Revision:** v2
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2369
> **Review artifacts (v1):** scripts/review/results/20260424T033357Z-2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md-plan-{claude,codex,gemini}.md
> **v1 verdict:** Claude MAJOR, Gemini MINOR, Codex UNAVAILABLE (#2406 stdin-hang).
> **Evidence-block git SHA:** `3142ad33f8e8076e5a7bfb54bd629edf3fd5667a` (HEAD at evidence gathering, 2026-04-24).

---

## Revision Log (v1 → v2)

Surgical deltas applied from Claude P1/P2/P3 + Gemini P2 findings:

| # | Source | Severity | Delta |
|---|---|---|---|
| R1 | Claude P1 | blocker | Cross-link JSONL schema will be inlined as Appendix A in this plan and declared the source-of-truth for #2369; #2068 will adopt this schema, removing the forward-dependency. |
| R2 | Claude P1 + Gemini P2 | blocker | `cluster_by_topic` will be specified with a complete deterministic contract (algorithm, library pin, tokenizer, stop-words, min/max-df, cluster-count rule, tie-break). Implementation will be stdlib-only — no new dependency on scikit-learn — pinned to a custom TF-IDF using `collections.Counter` + `math.log` with a frozen `STOPWORDS` constant. |
| R3 | Claude P2 | major | Strict `assert` on `{DOT,OMAE,OTC}` will be replaced by `log.warning + continue`; new test will cover the ISOPE-becomes-phase_a fixture path. |
| R4 | Claude P2 | major | Domain → target-wiki mapping table will be written down explicitly; new test will iterate the table and assert each maps to an allowed target wiki. |
| R5 | Claude P2 | major | Classifier will return a ranked list (primary + secondary domain) instead of single winner; secondary-signal tests will cover `pipeline ∧ VIV` cross-domain titles. |
| R6 | Claude P2 | major | Acceptance criterion will state `classified + skipped == 14180`; runner will emit `data/document-index/batch-pack-2-skipped.jsonl`; new error-path tests will cover malformed records. |
| R7 | Claude P3 | minor | A one-line footnote will be appended to `llm-wiki-external-source-priority-queue.md` §5.2 and `llm-wiki-staged-batch-packs.md` §3.2 pointing readers to the corrected DOT/OMAE/OTC set in the new report. In-scope this issue. |
| R8 | Claude P3 | minor | Five additional error-path tests will be added (malformed catalog, missing JSONL, empty cluster, unknown indexing_status, unknown conference name). |
| R9 | Claude P3 | minor | Performance budget will be encoded: OMAE sub-slice `<5 min`, full run `<15 min` on reference machine; benchmark test with generous ceiling. |
| R10 | Claude P3 | minor | Evidence block now carries commit SHA `3142ad33` for reproducibility. |
| R11 | Gemini P2 | nit | Gemini "registry-freshness-check.py missing" is a verified false positive — file exists at `scripts/knowledge/registry-freshness-check.py` (7,807 bytes, Apr 16). v1 was correct; no change needed; documented here so the next reviewer doesn't re-raise. |
| R12 | Gemini P2 | major | TF-IDF library pin: stdlib-only (no sklearn), version-pinned to Python `>=3.11` (matches workspace `pyproject.toml`); explicit pseudocode in §Pseudocode below. |
| R13 | Hyphen-path hazard | guard | Plan and tests place no Python dotted import below any `*-*` directory; final grep `llm-wiki\.` enforced in self-check. |

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — LLM-wiki helper module (read-only context).
- Found: `scripts/knowledge/wiki-cross-links.py` — cross-link generator; Batch Pack 2 output will be shape-compatible so cross-link candidates feed into #2068 without re-processing.
- Found: `scripts/knowledge/build-knowledge-index.sh`, `scripts/knowledge/registry-freshness-check.py` — adjacent tooling, read-only context. (Verified present at HEAD `3142ad33`; Gemini v1 false-positive that this file is missing has been closed-out.)
- Gap: No `scripts/knowledge/run_batch_pack_2.py` (or equivalent) exists; runner will be created. **Note:** new runner will use underscore filename (`run_batch_pack_2.py`) — not `run-batch-pack-2.py` — so it can be imported as a Python module from tests under `tests/knowledge/`.

### Standards
Not applicable — conference papers are primary literature, not standards. Provenance still matters: every generated topic-stub will cite its source conference papers by record id.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — 83 pages, organized into `concepts/`, `entities/`, `sources/`, `standards/`, `workflows/`. Conference topic clusters slot into `concepts/` or `sources/`.
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema (`title`, `tags`, `added`, `last_updated` required).
- `knowledge/wikis/marine-engineering/CLAUDE.md` — 19,191 pages; Batch Pack 2 primary target for hydrodynamics/structural/marine clusters.
- `knowledge/wikis/naval-architecture/CLAUDE.md` — 46 pages; secondary target for hydrodynamics and seakeeping clusters.

### Documents consulted
- `docs/reports/llm-wiki-external-source-priority-queue.md` §5.2 — names DOT/OMAE/ISOPE; **contradicted by repo data**.
- `docs/reports/llm-wiki-staged-batch-packs.md` §3.2 — names DOT/OMAE/ISOPE; **contradicted by repo data**.
- `data/document-index/conference-paper-catalog.yaml` — **authoritative**: DOT, OMAE, OTC are `phase_a_complete`; ISOPE is `not_indexed`.
- `data/document-index/conference-phase-a-results.jsonl` — 14,180 records.
- `data/document-index/conference-index-stats.yaml` — top-priority index lists OMAE (7,292), OTC (5,432), ISOPE (4,074), DOT (1,456).
- `data/document-index/conference-index-batch.jsonl`, `conference-index.jsonl`, `conference-index-manifest.json`, `conference-registry.yaml` — existing index outputs available for summary-backed promotion without PDF re-reads.
- Epic `#2390` — Wave 6, explicit readiness note re: DOT/OMAE/OTC vs ISOPE.
- Related issues: `#2068` (OPEN, cross-link JSONL — see R1, this plan now defines the schema), `#2039` (OPEN, engineering wiki ingest), `#2001` (CLOSED, batch ingest precedent).

### Gaps identified
- **Readiness mismatch (CRITICAL):** Issue body, queue doc §5.2, batch-pack spec §3.2 all name DOT/OMAE/ISOPE. Authoritative catalog yaml names DOT/OMAE/OTC. v2 plan will use **DOT + OMAE + OTC** and explicitly defer ISOPE. v2 will append a one-line footnote to both contradicting upstream docs (R7) — in-scope this issue.
- No canonical topic/domain taxonomy for conference clustering — plan will use the six domain heuristics in the spec (subsea, structural, marine, pipeline, VIV, hydrodynamics) plus a `misc` bucket and record the mapping decision.
- No schema for conference "topic stub" — plan will define one (title, target wiki, paper count, top-N paper citations, short abstract cluster, cross-link candidates).
- No explicit de-duplication policy for wiki stubs that overlap with existing wiki pages — plan will add a `sources`-frontmatter duplicate check mirroring the #2364 pattern.
- Issue body acceptance criterion "no source-PDF rereads are required for the first execution slice" — runner will refuse to read under `/mnt/ace/docs/conferences/` (enforced by a path guard + unit test).
- **No cross-link JSONL schema exists yet.** v2 inlines the schema in Appendix A (R1).
- **TF-IDF library pin missing in v1.** v2 uses stdlib-only implementation (R2/R12).

### Evidence (embedded verification)

**Git SHA at evidence gathering:** `3142ad33f8e8076e5a7bfb54bd629edf3fd5667a` (HEAD on `main`, 2026-04-24).

**Issue statuses** (verified via `gh issue view`):
- `#2369` — OPEN — feat(knowledge): execute Batch Pack 2 …
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap
- `#2242` — CLOSED — priority queue
- `#2243` — CLOSED — staged batch packs
- `#2001` — CLOSED — batch ingest precedent
- `#2039` — OPEN — engineering wiki ingest
- `#2067` — OPEN — wire research into wiki ingest
- `#2068` — OPEN — cross-link JSONL package (this plan inlines schema; #2068 will adopt)

**File existence** (`ls` 2026-04-24 at SHA above):
- EXISTS: `docs/reports/llm-wiki-external-source-priority-queue.md`
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md`
- EXISTS: `data/document-index/conference-paper-catalog.yaml`
- EXISTS: `data/document-index/conference-phase-a-results.jsonl` (14,180 lines)
- EXISTS: `data/document-index/conference-index-stats.yaml`
- EXISTS: `data/document-index/conference-index-batch.jsonl`
- EXISTS: `data/document-index/conference-index.jsonl`
- EXISTS: `data/document-index/conference-index-manifest.json`
- EXISTS: `data/document-index/conference-registry.yaml`
- EXISTS: `scripts/knowledge/registry-freshness-check.py` (Gemini v1 false-positive corrected here)
- MISSING (new — this plan creates): `scripts/knowledge/run_batch_pack_2.py`
- MISSING (new — this plan creates): `tests/knowledge/test_batch_pack_2.py`
- MISSING (new — this plan creates): `docs/reports/batch-pack-2-conference-summary-stubs.md`
- MISSING (new — this plan creates): `data/document-index/batch-pack-2-cross-link-candidates.jsonl`
- MISSING (new — this plan creates): `data/document-index/batch-pack-2-skipped.jsonl` (R6)

**Phase-a record verification:** 14,180 lines in `conference-phase-a-results.jsonl` = 1,456 (DOT) + 7,292 (OMAE) + 5,432 (OTC); exact match.

<!-- Source count: 12 (issue body + 11 artifacts) — exceeds ≥3 minimum. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v2) | docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md |
| Runner | scripts/knowledge/run_batch_pack_2.py (new — underscore filename) |
| Tests | tests/knowledge/test_batch_pack_2.py (new) |
| Primary output report | docs/reports/batch-pack-2-conference-summary-stubs.md (new) |
| Cross-link candidates | data/document-index/batch-pack-2-cross-link-candidates.jsonl (new — input for #2068) |
| Skipped/malformed records | data/document-index/batch-pack-2-skipped.jsonl (new — R6) |
| Footnote on contradicting upstream doc 1 | docs/reports/llm-wiki-external-source-priority-queue.md (1-line append, R7) |
| Footnote on contradicting upstream doc 2 | docs/reports/llm-wiki-staged-batch-packs.md (1-line append, R7) |
| Plan reviews v1 | scripts/review/results/20260424T033357Z-…-plan-{claude,codex,gemini}.md |
| Plan reviews v2 | scripts/review/results/<timestamp>-…-plan-2369-v2-{claude,codex,gemini}.md |

---

## Deliverable

After this issue closes, `docs/reports/batch-pack-2-conference-summary-stubs.md` will exist, containing wiki-ready topic-cluster stubs derived from phase_a_complete conference indexing (actual set: DOT, OMAE, OTC), grouped by engineering domain and mapped to target wiki domains (marine-engineering, naval-architecture, engineering). A companion JSONL cross-link-candidate file will exist at `data/document-index/batch-pack-2-cross-link-candidates.jsonl` for #2068 consumption (schema inlined in Appendix A). A sibling `batch-pack-2-skipped.jsonl` will record any malformed input rows. ISOPE will be deferred with a filed follow-on issue for re-indexing. No source-PDF reads will occur. No wiki pages will be promoted in this issue.

---

## Pseudocode

```
function run_batch_pack_2(catalog_path, phase_a_jsonl, output_report_path):
    catalog = load_yaml(catalog_path)
    indexed = [c for c in catalog.conferences if c.indexing_status == "phase_a_complete"]
    indexed_names = {c.name for c in indexed}
    expected = {"DOT", "OMAE", "OTC"}
    if indexed_names != expected:
        log.warning(
            "phase_a_complete drift: expected=%s actual=%s — proceeding with actual set",
            expected, indexed_names
        )                                                          # R3: warn-not-assert
    deferred = [c.name for c in catalog.conferences
                if c.indexing_status != "phase_a_complete"]        # explicit deferral

    papers, skipped = load_jsonl_safely(phase_a_jsonl)             # R6: skip+collect malformed
    assert path_guard_never_reads("/mnt/ace/docs/conferences/")    # hard invariant

    clusters = {d: [] for d in DOMAIN_BUCKETS}                     # 6 domains + misc
    for paper in papers:
        primary, secondary = classify_paper_domain_ranked(
            paper.title, paper.conference, paper.path
        )                                                          # R5: returns ranked list
        clusters[primary].append(paper)
        if secondary:
            paper.secondary_domain = secondary                     # preserved for stub metadata

    stubs = []
    for domain, papers_in_domain in clusters.items():
        if len(papers_in_domain) == 0: continue
        topic_clusters = cluster_by_topic(
            papers_in_domain,
            top_n_per_cluster=10,
            **TFIDF_PARAMS                                         # R2/R12: pinned below
        )
        for topic in topic_clusters:
            target_wiki = DOMAIN_TARGET_WIKI[domain]               # R4: explicit table
            stub = build_topic_stub(topic, target_wiki,
                                    provenance=[p.id for p in topic.top_papers])
            stub.duplicate_candidate = check_wiki_duplicate(
                stub.title, stub.sources, wiki_root
            )
            stubs.append(stub)

    write_report(output_report_path, stubs, deferred_collections=deferred)
    write_cross_link_jsonl(
        "data/document-index/batch-pack-2-cross-link-candidates.jsonl",
        stubs                                                      # schema = Appendix A
    )
    write_skipped_jsonl(
        "data/document-index/batch-pack-2-skipped.jsonl", skipped  # R6
    )
    assert len(papers) + len(skipped) == 14180                     # R6: drift detector
    return summary(
        total_papers=len(papers),
        skipped=len(skipped),
        clusters=len(stubs),
        deferred=deferred
    )
```

### Domain → Target-Wiki mapping table (R4)

```python
DOMAIN_TARGET_WIKI = {
    "pipeline":      "engineering",
    "subsea":        "engineering",
    "VIV":           "marine-engineering",
    "hydrodynamics": "marine-engineering",
    "marine":        "marine-engineering",
    "structural":    "naval-architecture",
    "misc":          "engineering",            # default sink
}
# Invariant (tested): all values ∈ {"engineering","marine-engineering","naval-architecture"}.
```

### Classifier ranked-output contract (R5)

```
function classify_paper_domain_ranked(title, conference, path) -> (primary, secondary|None):
    # Score each domain by keyword hits in lowercased title.
    # Keywords (frozen):
    #   pipeline:      {"pipeline","pipelines","riser","spool","jumper","flowline"}
    #   VIV:           {"viv","vortex-induced","vortex induced","strake"}
    #   hydrodynamics: {"hydrodynamic","seakeeping","wave","diffraction","radiation","slam","slamming"}
    #   marine:        {"mooring","floater","fpso","spar","semi-submersible","tlp","offshore wind"}
    #   structural:    {"fatigue","fracture","crack","s-n","weld","stress concentration"}
    #   subsea:        {"subsea","manifold","umbilical","wellhead","tree","christmas tree"}
    # Score = count of matched keywords (multi-occurrence counted once per keyword).
    # Tie-break for primary: deterministic alphabetical on domain name.
    # Conference and path are used ONLY when title-score is zero across all domains:
    #   - conference name "OMAE" weakly biases toward marine
    #   - path containing "/pipeline/" weakly biases toward pipeline
    # If still all-zero → primary="misc", secondary=None.
    # secondary = second-highest-scoring domain if score >= max(1, primary_score - 1); else None.
```

### TF-IDF clustering — full determinism contract (R2/R12)

```python
TFIDF_PARAMS = {
    "tokenizer":       "title_ascii_lower_alphanum_v1",   # frozen below
    "stopwords_path":  "scripts/knowledge/data/stopwords_en_v1.txt",  # frozen, version-pinned
    "stopwords_sha":   "<computed at first commit; pinned in code constant>",
    "ngram_range":     (1, 2),                            # unigrams + bigrams
    "min_df":          3,                                 # term must appear in ≥3 titles
    "max_df_ratio":    0.40,                              # drop terms in >40% of titles
    "max_vocab":       2000,                              # cap vocabulary size
    "cluster_count_rule": "ceil(sqrt(N_papers / 5))",     # deterministic per-domain k
    "cluster_count_min": 2,
    "cluster_count_max": 25,
    "tie_break":       "lexical_on_paper_id",             # for top-N selection
    "implementation":  "stdlib_only",                     # no sklearn, no nltk
    "library_pin":     "python>=3.11 (collections.Counter, math.log, re, json)",
    "rng_seed":        20260423,                          # only if any sampling occurs
}

# Tokenizer "title_ascii_lower_alphanum_v1":
#   1. NFKD-normalize, drop non-ASCII.
#   2. Lowercase.
#   3. Split on regex r"[^a-z0-9]+".
#   4. Drop tokens of length < 2.
#   5. Drop tokens in STOPWORDS.
#   6. Emit unigrams; emit consecutive bigrams (joined by "_").

# Clustering algorithm (no sklearn):
#   For each domain bucket of N_d papers:
#     1. Build TF-IDF vectors (sparse dict[token]->float) per paper.
#        - tf = raw count / sum(counts)
#        - idf = log((N_d + 1) / (df + 1)) + 1
#     2. k = clip(ceil(sqrt(N_d / 5)), 2, 25)
#     3. Run greedy farthest-first seeding (initial centroid = highest L2-norm vector;
#        next centroid = paper with maximum min-cosine-distance to existing centroids).
#     4. One pass of cosine-similarity assignment to nearest centroid.
#     5. For each cluster, top-N papers = papers with highest cosine-similarity to centroid;
#        ties broken by lexical paper_id.
#     6. Cluster topic_label = top-3 highest-idf-weighted tokens, joined by " | ".
#   No iterative refinement (no k-means convergence) — single pass for full determinism.
```

This is fully deterministic given a fixed input, requires no external libraries, and runs in `O(N_d × max_vocab)` per domain.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/knowledge/run_batch_pack_2.py | runner: domain classification + topic clustering (underscore filename so tests can import) |
| Create | scripts/knowledge/data/stopwords_en_v1.txt | frozen stop-word list pinned by SHA in code |
| Create | tests/knowledge/test_batch_pack_2.py | TDD coverage (19 tests, see list) |
| Create | docs/reports/batch-pack-2-conference-summary-stubs.md | primary output (topic stubs grouped by domain + wiki target) |
| Create | data/document-index/batch-pack-2-cross-link-candidates.jsonl | input for #2068; schema = Appendix A |
| Create | data/document-index/batch-pack-2-skipped.jsonl | malformed-record sidecar (R6) |
| Update | docs/reports/llm-wiki-external-source-priority-queue.md | one-line footnote at §5.2 (R7) |
| Update | docs/reports/llm-wiki-staged-batch-packs.md | one-line footnote at §3.2 (R7) |
| Update | docs/plans/README.md | add index row for this plan |
| (No modify) | data/document-index/conference-paper-catalog.yaml | plan does NOT rewrite ISOPE status — separate follow-on issue if/when ISOPE is indexed |
| (No modify) | knowledge/wikis/** | read-only guard holds; verified by git diff scope |
| (No modify) | config/**, .claude/**, tests/** other than the new file above |

---

## TDD Test List

| # | Test name | What it verifies | Acceptance criterion |
|---|---|---|---|
| 1 | test_catalog_phase_a_complete_set_is_dot_omae_otc | authoritative phase_a set excludes ISOPE | AC1 |
| 2 | test_phase_a_set_drift_warns_not_crashes | R3: synthetic catalog with ISOPE=phase_a_complete logs WARN, runner continues | AC1 |
| 3 | test_isope_is_deferred_not_processed | ISOPE flagged as deferred with `not_indexed` reason | AC2 |
| 4 | test_phase_a_jsonl_line_count_matches_catalog | classified + skipped == 14180 | AC3 |
| 5 | test_path_guard_rejects_reading_conference_pdf_dir | runner refuses to open under /mnt/ace/docs/conferences/ | AC4 |
| 6 | test_classify_paper_domain_pipeline_wins | "pipeline" → primary=pipeline | AC5 |
| 7 | test_classify_paper_domain_viv | "VIV fatigue in deepwater risers" → primary=VIV, secondary=structural | AC5 |
| 8 | test_classify_returns_secondary_for_cross_domain | "VIV fatigue on pipelines" → primary=pipeline, secondary=VIV (R5) | AC5 |
| 9 | test_classify_paper_domain_default_misc | no keyword hit → primary=misc, secondary=None | AC5 |
| 10 | test_cluster_preserves_paper_count_per_domain | sum(cluster.paper_count) == len(papers_in_domain) | AC3 |
| 11 | test_cluster_top_n_is_deterministic | same input → byte-identical top-N ordering | AC6 |
| 12 | test_tfidf_stopwords_sha_pinned | constant in code matches sha256 of stopwords file (R2/R12) | AC6 |
| 13 | test_build_topic_stub_frontmatter_has_required_keys | stub has `title`,`tags`,`added`,`last_updated` | AC7 |
| 14 | test_build_topic_stub_provenance_is_list_of_paper_ids | each `sources:` resolvable to a phase_a record | AC8 |
| 15 | test_duplicate_check_detects_existing_wiki_page | existing wiki page with matching `sources:` flagged | AC9 |
| 16 | test_cross_link_jsonl_schema | output JSONL conforms to Appendix A | AC10 |
| 17 | test_runner_is_idempotent | re-run yields byte-identical report + JSONL | AC11 |
| 18 | test_domain_to_target_wiki_table_all_allowed | every entry in DOMAIN_TARGET_WIKI maps to allowed set (R4) | AC12 |
| 19 | test_malformed_jsonl_row_is_skipped_not_crashed | malformed row → emitted to skipped.jsonl, run continues (R6/R8) | AC3 |
| 20 | test_missing_phase_a_jsonl_raises_clear_error | absent file → typed exception with path in message (R8) | AC13 |
| 21 | test_unknown_indexing_status_value_warns | catalog with `indexing_status: in_progress` → WARN, treated as deferred (R8) | AC1 |
| 22 | test_empty_cluster_does_not_emit_stub | domain with zero papers produces no stub (R8) | AC3 |
| 23 | test_omae_subslice_perf_budget | OMAE-only run completes in <300s on reference machine (R9) | AC14 |
| 24 | test_upstream_doc_footnote_present | both contradicting docs contain post-edit footnote pointing to new report (R7) | AC15 |

(Total: 24 tests; v1 had 14.)

---

## Acceptance Criteria

| # | Criterion |
|---|---|
| AC1 | `uv run pytest tests/knowledge/test_batch_pack_2.py -v` — all tests pass |
| AC2 | `uv run python scripts/knowledge/run_batch_pack_2.py` exits 0 and produces `docs/reports/batch-pack-2-conference-summary-stubs.md`, `data/document-index/batch-pack-2-cross-link-candidates.jsonl`, `data/document-index/batch-pack-2-skipped.jsonl` |
| AC3 | Output report records **DOT + OMAE + OTC** as processed and **ISOPE** as deferred with reason; `len(classified) + len(skipped) == 14180` |
| AC4 | Runner never reads under `/mnt/ace/docs/conferences/` (test 5) |
| AC5 | Classifier returns `(primary, secondary|None)` per ranked-output contract |
| AC6 | Two consecutive runs produce byte-identical outputs; stop-words SHA matches code constant |
| AC7 | Each stub frontmatter contains `title`, `tags`, `added`, `last_updated` |
| AC8 | Each stub records provenance as a list of phase-a record ids |
| AC9 | Duplicate-check flags overlapping existing wiki pages (does NOT auto-merge) |
| AC10 | Cross-link JSONL conforms to Appendix A schema |
| AC11 | No wiki pages promoted (knowledge/wikis/** read-only — verified by git diff scope); no files under `config/**`, `.claude/**` modified |
| AC12 | Each stub `target_wiki ∈ {engineering, marine-engineering, naval-architecture}`; mapping table in code matches plan §Pseudocode |
| AC13 | ISOPE re-index follow-on issue is filed (or flagged for user to file) and linked from the report |
| AC14 | OMAE sub-slice completes in `<5 min`, full run in `<15 min` on reference machine |
| AC15 | Both contradicting upstream docs (`llm-wiki-external-source-priority-queue.md` §5.2 and `llm-wiki-staged-batch-packs.md` §3.2) carry a footnote pointing to the new report |
| AC16 | Review artifacts for all three providers posted to `scripts/review/results/` |

---

## Adversarial Review Summary

| Provider | v1 Verdict | v2 Verdict |
|---|---|---|
| Claude | MAJOR | PENDING |
| Codex | UNAVAILABLE (#2406) | PENDING |
| Gemini | MINOR | PENDING |

**v1 → v2 revisions:** see Revision Log at top. All v1 P1 items addressed (R1, R2). All v1 P2 items addressed (R3, R4, R5, R6, R12). All v1 P3 items addressed (R7, R8, R9, R10).

---

## Risks and Open Questions

- **Risk (inherited misstatement):** v1 deferred fixing the two upstream docs. v2 includes a one-line footnote on each (R7) — minimal, in-scope, removes the silent-defect trap.
- **Risk (OMAE scale):** OMAE alone has 7,292 titles. Stdlib-only TF-IDF with `max_vocab=2000`, single-pass farthest-first clustering, runs in `O(N × V) ≈ 7292 × 2000 = 1.5e7` ops per domain — fits the `<5 min` budget by orders of magnitude.
- **Risk (classifier precision):** v2 returns ranked `(primary, secondary)` so cross-domain papers (`VIV ∧ pipeline`) preserve secondary signal in stub metadata. Per-cluster confidence still surfaced per #2364 pattern.
- **Risk (PDF read-through):** explicit path guard invariant + failing test 5.
- **Risk (duplicate-check scope):** marine-engineering wiki has 19,191 pages. v2 uses `sources:` frontmatter index (incremental; built once, cached at startup); same approach as #2364.
- **Risk (#2068 schema fork):** v2 inlines schema (Appendix A); when #2068 lands, it will adopt this schema. If #2068 lands FIRST and chooses a different schema, v2 will need a one-issue migration shim. Acceptable trade given current state.
- **Open:** Should the report group stubs first by `target_wiki_domain` or by engineering-topic-domain? Defaults to topic-domain per spec §3.2 step 2.
- **Open:** Auto-filing the ISOPE re-index follow-on vs leaving it to a human. Plan defaults to leaving it to a human (writes a proposed issue body to the report).
- **Open:** Whether `--collections` flag should default to all-three or require explicit set. Plan defaults to all-three for the canonical execution; flag exists for sub-slicing in CI/dev.

---

## Complexity: T2

**T2** — new runner + TDD test module + report + JSONL cross-link artifact + JSONL skipped sidecar + 2 footnote edits to existing docs; zero mods to wiki pages; reads only indexed JSONL/YAML (no PDFs); explicit readiness-mismatch reconciliation is the load-bearing correctness move; stdlib-only TF-IDF with full determinism contract removes the v1 ambiguity.

---

## Appendix A — Cross-Link JSONL Schema (v1, source-of-truth for #2369; #2068 will adopt)

Each line in `data/document-index/batch-pack-2-cross-link-candidates.jsonl` is a JSON object with the following fields:

```json
{
  "stub_id": "bp2-pipeline-001",
  "schema_version": "1.0",
  "source_issue": 2369,
  "title": "Pipeline integrity under sour service",
  "engineering_domain": "pipeline",
  "secondary_domain": "structural",
  "target_wiki": "engineering",
  "target_wiki_path_hint": "concepts/pipeline-integrity.md",
  "paper_count": 47,
  "top_paper_ids": ["DOT-2007-0123", "OMAE-2011-0456", "OTC-2015-0789"],
  "topic_label": "pipeline | sour | corrosion",
  "duplicate_candidate_path": null,
  "cross_link_candidates": [
    {"target_wiki": "marine-engineering", "target_path": "concepts/cathodic-protection.md", "confidence": 0.62},
    {"target_wiki": "engineering",        "target_path": "standards/dnv-os-f101.md",       "confidence": 0.81}
  ],
  "generated_at": "2026-04-24T00:00:00Z",
  "generator": "scripts/knowledge/run_batch_pack_2.py",
  "generator_version": "1.0"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `stub_id` | string | yes | format `bp2-<domain>-<3-digit-zero-padded>`; deterministic per run |
| `schema_version` | string | yes | semver; `1.0` for this issue |
| `source_issue` | int | yes | `2369` |
| `title` | string | yes | stub title |
| `engineering_domain` | enum | yes | one of {`pipeline`,`subsea`,`VIV`,`hydrodynamics`,`marine`,`structural`,`misc`} |
| `secondary_domain` | enum or null | yes | same enum or null |
| `target_wiki` | enum | yes | one of {`engineering`,`marine-engineering`,`naval-architecture`} |
| `target_wiki_path_hint` | string | yes | suggested wiki-relative path; ingestion may override |
| `paper_count` | int | yes | papers in this cluster |
| `top_paper_ids` | list[string] | yes | up to N=10 phase-a record ids; deterministic ordering |
| `topic_label` | string | yes | top-3 idf-weighted tokens, ` \| `-joined |
| `duplicate_candidate_path` | string or null | yes | path to existing wiki page if `sources:` overlap detected |
| `cross_link_candidates` | list[object] | yes | each `{target_wiki, target_path, confidence}`; up to 5 |
| `generated_at` | string | yes | ISO-8601 UTC; timestamp at runner start |
| `generator` | string | yes | this runner path |
| `generator_version` | string | yes | semver of runner; `1.0` at first emit |

Validation: `tests/knowledge/test_batch_pack_2.py::test_cross_link_jsonl_schema` round-trips each line through a `dataclass` parser; any field missing or type-mismatched fails.

#2068 integration note: when #2068 implements the cross-link generator, it consumes this JSONL as input. Schema changes after this issue lands require a `schema_version` bump and a migration note in #2068's plan.
