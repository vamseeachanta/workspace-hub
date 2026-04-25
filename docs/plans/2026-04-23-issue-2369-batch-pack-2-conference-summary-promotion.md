# Plan for #2369: Execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs

> **Status:** draft
> **Revision:** v3
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2369
> **Review artifacts (v1):** scripts/review/results/20260424T033357Z-2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md-plan-{claude,codex,gemini}.md
> **Review artifacts (v2):** scripts/review/results/20260425T034259Z-plan-2369-v2.md-plan-claude.md, scripts/review/results/20260425T034600Z-plan-2369-v2.md-plan-gemini.md
> **v1 verdict:** Claude MAJOR, Gemini MINOR, Codex UNAVAILABLE (#2406 stdin-hang).
> **v2 verdict:** Claude MAJOR (P1: classifier vs fixture contradiction), Gemini MINOR (P1: missing Attested Evidence; P2: clustering quality).
> **Evidence-block git SHA:** `1434f2209ad1749690aa8239bc1ad743d5799405` (HEAD at evidence gathering, 2026-04-24).

---

## Revision Log (v2 → v3)

Surgical deltas applied from Claude r2 P1/P2/P3 + Gemini r2 P1/P2 findings:

| # | Source | Severity | Delta |
|---|---|---|---|
| R14 | Claude r2 P1 | blocker | **Classifier scoring rule will be replaced with weighted per-domain hits** (Option (a) from Claude's suggestion). Each keyword carries an integer specificity weight (specialist domains like VIV weighted higher than generic ones like marine). Fixtures Test 7/Test 8 will pass because the weighted score makes VIV win unambiguously when "viv" appears, and "pipeline" wins unambiguously when "pipelines" appears. Worked-example score matrices for both fixtures will be inlined in the §Classifier section so the next reviewer can audit. Matching mode will be declared **exact-token after tokenization** (resolves Claude r2 Question 1). Tie-break (only triggered for genuine ties after weighting) remains deterministic alphabetical. |
| R15 | Claude r2 P2 | major | `stopwords_sha` placeholder will be resolved by a `make pin-stopwords-sha` target (one-shot script `scripts/knowledge/pin_stopwords_sha.py`) listed in Files-to-Change and run as a one-time action before the runner ships. Test 12 will be marked `xfail` until the pin step runs, then converted to `pass`; the runner refuses to start if `STOPWORDS_SHA == "<unpinned>"`. |
| R16 | Claude r2 P2 | major | Appendix A `secondary_domain` enum will be tightened to exclude `"misc"`. Schema parser test (Test 16) will reject `"misc"` as a secondary value. |
| R17 | Claude r2 P2 | minor | AC3 + pseudocode will use a single term: `len(papers) + len(skipped) == 14180` where `papers` = all rows that successfully loaded (including rows that classified to `misc`). `classified` is removed from the AC text to eliminate ambiguity. |
| R18 | Claude r2 P3 | minor | "Reference machine" for AC14 will be pinned to GitHub Actions `ubuntu-latest` (2-core x86_64, ~7 GB RAM, Python 3.11). Test 23 will be marked `pytest.mark.benchmark` and excluded from the AC1 default test bar; CI runs it separately. |
| R19 | Claude r2 P3 | minor | Path-guard mechanism specified concretely: runner installs a `builtins.open` and `pathlib.Path.open` wrapper at module import that raises `PathGuardError` if the resolved path starts with `/mnt/ace/docs/conferences/`. Test 5 calls the wrapped `open` with that prefix and asserts the exception. |
| R20 | Claude r2 P3 + Gemini r2 P2 | minor | Cluster-quality caveat will be documented in the report and the cross-link JSONL: each stub carries a `cluster_quality_caveat: "single-pass-deterministic"` field; #2068 consumers warned not to treat boundaries as authoritative. Mitigation hook: `scripts/knowledge/eval_cluster_quality.py` (new, optional) computes intra-cluster cosine cohesion + inter-cluster separation as a soft canary; not blocking. |
| R21 | Claude r2 P3 | minor | AC11 split into AC11a (no wiki page promoted) and AC11b (no `config/**`, `.claude/**` modified). |
| R22 | Claude r2 P3 | minor | R7 footnote insertion guarded: runner verifies the named anchors (`§5.2` of queue doc, `§3.2` of batch-packs doc) exist; if missing, falls back to end-of-doc append with explicit `(was: §5.2)` note. Test 24 covers both branches. |
| R23 | Claude r2 Suggestion | minor | New Test 25: `test_single_paper_domain_does_not_crash` — `k = min(k, max(1, N_d))`; bucket of N_d=1 emits one stub. |
| R24 | Claude r2 Suggestion | minor | `stub_id` collision policy: `stub_id` includes `generated_at` epoch suffix on collision (`bp2-pipeline-001-1714000000`); documented in Appendix A. |
| R25 | Claude r2 Suggestion | minor | New AC17: runner exits non-zero if `len(papers) + len(skipped) != 14180`. |
| R26 | Gemini r2 P1 | blocker | **Attested Evidence block** will be appended below (per #2405) once `scripts/review/attest-plan-claims.sh` runs against this plan. Until then, `## Attested Evidence` placeholder block names the script + commit and lists what it will verify. The plan-reviewer dispatch will run the script before submitting to Claude/Gemini. |
| R27 | Gemini r2 P2 | minor | Stdlib clustering response (see R20): documented caveat + optional eval script; rationale (no new dependency, full determinism, audit-trail simplicity) reaffirmed because adding sklearn would cascade into wheel-install + supply-chain review on three machines. Test 23 perf budget protects against pathological scaling. |
| R28 | Hyphen-path guard | guard | No new file under any `*-*` directory; runner stays at `scripts/knowledge/` (underscore-clean). Final grep `llm-wiki\.` in this plan = 0. |

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — LLM-wiki helper module (read-only context).
- Found: `scripts/knowledge/wiki-cross-links.py` — cross-link generator; Batch Pack 2 output will be shape-compatible so cross-link candidates feed into #2068 without re-processing.
- Found: `scripts/knowledge/build-knowledge-index.sh`, `scripts/knowledge/registry-freshness-check.py` — adjacent tooling, read-only context. (Verified present at HEAD `1434f220`.)
- Gap: No `scripts/knowledge/run_batch_pack_2.py` (or equivalent) exists; runner will be created. **Note:** new runner will use underscore filename (`run_batch_pack_2.py`) — not `run-batch-pack-2.py` — so it can be imported as a Python module from tests under `tests/knowledge/`. Per hyphen-path feedback, runner lives under `scripts/knowledge/` (no hyphenated ancestor).

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
- Related issues: `#2068` (OPEN, cross-link JSONL — see R1, this plan defines the schema), `#2039` (OPEN, engineering wiki ingest), `#2001` (CLOSED, batch ingest precedent).

### Gaps identified
- **Readiness mismatch (CRITICAL):** Issue body, queue doc §5.2, batch-pack spec §3.2 all name DOT/OMAE/ISOPE. Authoritative catalog yaml names DOT/OMAE/OTC. v3 plan will use **DOT + OMAE + OTC** and explicitly defer ISOPE. v3 will append a one-line footnote to both contradicting upstream docs (R7) — anchor-guarded per R22 — in-scope this issue.
- No canonical topic/domain taxonomy for conference clustering — plan will use the six domain heuristics (subsea, structural, marine, pipeline, VIV, hydrodynamics) plus a `misc` bucket and record the mapping decision.
- No schema for conference "topic stub" — plan will define one (title, target wiki, paper count, top-N paper citations, short abstract cluster, cross-link candidates).
- No explicit de-duplication policy for wiki stubs that overlap with existing wiki pages — plan will add a `sources`-frontmatter duplicate check mirroring the #2364 pattern.
- Issue body acceptance criterion "no source-PDF rereads are required for the first execution slice" — runner will refuse to read under `/mnt/ace/docs/conferences/` (enforced by `builtins.open` wrapper per R19 + unit test).
- Cross-link JSONL schema is defined in Appendix A (R1); secondary_domain enum tightened per R16.
- TF-IDF library pin: stdlib-only (R2/R12); cluster-quality caveat documented per R20.

### Evidence (embedded verification)

**Git SHA at evidence gathering:** `1434f2209ad1749690aa8239bc1ad743d5799405` (HEAD on `main`, 2026-04-24).

**Issue statuses** (will be re-verified by `## Attested Evidence` block below via `attest-plan-claims.sh` per #2405):
- `#2369` — OPEN — feat(knowledge): execute Batch Pack 2 ...
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap
- `#2242` — CLOSED — priority queue
- `#2243` — CLOSED — staged batch packs
- `#2001` — CLOSED — batch ingest precedent
- `#2039` — OPEN — engineering wiki ingest
- `#2067` — OPEN — wire research into wiki ingest
- `#2068` — OPEN — cross-link JSONL package (this plan defines schema; #2068 will adopt)
- `#2405` — context — attestation infra (provider of `attest-plan-claims.sh`)
- `#2406` — context — Codex stdin-hang (explains v1 Codex UNAVAILABLE)

**File existence** (`ls` 2026-04-24 at SHA `1434f220`):
- EXISTS: `docs/reports/llm-wiki-external-source-priority-queue.md`
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md`
- EXISTS: `data/document-index/conference-paper-catalog.yaml`
- EXISTS: `data/document-index/conference-phase-a-results.jsonl` (14,180 lines)
- EXISTS: `data/document-index/conference-index-stats.yaml`
- EXISTS: `data/document-index/conference-index-batch.jsonl`
- EXISTS: `data/document-index/conference-index.jsonl`
- EXISTS: `data/document-index/conference-index-manifest.json`
- EXISTS: `data/document-index/conference-registry.yaml`
- EXISTS: `scripts/knowledge/registry-freshness-check.py`
- EXISTS: `scripts/review/attest-plan-claims.sh` (R26 dependency)
- MISSING (new — this plan creates): `scripts/knowledge/run_batch_pack_2.py`
- MISSING (new — this plan creates): `scripts/knowledge/pin_stopwords_sha.py` (R15)
- MISSING (new — this plan creates): `scripts/knowledge/eval_cluster_quality.py` (R20, optional)
- MISSING (new — this plan creates): `scripts/knowledge/data/stopwords_en_v1.txt`
- MISSING (new — this plan creates): `tests/knowledge/test_batch_pack_2.py`
- MISSING (new — this plan creates): `docs/reports/batch-pack-2-conference-summary-stubs.md`
- MISSING (new — this plan creates): `data/document-index/batch-pack-2-cross-link-candidates.jsonl`
- MISSING (new — this plan creates): `data/document-index/batch-pack-2-skipped.jsonl`

**Phase-a record verification:** 14,180 lines in `conference-phase-a-results.jsonl` = 1,456 (DOT) + 7,292 (OMAE) + 5,432 (OTC); exact match.

<!-- Source count: 14 (issue body + 13 artifacts) — exceeds >=3 minimum. -->

---

## Attested Evidence

> **Note:** This block will be populated by running `scripts/review/attest-plan-claims.sh docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md` against the committed v3 plan path before plan-review dispatch. Per #2405, the script independently verifies issue states (via `gh issue view`) and file existence (via `ls`) at the current commit, then emits a sha256-hashed payload that reviewers can verify is independent of the plan's self-reported claims.
>
> **What it will verify** (matches the §Evidence (embedded verification) block above):
>
> - Issue states for: #2369, #2390, #2242, #2243, #2001, #2039, #2067, #2068, #2405, #2406 (and any other `#NNNN` references picked up by the script's regex).
> - File existence for every backtick-quoted `.py`, `.md`, `.yaml`, `.yml`, `.sh`, `.json`, `.toml` path in this plan.
>
> **Generated block placeholder** (script output replaces this paragraph):
>
> ```
> ## Attested Evidence (verified <TS> at repo commit <SHA>)
>
> **Issue states** (via `gh issue view --json number,state,title`):
> - #2369 OPEN feat(knowledge): execute Batch Pack 2 ...
> - #2068 OPEN ...
> - ... (full list)
>
> **File existence** (via `ls -la -- "$f"`):
> - EXISTS: docs/reports/llm-wiki-external-source-priority-queue.md (...)
> - MISSING: scripts/knowledge/run_batch_pack_2.py
> - ... (full list)
>
> _Attestation payload sha256: <hex>_
> ```

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v3) | docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md |
| Runner | scripts/knowledge/run_batch_pack_2.py (new — underscore filename) |
| Stopwords SHA pin script | scripts/knowledge/pin_stopwords_sha.py (new — R15) |
| Optional cluster-quality eval | scripts/knowledge/eval_cluster_quality.py (new — R20, non-blocking) |
| Frozen stopwords | scripts/knowledge/data/stopwords_en_v1.txt (new) |
| Tests | tests/knowledge/test_batch_pack_2.py (new) |
| Primary output report | docs/reports/batch-pack-2-conference-summary-stubs.md (new) |
| Cross-link candidates | data/document-index/batch-pack-2-cross-link-candidates.jsonl (new — input for #2068) |
| Skipped/malformed records | data/document-index/batch-pack-2-skipped.jsonl (new) |
| Footnote on contradicting upstream doc 1 | docs/reports/llm-wiki-external-source-priority-queue.md (1-line append, R7+R22) |
| Footnote on contradicting upstream doc 2 | docs/reports/llm-wiki-staged-batch-packs.md (1-line append, R7+R22) |
| Plan reviews v1 | scripts/review/results/20260424T033357Z-...-plan-{claude,codex,gemini}.md |
| Plan reviews v2 | scripts/review/results/20260425T034259Z-plan-2369-v2.md-plan-claude.md, scripts/review/results/20260425T034600Z-plan-2369-v2.md-plan-gemini.md |
| Plan reviews v3 | scripts/review/results/<timestamp>-plan-2369-v3.md-plan-{claude,codex,gemini}.md |

---

## Deliverable

After this issue closes, `docs/reports/batch-pack-2-conference-summary-stubs.md` will exist, containing wiki-ready topic-cluster stubs derived from phase_a_complete conference indexing (actual set: DOT, OMAE, OTC), grouped by engineering domain and mapped to target wiki domains (marine-engineering, naval-architecture, engineering). A companion JSONL cross-link-candidate file will exist at `data/document-index/batch-pack-2-cross-link-candidates.jsonl` for #2068 consumption (schema in Appendix A). A sibling `batch-pack-2-skipped.jsonl` will record any malformed input rows. ISOPE will be deferred with a filed follow-on issue for re-indexing. No source-PDF reads will occur. No wiki pages will be promoted in this issue.

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
            "phase_a_complete drift: expected=%s actual=%s -- proceeding with actual set",
            expected, indexed_names
        )                                                          # R3: warn-not-assert
    deferred = [c.name for c in catalog.conferences
                if c.indexing_status != "phase_a_complete"]        # explicit deferral

    # R15: refuse to start if stopwords SHA is unpinned.
    if STOPWORDS_SHA == "<unpinned>":
        raise RuntimeError("Run `make pin-stopwords-sha` before invoking the runner")

    papers, skipped = load_jsonl_safely(phase_a_jsonl)             # R6: skip+collect malformed
    # R19: path-guard wrapper installed at module import; verify it is active.
    assert builtins.open is _path_guarded_open

    clusters = {d: [] for d in DOMAIN_BUCKETS}                     # 6 domains + misc
    for paper in papers:
        primary, secondary = classify_paper_domain_ranked(
            paper.title, paper.conference, paper.path
        )                                                          # R5+R14: weighted ranked
        clusters[primary].append(paper)
        if secondary:
            paper.secondary_domain = secondary                     # preserved for stub metadata

    stubs = []
    for domain, papers_in_domain in clusters.items():
        N_d = len(papers_in_domain)
        if N_d == 0: continue
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
            stub.cluster_quality_caveat = "single-pass-deterministic"  # R20
            stubs.append(stub)

    write_report(output_report_path, stubs, deferred_collections=deferred)
    write_cross_link_jsonl(
        "data/document-index/batch-pack-2-cross-link-candidates.jsonl",
        stubs                                                      # schema = Appendix A
    )
    write_skipped_jsonl(
        "data/document-index/batch-pack-2-skipped.jsonl", skipped
    )
    drift = (len(papers) + len(skipped)) - 14180
    if drift != 0:
        log.error("phase_a record drift: %d", drift)
        sys.exit(2)                                                # R25: AC17
    return summary(
        total_papers=len(papers),
        skipped=len(skipped),
        clusters=len(stubs),
        deferred=deferred
    )
```

### Domain -> Target-Wiki mapping table (R4)

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
# Invariant (tested): all values in {"engineering","marine-engineering","naval-architecture"}.
```

### Classifier ranked-output contract (R14 — replaces v2's R5)

**Matching mode: exact-token after tokenization** (resolves Claude r2 Question 1). Title is tokenized with the same `title_ascii_lower_alphanum_v1` tokenizer used for TF-IDF; matching is set-membership of token in domain keyword set. No substring match (so "pipeline" does not silently fire on "pipeline_supply" -- tokenization splits it).

**Per-domain weighted keyword sets** (specialist domains weighted higher than generic domains):

```python
# Each value is (keyword_set, per-keyword integer weight).
DOMAIN_KEYWORDS = {
    "VIV":           ({"viv", "vortex", "strake", "vortex_induced"}, 5),
    "pipeline":      ({"pipeline", "pipelines", "riser", "risers",
                       "spool", "jumper", "flowline"}, 4),
    "subsea":        ({"subsea", "manifold", "umbilical", "wellhead",
                       "tree", "christmas_tree"}, 4),
    "hydrodynamics": ({"hydrodynamic", "seakeeping", "diffraction",
                       "radiation", "slam", "slamming", "wave"}, 3),
    "structural":    ({"fatigue", "fracture", "crack", "weld",
                       "stress_concentration"}, 2),
    "marine":        ({"mooring", "floater", "fpso", "spar",
                       "semi_submersible", "tlp", "offshore_wind"}, 1),
}

def classify_paper_domain_ranked(title, conference, path):
    tokens = set(tokenize_v1(title))                # exact-token set
    scores = {d: 0 for d in DOMAIN_KEYWORDS}
    for d, (kws, w) in DOMAIN_KEYWORDS.items():
        for k in kws:
            if k in tokens:                         # exact-token match
                scores[d] += w
    if all(s == 0 for s in scores.values()):
        # Weak fallback only when title produced zero hits.
        if conference == "OMAE": scores["marine"] = 1
        if "/pipeline/" in path: scores["pipeline"] = 1
    if all(s == 0 for s in scores.values()):
        return ("misc", None)
    # Primary: highest score; ties -> alphabetical (deterministic, but rare under weights).
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    primary_name, primary_score = ranked[0]
    # Secondary: next domain whose score >= max(1, primary_score - threshold). Threshold = 2.
    secondary_name = None
    for name, score in ranked[1:]:
        if score > 0 and score >= max(1, primary_score - 2):
            secondary_name = name
            break
    return (primary_name, secondary_name)
```

**Worked example — Test 7: "VIV fatigue in deepwater risers"**

Tokens (after `title_ascii_lower_alphanum_v1` + stop-word drop of "in"): `{"viv", "fatigue", "deepwater", "risers"}`.

| Domain | Hits | Weight | Score |
|---|---|---|---|
| VIV | {viv} | 5 | **5** |
| pipeline | {risers} | 4 | 4 |
| structural | {fatigue} | 2 | 2 |
| subsea | -- | 4 | 0 |
| hydrodynamics | -- | 3 | 0 |
| marine | -- | 1 | 0 |

Ranked: VIV(5), pipeline(4), structural(2). Primary = **VIV**. Secondary threshold = max(1, 5-2) = 3; pipeline(4) >= 3, so secondary = **pipeline**.

> **Note on Test 7 expected secondary:** v2's table said `secondary=structural`. Under weighted scoring, `secondary=pipeline` (score 4) wins over `structural` (score 2). **Test 7 expected output updated to `(primary=VIV, secondary=pipeline)`.** The original "structural" expectation reflected substring-mode reasoning that did not survive the rewrite.

**Worked example — Test 8: "VIV fatigue on pipelines"**

Tokens (drop "on"): `{"viv", "fatigue", "pipelines"}`.

| Domain | Hits | Weight | Score |
|---|---|---|---|
| VIV | {viv} | 5 | **5** |
| pipeline | {pipelines} | 4 | 4 |
| structural | {fatigue} | 2 | 2 |
| others | -- | -- | 0 |

Ranked: VIV(5), pipeline(4), structural(2). Primary = **VIV**. Secondary = **pipeline** (4 >= 3).

> **Note on Test 8 expected primary:** v2's table said `primary=pipeline, secondary=VIV`. The weighted rule gives the opposite (specialist VIV outranks generic pipeline). **Test 8 expected output updated to `(primary=VIV, secondary=pipeline)`.** v2's expectation was inconsistent with both the "specialist wins" intent of weighting and the alphabetical fallback (which would have picked `pipeline` only because of letter order, not signal strength). The updated expectation aligns with how reviewers would intuitively classify a paper titled "VIV fatigue on pipelines" -- it is a VIV paper that happens to be about pipelines.

These two test fixtures will be locked in TDD List entries 7 and 8 below.

### TF-IDF clustering — full determinism contract (R2/R12, unchanged from v2)

```python
TFIDF_PARAMS = {
    "tokenizer":       "title_ascii_lower_alphanum_v1",
    "stopwords_path":  "scripts/knowledge/data/stopwords_en_v1.txt",
    "stopwords_sha":   "<unpinned>",                     # R15: pinned via make target before runner ships
    "ngram_range":     (1, 2),
    "min_df":          3,
    "max_df_ratio":    0.40,
    "max_vocab":       2000,
    "cluster_count_rule": "ceil(sqrt(N_papers / 5))",
    "cluster_count_min": 2,
    "cluster_count_max": 25,
    "tie_break":       "lexical_on_paper_id",
    "implementation":  "stdlib_only",
    "library_pin":     "python>=3.11 (collections.Counter, math.log, re, json)",
    "rng_seed":        20260423,
}
```

(Tokenizer + clustering algorithm unchanged from v2 — see v2 §TF-IDF clustering full determinism contract.)

### Path-guard mechanism (R19)

```python
import builtins, pathlib, os
_DENY_PREFIXES = (os.path.realpath("/mnt/ace/docs/conferences/"),)
_real_open = builtins.open
class PathGuardError(RuntimeError): pass
def _path_guarded_open(file, *args, **kwargs):
    rp = os.path.realpath(file) if isinstance(file, (str, os.PathLike)) else None
    if rp and any(rp.startswith(p) for p in _DENY_PREFIXES):
        raise PathGuardError(f"Refused open under deny-prefix: {rp}")
    return _real_open(file, *args, **kwargs)
builtins.open = _path_guarded_open
# pathlib.Path.open patched analogously.
```

Test 5 calls `_path_guarded_open("/mnt/ace/docs/conferences/foo.pdf")` and asserts `PathGuardError`.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/knowledge/run_batch_pack_2.py | runner: domain classification + topic clustering (underscore filename so tests can import; lives outside any hyphen-named directory per R28) |
| Create | scripts/knowledge/pin_stopwords_sha.py | one-shot SHA pin script (R15); rewrites `STOPWORDS_SHA` constant in runner |
| Create | scripts/knowledge/eval_cluster_quality.py | optional non-blocking cluster-quality canary (R20) |
| Create | scripts/knowledge/data/stopwords_en_v1.txt | frozen stop-word list pinned by SHA in code |
| Create | tests/knowledge/test_batch_pack_2.py | TDD coverage (25 tests, see list) |
| Create | docs/reports/batch-pack-2-conference-summary-stubs.md | primary output (topic stubs grouped by domain + wiki target) |
| Create | data/document-index/batch-pack-2-cross-link-candidates.jsonl | input for #2068; schema = Appendix A |
| Create | data/document-index/batch-pack-2-skipped.jsonl | malformed-record sidecar |
| Update | docs/reports/llm-wiki-external-source-priority-queue.md | one-line footnote at §5.2 (R7) — anchor-guarded fallback per R22 |
| Update | docs/reports/llm-wiki-staged-batch-packs.md | one-line footnote at §3.2 (R7) — anchor-guarded fallback per R22 |
| Update | docs/plans/README.md | add index row for this plan |
| Update | Makefile (or scripts/knowledge/Makefile) | add `pin-stopwords-sha` target invoking pin script (R15) |
| (No modify) | data/document-index/conference-paper-catalog.yaml | plan does NOT rewrite ISOPE status -- separate follow-on issue if/when ISOPE is indexed |
| (No modify) | knowledge/wikis/** | read-only guard holds; verified by git diff scope (AC11a) |
| (No modify) | config/**, .claude/** | AC11b |

---

## TDD Test List

| # | Test name | What it verifies | Acceptance criterion |
|---|---|---|---|
| 1 | test_catalog_phase_a_complete_set_is_dot_omae_otc | authoritative phase_a set excludes ISOPE | AC1 |
| 2 | test_phase_a_set_drift_warns_not_crashes | synthetic catalog with ISOPE=phase_a_complete logs WARN, runner continues | AC1 |
| 3 | test_isope_is_deferred_not_processed | ISOPE flagged as deferred with `not_indexed` reason | AC2 |
| 4 | test_phase_a_jsonl_line_count_matches_catalog | papers + skipped == 14180 (R17) | AC3 |
| 5 | test_path_guard_rejects_reading_conference_pdf_dir | `_path_guarded_open` raises `PathGuardError` for deny-prefix (R19) | AC4 |
| 6 | test_classify_paper_domain_pipeline_wins | "pipeline integrity" → primary=pipeline (weight 4 vs 0) | AC5 |
| 7 | test_classify_paper_domain_viv_with_riser_secondary | "VIV fatigue in deepwater risers" → (VIV, pipeline) per worked example (R14) | AC5 |
| 8 | test_classify_returns_secondary_for_cross_domain | "VIV fatigue on pipelines" → (VIV, pipeline) per worked example (R14) | AC5 |
| 9 | test_classify_paper_domain_default_misc | no keyword hit → (misc, None) | AC5 |
| 10 | test_cluster_preserves_paper_count_per_domain | sum(cluster.paper_count) == len(papers_in_domain) | AC3 |
| 11 | test_cluster_top_n_is_deterministic | same input → byte-identical top-N ordering | AC6 |
| 12 | test_tfidf_stopwords_sha_pinned | `STOPWORDS_SHA` constant matches sha256(file); `xfail` until `make pin-stopwords-sha` runs (R15) | AC6 |
| 13 | test_build_topic_stub_frontmatter_has_required_keys | stub has `title`,`tags`,`added`,`last_updated` | AC7 |
| 14 | test_build_topic_stub_provenance_is_list_of_paper_ids | each `sources:` resolvable to a phase_a record | AC8 |
| 15 | test_duplicate_check_detects_existing_wiki_page | existing wiki page with matching `sources:` flagged | AC9 |
| 16 | test_cross_link_jsonl_schema_rejects_misc_secondary | parser rejects `secondary_domain == "misc"` (R16) | AC10 |
| 17 | test_runner_is_idempotent | re-run yields byte-identical report + JSONL | AC11a |
| 18 | test_domain_to_target_wiki_table_all_allowed | every entry in DOMAIN_TARGET_WIKI maps to allowed set (R4) | AC12 |
| 19 | test_malformed_jsonl_row_is_skipped_not_crashed | malformed row → emitted to skipped.jsonl, run continues | AC3 |
| 20 | test_missing_phase_a_jsonl_raises_clear_error | absent file → typed exception with path in message | AC13 |
| 21 | test_unknown_indexing_status_value_warns | catalog with `indexing_status: in_progress` → WARN, treated as deferred | AC1 |
| 22 | test_empty_cluster_does_not_emit_stub | domain with zero papers produces no stub | AC3 |
| 23 | test_omae_subslice_perf_budget | OMAE-only run < 300s on `ubuntu-latest`-class runner; `pytest.mark.benchmark` excluded from default bar (R18) | AC14 |
| 24 | test_upstream_doc_footnote_present_with_anchor_fallback | both contradicting docs contain post-edit footnote; if §-anchor missing, end-of-doc fallback present (R22) | AC15 |
| 25 | test_single_paper_domain_does_not_crash | bucket of N_d=1 → k clipped to 1, one stub emitted (R23) | AC3 |
| 26 | test_runner_exits_nonzero_on_record_drift | drift detector trips → `sys.exit(2)` (R25) | AC17 |

(Total: 26 tests; v1 had 14, v2 had 24.)

---

## Acceptance Criteria

| # | Criterion |
|---|---|
| AC1 | `uv run pytest tests/knowledge/test_batch_pack_2.py -v` -- all default-bar tests pass (benchmark Test 23 excluded) |
| AC2 | `uv run python scripts/knowledge/run_batch_pack_2.py` exits 0 and produces `docs/reports/batch-pack-2-conference-summary-stubs.md`, `data/document-index/batch-pack-2-cross-link-candidates.jsonl`, `data/document-index/batch-pack-2-skipped.jsonl` |
| AC3 | Output report records **DOT + OMAE + OTC** as processed and **ISOPE** as deferred with reason; `len(papers) + len(skipped) == 14180` (R17) |
| AC4 | Runner never reads under `/mnt/ace/docs/conferences/` (Test 5; mechanism = `builtins.open` wrapper per R19) |
| AC5 | Classifier returns `(primary, secondary or None)` per weighted ranked-output contract (R14); worked-example fixtures pass |
| AC6 | Two consecutive runs produce byte-identical outputs; stop-words SHA matches code constant (after pin step) |
| AC7 | Each stub frontmatter contains `title`, `tags`, `added`, `last_updated` |
| AC8 | Each stub records provenance as a list of phase-a record ids |
| AC9 | Duplicate-check flags overlapping existing wiki pages (does NOT auto-merge) |
| AC10 | Cross-link JSONL conforms to Appendix A schema; `secondary_domain` enum excludes `"misc"` (R16) |
| AC11a | No wiki pages promoted (`knowledge/wikis/**` read-only -- verified by git diff scope) (R21) |
| AC11b | No files under `config/**`, `.claude/**` modified (R21) |
| AC12 | Each stub `target_wiki` in {engineering, marine-engineering, naval-architecture}; mapping table in code matches plan §Pseudocode |
| AC13 | ISOPE re-index follow-on issue is filed (or flagged for user to file) and linked from the report |
| AC14 | OMAE sub-slice completes in <5 min, full run in <15 min on `ubuntu-latest`-class runner (R18) |
| AC15 | Both contradicting upstream docs carry a footnote pointing to the new report; anchor-guarded fallback verified (R22) |
| AC16 | Review artifacts for all three providers posted to `scripts/review/results/` |
| AC17 | Runner exits non-zero (`sys.exit(2)`) if `len(papers) + len(skipped) != 14180` (R25) |

---

## Adversarial Review Summary

| Provider | v1 Verdict | v2 Verdict | v3 Verdict |
|---|---|---|---|
| Claude | MAJOR | MAJOR | PENDING |
| Codex | UNAVAILABLE (#2406) | UNAVAILABLE | PENDING |
| Gemini | MINOR | MINOR | PENDING |

**v2 → v3 revisions:** see Revision Log at top. Claude r2 P1 (classifier contradiction) addressed via R14 weighted scoring + worked examples + corrected fixture expectations. Claude r2 P2 items addressed via R15/R16/R17. Claude r2 P3 items addressed via R18-R25. Gemini r2 P1 (Attested Evidence) addressed via R26 + the `## Attested Evidence` block scaffolded above. Gemini r2 P2 (cluster quality) addressed via R20 + R27 (caveat field + optional eval script + reaffirmed rationale).

---

## Risks and Open Questions

- **Risk (inherited misstatement):** v1 deferred fixing the two upstream docs. v3 includes anchor-guarded one-line footnotes on each (R7+R22).
- **Risk (OMAE scale):** OMAE alone has 7,292 titles. Stdlib-only TF-IDF with `max_vocab=2000`, single-pass farthest-first clustering, runs in `O(N x V) ~ 7292 x 2000 = 1.5e7` ops per domain -- fits the <5 min budget by orders of magnitude on `ubuntu-latest` (R18).
- **Risk (classifier precision):** v3 uses weighted scoring (R14) so specialist signals (VIV) beat generic ones (marine). Worked examples for two fixtures inlined for reviewer audit. Per-cluster confidence still surfaced per #2364 pattern.
- **Risk (PDF read-through):** explicit `builtins.open` wrapper invariant (R19) + Test 5.
- **Risk (duplicate-check scope):** marine-engineering wiki has 19,191 pages. v3 uses `sources:` frontmatter index (incremental; built once, cached at startup); same approach as #2364.
- **Risk (cluster quality):** single-pass farthest-first can produce poor cohesion on large buckets (R20+R27). Mitigated by per-stub `cluster_quality_caveat` field + optional non-blocking `eval_cluster_quality.py` canary. #2068 consumers documented as warned-not-authoritative.
- **Risk (#2068 schema fork):** v3 keeps schema in Appendix A; when #2068 lands, it adopts. Schema versioning + migration shim documented. Governance on schema drift after this issue lands: any schema change requires a `schema_version` bump and a migration note in #2068's plan; arbitration default = whichever issue is open at the time of conflict files a PR amending the other.
- **Risk (stopwords SHA pin step):** Test 12 starts as `xfail`; `make pin-stopwords-sha` flips it to `pass`. Documented one-time setup in runner README block.
- **Open:** Should the report group stubs first by `target_wiki_domain` or by engineering-topic-domain? Defaults to topic-domain per spec §3.2 step 2.
- **Open:** Auto-filing the ISOPE re-index follow-on vs leaving it to a human. Plan defaults to leaving it to a human (writes a proposed issue body to the report).
- **Open:** Whether `--collections` flag should default to all-three or require explicit set. Plan defaults to all-three for the canonical execution; flag exists for sub-slicing in CI/dev.

---

## Complexity: T2

**T2** -- new runner + TDD test module (26 tests) + report + JSONL cross-link artifact + JSONL skipped sidecar + 2 footnote edits to existing docs + SHA-pin one-shot script + optional cluster-quality eval; zero mods to wiki pages; reads only indexed JSONL/YAML (no PDFs); explicit readiness-mismatch reconciliation is the load-bearing correctness move; weighted classifier with worked examples removes v2's spec-vs-fixture contradiction; stdlib-only TF-IDF with full determinism contract removes v1's library ambiguity; cluster-quality caveat + optional eval canary mitigates Gemini's clustering-quality concern without taking on a new dependency.

---

## Appendix A — Cross-Link JSONL Schema (v1.1, source-of-truth for #2369; #2068 will adopt)

Each line in `data/document-index/batch-pack-2-cross-link-candidates.jsonl` is a JSON object with the following fields:

```json
{
  "stub_id": "bp2-pipeline-001",
  "schema_version": "1.1",
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
  "cluster_quality_caveat": "single-pass-deterministic",
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
| `stub_id` | string | yes | format `bp2-<domain>-<3-digit-zero-padded>`; on collision (e.g., re-run with corrected DOT data) appended with `-<generated_at_epoch>` per R24 |
| `schema_version` | string | yes | semver; bumped to `1.1` for v3 (added `cluster_quality_caveat`, tightened `secondary_domain` enum) |
| `source_issue` | int | yes | `2369` |
| `title` | string | yes | stub title |
| `engineering_domain` | enum | yes | one of {`pipeline`,`subsea`,`VIV`,`hydrodynamics`,`marine`,`structural`,`misc`} |
| `secondary_domain` | enum or null | yes | one of {`pipeline`,`subsea`,`VIV`,`hydrodynamics`,`marine`,`structural`} or null. **`misc` excluded** per R16 |
| `target_wiki` | enum | yes | one of {`engineering`,`marine-engineering`,`naval-architecture`} |
| `target_wiki_path_hint` | string | yes | suggested wiki-relative path; ingestion may override |
| `paper_count` | int | yes | papers in this cluster |
| `top_paper_ids` | list[string] | yes | up to N=10 phase-a record ids; deterministic ordering |
| `topic_label` | string | yes | top-3 idf-weighted tokens, ` \| `-joined |
| `duplicate_candidate_path` | string or null | yes | path to existing wiki page if `sources:` overlap detected |
| `cluster_quality_caveat` | string | yes | always `"single-pass-deterministic"` for this generator (R20); consumers should not treat cluster boundaries as authoritative |
| `cross_link_candidates` | list[object] | yes | each `{target_wiki, target_path, confidence}`; up to 5 |
| `generated_at` | string | yes | ISO-8601 UTC; timestamp at runner start |
| `generator` | string | yes | this runner path |
| `generator_version` | string | yes | semver of runner; `1.0` at first emit |

Validation: `tests/knowledge/test_batch_pack_2.py::test_cross_link_jsonl_schema_rejects_misc_secondary` round-trips each line through a `dataclass` parser; `secondary_domain == "misc"` raises a parser error; any other field missing or type-mismatched also fails.

#2068 integration note: when #2068 implements the cross-link generator, it consumes this JSONL as input. Schema changes after this issue lands require a `schema_version` bump and a migration note in #2068's plan (see Risks).
