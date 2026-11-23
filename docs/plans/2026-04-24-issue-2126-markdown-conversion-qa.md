# Plan for #2126: test(llm-wiki): validate markdown conversion quality across all 717 topics

> **Status:** draft (v6 — addresses r5 Claude MAJOR; folds r5 Gemini P3s)
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
> - r5 Claude (MAJOR): `scripts/review/results/20260425T032315Z-plan-2126-v5.md-plan-claude.md`
> - r5 Gemini (APPROVE w/ P3): `scripts/review/results/20260425T032713Z-plan-2126-v5.md-plan-gemini.md`
> - r1/r2/r3/r4/r5 Codex: not produced (codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression`; tracked in #2479)
> - r6 artifacts: pending; revision-bound to this v6 (paths and SHA to be recorded below once reviews land)

---

## Review History

### v1 → v2 → v3 → v4 → v5 (resolutions, for context)
Carried forward unchanged from v5. Summary:
- r1 → v2: parametrize arithmetic; per-topic floor-occupancy; marginal-only stratification; oracle blinding; formulas locked; `pytest-socket`; Attested Evidence.
- r2 → v3: `pytest_sessionfinish` replaces aggregate test; rank-vector Kendall-tau + `scipy>=1.11`; structural regression test; pyproject pins; collection-safe loader; AC grep unified; src-keyed image match; `_disable_network` cleaned; scorer-lib attestations.
- r3 → v4: shared `empty_safe_ratio` for dims 2-5; `_disable_network` scope narrowed by relocating to `markdown_qa/`; AC injection mechanism pinned; solo-contributor 24-hour-delay path; scipy attestation corrected.
- r4 → v5: regression test rewritten to filesystem-path-only (no hyphen-dotted-path); `MARKDOWN_QA_ARTIFACTS_DIR` env-seam in conftest pseudocode; HTML-only re-review on solo path; `oracle_reviewed_at` manifest field; tolerant grep; 4-quadrant empty-safe assertion; tolerance band on test #11; two-provider review policy.

### v5 → v6 deltas (this revision)

| Finding | Severity (r5) | Resolution in v6 |
|---|---|---|
| **Oracle YAML-comment header (`# oracle_authored_by: X`) in `.md` fixtures collides with the locked heading-preservation regex `^(#{1,6})\s+(.*)$`. The regex matches each ~6 header lines as H1 in `expected_md` but not in `actual_md` (converter never emits them), depressing dim-1 scores systematically across all 20 fixtures.** | **P1 (Claude r5)** | **Resolved (option (b): HTML comments).** Every oracle `.md` file will use HTML comment syntax `<!-- oracle_authored_by: X -->` for ALL provenance metadata instead of `# key: value`. Rationale for picking (b) over the alternatives: (a) YAML-frontmatter (`---\nkey: value\n---`) requires fence-parsing logic and adds a parsing dependency in any future tool that reads the fixtures; (c) a fixture preprocessor that strips oracle-meta headers before scoring adds runtime complexity that could itself mask real defects (a wrong strip pattern silently filters real H1s). HTML comments are markdown-legal, invisible when rendered, syntactically inert to the H1 regex (`<!--` does not match `^#{1,6}\s+`), and require ZERO scorer-side changes. The locked heading scorer regex stays exactly as written; the contamination cannot occur because no oracle line will start with `#`. New AC test #14 (`test_oracle_md_files_lack_heading_regex_metadata`) parses each oracle `.md`, runs the EXACT scorer regex `^(#{1,6})\s+(.*)$` over its raw lines, and asserts that none of the matched headings contain any of the metadata keys (`oracle_authored_by`, `oracle_review_method`, `oracle_authored_at`, `oracle_second_reviewer`, `oracle_reviewed_at`, `single_reviewer_timelag`). This proves the contamination cannot regress. |
| **`markdown_qa/__init__.py` + bare `from fixtures_sampling import check_floor_occupancy` in `conftest.py` will fail under pytest's default `importmode=prepend`. With `__init__.py` present pytest puts the package PARENT (`scripts/data/llm-wiki/tests/`) on sys.path, NOT `markdown_qa/` itself, so the bare import resolves to nothing and `pytest_sessionfinish` never registers — the floor-occupancy gate silently never fires.** | **P1 (Claude r5)** | **Resolved (option (a): drop `__init__.py`).** Files-to-Change row that creates `scripts/data/llm-wiki/tests/markdown_qa/__init__.py` will be **deleted**. Rationale for picking (a) over the alternatives: (b) relative imports (`from .fixtures_sampling import ...`) require the file to be loaded AS a package member, which pytest does only when the parent has `__init__.py`; that's exactly the broken path. (c) sys.path shim adds three extra lines per import-site and is not needed once `__init__.py` is gone. With `__init__.py` removed, pytest's rootdir-walk discovers `conftest.py` directly and pytest's `rootdir` plus `testpaths` mechanism puts `markdown_qa/` itself on sys.path during collection — the bare `from fixtures_sampling import check_floor_occupancy` then resolves correctly to its sibling. This is also the pattern the existing sibling test uses (`tests/test_resolve_wiki_path.py:21-26` inserts the script dir into sys.path manually for the SAME hyphen-path reason; pytest's rootdir-based discovery achieves the same effect for subdirectory tests when no `__init__.py` is present). New AC test #15 (`test_session_hook_actually_fires_sentinel`) writes a sentinel file from inside `pytest_sessionfinish` and asserts post-run that the file exists — proving the hook registered AND ran. The session-hook regression test (test R1, formerly v5) is also tightened to drop the `__init__.py` copy step (none exists) AND to add `--capture=no` to the subprocess pytest args so the stderr substring assertion is robust across pytest versions (Claude r5 P2 #5 suggestion). |
| **Drift between manifest `oracle_authored_at`/`oracle_reviewed_at` and the same fields embedded in `.md` HTML-comment header lines.** | **P2 (Claude r5)** | **Resolved.** New AC test #16 (`test_oracle_md_provenance_matches_manifest`) parses each oracle `.md` file's HTML-comment header block, extracts `oracle_authored_at`, `oracle_authored_by`, `oracle_reviewed_at`, `oracle_second_reviewer`, `oracle_review_method`, `single_reviewer_timelag`, and asserts each equals the corresponding field in the manifest entry for that slug. Drift in either direction fails the run. |
| **Honor-system gap on solo-contributor 24-hour delay (timestamps are author-supplied; no external clock anchor).** | **P2 (Claude r5)** | **Acknowledged as a known v1 limitation.** Risks section will document it explicitly and reference a follow-up for external-clock anchoring (signed commit timestamps, CI-recorded `fetched_at`). The HTML-only re-review tightening from v5 stands; full timestamp-fabrication mitigation is deferred and not scoped here, because anchoring requires either a CI lane (currently absent for fixture authoring) or signed commits (workflow change beyond this plan's scope). |
| **Subprocess regression-test stderr capture under pytest may swallow `print(..., file=sys.stderr)` from `pytest_sessionfinish` in some pytest configurations.** | **P2 (Claude r5)** | **Resolved.** The subprocess pytest invocation in `test_session_hook_fails_run_on_injected_violation` will pass `-s` (alias of `--capture=no`) to disable per-test capture; this also keeps the `pytest_sessionfinish` stderr text visible in `result.stderr`. Updated arg list shown in v6 pseudocode. |
| **Hard-tier `encoding_stress` feasibility unverified — manifest validator requires >=2 entries with `encoding_stress: true` but plan does not enumerate candidate Orcina pages.** | **P3 (Claude r5)** | **Resolved.** Added a one-off corpus pre-scan as Build-Sequence step 0 (`grep -lE '\xc2\xb0\|[\xce\xb1-\xcf\x89]\|[\xe2\x88]' data/llm-wiki/orca*/topics/*.html | head -8`), and committed candidate slugs in the manifest README so fixture authoring is unblocked at step 8. The 8-candidate pre-scan ensures the >=2 requirement is satisfiable and provides slack. |
| **`empty_safe_ratio` naming may invite a future contributor to retrofit dim 6 to use it and break the formula.** | **P3 (Claude r5)** | **Resolved.** Added a docstring note inside dim 6's scorer function explicitly explaining why it does NOT call `empty_safe_ratio` (because the formula is `1 - tree_edit_distance / max(size)`, an edit-distance ratio, not a match-count ratio), and re-stating the both-empty semantics inline. |
| **`pytest --collect-only` exit-code semantics not pinned: AC commands chain `... \| grep -c '::'` and rely on grep's exit code being 0 when matches are found; if pytest collection errors, grep silently reports a misleading count.** | **P3 (Claude r5)** | **Resolved.** Each affected AC will be split into a two-step assertion: (1) `pytest --collect-only --quiet -p no:cacheprovider <path>` exits 0 (collection succeeds); (2) the same command piped to `grep -c '::'` returns the expected count. ACs are reformulated as two checkboxes per command. |
| **`jsonschema` and `PyYAML` may not be present in `pyproject.toml` test/dev deps but are required by `test_sample_manifest_schema_valid` and `yaml.safe_load(MANIFEST_PATH.read_text())`.** | **P3 (Gemini r5)** | **Resolved.** `pyproject.toml` Files-to-Change row will declare BOTH `jsonschema>=4.0` and `PyYAML>=6.0` alongside the existing `pytest-socket`, `zss==1.2.0`, and `scipy>=1.11` adds. Verified at base SHA: `grep -nE 'jsonschema\|PyYAML' pyproject.toml` returns no match for `jsonschema`; `PyYAML` may already be present transitively but will be declared explicitly in the test/dev group. |
| **`write_report` (called in `conftest.py`) and `write_per_topic_artifact` (called in `test_conversion_quality.py`) are referenced but neither defined nor imported in v5 pseudocode.** | **P3 (Gemini r5)** | **Resolved.** Both helpers will be defined in `markdown_qa/fixtures_sampling.py` (so they share the module that already exports `check_floor_occupancy`); pseudocode now shows `from fixtures_sampling import check_floor_occupancy, write_report, write_per_topic_artifact` for `conftest.py` and `from fixtures_sampling import write_per_topic_artifact` for `test_conversion_quality.py`. Their signatures are pinned in the pseudocode below. |

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/data/llm-wiki/ingest-orcina.py` lines 98-259 — `html_to_markdown()` + `_convert_element()` + `_convert_table()` are the single canonical conversion surface under test. It emits a `<!-- source: URL -->` header, strips `script/style/nav/footer/header/link/meta/noscript` and MadCap `MCBreadcrumbs*`/`MCMiniTocBox_0`/`MCRelatedTopics` containers, and preserves heading levels, `<p>` inline mixing (`strong|b`, `em|i`, `code`, `a`, `br`, `img`), `ul/ol` (non-nested, non-recursive — see line 192 `recursive=False`), `table` via `_convert_table`, `pre` as fenced code, `dl`/`dt`/`dd` as definition terms, and a top-level `<hr>` → `---`.
- `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` (186 lines) — existing pytest harness pattern. It already solves the hyphenated-package import problem via `sys.path.insert(0, scripts/data/llm-wiki/)` at lines 22-26 and demonstrates fixture-driven isolation with `tmp_path`, `monkeypatch`, and `patch.object(mod, "REPO_ROOT", tmp_repo)`. The new conversion-QA module reuses this sys.path bootstrap to import `ingest-orcina` as `ingest_orcina` via `importlib.util.spec_from_file_location`.
- `scripts/data/llm-wiki/tests/__init__.py` (empty) — test package anchor already exists at the parent `tests/` level. NOTE: v6 does NOT create a sibling `markdown_qa/__init__.py` (P1 #2 resolution above) — pytest's rootdir-walk discovers `conftest.py` and the sibling-import works because no `__init__.py` exists in `markdown_qa/`.
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
- Memory file `feedback_llm_wiki_hyphen_module_path_pattern` — explicitly consulted for v5 AND v6 to prevent recurrence of the hyphen-dotted-path defect.

### Data-Pipeline retrieval contract (`cat:data-pipeline`)
| Required source | Consulted | Finding |
|---|---|---|
| `data/document-index/registry.yaml` | YES | No match for the hyphenated llm-wiki directory token / orcina / `html_to_markdown`. Ingestion pipeline unregistered. Gap flagged as follow-up; not scoped here. |
| `config/data/pipeline-manifest.yaml` | YES | File contains `pipelines: {}` only. Same gap. |
| `data/document-index/resource-intelligence-maturity.yaml` | YES | No llm-wiki row. Gap flagged; not extended. |

### Gaps identified
- No conversion-quality test module exists.
- No oracle markdown fixtures exist for any topic.
- No stratified sampler exists.
- llm-wiki ingestion is absent from registry / pipeline-manifest / maturity ledger — flagged as follow-up, not scoped here.

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
- Decision: v6 retains v5's **subdirectory option** (`scripts/data/llm-wiki/tests/markdown_qa/`) as a defense-in-depth choice — it prevents *future* sibling additions from silently inheriting the socket disable and keeps the fixture's blast radius equal to its intent. v6 changes ONLY the package-vs-non-package decision: `markdown_qa/` no longer carries `__init__.py` (P1 #2 resolution).

**Hyphen-path hazard probe** (verify via the shown command, run against this v6 plan file before submission):
- Command: `grep -c 'llm-wiki\.' /tmp/plan-drafts/plan-2126-v6.md`
- Expected result: `0` matches. Any non-zero result indicates a recurrence of the v4 P1 defect and the plan must be regrepped/repaired before submission.

**Gap proofs** (verify via the shown command):
- Run `git grep -n llm-wiki -- config/data/pipeline-manifest.yaml` (also try `orcina`) → expected empty
- Run `git grep -n llm-wiki -- data/document-index/registry.yaml` (also try `orcina`) → expected empty
- Run `git grep -n llm-wiki -- data/document-index/resource-intelligence-maturity.yaml` (also try `orcina`) → expected empty
- Run `git ls-files scripts/data/llm-wiki/tests/ | grep -c conversion` → expected 0
- Run `git ls-files .gitignore | xargs grep -n llm-wiki` → expected to show `data/llm-wiki` ignored

**Tooling / dep availability at HEAD = 07e73c2e** (verify via the shown command):
- `pytest-socket` — will be added in this plan. `grep -n pytest-socket pyproject.toml` at base SHA returns **no match**.
- `zss==1.2.0` — will be added in this plan. `grep -n 'zss' pyproject.toml` at base SHA returns **no match**.
- `scipy>=1.11` — will be added in this plan. `grep -n scipy pyproject.toml` at base SHA returns **no match** (scipy is NOT currently declared in `pyproject.toml` at any scope — this corrects v3's inaccurate claim that scipy was a declared general dep). The `pyproject.toml` Files-to-Change row therefore introduces scipy for the first time into the project.
- `jsonschema>=4.0` — will be added in this plan (v6, per Gemini r5 P3). `grep -n jsonschema pyproject.toml` at base SHA returns **no match**.
- `PyYAML>=6.0` — will be added in this plan (v6, per Gemini r5 P3) explicitly in test/dev group. May already be present transitively; explicit declaration ensures the plan is self-contained.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-2126-markdown-conversion-qa.md` |
| Test module | `scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py` |
| Session hook + scoped fixture | `scripts/data/llm-wiki/tests/markdown_qa/conftest.py` |
| Session-hook regression test | `scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` |
| Sampling helper + report writers | `scripts/data/llm-wiki/tests/markdown_qa/fixtures_sampling.py` |
| Rubric scorer helper | `scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py` |
| (NO `__init__.py` in `markdown_qa/` — v6 P1 #2 resolution; pytest rootdir-walk handles discovery without it) | n/a |
| Oracle fixtures | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` + `{slug}.md` |
| Stratification manifest | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` |
| Manifest JSON Schema | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` |
| Oracle authoring checklist | `tests/fixtures/llm-wiki/conversion-oracle/README.md` |
| Rubric report (generated, gitignored) | `scripts/data/llm-wiki/tests/markdown_qa/.artifacts/conversion-quality-report.json` |
| Plan review r6 — Claude | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-claude.md` |
| Plan review r6 — Codex | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-codex.md` (conditional on codex-cli fix #2479) |
| Plan review r6 — Gemini | `scripts/review/results/<stamp>-2026-04-24-issue-2126-markdown-conversion-qa.md-plan-gemini.md` |

---

## Deliverable

A self-contained pytest module `test_conversion_quality.py` under `scripts/data/llm-wiki/tests/markdown_qa/`, plus a subdirectory-scoped `conftest.py` (NO `__init__.py` — pytest discovers via rootdir-walk, so bare sibling imports resolve correctly) that enforces the aggregate floor-occupancy gate AFTER all parametrized runs complete, plus a `test_session_hook_regression.py` that copies the conftest into a `tmp_path` and runs `python -m pytest <tmp_path> -s` (filesystem-path-only with `--capture=no` so stderr survives subprocess capture) with a synthetic violation, asserting exit-code 1 and stderr substring. 20 oracle-backed HTML/markdown fixtures live under `tests/fixtures/llm-wiki/conversion-oracle/`. **Oracle `.md` files use HTML-comment provenance metadata (`<!-- key: value -->`) so the locked heading-preservation regex cannot match metadata lines as H1 headings (v6 P1 #1 resolution).** The module executes `html_to_markdown()` on stratified topics, scores each output against six rubric dimensions with locked formulas (dims 2-5 use shared `empty_safe_ratio`; dim 1 uses explicit Jaccard+Kendall-tau; dim 6 uses Zhang-Shasha tree-edit distance), and fails the run when the floor-occupancy rule is violated. Strict offline enforcement via `pytest-socket` is scoped to the `markdown_qa/` subdirectory so sibling tests are not affected (an active `SocketBlockedError` probe lives in a structural test). Oracle authorship is blinded from current converter output at both T0 and the T0+24h re-review (re-review is HTML-only, never converter output).

---

## Pseudocode

### Subdirectory-scoped conftest.py (v6 — no `__init__.py`, explicit imports, sentinel hook)

```python
# scripts/data/llm-wiki/tests/markdown_qa/conftest.py
# ---------------------------------------------------
# This conftest applies ONLY to tests under markdown_qa/.
# Sibling tests under scripts/data/llm-wiki/tests/ (e.g., test_resolve_wiki_path.py)
# are NOT affected by the socket disable or the session-finish hook.
#
# v6 NOTE: markdown_qa/ does NOT have __init__.py. pytest's rootdir-walk
# discovers this conftest and adds markdown_qa/ to sys.path during collection,
# so the bare sibling import below resolves to fixtures_sampling.py in this
# same directory. This is the same mechanism the existing
# tests/test_resolve_wiki_path.py uses (manual sys.path insert lines 22-26)
# to escape the hyphenated llm-wiki/ ancestor — pytest does the equivalent
# automatically when there is no __init__.py.

import os
import sys
import json
from pathlib import Path
import pytest

from fixtures_sampling import (
    check_floor_occupancy,
    write_report,
    write_per_topic_artifact,  # re-exported for the test module
)

# v5: env-seam spelled into source; v6: unchanged.
ARTIFACTS_DIR = Path(os.environ.get(
    "MARKDOWN_QA_ARTIFACTS_DIR",
    str(Path(__file__).parent / ".artifacts" / "per-topic"),
))

# v6: sentinel path proves pytest_sessionfinish actually fires (test #15).
# Default lives next to ARTIFACTS_DIR; can be redirected via env var for tests.
SENTINEL_PATH = Path(os.environ.get(
    "MARKDOWN_QA_SESSIONFINISH_SENTINEL",
    str(ARTIFACTS_DIR.parent / ".sessionfinish-fired"),
))


def pytest_sessionfinish(session, exitstatus):
    # v6: write sentinel UNCONDITIONALLY at hook entry so test #15 can prove
    # the hook actually registered and ran. The sentinel write happens BEFORE
    # the empty-artifacts early-return so that even narrow `-k` runs prove
    # the hook fired.
    SENTINEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SENTINEL_PATH.write_text("fired")

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

### fixtures_sampling.py — helpers (v6: pinned signatures for `write_report` / `write_per_topic_artifact`)

```python
# scripts/data/llm-wiki/tests/markdown_qa/fixtures_sampling.py

import json
from pathlib import Path
from typing import Iterable, Mapping

# Per-topic per-dim floors (kept aligned with plan §"Per-topic floor and hard-min")
PER_TOPIC_FLOOR = {
    "heading": 0.90, "link": 0.90, "table": 0.85,
    "code": 0.90, "image": 0.80, "list": 0.85,
}
HARD_MIN = 0.70  # zero-tolerance floor for ALL dims
MAX_BELOW_FLOOR = 2  # per-dim count of topics permitted to fall below per-topic floor


def check_floor_occupancy(per_topic: Iterable[Mapping]) -> list[dict]:
    """Returns list of violation records; empty list = pass."""
    by_dim: dict[str, list[float]] = {}
    for entry in per_topic:
        by_dim.setdefault(entry["dim"], []).append(entry["score"])
    violations = []
    for dim, scores in by_dim.items():
        below = [s for s in scores if s < PER_TOPIC_FLOOR[dim]]
        hard_breaches = [s for s in scores if s < HARD_MIN]
        if len(below) > MAX_BELOW_FLOOR:
            violations.append({"dim": dim, "rule": "below_floor",
                               "count": len(below), "max": MAX_BELOW_FLOOR})
        if hard_breaches:
            violations.append({"dim": dim, "rule": "hard_min",
                               "count": len(hard_breaches), "scores": hard_breaches})
    return violations


def write_per_topic_artifact(slug: str, dim: str, score: float,
                             artifacts_dir: Path | None = None) -> Path:
    """Atomically write {slug}-{dim}.json under ARTIFACTS_DIR. Returns the path."""
    import os
    base = artifacts_dir or Path(os.environ.get(
        "MARKDOWN_QA_ARTIFACTS_DIR",
        str(Path(__file__).parent / ".artifacts" / "per-topic"),
    ))
    base.mkdir(parents=True, exist_ok=True)
    out = base / f"{slug}-{dim}.json"
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps({"slug": slug, "dim": dim, "score": score}))
    tmp.replace(out)
    return out


def write_report(filename: str, per_topic: list[dict], violations: list[dict],
                 artifacts_dir: Path | None = None) -> Path:
    """Write the aggregate report next to per-topic artifacts."""
    import os
    base = artifacts_dir or Path(os.environ.get(
        "MARKDOWN_QA_ARTIFACTS_DIR",
        str(Path(__file__).parent / ".artifacts" / "per-topic"),
    ))
    out = base.parent / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "per_topic": per_topic,
        "violations": violations,
        "floor_occupancy_summary": {
            "total_dims": len(set(e["dim"] for e in per_topic)),
            "violation_count": len(violations),
            "passed": len(violations) == 0,
        },
    }
    out.write_text(json.dumps(payload, indent=2))
    return out
```

### Test module

```python
# scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py

import yaml
from pathlib import Path
import pytest

from fixtures_sampling import write_per_topic_artifact  # bare sibling import (no __init__.py)
from rubric_scorers import SCORERS, RUBRIC_DIMENSIONS
# ingest_orcina is loaded via importlib.util.spec_from_file_location (hyphen-path shim)

MANIFEST_PATH = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "llm-wiki" / "conversion-oracle" / "sample-manifest.yaml"


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
    # Per-topic floor is NOT asserted here; the session hook enforces
    # the floor-occupancy rule after ALL tests complete.
```

### Shared empty-safe helper (carried forward from v4, unchanged in v6)

```python
# scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py

def empty_safe_ratio(actual_tokens, oracle_tokens, match_count):
    """Shared denominator-safe ratio used by dims 2-5.

    Rule:
      - both empty       -> 1.0   (trivially well-matched; no regression vs oracle)
      - oracle empty,
        actual non-empty -> 0.0   (spurious content against empty oracle)
      - oracle non-empty,
        actual empty     -> 0.0   (missed all oracle tokens; falls through naturally)
      - otherwise        -> match_count / max(len(oracle_tokens), 1)

    NOTE (v6): dim 6 (list nesting) does NOT call this helper because its
    formula is `1 - tree_edit_distance / max(size)`, an edit-distance ratio
    rather than a match-count ratio. Its scorer applies the both-empty -> 1.0
    semantics inline. Do NOT retrofit dim 6 to use empty_safe_ratio — the
    output unit is incompatible.
    """
    a, o = len(actual_tokens), len(oracle_tokens)
    if a == 0 and o == 0:
        return 1.0
    if o == 0 and a > 0:
        return 0.0  # asymmetric: false-positive tokens on an empty oracle
    return match_count / max(o, 1)
```

### Session-hook regression test (v6: drops `__init__.py` copy; adds `-s` flag)

```python
# scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py
#
# v6: builds on v5 filesystem-path-only design. Two deltas:
#   1. NO __init__.py to copy (markdown_qa/ is no longer a package).
#   2. Subprocess pytest invocation passes -s (= --capture=no) so the
#      pytest_sessionfinish stderr substring is reliably visible in
#      result.stderr across pytest versions (Claude r5 P2 #5).
#
# Strategy: copy the markdown_qa/conftest.py and fixtures_sampling.py into
# tmp_path, then invoke `python -m pytest <tmp_path> -s` (filesystem path only).
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
    #    no Python dotted path is ever used. No __init__.py copy (none exists).
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
    #    to our synthetic tree. -s disables capture so the sessionfinish
    #    print-to-stderr survives subprocess capture across pytest versions.
    env = {
        **os.environ,
        "MARKDOWN_QA_ARTIFACTS_DIR": str(synthetic_artifacts),
    }
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-s",
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

(The `MARKDOWN_QA_ARTIFACTS_DIR` env override is implemented in `conftest.py` per the env-seam pseudocode above. The `-p no:cacheprovider` flag stabilizes pytest output; it disables the optional cache plugin, NOT a custom plugin reference. The `-s` flag disables per-test capture so the `pytest_sessionfinish` `print(..., file=sys.stderr)` survives subprocess capture.)

### Sentinel-firing proof test (NEW in v6 — proves `pytest_sessionfinish` actually registers and runs)

```python
# scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py (continued)

def test_session_hook_actually_fires_sentinel(tmp_path):
    """v6 P1 #2 proof: invoke pytest in a tmp_path that mirrors the
    package structure, point the sentinel env var at a tmp file, and after
    the subprocess exits assert the sentinel was written. This proves the
    hook actually registered (i.e., conftest.py loaded; sibling import did
    not raise) and ran (i.e., pytest_sessionfinish was actually called)."""
    shutil.copy(SOURCE_CONFTEST, tmp_path / "conftest.py")
    shutil.copy(SOURCE_FIXTURES_SAMPLING, tmp_path / "fixtures_sampling.py")
    (tmp_path / "test_trivial.py").write_text("def test_noop():\n    assert True\n")

    sentinel = tmp_path / ".sessionfinish-fired"
    env = {
        **os.environ,
        "MARKDOWN_QA_SESSIONFINISH_SENTINEL": str(sentinel),
        # Point ARTIFACTS_DIR at a non-existent path so the empty-artifacts
        # early-return triggers AFTER the sentinel write — confirming the
        # sentinel write happens unconditionally at hook entry.
        "MARKDOWN_QA_ARTIFACTS_DIR": str(tmp_path / "nonexistent"),
    }
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-q",
         "-p", "no:cacheprovider"],
        env=env,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Trivial test should pass; stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert sentinel.exists(), (
        "pytest_sessionfinish hook did not fire — conftest.py likely failed "
        "to load (sibling import resolution failed) OR pytest_sessionfinish "
        "was not registered. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert sentinel.read_text() == "fired"
```

Formula pseudocode for composite scorers is given in the "Rubric dimensions and formulas" section below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| **REMOVED in v6** | ~~`scripts/data/llm-wiki/tests/markdown_qa/__init__.py`~~ | **v6 P1 #2 resolution:** dropping `__init__.py` so pytest's rootdir-walk handles conftest discovery and bare sibling imports resolve correctly. Was present in v5 Files-to-Change; will NOT be created. |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py` | pytest module — per-topic scoring + 16 structural tests (was 13 in v5; +3 in v6: tests #14, #15, #16) |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/conftest.py` | Subdirectory-scoped `pytest_sessionfinish` hook with sentinel write + `_disable_network` session-autouse fixture + `MARKDOWN_QA_ARTIFACTS_DIR` env-seam + `MARKDOWN_QA_SESSIONFINISH_SENTINEL` env-seam (v6). Scope is `markdown_qa/` only; sibling `test_resolve_wiki_path.py` unaffected. Bare sibling import `from fixtures_sampling import ...` works because `markdown_qa/` has NO `__init__.py` (P1 #2). |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` | Filesystem-path-only subprocess regression test (v5 design) PLUS new `test_session_hook_actually_fires_sentinel` (v6 P1 #2 proof). |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/fixtures_sampling.py` | Marginal-quota validator + manifest schema loader + `check_floor_occupancy()` + `write_per_topic_artifact()` + `write_report()` (v6: helpers explicitly defined per Gemini r5 P3). |
| Create | `scripts/data/llm-wiki/tests/markdown_qa/rubric_scorers.py` | Six pure-function scorers implementing locked formulas (heading scorer uses `scipy.stats.kendalltau` on rank vectors) + shared `empty_safe_ratio()` helper used by dims 2-5; dim 6 carries an explicit docstring (v6) explaining why it does NOT call `empty_safe_ratio`. |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.yaml` | 20-entry manifest with full provenance fields including `oracle_reviewed_at` for sentinel rows. |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/sample-manifest.schema.json` | JSON Schema enforcing required fields including conditional `oracle_reviewed_at`. |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.html` × 20 | Frozen HTML snapshots. |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/{slug}.md` × 20 | **Oracle markdown — v6: provenance metadata in HTML comments (`<!-- key: value -->`), NOT YAML-comment headers (`# key: value`). The H1 regex `^(#{1,6})\s+(.*)$` cannot match `<!--`, so dim-1 contamination is structurally impossible.** From-source authorship only. |
| Create | `tests/fixtures/llm-wiki/conversion-oracle/README.md` | Blinding protocol + conflict-resolution + 24-hour-delay solo-reviewer escape hatch (HTML-only re-review per v5); v6 adds the HTML-comment metadata template and a one-off pre-scan candidate list for Hard-tier `encoding_stress` slugs. |
| Modify | `.gitignore` | Add `**/.artifacts/` repo-wide (per Gemini r1/r4 suggestion). |
| Modify | `pyproject.toml` (test/dev dependency group) | Add **five pinned deps**: `pytest-socket` (any recent version), `zss==1.2.0` (Zhang-Shasha tree-edit distance for list-nesting scorer), `scipy>=1.11` (Kendall-tau for heading-preservation scorer), `jsonschema>=4.0` (manifest schema validation — Gemini r5 P3), `PyYAML>=6.0` (manifest parsing — Gemini r5 P3, declared explicitly in test/dev group even if present transitively). scipy and jsonschema are introduced here for the first time. |
| Update | `docs/plans/README.md` | Index this plan. |

---

## Stratification strategy (marginal-only)

Sample 20 topics from the 717-topic corpus using three axes. **Each axis's marginal counts are validated independently; joint cells are not constrained.** A 3×5×3 = 45-cell joint cannot be honored by 20 samples, and the plan does not attempt to. Selection is deterministic via the pinned manifest.

**Axis 1 — Product marginal** (sums to 20):
- OrcaFlex: 12; OrcaWave: 5; OrcFxAPI: 3

**Axis 2 — Topic-category marginal** (sums to 20):
- introduction: 4; data: 5; theory: 4; results: 3; API: 4

**Axis 3 — Complexity-tier marginal** (sums to 20):
- Simple: 6; Medium: 8; Hard: 6

**Hard-tier reservation**: **at least 2 of the 6 Hard slots MUST be formula-heavy pages** (UTF-8 Greek letters, degree signs, math operators) so the encoding check #6 from the issue body is exercised. The manifest field `encoding_stress: bool` flags these and the validator asserts `sum(encoding_stress) >= 2 within complexity == "Hard"`.

**v6 Build-Sequence step 0 (NEW)** runs a one-off `grep` over the 717-topic corpus to identify >=8 candidate slugs containing `\xc2\xb0` (degree sign, UTF-8) and Greek-letter / math-operator code points; the candidates are committed to `tests/fixtures/llm-wiki/conversion-oracle/README.md` so fixture authoring at step 8 is unblocked.

**`fixtures_sampling.py` validates**:
1. total entries == 20
2. three axis marginals match the quotas above
3. Hard-tier encoding_stress count >= 2
4. all provenance fields populated
5. all `oracle_review_method == "from-source"`

The validator explicitly does **not** check joint-cell occupancy; the schema docstring documents this trade-off.

---

## Rubric dimensions and formulas

All scores in `[0.0, 1.0]`. Two implementers given the same `(actual_md, expected_md, html)` MUST produce bit-identical scores (modulo scipy version variance on dim 1, see test #11 tolerance band). Dimensions 2-5 all use the shared `empty_safe_ratio(actual_tokens, oracle_tokens, match_count)` helper defined in `rubric_scorers.py` (pseudocode in the Pseudocode section). The helper's contract — `both empty -> 1.0`, `oracle empty / actual non-empty -> 0.0`, `oracle non-empty / actual empty -> 0.0` (falls through to `0 / max(|oracle|, 1)`), `otherwise -> match_count / max(|oracle|, 1)` — is invoked explicitly in each dimension below.

| # | Dimension | Formula (exact) |
|---|---|---|
| 1 | **Heading preservation** | Let `A`, `O` = ordered lists of `(level, normalized_text)` tuples extracted via regex `^(#{1,6})\s+(.*)$`. **v6 NOTE: oracle `.md` files use HTML-comment provenance metadata (`<!-- key: value -->`), so this regex CANNOT match metadata lines. Test #14 enforces this contract.** **Set component (Jaccard)**: `J = |set(A) ∩ set(O)| / |set(A) ∪ set(O)|` (if both empty -> `J = 1.0`). **Order component (Kendall-tau on rank vectors of common elements)**: `I = set(A) ∩ set(O)`. If `|I| < 2`: `K = 1.0` (trivially well-ordered). Else: for each `h ∈ I` record `rank_A[h]` = index of `h` in `A` and `rank_O[h]` = index of `h` in `O`; compute `tau = scipy.stats.kendalltau(rank_A_vector, rank_O_vector).statistic` (returns τ in `[-1, 1]`); normalize to `[0, 1]` via `K = (tau + 1) / 2`. **Score = 0.7 * J + 0.3 * K**. |
| 2 | Link resolution | Parse `[text](href)` tokens from both. Let `H_a`, `H_o` = multisets of hrefs. `match_count = |H_a ∩ H_o|`. **Score = `empty_safe_ratio(H_a, H_o, match_count)`**. Explicitly: if `|H_a| == 0 and |H_o| == 0 -> 1.0`; if `|H_o| == 0 and |H_a| > 0 -> 0.0` (spurious links, token set written to per-topic JSON as `spurious_tokens`); otherwise `match_count / max(|H_o|, 1)`. Anchor (`#...`), `mailto:`, and `https://` links are counted in the same bucket; sub-score breakdown (internal / external / anchor) is recorded in the per-topic JSON for diagnostic purposes but does not factor into the gate score. |
| 3 | Table fidelity | Parse markdown tables via `\| ... \|` rows. Let `G_a`, `G_o` = row-major flattened cell strings (whitespace-normalized). `match_count = ` count of positions where `G_a[i] == G_o[i]` within the common prefix. **Score = `empty_safe_ratio(G_a, G_o, match_count)`**. Explicitly: if `|G_a| == 0 and |G_o| == 0 -> 1.0` (introduction pages with no tables score 1.0, not 0.0 — defect fixed in v4); if `|G_o| == 0 and |G_a| > 0 -> 0.0` (spurious tables); otherwise `match_count / max(|G_o|, 1)`. Missing or extra tables: absent cells count as non-matching against the oracle grid. |
| 4 | Code-block fidelity | Parse fenced ` ```...``` ` blocks. Let `B_a`, `B_o` = lists of `(lang_tag, body_normalized)`. `match_count = Σ match_i` where `match_i = 1` iff lang tag equals AND body equals after stripping trailing whitespace on each line. **Score = `empty_safe_ratio(B_a, B_o, match_count)`**. Explicitly: if `|B_a| == 0 and |B_o| == 0 -> 1.0` (no code blocks on either side — trivially well-matched); if `|B_o| == 0 and |B_a| > 0 -> 0.0` (spurious code blocks); otherwise `match_count / max(|B_o|, 1)`. |
| 5 | **Image alt-text** | Parse `![alt](src)` tokens. Let `M_a = {normalized_src(i) -> alt_a(i)}` and `M_o = {normalized_src(i) -> alt_o(i)}`. Match by `src` first: `common = set(M_a.keys()) ∩ set(M_o.keys())`. For each oracle image with `src ∈ common`, `match_i = 1` iff `M_a[src] == M_o[src]`. `match_count = Σ match_i`. **Score = `empty_safe_ratio(M_a.keys(), M_o.keys(), match_count)`**. Explicitly: if `|M_a| == 0 and |M_o| == 0 -> 1.0` (introduction pages with no images); if `|M_o| == 0 and |M_a| > 0 -> 0.0` (spurious images); otherwise `match_count / max(|M_o|, 1)`. Unmatched oracle `src`s (dropped/reordered) contribute `0` to the numerator but still count in the denominator, producing a localized penalty rather than a positional cascade. |
| 6 | List nesting | Extract depth-trees `T_a`, `T_o` from bullet/ordered-list lines (leading whitespace -> depth; `-`/`*`/`N.` markers). **Score**: if `size(T_a) == 0 and size(T_o) == 0 -> 1.0` (explicit both-empty clause; a page with no lists scores 1.0). Else: `1 - zhang_shasha_tree_edit_distance(T_a, T_o) / max(size(T_a), size(T_o), 1)`. Tree size = node count. Zhang-Shasha implementation via `zss` package (pinned `zss==1.2.0`). **v6 NOTE (in scorer docstring): does NOT call `empty_safe_ratio` because the formula is an edit-distance ratio, not a match-count ratio. Do NOT retrofit.** |

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

**Required method:** `from-source`. The oracle author opens the raw `.html` snapshot and the published MadCap Flare target-rendering guidance (Orcina webhelp's rendered output in a browser, which is the *specification* of what the HTML should render to), then hand-writes the `.md` file. The author MUST NOT view `html_to_markdown()` output during authorship.

**v6 metadata format change.** Each oracle `.md` file MUST carry provenance metadata as **HTML comments** at the top of the file. This is the v6 P1 #1 resolution: the locked H1 regex `^(#{1,6})\s+(.*)$` cannot match a line beginning with `<!--`, so metadata can NEVER contaminate dim-1 scoring.

```html
<!-- oracle_authored_by: <reviewer-github-handle> -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: <ISO-8601 UTC> -->
<!-- oracle_second_reviewer: <second-reviewer-github-handle | "self-reviewed-with-24h-delay"> -->
<!-- oracle_reviewed_at: <ISO-8601 UTC> -->
<!-- single_reviewer_timelag: false -->
```

(Each metadata field on its own HTML-comment line so test #16 can parse them with a simple line-prefix regex `^<!--\s+(\w+):\s+(.*)\s+-->$`.)

Matching fields are also required in `sample-manifest.yaml`. The validator test (`test_oracle_authorship_method_is_from_source`) fails the run on any `reviewed-from-output` row. New v6 test #16 (`test_oracle_md_provenance_matches_manifest`) cross-validates manifest fields against the HTML-comment metadata in each `.md` file.

### Solo-contributor escape hatch (v5 tightening retained)

If a second reviewer is unavailable, the author may satisfy the two-reviewer requirement by **self-review with 24-hour cooling-off delay**, under a strictly-blinded protocol:

1. At initial authorship time `T0`, the author writes the `.md` file against `.html` + live rendering only (no converter output viewed), commits the fixture with a `fixture(initial): <slug>` commit message, and records `oracle_authored_at: T0` in the manifest AND the HTML-comment header.
2. At `T0 + >=24h`, the author re-opens the fixture and re-reads **ONLY the rendered HTML page** (open `source_url` in a browser, OR open the saved `.html` snapshot in a browser to render it locally). The author **MUST NOT** view `html_to_markdown()` output during the re-review. Confirms the fixture unchanged or amends it in a second commit `fixture(second-review): <slug>`. The `oracle_reviewed_at` HTML-comment field AND manifest field is set to the re-review timestamp.
3. The manifest records `oracle_second_reviewer: self-reviewed-with-24h-delay`, `single_reviewer_timelag: true`, and `oracle_reviewed_at: <ISO-8601 UTC>`. The same fields appear in the HTML-comment header.
4. Structural test `test_oracle_has_second_reviewer` accepts either a distinct handle OR the exact sentinel string `self-reviewed-with-24h-delay`. For sentinel entries, it compares `oracle_reviewed_at - oracle_authored_at >= 24h` directly from manifest fields (no git-log parsing — robust under shallow CI clones).
5. The README protocol explicitly forbids opening `html_to_markdown()` output at any point during initial authorship OR re-review. Violating this is a fixture-level defect that voids the oracle.

The escape hatch is explicitly a fallback, not a first choice; fixtures with a distinct second reviewer are preferred whenever feasible. Even with the tightened HTML-only re-review, a residual single-author bias remains (one human's interpretation of HTML may be systematically idiosyncratic) — see Risks. The honor-system gap on author-supplied timestamps is acknowledged as a v1 limitation and tracked as a follow-up (Risks).

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

## TDD Test List (16 structural + 120 parametrized = 136 collected; aggregate floor-occupancy enforced by session hook; session-hook regression test lives in a separate test file)

### Structural (16)

| # | Test name | What it verifies |
|---|---|---|
| 1 | `test_sample_manifest_loads` | File parses; entry count == 20 (this test surfaces a collection-time loader failure, since the parametrize loader returns `[]` silently on error). |
| 2 | `test_sample_manifest_schema_valid` | Entries conform to `sample-manifest.schema.json`; all required fields present; conditional `oracle_reviewed_at` present when `single_reviewer_timelag: true`. |
| 3 | `test_sample_manifest_marginal_axes` | Product/category/complexity marginals match declared quotas. |
| 4 | `test_sample_manifest_hard_tier_encoding_stress` | `>=2` Hard-tier entries have `encoding_stress: true`. |
| 5 | `test_sample_manifest_fixture_files_exist` | Every entry's `html_path` and `oracle_md_path` resolve to non-empty tracked files. |
| 6 | `test_sample_manifest_html_sha256_matches` | Recomputed SHA-256 of each `.html` equals the manifest value. |
| 7 | `test_oracle_authorship_method_is_from_source` | Every entry has `oracle_review_method == "from-source"`. |
| 8 | `test_oracle_has_second_reviewer` | Every entry declares a non-empty `oracle_second_reviewer`; value is either distinct from `oracle_authored_by` OR the literal sentinel `self-reviewed-with-24h-delay`. **For sentinel entries:** asserts `oracle_reviewed_at - oracle_authored_at >= 24h` by parsing the two manifest ISO-8601 timestamps directly (NO git log read; robust under shallow CI clones). |
| 9 | `test_html_to_markdown_import` | `ingest_orcina.html_to_markdown` is importable via the hyphenated-path shim (`importlib.util.spec_from_file_location`). |
| 10 | `test_rubric_scorer_determinism` | Running each scorer twice on the same inputs returns identical floats. |
| 11 | `test_heading_preservation_detects_reordering` | (Carried from v3, v5 tolerance.) Constructs `A = "# H1\n# H2\n# H3"` and `O = "# H1\n# H3\n# H2"`. Asserts `0.85 <= heading_scorer(A, O, "") <= 0.95` AND `score < 1.0` (i.e., the reordering penalty fires within a tolerance band that absorbs scipy version differences). Approximate values: `tau ≈ 0.333`, `K ≈ 0.667`, `J = 1.0`, Score ≈ 0.9. |
| 12 | **`test_rubric_scorer_handles_empty_oracle_and_actual` (4-quadrant)** | Asserts all four quadrants explicitly for each of `link_scorer`, `table_scorer`, `code_scorer`, `image_scorer`: (a) both empty -> 1.0; (b) oracle empty, actual non-empty -> 0.0 (spurious-content path); (c) oracle non-empty, actual empty -> 0.0 (missed-all-tokens path; falls through to `0/max(|o|,1)`); (d) both non-empty with partial match (e.g., 1 of 2 oracle tokens matched) -> 0.5 (the expected ratio). |
| 13 | `test_no_network_access` | `pytest-socket` is active within the `markdown_qa/` subdirectory; a live `socket.socket(AF_INET, SOCK_STREAM)` call raises `SocketBlockedError`. (Active probe lives here, not in the `_disable_network` fixture.) |
| **14 (NEW v6)** | **`test_oracle_md_files_lack_heading_regex_metadata`** | **v6 P1 #1 proof.** For each oracle `.md` file in the manifest, runs the EXACT scorer regex `^(#{1,6})\s+(.*)$` over its raw lines. For every match, asserts the captured heading text does NOT contain any of the metadata keys: `oracle_authored_by`, `oracle_review_method`, `oracle_authored_at`, `oracle_second_reviewer`, `oracle_reviewed_at`, `single_reviewer_timelag`. This proves no oracle `.md` accidentally uses YAML-comment headers (`# key: value`) instead of HTML comments (`<!-- key: value -->`); reverting to the v5 metadata format would FAIL this test loudly. |
| **15 (NEW v6)** | **`test_session_hook_actually_fires_sentinel`** | **v6 P1 #2 proof.** Lives in `test_session_hook_regression.py` (alongside R1) but counted here as a structural assertion of the conftest contract. Spawns `python -m pytest` in `tmp_path` with `MARKDOWN_QA_SESSIONFINISH_SENTINEL` pointing at a tmp file and `MARKDOWN_QA_ARTIFACTS_DIR` pointing at a non-existent path so the hook's empty-artifacts early-return triggers AFTER the sentinel write. Asserts the sentinel exists post-run, proving `pytest_sessionfinish` was actually registered AND ran. If `__init__.py` accidentally returns OR a bare sibling import accidentally regresses, this test FAILS — exactly the silent-no-op failure mode r5 P1 #2 surfaced. |
| **16 (NEW v6)** | **`test_oracle_md_provenance_matches_manifest`** | **v6 Claude r5 P2 resolution.** For each oracle `.md`, parses the HTML-comment header block via regex `^<!--\s+(\w+):\s+(.*)\s+-->$`, builds a dict of metadata, and asserts equality with the corresponding fields in `sample-manifest.yaml`: `oracle_authored_by`, `oracle_authored_at`, `oracle_second_reviewer`, `oracle_reviewed_at`, `oracle_review_method`, `single_reviewer_timelag`. Catches drift in either direction. |

**Note:** v2's `test_aggregate_floor_occupancy` and `test_report_artifact_written` remain retired. Both concerns are handled by the `pytest_sessionfinish` hook in `markdown_qa/conftest.py`. The session-hook regression test lives in `test_session_hook_regression.py` as a separate file (see below); test #15 (sentinel-firing) ALSO lives there but is enumerated here as a structural assertion.

### Session-hook regression (separate test file, 2 cases — v6: original R1 + new sentinel test #15)

| # | Test name | What it verifies |
|---|---|---|
| R1 | `test_session_hook_fails_run_on_injected_violation` | (v6 update.) Copies `markdown_qa/conftest.py` and `markdown_qa/fixtures_sampling.py` into `tmp_path` via `shutil.copy()`, writes 3 known-bad per-topic JSONs (score = 0.50 on heading dim, count > MAX_BELOW_FLOOR) into a `tmp_path / .artifacts / per-topic` dir, sets `MARKDOWN_QA_ARTIFACTS_DIR` in subprocess env, then invokes `subprocess.run([sys.executable, "-m", "pytest", str(tmp_path), "-s", "-p", "no:cacheprovider"], check=False)`. Asserts `returncode == 1` AND `b"FLOOR-OCCUPANCY VIOLATIONS" in result.stderr`. **v6 deltas:** (1) NO `__init__.py` to copy (none exists); (2) `-s` flag added to disable per-test capture so the `pytest_sessionfinish` stderr text survives subprocess capture across pytest versions. |
| R2 (= test #15) | `test_session_hook_actually_fires_sentinel` | (v6 NEW.) See structural test #15 above. |

### Parametrized (120 = 6 dims × 20 topics)

| Test | Count | Notes |
|---|---|---|
| `test_per_topic_dimension[<slug>-<dim>]` | 120 | Double-parametrized on `entry` × `dim`. Each case computes a single score and writes `<slug>-<dim>.json`. Per-topic assertion is informational (logged); the gate is enforced by the session hook. |

**Collection assertion (v6: split into two checks per Claude r5 P3 #8)**:
1. Run `uv run pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py` → exit 0.
2. Pipe the same command's output to `grep -c '::'` → returns `136` (16 structural + 120 parametrized).
3. Run `uv run pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/markdown_qa/` → exit 0.
4. Pipe to `grep -c '::'` → returns `138` (136 from `test_conversion_quality.py` + 2 from `test_session_hook_regression.py`).

---

## Acceptance Criteria

- [ ] **(v6 P3 split)** `uv run pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py` exits 0.
- [ ] **(v6 P3 split)** Piping the same command to `grep -c '::'` returns exactly **136** (16 structural + 120 parametrized).
- [ ] **(v6 P3 split)** `uv run pytest --collect-only --quiet -p no:cacheprovider scripts/data/llm-wiki/tests/markdown_qa/` exits 0.
- [ ] **(v6 P3 split)** Piping the same command to `grep -c '::'` returns exactly **138** (136 + 2 regression-file cases R1 and R2).
- [ ] `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/test_conversion_quality.py -v` exits 0 on a clean corpus.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py -v` exits 0 (BOTH R1 and R2 pass: R1 by subprocess-asserting that pytest on a synthetic violation returns exit code 1; R2 by asserting the sentinel file exists post-subprocess-run, proving `pytest_sessionfinish` actually fired).
- [ ] 20 `.html` + 20 `.md` oracle pairs exist under `tests/fixtures/llm-wiki/conversion-oracle/` and are tracked by `git ls-files`.
- [ ] **(v6 P1 #1)** Every oracle `.md` file uses HTML-comment provenance metadata (`<!-- key: value -->`), NOT YAML-comment headers (`# key: value`). Verified by `test_oracle_md_files_lack_heading_regex_metadata` (#14).
- [ ] **(v6 Claude r5 P2)** For each oracle `.md`, the parsed HTML-comment metadata equals the corresponding fields in `sample-manifest.yaml`. Verified by `test_oracle_md_provenance_matches_manifest` (#16).
- [ ] **(v6 P1 #2)** `markdown_qa/` has NO `__init__.py`. Verified by `[ ! -f scripts/data/llm-wiki/tests/markdown_qa/__init__.py ]` returning exit 0.
- [ ] **(v6 P1 #2)** `pytest_sessionfinish` actually fires when `markdown_qa/` tests run. Verified by `test_session_hook_actually_fires_sentinel` (#15) which writes a sentinel file from inside the hook and asserts it exists post-subprocess-run.
- [ ] `sample-manifest.yaml` declares, for each of the 20 entries, all required provenance fields (including `single_reviewer_timelag` and conditional `oracle_reviewed_at`); `sample-manifest.schema.json` is the authoritative schema.
- [ ] All 20 entries have `oracle_review_method: from-source`.
- [ ] Every `oracle_second_reviewer` is either a distinct handle OR the exact sentinel `self-reviewed-with-24h-delay`; sentinel entries have `single_reviewer_timelag: true` AND `oracle_reviewed_at - oracle_authored_at >= 24h` (compared from manifest fields, NOT git log).
- [ ] `fixtures_sampling.py` validates marginal-only stratification and the Hard-tier encoding-stress floor, and fails on drift; also exports `check_floor_occupancy()`, `write_per_topic_artifact()`, and `write_report()` consumed by `conftest.py` and `test_conversion_quality.py`.
- [ ] `scripts/data/llm-wiki/tests/markdown_qa/.artifacts/conversion-quality-report.json` is produced on every run by the `pytest_sessionfinish` hook; contains per-topic per-dimension scores and a `floor_occupancy_summary` block.
- [ ] All six rubric dimensions have their formulas documented in `rubric_scorers.py` module docstring and in this plan's Rubric section; the two MUST match. Dimensions 2-5 invoke `empty_safe_ratio()`; dimension 1 uses the explicit `J = 1.0` both-empty clause; dimension 6 uses an explicit both-empty `-> 1.0` clause before its edit-distance ratio AND carries an in-source docstring explaining why it does NOT use `empty_safe_ratio` (v6 Claude r5 P3 #7).
- [ ] **(v6 Gemini r5 P3)** `pyproject.toml` test/dev dep group pins **`pytest-socket`**, **`zss==1.2.0`**, **`scipy>=1.11`**, **`jsonschema>=4.0`**, AND **`PyYAML>=6.0`**; verified by `grep -E '(pytest-socket|zss==1\.2\.0|scipy>=1\.11|jsonschema>=4\.0|PyYAML>=6\.0)' pyproject.toml | wc -l` == 5.
- [ ] **(v6 Gemini r5 P3)** `write_report` and `write_per_topic_artifact` are explicitly defined in `fixtures_sampling.py` and explicitly imported in their respective callers (`conftest.py` imports both via `from fixtures_sampling import check_floor_occupancy, write_report, write_per_topic_artifact`; `test_conversion_quality.py` imports `write_per_topic_artifact`).
- [ ] `test_no_network_access` actively verifies the socket block; the `_disable_network` fixture contains activation only, no probe.
- [ ] `_disable_network` fixture lives in `scripts/data/llm-wiki/tests/markdown_qa/conftest.py`, NOT in `scripts/data/llm-wiki/tests/conftest.py`; sibling `test_resolve_wiki_path.py` runs with normal socket access. Verify by `uv run pytest scripts/data/llm-wiki/tests/test_resolve_wiki_path.py -v` passing without socket activation.
- [ ] `conftest.py` reads `ARTIFACTS_DIR` from the `MARKDOWN_QA_ARTIFACTS_DIR` env var with a fallback to the in-repo path; verified by source inspection AND by the session-hook regression test exercising the env override. Same for `MARKDOWN_QA_SESSIONFINISH_SENTINEL` (v6 new).
- [ ] **(v6)** `test_session_hook_regression.py` uses ONLY filesystem paths and never references any Python dotted name below the hyphenated llm-wiki directory; verified by `grep -c 'llm-wiki\.' scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py` returning 0. Subprocess pytest invocation passes `-s` for stderr-capture robustness.
- [ ] `test_heading_preservation_detects_reordering` asserts a tolerance band `0.85 <= score <= 0.95 AND score < 1.0` (not an exact float).
- [ ] `test_rubric_scorer_handles_empty_oracle_and_actual` passes with all four quadrants explicitly asserted on each of dims 2-5: (both empty -> 1.0), (oracle empty / actual non-empty -> 0.0), (oracle non-empty / actual empty -> 0.0), (both non-empty partial -> expected ratio).
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` passes (both existing `test_resolve_wiki_path.py` and the new `markdown_qa/` subdirectory).

### Deferred / conditional

- [ ] **(Policy decided in v5, retained in v6)** Two-provider review (Claude + Gemini) is sufficient for the revision-bound approval gate while codex-cli #2479 remains unresolved. r6 will proceed under this policy; Codex r6 review will be added retroactively if #2479 is fixed before merge. The decision is recorded here so subsequent reviewers do not re-block on the same question.

---

## Build Sequence (TDD order)

0. **(NEW v6)** One-off corpus pre-scan for Hard-tier `encoding_stress` candidates. Run `grep -lE '\xc2\xb0\|[\xce\xb1-\xcf\x89]\|[\xe2\x88]' data/llm-wiki/orca*/topics/*.html | head -8` and commit the resulting candidate slugs to `tests/fixtures/llm-wiki/conversion-oracle/README.md`. Ensures step 8 (fixture authoring) is unblocked.
1. Add `pytest-socket`, `zss==1.2.0`, `scipy>=1.11`, `jsonschema>=4.0`, `PyYAML>=6.0` to `pyproject.toml` test/dev group; run `uv sync` and assert all five import. (Attested: scipy and jsonschema are introduced here for the first time.)
2. Create the subdirectory scaffold at `scripts/data/llm-wiki/tests/markdown_qa/`. **Do NOT create `__init__.py`** (v6 P1 #2 resolution).
3. Write `sample-manifest.schema.json` (with conditional `oracle_reviewed_at` requirement).
4. Write `markdown_qa/fixtures_sampling.py` (validator + `check_floor_occupancy()` + `write_per_topic_artifact()` + `write_report()`) with unit tests (folded into structural tests 3, 4, and the session-hook injection test).
5. Write `markdown_qa/rubric_scorers.py`. Implement `empty_safe_ratio()` helper first; then implement dims 2-5 against `test_rubric_scorer_handles_empty_oracle_and_actual` (4-quadrant) — RED first, then GREEN with the helper. Implement heading scorer last, against `test_heading_preservation_detects_reordering` (tolerance band) — RED first, then GREEN with the rank-vector formula. Implement dim 6 with explicit both-empty clause AND in-source docstring explaining non-use of `empty_safe_ratio`.
6. Write `markdown_qa/conftest.py` with the `pytest_sessionfinish` hook (including unconditional sentinel write at hook entry, `MARKDOWN_QA_ARTIFACTS_DIR` env override read at the `ARTIFACTS_DIR` definition site, and `MARKDOWN_QA_SESSIONFINISH_SENTINEL` env override) and the subdirectory-scoped session-autouse `_disable_network` fixture. Verify by running `uv run pytest scripts/data/llm-wiki/tests/test_resolve_wiki_path.py -v` and confirming it passes (sibling not affected by socket disable). ALSO verify the bare sibling import works by running `uv run pytest scripts/data/llm-wiki/tests/markdown_qa/ -k "noop_collection" --collect-only` and confirming exit 0 (proves conftest loaded without ImportError).
7. Write the 16 structural tests in `markdown_qa/test_conversion_quality.py`, including v6 NEW tests #14, #15, #16. Tests #14 and #16 cover oracle metadata; test #15 lives physically in `test_session_hook_regression.py` for proximity to its subprocess machinery.
8. Author 20 blinded oracle fixtures following the protocol in `tests/fixtures/llm-wiki/conversion-oracle/README.md`. **Use HTML-comment provenance metadata format (`<!-- key: value -->`)**, never YAML-comment headers. Solo contributors follow the 24-hour-delay path with HTML-only re-review (no converter output viewed at any point); multi-reviewer contributors follow the distinct-reviewer path. Hard-tier `encoding_stress: true` slugs are drawn from the step-0 candidate list.
9. Write the 120-case `test_per_topic_dimension` parametrized test; assert split-collection: `--collect-only --quiet -p no:cacheprovider` exits 0 AND piped to `grep -c '::'` returns `136` for the module / `138` for the subdirectory.
10. Write `markdown_qa/test_session_hook_regression.py` with R1 (v6 update: `-s` flag, no `__init__.py` copy) and R2 (= test #15, sentinel-firing proof). Run both and assert they pass.
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
- **Not** renaming the hyphenated llm-wiki directory to an underscore form — that is a separate cross-repo migration (out of scope per memory `feedback_llm_wiki_hyphen_module_path_pattern`); this plan works around the hyphen via filesystem-only paths and `importlib.util.spec_from_file_location`.
- **Not** anchoring `oracle_authored_at`/`oracle_reviewed_at` to an external clock (signed commit timestamps, CI-recorded `fetched_at`) — acknowledged honor-system gap on the solo-contributor path; deferred to a follow-up.

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
| Claude | **MAJOR** | 1 P1 (regression-test subprocess used invalid `-p` dotted-path argument referencing scripts.data.<hyphenated-dir>... — hyphen invalid as Python module name; `-p` does not load conftest files anyway); 2 P2 (env-seam not in conftest pseudocode; solo-reviewer escape hatch permits converter-output reading); 3 P3 (git-log parse fails under shallow CI clones; collection-count grep brittle; test #12 only asserts 2 of 4 quadrants); plus suggestion to use tolerance band on test #11 |
| Codex | n/a | not produced — codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression` (#2479) |
| Gemini | **APPROVE** | clean; one optional suggestion (`**/.artifacts/` repo-wide ignore — already in v4 Files-to-Change) |

## Adversarial Review Summary (r5 — complete)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | 2 P1 (oracle YAML-comment header collides with H1 regex on every fixture; `__init__.py` + bare sibling import in conftest will fail under default pytest importmode → `pytest_sessionfinish` never registers → floor-occupancy gate silently never fires); 3 P2 (manifest/`.md` provenance drift; honor-system 24h timestamps; subprocess stderr capture not pinned with `-s`); 3 P3 (encoding_stress feasibility unverified; `empty_safe_ratio` naming hazard for dim 6; `--collect-only` + `grep -c` brittle without pipefail) |
| Codex | n/a | not produced — codex-cli 0.124.0 upstream stdin-hang per memory `feedback_codex_cli_0_124_upstream_regression` (#2479) |
| Gemini | **APPROVE** w/ P3 | 2 P3 (`jsonschema`/`PyYAML` may be missing from `pyproject.toml`; `write_report`/`write_per_topic_artifact` undefined in pseudocode) |

**Overall r5 result:** MAJOR (Claude) → this v6 revision. Both Claude P1s are concrete runtime defects: the H1-regex contamination would systematically depress dim-1 scores on every fixture, and the import failure would make the floor-occupancy gate a silent no-op. v6 fixes both with structural changes (HTML-comment metadata; drop `__init__.py`) and adds three new ACs (#14, #15, #16) that prove the fixes hold and would FAIL loudly on regression. Gemini P3s are folded inline.

## Adversarial Review Summary (r6)

*Pending. Will be populated once r6 reviews land against this v6's commit SHA. Reviews produced against v1-v5 artifacts do not satisfy the revision-bound approval gate. Per the policy decision in §Acceptance Criteria → Deferred, two-provider coverage (Claude + Gemini) is sufficient while codex-cli #2479 remains open.*

---

## Risks and Open Questions

- **Risk (fixture drift):** Oracle markdown is authored manually against HTML + live rendering. Mitigation — two-reviewer sign-off required OR documented 24-hour-delay self-review path with HTML-only re-review (no converter output at any point), explicit blinding protocol, conflict-resolution procedure in fixture README, and a swap-and-replace path if disagreement survives.
- **Risk (residual single-author bias under sentinel path):** Even with the v5-tightened HTML-only re-review, a single author re-reading their own HTML interpretation may not catch systematic idiosyncrasies that a second human would. The 24-hour delay provides temporal detachment but not perspective diversity. Mitigation — sentinel path is documented as a fallback, not first choice; teams with a second reviewer should always use the distinct-handle path.
- **Risk (honor-system on solo-contributor timestamps):** `oracle_authored_at`/`oracle_reviewed_at` are author-supplied manifest fields. An author can satisfy the gate by setting both fields ≥24h apart while authoring the fixture in one sitting. **v6 acknowledges this as a v1 limitation;** mitigation requires an external clock anchor (signed commit timestamp via GPG, or CI-recorded `fetched_at` from a server-side runner). Both options require workflow changes beyond this plan's scope. Tracked as a follow-up — **NEW issue to be filed for "external-clock anchor on oracle authorship timestamps"** if a fabrication risk surfaces in practice.
- **Risk (orcina.com content change):** HTML snapshots may diverge from live pages. Mitigation — `html_sha256` + `fetched_at` + `source_url` captured per entry. A refresh job is out of scope for this plan; #2125 (auto-refresh) is the natural home.
- **Risk (scorer coupling to parser quirks):** Rubric scorers parse markdown with regexes/custom logic. Two independent implementations could still disagree on malformed inputs. Mitigation — `test_rubric_scorer_determinism` asserts repeatability; the README documents that ill-formed corner cases score `0.0` by policy.
- **Risk (`zss`/`scipy`/`jsonschema` offline availability):** All three are external packages. Mitigation — pinned versions declared in `pyproject.toml`; `uv` prefers the wheel cache under offline execution. If offline CI lacks them, the remediation is to pre-populate the wheel cache, NOT to vendor in-tree (explicitly out of scope here to keep surface area small).
- **Risk (`pytest-socket` + unix-socket subprocess IPC):** `allow_unix_socket=False` is the strict setting; some tooling (e.g., `uv` subprocess IPC in certain modes) may rely on unix sockets. Mitigation — fixture is now scoped to `markdown_qa/` subdirectory only, and an actual CI probe is listed in Build Sequence step 6.
- **Risk (session hook vs isolated invocation):** When the whole test module is NOT collected (e.g., `pytest -k missing_pattern`), no per-topic artifacts are written. The `pytest_sessionfinish` hook detects the empty-artifacts case and returns without altering `exitstatus` AFTER writing the sentinel — so it never spuriously fails a narrow run AND test #15 can still prove the hook fired. Documented in `conftest.py` docstring.
- **Risk (duplicate-heading question from Gemini r2 P3):** The heading-preservation Jaccard is over sets of `(level, normalized_text)` tuples. If two distinct headings have the same `(level, text)` (rare in Orcina webhelp, common in other corpora), they collapse into a single set element. Mitigation — documented in `rubric_scorers.py` docstring as a known, accepted corpus-specific quirk; does not affect the 20-topic Orcina sample.
- **Risk (scipy version float drift on test #11):** `scipy.stats.kendalltau` may produce slightly different floats across scipy versions. Mitigation (v5) — test #11 asserts a tolerance band `0.85 <= score <= 0.95 AND score < 1.0` rather than an exact value.
- **Risk (`MARKDOWN_QA_ARTIFACTS_DIR` env leak across test runs):** A stale env var from a CI runner could redirect artifacts unintentionally. Mitigation — the regression test sets the var only within the `subprocess.run` env mapping, never in the parent process; the parent test process does not inherit any modification. Default fallback path is the in-repo `.artifacts/` tree. Same for `MARKDOWN_QA_SESSIONFINISH_SENTINEL` (v6 new env-seam).
- **Risk (`MARKDOWN_QA_SESSIONFINISH_SENTINEL` accidentally overwritten on real runs):** The sentinel write is unconditional in the hook, so repeated runs against the same sentinel path produce a stale "fired" marker. Mitigation — default sentinel path is under `.artifacts/` (gitignored); env override is intended ONLY for the regression test. Documented in `conftest.py` docstring.
- **Risk (filesystem-path-only regression test brittleness):** Copying `conftest.py` and `fixtures_sampling.py` into `tmp_path` requires that conftest's bare sibling import works in the new location. Mitigation — `conftest.py` uses `from fixtures_sampling import ...` (sibling import, not dotted) which works in any directory both files share when no `__init__.py` is present (v6 P1 #2). Build Sequence step 10 verifies end-to-end.
- **Risk (HTML-comment metadata collision with markdown body):** A future oracle author might write an HTML comment in the markdown body that happens to match the metadata regex. Mitigation — test #16 asserts equality between parsed HTML-comment metadata and manifest fields; an extraneous comment matching the regex but not appearing in the manifest would fail equality OR (if it shadowed a real field) would diverge from the manifest value, both failing test #16. The metadata block is conventionally placed at the TOP of the file before any heading.
- **Open:** None remaining. All Open items from v5 have been resolved.

---

## Complexity: T3
