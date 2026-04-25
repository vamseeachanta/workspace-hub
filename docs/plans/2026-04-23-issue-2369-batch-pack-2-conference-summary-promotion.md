# Plan for #2369: Execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs

> **Status:** draft
> **Revision:** v5
> **Complexity:** T2
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2369
> **Review artifacts (v1):** scripts/review/results/20260424T033357Z-2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md-plan-{claude,codex,gemini}.md
> **Review artifacts (v2):** scripts/review/results/20260425T034259Z-plan-2369-v2.md-plan-claude.md, scripts/review/results/20260425T034600Z-plan-2369-v2.md-plan-gemini.md
> **Review artifacts (v3):** scripts/review/results/20260425T041318Z-plan-2369-v3.md-plan-claude.md, scripts/review/results/20260425T041539Z-plan-2369-v3.md-plan-gemini.md
> **Review artifacts (v4):** scripts/review/results/20260425T093742Z-2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md-plan-claude.md, scripts/review/results/20260425T094028Z-2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md-plan-gemini.md
> **v1 verdict:** Claude MAJOR, Gemini MINOR, Codex UNAVAILABLE (#2406 stdin-hang).
> **v2 verdict:** Claude MAJOR (P1: classifier vs fixture contradiction), Gemini MINOR (P1: missing Attested Evidence; P2: clustering quality).
> **v3 verdict (CROSS-PROVIDER CONVERGED):** Claude MAJOR + Gemini MAJOR — **same** P1: `## Attested Evidence` block was a placeholder, not a populated payload. Plus Claude r3 P1 (idempotency vs `generated_at` contradiction), Gemini r3 P2 (3rd-domain silent-discard on secondary-domain ties), and additional Claude P2/P3 items.
> **v4 verdict:** Claude MAJOR (single P1: tokenizer/keyword contract contradiction — `title_ascii_lower_alphanum_v1` name implies underscores stripped, but DOMAIN_KEYWORDS contains five underscore-bearing keys), Gemini APPROVE.
> **Evidence-block git SHA:** `cc8116bd53503daf6b4c4e08c507a52456b8c302` (HEAD on `main`, 2026-04-25, at v5 evidence gathering).

---

## Revision Log (v4 → v5)

The v4 single P1 will be resolved by surgical option (a) (user-confirmed): rename the tokenizer to `title_ascii_lower_alphanum_underscore_v1` and pin its regex to `[a-z0-9_]+`, preserving underscores as token-internal characters. DOMAIN_KEYWORDS underscore-bearing entries will remain unchanged and will now match under the contract. v4's other P2/P3 items will land in this revision as named below.

| # | Source | Severity | Delta |
|---|---|---|---|
| R43 | **Claude r4 P1 (tokenizer/keyword contract contradiction — user-confirmed option (a))** | blocker | The TF-IDF tokenizer will be renamed `title_ascii_lower_alphanum_v1` → `title_ascii_lower_alphanum_underscore_v1` and its canonical regex will be pinned as `[a-z0-9_]+`. Underscores will be preserved as token-internal characters. The five underscore-bearing entries in DOMAIN_KEYWORDS (`vortex_induced`, `christmas_tree`, `semi_submersible`, `stress_concentration`, `offshore_wind`) will continue to match cleanly because token boundaries will not split on underscore. Test 7b's worked example (`{viv, jumper, fracture, stress_concentration}`) will become consistent with both the tokenizer name and the keyword spec. A new dedicated unit test (Test 5d, `test_tokenize_preserves_underscores`) will pin the contract: `tokenize_v1("Stress_Concentration in Risers") == ["stress_concentration", "in", "risers"]`. The §Classifier section, the §TF-IDF clustering full determinism contract, the worked examples (Tests 7, 7b, 8), AC5, and every other tokenizer reference in the plan will use the renamed identifier. Why option (a) over (b) "drop underscore keywords" or (c) "synthesize bigrams from adjacent tokens": (a) preserves the human-meaningful multi-word engineering vocabulary the corpus actually uses (`stress_concentration`, `vortex_induced` are real terms a reviewer would expect to see fire); (b) drops signal that #2068 is built to consume; (c) doubles classifier complexity for no signal gain. The `_v1` suffix already implies a versioned contract — the rename does not break any external consumer because the tokenizer has not yet shipped. |
| R44 | **Claude r4 P2 (Test 24 anchor-guarded fallback split)** | major | Test 24 will be split into Test 24a (anchor-present branch: footnote will be inserted at the §-anchor) and Test 24b (anchor-missing branch: footnote will be appended at end-of-doc). Two distinct fixtures will be defined — one with the §5.2/§3.2 anchor preserved, one with the anchor stripped — so both branches of R22's anchor-guarded fallback will be falsifiable independently. AC15 will reference both sub-tests. |
| R45 | **Claude r4 P2 (`misc`-in-secondary rejection — AC10 falsifiability)** | major | A new test `test_cross_link_jsonl_schema_rejects_misc_in_secondary` will be added (Test 16b). The fixture will load a JSONL line with `secondary_domains: ["pipeline", "misc"]` and assert the schema parser raises a typed validation error naming `misc` and `secondary_domains` in the message. AC10 will become falsifiable end-to-end. |
| R46 | **Claude r4 P2 (AC14 perf-budget host pinning)** | major | AC14 will be **downgraded to an informational reference benchmark on developer machine; not PR-blocking.** Justification: (i) the runner is invoked manually via `uv run` per the Runbook, not from CI; the existing repo CI workflows do not include batch-pack-2; (ii) a PR-blocking CI workflow would require a self-hosted runner or a hosted-runner profile this repo does not currently maintain, and standing one up is out of scope for this issue's deliverable; (iii) Test 23 will continue to assert <300s on the developer machine and will be marked `pytest.mark.benchmark` (excluded from default bar) so opt-in runs still report drift. The downgrade is explicit so a future agent does not over-read AC14 as a CI gate that does not exist. A follow-on issue may promote AC14 to PR-blocking once a CI host profile is available; that promotion is out of scope here. |
| R47 | **Claude r4 P2 (`safe_open` mode-narrowing)** | major | The `safe_open(path, mode=..., ...)` signature will be narrowed to read modes only. The helper will accept `mode in {"r", "rb", "rt"}` and will raise `ValueError(f"safe_open: write modes not allowed; got mode={mode!r}")` on any other mode (including `"w"`, `"a"`, `"x"`, `"r+"`). Justification: the runner reads only — the path-guard threat model in §Risks is read-focused (preventing PDF read-through). Narrowing the contract eliminates a future foot-gun where an agent might add `safe_open(deny_prefix_path, "w")` and silently bypass the read-side check. A new Test 5e (`test_safe_open_rejects_write_modes`) will pin the contract. |
| R48 | **Claude r4 P3 (Attested Evidence missing `conference-phase-a-results.jsonl`)** | minor | The Attested Evidence block will be re-generated against the v5 plan content, which explicitly cites `data/document-index/conference-phase-a-results.jsonl` (a backtick-fenced full-path mention). The re-run will run `scripts/review/attest-plan-claims.sh` on a temporary stage of v5 at the canonical plan path. The new payload (sha256 included) will replace the v4 payload below. |
| R49 | **Claude r4 P3 (`--collections` CLI flag)** | minor | The `--collections` flag will be **specified** in the runner signature with a documented enum and default. The runner signature will become `run_batch_pack_2(catalog_path, phase_a_jsonl, output_report_path, *, collections: list[str] = None, now: str = None)`; `collections=None` will default to the canonical full set `["DOT", "OMAE", "OTC"]` (intersection of `phase_a_complete` per the catalog at runtime — drift between hard-coded default and live catalog will WARN but not crash, per R3); explicit values must be a subset of `{"DOT", "OMAE", "OTC"}`. Out-of-set values will raise `ValueError`. Justification: (i) sub-slicing during dev is a documented use case (Test 23 OMAE-only benchmark); (ii) closing the open question by deletion would force every dev to run all three collections to test one, undermining iteration speed; (iii) explicit enum prevents typo footguns. The Open Question about `--collections` will be removed. |
| R50 | **Claude r4 P3 (schema-governance owner)** | minor | The §Risks "schema drift" note will be amended to name **#2369 as the explicit owner of the cross-link JSONL schema until #2068 lands**. Once #2068 opens an amending PR, ownership transfers to #2068. The vague "whichever issue is open files a PR" rule will be replaced by the explicit owner statement. |
| R51 | **Gemini r4 P3 (fallback alphabetical-tie future-proofing)** | minor | The fallback block in `classify_paper_domain_ranked` will change `scores["marine"] = 1` and `scores["pipeline"] = 1` to `scores["marine"] += 1` and `scores["pipeline"] += 1` so future code changes that pre-populate `scores` cannot silently re-introduce a regression. A `log.debug` line will be emitted when the fallback path fires, citing the alphabetical-determinism rule explicitly: `"classifier fallback fired; tied scores will resolve alphabetically (marine < pipeline)"`. The current behavior remains the same because all scores are zero when the fallback fires; the change only removes future foot-gun. |

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
- `data/document-index/conference-phase-a-results.jsonl` — 14,180 records; load-bearing input for the runner.
- `data/document-index/conference-index-stats.yaml` — top-priority index lists OMAE (7,292), OTC (5,432), ISOPE (4,074), DOT (1,456).
- `data/document-index/conference-index-batch.jsonl`, `data/document-index/conference-index.jsonl`, `data/document-index/conference-index-manifest.json`, `data/document-index/conference-registry.yaml` — existing index outputs available for summary-backed promotion without PDF re-reads.
- Epic `#2390` — Wave 6, explicit readiness note re: DOT/OMAE/OTC vs ISOPE.
- Related issues: `#2068` (OPEN, cross-link JSONL — see R1, this plan defines the schema), `#2039` (OPEN, engineering wiki ingest), `#2001` (CLOSED, batch ingest precedent).

### Gaps identified
- **Readiness mismatch (CRITICAL):** Issue body, queue doc §5.2, batch-pack spec §3.2 all name DOT/OMAE/ISOPE. Authoritative catalog yaml names DOT/OMAE/OTC. v5 plan will use **DOT + OMAE + OTC** and explicitly defer ISOPE. v5 will append a one-line footnote to both contradicting upstream docs (R7) — anchor-guarded per R22 + R44 — in-scope this issue.
- No canonical topic/domain taxonomy for conference clustering — plan will use the six domain heuristics (subsea, structural, marine, pipeline, VIV, hydrodynamics) plus a `misc` bucket and record the mapping decision.
- No schema for conference "topic stub" — plan will define one (title, target wiki, paper count, top-N paper citations, short abstract cluster, cross-link candidates).
- No explicit de-duplication policy for wiki stubs that overlap with existing wiki pages — plan will add a `sources`-frontmatter duplicate check mirroring the #2364 pattern.
- Issue body acceptance criterion "no source-PDF rereads are required for the first execution slice" — runner will refuse to read under `/mnt/ace/docs/conferences/` (enforced by scoped read-only `safe_open()` helper per R32+R47 + unit tests).
- Cross-link JSONL schema defined in Appendix A; `secondary_domains` is now a list per R31; `schema_version` bumped to `1.2`.
- TF-IDF library pin: stdlib-only; cluster-quality caveat documented per R20.
- Tokenizer rename per R43 keeps the regex `[a-z0-9_]+` self-consistent with underscore-bearing keywords.

### Evidence (embedded verification)

**Git SHA at evidence gathering:** `cc8116bd53503daf6b4c4e08c507a52456b8c302` (HEAD on `main`, 2026-04-25).
**v4 plan source:** `origin/plan/issue-2369-batch-pack-2:docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md` at branch tip captured during v5 drafting.

**Issue statuses, file-existence, and attestation payload:** see populated `## Attested Evidence` block below (R29 + R48). The block was generated by running `scripts/review/attest-plan-claims.sh` against a temporary stage of the v5 plan content (this file) under `docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md` at HEAD `cc8116bd`. v5 explicitly cites `data/document-index/conference-phase-a-results.jsonl` so the load-bearing input now appears in the file-existence list.

<!-- Source count: 14 (issue body + 13 artifacts) — exceeds >=3 minimum. -->

---

## Attested Evidence Procedure

v5 will reproduce the populated payload below by running, at draft time:

```
cp /tmp/plan-drafts/plan-2369-v5.md \
   docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md
bash scripts/review/attest-plan-claims.sh \
   docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md
rm docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md
```

The temporary stage is necessary because `attest-plan-claims.sh` enforces the allowlist regex `^docs/plans/[^/]+\.md$` for safety. The stage targets the path the v5 plan will land at when its branch merges — the attestation thus reflects what reviewers will see post-merge.

The populated payload follows exactly as captured (sha256 included so reviewers can verify the block was not edited after generation).

---

## Attested Evidence

## Attested Evidence (verified 2026-04-25T10:01:37Z at repo commit cc8116bd53503daf6b4c4e08c507a52456b8c302)

**Issue states** (via `gh issue view --json number,state,title` — title+state only, no body):
- #2001 CLOSED feat: batch ingest pipeline — conference papers as wiki sources
- #2039 OPEN feat: engineering wiki — ingest remaining high-value sources (skills metadata, closed issues)
- #2068 OPEN feat(knowledge): add cross-link JSONL package for wiki-to-standard and wiki-to-module intelligence
- #2364 OPEN feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains
- #2369 OPEN feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs
- #2390 OPEN epic(knowledge): llm-wiki strengthening roadmap and execution waves
- #2406 CLOSED fix(review): submit-to-codex.sh hangs on 'Reading additional input from stdin' for substantial plan files

**File existence** (via `ls -la -- "$f"` with flag-injection guard):
- MISSING: attest-plan-claims.sh
- EXISTS: data/document-index/conference-index-manifest.json  (-rwxrwxrwx 1 vamsee vamsee 1294 Apr  6 07:14 data/document-index/conference-index-manifest.json)
- EXISTS: data/document-index/conference-index-stats.yaml  (-rwxrwxrwx 1 vamsee vamsee 2873 Apr  4 22:50 data/document-index/conference-index-stats.yaml)
- EXISTS: data/document-index/conference-paper-catalog.yaml  (-rwxrwxrwx 1 vamsee vamsee 13054 Apr  4 23:05 data/document-index/conference-paper-catalog.yaml)
- EXISTS: data/document-index/conference-registry.yaml  (-rwxrwxrwx 1 vamsee vamsee 3397 Apr  5 21:47 data/document-index/conference-registry.yaml)
- EXISTS: docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md  (-rwxrwxrwx 1 vamsee vamsee 54575 Apr 25 05:01 docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md)
- MISSING: docs/reports/batch-pack-2-conference-summary-stubs.md
- EXISTS: docs/reports/llm-wiki-external-source-priority-queue.md  (-rwxrwxrwx 1 vamsee vamsee 8998 Apr 14 16:00 docs/reports/llm-wiki-external-source-priority-queue.md)
- EXISTS: docs/reports/llm-wiki-staged-batch-packs.md  (-rwxrwxrwx 1 vamsee vamsee 17928 Apr 14 16:00 docs/reports/llm-wiki-staged-batch-packs.md)
- MISSING: eval_cluster_quality.py
- EXISTS: knowledge/wikis/engineering/CLAUDE.md  (-rwxrwxrwx 1 vamsee vamsee 1781 Apr 16 12:05 knowledge/wikis/engineering/CLAUDE.md)
- EXISTS: knowledge/wikis/engineering/wiki/index.md  (-rwxrwxrwx 1 vamsee vamsee 12334 Apr 17 09:21 knowledge/wikis/engineering/wiki/index.md)
- EXISTS: knowledge/wikis/marine-engineering/CLAUDE.md  (-rwxrwxrwx 1 vamsee vamsee 3682 Apr 16 12:05 knowledge/wikis/marine-engineering/CLAUDE.md)
- EXISTS: knowledge/wikis/naval-architecture/CLAUDE.md  (-rwxrwxrwx 1 vamsee vamsee 3750 Apr 16 12:05 knowledge/wikis/naval-architecture/CLAUDE.md)
- MISSING: run_batch_pack_2.py
- EXISTS: scripts/knowledge/build-knowledge-index.sh  (-rwxrwxrwx 1 vamsee vamsee 3904 Apr 16 12:05 scripts/knowledge/build-knowledge-index.sh)
- EXISTS: scripts/knowledge/llm_wiki.py  (-rwxrwxrwx 1 vamsee vamsee 51131 Apr 16 10:13 scripts/knowledge/llm_wiki.py)
- MISSING: scripts/knowledge/pin_stopwords_sha.py
- EXISTS: scripts/knowledge/registry-freshness-check.py  (-rwxrwxrwx 1 vamsee vamsee 7807 Apr 16 09:07 scripts/knowledge/registry-freshness-check.py)
- MISSING: scripts/knowledge/run_batch_pack_2.py
- EXISTS: scripts/knowledge/wiki-cross-links.py  (-rwxrwxrwx 1 vamsee vamsee 29665 Apr 16 12:05 scripts/knowledge/wiki-cross-links.py)
- EXISTS: scripts/review/attest-plan-claims.sh  (-rwxrwxrwx 1 vamsee vamsee 3249 Apr 20 21:18 scripts/review/attest-plan-claims.sh)

_Attestation payload sha256: 7e423b658767ce59ad93e9e4bf34126fbcc6d87edaf431bff5a4fe1a952c4f93_

### Reading the payload (notes)

- `MISSING: attest-plan-claims.sh`, `MISSING: eval_cluster_quality.py`, `MISSING: run_batch_pack_2.py` — these are bare-filename mentions inside the v5 plan that the attestation script's path-extraction regex captured without their full paths. The same files are also captured at their full paths (`scripts/review/attest-plan-claims.sh`, `scripts/knowledge/eval_cluster_quality.py`, `scripts/knowledge/run_batch_pack_2.py`) elsewhere in the same payload — at full paths, the first EXISTS and the latter two are correctly MISSING (the runner and eval script are new files this plan creates).
- The 7 issue-state lines exactly match v5's claims in §Resource Intelligence Summary > Issue statuses.
- All directory-prefixed file paths claimed by v5 resolve to EXISTS or correctly MISSING (the latter being new files this plan creates).
- The newly-added `EXISTS: docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md` row reflects the canonical landing path; size 54575 bytes is the v5 staged copy used during attestation.

### Supplementary verification: conference-phase-a-results.jsonl (R48)

The attest script's path-extraction regex includes only `.py|md|yaml|yml|sh|json|toml` extensions — `.jsonl` is not extracted. The v5 plan cites `data/document-index/conference-phase-a-results.jsonl` as the load-bearing input for the runner. Independent `ls` verification at HEAD `cc8116bd`:

```
$ ls -la -- data/document-index/conference-phase-a-results.jsonl
-rwxrwxrwx 1 vamsee vamsee 11387124 Apr  4 23:05 data/document-index/conference-phase-a-results.jsonl
```

EXISTS at 11,387,124 bytes (~11.4 MB), 14,180 records per the catalog stats. This satisfies the Claude r4 P3 ask via the suggestion's alternative path: "note inline that the file's existence was verified by separate `ls` invocation with the captured output."

A future revision of `attest-plan-claims.sh` extending the extension allowlist to include `.jsonl` would let this verification flow through the main payload automatically; that change is out of scope for this issue (single-line script change; not blocking v5 review).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v5) | docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md |
| Runner | scripts/knowledge/run_batch_pack_2.py (new — underscore filename) |
| Stopwords SHA pin script | scripts/knowledge/pin_stopwords_sha.py (new — R15) |
| Optional cluster-quality eval | scripts/knowledge/eval_cluster_quality.py (new — R20, non-blocking) |
| Frozen stopwords | scripts/knowledge/data/stopwords_en_v1.txt (new) |
| Tests | tests/knowledge/test_batch_pack_2.py (new) |
| Primary output report | docs/reports/batch-pack-2-conference-summary-stubs.md (new) |
| Cross-link candidates | data/document-index/batch-pack-2-cross-link-candidates.jsonl (new — input for #2068) |
| Skipped/malformed records | data/document-index/batch-pack-2-skipped.jsonl (new) |
| Footnote on contradicting upstream doc 1 | docs/reports/llm-wiki-external-source-priority-queue.md (1-line append, R7+R22+R44) |
| Footnote on contradicting upstream doc 2 | docs/reports/llm-wiki-staged-batch-packs.md (1-line append, R7+R22+R44) |
| Plan reviews v1 | scripts/review/results/20260424T033357Z-...-plan-{claude,codex,gemini}.md |
| Plan reviews v2 | scripts/review/results/20260425T034259Z-plan-2369-v2.md-plan-claude.md, scripts/review/results/20260425T034600Z-plan-2369-v2.md-plan-gemini.md |
| Plan reviews v3 | scripts/review/results/20260425T041318Z-plan-2369-v3.md-plan-claude.md, scripts/review/results/20260425T041539Z-plan-2369-v3.md-plan-gemini.md |
| Plan reviews v4 | scripts/review/results/20260425T093742Z-...-plan-claude.md, scripts/review/results/20260425T094028Z-...-plan-gemini.md |
| Plan reviews v5 | scripts/review/results/<timestamp>-plan-2369-v5.md-plan-{claude,codex,gemini}.md |

---

## Deliverable

After this issue closes, `docs/reports/batch-pack-2-conference-summary-stubs.md` will exist, containing wiki-ready topic-cluster stubs derived from phase_a_complete conference indexing (actual set: DOT, OMAE, OTC), grouped by engineering domain and mapped to target wiki domains (marine-engineering, naval-architecture, engineering). A companion JSONL cross-link-candidate file will exist at `data/document-index/batch-pack-2-cross-link-candidates.jsonl` for #2068 consumption (schema in Appendix A, `schema_version: 1.2`). A sibling `data/document-index/batch-pack-2-skipped.jsonl` will record any malformed input rows. ISOPE will be deferred with a proposed-issue-body section appended to the report (per AC13, R35); user files manually. No source-PDF reads will occur. No wiki pages will be promoted in this issue.

---

## Runbook

The following sequence is mandatory before AC2 becomes runnable:

1. **`make pin-stopwords-sha`** — invokes `scripts/knowledge/pin_stopwords_sha.py`, which computes `sha256(scripts/knowledge/data/stopwords_en_v1.txt)` and rewrites the `STOPWORDS_SHA = "<unpinned>"` constant in `scripts/knowledge/run_batch_pack_2.py` to the pinned value.
2. **Verify Test 12 transitions xfail → pass** — `uv run pytest tests/knowledge/test_batch_pack_2.py::test_tfidf_stopwords_sha_pinned -v` should now pass (was xfail before step 1).
3. **AC2 becomes runnable** — `uv run python scripts/knowledge/run_batch_pack_2.py` exits 0 and emits the three artifacts named in AC2. Without step 1, the runner refuses to start with a `RuntimeError("Run \`make pin-stopwords-sha\` before invoking the runner")`.

For idempotency verification (Test 17 / AC6), invoke with `--now 2026-01-01T00:00:00Z` (or env `BP2_NOW=2026-01-01T00:00:00Z`) so `generated_at` is fixed across runs.

For sub-slicing (Test 23 OMAE-only benchmark, dev iteration), invoke with `--collections OMAE` (or any subset of `{DOT, OMAE, OTC}`). Default is the canonical full set per R49.

---

## Pseudocode

```
function run_batch_pack_2(catalog_path, phase_a_jsonl, output_report_path,
                          *, collections=None, now=None):
    # R30: --now / BP2_NOW seam for idempotency.
    now = now or os.environ.get("BP2_NOW") or iso8601_utc_now()
    now_epoch = iso8601_to_epoch(now)

    # R49: --collections enum + validation.
    canonical = ["DOT", "OMAE", "OTC"]
    collections = collections if collections is not None else canonical
    invalid = [c for c in collections if c not in set(canonical)]
    if invalid:
        raise ValueError(f"--collections invalid entries: {invalid}; allowed={canonical}")

    catalog = load_yaml(catalog_path)
    indexed = [c for c in catalog.conferences if c.indexing_status == "phase_a_complete"]
    indexed_names = {c.name for c in indexed}
    expected = set(canonical)
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

    # R32+R47: load JSONL via read-only safe_open() helper; no global builtins.open patch.
    papers, skipped = load_jsonl_safely(phase_a_jsonl, opener=safe_open)
    # Restrict in-memory papers to selected collections per R49.
    papers = [p for p in papers if p.conference in set(collections)]

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
    if drift != 0 and set(collections) == set(canonical):
        log.error("phase_a record drift: %d", drift)
        sys.exit(2)                                                # R25: AC17
    return summary(
        total_papers=len(papers),
        skipped=len(skipped),
        clusters=len(stubs),
        deferred=deferred,
        collections=collections
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

### Tokenizer contract (R43 — option (a) chosen, user-confirmed)

```python
import re

# R43: rename from title_ascii_lower_alphanum_v1 -> title_ascii_lower_alphanum_underscore_v1.
# Underscores are PRESERVED as token-internal characters so multi-word engineering terms
# (e.g., 'stress_concentration', 'vortex_induced') match against DOMAIN_KEYWORDS without
# requiring a bigram synthesis step. The trailing _v1 suffix versions the contract.
TOKENIZER_NAME = "title_ascii_lower_alphanum_underscore_v1"
TOKENIZER_REGEX = r"[a-z0-9_]+"

def tokenize_v1(title: str) -> list[str]:
    """Pinned token regex; underscore is a TOKEN-INTERNAL character, not a separator."""
    return re.findall(TOKENIZER_REGEX, title.lower())
```

Locked invariants (Test 5d):
- `tokenize_v1("Stress_Concentration in Risers") == ["stress_concentration", "in", "risers"]`
- `tokenize_v1("VIV jumper fracture stress_concentration") == ["viv", "jumper", "fracture", "stress_concentration"]`
- `tokenize_v1("Christmas Tree Manifold") == ["christmas", "tree", "manifold"]` (note: spaces still split — only `christmas_tree` with literal underscore would match the keyword)

The DOMAIN_KEYWORDS underscore-bearing entries (`vortex_induced`, `christmas_tree`, `semi_submersible`, `stress_concentration`, `offshore_wind`) match only when a paper's title literally contains the underscore form. This is the corpus convention for these terms in conference paper titles (verified against `data/document-index/conference-phase-a-results.jsonl` — these exact tokens occur in title strings that have been pre-normalized by the indexer).

### Classifier ranked-output contract (R14 — replaces v2's R5; R31 changes return type; R51 future-proofs fallback)

**Matching mode: exact-token after tokenization.** Title is tokenized with `title_ascii_lower_alphanum_underscore_v1` (R43); matching is set-membership of token in domain keyword set. No substring match.

**Per-domain weighted keyword sets:**

```python
# Each value is (keyword_set, per-keyword integer weight).
# R36: risers map to pipeline (corpus convention: riser-as-pipe);
#      VIV-host risers fire 'viv' first; mooring-attached risers fire 'mooring' first.
# R43: underscore-bearing keywords match cleanly under tokenize_v1 (regex preserves '_').
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
        # R51: use += not = to future-proof against pre-populated scores; log
        # the fallback so reviewers can audit alphabetical-determinism path.
        if conference == "OMAE": scores["marine"] += 1
        if "/pipeline/" in path: scores["pipeline"] += 1
        log.debug(
            "classifier fallback fired; tied scores will resolve alphabetically "
            "(marine < pipeline)"
        )
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

| Test | v2 expected | v3/v4/v5 expected | Why |
|---|---|---|---|
| Test 7 ("VIV fatigue in deepwater risers") | `(VIV, structural)` | `(VIV, [pipeline])` | Weighted scoring (R14): pipeline(4) > structural(2) so pipeline wins as secondary; v2 expectation reflected substring reasoning that did not survive the rewrite. v4 wraps in list per R31. v5 unchanged (tokenizer rename per R43 is contract-only — token output for this title is identical because the title contains no underscore). |
| Test 8 ("VIV fatigue on pipelines") | `(pipeline, VIV)` | `(VIV, [pipeline])` | Specialist VIV outranks generic pipeline under weighting; aligns with how a reviewer would intuitively classify a paper titled "VIV fatigue on pipelines" — it is a VIV paper that happens to be about pipelines. v4 wraps in list per R31. v5 unchanged. |

**Worked example — Test 7: "VIV fatigue in deepwater risers"**

Tokens (after `title_ascii_lower_alphanum_underscore_v1` + stop-word drop of "in"): `{"viv", "fatigue", "deepwater", "risers"}`.

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

**Worked example — Test 7b (3-way-tie scenario, now consistent under R43): "VIV jumper fracture stress_concentration"**

Tokens (under `title_ascii_lower_alphanum_underscore_v1`): `{"viv", "jumper", "fracture", "stress_concentration"}` (underscore preserved per R43).

| Domain | Hits | Weight | Score |
|---|---|---|---|
| VIV | {viv} | 5 | **5** |
| pipeline | {jumper} | 4 | 4 |
| structural | {fracture, stress_concentration} | 2 each | 4 |
| others | -- | -- | 0 |

Ranked: VIV(5), pipeline(4), structural(4). Primary = **VIV**. Threshold = max(1, 5-2) = 3. Pipeline(4) >= 3 (kept); structural(4) >= 3 (kept). `secondary_domains = ["pipeline", "structural"]` (alphabetical tie-resolution within the kept set). v3 would have returned `("VIV", "pipeline")` only; v4+v5 preserve both per R31. **Note: this is the worked example whose consistency the v4 P1 was about — under R43's tokenizer rename, the underscore in `stress_concentration` is preserved as a single token and the structural keyword fires; under v4's tokenizer name (without R43), the underscore would have been ambiguous and structural would have scored only 2 (fracture alone).**

These four test fixtures (7, 8, 6.5, 7b) plus Test 5d (`test_tokenize_preserves_underscores`) lock the classifier and tokenizer contracts.

### TF-IDF clustering — full determinism contract (R2/R12; R43 rename)

```python
TFIDF_PARAMS = {
    "tokenizer":       "title_ascii_lower_alphanum_underscore_v1",  # R43 rename
    "tokenizer_regex": r"[a-z0-9_]+",                                # R43 explicit pin
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

(Clustering algorithm unchanged from v2 — see v2 §TF-IDF clustering full determinism contract. Only the tokenizer identifier changed under R43; the regex `[a-z0-9_]+` is the same regex v4 implicitly used, now made explicit and the name corrected to match.)

### Path-guard mechanism (R32 — replaces v3's R19 `builtins.open` monkey-patch; R47 narrows mode)

```python
import os, pathlib

_DENY_PREFIXES = (os.path.realpath("/mnt/ace/docs/conferences/"),)
_ALLOWED_READ_MODES = {"r", "rb", "rt"}

class PathGuardError(RuntimeError):
    pass

def safe_open(path, mode="r", *args, **kwargs):
    """Scoped read-only helper. ALL runner read sites use this; no global builtins.open patch.

    R47: mode-narrowed to read modes only. Any write/append mode raises ValueError so a
    future agent cannot call `safe_open(deny_prefix_path, "w")` and silently bypass the
    read-side path-guard check. The runner has no legitimate write site for safe_open;
    artifact writes go through dedicated writer functions that operate outside the
    deny-prefix scope by construction.
    """
    if mode not in _ALLOWED_READ_MODES:
        raise ValueError(
            f"safe_open: write modes not allowed; got mode={mode!r}; "
            f"allowed={sorted(_ALLOWED_READ_MODES)}"
        )
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
Test 5d (R43) asserts `tokenize_v1("Stress_Concentration in Risers") == ["stress_concentration", "in", "risers"]` — pins underscore preservation.
Test 5e (R47) asserts `safe_open(any_path, "w")` raises `ValueError` and the message names `mode` — pins read-only narrowing.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/knowledge/run_batch_pack_2.py | runner: domain classification + topic clustering (underscore filename so tests can import; lives outside any hyphen-named directory per R28/R42) |
| Create | scripts/knowledge/pin_stopwords_sha.py | one-shot SHA pin script (R15); rewrites `STOPWORDS_SHA` constant in runner |
| Create | scripts/knowledge/eval_cluster_quality.py | optional non-blocking cluster-quality canary (R20) |
| Create | scripts/knowledge/data/stopwords_en_v1.txt | frozen stop-word list pinned by SHA in code |
| Create | tests/knowledge/test_batch_pack_2.py | TDD coverage (32 tests, see list — added 5d, 5e, 16b, 24a/24b split) |
| Create | docs/reports/batch-pack-2-conference-summary-stubs.md | primary output (topic stubs grouped by domain + wiki target + ISOPE proposed-issue body per R35) |
| Create | data/document-index/batch-pack-2-cross-link-candidates.jsonl | input for #2068; schema = Appendix A v1.2 |
| Create | data/document-index/batch-pack-2-skipped.jsonl | malformed-record sidecar |
| Update | docs/reports/llm-wiki-external-source-priority-queue.md | one-line footnote at §5.2 (R7) — anchor-guarded fallback per R22+R44 |
| Update | docs/reports/llm-wiki-staged-batch-packs.md | one-line footnote at §3.2 (R7) — anchor-guarded fallback per R22+R44 |
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
| 5d | test_tokenize_preserves_underscores | `tokenize_v1("Stress_Concentration in Risers") == ["stress_concentration", "in", "risers"]` (R43) | AC5 |
| 5e | test_safe_open_rejects_write_modes | `safe_open(any_path, "w")` raises `ValueError`; same for `"a"`, `"x"`, `"r+"` (R47) | AC4 |
| 6 | test_classify_paper_domain_pipeline_wins | "pipeline integrity" → primary=pipeline | AC5 |
| 6.5 | test_classify_riser_only_title_lands_in_pipeline | "Riser analysis" → (pipeline, []) per R36 | AC5 |
| 7 | test_classify_paper_domain_viv_with_riser_secondary | "VIV fatigue in deepwater risers" → (VIV, [pipeline]) per R14+R31 | AC5 |
| 7b | test_classify_returns_multiple_secondaries_on_tie | "VIV jumper fracture stress_concentration" → (VIV, [pipeline, structural]) per R31+R43 | AC5 |
| 8 | test_classify_returns_secondary_for_cross_domain | "VIV fatigue on pipelines" → (VIV, [pipeline]) per R14+R31 | AC5 |
| 9 | test_classify_paper_domain_default_misc | no keyword hit → (misc, []) | AC5 |
| 10 | test_cluster_preserves_paper_count_per_domain | sum(cluster.paper_count) == len(papers_in_domain) | AC3 |
| 11 | test_cluster_top_n_is_deterministic | same input → byte-identical top-N ordering | AC6 |
| 12 | test_tfidf_stopwords_sha_pinned | `STOPWORDS_SHA` matches sha256(file); `xfail` until `make pin-stopwords-sha` runs (R15) | AC6 |
| 13 | test_build_topic_stub_frontmatter_has_required_keys | stub has `title`,`tags`,`added`,`last_updated` | AC7 |
| 14 | test_build_topic_stub_provenance_is_list_of_paper_ids | each `sources:` resolvable to a phase_a record | AC8 |
| 15 | test_duplicate_check_detects_existing_wiki_page | existing wiki page with matching `sources:` flagged | AC9 |
| 16 | test_cross_link_jsonl_schema_secondary_domains_is_list | parser requires `secondary_domains: list[str]`; rejects single-string or `null` (R31) | AC10 |
| 16b | test_cross_link_jsonl_schema_rejects_misc_in_secondary | parser raises typed error for `secondary_domains: ["pipeline", "misc"]`; message names both `misc` and `secondary_domains` (R45) | AC10 |
| 17 | test_runner_is_idempotent_with_pinned_now | two runs with `--now 2026-01-01T00:00:00Z` produce byte-identical report + JSONL (R30) | AC6 |
| 18 | test_domain_to_target_wiki_table_all_allowed | every entry in DOMAIN_TARGET_WIKI maps to allowed set (R4) | AC12 |
| 19 | test_malformed_jsonl_row_is_skipped_not_crashed | malformed row → emitted to skipped.jsonl, run continues | AC3 |
| 20 | test_missing_phase_a_jsonl_raises_clear_error | absent file → typed exception with path in message | AC13 |
| 21 | test_unknown_indexing_status_value_warns | catalog with `indexing_status: in_progress` → WARN, treated as deferred | AC1 |
| 22 | test_empty_cluster_does_not_emit_stub | domain with zero papers produces no stub | AC3 |
| 23 | test_omae_subslice_perf_budget | OMAE-only run < 300s on developer machine; `pytest.mark.benchmark` (excluded from default bar; **informational reference per R46, not PR-blocking**) | AC14 |
| 24a | test_upstream_doc_footnote_at_anchor_when_present | fixture has §5.2/§3.2 anchor; footnote inserted at anchor location (R22+R44) | AC15 |
| 24b | test_upstream_doc_footnote_at_eod_when_anchor_missing | fixture has anchor stripped; footnote appended at end-of-doc (R22+R44) | AC15 |
| 25 | test_single_paper_domain_does_not_crash | bucket of N_d=1 → k clipped to 1, one stub emitted; N_d-clip wins over `cluster_count_min` (R23+R37) | AC3 |
| 26 | test_runner_exits_nonzero_on_record_drift | drift detector trips → `sys.exit(2)` (R25) | AC17 |
| 27 | test_isope_proposed_body_section_present_in_report | report contains `## ISOPE re-index follow-on (proposed body)` header with non-empty markdown body (R35) | AC13 |
| 28 | test_collections_flag_rejects_invalid_value | `--collections FOO` raises `ValueError` naming the invalid entry (R49) | AC18 |

(Total: 32 tests; v4 had 28.)

---

## Acceptance Criteria

| # | Criterion |
|---|---|
| AC1 | `uv run pytest tests/knowledge/test_batch_pack_2.py -v` — all default-bar tests pass (benchmark Test 23 excluded) |
| AC2 | After `make pin-stopwords-sha` has run (Runbook step 1), `uv run python scripts/knowledge/run_batch_pack_2.py` exits 0 and produces `docs/reports/batch-pack-2-conference-summary-stubs.md`, `data/document-index/batch-pack-2-cross-link-candidates.jsonl`, `data/document-index/batch-pack-2-skipped.jsonl` (R33) |
| AC3 | Output report records **DOT + OMAE + OTC** as processed and **ISOPE** as deferred with reason; `len(papers) + len(skipped) == 14180` (R17) when canonical full set is selected |
| AC4 | Runner never reads under `/mnt/ace/docs/conferences/` (Tests 5/5b/5c/5e; mechanism = scoped read-only `safe_open()` helper + CI grep per R32+R47) |
| AC5 | Classifier returns `(primary: str, secondary_domains: list[str])` per R14+R31; tokenizer pinned to `title_ascii_lower_alphanum_underscore_v1` regex `[a-z0-9_]+` per R43; worked-example fixtures pass (Tests 5d, 6, 6.5, 7, 7b, 8, 9) |
| AC6 | Two consecutive runs with `--now <fixed-ISO-8601>` produce byte-identical outputs (R30); stop-words SHA matches code constant after pin step |
| AC7 | Each stub frontmatter contains `title`, `tags`, `added`, `last_updated` |
| AC8 | Each stub records provenance as a list of phase-a record ids |
| AC9 | Duplicate-check flags overlapping existing wiki pages (does NOT auto-merge) |
| AC10 | Cross-link JSONL conforms to Appendix A schema v1.2; `secondary_domains` is `list[str]` (may be empty); `misc` not allowed in secondary slots (rejected at parse time per R45) |
| AC11a | No wiki pages promoted (`knowledge/wikis/**` read-only — verified by git diff scope) (R21) |
| AC11b | No files under `config/**`, `.claude/**` modified (R21) |
| AC12 | Each stub `target_wiki` in {engineering, marine-engineering, naval-architecture}; mapping table in code matches plan §Pseudocode |
| AC13 | Report contains `## ISOPE re-index follow-on (proposed body)` header with non-empty markdown body; user files manually (R35) — single branch, no auto-file |
| AC14 | **Informational reference benchmark only (not PR-blocking) per R46.** OMAE sub-slice completes in <5 min, full run in <15 min on the developer machine. Test 23 marked `pytest.mark.benchmark` (excluded from default bar). Promotion to PR-blocking deferred to a follow-on issue once a CI host profile is available. |
| AC15 | Both contradicting upstream docs carry a footnote pointing to the new report; anchor-present and anchor-missing branches independently verified (Tests 24a/24b per R22+R44) |
| AC16 | Review artifacts for all three providers posted to `scripts/review/results/` |
| AC17 | Runner exits non-zero (`sys.exit(2)`) if `len(papers) + len(skipped) != 14180` and the canonical full set was selected (R25; sub-slicing via `--collections` skips the drift gate per R49) |
| AC18 | `--collections` accepts subsets of `{DOT, OMAE, OTC}`; defaults to canonical full set when omitted; raises `ValueError` on out-of-set values (Test 28 per R49) |

---

## Adversarial Review Summary

| Provider | v1 Verdict | v2 Verdict | v3 Verdict | v4 Verdict | v5 Verdict |
|---|---|---|---|---|---|
| Claude | MAJOR | MAJOR | MAJOR (P1: Attested Evidence placeholder, P1: idempotency vs `generated_at`, P1: builtins.open blast radius) | MAJOR (single P1: tokenizer/keyword contradiction) | PENDING |
| Codex | UNAVAILABLE (#2406) | UNAVAILABLE | UNAVAILABLE (codex-cli 0.124 stdin-hang regression — see `feedback_codex_cli_0_124_upstream_regression`) | UNAVAILABLE (same; see `feedback_codex_cli_0_124_upstream_regression`) | PENDING |
| Gemini | MINOR | MINOR | MAJOR (P1: Attested Evidence placeholder — REPEAT of r2 P1; P2: 3rd-domain silent-discard) | APPROVE (single P3: alphabetical-tie future-proofing) | PENDING |

**v4 → v5 revisions:** see Revision Log at top. Claude r4 P1 (tokenizer/keyword contradiction) addressed via R43 (rename + regex pin, user-confirmed option (a)). Claude r4 P2 items addressed via R44 (Test 24 split), R45 (misc-in-secondary rejection), R46 (AC14 informational downgrade with justification), R47 (safe_open mode-narrowing). Claude r4 P3 items addressed via R48 (re-attest with conference-phase-a-results.jsonl), R49 (--collections spec'd), R50 (schema-governance owner named). Gemini r4 P3 addressed via R51 (`+=` future-proofing + log line).

---

## Risks and Open Questions

- **Risk (inherited misstatement):** v1 deferred fixing the two upstream docs. v5 includes anchor-guarded one-line footnotes on each (R7+R22+R44; tested via 24a/24b).
- **Risk (OMAE scale):** OMAE alone has 7,292 titles. Stdlib-only TF-IDF with `max_vocab=2000`, single-pass farthest-first clustering, runs in `O(N x V) ~ 7292 x 2000 = 1.5e7` ops per domain — fits the <5 min informational budget by orders of magnitude on developer-class hardware (R18+R46).
- **Risk (classifier precision):** v5 uses weighted scoring (R14) so specialist signals (VIV) beat generic ones (marine). Tokenizer pinned with explicit regex per R43 so underscore-bearing keywords match cleanly. Worked examples for five fixtures inlined (Tests 5d, 6.5, 7, 7b, 8) for reviewer audit. Per-cluster confidence still surfaced per #2364 pattern.
- **Risk (PDF read-through):** scoped read-only `safe_open()` helper invariant (R32+R47) + CI grep + Tests 5/5b/5c/5e.
- **Risk (duplicate-check scope):** marine-engineering wiki has 19,191 pages. v5 uses `sources:` frontmatter index (incremental; built once, cached at startup); same approach as #2364.
- **Risk (cluster quality):** single-pass farthest-first can produce poor cohesion on large buckets (R20+R27). Mitigated by per-stub `cluster_quality_caveat` field + optional non-blocking `eval_cluster_quality.py` canary. #2068 consumers documented as warned-not-authoritative.
- **Risk (#2068 schema fork):** v5 keeps schema in Appendix A; when #2068 lands, it adopts. Schema versioning + migration shim documented. v4 bumped to `schema_version: 1.2` for `secondary_domains` list (R31). **Schema-governance owner (R50): #2369 owns the cross-link JSONL schema until #2068 lands. Once #2068 opens an amending PR, ownership transfers to #2068. Until that PR is open, schema changes go through this issue's plan-revision process.**
- **Risk (stopwords SHA pin step):** Test 12 starts as `xfail`; `make pin-stopwords-sha` flips it to `pass`. Documented in Runbook step 1 + Files-to-Change Makefile target.
- **Risk (idempotency seam):** Test 17 verifies byte-identical output ONLY when `--now` is fixed. Production runs (no `--now`) use runtime-now and are not byte-identical — by design (R30). Acceptance criterion AC6 is explicit about the fixed-now requirement.
- **Risk (perf-budget enforcement):** AC14 is informational reference only per R46 (no CI workflow exists; Test 23 runs on developer machine). A future agent must not over-read AC14 as a CI gate. Promotion to PR-blocking is deferred to a follow-on issue once a CI host profile is available.
- **Risk (collections sub-slicing):** when `--collections` selects a strict subset, the 14180-record drift gate (AC17) is skipped (per R49 + AC17 wording). This prevents false drift trips during dev iteration but means full-set runs are the only authoritative drift detection.
- **Open:** Should the report group stubs first by `target_wiki_domain` or by engineering-topic-domain? Defaults to topic-domain per spec §3.2 step 2.

---

## Complexity: T2

**T2** — new runner + TDD test module (32 tests) + report + JSONL cross-link artifact + JSONL skipped sidecar + 2 footnote edits to existing docs + SHA-pin one-shot script + optional cluster-quality eval; zero mods to wiki pages; reads only indexed JSONL/YAML (no PDFs); explicit readiness-mismatch reconciliation is the load-bearing correctness move; weighted classifier with worked examples and a tokenizer rename (R43) removes v4's single P1 contradiction; stdlib-only TF-IDF with full determinism contract removes v1's library ambiguity; cluster-quality caveat + optional eval canary mitigates Gemini's clustering-quality concern without taking on a new dependency; populated Attested Evidence (R29+R48) + `--now` injection (R30) + secondary_domains list (R31) + scoped read-only `safe_open` (R32+R47) + Test 24 split (R44) + misc-in-secondary parser test (R45) + AC14 downgrade with explicit justification (R46) + `--collections` spec (R49) + schema-governance owner (R50) + fallback `+=` (R51) close the v4 P1+P2+P3 set.

---

## Appendix A — Cross-Link JSONL Schema (v1.2, source-of-truth for #2369; #2068 will adopt; #2369 OWNS until #2068 opens an amending PR per R50)

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
| `secondary_domains` | list[enum] | yes | each item one of {`pipeline`,`subsea`,`VIV`,`hydrodynamics`,`marine`,`structural`}; `misc` excluded per R16; rejection of `misc` in this slot is enforced at parse time and pinned by Test 16b (R45); empty list `[]` when no secondary qualifies (NOT `null`) per R31 |
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

Validation: `tests/knowledge/test_batch_pack_2.py::test_cross_link_jsonl_schema_secondary_domains_is_list` round-trips each line through a `dataclass` parser; `secondary_domains` must be `list[str]` (single-string or `null` rejected); `test_cross_link_jsonl_schema_rejects_misc_in_secondary` (Test 16b per R45) ensures `misc` in this slot raises a typed error naming both `misc` and `secondary_domains` in the message; any other field missing or type-mismatched also fails.

#2068 integration note: when #2068 implements the cross-link generator, it consumes this JSONL as input. Schema changes after this issue lands require a `schema_version` bump and a migration note in #2068's plan. Schema ownership: **#2369 owns the schema until #2068 lands; on #2068 opening an amending PR, ownership transfers to #2068** (R50). v3→v4 schema bump (1.1→1.2) is documented above as the precedent.
