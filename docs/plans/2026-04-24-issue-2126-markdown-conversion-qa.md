# Plan for #2126: test(llm-wiki): validate markdown conversion quality across all 717 topics

> **Status:** draft (v4 — addresses r3 findings)
> **Complexity:** T3
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2126
> **Base commit:** `07e73c2ec9775fd6bec3e4ea2b61876bbf4fb752` (live-state claims anchored to this SHA)
> **Review artifacts:**
> - r1 Claude (MAJOR): `scripts/review/results/20260424T150953Z-plan-2126.md-plan-claude.md`
> - r1 Gemini (MINOR): `scripts/review/results/20260424T151456Z-plan-2126.md-plan-gemini.md`
> - r2 Claude (MAJOR): `scripts/review/results/20260424T184113Z-plan-2126-v2.md-plan-claude.md`
> - r2 Gemini (MINOR): `scripts/review/results/20260424T184400Z-plan-2126-v2.md-plan-gemini.md`
> - r3 Claude (MAJOR): `scripts/review/results/20260424T185934Z-plan-2126-v3.md-plan-claude.md`
> - r3 Gemini (APPROVE): `scripts/review/results/20260424T190207Z-plan-2126-v3.md-plan-gemini.md`
> - r1/r2/r3 Codex: not produced (codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression`; tracked in #2479)
> - r4 artifacts: pending; revision-bound to this v4 (paths and SHA to be recorded below once reviews land)

---

## Review History

### v1 → v2 (r1 resolutions, for context)
- r1 Claude P1: parametrize arithmetic off-by-20 → 13 structural + 120 parametrized = 133.
- r1 Claude P1: per-topic/aggregate threshold contradiction → aggregate-mean dropped; floor-occupancy rule adopted.
- r1 Claude P1: stratification over-constrained → marginal-only validation.
- r1 Claude P2/P3 + r1 Gemini: oracle blinding; formulas locked; `pytest-socket` active probe; Attested Evidence block added.

### v2 → v3 (r2 resolutions, for context)
- r2 Claude P1 (test-order dependency): `pytest_sessionfinish` hook replaces `test_aggregate_floor_occupancy`.
- r2 Claude P1 (Kendall-tau self-referential): rank-vector formula + `scipy>=1.11`; structural regression test added.
- r2 P2/P3: pyproject pins, collection-safe manifest loader, AC grep pattern unified, positional image match replaced with src-keyed match, Artifact Map stubs corrected, `_disable_network` fixture cleaned, Attested Evidence scorer-lib checks added.

### v3 → v4 deltas (this revision)

| Finding | Severity (r3) | Resolution in v4 |
|---|---|---|
| Empty-denominator defect on dims 2-5 (introduction pages with zero tables/code/images/links would fail despite perfect conversion) | **P2 (escalated MAJOR; Claude r3)** | **Resolved:** hoisted a shared helper `empty_safe_ratio(actual_tokens, oracle_tokens, match_count)` in `rubric_scorers.py` and applied it explicitly in the pseudocode of dimensions 2, 3, 4, and 5 (no "same as dim 1" hand-waves). The rule is `if |actual| == 0 and |oracle| == 0: return 1.0; else: return match_count / max(|oracle|, 1)`. The asymmetric case (oracle empty, actual non-empty) is made explicit: returns `0.0` with the token set surfaced in the per-topic JSON as `spurious_tokens` (false-positive content against an empty oracle). New TDD row `test_rubric_scorer_handles_empty_oracle_and_actual` guards the both-empty path across all four dims. |
| `_disable_network` fixture scope (`conftest.py` at `scripts/data/llm-wiki/tests/` applies to sibling `test_resolve_wiki_path.py`) | P3 (Claude r3) | **Resolved:** chose the **subdirectory option** — move the conversion-QA module + `conftest.py` under `scripts/data/llm-wiki/tests/markdown_qa/`. The `_disable_network` fixture now scopes only to that subdirectory. Rationale recorded below; sibling test inventory attested in Attested Evidence. |
| AC regression-test injection mechanism unspecified | P3 (Claude r3) | **Resolved:** pinned to a dedicated test file `scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` that writes known-bad per-topic JSON fixtures into a `tmp_path`-redirected artifacts dir and invokes pytest in a subprocess (`subprocess.run([sys.executable, "-m", "pytest", ...], ...)`) with `check=False`, asserting `result.returncode == 1`. Exact pattern spelled out in Pseudocode and Build Sequence. |
| `test_oracle_has_second_reviewer` blocks solo execution | P3 (Claude r3) | **Resolved:** added an escape hatch — the value `self-reviewed-with-24h-delay` is a valid `oracle_second_reviewer` when `oracle_authored_by == oracle_second_reviewer` would otherwise hold. The Fixture Authoring Protocol documents the 24-hour cooling-off requirement: the author must re-open each fixture ≥24h after initial authorship, diff against the current converter output, and sign off with a dated commit message. The manifest also carries `single_reviewer_timelag: true` for audit. The structural test accepts this sentinel in lieu of a distinct handle. |
| scipy pyproject attestation | P3 (Claude r3) | **Resolved:** ran `grep -n scipy pyproject.toml` against HEAD = `07e73c2e`; result = **no match** (scipy is NOT declared at all). v3's claim that scipy was declared as a general dep was incorrect. Attested Evidence block updated verbatim. Files-to-Change row for `pyproject.toml` already adds `scipy>=1.11` — no additional row needed; the earlier row is simply the first introduction of scipy into the project. |

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

Claims below are independently verifiable and anchored to base commit `07e73c2ec9775fd6bec3e4ea2b61876bbf4fb752`. Each claim is stated with the verification command so a reviewer can reproduce.

**Issue statuses** (verify via `gh issue view <N> --json number,state,title`):
- `#2126` — expected OPEN — `test(llm-wiki): validate markdown conversion quality across all 717 topics`
- `#2088` — expected CLOSED — `feat(llm-wiki): ingest OrcaFlex, OrcaWave, and OrcFxAPI online help into llm-wiki`
- `#2140` — expected CLOSED — portable path resolution + smoke tests
- `#2141` — expected OPEN — fixture-backed tests for llm-wiki ingest and search scripts
- `#2476` — expected OPEN — canonical spec semantic-equivalence contract and fixture cookbook
- `#2479` — expected OPEN — codex-cli 0.124.0 upstream stdin-hang

**File existence at HEAD = 07e73c2e** (verify via `git ls-files <path>` or `git show HEAD:<path> | wc -l`):
- `scripts/data/llm-wiki/ingest-orcina.py` — present, 637 lines
- `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` — present, 186 lines
- `scripts/data/llm-wiki/tests/__init__.py` — present, 0 bytes
- `scripts/data/llm-wiki/resolve_wiki_path.py` — present

**Sibling-test inventory** (verify via `ls scripts/data/llm-wiki/tests/`):
- Directory currently contains exactly one test module: `test_resolve_wiki_path.py` (plus `__init__.py` and `__pycache__/`).
- Network-sensitivity probe: `grep -nE 'socket|urlopen|requests|httpx|urllib' scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` returns **no matches** at HEAD. The sibling test does not touch network or unix sockets and would tolerate `disable_socket(allow_unix_socket=False)`.
- Decision: Despite the sibling being safe today, v4 adopts the **subdirectory option** (`scripts/data/llm-wiki/tests/markdown_qa/`) as a defense-in-depth choice — it prevents *future* sibling additions from silently inheriting the socket disable and keeps the fixture's blast radius equal to its intent.

**Gap proofs** (verify via the shown command):
- `git grep -n "llm-wiki\|orcina" -- config/data/pipeline-manifest.yaml` → expected empty
- `git grep -n "llm-wiki\|orcina" -- data/document-index/registry.yaml` → expected empty
- `git grep -n "llm-wiki\|orcina" -- data/document-index/resource-intelligence-maturity.yaml` → expected empty
- `git ls-files scripts/data/llm-wiki/tests/ | grep -c conversion` → expected 0
- `git ls-files .gitignore | xargs grep -n llm-wiki` → expected to show `data/llm-wiki` ignored

**Tooling / dep availability at HEAD = 07e73c2e** (verify via the shown command):
- `pytest-socket` — will be added in this plan. `grep -n pytest-socket pyproject.toml` at base SHA returns **no match**.
- `zss==1.2.0` — will be added in this plan. `grep -n 'zss' pyproject.toml` at base SHA returns **no match**.
- `scipy>=1.11` — will be added in this plan. `grep -n scipy pyproject.toml` at base SHA returns **no match** (scipy is NOT currently declared in `pyproject.toml` at any scope — this corrects v3's inaccurate claim that scipy was a declared general dep). The `pyproject.toml` Files-to-Change row therefore introduces scipy for the first time into the project.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-2126-markdown-conversion-qa.md` |
| Test module (relocated in v4) | `scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py` |
| Session hook + scoped fixture (relocated in v4) | `scripts/data/llm-wiki/tests/markdown_qa/conftest.py` |
| Session-hook regression test (new in v4) | `scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` |
| Sampling helper | `scripts/data/llm-wiki/tests/markdown_qa/fixtures_sampling.py` |
| Rubric scorer helper | `scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py` |
| Subdirectory package anchor | `scripts/data/llm-wiki/tests/markdown_qa/__init__.py` |
| Oracle fixtures | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` + `{slug}.md` |
| Stratification manifest | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` |
| Manifest JSON Schema | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` |
| Oracle authoring checklist | `tests/fixtures/llm-wiki/conversion-oracle/README.md` |
| Rubric report (generated, gitignored) | `scripts/data/llm-wiki/tests/markdown_qa/.artifacts/conversion-quality-report.json` |
| Plan review r4 — Claude | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-claude.md` |
| Plan review r4 — Codex | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-codex.md` (conditional on codex-cli fix #2479) |
| Plan review r4 — Gemini | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-gemini.md` |

---

## Deliverable

A self-contained pytest module `test_conversion_quality.py` under `scripts/data/llm-wiki/tests/markdown_qa/`, plus a subdirectory-scoped `conftest.py` that enforces the aggregate floor-occupancy gate AFTER all parametrized runs complete, plus a `test_session_hook_regression.py` that subprocess-invokes pytest with a synthetic violation and asserts exit-code 1, plus 20 oracle-backed HTML/markdown fixtures under `tests/fixtures/llm-wiki/conversion-oracle/`. The module executes `html_to_markdown()` on stratified topics, scores each output against six rubric dimensions with locked formulas (all six use the shared `empty_safe_ratio` helper where applicable), and fails the run when the floor-occupancy rule is violated. Strict offline enforcement via `pytest-socket` is scoped to the `markdown_qa/` subdirectory so sibling tests are not affected (an active `SocketBlockedError` probe lives in a structural test). Oracle authorship blinded from current converter output, with a documented 24-hour-delay solo-reviewer escape hatch.

---

## Pseudocode

### Subdirectory-scoped conftest.py (v4)

```python
# scripts/data/llm-wiki/tests/markdown_qa/conftest.py
# ---------------------------------------------------
# This conftest applies ONLY to tests under markdown_qa/.
# Sibling tests under scripts/data/llm-wiki/tests/ (e.g., test_resolve_wiki_path.py)
# are NOT affected by the socket disable or the session-finish hook.

ARTIFACTS_DIR = Path(__file__).parent / ".artifacts" / "per-topic"

def pytest_sessionfinish(session, exitstatus):
    # Fires ONLY for sessions that collected markdown_qa/ tests; because
    # conftest.py is subdirectory-scoped, pytest runs it only when the
    # subdirectory participates in collection. Additionally guard on artifacts
    # existence so narrow `-k` runs that collect zero per-topic tests don't
    # flip the exit code.
    if not ARTIFACTS_DIR.exists():
        return
    per_topic = [json.loads(p.read_text()) for p in ARTIFACTS_DIR.glob("*.json")]
    if not per_topic:
        return
    violations = check_floor_occupancy(per_topic)  # from fixtures_sampling
    write_report("conversion-quality-report.json", per_topic, violations)
    if violations:
        session.exitstatus = 1
        print("FLOOR-OCCUPANCY VIOLATIONS:", violations, file=sys.stderr)

@pytest.fixture(scope="session", autouse=True)
def _disable_network():
    # Activation only; active probe lives in test_no_network_access.
    # Scoped to markdown_qa/ via subdirectory conftest — sibling tests unaffected.
    from pytest_socket import disable_socket
    disable_socket(allow_unix_socket=False)
    yield
```

### Test module

```python
# scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py

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

### Shared empty-safe helper (new in v4)

```python
# scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py

def empty_safe_ratio(actual_tokens, oracle_tokens, match_count):
    """Shared denominator-safe ratio used by dims 2-5.

    Rule:
      - both empty       → 1.0   (trivially well-matched; no regression vs oracle)
      - oracle empty,
        actual non-empty → 0.0   (spurious content against empty oracle)
      - otherwise        → match_count / max(len(oracle_tokens), 1)
    """
    a, o = len(actual_tokens), len(oracle_tokens)
    if a == 0 and o == 0:
        return 1.0
    if o == 0 and a > 0:
        return 0.0  # asymmetric: false-positive tokens on an empty oracle
    return match_count / max(o, 1)
```

### Session-hook regression test (new in v4)

```python
# scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py

def test_session_hook_fails_run_on_injected_violation(tmp_path, monkeypatch):
    """Write known-bad per-topic JSON fixtures into a tmp artifacts dir,
    then invoke pytest in a subprocess against a minimal collection that
    triggers pytest_sessionfinish. Assert exit code 1."""
    # 1. Build a synthetic .artifacts/per-topic dir with 3 entries below floor
    synthetic_artifacts = tmp_path / ".artifacts" / "per-topic"
    synthetic_artifacts.mkdir(parents=True)
    for i, slug in enumerate(["a", "b", "c"]):
        # MAX_BELOW_FLOOR is 2; 3 below-floor rows forces a violation
        (synthetic_artifacts / f"{slug}-heading.json").write_text(
            json.dumps({"slug": slug, "dim": "heading", "score": 0.50})
        )

    # 2. Invoke pytest in a subprocess against a trivial test file that
    #    does nothing but let sessionfinish run, with the artifacts dir
    #    pointed at our synthetic tree via env var.
    trivial = tmp_path / "trivial_test.py"
    trivial.write_text("def test_noop():\n    assert True\n")

    # The conftest reads ARTIFACTS_DIR from MARKDOWN_QA_ARTIFACTS_DIR when set
    env = {**os.environ, "MARKDOWN_QA_ARTIFACTS_DIR": str(synthetic_artifacts)}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(trivial), "-p",
         "scripts.data.llm-wiki.tests.markdown_qa.conftest", "-q"],
        env=env, capture_output=True, check=False,
    )
    assert result.returncode == 1, (
        f"Session hook did not fail on injected violation; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert b"FLOOR-OCCUPANCY VIOLATIONS" in result.stderr
```

(The `MARKDOWN_QA_ARTIFACTS_DIR` env override is a narrow test seam added to `conftest.py` so the regression test does not pollute the real `.artifacts/` tree.)

Formula pseudocode for composite scorers is given in the "Rubric dimensions and formulas" section below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/tests/markdown_qa/__init__.py` | Empty package anchor for the new subdirectory |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py` | pytest module — per-topic scoring + 12 structural tests |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/conftest.py` | Subdirectory-scoped `pytest_sessionfinish` hook + `_disable_network` session-autouse fixture. Scope is `markdown_qa/` only; sibling `test_resolve_wiki_path.py` unaffected. |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` | Subprocess-pytest regression test pinning the AC injection mechanism |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/fixtures_sampling.py` | marginal-quota validator + manifest schema loader + `check_floor_occupancy()` used by the session hook |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py` | six pure-function scorers implementing locked formulas (heading scorer uses `scipy.stats.kendalltau` on rank vectors) + shared `empty_safe_ratio()` helper used by dims 2-5 |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` | 20-entry manifest with full provenance fields |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` | JSON Schema enforcing required fields; referenced by validator |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` × 20 | frozen HTML snapshots |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.md` × 20 | oracle markdown — from-source authorship only |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/README.md` | blinding protocol + conflict-resolution procedure + 24-hour-delay solo-reviewer escape hatch |
| Modify | `.gitignore` | add `**/.artifacts/` repo-wide (per Gemini r1 suggestion, keeps convention uniform) |
| Modify | `pyproject.toml` (test/dev dependency group) | add **three pinned deps**: `pytest-socket` (any recent version), `zss==1.2.0` (Zhang-Shasha tree-edit distance for list-nesting scorer), `scipy>=1.11` (Kendall-tau for heading-preservation scorer). scipy is introduced here for the first time (attested: `grep -n scipy pyproject.toml` at HEAD returns no match). |
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

All scores in `[0.0, 1.0]`. Two implementers given the same `(actual_md, expected_md, html)` MUST produce bit-identical scores. Dimensions 2-5 all use the shared `empty_safe_ratio(actual_tokens, oracle_tokens, match_count)` helper defined in `rubric_scorers.py` (pseudocode in the Pseudocode section). The helper's contract — `both empty → 1.0`, `oracle empty / actual non-empty → 0.0`, `otherwise → match_count / max(|oracle|, 1)` — is invoked explicitly in each dimension below.

| # | Dimension | Formula (exact) |
|---|---|---|
| 1 | **Heading preservation** | Let `A`, `O` = ordered lists of `(level, normalized_text)` tuples extracted via regex `^(#{1,6})\s+(.*)$`. **Set component (Jaccard)**: `J = |set(A) ∩ set(O)| / |set(A) ∪ set(O)|` (if both empty → `J = 1.0`). **Order component (Kendall-tau on rank vectors of common elements)**: `I = set(A) ∩ set(O)`. If `|I| < 2`: `K = 1.0` (trivially well-ordered). Else: for each `h ∈ I` record `rank_A[h]` = index of `h` in `A` and `rank_O[h]` = index of `h` in `O`; compute `tau = scipy.stats.kendalltau(rank_A_vector, rank_O_vector).statistic` (returns τ in `[-1, 1]`); normalize to `[0, 1]` via `K = (tau + 1) / 2`. **Score = 0.7 * J + 0.3 * K**. |
| 2 | Link resolution | Parse `[text](href)` tokens from both. Let `H_a`, `H_o` = multisets of hrefs. `match_count = |H_a ∩ H_o|`. **Score = `empty_safe_ratio(H_a, H_o, match_count)`**. Explicitly: if `|H_a| == 0 and |H_o| == 0 → 1.0`; if `|H_o| == 0 and |H_a| > 0 → 0.0` (spurious links, token set written to per-topic JSON as `spurious_tokens`); otherwise `match_count / max(|H_o|, 1)`. Anchor (`#...`), `mailto:`, and `https://` links are counted in the same bucket; sub-score breakdown (internal / external / anchor) is recorded in the per-topic JSON for diagnostic purposes but does not factor into the gate score. |
| 3 | Table fidelity | Parse markdown tables via `\| ... \|` rows. Let `G_a`, `G_o` = row-major flattened cell strings (whitespace-normalized). `match_count = ` count of positions where `G_a[i] == G_o[i]` within the common prefix. **Score = `empty_safe_ratio(G_a, G_o, match_count)`**. Explicitly: if `|G_a| == 0 and |G_o| == 0 → 1.0` (introduction pages with no tables score 1.0, not 0.0 — this is the defect fixed in v4); if `|G_o| == 0 and |G_a| > 0 → 0.0` (spurious tables); otherwise `match_count / max(|G_o|, 1)`. Missing or extra tables: absent cells count as non-matching against the oracle grid. |
| 4 | Code-block fidelity | Parse fenced ` ```...``` ` blocks. Let `B_a`, `B_o` = lists of `(lang_tag, body_normalized)`. `match_count = Σ match_i` where `match_i = 1` iff lang tag equals AND body equals after stripping trailing whitespace on each line. **Score = `empty_safe_ratio(B_a, B_o, match_count)`**. Explicitly: if `|B_a| == 0 and |B_o| == 0 → 1.0` (no code blocks on either side — trivially well-matched); if `|B_o| == 0 and |B_a| > 0 → 0.0` (spurious code blocks); otherwise `match_count / max(|B_o|, 1)`. |
| 5 | **Image alt-text** | Parse `![alt](src)` tokens. Let `M_a = {normalized_src(i) → alt_a(i)}` and `M_o = {normalized_src(i) → alt_o(i)}`. Match by `src` first: `common = set(M_a.keys()) ∩ set(M_o.keys())`. For each oracle image with `src ∈ common`, `match_i = 1` iff `M_a[src] == M_o[src]`. `match_count = Σ match_i`. **Score = `empty_safe_ratio(M_a.keys(), M_o.keys(), match_count)`**. Explicitly: if `|M_a| == 0 and |M_o| == 0 → 1.0` (introduction pages with no images); if `|M_o| == 0 and |M_a| > 0 → 0.0` (spurious images); otherwise `match_count / max(|M_o|, 1)`. Unmatched oracle `src`s (dropped/reordered) contribute `0` to the numerator but still count in the denominator, producing a localized penalty rather than a positional cascade. |
| 6 | List nesting | Extract depth-trees `T_a`, `T_o` from bullet/ordered-list lines (leading whitespace → depth; `-`/`*`/`N.` markers). **Score**: if `size(T_a) == 0 and size(T_o) == 0 → 1.0` (explicit both-empty clause; a page with no lists scores 1.0). Else: `1 - zhang_shasha_tree_edit_distance(T_a, T_o) / max(size(T_a), size(T_o), 1)`. Tree size = node count. Zhang-Shasha implementation via `zss` package (pinned `zss==1.2.0`). (Note: Dim 6 does not use `empty_safe_ratio` directly because the formula is an edit-distance ratio rather than a match-count ratio, but the same both-empty semantics are applied.) |

**Per-topic floor and hard-min thresholds** (for the floor-occupancy rule):

| Dim | Per-topic floor | Hard-min (zero-tolerance) | MAX_BELOW_FLOOR (of 20) |
|---|---|---|---|
| 1 Heading | 0.90 | 0.70 | 2 |
| 2 Link | 0.90 | 0.70 | 2 |
| 3 Table | 0.85 | 0.70 | 2 |
| 4 Code | 0.90 | 0.70 | 2 |
| 5 Image alt | 0.80 | 0.70 | 2 |
| 6 List nesting | 0.85 | 0.70 | 2 |

**Rule (provably consistent)**: on any dimension `d`, fail the run iff `count(topic_scores[d] < per_topic_floor[d]) > 2` OR `count(topic_scores[d] < 0.70) > 0`. No aggregate-mean claim is made; the v1 mean-rule remains intentionally removed. Enforcement is in `pytest_sessionfinish` (subdirectory-scoped conftest), not in a pytest test — so ordering is not a concern.

---

## Oracle authorship and blinding protocol

**Required method:** `from-source`. The oracle author opens the raw `.html` snapshot and the published MadCap Flare target-rendering guidance (Orcina webhelp's rendered output in a browser, which is the *specification* of what the HTML should render to), then hand-writes the `.md` file. The author MUST NOT view `html_to_markdown()` output during authorship. Each oracle file carries a YAML-comment header:

```yaml
# oracle_authored_by: <reviewer-github-handle>
# oracle_review_method: from-source
# oracle_authored_at: <ISO-8601 UTC>
# oracle_second_reviewer: <second-reviewer-github-handle | "self-reviewed-with-24h-delay">
# single_reviewer_timelag: false   # true iff oracle_second_reviewer == "self-reviewed-with-24h-delay"
```

Matching fields are also required in `sample-manifest.yaml`. The validator test (`test_oracle_authorship_method_is_from_source`) fails the run on any `reviewed-from-output` row.

### Solo-contributor escape hatch (new in v4)

If a second reviewer is unavailable, the author may satisfy the two-reviewer requirement by **self-review with 24-hour cooling-off delay**:

1. At initial authorship time `T0`, the author writes the `.md` file against `.html` + live rendering only (no converter output viewed), commits the fixture with a `fixture(initial): <slug>` commit message, and records `oracle_authored_at: T0`.
2. At `T0 + >=24h`, the author re-opens the fixture, reads the current `html_to_markdown` output for comparison, and either confirms the fixture unchanged or amends it in a second commit `fixture(second-review): <slug>`.
3. Both commits must appear in `git log -- <fixture path>` for the fixture to be valid.
4. The manifest records `oracle_second_reviewer: self-reviewed-with-24h-delay` and `single_reviewer_timelag: true`.
5. Structural test `test_oracle_has_second_reviewer` accepts either a distinct handle OR the exact sentinel string `self-reviewed-with-24h-delay`.
6. A follow-up test `test_single_reviewer_timelag_has_two_commits` (folded into structural #8) verifies that fixtures marked `single_reviewer_timelag: true` have at least two commits in git history separated by ≥24 hours (queried via `git log --format=%aI -- <path>`).

The escape hatch is explicitly a fallback, not a first choice; fixtures with a distinct second reviewer are preferred whenever feasible.

### Conflict resolution (from v3, unchanged)

If two reviewers disagree on a cell of a complex table or a nested-list shape, the fixture README prescribes:
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
  oracle_second_reviewer: "<handle>"       # or literal "self-reviewed-with-24h-delay"
  single_reviewer_timelag: false           # true iff oracle_second_reviewer sentinel set
  oracle_review_method: from-source
```

`sample-manifest.schema.json` encodes these as required; the structural test `test_sample_manifest_schema_valid` runs the schema validation and fails on any missing field.

---

## TDD Test List (13 structural + 120 parametrized = 133 collected; aggregate floor-occupancy enforced by session hook; session-hook regression test lives in a separate test file)

### Structural (13)

| # | Test name | What it verifies |
|---|---|---|
| 1 | `test_sample_manifest_loads` | file parses; entry count == 20 (this test is what surfaces a collection-time loader failure, since the parametrize loader returns `[]` silently on error) |
| 2 | `test_sample_manifest_schema_valid` | entries conform to `sample-manifest.schema.json`; all required fields present |
| 3 | `test_sample_manifest_marginal_axes` | product/category/complexity marginals match declared quotas |
| 4 | `test_sample_manifest_hard_tier_encoding_stress` | `>=2` Hard-tier entries have `encoding_stress: true` |
| 5 | `test_sample_manifest_fixture_files_exist` | every entry's `html_path` and `oracle_md_path` resolve to non-empty tracked files |
| 6 | `test_sample_manifest_html_sha256_matches` | recomputed SHA-256 of each `.html` equals the manifest value |
| 7 | `test_oracle_authorship_method_is_from_source` | every entry has `oracle_review_method == "from-source"` |
| 8 | `test_oracle_has_second_reviewer` | every entry declares a non-empty `oracle_second_reviewer`; value is either distinct from `oracle_authored_by` OR the literal sentinel `self-reviewed-with-24h-delay`. If the sentinel is used, the fixture's git log is inspected: at least two commits touching `<oracle_md_path>` must exist, with `committer_date[1] - committer_date[0] >= 24h`. |
| 9 | `test_html_to_markdown_import` | `ingest_orcina.html_to_markdown` is importable via the hyphenated-path shim |
| 10 | `test_rubric_scorer_determinism` | running each scorer twice on the same inputs returns identical floats |
| 11 | `test_heading_preservation_detects_reordering` | (from v3) Constructs `A = "# H1\n# H2\n# H3"` and `O = "# H1\n# H3\n# H2"`. Asserts `heading_scorer(A, O, "") < 1.0` (i.e., the reordering penalty fires). Rank-vector formula: `tau ≈ 0.333`, `K ≈ 0.667`, `J = 1.0`, Score ≈ 0.9. |
| 12 | **`test_rubric_scorer_handles_empty_oracle_and_actual`** | **NEW in v4.** Given a fixture where the oracle markdown has zero tables, zero code blocks, zero images, zero links (an introduction page) AND the actual conversion also produces zero tokens of each type, asserts **all four** of `link_scorer`, `table_scorer`, `code_scorer`, and `image_scorer` return `1.0`. Asymmetric cases (oracle empty, actual non-empty) are asserted to return `0.0`. This test would have FAILED on dims 2-5 under v3's formula (which returned `0/1 = 0.0` for the both-empty case) and PASSES under v4's `empty_safe_ratio` helper. |
| 13 | `test_no_network_access` | `pytest-socket` is active within the `markdown_qa/` subdirectory; a live `socket.socket(AF_INET, SOCK_STREAM)` call raises `SocketBlockedError`. (Active probe lives here, not in the `_disable_network` fixture.) |

**Note:** v2's `test_aggregate_floor_occupancy` and `test_report_artifact_written` remain retired. Both concerns are handled by the `pytest_sessionfinish` hook in `markdown_qa/conftest.py`. The session-hook regression test lives in `test_session_hook_regression.py` as a separate file (see below) — it is counted outside the 13 structural tests because it exercises an injected failure mode via subprocess and is not part of the happy-path structural suite.

### Session-hook regression (separate test file, 1 case)

| # | Test name | What it verifies |
|---|---|---|
| R1 | `test_session_hook_fails_run_on_injected_violation` | Writes 3 known-bad per-topic JSONs (score = 0.50 on heading dim, count > MAX_BELOW_FLOOR) into a `tmp_path`-redirected artifacts dir via the `MARKDOWN_QA_ARTIFACTS_DIR` env var, invokes `subprocess.run([sys.executable, "-m", "pytest", ...], check=False)` against a trivial test file with the markdown_qa conftest loaded, asserts `returncode == 1` AND `"FLOOR-OCCUPANCY VIOLATIONS"` appears in stderr. Lives in a separate file so it can use subprocess without interfering with the parametrized suite. |

### Parametrized (120 = 6 dims × 20 topics)

| Test | Count | Notes |
|---|---|---|
| `test_per_topic_dimension[<slug>-<dim>]` | 120 | double-parametrized on `entry` × `dim`. Each case computes a single score and writes `<slug>-<dim>.json`. Per-topic assertion is informational (logged); the gate is enforced by the session hook. |

**Collection assertion**: `pytest --collect-only -q scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py | grep -cE "^[^ ]+::test_"` == `133`. Including the regression file: `pytest --collect-only -q scripts/data/llm-wiki/tests/markdown_qa/ | grep -cE "^[^ ]+::test_"` == `134`.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py --collect-only -q | grep -cE "^[^ ]+::test_"` returns exactly **133**.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/ --collect-only -q | grep -cE "^[^ ]+::test_"` returns exactly **134** (133 from `test_conversion_quality.py` + 1 from `test_session_hook_regression.py`).
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ --collect-only -q | grep -cE "^[^ ]+::test_"` returns **134 + (existing `test_resolve_wiki_path.py` count)** — the `markdown_qa/` subdirectory contributes exactly 134.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py -v` exits 0 on a clean corpus.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py -v` exits 0 (the regression test itself passes by subprocess-asserting that pytest on a synthetic violation returns exit code 1).
- [ ] 20 `.html` + 20 `.md` oracle pairs exist under `tests/fixtures/llm-wiki/conversion-oracle/` and are tracked by `git ls-files`.
- [ ] `sample-manifest.yaml` declares, for each of the 20 entries, all required provenance fields (including `single_reviewer_timelag`); `sample-manifest.schema.json` is the authoritative schema.
- [ ] All 20 entries have `oracle_review_method: from-source`.
- [ ] Every `oracle_second_reviewer` is either a distinct handle OR the exact sentinel `self-reviewed-with-24h-delay`; sentinel entries have `single_reviewer_timelag: true` AND ≥2 commits in git log for that fixture separated by ≥24h.
- [ ] `fixtures_sampling.py` validates marginal-only stratification and the Hard-tier encoding-stress floor, and fails on drift; also exports `check_floor_occupancy()` consumed by `conftest.py`.
- [ ] `scripts/data/llm-wiki/tests/markdown_qa/.artifacts/conversion-quality-report.json` is produced on every run by the `pytest_sessionfinish` hook; contains per-topic per-dimension scores and a `floor_occupancy_summary` block.
- [ ] All six rubric dimensions have their formulas documented in `rubric_scorers.py` module docstring and in this plan's Rubric section; the two MUST match. Dimensions 2-5 invoke `empty_safe_ratio()`; dimension 1 uses the explicit `J = 1.0` both-empty clause; dimension 6 uses an explicit both-empty `→ 1.0` clause before its edit-distance ratio.
- [ ] `pyproject.toml` test/dev dep group pins **`pytest-socket`**, **`zss==1.2.0`**, and **`scipy>=1.11`**; verified by `grep -E '(pytest-socket|zss==1\.2\.0|scipy>=1\.11)' pyproject.toml | wc -l` == 3. (Note: scipy is newly introduced — at base SHA `grep -n scipy pyproject.toml` returns no match.)
- [ ] `test_no_network_access` actively verifies the socket block; the `_disable_network` fixture contains activation only, no probe.
- [ ] `_disable_network` fixture lives in `scripts/data/llm-wiki/tests/markdown_qa/conftest.py`, NOT in `scripts/data/llm-wiki/tests/conftest.py`; sibling `test_resolve_wiki_path.py` runs with normal socket access. Verify by `uv run pytest scripts/data/llm-wiki/tests/test_resolve_wiki_path.py -v` passing without socket activation.
- [ ] `test_heading_preservation_detects_reordering` passes on v3's rank-vector formula (carried into v4 unchanged).
- [ ] `test_rubric_scorer_handles_empty_oracle_and_actual` passes — all four of dims 2-5 return 1.0 on a both-empty fixture. This test would fail under v3's pre-helper formulas.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` passes (both existing `test_resolve_wiki_path.py` and the new `markdown_qa/` subdirectory).

### Deferred / conditional

- [ ] **(Deferred)** Three-provider cross-review artifacts posted at `scripts/review/results/` against this v4's commit SHA. Unblock condition: codex-cli 0.124.0 stdin-hang (#2479) resolved OR explicit single-exception granted by user. Plan will not be moved to `status:plan-review` until Claude + Gemini r4 reviews (minimum two-provider) land under the v4 SHA. No self-approval is requested or implied.

---

## Build Sequence (TDD order)

1. Add `pytest-socket`, `zss==1.2.0`, `scipy>=1.11` to `pyproject.toml` test/dev group; run `uv sync` and assert all three import. (Attested: scipy is introduced here for the first time.)
2. Create `scripts/data/llm-wiki/tests/markdown_qa/__init__.py` (empty) and the subdirectory scaffold.
3. Write `sample-manifest.schema.json`.
4. Write `markdown_qa/fixtures_sampling.py` (validator + `check_floor_occupancy()`) with unit tests (folded into structural tests 3, 4, and the session-hook injection test).
5. Write `markdown_qa/rubric_scorers.py`. Implement `empty_safe_ratio()` helper first; then implement dims 2-5 against `test_rubric_scorer_handles_empty_oracle_and_actual` — RED first (the test should fail with a hypothetical non-helper implementation), then GREEN with the helper. Implement heading scorer last, against `test_heading_preservation_detects_reordering` — RED first, then GREEN with the rank-vector formula.
6. Write `markdown_qa/conftest.py` with the `pytest_sessionfinish` hook (including `MARKDOWN_QA_ARTIFACTS_DIR` env override) and the subdirectory-scoped session-autouse `_disable_network` fixture. Verify by running `uv run pytest scripts/data/llm-wiki/tests/test_resolve_wiki_path.py -v` and confirming it passes (sibling not affected by socket disable).
7. Write the 13 structural tests in `markdown_qa/test_conversion_quality.py`.
8. Author 20 blinded oracle fixtures following the protocol in `tests/fixtures/llm-wiki/conversion-oracle/README.md`. Solo contributors follow the 24-hour-delay path; multi-reviewer contributors follow the distinct-reviewer path.
9. Write the 120-case `test_per_topic_dimension` parametrized test; assert `--collect-only` count == 133 for the module and 134 for the subdirectory.
10. Write `markdown_qa/test_session_hook_regression.py` with `test_session_hook_fails_run_on_injected_violation`. Run it and assert it passes (i.e., subprocess pytest returns 1 on the injected violation).
11. Full green run under `uv run pytest scripts/data/llm-wiki/tests/ -v` (sibling + markdown_qa/ both green).

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

## Adversarial Review Summary (r3 — complete)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | 1 P2 escalated (empty-denominator defect on dims 2-5); 4 P3 (conftest scope; AC regression-test mechanism; solo-contributor blocker; scipy attestation unverified) |
| Codex | n/a | not produced — codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression` (#2479) |
| Gemini | **APPROVE** | clean; no findings |

**Overall r3 result:** MAJOR (Claude) → this v4 revision. Gemini's APPROVE does not dominate because Claude's P2 identifies a concrete scoring defect with corpus-realistic failure modes.

## Adversarial Review Summary (r4)

*Pending. Will be populated once r4 reviews land against this v4's commit SHA. Reviews produced against v1, v2, or v3 artifacts do not satisfy the revision-bound approval gate.*

---

## Risks and Open Questions

- **Risk (fixture drift):** Oracle markdown is authored manually against HTML + live rendering. Mitigation — two-reviewer sign-off required OR documented 24-hour-delay self-review path, explicit blinding protocol, conflict-resolution procedure in fixture README, and a swap-and-replace path if disagreement survives.
- **Risk (orcina.com content change):** HTML snapshots may diverge from live pages. Mitigation — `html_sha256` + `fetched_at` + `source_url` captured per entry. A refresh job is out of scope for this plan; #2125 (auto-refresh) is the natural home.
- **Risk (scorer coupling to parser quirks):** Rubric scorers parse markdown with regexes/custom logic. Two independent implementations could still disagree on malformed inputs. Mitigation — `test_rubric_scorer_determinism` asserts repeatability; the README documents that ill-formed corner cases score `0.0` by policy.
- **Risk (`zss` / `scipy` offline availability):** Both are external packages. Mitigation — pinned versions declared in `pyproject.toml`; `uv` prefers the wheel cache under offline execution. If offline CI turns out to lack them, the remediation is to pre-populate the wheel cache, NOT to vendor in-tree (explicitly out of scope here to keep surface area small).
- **Risk (`pytest-socket` + unix-socket subprocess IPC):** `allow_unix_socket=False` is the strict setting; some tooling (e.g., `uv` subprocess IPC in certain modes) may rely on unix sockets. Mitigation — fixture is now scoped to `markdown_qa/` subdirectory only, and an actual CI probe is listed in Build Sequence step 6.
- **Risk (session hook vs isolated invocation):** When the whole test module is NOT collected (e.g., `pytest -k missing_pattern`), no per-topic artifacts are written. The `pytest_sessionfinish` hook detects the empty-artifacts case and returns without altering `exitstatus`, so it never spuriously fails a narrow run. Documented in `conftest.py` docstring.
- **Risk (duplicate-heading question from Gemini r2 P3):** The heading-preservation Jaccard is over sets of `(level, normalized_text)` tuples. If two distinct headings have the same `(level, text)` (rare in Orcina webhelp, common in other corpora), they collapse into a single set element. Mitigation — documented in `rubric_scorers.py` docstring as a known, accepted corpus-specific quirk; does not affect the 20-topic Orcina sample.
- **Risk (solo-reviewer time-lag gaming):** A contributor could commit fixtures in two back-to-back commits and forge the 24-hour window by rewriting `committer_date`. Mitigation — test #8 uses `%aI` (author-date ISO-8601) which is hard to rewrite post-push without a force-push; the review process is expected to spot-check recent fixtures' git history. This is a protocol-level risk, accepted for solo-contributor viability.
- **Open:** Whether `**/.artifacts/` belongs in the repo-wide `.gitignore` (Gemini suggestion) or remains scoped. Current recommendation — repo-wide, because the same pattern will recur elsewhere. Flag for user confirmation.
- **Open:** Whether r4 can proceed with two providers (Claude + Gemini) given the codex-cli regression, or whether the plan waits for #2479 resolution. Decision belongs to the user; see deferred AC above.

---

## Complexity: T3

**T3** — 20 blinded hand-authored oracle files × 3 products + 6 rubric scorers (with shared `empty_safe_ratio` helper) + 3 new test deps (`pytest-socket`, `zss==1.2.0`, `scipy>=1.11` — scipy newly introduced) + 13 structural tests + session hook + session-hook regression test + JSON Schema + two-reviewer blinding protocol with documented solo-contributor escape hatch. Bumped from T2 at v3 per r2 Claude P3 and r2 Gemini P3 consensus; v4 does not re-adjust. Scope remains test/QA only (no production code modified); TDD required; deterministic and offline.
