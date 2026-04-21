# Plan for #2444: aceengineer-admin — add minimal viable CI (uv + ruff + black + pytest) scoped to src/ + tests/

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2444
> **Parent meta-issue:** #2424 (ecosystem CI health — 6-of-7 repos red)
> **Review artifacts (pending):** scripts/review/results/2026-04-21-plan-2444-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code (aceengineer-admin)

- Confirmed: `aceengineer-admin/pyproject.toml` exists and already declares a full modern test/lint stack. Relevant blocks:
  - `requires-python = ">=3.11"` (line 10)
  - classifiers include Python 3.11 and 3.12 only (lines 20-21) — no 3.13 intent
  - `[project.optional-dependencies].test` → `pytest>=8.0`, `pytest-cov>=5.0`, `pytest-mock>=3.14`, `pytest-asyncio>=0.23` (lines 51-56)
  - `[project.optional-dependencies].dev` → `black>=24.0`, `ruff>=0.5.0`, `mypy>=1.10`, `pre-commit>=3.7` (lines 43-50)
  - `[tool.pytest.ini_options]` → `addopts = "-ra -q --strict-markers --cov=src --cov-report=term-missing"`, `testpaths = ["tests", "src/aceengineer_admin/tests"]` (lines 67-73)
  - `[tool.coverage.report] fail_under = 0` (line 89) — no coverage gate to break
  - `[tool.ruff] select = ["E","F","W","I","N","UP","B","C4","SIM"]`, `ignore = ["E501"]`, `target-version = "py311"` (lines 108-111)
  - `[tool.black] target-version = ["py311","py312"]`, `line-length = 88` (lines 91-93)
- Confirmed: `aceengineer-admin/src/aceengineer_admin/` package exists (subdirs: `automation/`, `common/`, `invoice/`, `knowledge/`, `tax/`, `tests/`, plus `cli.py` and `__init__.py`)
- Confirmed: `aceengineer-admin/tests/` has more content than the issue body claimed. Actual contents:
  - `tests/knowledge/` → `conftest.py`, `__init__.py`, and 10 substantive test files (`test_anonymizer.py`, `test_code_scanner.py`, `test_knowledge_config.py`, `test_project_scanner.py`, `test_schema.py`, `test_simulation_scanner.py`, `test_spreadsheet_scanner.py`, `test_sqlite_backend.py`, `test_standards_scanner.py`, `test_unified_index.py`)
  - `tests/unit/` → `automation/test_cli.py` and `automation/common/test_config.py` (+ `__init__.py`)
  - `tests/integration/` and `tests/fixtures/` → empty scaffolding
- Confirmed: `.python-version` contains `3.11`
- Confirmed: `aceengineer-admin/.github/` directory does NOT exist (verified via `ls /mnt/local-analysis/workspace-hub/aceengineer-admin/.github/` → "No such file or directory"). There is no pre-existing CI workflow of any kind.
- Root-level one-shot scripts (`generate_invoice_from_config.py`, `convert_invoice_to_pdf.py`, `analyze_timesheet.py`, etc.) — confirmed present; these are positional-arg CLI wrappers coupled to real xlsx/docx files and are explicitly out of CI scope.

### Standards

Not applicable — this is infrastructure/CI, not an engineering standards-backed computation.

### LLM Wiki pages consulted

No relevant wiki pages — CI bootstrap.

### Documents consulted

- Sibling template chosen: `digitalmodel/.github/workflows/workflow-automation-tests.yml` — single job, matrix-driven, `astral-sh/setup-uv@v5` + `uv pip install -e ".[dev]"` + `pytest` + coverage upload. Closest structural and stack match to aceengineer-admin (same uv + ruff + pytest-cov profile; path-scoped triggers).
- Sibling template rejected: `digitalmodel/.github/workflows/quality-gates.yml` — too heavy (requires a repo-local `quality_gates_cli`, bandit, artifact uploads, PR commenter). Overkill for a greenfield minimal-viable CI.
- Sibling reference (not adapted): `workspace-hub/.github/workflows/baseline-check.yml` — uses `python -m pip` instead of uv-native, includes governance + shell-test jobs specific to workspace-hub. Structurally divergent.
- Issue body (#2444) — scoping decisions (src/ + tests/ only; skip root one-shots; PII-path-ignore list).
- Parent meta-issue #2424 — ecosystem CI rollout context.
- User memory: `feedback_never_offer_to_self_label_plan_approved` — plan-approval remains user-in-loop.

### Gaps identified

- No `.github/workflows/ci.yml` in aceengineer-admin (this plan creates it)
- No path-ignore filter currently exists; PII-carrying document directories would otherwise trigger CI on every xlsx edit
- Current single-batch test suite has never been executed in CI; first run may surface latent failures in the existing 12+ test files (particularly `tests/knowledge/` which depends on optional `sentence-transformers`/`numpy` extras — flagged as a risk, mitigated by installing only `[test]` extras and skipping semantic tests via pytest markers or `-k` filter on first run if needed)

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view 2444`):
- `#2444` — OPEN — "chore(ci-health): aceengineer-admin — add minimal viable CI (uv + ruff + black + pytest) scoped to src/ + tests/"
- Labels: `cat:infrastructure`, `status:plan-approved` (NOTE: label present pre-plan — governance drift from parent-issue labeling; this plan is still being drafted, so plan-approval must come from user after adversarial review per `feedback_never_offer_to_self_label_plan_approved`)
- Comments: 0

**File existence** (verified 2026-04-21):
- EXISTS: `aceengineer-admin/pyproject.toml` (3,200 bytes approx, 129 lines)
- EXISTS: `aceengineer-admin/src/aceengineer_admin/` (package dir)
- EXISTS: `aceengineer-admin/tests/unit/automation/test_cli.py`
- EXISTS: `aceengineer-admin/tests/knowledge/test_*.py` (10 files)
- EXISTS: `aceengineer-admin/.python-version` (contents: `3.11`)
- MISSING (new — this plan creates): `aceengineer-admin/.github/workflows/ci.yml`

**Line excerpt — pyproject testpaths** (`sed -n 67,73p pyproject.toml`):
```
[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --strict-markers --cov=src --cov-report=term-missing"
testpaths = ["tests", "src/aceengineer_admin/tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

**Gap proof — no CI**:
- `ls aceengineer-admin/.github/` → "No such file or directory" — confirms no CI workflow exists.

**Source count:** 6 (issue body + aceengineer-admin pyproject.toml + aceengineer-admin tree + digitalmodel workflow-automation-tests.yml + digitalmodel quality-gates.yml + workspace-hub baseline-check.yml).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md |
| New CI workflow | `aceengineer-admin/.github/workflows/ci.yml` |
| Plan review — Claude | scripts/review/results/2026-04-21-plan-2444-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-21-plan-2444-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-21-plan-2444-gemini.md |
| Sibling template referenced | digitalmodel/.github/workflows/workflow-automation-tests.yml |

---

## Deliverable

A single `aceengineer-admin/.github/workflows/ci.yml` that runs `uv sync --extra test --extra dev` → `ruff check src tests` → `black --check src tests` → `pytest` on Python 3.11 and 3.12 on ubuntu-latest, path-filtered to exclude PII-carrying directories and agent-harness scaffolding, producing a green first run that reports the existing test suite result.

---

## Pseudocode

T1 — trivial. See Files to Change. Workflow structure follows the digitalmodel `workflow-automation-tests.yml` template with these substitutions: `tests/workflows/workflow_automation/` → `src tests`; `workflow-automation list` CLI smoke → removed (aceengineer CLI `aceengineer` exists but not validated here — reserve for follow-up); codecov upload → removed (optional, not required for minimal viable).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `aceengineer-admin/.github/workflows/ci.yml` | sole deliverable — CI workflow |

**Note:** this plan does NOT modify `workspace-hub/docs/plans/README.md` (explicit hard constraint from planning task). The index row must be added by a later governance step.

---

## TDD Test List

CI infrastructure — no unit-test TDD. Acceptance is workflow-run green. Informal test list:

| Test | What it verifies | Pass condition |
|---|---|---|
| trigger-on-push | workflow runs on push to main touching `src/` | GitHub Actions run appears |
| trigger-on-src-change | PR that edits `src/aceengineer_admin/cli.py` triggers CI | run queued |
| no-trigger-on-xlsx | commit that only edits `invoices/**/*.xlsx` does NOT trigger CI | no run queued |
| no-trigger-on-agent-harness | commit that only edits `.claude/**` does NOT trigger CI | no run queued |
| ruff-gate | ruff check on `src/ tests/` passes on first run (or surfaces real issues to be fixed) | step exit 0 OR known-issue list captured |
| black-gate | black --check on `src/ tests/` passes | step exit 0 OR formatting fixed in same PR |
| pytest-gate | pytest runs and reports PASS/FAIL counts for existing test files | step exits 0, coverage printed |
| matrix-coverage | both py3.11 and py3.12 jobs complete | 2 green jobs |

---

## Acceptance Criteria

- [ ] `aceengineer-admin/.github/workflows/ci.yml` is committed to aceengineer-admin `main` (after user `status:plan-approved` + marker)
- [ ] First GitHub Actions run on aceengineer-admin after merge is GREEN on both py3.11 and py3.12 (ubuntu-latest)
- [ ] Workflow skips xlsx/docx-only commits via `paths-ignore`
- [ ] Workflow scopes lint and tests to `src/` + `tests/` — does NOT attempt to lint root-level one-shot scripts
- [ ] Lint step (ruff + black) completes within 2 minutes per matrix cell
- [ ] Pytest step respects `pyproject.toml` `testpaths` (no `--rootdir` override)
- [ ] Summary comment posted back to issue #2444 with the Actions run URL and the resulting status
- [ ] Adversarial review artifacts (Claude + Codex + Gemini) posted under `scripts/review/results/` before user approval

---

## Detailed CI Workflow Spec

This section freezes the target file content so reviewers can verify correctness without guessing.

**File:** `aceengineer-admin/.github/workflows/ci.yml`

**Triggers:**
- `push` on branches: `main`
- `pull_request` (any branch into `main`)
- `paths-ignore` applies to both trigger types:
  - `invoices/**`
  - `employees/**`
  - `taxes/**`
  - `Tax/**`
  - `contracts/**`
  - `reports/**`
  - `data/**`
  - `SA/**`
  - `Sabitha/**`
  - `preferred_vendor/**`
  - `Experience/**`
  - `00_office_opening/**`
  - `admin/**`
  - `Superseded/**`
  - `**/*.xlsx`
  - `**/*.docx`
  - `**/*.pdf`
  - `CLAUDE.md.backup*`
  - `.agent-os/**`
  - `.claude/**`
  - `.codex/**`
  - `.cursor/**`
  - `.gemini/**`
  - `.drcode/**`
  - `.common/**`
  - `.git-commands/**`
  - `.slash-commands/**`
  - `.hive-mind/**`
  - `docs/**`
  - `**/*.md`

**Jobs (single job `ci`):**

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ['3.11', '3.12']
runs-on: ubuntu-latest
```

**Steps (ordered):**
1. `actions/checkout@v4`
2. `astral-sh/setup-uv@v5` with `enable-cache: true`
3. `actions/setup-python@v5` with `python-version: ${{ matrix.python-version }}`
4. `uv venv && echo "$PWD/.venv/bin" >> $GITHUB_PATH`
5. `uv pip install -e ".[dev,test]"` (installs black, ruff, pytest, pytest-cov, pytest-mock, pytest-asyncio)
6. Ruff: `uv run ruff check src tests`
7. Black: `uv run black --check src tests`
8. Pytest: `uv run pytest` (respects `pyproject.toml` testpaths)
9. Smoke compile (optional, final step): `uv run python -m compileall -q src tests`

**Not included (deferred to follow-ups):**
- Codecov upload
- Windows/macOS matrix rows
- Python 3.13
- CLI smoke (`aceengineer --help`) — can be added once entrypoint is validated
- mypy step — `dev` extra includes it but pyproject does not declare strict mode; adding it would likely fail first run

---

## Risks and Open Questions

- **Risk (HIGH):** `tests/knowledge/` suite may depend on the `knowledge-semantic` extra (`sentence-transformers`, `numpy`). If tests fail-import on first run, either (a) install `[knowledge-semantic]` extra as well, or (b) exclude `tests/knowledge/` via `pytest --ignore=tests/knowledge` on first run and open a follow-up issue. **Open for reviewer:** which mitigation is preferred?
- **Risk (MEDIUM):** existing `tests/unit/automation/test_cli.py` and `tests/unit/automation/common/test_config.py` have never run in CI — first run may surface latent failures. Mitigation: if pytest fails on first CI run, capture the failure list in an issue comment, triage, and either fix or `pytest.skip` per-test before re-enabling the gate. Do NOT `fail_under` coverage on first run (already `0` in pyproject).
- **Risk (MEDIUM):** ruff and black have never been enforced. First run may surface formatting issues across `src/`. Mitigation: run `uv run ruff check --fix src tests` + `uv run black src tests` locally during implementation (after `plan-approved`), commit the formatting fixes in the same PR as the workflow file.
- **Risk (LOW):** path-ignore list is long; any missing path means CI burns minutes on doc-only commits. Tolerable — fix forward when noticed.
- **Risk (LOW):** `invoice_config_2025-10.yaml` (client name + rate) sits at repo root and would be included in any CI-triggering commit diff (it is a `.yaml`, not covered by `paths-ignore`). Even though CI doesn't read its contents, the GitHub Actions event payload may log the filename. Acceptable (private repo); flagged for awareness.
- **Open:** should `workflow_dispatch` be added for manual re-runs? Recommended yes (zero cost, aids debugging). Defer to reviewer.
- **Open:** should `fail-fast: false` stay? Recommended yes so py3.11 and py3.12 failures surface independently on first run.
- **Open:** parent meta-issue #2424 may prescribe a standard workflow template. Not yet audited. If #2424 surfaces a canonical template after this plan lands, this workflow will be migrated in a follow-up.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING — review wave has not been dispatched yet.

---

## Complexity: T1

**T1** — single new file in an external repo, no code changes, no tests to author, adapts a well-understood sibling template. No Pseudocode needed. No TDD in the strict sense (CI infrastructure). Risk is confined to first-run green/red outcome, which is reversible.
