# Plan for #2126: test(llm-wiki): validate markdown conversion quality across all 717 topics

> **Status:** draft (v2 — addresses r1 findings)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2126
> **Base commit:** `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` (live-state claims anchored to this SHA)
> **Review artifacts:**
> - r1 Claude (MAJOR): `scripts/review/results/20260424T150953Z-plan-2126.md-plan-claude.md`
> - r1 Gemini (MINOR): `scripts/review/results/20260424T151456Z-plan-2126.md-plan-gemini.md`
> - r1 Codex: not produced (codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression`)
> - r2 artifacts: pending; revision-bound to this v2 (path and SHA to be recorded below once reviews land)

---

## Changes from v1 (summary)

This v2 resolves all three P1 findings from the r1 Claude review, the four P2 findings (two from Claude, two from Gemini's implicit asks about stratification and reviewer conflict), and the two P3 findings. Past-tense artifact language has been removed throughout. An Attested Evidence block replaces the prior embedded-verification prose.

| Finding | Severity | Resolution chosen |
|---|---|---|
| Parametrize arithmetic off-by-20 | P1 | Structural test count raised to **13** by adding six explicit structural tests (enumerated in TDD list). AC asserts `pytest --collect-only` yields exactly **133 = 13 + 120** items. |
| Per-topic/aggregate threshold contradiction | P1 | Aggregate-mean rule **dropped**. Replaced with a floor-occupancy rule: *"on any dimension, at most 2 of 20 topics may score below the per-topic floor, and zero may score below 0.70."* Math is provably consistent (no mean/floor ordering trap). |
| Stratification over-constrained | P1 | Relaxed to **marginal-only**. Each axis's marginal counts are honored independently; joint cells are not constrained. Validator checks marginals only. |
| Oracle authorship circularity | P2 | Blinding protocol pinned: oracle authored from raw HTML + published-target rendering guidance, without viewing converter output. Schema field `oracle_review_method` (`from-source` \| `reviewed-from-output`) logs the method per entry; CI fails any `reviewed-from-output` row. |
| Rubric formulas under-specified | P2 | Explicit formulas locked for all six dimensions (see Rubric section). Two implementers given the same inputs MUST produce bit-identical scores. |
| `test_no_network_access` trivially passes | P2 | Replaced urlopen monkeypatch with `pytest-socket`'s `disable_socket` autouse session-scoped fixture + an active probe asserting `socket.socket()` raises `SocketBlockedError`. |
| Review-artifact AC vs revision-bound gate | P3 | Moved to a "Deferred / conditional" subsection with explicit unblock condition. Plan will not enter `status:plan-review` until r2 reviews land under this v2's commit SHA. |
| Provenance fields missing from schema | P3 | `source_url`, `fetched_at` (ISO-8601 UTC), `html_sha256`, `oracle_authored_by`, `oracle_review_method` are now **required** manifest fields; validator test rejects any missing field. |

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/data/llm-wiki/ingest-orcina.py` lines 98-259 — `html_to_markdown()` + `_convert_element()` + `_convert_table()` are the single canonical conversion surface under test. It emits a `<!-- source: URL -->` header, strips `script/style/nav/footer/header/link/meta/noscript` and MadCap `MCBreadcrumbs*`/`MCMiniTocBox_0`/`MCRelatedTopics` containers, and preserves heading levels, `<p>` inline mixing (`strong|b`, `em|i`, `code`, `a`, `br`, `img`), `ul/ol` (non-nested, non-recursive — see line 192 `recursive=False`), `table` via `_convert_table`, `pre` as fenced code, `dl`/`dt`/`dd` as definition terms, and a top-level `<hr>` → `---`.
- `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` (186 lines) — existing pytest harness pattern. It already solves the hyphenated-package import problem (`sys.path.insert(0, scripts/data/llm-wiki/)` at lines 22-26) and demonstrates fixture-driven isolation with `tmp_path`, `monkeypatch`, and `patch.object(mod, "REPO_ROOT", tmp_repo)`. The new conversion-QA module will reuse this sys.path bootstrap to import `ingest-orcina` as `ingest_orcina` via `importlib.util.spec_from_file_location`.
- `scripts/data/llm-wiki/tests/__init__.py` (empty) — test package anchor already exists.
- `scripts/data/llm-wiki/resolve_wiki_path.py` — resolves topic-corpus root; NOT used by this plan at run time because fixtures are self-contained.
- Gap: no `html_to_markdown` quality test exists under `scripts/data/llm-wiki/tests/`, `tests/`, or `knowledge/`. The ingestion surface has been production-running since #2088 without oracle-backed regression coverage.

### Standards
Not applicable — conversion fidelity is a domain rubric (MadCap Flare HTML → markdown), not an engineering standard.

### LLM Wiki pages consulted
Not directly applicable — this plan tests the ingestion surface producing wiki content, not the wiki content itself.

### Documents consulted
- Issue body #2126 — 6 quality checks, sample-20 protocol, 5 categories.
- Parent #2088 (CLOSED) — shipped `ingest-orcina.py`; Orcina webhelp totals correspond to `data/llm-wiki/{orcaflex,orcawave,orcfxapi}/topics/`.
- Sibling #2141 (OPEN) — fixture-backed tests for llm-wiki ingest and search scripts (this plan covers the conversion-quality slice; search-side remains).
- Sibling #2476 (OPEN) — canonical spec semantic-equivalence contract + fixture cookbook; this plan adopts `tests/fixtures/llm-wiki/conversion-oracle/` so #2476 can link/absorb.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — parent operating model.
- `data/document-index/intelligence-accessibility-registry.yaml` lines 342-349 — llm-wiki accessibility entry exists; no new registry row added (transient test infra per #2209 boundary).
- `data/document-index/online-resource-registry.yaml` lines 2187-2223 — Orcina webhelp sources already registered.
- `docs/plans/README.md` retrieval contract (`cat:data-pipeline`) — status table below.

### Data-Pipeline retrieval contract (`cat:data-pipeline`)
| Required source | Consulted | Finding |
|---|---|---|
| `data/document-index/registry.yaml` | YES | No match for `llm-wiki`/`orcina`/`html_to_markdown`. Ingestion pipeline unregistered. Gap flagged as follow-up; not scoped here. |
| `config/data/pipeline-manifest.yaml` | YES | File contains `pipelines: {}` only. Same gap. |
| `data/document-index/resource-intelligence-maturity.yaml` | YES | No llm-wiki row. Gap flagged; not extended. |

### Gaps identified
- No conversion-quality test module exists.
- No oracle markdown fixtures exist for any topic.
- No stratified sampler exists.
- `llm-wiki` ingestion is absent from registry / pipeline-manifest / maturity ledger — flagged as follow-up, not scoped here.

---

## Attested Evidence

Claims below are independently verifiable and anchored to base commit `8c235f5e4a02a5ce633f43578b7335e30a53fb4b`. Each claim is stated with the verification command so a reviewer can reproduce.

**Issue statuses** (verify via `gh issue view <N> --json number,state,title`):
- `#2126` — expected OPEN — `test(llm-wiki): validate markdown conversion quality across all 717 topics`
- `#2088` — expected CLOSED — `feat(llm-wiki): ingest OrcaFlex, OrcaWave, and OrcFxAPI online help into llm-wiki`
- `#2140` — expected CLOSED — portable path resolution + smoke tests
- `#2141` — expected OPEN — fixture-backed tests for llm-wiki ingest and search scripts
- `#2476` — expected OPEN — canonical spec semantic-equivalence contract and fixture cookbook

**File existence at HEAD = 8c235f5e** (verify via `git ls-files <path>` or `git show HEAD:<path> | wc -l`):
- `scripts/data/llm-wiki/ingest-orcina.py` — present, 637 lines
- `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` — present, 186 lines
- `scripts/data/llm-wiki/tests/__init__.py` — present, 0 bytes
- `scripts/data/llm-wiki/resolve_wiki_path.py` — present

**Gap proofs** (verify via the shown command):
- `git grep -n "llm-wiki\|orcina" -- config/data/pipeline-manifest.yaml` → expected empty
- `git grep -n "llm-wiki\|orcina" -- data/document-index/registry.yaml` → expected empty
- `git grep -n "llm-wiki\|orcina" -- data/document-index/resource-intelligence-maturity.yaml` → expected empty
- `git ls-files scripts/data/llm-wiki/tests/ | grep -c conversion` → expected 0
- `git ls-files .gitignore | xargs grep -n llm-wiki` → expected to show `data/llm-wiki` ignored

**Tooling availability** (verify via `python -c "import X"` under `uv run`):
- `pytest-socket` is the chosen network-block harness; it is not yet in `pyproject.toml` dependencies and MUST be added during implementation. The plan flags this as a concrete install step, not an assumption.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-2126-markdown-conversion-qa.md` |
| Test module | `scripts/data/llm-wiki/tests/test_conversion_quality.py` |
| Sampling helper | `scripts/data/llm-wiki/tests/fixtures_sampling.py` |
| Rubric scorer helper | `scripts/data/llm-wiki/tests/rubric_scorers.py` |
| Oracle fixtures | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` + `{slug}.md` |
| Stratification manifest | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` |
| Manifest JSON Schema | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` |
| Oracle authoring checklist | `tests/fixtures/llm-wiki/conversion-oracle/README.md` |
| Rubric report (generated, gitignored) | `scripts/data/llm-wiki/tests/.artifacts/conversion-quality-report.json` |
| Plan review r2 — Claude | `scripts/review/results/<stamp>-plan-2126-v2.md-plan-claude.md` |
| Plan review r2 — Codex | `scripts/review/results/<stamp>-plan-2126-v2.md-plan-codex.md` (conditional on codex-cli fix) |
| Plan review r2 — Gemini | `scripts/review/results/<stamp>-plan-2126-v2.md-plan-gemini.md` |

---

## Deliverable

A self-contained pytest module `test_conversion_quality.py` plus 20 oracle-backed HTML/markdown fixtures under `tests/fixtures/llm-wiki/conversion-oracle/` that will execute `html_to_markdown()` on stratified topics, score each output against six rubric dimensions with locked formulas, and fail the run when the floor-occupancy rule is violated. Strict offline enforcement via `pytest-socket`. Oracle authorship blinded from current converter output.

---

## Pseudocode

```
# test_conversion_quality.py

@pytest.fixture(scope="session", autouse=True)
def _disable_network(request):
    from pytest_socket import disable_socket, SocketBlockedError
    disable_socket(allow_unix_socket=False)
    # active probe: verify the block is live
    with pytest.raises(SocketBlockedError):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def load_sample_manifest():
    read tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml
    validate against sample-manifest.schema.json (required fields enforced)
    assert len(entries) == 20
    assert each axis marginal matches declared quota (axis-independent; no joint constraint)
    assert every entry.oracle_review_method == "from-source"
    return entries

@pytest.mark.parametrize("entry", load_sample_manifest(), ids=lambda e: e["slug"])
@pytest.mark.parametrize("dim", RUBRIC_DIMENSIONS)
def test_per_topic_dimension(entry, dim):
    html = read entry.html_path
    expected_md = read entry.oracle_md_path
    _, actual_md = ingest_orcina.html_to_markdown(html, entry.source_url)
    score = SCORERS[dim](actual_md, expected_md, html)  # locked formula per dim
    write {slug, dim, score} to .artifacts/per-topic/<slug>-<dim>.json
    # NOTE: per-topic floor is NOT asserted here; the aggregation test enforces
    # the floor-occupancy rule so a single dipped topic does not fail the run.

def test_aggregate_floor_occupancy():
    read .artifacts/per-topic/*.json, group by dim
    for dim in RUBRIC_DIMENSIONS:
        below_floor = [s for s in scores[dim] if s < PER_TOPIC_FLOOR[dim]]
        below_hard  = [s for s in scores[dim] if s < HARD_MIN[dim]]
        assert len(below_floor) <= MAX_BELOW_FLOOR[dim]   # 2 of 20 by default
        assert len(below_hard)  == 0                       # zero tolerance for <0.70
    write .artifacts/conversion-quality-report.json
```

Formula pseudocode for composite scorers is given in the "Rubric dimensions and formulas" section below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/tests/test_conversion_quality.py` | pytest module — per-topic scoring + aggregate floor-occupancy + structural tests |
| Create | `scripts/data/llm-wiki/tests/fixtures_sampling.py` | marginal-quota validator + manifest schema loader |
| Create | `scripts/data/llm-wiki/tests/rubric_scorers.py` | six pure-function scorers implementing locked formulas |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` | 20-entry manifest with full provenance fields |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` | JSON Schema enforcing required fields; referenced by validator |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` × 20 | frozen HTML snapshots |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.md` × 20 | oracle markdown — from-source authorship only |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/README.md` | blinding protocol + conflict-resolution procedure |
| Modify | `.gitignore` | add `**/.artifacts/` repo-wide (per Gemini r1 suggestion, keeps convention uniform) |
| Modify | `pyproject.toml` / test-deps | add `pytest-socket` to the dev/test dependency group |
| Update | `docs/plans/README.md` | index this plan |

---

## Stratification strategy (marginal-only)

Sample 20 topics from the 717-topic corpus using three axes. **Each axis's marginal counts are validated independently; joint cells are not constrained.** A 3×5×3 = 45-cell joint cannot be honored by 20 samples, and the plan does not attempt to. Selection is deterministic via the pinned manifest.

**Axis 1 — Product marginal** (sums to 20):
- OrcaFlex: 12; OrcaWave: 5; OrcFxAPI: 3

**Axis 2 — Topic-category marginal** (sums to 20):
- introduction: 4; data: 5; theory: 4; results: 3; API: 4

**Axis 3 — Complexity-tier marginal** (sums to 20):
- Simple: 6; Medium: 8; Hard: 6

**Hard-tier reservation** (addressing Gemini P3): **at least 2 of the 6 Hard slots MUST be formula-heavy pages** (UTF-8 Greek letters, degree signs, math operators) so the encoding check #6 from the issue body is exercised. The manifest field `encoding_stress: bool` flags these and the validator asserts `sum(encoding_stress) >= 2 within complexity == "Hard"`.

**`fixtures_sampling.py` validates**:
1. total entries == 20
2. three axis marginals match the quotas above
3. Hard-tier encoding_stress count >= 2
4. all provenance fields populated
5. all `oracle_review_method == "from-source"`

The validator explicitly does **not** check joint-cell occupancy; the schema docstring documents this trade-off.

---

## Rubric dimensions and formulas

All scores in `[0.0, 1.0]`. Two implementers given the same `(actual_md, expected_md, html)` MUST produce bit-identical scores.

| # | Dimension | Formula (exact) |
|---|---|---|
| 1 | Heading preservation | Let `A`, `O` = ordered lists of `(level, normalized_text)` tuples extracted via regex `^(#{1,6})\s+(.*)$`. Let `J = |set(A) ∩ set(O)| / |set(A) ∪ set(O)|` (Jaccard over the set of tuples, `0` if both empty → score `1.0`). Let `K = 1 - kendall_tau_distance(common_subsequence(A, O)) / C(n, 2)` where `n = len(common)` and denominator `0` → `K = 1`. **Score = 0.7 * J + 0.3 * K**. |
| 2 | Link resolution | Parse `[text](href)` tokens from both. Let `H_a`, `H_o` = multisets of hrefs. **Score = \|H_a ∩ H_o\| / max(\|H_o\|, 1)**. Anchor (`#...`), `mailto:`, and `https://` links are counted in the same bucket in v2; a sub-score breakdown (internal / external / anchor) is recorded in the per-topic JSON for diagnostic purposes but does not factor into the gate score. |
| 3 | Table fidelity | Parse markdown tables via `\| ... \|` rows. Let `G_a`, `G_o` = row-major flattened cell strings (whitespace-normalized). **Score = matching_cells / max(\|G_o\|, 1)**, where a cell matches iff position and text both agree. Missing or extra tables: absent cells count as non-matching against the oracle grid. |
| 4 | Code-block fidelity | Parse fenced ` ```...``` ` blocks. Let `B_a`, `B_o` = lists of `(lang_tag, body_normalized)`. **Score = Σ (match_i) / max(len(B_o), 1)**, where `match_i = 1` iff lang tag equals AND body equals after stripping trailing whitespace on each line. |
| 5 | Image alt-text | Parse `![alt](src)` tokens. For each oracle image `i`, `match_i = 1` iff `alt_a[i] == alt_o[i]` (string equal). **Score = Σ match_i / max(len(oracle_images), 1)**. Empty-equals-empty counts as a match; the dimension records bugs (e.g., systematically stripped alts) because the oracle encodes what *should* be there. |
| 6 | List nesting | Extract depth-trees `T_a`, `T_o` from bullet/ordered-list lines (leading whitespace → depth; `-`/`*`/`N.` markers). **Score = 1 - zhang_shasha_tree_edit_distance(T_a, T_o) / max(size(T_a), size(T_o), 1)**. Tree size = node count. Zhang-Shasha implementation via `zss` package (pinned `zss==1.2.0`). |

**Per-topic floor and hard-min thresholds** (for the floor-occupancy rule):

| Dim | Per-topic floor | Hard-min (zero-tolerance) | MAX_BELOW_FLOOR (of 20) |
|---|---|---|---|
| 1 Heading | 0.90 | 0.70 | 2 |
| 2 Link | 0.90 | 0.70 | 2 |
| 3 Table | 0.85 | 0.70 | 2 |
| 4 Code | 0.90 | 0.70 | 2 |
| 5 Image alt | 0.80 | 0.70 | 2 |
| 6 List nesting | 0.85 | 0.70 | 2 |

**Rule (provably consistent)**: on any dimension `d`, fail the run iff `count(topic_scores[d] < per_topic_floor[d]) > 2` OR `count(topic_scores[d] < 0.70) > 0`. No aggregate-mean claim is made; the old mean-≥-0.95 rule has been removed.

---

## Oracle authorship and blinding protocol

**Required method:** `from-source`. The oracle author opens the raw `.html` snapshot and the published MadCap Flare target-rendering guidance (Orcina webhelp's rendered output in a browser, which is the *specification* of what the HTML should render to), then hand-writes the `.md` file. The author MUST NOT view `html_to_markdown()` output during authorship. Each oracle file carries a YAML-comment header:

```yaml
# oracle_authored_by: <reviewer-github-handle>
# oracle_review_method: from-source
# oracle_authored_at: <ISO-8601 UTC>
# oracle_second_reviewer: <second-reviewer-github-handle>
```

Matching fields are also required in `sample-manifest.yaml`. The validator test (`test_oracle_authorship_method_is_from_source`) fails the run on any `reviewed-from-output` row.

**Conflict resolution** (addressing Gemini P2): if two reviewers disagree on a cell of a complex table or a nested-list shape, the fixture README prescribes:
1. Open a "fixture-disagreement" comment on #2126 citing the specific file and cell.
2. Both reviewers annotate the HTML element they are interpreting.
3. If the disagreement survives one round, the fallback is the rendered view at orcina.com for that exact `source_url` at the recorded `fetched_at` timestamp.
4. If still unresolved, the topic is swapped out of the sample and a replacement chosen from the same product/category/complexity marginal bucket; the manifest tracks `previous_slug` for auditability.

---

## Manifest schema (required fields)

Each entry in `sample-manifest.yaml` MUST declare:

```yaml
- slug: orcaflex-line-types-intro
  product: OrcaFlex              # one of {OrcaFlex, OrcaWave, OrcFxAPI}
  category: introduction         # one of {introduction, data, theory, results, API}
  complexity: Simple             # one of {Simple, Medium, Hard}
  encoding_stress: false         # bool; >=2 true entries required among Hard
  source_url: https://www.orcina.com/webhelp/OrcaFlex/...
  fetched_at: 2026-04-24T14:00:00Z
  html_sha256: <64-hex>
  html_path: tests/fixtures/llm-wiki/conversion-oracle/orcaflex-line-types-intro.html
  oracle_md_path: tests/fixtures/llm-wiki/conversion-oracle/orcaflex-line-types-intro.md
  oracle_authored_by: "<handle>"
  oracle_authored_at: 2026-04-24T15:00:00Z
  oracle_second_reviewer: "<handle>"
  oracle_review_method: from-source
```

`sample-manifest.schema.json` encodes these as required; the structural test `test_sample_manifest_schema_valid` runs the schema validation and fails on any missing field.

---

## TDD Test List (13 structural + 120 parametrized = 133 collected)

### Structural (13)

| # | Test name | What it verifies |
|---|---|---|
| 1 | `test_sample_manifest_loads` | file parses; entry count == 20 |
| 2 | `test_sample_manifest_schema_valid` | entries conform to `sample-manifest.schema.json`; all required fields present |
| 3 | `test_sample_manifest_marginal_axes` | product/category/complexity marginals match declared quotas |
| 4 | `test_sample_manifest_hard_tier_encoding_stress` | `>=2` Hard-tier entries have `encoding_stress: true` |
| 5 | `test_sample_manifest_fixture_files_exist` | every entry's `html_path` and `oracle_md_path` resolve to non-empty tracked files |
| 6 | `test_sample_manifest_html_sha256_matches` | recomputed SHA-256 of each `.html` equals the manifest value |
| 7 | `test_oracle_authorship_method_is_from_source` | every entry has `oracle_review_method == "from-source"` |
| 8 | `test_oracle_has_second_reviewer` | every entry declares a non-empty `oracle_second_reviewer` distinct from `oracle_authored_by` |
| 9 | `test_html_to_markdown_import` | `ingest_orcina.html_to_markdown` is importable via the hyphenated-path shim |
| 10 | `test_rubric_scorer_determinism` | running each scorer twice on the same inputs returns identical floats |
| 11 | `test_aggregate_floor_occupancy` | floor-occupancy rule holds on all six dimensions |
| 12 | `test_no_network_access` | `pytest-socket` is active; a live `socket.socket(AF_INET, SOCK_STREAM)` call raises `SocketBlockedError` |
| 13 | `test_report_artifact_written` | `conversion-quality-report.json` is produced and conforms to its documented key schema |

### Parametrized (120 = 6 dims × 20 topics)

| Test | Count | Notes |
|---|---|---|
| `test_per_topic_dimension[<slug>-<dim>]` | 120 | double-parametrized on `entry` × `dim`. Each case computes a single score and writes `<slug>-<dim>.json`. Per-topic assertion is informational (logged); the gate is in `test_aggregate_floor_occupancy`. |

**Collection assertion**: `pytest --collect-only scripts/data/llm-wiki/tests/test_conversion_quality.py | grep -c "::test_"` == `133`. The AC below predicts exactly this number.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_conversion_quality.py --collect-only -q | grep -c "::"` returns exactly **133**.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_conversion_quality.py -v` exits 0.
- [ ] 20 `.html` + 20 `.md` oracle pairs exist under `tests/fixtures/llm-wiki/conversion-oracle/` and are tracked by `git ls-files`.
- [ ] `sample-manifest.yaml` declares, for each of the 20 entries, all required provenance fields (`source_url`, `fetched_at`, `html_sha256`, `oracle_authored_by`, `oracle_authored_at`, `oracle_second_reviewer`, `oracle_review_method`); `sample-manifest.schema.json` is the authoritative schema.
- [ ] All 20 entries have `oracle_review_method: from-source`.
- [ ] `fixtures_sampling.py` validates marginal-only stratification and the Hard-tier encoding-stress floor, and fails on drift.
- [ ] `scripts/data/llm-wiki/tests/.artifacts/conversion-quality-report.json` is produced on every run; contains per-topic per-dimension scores and a `floor_occupancy_summary` block.
- [ ] All six rubric dimensions have their formulas documented in `rubric_scorers.py` module docstring and in this plan's Rubric section; the two MUST match.
- [ ] `pytest-socket` is present in the test dependency group; `test_no_network_access` actively verifies the block.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` passes (both existing `test_resolve_wiki_path.py` and new module).

### Deferred / conditional

- [ ] **(Deferred)** Three-provider cross-review artifacts posted at `scripts/review/results/` against this v2's commit SHA. Unblock condition: codex-cli 0.124.0 stdin-hang (#2479) resolved OR explicit single-author exception granted by user. Plan will not be moved to `status:plan-review` until Claude + Gemini r2 reviews (minimum two-provider) land under the v2 SHA. No self-approval is requested or implied.

---

## Non-goals (explicit)

- **Not** fixing any conversion bug the rubric surfaces. Every bug becomes a separate issue; this plan ships only the diagnostic instrument.
- **Not** rewriting, refactoring, or extending `html_to_markdown` / `_convert_element` / `_convert_table`. Scope is test/QA only.
- **Not** testing supplementary pages (`ingest-orcina.py:415-451`) or PDF papers (`ingest_papers` at line 458). Topic pages only.
- **Not** testing the full 717 topics — sample-20 protocol only.
- **Not** registering the ingestion pipeline in `registry.yaml` / `pipeline-manifest.yaml` / `resource-intelligence-maturity.yaml` — follow-up governance task.
- **Not** touching `search-wiki.py` — #2141 covers search-side.
- **Not** computing an aggregate mean on any dimension; the v1 mean-rule is intentionally removed as internally inconsistent with per-topic floors.

---

## Adversarial Review Summary (r1 — complete)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | 3 P1 (parametrize arithmetic; threshold contradiction; stratification over-constraint); 2 P2 (oracle circularity; formula under-specification; urlopen patch trivially passes); 2 P3 (review-artifact AC vs revision-bound gate; provenance fields missing from schema) |
| Codex | n/a | not produced — codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression` (#2479) |
| Gemini | **MINOR** | 1 P2 (missing Attested Evidence block); 1 P3 (sample size may miss encoding edge cases) |

**Overall r1 result:** MAJOR → this v2 revision.

## Adversarial Review Summary (r2)

*Pending. Will be populated once r2 reviews land against this v2's commit SHA. Reviews produced against the v1 artifact do not satisfy the revision-bound approval gate.*

---

## Risks and Open Questions

- **Risk (fixture drift):** Oracle markdown is authored manually against HTML + live rendering. Mitigation — two-reviewer sign-off required, explicit blinding protocol, conflict-resolution procedure in fixture README, and a swap-and-replace path if disagreement survives.
- **Risk (orcina.com content change):** HTML snapshots may diverge from live pages. Mitigation — `html_sha256` + `fetched_at` + `source_url` captured per entry. A refresh job is out of scope for this plan; #2125 (auto-refresh) is the natural home.
- **Risk (scorer coupling to parser quirks):** Rubric scorers parse markdown with regexes/custom logic. Two independent implementations could still disagree on malformed inputs. Mitigation — `test_rubric_scorer_determinism` asserts repeatability; the README documents that ill-formed corner cases score `0.0` by policy.
- **Risk (zss dependency):** `zss==1.2.0` is an external package for tree-edit distance on list-nesting trees. Added as a test-only dep; if unavailable offline in CI, the scorer falls back to a vendored implementation (flagged as follow-up if needed).
- **Open:** Whether `**/.artifacts/` belongs in the repo-wide `.gitignore` (Gemini suggestion) or remains scoped to `scripts/data/llm-wiki/tests/.artifacts/`. Current recommendation — repo-wide, because the same pattern will recur elsewhere. Flag for user confirmation.
- **Open:** Whether r2 can proceed with two providers (Claude + Gemini) given the codex-cli regression, or whether the plan waits for #2479 resolution. Decision belongs to the user; see deferred AC above.

---

## Complexity: T2

**T2** — new test module + two helper modules + 20 fixture pairs + manifest + schema + gitignore + dependency add. No production code modified; TDD required; deterministic and offline.
