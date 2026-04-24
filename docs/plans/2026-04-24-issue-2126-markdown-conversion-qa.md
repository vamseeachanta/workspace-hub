# Plan for #2126: test(llm-wiki): validate markdown conversion quality across all 717 topics

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2126
> **Review artifacts:** scripts/review/results/2026-04-24-plan-2126-claude.md | ...-codex.md | ...-gemini.md (pending — cross-review infrastructure currently blocked per batch-coordination note)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/llm-wiki/ingest-orcina.py` lines 98-259 — `html_to_markdown()` + `_convert_element()` + `_convert_table()` will be the single canonical conversion surface under test. It emits a `<!-- source: URL -->` header, strips `script/style/nav/footer/header/link/meta/noscript` and MadCap `MCBreadcrumbs*`/`MCMiniTocBox_0`/`MCRelatedTopics` containers, and preserves heading levels, `<p>` inline mixing (`strong|b`, `em|i`, `code`, `a`, `br`, `img`), `ul/ol` (non-nested, non-recursive — see line 192 `recursive=False`), `table` via `_convert_table`, `pre` as fenced code, `dl`/`dt`/`dd` as definition terms, and a top-level `<hr>` → `---`.
- Found: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` (186 lines) — existing pytest harness pattern. It already solves the hyphenated-package import problem (`sys.path.insert(0, scripts/data/llm-wiki/)` at lines 22-26) and demonstrates fixture-driven isolation with `tmp_path`, `monkeypatch`, and `patch.object(mod, "REPO_ROOT", tmp_repo)`. The new conversion-QA module will reuse this sys.path bootstrap to import `ingest-orcina` as `ingest_orcina` (hyphen → underscore) via `importlib.util.spec_from_file_location`, because the current filename contains a hyphen that blocks plain `import`.
- Found: `scripts/data/llm-wiki/tests/__init__.py` (empty) — test package anchor already exists.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — resolves topic-corpus root via env var → `config/llm-wiki.yaml` → `${REPO_ROOT}/data/llm-wiki` → `${REPO_ROOT}/knowledge/wikis`. This plan will NOT read the live 717-topic corpus from disk; it will ship self-contained HTML fixtures so all assertions execute without network or machine-specific symlinks.
- Gap: no `html_to_markdown` quality test exists anywhere under `scripts/data/llm-wiki/tests/`, `tests/`, or `knowledge/`. The ingestion surface has been production-running since #2088 without oracle-backed regression coverage.

### Standards
Not applicable — the conversion rubric is domain (MadCap Flare HTML → markdown), not an engineering standard. No entry in `data/document-index/standards-transfer-ledger.yaml` applies.

### LLM Wiki pages consulted
- Not directly applicable — this plan tests the *ingestion surface that produces* the marine-engineering/naval-architecture wikis, not the wiki content itself. `knowledge/wikis/` does contain the downstream consumers (`marine-engineering/`, `naval-architecture/`, `engineering/`), but the 717-topic corpus referenced in the issue title is an out-of-tree artifact (see Evidence section).

### Documents consulted
- Issue body #2126 — lists 6 quality checks (table fidelity, formula preservation, cross-reference links, image alt text, code blocks, encoding), specifies a **sample-20 protocol across 5 categories** (introduction, data, theory, results, API), and names `scripts/data/llm-wiki/ingest-orcina.py` as the converter and `data/llm-wiki/orcaflex/topics/` + `data/llm-wiki/orcawave/topics/` as the sample sources.
- Parent #2088 (CLOSED) — feat issue that shipped `ingest-orcina.py`; Orcina webhelp totals referenced in #2126 title (717 topics) correspond to the `parse_toc_xml` crawl output under `data/llm-wiki/{orcaflex,orcawave,orcfxapi}/topics/`.
- Sibling #2141 (OPEN) — "Add fixture-backed tests for llm-wiki ingest and search scripts." Explicitly requests "Fixture-based ingestion tests for sample HTML/markdown inputs" and "small smoke test for end-to-end index build + search on fixture content." This plan executes the conversion-quality slice of that fixture work; #2141 remains for the search-side coverage and schema/ranking tests.
- Sibling #2476 (OPEN) — "docs(llm-wiki): add canonical spec semantic-equivalence contract and fixture cookbook." Will codify shared fixture layout. This plan adopts the fixture root `tests/fixtures/llm-wiki/conversion-oracle/` so #2476's cookbook can absorb or link it without a move.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — parent operating model. The conversion-QA module is an intelligence-quality instrument under that umbrella (verifies surface fidelity of the ingestion step).
- `data/document-index/intelligence-accessibility-registry.yaml` lines 342-349 — confirms the llm-wiki operating model has an accessibility entry; this plan does NOT add a new registry entry because test modules are transient infrastructure, not durable intelligence surfaces per #2209's durable-vs-transient boundary.
- `data/document-index/online-resource-registry.yaml` lines 2187-2223 — Orcina webhelp sources already registered (`orcina_com_webhelp_orcaflex_*`). Fixtures in this plan will be derived by fetching + snapshotting these pages once, NOT by re-crawling on every test run.
- `docs/plans/README.md` lines 53 (retrieval-contract table, `cat:data-pipeline`) — requires `registry.yaml`, pipeline config, `resource-intelligence-maturity.yaml` to be consulted. Status below.

### Data-Pipeline retrieval contract (`cat:data-pipeline`)
| Required source | Consulted | Finding |
|---|---|---|
| `data/document-index/registry.yaml` | YES | Search for `llm-wiki`/`orcina`/`html_to_markdown` returned no matches. The ingestion pipeline is not yet registered. Gap: pipeline registration is out of scope for this test-only plan; flag as follow-up for #2141 or a new entry under the #2205 operating model. |
| Pipeline config (`config/data/pipeline-manifest.yaml`) | YES | File contains `pipelines: {}` only — no llm-wiki entry. Same gap as above. |
| `data/document-index/resource-intelligence-maturity.yaml` | YES | Search for `llm-wiki`/`orcina` returned no matches; no maturity-tier row exists. Gap noted; not extended by this plan because maturity tracks intelligence-surface durability, not test coverage. |

### Gaps identified
- No existing conversion-quality test module under `scripts/data/llm-wiki/tests/`.
- No oracle markdown fixtures exist for any of the 717 topics.
- No stratified sampler exists — the issue references "sample 20 across categories" but provides no selection algorithm; this plan must define one.
- `llm-wiki` ingestion is not in `registry.yaml`, `pipeline-manifest.yaml`, or `resource-intelligence-maturity.yaml` — flagged as follow-up, not scoped here.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2126` — OPEN — test(llm-wiki): validate markdown conversion quality across all 717 topics
- `#2088` — CLOSED — feat(llm-wiki): ingest OrcaFlex, OrcaWave, and OrcFxAPI online help into llm-wiki
- `#2140` — CLOSED — Replace tracked absolute llm-wiki symlink with portable path resolution and smoke tests
- `#2141` — OPEN — Add fixture-backed tests for llm-wiki ingest and search scripts
- `#2476` — OPEN — docs(llm-wiki): add canonical spec semantic-equivalence contract and fixture cookbook

**File existence** (`ls -la` 2026-04-24):
- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py` (637 lines, canonical conversion surface)
- EXISTS: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` (existing pattern)
- EXISTS: `scripts/data/llm-wiki/tests/__init__.py` (empty package anchor)
- EXISTS: `scripts/data/llm-wiki/resolve_wiki_path.py`
- MISSING (gitignored per `.gitignore:445`): `data/llm-wiki/` — runtime corpus root, not in-repo.
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/test_conversion_quality.py`
- MISSING (new — this plan creates): `scripts/data/llm-wiki/tests/fixtures_sampling.py`
- MISSING (new — this plan creates, 20 files): `tests/fixtures/llm-wiki/conversion-oracle/*.{html,md,json}`

**Line excerpts** (`sed -n 98,132p scripts/data/llm-wiki/ingest-orcina.py`):
```
def html_to_markdown(html_content: str, source_url: str = "") -> tuple[str, str]:
    """Convert HTML to markdown using BeautifulSoup. Returns (title, markdown)."""
    soup = BeautifulSoup(html_content, "html.parser")
    ...
    if source_url:
        markdown = f"<!-- source: {source_url} -->\n\n{markdown}"
    return title, markdown
```

**Gap proofs**:
- `grep -n "llm-wiki\|orcina" config/data/pipeline-manifest.yaml` → empty
- `grep -rn "llm-wiki\|orcina" data/document-index/registry.yaml` → empty
- `grep -n "llm-wiki\|orcina" data/document-index/resource-intelligence-maturity.yaml` → empty
- `find scripts/data/llm-wiki/tests -name "test_conversion*"` → empty
- `ls .gitignore | grep llm-wiki` → `data/llm-wiki` (line 445) — confirms corpus is out-of-tree and fixtures MUST be committed separately.

**Source count:** Issue #2126 body + `ingest-orcina.py` + `test_resolve_wiki_path.py` + `docs/plans/README.md` + 3 data-pipeline contract files + 3 related issues (#2088, #2141, #2476) + `online-resource-registry.yaml` = 10 distinct sources (≥3 required).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-2126-markdown-conversion-qa.md` |
| Test module | `scripts/data/llm-wiki/tests/test_conversion_quality.py` |
| Sampling helper | `scripts/data/llm-wiki/tests/fixtures_sampling.py` |
| Oracle fixtures | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` + `{slug}.md` |
| Stratification manifest | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` |
| Rubric report (generated) | `scripts/data/llm-wiki/tests/.artifacts/conversion-quality-report.json` (gitignored) |
| Plan review — Claude | `scripts/review/results/2026-04-24-plan-2126-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-24-plan-2126-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-24-plan-2126-gemini.md` |

---

## Deliverable

A self-contained pytest module `test_conversion_quality.py` plus 20 oracle-backed HTML/markdown fixtures under `tests/fixtures/llm-wiki/conversion-oracle/` that will execute `html_to_markdown()` on stratified topics and score each output against six rubric dimensions, failing the run if any dimension falls below a published threshold.

---

## Pseudocode

```
# test_conversion_quality.py
def load_sample_manifest():
    read tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml
    assert len(entries) == 20
    assert stratification counts match product/category/complexity budgets
    return entries

@pytest.mark.parametrize("entry", load_sample_manifest())
def test_per_topic_conversion(entry):
    html = read entry.html_path
    expected_md = read entry.oracle_md_path
    actual_title, actual_md = ingest_orcina.html_to_markdown(html, entry.source_url)
    dimensions = score_rubric(actual_md, expected_md, html)
    write per-dimension scores to .artifacts/per-topic/<slug>.json
    for dim in RUBRIC_DIMENSIONS:
        assert dimensions[dim] >= PER_TOPIC_THRESHOLD[dim], explain(dim)

def test_aggregate_rubric_thresholds():
    read .artifacts/per-topic/*.json
    for dim in RUBRIC_DIMENSIONS:
        aggregate = mean(topic.scores[dim] for topic in all_topics)
        assert aggregate >= AGGREGATE_THRESHOLD[dim]
    write .artifacts/conversion-quality-report.json

# score_rubric(actual_md, expected_md, html)
    heading_preservation: compare ordered list of ^#{1,6} tokens from actual vs oracle, Jaccard+order penalty
    link_resolution: parse [text](href) from actual, verify count + hrefs match oracle allow-list
    table_fidelity: parse markdown tables (| ... |) from actual, compare cell grid to oracle grid (exact cell text match, order-sensitive)
    code_block_fidelity: compare fenced ```...``` blocks — count, language tag, body equal after normalizing trailing whitespace
    image_alt_text: parse ![alt](src) tokens, require non-empty alt OR alt matches oracle (documents bugs without silencing)
    list_nesting: count top-level + indented bullets; oracle encodes expected nesting shape as a tree of depths
    return {dim: float 0..1}
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/tests/test_conversion_quality.py` | pytest module — per-topic + aggregate rubric assertions |
| Create | `scripts/data/llm-wiki/tests/fixtures_sampling.py` | stratified-sampling logic + manifest schema validator; importable from both the test module and a CLI helper |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` | declares the 20 selected topics, their product/category/complexity tiers, and source URLs |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` × 20 | frozen HTML snapshots fetched once from orcina.com |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.md` × 20 | oracle markdown — manually reviewed reference conversion for each snapshot |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/README.md` | describes fixture provenance, refresh policy, and oracle-authoring checklist |
| Modify | `.gitignore` | add `scripts/data/llm-wiki/tests/.artifacts/` so generated reports stay out of git |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## Stratification strategy

Sample 20 topics from the 717-topic corpus using three orthogonal axes, then intersect. Selection is **deterministic** — the manifest pins exact topics so a reviewer can reproduce.

**Axis 1 — Product** (3 levels, proportional to TOC counts):
- OrcaFlex: 12 topics (largest product)
- OrcaWave: 5 topics
- OrcFxAPI: 3 topics

**Axis 2 — Topic category** (5 levels, from issue body; target ≥3 products per category where possible):
- introduction (concept/overview pages): 4 topics
- data (parameter/input-form pages with tables): 5 topics
- theory (equations/formulas): 4 topics
- results (output/plot pages): 3 topics
- API (OrcFxAPI reference pages with code blocks): 4 topics

**Axis 3 — Complexity tier** (3 levels, used to force hard cases into the sample):
- Simple (plain prose, ≤1 table, ≤5 links): 6 topics
- Medium (multi-section, ≥2 tables OR nested lists): 8 topics
- Hard (formulas with special chars, cross-references, code blocks, images with alt): 6 topics

The manifest schema encodes all three axes per entry and `fixtures_sampling.py` validates at test-collection time that the bucket budgets are met (fails loudly if the manifest drifts).

---

## Rubric dimensions and thresholds

| # | Dimension | Per-topic threshold | Aggregate threshold | Measurement |
|---|---|---|---|---|
| 1 | Heading preservation | ≥0.90 | ≥0.95 | Jaccard over ordered (level, text) tuples + order penalty |
| 2 | Link resolution | ≥0.90 | ≥0.95 | \|actual href set ∩ oracle href set\| / \|oracle href set\| |
| 3 | Table fidelity | ≥0.85 | ≥0.95 | cell-level exact match over flattened row-major grid |
| 4 | Code-block fidelity | ≥0.90 | ≥0.95 | block count match AND body equality after whitespace normalization |
| 5 | Image alt-text | ≥0.80 | ≥0.95 | fraction of images whose alt equals oracle (non-empty preferred; empty-but-matching-oracle counts as neutral, not failure) |
| 6 | List nesting | ≥0.85 | ≥0.95 | tree-edit distance between actual and oracle depth-trees, normalized |

**Why per-topic < aggregate on table/code/list:** those dimensions have high variance on edge-case pages; a single hard topic can legitimately score 0.85 while the aggregate stays ≥0.95. Thresholds are tuned to catch systematic regressions without punishing acceptable local fidelity loss.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_sample_manifest_loads` | manifest file exists, parses, contains exactly 20 entries | `sample-manifest.yaml` | 20 entries, all fields present |
| `test_sample_manifest_stratification` | bucket budgets match declared policy | loaded manifest | product/category/complexity counts satisfy quotas |
| `test_sample_manifest_fixture_files_exist` | every manifest entry has both `.html` and `.md` sidecars | manifest | all 40 files resolvable, non-empty |
| `test_html_to_markdown_import` | canonical converter is importable from hyphenated path | — | `ingest_orcina.html_to_markdown` callable |
| `test_per_topic_heading_preservation[slug]` × 20 | per-topic dim 1 meets per-topic threshold | (html, oracle_md) | score ≥ 0.90 |
| `test_per_topic_link_resolution[slug]` × 20 | per-topic dim 2 | " | score ≥ 0.90 |
| `test_per_topic_table_fidelity[slug]` × 20 | per-topic dim 3 | " | score ≥ 0.85 |
| `test_per_topic_code_block_fidelity[slug]` × 20 | per-topic dim 4 | " | score ≥ 0.90 |
| `test_per_topic_image_alt_text[slug]` × 20 | per-topic dim 5 | " | score ≥ 0.80 |
| `test_per_topic_list_nesting[slug]` × 20 | per-topic dim 6 | " | score ≥ 0.85 |
| `test_aggregate_rubric_meets_thresholds` | aggregate means across all 20 topics | per-topic JSON artifacts | every dimension mean ≥ 0.95 |
| `test_no_network_access` | assertions never hit orcina.com | monkeypatched `urllib.request.urlopen` | zero calls |
| `test_report_artifact_written` | the `conversion-quality-report.json` is produced and schema-valid | test run exit | file present, keys conform |

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_conversion_quality.py -v` passes with exit 0 and at least 125 collected items (13 structural tests + 120 parametrized `[slug]` cases).
- [ ] 20 `.html` + 20 `.md` oracle pairs exist under `tests/fixtures/llm-wiki/conversion-oracle/` and are tracked by `git ls-files`.
- [ ] `sample-manifest.yaml` explicitly declares each topic's product, category, and complexity tier; `fixtures_sampling.py` validates the stratification budgets and fails on drift.
- [ ] `scripts/data/llm-wiki/tests/.artifacts/conversion-quality-report.json` is produced on every run and contains per-dimension per-topic scores plus the six aggregate means.
- [ ] All six rubric dimensions have published per-topic AND aggregate thresholds (see table above); report format documented in module docstring.
- [ ] Tests run offline (no network) — enforced by `test_no_network_access`.
- [ ] No regression: `uv run pytest scripts/data/llm-wiki/tests/ -v` passes (both existing `test_resolve_wiki_path.py` and new module).
- [ ] Review artifacts posted to `scripts/review/results/` (deferred — cross-review infrastructure currently blocked; will attach once infrastructure restored).

---

## Non-goals (explicit)

- **Not** fixing any conversion bug that the rubric surfaces. Every bug becomes a separate issue; this plan ships only the diagnostic instrument.
- **Not** rewriting, refactoring, or extending `html_to_markdown`/`_convert_element`/`_convert_table`. Scope is test/QA only.
- **Not** testing supplementary pages (`scripts/data/llm-wiki/ingest-orcina.py:415-451`) or PDF papers (`ingest_papers` at line 458). Per issue body — topic pages only (the 717-topic figure in the title).
- **Not** testing the full 717 topics — the issue explicitly scopes this to a sample-20 protocol. Full-corpus QA is a separate (heavier) follow-up.
- **Not** updating `registry.yaml`, `pipeline-manifest.yaml`, or `resource-intelligence-maturity.yaml` — the ingestion pipeline needs registration, but that is a separate governance task (flag as follow-up comment on #2126 or a new issue).
- **Not** touching `search-wiki.py` — #2141 covers search-side test coverage.

---

## Adversarial Review Summary

*(Pending — cross-review infrastructure reported broken for the 2026-04-23/24 batch. Section to be populated once three-provider review runs; plan will not be marked `status:plan-review` until reviews complete.)*

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | pending |
| Codex | — | pending |
| Gemini | — | pending |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk (fixture drift):** Oracle markdown is authored manually. If reviewers disagree on the "correct" rendering of a complex table, the oracle itself becomes the bug. Mitigation — the fixture README documents a two-reviewer sign-off requirement on every oracle file before merge.
- **Risk (orcina.com content change):** HTML snapshots may diverge from live pages over time, making the fixtures stale. Mitigation — snapshot provenance (URL + fetch timestamp + content SHA) is recorded in `sample-manifest.yaml`; a periodic refresh job is out of scope but noted as a follow-up for #2125 (auto-refresh-on-release).
- **Risk (false green on dim 5):** Image alt-text dim can pass trivially if both actual and oracle have empty alts. Per-topic threshold 0.80 with the "non-empty preferred" note in the rubric is a soft guard; a sterner policy would be to require ≥50% of images to carry non-empty alt, but doing so would demand upstream content fixes that #2126 is scoped to diagnose, not solve.
- **Open:** Should the stratification also cover **encoding edge cases** (UTF-8 Greek letters in formulas, degree signs, math operators)? The issue's check #6 explicitly calls this out. Recommendation — reserve at least 2 of the 6 "Hard" tier slots for formula-heavy topics where such characters appear. Flag for user confirmation during approval.
- **Open:** Should the report output path `scripts/data/llm-wiki/tests/.artifacts/` be co-located with tests or hoisted to a repo-wide `.artifacts/` directory? Current placement keeps test outputs scoped; flag for user.
- **Open:** Cross-reference link resolution (dim 2) — should we accept relative links that match the oracle's pattern even if the target topic is not in the sample? Current thinking: yes (the rubric measures conversion fidelity, not end-to-end link validity). Resolving cross-topic references is out of scope.

---

## Complexity: T2

**T2** — new test module with helper, 20 fixture pairs, one manifest, and a gitignore touch. No production code modified; TDD required; deterministic and offline. Falls cleanly into "new module with multiple files" per the template guide.
