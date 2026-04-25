# Plan for #2369: Execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs

> **Status:** draft
> **Revision:** v4
> **Complexity:** T2
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2369
> **Review artifacts (v1):** scripts/review/results/20260424T033357Z-2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md-plan-{claude,codex,gemini}.md
> **Review artifacts (v2):** scripts/review/results/20260425T034259Z-plan-2369-v2.md-plan-claude.md, scripts/review/results/20260425T034600Z-plan-2369-v2.md-plan-gemini.md
> **Review artifacts (v3):** scripts/review/results/20260425T041318Z-plan-2369-v3.md-plan-claude.md, scripts/review/results/20260425T041539Z-plan-2369-v3.md-plan-gemini.md
> **v1 verdict:** Claude MAJOR, Gemini MINOR, Codex UNAVAILABLE (#2406 stdin-hang).
> **v2 verdict:** Claude MAJOR (P1: classifier vs fixture contradiction), Gemini MINOR (P1: missing Attested Evidence; P2: clustering quality).
> **v3 verdict (CROSS-PROVIDER CONVERGED):** Claude MAJOR + Gemini MAJOR — **same** P1: `## Attested Evidence` block was a placeholder, not a populated payload (this is exactly the gap Gemini r2 P1 had already flagged). Plus Claude r3 P1 (idempotency vs `generated_at` contradiction), Gemini r3 P2 (3rd-domain silent-discard on secondary-domain ties), and additional Claude P2/P3 items.
> **Evidence-block git SHA:** `3e0e7c2b5cc28c6e8aa0e446f6595276fb449afa` (HEAD on `main`, 2026-04-25, at v4 evidence gathering).

---

## Revision Log (v3 → v4)

Cross-provider convergence on the same P1 across two consecutive revisions is treated as high-signal per `feedback_cross_provider_review_payoff`: the v4 fix is a **populated attestation payload at draft time**, not a "will run before plan-review dispatch" promise. Surgical deltas:

| # | Source | Severity | Delta |
|---|---|---|---|
| R29 | **Claude r3 P1 + Gemini r3 P1 (CONVERGED)** | blocker | **`## Attested Evidence` block will contain the real `attest-plan-claims.sh` output captured at draft time.** v4 captures the actual issue-state JSON snapshots (via `gh issue view --json number,state,title`), the actual file-existence ls output, and the actual sha256 payload digest. Block is self-contained verifiable evidence at the moment v4 ships, not a scaffold. The exact procedure used to produce it — the script invocation and its captured stdout — is documented inline in the §Attested Evidence Procedure subsection so reviewers can re-run and compare. |
| R30 | **Claude r3 P1 (idempotency vs `generated_at`)** | blocker | **Resolved via option (i): inject `--now` seam.** The runner accepts a `--now ISO-8601` flag (env-var `BP2_NOW` as fallback). Default at runtime: ISO-8601 UTC at runner start. In tests (Test 17), `--now 2026-01-01T00:00:00Z` is passed; both runs use the same fixed timestamp; AC6 then becomes a true byte-identical test. The same seam also pins the R24 `generated_at_epoch` collision suffix so `stub_id` is also deterministic in tests. Why option (i) over (ii) "strip field for compare" or (iii) "move to sidecar": (a) downstream #2068 consumers explicitly want `generated_at` in the primary payload as part of cross-link provenance — moving to sidecar adds a join step; (b) "strip-and-compare" pushes idempotency verification into the test harness rather than the contract, making it easier for a future change to silently break determinism without the test catching it; (c) the `--now` seam is the same pattern already used elsewhere in the repo for reproducible-build determinism (see `SOURCE_DATE_EPOCH` handling in `scripts/review/attest-plan-claims.sh` itself), keeping the convention consistent. |
| R31 | **Gemini r3 P2 (3rd-domain silent-discard on ties)** | major | **Resolved by returning ALL tied secondary domains (list), not just the first match.** v3's `for name, score in ranked[1:]: ... break` discarded any 3rd domain that tied with the 2nd. v4 changes the secondary-domain selection to collect every domain whose `score >= max(1, primary_score - 2)` (the same threshold) AND `score > 0`. Return type changes from `(primary, secondary or None)` to `(primary, secondary_domains: list[str])` — `[]` when no qualifier passes the threshold. Why "return all" over "explicit-discard with tie_break_log": for a cross-link feed (#2068), preserving tied domains gives downstream consumers more candidate connections to score themselves; suppressing them at this layer would silently throw away signal that #2068 is built to weigh. A `tie_break_log` would be useful only if downstream needed to know which domains were dropped — they don't, because nothing is dropped. Schema field renamed `secondary_domain` → `secondary_domains` (list) with `schema_version` bumped to `1.2`. Empty list `[]` (not `null`) when no secondary qualifies, simplifying parser invariants. |
| R32 | **Claude r3 P1 (`builtins.open` monkey-patch blast radius)** | major | **Replaced global `builtins.open` patch with a scoped `safe_open(path, mode=...)` helper.** Every read site in the runner uses `safe_open()`; the helper checks `os.path.realpath(path)` against the deny-list and raises `PathGuardError` before opening. CI grep enforces no other open functions are imported into the runner module: `grep -E "^(from |import ).*\b(open|Path)\b" scripts/knowledge/run_batch_pack_2.py` whitelists only the helper itself + `pathlib.Path` (Path objects are read via `safe_open(path, ...)` — `Path.open()` is not called). Test 5 asserts `safe_open` raises on deny-prefix; new Test 5b grep-asserts the runner module imports zero raw `open` references. Pathlib `Path.open` and low-level `os.open` are no longer in scope: any agent introducing them flunks the CI grep. |
| R33 | **Claude r3 P2 (AC2/pin sequencing)** | minor | **Runbook now sequences the pin step explicitly as a hard prerequisite of AC2.** New Runbook subsection ordered: (1) `make pin-stopwords-sha`, (2) verify Test 12 transitions xfail→pass, (3) AC2 becomes runnable. Reading AC order without the runbook still surfaces the dependency because AC2 now reads "after `make pin-stopwords-sha` has run, `uv run python scripts/knowledge/run_batch_pack_2.py` exits 0". |
| R34 | **Claude r3 P2 (Tests 7/8 fixture-deltas callout)** | minor | **New "Fixture deltas vs v2" callout** in the §Classifier section lists every test whose expected output changed in v3 (Tests 7 and 8), with a one-line rationale per row. Reviewers no longer have to scroll the worked examples to find what was rotated. |
| R35 | **Claude r3 P2 (AC13 non-determinism)** | minor | **AC13 locked to single branch:** "runner emits a proposed issue body to the report under `## ISOPE re-index follow-on (proposed body)`; user files it manually." Auto-filing branch removed. AC13 satisfied iff the named header exists in the report and the body below it parses as a non-empty markdown block. |
| R36 | **Claude r3 P3 (riser → pipeline rationale)** | minor | **One-line rationale appended to DOMAIN_KEYWORDS pipeline entry:** risers map to `pipeline` (not `subsea`) because the corpus convention treats riser-as-pipe (mechanical/integrity) papers as pipeline; risers-as-VIV-host papers fire `viv` keyword and primary becomes VIV; risers-as-mooring or floater-attached papers fire `mooring`/`floater` and primary becomes marine. Test 6.5 added: `test_classify_riser_only_title_lands_in_pipeline` ("Riser analysis" → primary=pipeline, secondary=[]) — pins the call. |
| R37 | **Claude r3 P3 (cluster_count_min vs N_d=1 precedence)** | minor | **Explicit precedence note added to TFIDF_PARAMS:** "When `N_d == 1`, `k = max(1, min(N_d, ceil(sqrt(N_d/5))))` clips to 1; `cluster_count_min: 2` does NOT override this — N_d-clip wins." Added as a comment line in the dict definition and as a note on Test 25. |
| R38 | **Claude r3 P3 (R28 grep narrow scope)** | minor | **Explicit note added to R28:** the grep guard checks the dotted-module form `llm-wiki\.` only (which is the pattern that bites Python imports per the hyphen-path feedback). Filesystem paths like `llm-wiki/` and `llm-wiki-` are intentionally untouched — they refer to the existing directory and require a full repo migration to rename, which is out of scope. A future agent should NOT "fix" these. |
| R39 | **Claude r3 P3 (generator_version vs schema_version)** | minor | **Note added to Appendix A:** runner versioning is decoupled from schema versioning. `schema_version: 1.2` describes the JSONL contract (bumped this revision for `secondary_domains` list). `generator_version: 1.0` describes the runner module's own semver (first emit). Future runner bug-fixes bump generator_version; future schema changes bump schema_version. Both bumps may co-occur but neither is implied by the other. |
| R40 | **Claude r3 (path-guard verification on Python 3.11/3.12)** | minor | **Test 5c added:** `test_safe_open_rejects_pathlib_path_objects` — passes a `pathlib.Path("/mnt/ace/docs/conferences/foo.pdf")` to `safe_open()` and asserts `PathGuardError`. `safe_open()` accepts `str | os.PathLike` and resolves both via `os.path.realpath()`. Test runs on the project's pinned 3.11; documented as also applicable to 3.12 (no behavior change in `os.path.realpath` between minor versions). |
| R41 | **Claude r3 P3 (STOPWORDS_SHA pin at plan-write time)** | minor | **Choice deferred but justified:** v4 keeps the runtime-pin approach (Test 12 starts as `xfail`). Computing the SHA at plan-write time would embed a literal that becomes stale the moment the stopwords file is touched without a follow-up plan revision; pinning at runtime keeps the drift detection live. The xfail→pass window is narrow (~one `make` invocation) and the runner's hard-refusal-on-unpinned guard means there is no silent-failure window. |
| R42 | **R28 hyphen-path reaffirm** | guard | No new file under any `*-*` directory; runner stays at `scripts/knowledge/` (underscore-clean). v4 final grep for the dotted-import smell pattern (hyphen-segment followed by dot) in this plan = 0. v4 also re-verified that no Python dotted reference of the form "from <X>.<hyphen-dir>.<Y>", `importlib.import_module` invocations targeting hyphen-dir packages, or `pytest -p` plugin paths spanning hyphen-dir ancestors appear anywhere in pseudocode or runbook. |

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — LLM-wiki helper module (read-only context).
- Found: `scripts/knowledge/wiki-cross-links.py` — cross-link generator; Batch Pack 2 output will be shape-compatible so cross-link candidates feed into #2068 without re-processing.
- Found: `scripts/knowledge/build-knowledge-index.sh`, `scripts/knowledge/registry-freshness-check.py` — adjacent tooling, read-only context.
- Gap: No `scripts/knowledge/run_batch_pack_2.py` (or equivalent) exists; runner will be created. New runner uses underscore filename (`run_batch_pack_2.py`) so it can be imported as a Python module from tests under `tests/knowledge/`. Per hyphen-path feedback, runner lives under `scripts/knowledge/` (no hyphenated ancestor).

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
- **Readiness mismatch (CRITICAL):** Issue body, queue doc §5.2, batch-pack spec §3.2 all name DOT/OMAE/ISOPE. Authoritative catalog yaml names DOT/OMAE/OTC. v4 plan will use **DOT + OMAE + OTC** and explicitly defer ISOPE. v4 will append a one-line footnote to both contradicting upstream docs (R7) — anchor-guarded per R22 — in-scope this issue.
- No canonical topic/domain taxonomy for conference clustering — plan will use the six domain heuristics (subsea, structural, marine, pipeline, VIV, hydrodynamics) plus a `misc` bucket and record the mapping decision.
- No schema for conference "topic stub" — plan will define one (title, target wiki, paper count, top-N paper citations, short abstract cluster, cross-link candidates).
- No explicit de-duplication policy for wiki stubs that overlap with existing wiki pages — plan will add a `sources`-frontmatter duplicate check mirroring the #2364 pattern.
- Issue body acceptance criterion "no source-PDF rereads are required for the first execution slice" — runner will refuse to read under `/mnt/ace/docs/conferences/` (enforced by scoped `safe_open()` helper per R32 + unit test).
- Cross-link JSONL schema defined in Appendix A; `secondary_domains` is now a list per R31; `schema_version` bumped to `1.2`.
- TF-IDF library pin: stdlib-only; cluster-quality caveat documented per R20.

### Evidence (embedded verification)

**Git SHA at evidence gathering:** `3e0e7c2b5cc28c6e8aa0e446f6595276fb449afa` (HEAD on `main`, 2026-04-25).
**v3 plan source:** `origin/plan/issue-2369-batch-pack-2:docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md` at branch tip `12cc1ac65b5010511ebdeeedee2968325daea54e`. v3 content sha256: `b2253d24841507f77953716062850302a9482c1180c6ef8874f0611c2d31a481`.

**Issue statuses, file-existence, and attestation payload:** see populated `## Attested Evidence` block below (R29). The block was generated by running `scripts/review/attest-plan-claims.sh` against a temporary stage of the v3 plan content under `docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md` at HEAD `3e0e7c2b`.

<!-- Source count: 14 (issue body + 13 artifacts) — exceeds >=3 minimum. -->

---

## Attested Evidence Procedure

v4 will reproduce the populated payload below by running, at draft time:

```
cp /tmp/plan-drafts/plan-2369-v3-current.md \
   docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md
bash scripts/review/attest-plan-claims.sh \
   docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md
rm docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md
```

The temporary stage is necessary because `attest-plan-claims.sh` enforces the allowlist regex `^docs/plans/[^/]+\.md$` for safety. The stage targets the path the v3 plan will land at when its branch merges — the attestation thus reflects what reviewers will see post-merge.

The populated payload follows exactly as captured (sha256 included so reviewers can verify the block was not edited after generation).

---

## Attested Evidence

## Attested Evidence (verified 2026-04-25T09:05:34Z at repo commit 3e0e7c2b5cc28c6e8aa0e446f6595276fb449afa)

**Issue states** (via `gh issue view --json number,state,title` — title+state only, no body):
- #2001 CLOSED feat: batch ingest pipeline — conference papers as wiki sources
- #2039 OPEN feat: engineering wiki — ingest remaining high-value sources (skills metadata, closed issues)
- #2067 OPEN feat(knowledge): wire .planning/research into engineering wiki nightly ingest
- #2068 OPEN feat(knowledge): add cross-link JSONL package for wiki-to-standard and wiki-to-module intelligence
- #2242 CLOSED feat(llm-wiki): prioritize external-source queue for token-efficient wiki strengthening
- #2243 CLOSED chore(llm-wiki): define token-efficient staged batch packs for broad wiki strengthening
- #2364 OPEN feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains
- #2369 OPEN feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs
- #2390 OPEN epic(knowledge): llm-wiki strengthening roadmap and execution waves
- #2405 CLOSED chore(review): cross-review sandbox needs repo + gh access so reviewers can affirmatively verify live-state claims
- #2406 CLOSED fix(review): submit-to-codex.sh hangs on 'Reading additional input from stdin' for substantial plan files

**File existence** (via `ls -la -- "$f"` with flag-injection guard):
- MISSING: attest-plan-claims.sh
- MISSING: conference-index-manifest.json
- MISSING: conference-registry.yaml
- EXISTS: data/document-index/conference-index-manifest.json  (-rwxrwxrwx 1 vamsee vamsee 1294 Apr  6 07:14 data/document-index/conference-index-manifest.json)
- EXISTS: data/document-index/conference-index-stats.yaml  (-rwxrwxrwx 1 vamsee vamsee 2873 Apr  4 22:50 data/document-index/conference-index-stats.yaml)
- EXISTS: data/document-index/conference-paper-catalog.yaml  (-rwxrwxrwx 1 vamsee vamsee 13054 Apr  4 23:05 data/document-index/conference-paper-catalog.yaml)
- EXISTS: data/document-index/conference-registry.yaml  (-rwxrwxrwx 1 vamsee vamsee 3397 Apr  5 21:47 data/document-index/conference-registry.yaml)
- MISSING: docs/reports/batch-pack-2-conference-summary-stubs.md
- EXISTS: docs/reports/llm-wiki-external-source-priority-queue.md  (-rwxrwxrwx 1 vamsee vamsee 8998 Apr 14 16:00 docs/reports/llm-wiki-external-source-priority-queue.md)
- EXISTS: docs/reports/llm-wiki-staged-batch-packs.md  (-rwxrwxrwx 1 vamsee vamsee 17928 Apr 14 16:00 docs/reports/llm-wiki-staged-batch-packs.md)
- MISSING: eval_cluster_quality.py
- EXISTS: knowledge/wikis/engineering/CLAUDE.md  (-rwxrwxrwx 1 vamsee vamsee 1781 Apr 16 12:05 knowledge/wikis/engineering/CLAUDE.md)
- EXISTS: knowledge/wikis/engineering/wiki/index.md  (-rwxrwxrwx 1 vamsee vamsee 12334 Apr 17 09:21 knowledge/wikis/engineering/wiki/index.md)
- EXISTS: knowledge/wikis/marine-engineering/CLAUDE.md  (-rwxrwxrwx 1 vamsee vamsee 3682 Apr 16 12:05 knowledge/wikis/marine-engineering/CLAUDE.md)
- EXISTS: knowledge/wikis/naval-architecture/CLAUDE.md  (-rwxrwxrwx 1 vamsee vamsee 3750 Apr 16 12:05 knowledge/wikis/naval-architecture/CLAUDE.md)
- MISSING: run-batch-pack-2.py
- MISSING: run_batch_pack_2.py
- EXISTS: scripts/knowledge/build-knowledge-index.sh  (-rwxrwxrwx 1 vamsee vamsee 3904 Apr 16 12:05 scripts/knowledge/build-knowledge-index.sh)
- MISSING: scripts/knowledge/eval_cluster_quality.py
- EXISTS: scripts/knowledge/llm_wiki.py  (-rwxrwxrwx 1 vamsee vamsee 51131 Apr 16 10:13 scripts/knowledge/llm_wiki.py)
- MISSING: scripts/knowledge/pin_stopwords_sha.py
- EXISTS: scripts/knowledge/registry-freshness-check.py  (-rwxrwxrwx 1 vamsee vamsee 7807 Apr 16 09:07 scripts/knowledge/registry-freshness-check.py)
- MISSING: scripts/knowledge/run_batch_pack_2.py
- EXISTS: scripts/knowledge/wiki-cross-links.py  (-rwxrwxrwx 1 vamsee vamsee 29665 Apr 16 12:05 scripts/knowledge/wiki-cross-links.py)
- EXISTS: scripts/review/attest-plan-claims.sh  (-rwxrwxrwx 1 vamsee vamsee 3249 Apr 20 21:18 scripts/review/attest-plan-claims.sh)
- MISSING: tests/knowledge/test_batch_pack_2.py

_Attestation payload sha256: 4d720fcade569e949755cc5387e0173bb4167d76ef4f4a9bf3ff5645f1a9e8b7_

### Reading the payload (notes)

- `MISSING: attest-plan-claims.sh`, `MISSING: conference-index-manifest.json`, `MISSING: conference-registry.yaml`, `MISSING: eval_cluster_quality.py`, `MISSING: run-batch-pack-2.py`, `MISSING: run_batch_pack_2.py` — these are bare-filename mentions inside the v3 plan that the attestation script's path-extraction regex captured without their full paths. The same files are also captured at their full paths (`scripts/review/attest-plan-claims.sh`, `data/document-index/conference-index-manifest.json`, `data/document-index/conference-registry.yaml`, `scripts/knowledge/eval_cluster_quality.py`, `scripts/knowledge/run_batch_pack_2.py`) elsewhere in the same payload — at full paths, the first three EXIST and the latter two are correctly MISSING (the runner is the new file v4 creates). v4 does not add or remove any bare-filename mentions; the payload is what reviewers should accept.
- `MISSING: run-batch-pack-2.py` (hyphenated form) appears because v3's R28 callout mentions the rejected hyphen-name. The runner's actual filename is `run_batch_pack_2.py` (underscore) per R28 + R42; both are correctly MISSING because the runner is new.
- The 11 issue-state lines exactly match v3's claims in §Resource Intelligence Summary > Issue statuses.
- All directory-prefixed file paths claimed by v3 resolve to EXISTS or correctly MISSING (the latter being new files this plan creates).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v4) | docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md |
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
| Plan reviews v3 | scripts/review/results/20260425T041318Z-plan-2369-v3.md-plan-claude.md, scripts/review/results/20260425T041539Z-plan-2369-v3.md-plan-gemini.md |
| Plan reviews v4 | scripts/review/results/<timestamp>-plan-2369-v4.md-plan-{claude,codex,gemini}.md |

---

## Deliverable

After this issue closes, `docs/reports/batch-pack-2-conference-summary-stubs.md` will exist, containing wiki-ready topic-cluster stubs derived from phase_a_complete conference indexing (actual set: DOT, OMAE, OTC), grouped by engineering domain and mapped to target wiki domains (marine-engineering, naval-architecture, engineering). A companion JSONL cross-link-candidate file will exist at `data/document-index/batch-pack-2-cross-link-candidates.jsonl` for #2068 consumption (schema in Appendix A, `schema_version: 1.2`). A sibling `batch-pack-2-skipped.jsonl` will record any malformed input rows. ISOPE will be deferred with a proposed-issue-body section appended to the report (per AC13, R35); user files manually. No source-PDF reads will occur. No wiki pages will be promoted in this issue.

---

## Runbook

The following sequence is mandatory before AC2 becomes runnable:

1. **`make pin-stopwords-sha`** — invokes `scripts/knowledge/pin_stopwords_sha.py`, which computes `sha256(scripts/knowledge/data/stopwords_en_v1.txt)` and rewrites the `STOPWORDS_SHA = "<unpinned>"` constant in `scripts/knowledge/run_batch_pack_2.py` to the pinned value.
2. **Verify Test 12 transitions xfail → pass** — `uv run pytest tests/knowledge/test_batch_pack_2.py::test_tfidf_stopwords_sha_pinned -v` should now pass (was xfail before step 1).
3. **AC2 becomes runnable** — `uv run python scripts/knowledge/run_batch_pack_2.py` exits 0 and emits the three artifacts named in AC2. Without step 1, the runner refuses to start with a `RuntimeError("Run \`make pin-stopwords-sha\` before invoking the runner")`.

For idempotency verification (Test 17 / AC6), invoke with `--now 2026-01-01T00:00:00Z` (or env `BP2_NOW=2026-01-01T00:00:00Z`) so `generated_at` is fixed across runs.

---

## Pseudocode

```
function run_batch_pack_2(catalog_path, phase_a_jsonl, output_report_path, now=None):
    # R30: --now / BP2_NOW seam for idempotency.
    now = now or os.environ.get("BP2_NOW") or iso8601_utc_now()
    now_epoch = iso8601_to_epoch(now)

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

    # R32: load JSONL via safe_open() helper; no global builtins.open patch.
    papers, skipped = load_jsonl_safely(phase_a_jsonl, opener=safe_open)

    clusters = {d: [] for d in DOMAIN_BUCKETS}                     # 6 domains + misc
    for paper in papers:
        primary, secondary_domains = classify_paper_domain_ranked(  # R31: list, not single
            paper.title, paper.conference, paper.path
        )                                                          # R5+R14: weighted ranked
        clusters[primary].append(paper)
        paper.secondary_domains = secondary_domains                # may be []; preserved for stub metadata

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
                                    provenance=[p.id for p in topic.top_papers],
                                    now=now, now_epoch=now_epoch)  # R30: deterministic
            stub.duplicate_candidate = check_wiki_duplicate(
                stub.title, stub.sources, wiki_root
            )
            stub.cluster_quality_caveat = "single-pass-deterministic"  # R20
            stubs.append(stub)

    write_report(output_report_path, stubs,
                 deferred_collections=deferred,
                 isope_proposed_issue_body=isope_proposed_body())   # R35: AC13
    write_cross_link_jsonl(
        "data/document-index/batch-pack-2-cross-link-candidates.jsonl",
        stubs                                                      # schema = Appendix A v1.2
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

### Classifier ranked-output contract (R14 — replaces v2's R5; R31 changes return type)

**Matching mode: exact-token after tokenization.** Title is tokenized with the same `title_ascii_lower_alphanum_v1` tokenizer used for TF-IDF; matching is set-membership of token in domain keyword set. No substring match.

**Per-domain weighted keyword sets:**

```python
# Each value is (keyword_set, per-keyword integer weight).
# R36: risers map to pipeline (corpus convention: riser-as-pipe);
#      VIV-host risers fire 'viv' first; mooring-attached risers fire 'mooring' first.
DOMAIN_KEYWORDS = {
    "VIV":           ({"viv", "vortex", "strake", "vortex_induced"}, 5),
    "pipeline":      ({"pipeline", "pipelines", "riser", "risers",
                       "spool", "jumper", "flowline"}, 4),  # R36 rationale above
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
        return ("misc", [])                          # R31: empty list, not None
    # Primary: highest score; ties -> alphabetical (deterministic, but rare under weights).
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    primary_name, primary_score = ranked[0]
    # R31: collect ALL secondaries that pass the threshold (no break after first match).
    threshold = max(1, primary_score - 2)
    secondary_domains = [
        name for name, score in ranked[1:]
        if score > 0 and score >= threshold
    ]
    return (primary_name, secondary_domains)         # always (str, list[str])
```

**Fixture deltas vs v2 (R34):**

| Test | v2 expected | v3/v4 expected | Why |
|---|---|---|---|
| Test 7 ("VIV fatigue in deepwater risers") | `(VIV, structural)` | `(VIV, [pipeline])` | Weighted scoring (R14): pipeline(4) > structural(2) so pipeline wins as secondary; v2 expectation reflected substring reasoning that did not survive the rewrite. v4 wraps in list per R31. |
| Test 8 ("VIV fatigue on pipelines") | `(pipeline, VIV)` | `(VIV, [pipeline])` | Specialist VIV outranks generic pipeline under weighting; aligns with how a reviewer would intuitively classify a paper titled "VIV fatigue on pipelines" — it is a VIV paper that happens to be about pipelines. v4 wraps in list per R31. |

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

Ranked: VIV(5), pipeline(4), structural(2). Primary = **VIV**. Threshold = max(1, 5-2) = 3; pipeline(4) >= 3 (kept), structural(2) < 3 (dropped). `secondary_domains = ["pipeline"]`.

**Worked example — Test 8: "VIV fatigue on pipelines"**

Tokens (drop "on"): `{"viv", "fatigue", "pipelines"}`.

| Domain | Hits | Weight | Score |
|---|---|---|---|
| VIV | {viv} | 5 | **5** |
| pipeline | {pipelines} | 4 | 4 |
| structural | {fatigue} | 2 | 2 |
| others | -- | -- | 0 |

Ranked: VIV(5), pipeline(4), structural(2). Primary = **VIV**. Threshold = 3; secondary_domains = ["pipeline"].

**Worked example — Test 6.5 (R36): "Riser analysis"**

Tokens: `{"riser", "analysis"}`. Hits: pipeline {riser} = 4. All other domains 0. Primary = **pipeline**. Secondary_domains = []. Confirms R36 rationale.

**Worked example — 3-way tie scenario (R31 verification): "VIV pipeline fracture"**

Tokens: `{"viv", "pipeline", "fracture"}`. Scores: VIV=5, pipeline=4, structural=2. Threshold = max(1, 5-2) = 3. Pipeline(4) >= 3 (kept); structural(2) < 3 (dropped). `secondary_domains = ["pipeline"]`. To trigger a 3-way tie we need a title where two non-primary domains both pass the threshold — e.g., "VIV jumper fracture stress_concentration" gives VIV=5, pipeline=4 (jumper), structural=4 (fracture, stress_concentration). Threshold = 3; both pipeline and structural pass. `secondary_domains = ["pipeline", "structural"]` (alphabetical). v3 would have returned `("VIV", "pipeline")` only — v4 preserves both per R31.

These three test fixtures (7, 8, 6.5) plus the 3-way tie test (Test 7b) will be locked in TDD List entries below.

### TF-IDF clustering — full determinism contract (R2/R12)

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
    # R37: precedence — when N_d == 1, k = max(1, min(N_d, ceil(sqrt(N_d/5))))
    # clips to 1; cluster_count_min: 2 does NOT override this. N_d-clip wins.
    "tie_break":       "lexical_on_paper_id",
    "implementation":  "stdlib_only",
    "library_pin":     "python>=3.11 (collections.Counter, math.log, re, json)",
    "rng_seed":        20260423,
}
```

(Tokenizer + clustering algorithm unchanged from v2 — see v2 §TF-IDF clustering full determinism contract.)

### Path-guard mechanism (R32 — replaces v3's R19 `builtins.open` monkey-patch)

```python
import os, pathlib

_DENY_PREFIXES = (os.path.realpath("/mnt/ace/docs/conferences/"),)

class PathGuardError(RuntimeError):
    pass

def safe_open(path, mode="r", *args, **kwargs):
    """Scoped helper. ALL runner read sites use this; no global builtins.open patch."""
    rp = os.path.realpath(path) if isinstance(path, (str, os.PathLike)) else None
    if rp and any(rp.startswith(p) for p in _DENY_PREFIXES):
        raise PathGuardError(f"Refused open under deny-prefix: {rp}")
    return open(path, mode, *args, **kwargs)
```

**CI grep guard** (Test 5b): the runner module must not import any other open function or bare `open`:

```bash
# Whitelisted lines: import of safe_open itself, import of pathlib.Path (Path objects are
# passed to safe_open(), Path.open() is NOT used). Any other 'open' or 'Path.open' fails CI.
grep -nE '\b(open|Path\.open|os\.open|io\.open)\b' scripts/knowledge/run_batch_pack_2.py \
  | grep -vE '(def safe_open|return open\(|from pathlib import Path)' \
  && exit 1 || exit 0
```

Test 5 calls `safe_open("/mnt/ace/docs/conferences/foo.pdf")` and asserts `PathGuardError`.
Test 5b grep-asserts no raw `open()` references survive in the runner module.
Test 5c (R40) calls `safe_open(pathlib.Path("/mnt/ace/docs/conferences/foo.pdf"))` and asserts `PathGuardError` — verifies PathLike acceptance.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/knowledge/run_batch_pack_2.py | runner: domain classification + topic clustering (underscore filename so tests can import; lives outside any hyphen-named directory per R28/R42) |
| Create | scripts/knowledge/pin_stopwords_sha.py | one-shot SHA pin script (R15); rewrites `STOPWORDS_SHA` constant in runner |
| Create | scripts/knowledge/eval_cluster_quality.py | optional non-blocking cluster-quality canary (R20) |
| Create | scripts/knowledge/data/stopwords_en_v1.txt | frozen stop-word list pinned by SHA in code |
| Create | tests/knowledge/test_batch_pack_2.py | TDD coverage (28 tests, see list) |
| Create | docs/reports/batch-pack-2-conference-summary-stubs.md | primary output (topic stubs grouped by domain + wiki target + ISOPE proposed-issue body per R35) |
| Create | data/document-index/batch-pack-2-cross-link-candidates.jsonl | input for #2068; schema = Appendix A v1.2 |
| Create | data/document-index/batch-pack-2-skipped.jsonl | malformed-record sidecar |
| Update | docs/reports/llm-wiki-external-source-priority-queue.md | one-line footnote at §5.2 (R7) — anchor-guarded fallback per R22 |
| Update | docs/reports/llm-wiki-staged-batch-packs.md | one-line footnote at §3.2 (R7) — anchor-guarded fallback per R22 |
| Update | docs/plans/README.md | add index row for this plan |
| Update | Makefile (or scripts/knowledge/Makefile) | add `pin-stopwords-sha` target invoking pin script (R15) |
| (No modify) | data/document-index/conference-paper-catalog.yaml | plan does NOT rewrite ISOPE status — separate follow-on issue if/when ISOPE is indexed |
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
| 5 | test_safe_open_rejects_reading_conference_pdf_dir | `safe_open` raises `PathGuardError` for deny-prefix (R32) | AC4 |
| 5b | test_runner_module_imports_no_raw_open | CI grep passes: no raw `open`/`Path.open`/`os.open` in runner (R32) | AC4 |
| 5c | test_safe_open_rejects_pathlib_path_objects | `safe_open(Path("/mnt/ace/docs/conferences/foo"))` raises (R40) | AC4 |
| 6 | test_classify_paper_domain_pipeline_wins | "pipeline integrity" → primary=pipeline | AC5 |
| 6.5 | test_classify_riser_only_title_lands_in_pipeline | "Riser analysis" → (pipeline, []) per R36 | AC5 |
| 7 | test_classify_paper_domain_viv_with_riser_secondary | "VIV fatigue in deepwater risers" → (VIV, [pipeline]) per R14+R31 | AC5 |
| 7b | test_classify_returns_multiple_secondaries_on_tie | "VIV jumper fracture stress_concentration" → (VIV, [pipeline, structural]) per R31 | AC5 |
| 8 | test_classify_returns_secondary_for_cross_domain | "VIV fatigue on pipelines" → (VIV, [pipeline]) per R14+R31 | AC5 |
| 9 | test_classify_paper_domain_default_misc | no keyword hit → (misc, []) | AC5 |
| 10 | test_cluster_preserves_paper_count_per_domain | sum(cluster.paper_count) == len(papers_in_domain) | AC3 |
| 11 | test_cluster_top_n_is_deterministic | same input → byte-identical top-N ordering | AC6 |
| 12 | test_tfidf_stopwords_sha_pinned | `STOPWORDS_SHA` matches sha256(file); `xfail` until `make pin-stopwords-sha` runs (R15) | AC6 |
| 13 | test_build_topic_stub_frontmatter_has_required_keys | stub has `title`,`tags`,`added`,`last_updated` | AC7 |
| 14 | test_build_topic_stub_provenance_is_list_of_paper_ids | each `sources:` resolvable to a phase_a record | AC8 |
| 15 | test_duplicate_check_detects_existing_wiki_page | existing wiki page with matching `sources:` flagged | AC9 |
| 16 | test_cross_link_jsonl_schema_secondary_domains_is_list | parser requires `secondary_domains: list[str]`; rejects single-string or `null` (R31) | AC10 |
| 17 | test_runner_is_idempotent_with_pinned_now | two runs with `--now 2026-01-01T00:00:00Z` produce byte-identical report + JSONL (R30) | AC6 |
| 18 | test_domain_to_target_wiki_table_all_allowed | every entry in DOMAIN_TARGET_WIKI maps to allowed set (R4) | AC12 |
| 19 | test_malformed_jsonl_row_is_skipped_not_crashed | malformed row → emitted to skipped.jsonl, run continues | AC3 |
| 20 | test_missing_phase_a_jsonl_raises_clear_error | absent file → typed exception with path in message | AC13 |
| 21 | test_unknown_indexing_status_value_warns | catalog with `indexing_status: in_progress` → WARN, treated as deferred | AC1 |
| 22 | test_empty_cluster_does_not_emit_stub | domain with zero papers produces no stub | AC3 |
| 23 | test_omae_subslice_perf_budget | OMAE-only run < 300s on `ubuntu-latest`-class runner; `pytest.mark.benchmark` excluded from default bar (R18) | AC14 |
| 24 | test_upstream_doc_footnote_present_with_anchor_fallback | both contradicting docs contain post-edit footnote; if §-anchor missing, end-of-doc fallback present (R22) | AC15 |
| 25 | test_single_paper_domain_does_not_crash | bucket of N_d=1 → k clipped to 1, one stub emitted; N_d-clip wins over `cluster_count_min` (R23+R37) | AC3 |
| 26 | test_runner_exits_nonzero_on_record_drift | drift detector trips → `sys.exit(2)` (R25) | AC17 |
| 27 | test_isope_proposed_body_section_present_in_report | report contains `## ISOPE re-index follow-on (proposed body)` header with non-empty markdown body (R35) | AC13 |

(Total: 28 tests; v3 had 26.)

---

## Acceptance Criteria

| # | Criterion |
|---|---|
| AC1 | `uv run pytest tests/knowledge/test_batch_pack_2.py -v` — all default-bar tests pass (benchmark Test 23 excluded) |
| AC2 | After `make pin-stopwords-sha` has run (Runbook step 1), `uv run python scripts/knowledge/run_batch_pack_2.py` exits 0 and produces `docs/reports/batch-pack-2-conference-summary-stubs.md`, `data/document-index/batch-pack-2-cross-link-candidates.jsonl`, `data/document-index/batch-pack-2-skipped.jsonl` (R33) |
| AC3 | Output report records **DOT + OMAE + OTC** as processed and **ISOPE** as deferred with reason; `len(papers) + len(skipped) == 14180` (R17) |
| AC4 | Runner never reads under `/mnt/ace/docs/conferences/` (Tests 5/5b/5c; mechanism = scoped `safe_open()` helper + CI grep per R32) |
| AC5 | Classifier returns `(primary: str, secondary_domains: list[str])` per R14+R31; worked-example fixtures pass (Tests 6, 6.5, 7, 7b, 8, 9) |
| AC6 | Two consecutive runs with `--now <fixed-ISO-8601>` produce byte-identical outputs (R30); stop-words SHA matches code constant after pin step |
| AC7 | Each stub frontmatter contains `title`, `tags`, `added`, `last_updated` |
| AC8 | Each stub records provenance as a list of phase-a record ids |
| AC9 | Duplicate-check flags overlapping existing wiki pages (does NOT auto-merge) |
| AC10 | Cross-link JSONL conforms to Appendix A schema v1.2; `secondary_domains` is `list[str]` (may be empty); `misc` not allowed in either `engineering_domain` secondary slots (handled at parse time) |
| AC11a | No wiki pages promoted (`knowledge/wikis/**` read-only — verified by git diff scope) (R21) |
| AC11b | No files under `config/**`, `.claude/**` modified (R21) |
| AC12 | Each stub `target_wiki` in {engineering, marine-engineering, naval-architecture}; mapping table in code matches plan §Pseudocode |
| AC13 | Report contains `## ISOPE re-index follow-on (proposed body)` header with non-empty markdown body; user files manually (R35) — single branch, no auto-file |
| AC14 | OMAE sub-slice completes in <5 min, full run in <15 min on `ubuntu-latest`-class runner (R18) |
| AC15 | Both contradicting upstream docs carry a footnote pointing to the new report; anchor-guarded fallback verified (R22) |
| AC16 | Review artifacts for all three providers posted to `scripts/review/results/` |
| AC17 | Runner exits non-zero (`sys.exit(2)`) if `len(papers) + len(skipped) != 14180` (R25) |

---

## Adversarial Review Summary

| Provider | v1 Verdict | v2 Verdict | v3 Verdict | v4 Verdict |
|---|---|---|---|---|
| Claude | MAJOR | MAJOR | MAJOR (P1: Attested Evidence placeholder, P1: idempotency vs `generated_at`, P1: builtins.open blast radius) | PENDING |
| Codex | UNAVAILABLE (#2406) | UNAVAILABLE | UNAVAILABLE (codex-cli 0.124 stdin-hang regression — see `feedback_codex_cli_0_124_upstream_regression`) | PENDING |
| Gemini | MINOR | MINOR | MAJOR (P1: Attested Evidence placeholder — REPEAT of r2 P1; P2: 3rd-domain silent-discard) | PENDING |

**v3 → v4 revisions:** see Revision Log at top. Cross-provider P1 (CONVERGED) addressed via R29 (populated payload at draft time, not scaffold). Claude r3 P1 idempotency-vs-timestamp addressed via R30 (`--now` injection seam, option (i) chosen). Gemini r3 P2 ties addressed via R31 (return ALL tied secondaries as list; schema `secondary_domains` v1.2). Claude r3 P1 builtins.open blast-radius addressed via R32 (scoped `safe_open()` helper + CI grep). Other Claude r3 P2/P3 items addressed via R33-R41.

---

## Risks and Open Questions

- **Risk (inherited misstatement):** v1 deferred fixing the two upstream docs. v4 includes anchor-guarded one-line footnotes on each (R7+R22).
- **Risk (OMAE scale):** OMAE alone has 7,292 titles. Stdlib-only TF-IDF with `max_vocab=2000`, single-pass farthest-first clustering, runs in `O(N x V) ~ 7292 x 2000 = 1.5e7` ops per domain — fits the <5 min budget by orders of magnitude on `ubuntu-latest` (R18).
- **Risk (classifier precision):** v4 uses weighted scoring (R14) so specialist signals (VIV) beat generic ones (marine). Worked examples for four fixtures inlined (Tests 6.5, 7, 7b, 8) for reviewer audit. Per-cluster confidence still surfaced per #2364 pattern.
- **Risk (PDF read-through):** scoped `safe_open()` helper invariant (R32) + CI grep + Tests 5/5b/5c.
- **Risk (duplicate-check scope):** marine-engineering wiki has 19,191 pages. v4 uses `sources:` frontmatter index (incremental; built once, cached at startup); same approach as #2364.
- **Risk (cluster quality):** single-pass farthest-first can produce poor cohesion on large buckets (R20+R27). Mitigated by per-stub `cluster_quality_caveat` field + optional non-blocking `eval_cluster_quality.py` canary. #2068 consumers documented as warned-not-authoritative.
- **Risk (#2068 schema fork):** v4 keeps schema in Appendix A; when #2068 lands, it adopts. Schema versioning + migration shim documented. v4 bumps to `schema_version: 1.2` for `secondary_domains` list (R31). Governance on schema drift after this issue lands: any schema change requires a `schema_version` bump and a migration note in #2068's plan; arbitration default = whichever issue is open at the time of conflict files a PR amending the other.
- **Risk (stopwords SHA pin step):** Test 12 starts as `xfail`; `make pin-stopwords-sha` flips it to `pass`. Documented in Runbook step 1 + Files-to-Change Makefile target.
- **Risk (idempotency seam):** Test 17 verifies byte-identical output ONLY when `--now` is fixed. Production runs (no `--now`) use runtime-now and are not byte-identical — by design (R30). Acceptance criterion AC6 is explicit about the fixed-now requirement.
- **Open:** Should the report group stubs first by `target_wiki_domain` or by engineering-topic-domain? Defaults to topic-domain per spec §3.2 step 2.
- **Open:** Whether `--collections` flag should default to all-three or require explicit set. Plan defaults to all-three for the canonical execution; flag exists for sub-slicing in CI/dev.

---

## Complexity: T2

**T2** — new runner + TDD test module (28 tests) + report + JSONL cross-link artifact + JSONL skipped sidecar + 2 footnote edits to existing docs + SHA-pin one-shot script + optional cluster-quality eval; zero mods to wiki pages; reads only indexed JSONL/YAML (no PDFs); explicit readiness-mismatch reconciliation is the load-bearing correctness move; weighted classifier with worked examples removes v2's spec-vs-fixture contradiction; stdlib-only TF-IDF with full determinism contract removes v1's library ambiguity; cluster-quality caveat + optional eval canary mitigates Gemini's clustering-quality concern without taking on a new dependency; populated Attested Evidence (R29) + `--now` injection (R30) + secondary_domains list (R31) + scoped `safe_open` (R32) close the v3 cross-provider-converged blocker plus Claude r3 P1 items.

---

## Appendix A — Cross-Link JSONL Schema (v1.2, source-of-truth for #2369; #2068 will adopt)

Each line in `data/document-index/batch-pack-2-cross-link-candidates.jsonl` is a JSON object with the following fields:

```json
{
  "stub_id": "bp2-pipeline-001",
  "schema_version": "1.2",
  "source_issue": 2369,
  "title": "Pipeline integrity under sour service",
  "engineering_domain": "pipeline",
  "secondary_domains": ["structural"],
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
  "generated_at": "2026-04-25T00:00:00Z",
  "generator": "scripts/knowledge/run_batch_pack_2.py",
  "generator_version": "1.0"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `stub_id` | string | yes | format `bp2-<domain>-<3-digit-zero-padded>`; on collision (e.g., re-run with corrected DOT data) appended with `-<generated_at_epoch>` per R24; epoch derives from `--now` per R30 (deterministic in tests) |
| `schema_version` | string | yes | semver; v4 bumps to `1.2` for `secondary_domains` list type (R31) |
| `source_issue` | int | yes | `2369` |
| `title` | string | yes | stub title |
| `engineering_domain` | enum | yes | one of {`pipeline`,`subsea`,`VIV`,`hydrodynamics`,`marine`,`structural`,`misc`} |
| `secondary_domains` | list[enum] | yes | each item one of {`pipeline`,`subsea`,`VIV`,`hydrodynamics`,`marine`,`structural`}; `misc` excluded per R16; empty list `[]` when no secondary qualifies (NOT `null`) per R31 |
| `target_wiki` | enum | yes | one of {`engineering`,`marine-engineering`,`naval-architecture`} |
| `target_wiki_path_hint` | string | yes | suggested wiki-relative path; ingestion may override |
| `paper_count` | int | yes | papers in this cluster |
| `top_paper_ids` | list[string] | yes | up to N=10 phase-a record ids; deterministic ordering |
| `topic_label` | string | yes | top-3 idf-weighted tokens, ` \| `-joined |
| `duplicate_candidate_path` | string or null | yes | path to existing wiki page if `sources:` overlap detected |
| `cluster_quality_caveat` | string | yes | always `"single-pass-deterministic"` for this generator (R20); consumers should not treat cluster boundaries as authoritative |
| `cross_link_candidates` | list[object] | yes | each `{target_wiki, target_path, confidence}`; up to 5 |
| `generated_at` | string | yes | ISO-8601 UTC; defaults to runner-start; overridable via `--now` flag or `BP2_NOW` env (R30) for deterministic test runs |
| `generator` | string | yes | this runner path |
| `generator_version` | string | yes | semver of runner; `1.0` at first emit (R39: decoupled from `schema_version`) |

Validation: `tests/knowledge/test_batch_pack_2.py::test_cross_link_jsonl_schema_secondary_domains_is_list` round-trips each line through a `dataclass` parser; `secondary_domains` must be `list[str]` (single-string or `null` rejected); any other field missing or type-mismatched also fails.

#2068 integration note: when #2068 implements the cross-link generator, it consumes this JSONL as input. Schema changes after this issue lands require a `schema_version` bump and a migration note in #2068's plan (see Risks). v3→v4 schema bump (1.1→1.2) is documented above as the precedent.
