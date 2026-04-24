# Plan for #2126: test(llm-wiki): validate markdown conversion quality across all 717 topics

> **Status:** draft (v3 — addresses r2 findings)
> **Complexity:** T3
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2126
> **Base commit:** `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` (live-state claims anchored to this SHA)
> **Review artifacts:**
> - r1 Claude (MAJOR): `scripts/review/results/20260424T150953Z-plan-2126.md-plan-claude.md`
> - r1 Gemini (MINOR): `scripts/review/results/20260424T151456Z-plan-2126.md-plan-gemini.md`
> - r2 Claude (MAJOR): `scripts/review/results/20260424T184113Z-plan-2126-v2.md-plan-claude.md`
> - r2 Gemini (MINOR): `scripts/review/results/20260424T184400Z-plan-2126-v2.md-plan-gemini.md`
> - r1/r2 Codex: not produced (codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression`; tracked in #2479)
> - r3 artifacts: pending; revision-bound to this v3 (path and SHA to be recorded below once reviews land)

---

## Review History

### v1 → v2 (r1 resolutions, for context)
- r1 Claude P1: parametrize arithmetic off-by-20 → 13 structural + 120 parametrized = 133.
- r1 Claude P1: per-topic/aggregate threshold contradiction → aggregate-mean dropped; floor-occupancy rule adopted.
- r1 Claude P1: stratification over-constrained → marginal-only validation.
- r1 Claude P2/P3 + r1 Gemini: oracle blinding; formulas locked; `pytest-socket` active probe; Attested Evidence block added.

### v2 → v3 deltas (this revision)

| Finding | Severity (r2) | Resolution in v3 |
|---|---|---|
| Test-order dependency not pinned (aggregate reads artifacts from parametrized runs) | P1 (Claude r2) | **Resolved:** chose **Option A** — moved aggregate floor-occupancy enforcement out of the test collection graph into a `pytest_sessionfinish` hook in `conftest.py`. The hook reads `.artifacts/per-topic/*.json` after the full session completes and sets `session.exitstatus = 1` (with a detailed stderr report) when the floor-occupancy rule is violated. Rationale: runs reliably under `-k`, `pytest-xdist`, `--lf`, and isolated invocations; no new dependency. Structural `test_aggregate_floor_occupancy` is retired; structural count drops to 12; total collection count becomes **12 + 120 = 132**. |
| Kendall-tau formula self-referential (K ≡ 1 for n ≥ 2) | P1 (Claude r2) | **Resolved:** rewrote formula to compute tau over rank vectors of the intersection elements as they appear in A vs. O. Added `scipy>=1.11` as a pinned test dep. Added structural test `test_heading_preservation_detects_reordering` that would fail under v2's formula. |
| `zss==1.2.0` and `scipy>=1.11` missing from Files-to-Change | P2 (both) | **Resolved:** explicit Files-to-Change row for `pyproject.toml` adding `pytest-socket`, `zss==1.2.0`, `scipy>=1.11`. AC asserts pinned versions are present. Attested Evidence block gains scorer-lib availability checks. |
| `load_sample_manifest()` at collection time masks schema errors | P2 (Claude r2) | **Resolved:** loader returns `[]` on any parse/schema failure (silently). A dedicated structural test `test_sample_manifest_loads` asserts manifest loads AND count == 20; a second test `test_sample_manifest_schema_valid` re-loads raw YAML and runs schema validation. Collection never aborts; structural tests localize any load/schema defect. |
| AC grep pattern inconsistency (`::` vs `::test_`) | P2 (Claude r2) | **Resolved:** both AC lines use the identical pattern `pytest --collect-only -q \| grep -cE "^[^ ]+::test_"`. Expected count is **132** (12 structural + 120 parametrized) post–Option A retirement. |
| Complexity T2 optimistic (20 hand-authored oracles + 6 scorers + 3 deps) | P3 (Gemini r2) | **Resolved:** bumped to **T3**. Honest reflection of blinded oracle authoring effort across 20 topics × 3 products and three new test deps. |
| Image alt-text positional match cascades on drops/reorders | P3 (Claude r2) | **Resolved:** match by normalized `src` first, then score alt equality over the matched set. Unmatched images are surfaced as a localized penalty component, not a cascade. |
| Artifact Map r2 filename stubs vs actual plan filename | P3 (Claude r2) | **Resolved:** stubs now reference `2026-04-24-issue-2126-markdown-conversion-qa.md` (the actual plan filename) so `scripts/review/` output paths are retrievable without manual rewiring. |
| `_disable_network` fixture mixes activation with probe | P3 (Claude r2) | **Resolved:** session-scoped autouse fixture only calls `disable_socket(allow_unix_socket=False)`; the active `SocketBlockedError` probe lives solely in `test_no_network_access` (structural #12). |
| Attested Evidence lacks scorer-lib dep pin checks | P3 (Gemini r2) | **Resolved:** dep-availability lines added for `zss`, `scipy`, and `pytest-socket`. |

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
- `#2479` — expected OPEN — codex-cli 0.124.0 upstream stdin-hang

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

**Tooling / dep availability** (verify via `python -c "import X; print(X.__version__)"` under `uv run`, after implementation installs the deps):
- `pytest-socket` — will be added in this plan; current `pyproject.toml` does NOT declare it (verify: `grep pytest-socket pyproject.toml` → empty at base SHA).
- `zss==1.2.0` — will be added in this plan; current `pyproject.toml` does NOT declare it (verify: `grep -n 'zss' pyproject.toml` → empty at base SHA).
- `scipy>=1.11` — will be added in this plan; current `pyproject.toml` declares scipy as a general dep but NOT pinned in the test-dev group (verify: `grep -n 'scipy' pyproject.toml`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-2126-markdown-conversion-qa.md` |
| Test module | `scripts/data/llm-wiki/tests/test_conversion_quality.py` |
| Session hook (floor-occupancy gate) | `scripts/data/llm-wiki/tests/conftest.py` |
| Sampling helper | `scripts/data/llm-wiki/tests/fixtures_sampling.py` |
| Rubric scorer helper | `scripts/data/llm-wiki/tests/rubric_scorers.py` |
| Oracle fixtures | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` + `{slug}.md` |
| Stratification manifest | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` |
| Manifest JSON Schema | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` |
| Oracle authoring checklist | `tests/fixtures/llm-wiki/conversion-oracle/README.md` |
| Rubric report (generated, gitignored) | `scripts/data/llm-wiki/tests/.artifacts/conversion-quality-report.json` |
| Plan review r3 — Claude | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-claude.md` |
| Plan review r3 — Codex | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-codex.md` (conditional on codex-cli fix #2479) |
| Plan review r3 — Gemini | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-gemini.md` |

---

## Deliverable

A self-contained pytest module `test_conversion_quality.py` plus a `conftest.py` session hook that enforces the aggregate floor-occupancy gate AFTER all parametrized runs complete, plus 20 oracle-backed HTML/markdown fixtures under `tests/fixtures/llm-wiki/conversion-oracle/`. The module executes `html_to_markdown()` on stratified topics, scores each output against six rubric dimensions with locked formulas, and fails the run when the floor-occupancy rule is violated. Strict offline enforcement via `pytest-socket` (a session-autouse fixture disables the socket; a separate structural test actively probes that `SocketBlockedError` fires). Oracle authorship blinded from current converter output.

---

## Pseudocode

```python
# scripts/data/llm-wiki/tests/conftest.py
# ------------------------------------------
# Option A: aggregate floor-occupancy enforced via pytest_sessionfinish.
# This runs AFTER every test collected in the session, regardless of -k,
# pytest-xdist parallelism, or isolated invocation of a subset.

def pytest_sessionfinish(session, exitstatus):
    # Only enforce if the conversion-quality tests actually ran.
    artifacts_dir = Path("scripts/data/llm-wiki/tests/.artifacts/per-topic")
    if not artifacts_dir.exists():
        return  # nothing to aggregate; leave exitstatus unchanged
    per_topic = [json.loads(p.read_text()) for p in artifacts_dir.glob("*.json")]
    if not per_topic:
        return
    violations = check_floor_occupancy(per_topic)  # from fixtures_sampling
    write_report("conversion-quality-report.json", per_topic, violations)
    if violations:
        # Report to stderr, fail the session.
        session.exitstatus = 1
        print("FLOOR-OCCUPANCY VIOLATIONS:", violations, file=sys.stderr)

@pytest.fixture(scope="session", autouse=True)
def _disable_network():
    # Activation only; active probe lives in test_no_network_access.
    from pytest_socket import disable_socket
    disable_socket(allow_unix_socket=False)
    yield
    # (no teardown required; pytest-socket auto-reenables at session end)
```

```python
# scripts/data/llm-wiki/tests/test_conversion_quality.py

def load_sample_manifest():
    """Collection-safe loader. Returns [] on ANY failure so that pytest
    collection never aborts; structural tests localize real errors."""
    try:
        entries = yaml.safe_load(MANIFEST_PATH.read_text())
        return entries if isinstance(entries, list) else []
    except Exception:
        return []

@pytest.mark.parametrize("entry", load_sample_manifest(), ids=lambda e: e["slug"])
@pytest.mark.parametrize("dim", RUBRIC_DIMENSIONS)
def test_per_topic_dimension(entry, dim):
    html = Path(entry["html_path"]).read_text()
    expected_md = Path(entry["oracle_md_path"]).read_text()
    _, actual_md = ingest_orcina.html_to_markdown(html, entry["source_url"])
    score = SCORERS[dim](actual_md, expected_md, html)  # locked formula per dim
    write_per_topic_artifact(entry["slug"], dim, score)
    # NOTE: per-topic floor is NOT asserted here; the session hook enforces
    # the floor-occupancy rule after ALL tests complete.
```

Formula pseudocode for composite scorers is given in the "Rubric dimensions and formulas" section below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/tests/test_conversion_quality.py` | pytest module — per-topic scoring + 12 structural tests |
| Create | `scripts/data/llm-wiki/tests/conftest.py` | `pytest_sessionfinish` hook enforcing floor-occupancy after all parametrized runs complete (Option A test-order fix) + `_disable_network` session-autouse fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures_sampling.py` | marginal-quota validator + manifest schema loader + `check_floor_occupancy()` used by the session hook |
| Create | `scripts/data/llm-wiki/tests/rubric_scorers.py` | six pure-function scorers implementing locked formulas (heading scorer uses `scipy.stats.kendalltau` on rank vectors) |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` | 20-entry manifest with full provenance fields |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` | JSON Schema enforcing required fields; referenced by validator |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` × 20 | frozen HTML snapshots |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.md` × 20 | oracle markdown — from-source authorship only |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/README.md` | blinding protocol + conflict-resolution procedure |
| Modify | `.gitignore` | add `**/.artifacts/` repo-wide (per Gemini r1 suggestion, keeps convention uniform) |
| Modify | `pyproject.toml` (test/dev dependency group) | add **three pinned deps**: `pytest-socket` (any recent version), `zss==1.2.0` (Zhang-Shasha tree-edit distance for list-nesting scorer), `scipy>=1.11` (Kendall-tau for heading-preservation scorer) |
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
| 1 | **Heading preservation** | Let `A`, `O` = ordered lists of `(level, normalized_text)` tuples extracted via regex `^(#{1,6})\s+(.*)$`. **Set component (Jaccard)**: `J = |set(A) ∩ set(O)| / |set(A) ∪ set(O)|` (if both empty → `J = 1.0`). **Order component (Kendall-tau on rank vectors of common elements)**: `I = set(A) ∩ set(O)`. If `|I| < 2`: `K = 1.0` (trivially well-ordered). Else: for each `h ∈ I` record `rank_A[h]` = index of `h` in `A` and `rank_O[h]` = index of `h` in `O`; compute `tau = scipy.stats.kendalltau(rank_A_vector, rank_O_vector).statistic` (returns τ in `[-1, 1]`); normalize to `[0, 1]` via `K = (tau + 1) / 2`. **Score = 0.7 * J + 0.3 * K**. The `common_subsequence`-based formulation from v2 is explicitly rejected (self-referential: tau distance of a subsequence to itself is trivially 0). |
| 2 | Link resolution | Parse `[text](href)` tokens from both. Let `H_a`, `H_o` = multisets of hrefs. **Score = \|H_a ∩ H_o\| / max(\|H_o\|, 1)**. Anchor (`#...`), `mailto:`, and `https://` links are counted in the same bucket in v3; a sub-score breakdown (internal / external / anchor) is recorded in the per-topic JSON for diagnostic purposes but does not factor into the gate score. |
| 3 | Table fidelity | Parse markdown tables via `\| ... \|` rows. Let `G_a`, `G_o` = row-major flattened cell strings (whitespace-normalized). **Score = matching_cells / max(\|G_o\|, 1)**, where a cell matches iff position and text both agree. Missing or extra tables: absent cells count as non-matching against the oracle grid. |
| 4 | Code-block fidelity | Parse fenced ` ```...``` ` blocks. Let `B_a`, `B_o` = lists of `(lang_tag, body_normalized)`. **Score = Σ (match_i) / max(len(B_o), 1)**, where `match_i = 1` iff lang tag equals AND body equals after stripping trailing whitespace on each line. |
| 5 | **Image alt-text** | Parse `![alt](src)` tokens. Let `M_a = {normalized_src(i) → alt_a(i)}` and `M_o = {normalized_src(i) → alt_o(i)}`. **Match by `src` first**: `common = set(M_a.keys()) ∩ set(M_o.keys())`. For each oracle image with `src ∈ common`, `match_i = 1` iff `M_a[src] == M_o[src]`. **Score = Σ match_i / max(len(M_o), 1)**. Unmatched oracle `src`s (dropped/reordered) contribute `0` to the numerator but still count in the denominator, producing a localized penalty rather than a positional cascade. |
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

**Rule (provably consistent)**: on any dimension `d`, fail the run iff `count(topic_scores[d] < per_topic_floor[d]) > 2` OR `count(topic_scores[d] < 0.70) > 0`. No aggregate-mean claim is made; the v1 mean-rule remains intentionally removed. Enforcement is in `pytest_sessionfinish` (see Option A above), not in a pytest test — so ordering is not a concern.

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

## TDD Test List (12 structural + 120 parametrized = 132 collected; aggregate floor-occupancy enforced by session hook)

### Structural (12)

| # | Test name | What it verifies |
|---|---|---|
| 1 | `test_sample_manifest_loads` | file parses; entry count == 20 (this test is what surfaces a collection-time loader failure, since the parametrize loader returns `[]` silently on error) |
| 2 | `test_sample_manifest_schema_valid` | entries conform to `sample-manifest.schema.json`; all required fields present |
| 3 | `test_sample_manifest_marginal_axes` | product/category/complexity marginals match declared quotas |
| 4 | `test_sample_manifest_hard_tier_encoding_stress` | `>=2` Hard-tier entries have `encoding_stress: true` |
| 5 | `test_sample_manifest_fixture_files_exist` | every entry's `html_path` and `oracle_md_path` resolve to non-empty tracked files |
| 6 | `test_sample_manifest_html_sha256_matches` | recomputed SHA-256 of each `.html` equals the manifest value |
| 7 | `test_oracle_authorship_method_is_from_source` | every entry has `oracle_review_method == "from-source"` |
| 8 | `test_oracle_has_second_reviewer` | every entry declares a non-empty `oracle_second_reviewer` distinct from `oracle_authored_by` |
| 9 | `test_html_to_markdown_import` | `ingest_orcina.html_to_markdown` is importable via the hyphenated-path shim |
| 10 | `test_rubric_scorer_determinism` | running each scorer twice on the same inputs returns identical floats |
| 11 | `test_heading_preservation_detects_reordering` | **NEW in v3.** Constructs `A = "# H1\n# H2\n# H3"` and `O = "# H1\n# H3\n# H2"`. Asserts `heading_scorer(A, O, "") < 1.0` (i.e., the reordering penalty fires). This test would have FAILED under v2's `K = 1 - kendall_tau_distance(common_subsequence(A,O)) / C(n,2)` formula (which returns K = 1.0 trivially, hence Score = 1.0). It PASSES under v3's rank-vector formula: rank_A = [0,1,2], rank_O = [0,2,1], `tau = kendalltau([0,1,2], [0,2,1]).statistic ≈ 0.333`, `K ≈ 0.667`, `J = 1.0`, Score ≈ 0.9. |
| 12 | `test_no_network_access` | `pytest-socket` is active; a live `socket.socket(AF_INET, SOCK_STREAM)` call raises `SocketBlockedError`. (Active probe lives here, not in the `_disable_network` fixture.) |

**Note:** v2's `test_aggregate_floor_occupancy` (old #11) and `test_report_artifact_written` (old #13) are intentionally dropped from the structural test list. Both concerns are now handled by the `pytest_sessionfinish` hook in `conftest.py`, which runs reliably after every collected test regardless of ordering, `-k` filtering, or `pytest-xdist` parallelism. The report artifact is written by the same hook.

### Parametrized (120 = 6 dims × 20 topics)

| Test | Count | Notes |
|---|---|---|
| `test_per_topic_dimension[<slug>-<dim>]` | 120 | double-parametrized on `entry` × `dim`. Each case computes a single score and writes `<slug>-<dim>.json`. Per-topic assertion is informational (logged); the gate is enforced by the session hook in `conftest.py`. |

**Collection assertion**: `pytest --collect-only -q scripts/data/llm-wiki/tests/test_conversion_quality.py | grep -cE "^[^ ]+::test_"` == `132`. The AC below predicts exactly this number using the SAME grep pattern.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_conversion_quality.py --collect-only -q | grep -cE "^[^ ]+::test_"` returns exactly **132**.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ --collect-only -q | grep -cE "^[^ ]+::test_"` returns **132 + (existing `test_resolve_wiki_path.py` count)** — the new module contributes exactly 132.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_conversion_quality.py -v` exits 0 on a clean corpus; exits 1 when a synthetic floor-occupancy violation is injected (regression test for the session hook).
- [ ] 20 `.html` + 20 `.md` oracle pairs exist under `tests/fixtures/llm-wiki/conversion-oracle/` and are tracked by `git ls-files`.
- [ ] `sample-manifest.yaml` declares, for each of the 20 entries, all required provenance fields (`source_url`, `fetched_at`, `html_sha256`, `oracle_authored_by`, `oracle_authored_at`, `oracle_second_reviewer`, `oracle_review_method`); `sample-manifest.schema.json` is the authoritative schema.
- [ ] All 20 entries have `oracle_review_method: from-source`.
- [ ] `fixtures_sampling.py` validates marginal-only stratification and the Hard-tier encoding-stress floor, and fails on drift; also exports `check_floor_occupancy()` consumed by `conftest.py`.
- [ ] `scripts/data/llm-wiki/tests/.artifacts/conversion-quality-report.json` is produced on every run by the `pytest_sessionfinish` hook; contains per-topic per-dimension scores and a `floor_occupancy_summary` block.
- [ ] All six rubric dimensions have their formulas documented in `rubric_scorers.py` module docstring and in this plan's Rubric section; the two MUST match. The heading scorer imports `scipy.stats.kendalltau` and operates on rank vectors of the intersection.
- [ ] `pyproject.toml` test/dev dep group pins **`pytest-socket`**, **`zss==1.2.0`**, and **`scipy>=1.11`**; verified by `grep -E '(pytest-socket|zss==1\.2\.0|scipy>=1\.11)' pyproject.toml | wc -l` == 3.
- [ ] `test_no_network_access` actively verifies the socket block; the `_disable_network` fixture contains activation only, no probe.
- [ ] `test_heading_preservation_detects_reordering` passes on v3's rank-vector formula. Sanity-checked by running it against the rejected v2 formula in a scratch branch: expect FAIL under v2 formula, PASS under v3. This check is a build-sequence step, not a CI artifact.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` passes (both existing `test_resolve_wiki_path.py` and new module).

### Deferred / conditional

- [ ] **(Deferred)** Three-provider cross-review artifacts posted at `scripts/review/results/` against this v3's commit SHA. Unblock condition: codex-cli 0.124.0 stdin-hang (#2479) resolved OR explicit single-exception granted by user. Plan will not be moved to `status:plan-review` until Claude + Gemini r3 reviews (minimum two-provider) land under the v3 SHA. No self-approval is requested or implied.

---

## Build Sequence (TDD order)

1. Add `pytest-socket`, `zss==1.2.0`, `scipy>=1.11` to `pyproject.toml` test/dev group; run `uv sync` and assert all three import.
2. Write `sample-manifest.schema.json`.
3. Write `fixtures_sampling.py` (validator + `check_floor_occupancy()`) with unit tests (folded into structural tests 3, 4, and the session-hook injection test).
4. Write `rubric_scorers.py`. Implement heading scorer last, against `test_heading_preservation_detects_reordering` — RED first, then GREEN with the rank-vector formula.
5. Write `conftest.py` with `pytest_sessionfinish` hook and the session-autouse `_disable_network` fixture.
6. Write the 12 structural tests.
7. Author 20 blinded oracle fixtures following the protocol in `tests/fixtures/llm-wiki/conversion-oracle/README.md`.
8. Write the 120-case `test_per_topic_dimension` parametrized test; assert `--collect-only` count == 132.
9. Inject a synthetic floor-occupancy violation and assert the session hook sets `session.exitstatus = 1`.
10. Full green run under `uv run pytest scripts/data/llm-wiki/tests/ -v`.

---

## Non-goals (explicit)

- **Not** fixing any conversion bug the rubric surfaces. Every bug becomes a separate issue; this plan ships only the diagnostic instrument.
- **Not** rewriting, refactoring, or extending `html_to_markdown` / `_convert_element` / `_convert_table`. Scope is test/QA only.
- **Not** testing supplementary pages (`ingest-orcina.py:415-451`) or PDF papers (`ingest_papers` at line 458). Topic pages only.
- **Not** testing the full 717 topics — sample-20 protocol only.
- **Not** registering the ingestion pipeline in `registry.yaml` / `pipeline-manifest.yaml` / `resource-intelligence-maturity.yaml` — follow-up governance task.
- **Not** touching `search-wiki.py` — #2141 covers search-side.
- **Not** computing an aggregate mean on any dimension; the v1 mean-rule is intentionally removed as internally inconsistent with per-topic floors.
- **Not** introducing `pytest-ordering` or `pytest-dependency`. Option A (session hook) dominates because it requires no new dep and is robust under `pytest-xdist`.

---

## Adversarial Review Summary (r1 — complete)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | 3 P1 (parametrize arithmetic; threshold contradiction; stratification over-constraint); 2 P2 (oracle circularity; formula under-specification; urlopen patch trivially passes); 2 P3 (review-artifact AC vs revision-bound gate; provenance fields missing from schema) |
| Codex | n/a | not produced — codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression` (#2479) |
| Gemini | **MINOR** | 1 P2 (missing Attested Evidence block); 1 P3 (sample size may miss encoding edge cases) |

## Adversarial Review Summary (r2 — complete)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | 2 P1 (test-order dependency not pinned; Kendall-tau self-referential); 4 P2 (zss dep missing from Files-to-Change; manifest loader at collection time; AC grep drift; image positional cascade); 4 P3 (Artifact Map filename stubs; fixture probe mixing; complexity T2 optimistic; additional questions) |
| Codex | n/a | not produced — codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression` (#2479) |
| Gemini | **MINOR** | 2 P2 (zss missing from Files-to-Change; Attested Evidence lacks scorer-lib dep checks); 2 P3 (vendored zss fallback; duplicate-heading question) |

**Overall r2 result:** MAJOR → this v3 revision.

## Adversarial Review Summary (r3)

*Pending. Will be populated once r3 reviews land against this v3's commit SHA. Reviews produced against v1 or v2 artifacts do not satisfy the revision-bound approval gate.*

---

## Risks and Open Questions

- **Risk (fixture drift):** Oracle markdown is authored manually against HTML + live rendering. Mitigation — two-reviewer sign-off required, explicit blinding protocol, conflict-resolution procedure in fixture README, and a swap-and-replace path if disagreement survives.
- **Risk (orcina.com content change):** HTML snapshots may diverge from live pages. Mitigation — `html_sha256` + `fetched_at` + `source_url` captured per entry. A refresh job is out of scope for this plan; #2125 (auto-refresh) is the natural home.
- **Risk (scorer coupling to parser quirks):** Rubric scorers parse markdown with regexes/custom logic. Two independent implementations could still disagree on malformed inputs. Mitigation — `test_rubric_scorer_determinism` asserts repeatability; the README documents that ill-formed corner cases score `0.0` by policy.
- **Risk (`zss` / `scipy` offline availability):** Both are external packages. Mitigation — pinned versions declared in `pyproject.toml`; `uv` prefers the wheel cache under offline execution. If offline CI turns out to lack them, the remediation is to pre-populate the wheel cache, NOT to vendor in-tree (explicitly out of scope here to keep surface area small).
- **Risk (`pytest-socket` + unix-socket subprocess IPC):** `allow_unix_socket=False` is the strict setting; some tooling (e.g., `uv` subprocess IPC in certain modes) may rely on unix sockets. Mitigation — the session-autouse fixture is scoped to the `tests/test_conversion_quality.py` module's session; an actual CI probe is listed in Build Sequence step 1.
- **Risk (session hook vs isolated invocation):** When the whole test module is NOT collected (e.g., `pytest -k missing_pattern`), no per-topic artifacts are written. The `pytest_sessionfinish` hook detects the empty-artifacts case and returns without altering `exitstatus`, so it never spuriously fails a narrow run. Documented in `conftest.py` docstring.
- **Risk (duplicate-heading question from Gemini r2 P3):** The heading-preservation Jaccard is over sets of `(level, normalized_text)` tuples. If two distinct headings have the same `(level, text)` (rare in Orcina webhelp, common in other corpora), they collapse into a single set element. Mitigation — documented in `rubric_scorers.py` docstring as a known, accepted corpus-specific quirk; does not affect the 20-topic Orcina sample.
- **Open:** Whether `**/.artifacts/` belongs in the repo-wide `.gitignore` (Gemini suggestion) or remains scoped to `scripts/data/llm-wiki/tests/.artifacts/`. Current recommendation — repo-wide, because the same pattern will recur elsewhere. Flag for user confirmation.
- **Open:** Whether r3 can proceed with two providers (Claude + Gemini) given the codex-cli regression, or whether the plan waits for #2479 resolution. Decision belongs to the user; see deferred AC above.

---

## Complexity: T3

**T3** — 20 blinded hand-authored oracle files × 3 products + 6 rubric scorers + 3 new test deps (`pytest-socket`, `zss==1.2.0`, `scipy>=1.11`) + 12 structural tests + session hook + JSON Schema + two-reviewer blinding protocol. Bumped from T2 per r2 Claude P3 and r2 Gemini P3 consensus: the 20-fixture authoring effort alone dominates implementation time, and T2 pacing risks shortcutting the blinding protocol. Scope remains test/QA only (no production code modified); TDD required; deterministic and offline.
