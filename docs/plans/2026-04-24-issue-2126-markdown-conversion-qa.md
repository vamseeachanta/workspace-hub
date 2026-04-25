# Plan for #2126: test(llm-wiki): validate markdown conversion quality across all 717 topics

> **Status:** draft (v5 — addresses r4 findings)
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
> - r4 Claude (MAJOR): `scripts/review/results/20260424T202908Z-plan-2126-v4.md-plan-claude.md`
> - r4 Gemini (APPROVE): `scripts/review/results/20260424T203144Z-plan-2126-v4.md-plan-gemini.md`
> - r1/r2/r3/r4 Codex: not produced (codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression`; tracked in #2479)
> - r5 artifacts: pending; revision-bound to this v5 (paths and SHA to be recorded below once reviews land)

---

## Review History

### v1 → v2 → v3 → v4 (r1/r2/r3 resolutions, for context)
Carried forward unchanged from v4. Summary:
- r1 → v2: parametrize arithmetic (133 collected); per-topic floor-occupancy rule replaces aggregate-mean; marginal-only stratification; oracle blinding; formulas locked; `pytest-socket` active probe; Attested Evidence block.
- r2 → v3: `pytest_sessionfinish` hook replaces `test_aggregate_floor_occupancy`; rank-vector Kendall-tau formula + `scipy>=1.11`; structural regression test; pyproject pins; collection-safe manifest loader; AC grep pattern unified; positional image match replaced with src-keyed match; Artifact Map stubs corrected; `_disable_network` cleaned; Attested Evidence scorer-lib checks added.
- r3 → v4: shared `empty_safe_ratio` helper for dims 2-5 + explicit per-dimension application; `_disable_network` scope narrowed by relocating module to `markdown_qa/` subdirectory; AC injection mechanism pinned to a `test_session_hook_regression.py` file; solo-contributor 24-hour-delay escape hatch; scipy attestation corrected (was NOT pre-declared).

### v4 → v5 deltas (this revision)

| Finding | Severity (r4) | Resolution in v5 |
|---|---|---|
| Subprocess regression test in v4 used a broken pytest `-p` argument with the dotted form `scripts.data.<hyphenated-dir>.tests.markdown_qa.conftest`, which is broken Python dotted-path syntax (hyphen in the `llm-wiki` directory name invalidates the module name; also `-p` loads plugins not conftest files). The hook would never be invoked → AC-injection mechanism would be effectively unspecified. | **P1 (Claude r4)** | **Resolved:** rewrote the regression test to use a **pure filesystem path** invocation that does NOT use any Python dotted name below `scripts/data/llm-wiki/`. The new approach copies (or symlinks) `markdown_qa/conftest.py` and a trivial `trivial_test.py` into `tmp_path`, then runs `python -m pytest <tmp_path>` (filesystem path only) so pytest discovers conftest by the normal rootdir-walk. No `-p` flag, no dotted import. Verified this v5 draft contains zero literal-hyphen-then-dot occurrences for the `llm-wiki` directory token. The systemic hazard recorded in `feedback_llm_wiki_hyphen_module_path_pattern` is acknowledged here as the recurrence root cause. |
| `MARKDOWN_QA_ARTIFACTS_DIR` env-seam not in conftest.py pseudocode — only mentioned parenthetically | **P2 (Claude r4)** | **Resolved:** the env override is now spelled directly into the `conftest.py` pseudocode at the point of `ARTIFACTS_DIR` definition: `ARTIFACTS_DIR = Path(os.environ.get("MARKDOWN_QA_ARTIFACTS_DIR", str(Path(__file__).parent / ".artifacts" / "per-topic")))`. Two implementers following the plan exactly will produce a conftest the regression test can exercise. The same env name is used in CI overrides (e.g., a CI runner can redirect artifacts to a workspace-scoped path without code changes). |
| Solo-reviewer 24-hour-delay escape hatch permits reading converter output at sign-off — weakens blinding (the first commit is blinded; the second is not, against converter drift) | **P2 (Claude r4)** | **Resolved:** tightened the protocol so the T0+24h re-review reads **ONLY the rendered HTML page** (rendered in a browser via the recorded `source_url` at the recorded `fetched_at` timestamp), NOT the converter output (markdown). The reviewer is explicitly forbidden from opening `html_to_markdown()` output during the second pass. Rationale: the 24-hour delay provides temporal detachment so the author re-reads HTML fresh; converter comparison is a separate, weaker concession that is now excluded. Risks section flags the residual single-author bias that remains even with this tightening. |
| `test_oracle_has_second_reviewer` parses `git log` for the 24h interval check, which fails under shallow CI clones (default `fetch-depth: 1`) | **P3 (Claude r4)** | **Resolved:** added `oracle_authored_at` (already present) and **`oracle_reviewed_at`** (new manifest field, required for sentinel entries only) to the manifest schema. Test #8 compares these two ISO-8601 timestamps directly, never reading git log for the interval. CI clone depth becomes irrelevant. The schema validator (test #2) requires `oracle_reviewed_at` when `single_reviewer_timelag: true`. |
| Collection-count ACs use `grep -cE "^[^ ]+::test_"` against `pytest -q` output, which is format-unstable across versions and terminal widths | **P3 (Claude r4)** | **Resolved:** AC grep pattern switched to the more tolerant `\| grep -c '::'` form, paired with explicit `-p no:cacheprovider` flag for stable output. New form: `pytest --collect-only --quiet -p no:cacheprovider <path> \| grep -c '::'`. |
| `test_rubric_scorer_handles_empty_oracle_and_actual` only asserts two of four quadrants explicitly | **P3 (Claude r4)** | **Resolved:** test #12 now asserts **all four quadrants** explicitly: (a) both empty → 1.0; (b) oracle empty / actual non-empty → 0.0; (c) oracle non-empty / actual empty → 0.0; (d) both non-empty with partial match → expected ratio. The four-quadrant matrix is enumerated in the TDD table. |
| `test_heading_preservation_detects_reordering` asserts a specific float (Score ≈ 0.9) that depends on scipy version | **(suggestion only, Claude r4)** | **Resolved:** test now asserts a tolerance band rather than an exact float: `0.85 <= score <= 0.95` AND `score < 1.0`. Documented in the test's docstring. |
| Whether to proceed with two-provider review (Claude + Gemini) given codex-cli #2479 unresolved | **(question, both r4)** | **Resolved:** the deferred AC now declares the user's policy explicitly: **r5 will proceed with Claude + Gemini two-provider coverage** (no indefinite block on #2479). Codex review will be added retroactively if the codex-cli regression is resolved before merge; otherwise the plan is approved on two-provider coverage alone with the codex-cli regression cited as the documented exception per memory `feedback_codex_cli_0_124_upstream_regression`. |
| Gemini r4 suggestion: add `**/.artifacts/` to repo-wide `.gitignore` | **(suggestion only, Gemini r4)** | **Resolved:** Files-to-Change retains the repo-wide `**/.artifacts/` `.gitignore` entry (already present in v4); plan now records the affirmative decision rather than leaving it open. |

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
- Memory file `feedback_llm_wiki_hyphen_module_path_pattern` — explicitly consulted for v5 to prevent recurrence of the v4 P1.

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
- Decision: v5 retains v4's **subdirectory option** (`scripts/data/llm-wiki/tests/markdown_qa/`) as a defense-in-depth choice — it prevents *future* sibling additions from silently inheriting the socket disable and keeps the fixture's blast radius equal to its intent.

**Hyphen-path hazard probe** (verify via the shown command, run against this v5 plan file before submission):
- Command: `grep -c 'llm-wiki\.' /tmp/plan-drafts/plan-2126-v5.md`
- Expected result: `0` matches. Any non-zero result indicates a recurrence of the v4 P1 defect and the plan must be regrepped/repaired before submission.

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
| Test module | `scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py` |
| Session hook + scoped fixture | `scripts/data/llm-wiki/tests/markdown_qa/conftest.py` |
| Session-hook regression test (rewritten in v5 to avoid hyphen-dotted-path) | `scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` |
| Sampling helper | `scripts/data/llm-wiki/tests/markdown_qa/fixtures_sampling.py` |
| Rubric scorer helper | `scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py` |
| Subdirectory package anchor | `scripts/data/llm-wiki/tests/markdown_qa/__init__.py` |
| Oracle fixtures | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` + `{slug}.md` |
| Stratification manifest | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` |
| Manifest JSON Schema | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` |
| Oracle authoring checklist | `tests/fixtures/llm-wiki/conversion-oracle/README.md` |
| Rubric report (generated, gitignored) | `scripts/data/llm-wiki/tests/markdown_qa/.artifacts/conversion-quality-report.json` |
| Plan review r5 — Claude | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-claude.md` |
| Plan review r5 — Codex | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-codex.md` (conditional on codex-cli fix #2479) |
| Plan review r5 — Gemini | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-gemini.md` |

---

## Deliverable

A self-contained pytest module `test_conversion_quality.py` under `scripts/data/llm-wiki/tests/markdown_qa/`, plus a subdirectory-scoped `conftest.py` that enforces the aggregate floor-occupancy gate AFTER all parametrized runs complete, plus a `test_session_hook_regression.py` that copies the conftest into a `tmp_path` and runs `python -m pytest <tmp_path>` (filesystem-path-only, no Python dotted reference below the hyphenated `llm-wiki/` directory) with a synthetic violation, asserting exit-code 1, plus 20 oracle-backed HTML/markdown fixtures under `tests/fixtures/llm-wiki/conversion-oracle/`. The module executes `html_to_markdown()` on stratified topics, scores each output against six rubric dimensions with locked formulas (all six use the shared `empty_safe_ratio` helper where applicable), and fails the run when the floor-occupancy rule is violated. Strict offline enforcement via `pytest-socket` is scoped to the `markdown_qa/` subdirectory so sibling tests are not affected (an active `SocketBlockedError` probe lives in a structural test). Oracle authorship is blinded from current converter output at both T0 and the T0+24h re-review (re-review is HTML-only, never converter output).

---

## Pseudocode

### Subdirectory-scoped conftest.py (v5 — env-seam in pseudocode, not just prose)

```python
# scripts/data/llm-wiki/tests/markdown_qa/conftest.py
# ---------------------------------------------------
# This conftest applies ONLY to tests under markdown_qa/.
# Sibling tests under scripts/data/llm-wiki/tests/ (e.g., test_resolve_wiki_path.py)
# are NOT affected by the socket disable or the session-finish hook.

import os
import sys
import json
from pathlib import Path
import pytest

# v5: env-seam now spelled into the source. The regression test sets this
# env var to redirect artifacts into a tmp_path; CI may also set it to point
# the artifacts dir at a workspace-scoped path. Default falls back to the
# in-repo .artifacts/ tree.
ARTIFACTS_DIR = Path(os.environ.get(
    "MARKDOWN_QA_ARTIFACTS_DIR",
    str(Path(__file__).parent / ".artifacts" / "per-topic"),
))

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
    from fixtures_sampling import check_floor_occupancy  # sibling import
    violations = check_floor_occupancy(per_topic)
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

### Shared empty-safe helper (carried forward from v4, unchanged)

```python
# scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py

def empty_safe_ratio(actual_tokens, oracle_tokens, match_count):
    """Shared denominator-safe ratio used by dims 2-5.

    Rule:
      - both empty       → 1.0   (trivially well-matched; no regression vs oracle)
      - oracle empty,
        actual non-empty → 0.0   (spurious content against empty oracle)
      - oracle non-empty,
        actual empty     → 0.0   (missed all oracle tokens; falls through naturally)
      - otherwise        → match_count / max(len(oracle_tokens), 1)
    """
    a, o = len(actual_tokens), len(oracle_tokens)
    if a == 0 and o == 0:
        return 1.0
    if o == 0 and a > 0:
        return 0.0  # asymmetric: false-positive tokens on an empty oracle
    return match_count / max(o, 1)
```

### Session-hook regression test (REWRITTEN in v5 — filesystem-path-only)

```python
# scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py
#
# v5 rewrite: avoids ALL Python dotted paths below the hyphenated `llm-wiki/`
# directory (per memory feedback_llm_wiki_hyphen_module_path_pattern).
#
# Strategy: copy the markdown_qa/conftest.py and a trivial test file into
# tmp_path, then invoke `python -m pytest <tmp_path>` (filesystem path only).
# pytest auto-discovers conftest.py via rootdir walk — no `-p` flag, no
# dotted module name, no plugin syntax. The hyphenated directory is never
# referenced in any importable form.

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
SOURCE_CONFTEST = THIS_DIR / "conftest.py"
SOURCE_FIXTURES_SAMPLING = THIS_DIR / "fixtures_sampling.py"

def test_session_hook_fails_run_on_injected_violation(tmp_path):
    """Inject 3 below-floor per-topic JSONs (MAX_BELOW_FLOOR=2) into a
    tmp artifacts dir, then run pytest in tmp_path with the conftest copied
    in so it auto-loads. Assert exit code 1 and that the violation message
    appears in stderr."""
    # 1. Copy the real conftest.py and its sibling helper into tmp_path so
    #    pytest discovers them via normal rootdir walk. Filesystem-only —
    #    no Python dotted path is ever used.
    shutil.copy(SOURCE_CONFTEST, tmp_path / "conftest.py")
    shutil.copy(SOURCE_FIXTURES_SAMPLING, tmp_path / "fixtures_sampling.py")

    # 2. Build a synthetic .artifacts/per-topic dir with 3 below-floor entries.
    synthetic_artifacts = tmp_path / ".artifacts" / "per-topic"
    synthetic_artifacts.mkdir(parents=True)
    for slug in ["a", "b", "c"]:
        (synthetic_artifacts / f"{slug}-heading.json").write_text(
            json.dumps({"slug": slug, "dim": "heading", "score": 0.50})
        )

    # 3. Write a trivial test file so pytest has something to collect.
    (tmp_path / "test_trivial.py").write_text("def test_noop():\n    assert True\n")

    # 4. Invoke pytest against tmp_path. The MARKDOWN_QA_ARTIFACTS_DIR env
    #    var (read by the env-seam in conftest.py) redirects ARTIFACTS_DIR
    #    to our synthetic tree. No -p flag; conftest auto-discovered.
    env = {
        **os.environ,
        "MARKDOWN_QA_ARTIFACTS_DIR": str(synthetic_artifacts),
    }
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-q",
         "-p", "no:cacheprovider"],
        env=env,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1, (
        f"Session hook did not fail run on injected violation; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert b"FLOOR-OCCUPANCY VIOLATIONS" in result.stderr
```

(The `MARKDOWN_QA_ARTIFACTS_DIR` env override is implemented in `conftest.py` per the env-seam pseudocode above. The `-p no:cacheprovider` flag stabilizes pytest output; it disables the optional cache plugin, NOT a custom plugin reference.)

Formula pseudocode for composite scorers is given in the "Rubric dimensions and formulas" section below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/tests/markdown_qa/__init__.py` | Empty package anchor for the new subdirectory |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py` | pytest module — per-topic scoring + 13 structural tests |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/conftest.py` | Subdirectory-scoped `pytest_sessionfinish` hook + `_disable_network` session-autouse fixture + `MARKDOWN_QA_ARTIFACTS_DIR` env-seam (v5). Scope is `markdown_qa/` only; sibling `test_resolve_wiki_path.py` unaffected. |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` | Filesystem-path-only subprocess regression test pinning the AC injection mechanism (v5 rewrite) |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/fixtures_sampling.py` | marginal-quota validator + manifest schema loader + `check_floor_occupancy()` used by the session hook |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py` | six pure-function scorers implementing locked formulas (heading scorer uses `scipy.stats.kendalltau` on rank vectors) + shared `empty_safe_ratio()` helper used by dims 2-5 |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` | 20-entry manifest with full provenance fields including `oracle_reviewed_at` for sentinel rows (v5) |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` | JSON Schema enforcing required fields including conditional `oracle_reviewed_at` |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` × 20 | frozen HTML snapshots |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.md` × 20 | oracle markdown — from-source authorship only |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/README.md` | blinding protocol + conflict-resolution procedure + 24-hour-delay solo-reviewer escape hatch (v5: re-review reads HTML only, never converter output) |
| Modify | `.gitignore` | add `**/.artifacts/` repo-wide (per Gemini r1/r4 suggestion, keeps convention uniform) |
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

All scores in `[0.0, 1.0]`. Two implementers given the same `(actual_md, expected_md, html)` MUST produce bit-identical scores (modulo scipy version variance on dim 1, see test #11 tolerance band). Dimensions 2-5 all use the shared `empty_safe_ratio(actual_tokens, oracle_tokens, match_count)` helper defined in `rubric_scorers.py` (pseudocode in the Pseudocode section). The helper's contract — `both empty → 1.0`, `oracle empty / actual non-empty → 0.0`, `oracle non-empty / actual empty → 0.0` (falls through to `0 / max(|oracle|, 1)`), `otherwise → match_count / max(|oracle|, 1)` — is invoked explicitly in each dimension below.

| # | Dimension | Formula (exact) |
|---|---|---|
| 1 | **Heading preservation** | Let `A`, `O` = ordered lists of `(level, normalized_text)` tuples extracted via regex `^(#{1,6})\s+(.*)$`. **Set component (Jaccard)**: `J = |set(A) ∩ set(O)| / |set(A) ∪ set(O)|` (if both empty → `J = 1.0`). **Order component (Kendall-tau on rank vectors of common elements)**: `I = set(A) ∩ set(O)`. If `|I| < 2`: `K = 1.0` (trivially well-ordered). Else: for each `h ∈ I` record `rank_A[h]` = index of `h` in `A` and `rank_O[h]` = index of `h` in `O`; compute `tau = scipy.stats.kendalltau(rank_A_vector, rank_O_vector).statistic` (returns τ in `[-1, 1]`); normalize to `[0, 1]` via `K = (tau + 1) / 2`. **Score = 0.7 * J + 0.3 * K**. |
| 2 | Link resolution | Parse `[text](href)` tokens from both. Let `H_a`, `H_o` = multisets of hrefs. `match_count = |H_a ∩ H_o|`. **Score = `empty_safe_ratio(H_a, H_o, match_count)`**. Explicitly: if `|H_a| == 0 and |H_o| == 0 → 1.0`; if `|H_o| == 0 and |H_a| > 0 → 0.0` (spurious links, token set written to per-topic JSON as `spurious_tokens`); otherwise `match_count / max(|H_o|, 1)`. Anchor (`#...`), `mailto:`, and `https://` links are counted in the same bucket; sub-score breakdown (internal / external / anchor) is recorded in the per-topic JSON for diagnostic purposes but does not factor into the gate score. |
| 3 | Table fidelity | Parse markdown tables via `\| ... \|` rows. Let `G_a`, `G_o` = row-major flattened cell strings (whitespace-normalized). `match_count = ` count of positions where `G_a[i] == G_o[i]` within the common prefix. **Score = `empty_safe_ratio(G_a, G_o, match_count)`**. Explicitly: if `|G_a| == 0 and |G_o| == 0 → 1.0` (introduction pages with no tables score 1.0, not 0.0 — defect fixed in v4); if `|G_o| == 0 and |G_a| > 0 → 0.0` (spurious tables); otherwise `match_count / max(|G_o|, 1)`. Missing or extra tables: absent cells count as non-matching against the oracle grid. |
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
# oracle_reviewed_at: <ISO-8601 UTC>     # required when sentinel used; >=24h after authored_at
# single_reviewer_timelag: false   # true iff oracle_second_reviewer == "self-reviewed-with-24h-delay"
```

Matching fields are also required in `sample-manifest.yaml`. The validator test (`test_oracle_authorship_method_is_from_source`) fails the run on any `reviewed-from-output` row.

### Solo-contributor escape hatch (v5: tightened blinding)

If a second reviewer is unavailable, the author may satisfy the two-reviewer requirement by **self-review with 24-hour cooling-off delay**, under a strictly-blinded protocol:

1. At initial authorship time `T0`, the author writes the `.md` file against `.html` + live rendering only (no converter output viewed), commits the fixture with a `fixture(initial): <slug>` commit message, and records `oracle_authored_at: T0` in the manifest.
2. At `T0 + >=24h`, the author re-opens the fixture and re-reads **ONLY the rendered HTML page** (open `source_url` in a browser, OR open the saved `.html` snapshot in a browser to render it locally). The author **MUST NOT** view `html_to_markdown()` output during the re-review. Confirms the fixture unchanged or amends it in a second commit `fixture(second-review): <slug>`. The `oracle_reviewed_at` manifest field is set to the re-review timestamp.
3. The manifest records `oracle_second_reviewer: self-reviewed-with-24h-delay`, `single_reviewer_timelag: true`, and `oracle_reviewed_at: <ISO-8601 UTC>`.
4. Structural test `test_oracle_has_second_reviewer` accepts either a distinct handle OR the exact sentinel string `self-reviewed-with-24h-delay`. For sentinel entries, it compares `oracle_reviewed_at - oracle_authored_at >= 24h` directly from manifest fields (no git-log parsing — robust under shallow CI clones).
5. The README protocol explicitly forbids opening `html_to_markdown()` output at any point during initial authorship OR re-review. Violating this is a fixture-level defect that voids the oracle.

The escape hatch is explicitly a fallback, not a first choice; fixtures with a distinct second reviewer are preferred whenever feasible. Even with the tightened HTML-only re-review, a residual single-author bias remains (one human's interpretation of HTML may be systematically idiosyncratic) — see Risks.

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
  oracle_second_reviewer: "<handle>"            # or literal "self-reviewed-with-24h-delay"
  oracle_reviewed_at: 2026-04-25T15:00:00Z      # REQUIRED when sentinel used; OPTIONAL for distinct-reviewer rows
  single_reviewer_timelag: false                 # true iff oracle_second_reviewer sentinel set
  oracle_review_method: from-source
```

`sample-manifest.schema.json` encodes these as required; `oracle_reviewed_at` is conditionally required (required when `single_reviewer_timelag: true`). The structural test `test_sample_manifest_schema_valid` runs the schema validation and fails on any missing field.

---

## TDD Test List (13 structural + 120 parametrized = 133 collected; aggregate floor-occupancy enforced by session hook; session-hook regression test lives in a separate test file)

### Structural (13)

| # | Test name | What it verifies |
|---|---|---|
| 1 | `test_sample_manifest_loads` | file parses; entry count == 20 (this test is what surfaces a collection-time loader failure, since the parametrize loader returns `[]` silently on error) |
| 2 | `test_sample_manifest_schema_valid` | entries conform to `sample-manifest.schema.json`; all required fields present; conditional `oracle_reviewed_at` present when `single_reviewer_timelag: true` |
| 3 | `test_sample_manifest_marginal_axes` | product/category/complexity marginals match declared quotas |
| 4 | `test_sample_manifest_hard_tier_encoding_stress` | `>=2` Hard-tier entries have `encoding_stress: true` |
| 5 | `test_sample_manifest_fixture_files_exist` | every entry's `html_path` and `oracle_md_path` resolve to non-empty tracked files |
| 6 | `test_sample_manifest_html_sha256_matches` | recomputed SHA-256 of each `.html` equals the manifest value |
| 7 | `test_oracle_authorship_method_is_from_source` | every entry has `oracle_review_method == "from-source"` |
| 8 | `test_oracle_has_second_reviewer` | every entry declares a non-empty `oracle_second_reviewer`; value is either distinct from `oracle_authored_by` OR the literal sentinel `self-reviewed-with-24h-delay`. **For sentinel entries (v5):** asserts `oracle_reviewed_at - oracle_authored_at >= 24h` by parsing the two manifest ISO-8601 timestamps directly (NO git log read; robust under shallow CI clones). |
| 9 | `test_html_to_markdown_import` | `ingest_orcina.html_to_markdown` is importable via the hyphenated-path shim (`importlib.util.spec_from_file_location`) |
| 10 | `test_rubric_scorer_determinism` | running each scorer twice on the same inputs returns identical floats |
| 11 | `test_heading_preservation_detects_reordering` | (carried from v3, v5 tolerance) Constructs `A = "# H1\n# H2\n# H3"` and `O = "# H1\n# H3\n# H2"`. Asserts `0.85 <= heading_scorer(A, O, "") <= 0.95` AND `score < 1.0` (i.e., the reordering penalty fires within a tolerance band that absorbs scipy version differences). Approximate values: `tau ≈ 0.333`, `K ≈ 0.667`, `J = 1.0`, Score ≈ 0.9. |
| 12 | **`test_rubric_scorer_handles_empty_oracle_and_actual` (v5: 4-quadrant)** | **Asserts all four quadrants explicitly for each of `link_scorer`, `table_scorer`, `code_scorer`, `image_scorer`:** (a) both empty → 1.0; (b) oracle empty, actual non-empty → 0.0 (spurious-content path); (c) oracle non-empty, actual empty → 0.0 (missed-all-tokens path; falls through to `0/max(|o|,1)`); (d) both non-empty with partial match (e.g., 1 of 2 oracle tokens matched) → 0.5 (the expected ratio). This test would have FAILED on dims 2-5 under v3's pre-helper formulas and PASSES under v4/v5's `empty_safe_ratio` helper. |
| 13 | `test_no_network_access` | `pytest-socket` is active within the `markdown_qa/` subdirectory; a live `socket.socket(AF_INET, SOCK_STREAM)` call raises `SocketBlockedError`. (Active probe lives here, not in the `_disable_network` fixture.) |

**Note:** v2's `test_aggregate_floor_occupancy` and `test_report_artifact_written` remain retired. Both concerns are handled by the `pytest_sessionfinish` hook in `markdown_qa/conftest.py`. The session-hook regression test lives in `test_session_hook_regression.py` as a separate file (see below) — counted outside the 13 structural tests because it exercises an injected failure mode via subprocess and is not part of the happy-path structural suite.

### Session-hook regression (separate test file, 1 case — v5 rewritten)

| # | Test name | What it verifies |
|---|---|---|
| R1 | `test_session_hook_fails_run_on_injected_violation` | **v5 rewrite:** copies `markdown_qa/conftest.py` and `markdown_qa/fixtures_sampling.py` into `tmp_path` via `shutil.copy()`, writes 3 known-bad per-topic JSONs (score = 0.50 on heading dim, count > MAX_BELOW_FLOOR) into a `tmp_path / .artifacts / per-topic` dir, sets `MARKDOWN_QA_ARTIFACTS_DIR` in subprocess env, then invokes `subprocess.run([sys.executable, "-m", "pytest", str(tmp_path), "-q", "-p", "no:cacheprovider"], check=False)`. Asserts `returncode == 1` AND `b"FLOOR-OCCUPANCY VIOLATIONS" in result.stderr`. **Filesystem path only** — no Python dotted reference below the hyphenated `llm-wiki/` directory; `-p no:cacheprovider` disables the optional pytest cache plugin (NOT a custom plugin reference). |

### Parametrized (120 = 6 dims × 20 topics)

| Test | Count | Notes |
|---|---|---|
| `test_per_topic_dimension[<slug>-<dim>]` | 120 | double-parametrized on `entry` × `dim`. Each case computes a single score and writes `<slug>-<dim>.json`. Per-topic assertion is informational (logged); the gate is enforced by the session hook. |

**Collection assertion (v5: tolerant grep)**: `pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py | grep -c '::'` == `133`. Including the regression file: `pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/markdown_qa/ | grep -c '::'` == `134`.

---

## Acceptance Criteria

- [ ] `uv run pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py | grep -c '::'` returns exactly **133**.
- [ ] `uv run pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/markdown_qa/ | grep -c '::'` returns exactly **134** (133 from `test_conversion_quality.py` + 1 from `test_session_hook_regression.py`).
- [ ] `uv run pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/ | grep -c '::'` returns **134 + (existing `test_resolve_wiki_path.py` count)** — the `markdown_qa/` subdirectory contributes exactly 134.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py -v` exits 0 on a clean corpus.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py -v` exits 0 (the regression test itself passes by subprocess-asserting that pytest on a synthetic violation returns exit code 1).
- [ ] 20 `.html` + 20 `.md` oracle pairs exist under `tests/fixtures/llm-wiki/conversion-oracle/` and are tracked by `git ls-files`.
- [ ] `sample-manifest.yaml` declares, for each of the 20 entries, all required provenance fields (including `single_reviewer_timelag` and conditional `oracle_reviewed_at`); `sample-manifest.schema.json` is the authoritative schema.
- [ ] All 20 entries have `oracle_review_method: from-source`.
- [ ] Every `oracle_second_reviewer` is either a distinct handle OR the exact sentinel `self-reviewed-with-24h-delay`; sentinel entries have `single_reviewer_timelag: true` AND `oracle_reviewed_at - oracle_authored_at >= 24h` (compared from manifest fields, NOT git log).
- [ ] `fixtures_sampling.py` validates marginal-only stratification and the Hard-tier encoding-stress floor, and fails on drift; also exports `check_floor_occupancy()` consumed by `conftest.py`.
- [ ] `scripts/data/llm-wiki/tests/markdown_qa/.artifacts/conversion-quality-report.json` is produced on every run by the `pytest_sessionfinish` hook; contains per-topic per-dimension scores and a `floor_occupancy_summary` block.
- [ ] All six rubric dimensions have their formulas documented in `rubric_scorers.py` module docstring and in this plan's Rubric section; the two MUST match. Dimensions 2-5 invoke `empty_safe_ratio()`; dimension 1 uses the explicit `J = 1.0` both-empty clause; dimension 6 uses an explicit both-empty `→ 1.0` clause before its edit-distance ratio.
- [ ] `pyproject.toml` test/dev dep group pins **`pytest-socket`**, **`zss==1.2.0`**, and **`scipy>=1.11`**; verified by `grep -E '(pytest-socket|zss==1\.2\.0|scipy>=1\.11)' pyproject.toml | wc -l` == 3. (Note: scipy is newly introduced — at base SHA `grep -n scipy pyproject.toml` returns no match.)
- [ ] `test_no_network_access` actively verifies the socket block; the `_disable_network` fixture contains activation only, no probe.
- [ ] `_disable_network` fixture lives in `scripts/data/llm-wiki/tests/markdown_qa/conftest.py`, NOT in `scripts/data/llm-wiki/tests/conftest.py`; sibling `test_resolve_wiki_path.py` runs with normal socket access. Verify by `uv run pytest scripts/data/llm-wiki/tests/test_resolve_wiki_path.py -v` passing without socket activation.
- [ ] `conftest.py` reads `ARTIFACTS_DIR` from the `MARKDOWN_QA_ARTIFACTS_DIR` env var with a fallback to the in-repo path; verified by source inspection AND by the session-hook regression test exercising the env override.
- [ ] `test_session_hook_regression.py` uses ONLY filesystem paths and never references any Python dotted name below the hyphenated `llm-wiki/` directory; verified by `grep -c 'llm-wiki\.' scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` returning 0.
- [ ] `test_heading_preservation_detects_reordering` asserts a tolerance band `0.85 <= score <= 0.95 AND score < 1.0` (not an exact float).
- [ ] `test_rubric_scorer_handles_empty_oracle_and_actual` passes with all four quadrants explicitly asserted on each of dims 2-5: (both empty → 1.0), (oracle empty / actual non-empty → 0.0), (oracle non-empty / actual empty → 0.0), (both non-empty partial → expected ratio).
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` passes (both existing `test_resolve_wiki_path.py` and the new `markdown_qa/` subdirectory).

### Deferred / conditional

- [ ] **(Policy decided in v5)** Two-provider review (Claude + Gemini) is sufficient for the revision-bound approval gate while codex-cli #2479 remains unresolved. r5 will proceed under this policy; Codex r5 review will be added retroactively if #2479 is fixed before merge. The decision is recorded here so subsequent reviewers do not re-block on the same question.

---

## Build Sequence (TDD order)

1. Add `pytest-socket`, `zss==1.2.0`, `scipy>=1.11` to `pyproject.toml` test/dev group; run `uv sync` and assert all three import. (Attested: scipy is introduced here for the first time.)
2. Create `scripts/data/llm-wiki/tests/markdown_qa/__init__.py` (empty) and the subdirectory scaffold.
3. Write `sample-manifest.schema.json` (with conditional `oracle_reviewed_at` requirement).
4. Write `markdown_qa/fixtures_sampling.py` (validator + `check_floor_occupancy()`) with unit tests (folded into structural tests 3, 4, and the session-hook injection test).
5. Write `markdown_qa/rubric_scorers.py`. Implement `empty_safe_ratio()` helper first; then implement dims 2-5 against `test_rubric_scorer_handles_empty_oracle_and_actual` (4-quadrant) — RED first, then GREEN with the helper. Implement heading scorer last, against `test_heading_preservation_detects_reordering` (tolerance band) — RED first, then GREEN with the rank-vector formula.
6. Write `markdown_qa/conftest.py` with the `pytest_sessionfinish` hook (including `MARKDOWN_QA_ARTIFACTS_DIR` env override read at the `ARTIFACTS_DIR` definition site) and the subdirectory-scoped session-autouse `_disable_network` fixture. Verify by running `uv run pytest scripts/data/llm-wiki/tests/test_resolve_wiki_path.py -v` and confirming it passes (sibling not affected by socket disable).
7. Write the 13 structural tests in `markdown_qa/test_conversion_quality.py`.
8. Author 20 blinded oracle fixtures following the protocol in `tests/fixtures/llm-wiki/conversion-oracle/README.md`. Solo contributors follow the 24-hour-delay path with HTML-only re-review (no converter output viewed at any point); multi-reviewer contributors follow the distinct-reviewer path.
9. Write the 120-case `test_per_topic_dimension` parametrized test; assert tolerant `--collect-only --quiet -p no:cacheprovider | grep -c '::'` count == 133 for the module and 134 for the subdirectory.
10. Write `markdown_qa/test_session_hook_regression.py` per the v5 filesystem-path-only rewrite (copy conftest into `tmp_path`, `subprocess.run` against `tmp_path`, no `-p` plugin reference to a hyphenated module). Run it and assert it passes (i.e., subprocess pytest returns 1 on the injected violation).
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
- **Not** renaming the `llm-wiki/` directory to `llm_wiki/` — that is a separate cross-repo migration (out of scope per memory `feedback_llm_wiki_hyphen_module_path_pattern`); this plan works around the hyphen via filesystem-only paths and `importlib.util.spec_from_file_location`.

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

## Adversarial Review Summary (r4 — complete)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | 1 P1 (regression-test subprocess used an invalid `-p` dotted-path argument referencing `scripts.data.<hyphenated-dir>...` — hyphen in the `llm-wiki` directory name is invalid as a Python module name; `-p` does not load conftest files anyway; per memory `feedback_llm_wiki_hyphen_module_path_pattern`); 2 P2 (`MARKDOWN_QA_ARTIFACTS_DIR` env-seam not in conftest pseudocode; solo-reviewer escape hatch permits converter-output reading at sign-off, weakening blinding); 3 P3 (git-log parse fails under shallow CI clones; collection-count grep brittle; test #12 only asserts 2 of 4 quadrants); plus suggestion to use tolerance band on test #11 |
| Codex | n/a | not produced — codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression` (#2479) |
| Gemini | **APPROVE** | clean; one optional suggestion (`**/.artifacts/` repo-wide ignore — already in v4 Files-to-Change) |

**Overall r4 result:** MAJOR (Claude) → this v5 revision. Gemini's APPROVE does not dominate because Claude's P1 is a concrete defect that would prevent the regression test from invoking the hook it claims to verify, reopening r3's "AC injection mechanism unspecified" concern.

## Adversarial Review Summary (r5)

*Pending. Will be populated once r5 reviews land against this v5's commit SHA. Reviews produced against v1, v2, v3, or v4 artifacts do not satisfy the revision-bound approval gate. Per the policy decision in §Acceptance Criteria → Deferred, two-provider coverage (Claude + Gemini) is sufficient while codex-cli #2479 remains open.*

---

## Risks and Open Questions

- **Risk (fixture drift):** Oracle markdown is authored manually against HTML + live rendering. Mitigation — two-reviewer sign-off required OR documented 24-hour-delay self-review path with HTML-only re-review (no converter output at any point), explicit blinding protocol, conflict-resolution procedure in fixture README, and a swap-and-replace path if disagreement survives.
- **Risk (residual single-author bias under sentinel path):** Even with the v5-tightened HTML-only re-review, a single author re-reading their own HTML interpretation may not catch systematic idiosyncrasies that a second human would. The 24-hour delay provides temporal detachment but not perspective diversity. Mitigation — sentinel path is documented as a fallback, not first choice; teams with a second reviewer should always use the distinct-handle path. Future refinement could require sentinel rows be capped at, e.g., 30% of the sample, but that constraint is out of scope here.
- **Risk (orcina.com content change):** HTML snapshots may diverge from live pages. Mitigation — `html_sha256` + `fetched_at` + `source_url` captured per entry. A refresh job is out of scope for this plan; #2125 (auto-refresh) is the natural home.
- **Risk (scorer coupling to parser quirks):** Rubric scorers parse markdown with regexes/custom logic. Two independent implementations could still disagree on malformed inputs. Mitigation — `test_rubric_scorer_determinism` asserts repeatability; the README documents that ill-formed corner cases score `0.0` by policy.
- **Risk (`zss` / `scipy` offline availability):** Both are external packages. Mitigation — pinned versions declared in `pyproject.toml`; `uv` prefers the wheel cache under offline execution. If offline CI turns out to lack them, the remediation is to pre-populate the wheel cache, NOT to vendor in-tree (explicitly out of scope here to keep surface area small).
- **Risk (`pytest-socket` + unix-socket subprocess IPC):** `allow_unix_socket=False` is the strict setting; some tooling (e.g., `uv` subprocess IPC in certain modes) may rely on unix sockets. Mitigation — fixture is now scoped to `markdown_qa/` subdirectory only, and an actual CI probe is listed in Build Sequence step 6.
- **Risk (session hook vs isolated invocation):** When the whole test module is NOT collected (e.g., `pytest -k missing_pattern`), no per-topic artifacts are written. The `pytest_sessionfinish` hook detects the empty-artifacts case and returns without altering `exitstatus`, so it never spuriously fails a narrow run. Documented in `conftest.py` docstring.
- **Risk (duplicate-heading question from Gemini r2 P3):** The heading-preservation Jaccard is over sets of `(level, normalized_text)` tuples. If two distinct headings have the same `(level, text)` (rare in Orcina webhelp, common in other corpora), they collapse into a single set element. Mitigation — documented in `rubric_scorers.py` docstring as a known, accepted corpus-specific quirk; does not affect the 20-topic Orcina sample.
- **Risk (scipy version float drift on test #11):** `scipy.stats.kendalltau` may produce slightly different floats across scipy versions. Mitigation (v5) — test #11 asserts a tolerance band `0.85 <= score <= 0.95 AND score < 1.0` rather than an exact value.
- **Risk (`MARKDOWN_QA_ARTIFACTS_DIR` env leak across test runs):** A stale env var from a CI runner could redirect artifacts unintentionally. Mitigation — the regression test sets the var only within the `subprocess.run` env mapping, never in the parent process; the parent test process does not inherit any modification. Default fallback path is the in-repo `.artifacts/` tree.
- **Risk (filesystem-path-only regression test brittleness):** Copying `conftest.py` and `fixtures_sampling.py` into `tmp_path` requires that conftest's relative imports work in the new location. Mitigation — `conftest.py` uses `from fixtures_sampling import ...` (sibling import, not dotted) which works in any directory both files share. Build Sequence step 10 verifies end-to-end.
- **Open:** None remaining. All Open items from v4 have been resolved.

---

## Complexity: T3

**T3** — 20 blinded hand-authored oracle files × 3 products + 6 rubric scorers (with shared `empty_safe_ratio` helper) + 3 new test deps (`pytest-socket`, `zss==1.2.0`, `scipy>=1.11` — scipy newly introduced) + 13 structural tests + session hook + filesystem-path-only session-hook regression test + JSON Schema (with conditional fields) + two-reviewer blinding protocol with documented HTML-only solo-contributor escape hatch. Bumped from T2 at v3 per r2 Claude P3 and r2 Gemini P3 consensus; v4/v5 do not re-adjust. Scope remains test/QA only (no production code modified); TDD required; deterministic and offline.
