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
- Current single-batch test suite has never been executed in CI; first run may surface latent failures. Verified defects (2026-04-21):
  - `tests/unit/automation/test_cli.py:6` imports `from aceengineer_automation.cli import main` — module was renamed to `aceengineer_admin.cli`; import will fail at collection.
  - `tests/unit/automation/common/test_config.py:8` imports `from aceengineer_automation.common.config import Config` — same rename; import will fail at collection.
  - `src/aceengineer_admin/automation/cli.py:6` imports `from aceengineer_automation import __version__` — same rename; affects runtime.
  All three must be updated as part of this plan's implementation scope or first-run green is impossible.
- `tests/knowledge/` suite: earlier draft flagged `sentence_transformers`/`numpy` as collection-time import risk. Re-verified via `grep -l "sentence_transformers\|numpy" tests/knowledge/*.py` — no top-level imports found; matches in `test_code_scanner.py` and `test_project_scanner.py` are string-literal fixture payloads. Risk downgraded to MEDIUM. However, `tests/knowledge/` has not been executed end-to-end in this environment, so this plan elects Option A2 (`--ignore=tests/knowledge`) for the first CI run and opens a follow-on issue to enable the suite with proper extras.

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

A single `aceengineer-admin/.github/workflows/ci.yml` that runs `uv sync --frozen --extra dev --extra test` → package-import smoke (`python -c "import aceengineer_admin"`) → `ruff check src tests` → `black --check src tests` → `pytest --ignore=tests/knowledge` on Python 3.11 and 3.12 on ubuntu-latest, triggered by positive `paths:` filter restricted to `src/**`, `tests/**`, `pyproject.toml`, and `.github/workflows/**`, producing a green first run that reports the existing test suite result (excluding the `tests/knowledge/` subtree, which is deferred to a follow-on issue). Plan implementation also updates three stale `aceengineer_automation.*` import sites so the suite can actually collect.

---

## Pseudocode

T1 — trivial. See Files to Change. Workflow structure follows the digitalmodel `workflow-automation-tests.yml` template with these substitutions (every deviation disclosed here): `tests/workflows/workflow_automation/` → `src tests`; `workflow-automation list` CLI smoke → removed (aceengineer CLI entrypoint exists but not validated here — reserved for follow-up); codecov upload → removed; template's `Verify package installation` step retained, rewritten as `uv run python -c "import aceengineer_admin"`; `uv pip install -e ".[dev]"` → `uv sync --frozen --extra dev --extra test` (repo has a committed `uv.lock`, so `uv sync --frozen` gives reproducible installs); manual `uv venv && echo "$PWD/.venv/bin" >> $GITHUB_PATH` step removed (redundant with `uv run`, per Gemini finding); step order `actions/setup-python@v5` → `astral-sh/setup-uv@v5` preserved exactly from template; pytest narrowed via `--ignore=tests/knowledge` for first run; windows-latest and py3.13 matrix cells dropped (see Risks). `workflow_dispatch` and `concurrency` added (zero template precedent, rationale in Risks).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `aceengineer-admin/.github/workflows/ci.yml` | primary deliverable — CI workflow |
| Modify | `aceengineer-admin/tests/unit/automation/test_cli.py` | line 6: `from aceengineer_automation.cli import main` → `from aceengineer_admin.automation.cli import main` — stale import blocks pytest collection |
| Modify | `aceengineer-admin/tests/unit/automation/common/test_config.py` | line 8: `from aceengineer_automation.common.config import Config` → `from aceengineer_admin.common.config import Config` — stale import blocks pytest collection |
| Modify | `aceengineer-admin/src/aceengineer_admin/automation/cli.py` | line 6: `from aceengineer_automation import __version__` → `from aceengineer_admin import __version__` — stale import affects package runtime |

**Verification command (before implementation starts):**
```
cd aceengineer-admin && grep -rn "aceengineer_automation" tests/ src/ 2>&1
```
All three sites above must be updated; re-run the grep after the edit to confirm zero hits. If new hits appear after a rebase, add them to the edit list.

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
- [ ] Three stale-import fixes (see §Files to Change) committed in the same PR as the workflow
- [ ] First GitHub Actions run on aceengineer-admin after merge is GREEN on both py3.11 and py3.12 (ubuntu-latest), scope: `tests/unit/` + `src/` (i.e., `pytest --ignore=tests/knowledge`)
- [ ] Workflow triggers ONLY on changes to `src/**`, `tests/**`, `pyproject.toml`, or `.github/workflows/**` (positive `paths:` filter)
- [ ] Workflow is manually triggerable via `workflow_dispatch`
- [ ] Workflow concurrency group cancels superseded PR commits
- [ ] Package import smoke (`python -c "import aceengineer_admin"`) runs and passes on both matrix cells
- [ ] Lint step (ruff + black) completes within 2 minutes per matrix cell
- [ ] Pytest step respects `pyproject.toml` `testpaths` (no `--rootdir` override)
- [ ] Adversarial review artifacts (Claude + Codex + Gemini) posted under `scripts/review/results/` before user approval
- [ ] Follow-on issue opened to re-enable `tests/knowledge/` with `[knowledge-semantic]` extra once ML-extras-on-runner footprint is scoped

**Post-merge governance (tracked separately, NOT workflow steps):**
- Human-authored summary comment posted to issue #2444 with the first Actions run URL and resulting status.

---

## Detailed CI Workflow Spec

This section freezes the target file content so reviewers can verify correctness without guessing.

**File:** `aceengineer-admin/.github/workflows/ci.yml`

**Triggers (positive `paths:` filter, matching source template's scoping style):**
- `push` on branches: `main`
- `pull_request` (any branch into `main`)
- `workflow_dispatch` (manual re-runs for debugging — zero cost, essential for first-run rollout)
- `paths:` applies to both `push` and `pull_request`:
  - `src/**`
  - `tests/**`
  - `pyproject.toml`
  - `uv.lock`
  - `.github/workflows/**`

Positive `paths:` intrinsically excludes PII-carrying directories (`invoices/**`, `employees/**`, `taxes/**`, `Tax/**`, `contracts/**`, etc.) and agent-harness scaffolding (`.claude/**`, `.codex/**`, `.cursor/**`, etc.) because those paths are NOT listed. This is tighter and less error-prone than the earlier broad `paths-ignore` approach — any new private directory added to the repo is automatically excluded from CI triggers.

**Concurrency:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Jobs (single job `ci`):**

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ['3.11', '3.12']
runs-on: ubuntu-latest
```

**Steps (ordered — preserves source template's `setup-python` → `setup-uv` order exactly):**
1. `actions/checkout@v4`
2. `actions/setup-python@v5` with `python-version: ${{ matrix.python-version }}`
3. `astral-sh/setup-uv@v5` with `enable-cache: true`
4. Install dependencies: `uv sync --frozen --extra dev --extra test` (reproducible install from committed `uv.lock`; installs black, ruff, pytest, pytest-cov, pytest-mock, pytest-asyncio). The redundant manual `uv venv && echo "$PWD/.venv/bin" >> $GITHUB_PATH` step is omitted — `uv run` resolves the project venv automatically (Gemini finding).
5. Package import smoke: `uv run python -c "import aceengineer_admin"` (verifies installed package is importable — direct adaptation of template's `Verify package installation` step)
6. Ruff: `uv run ruff check src tests`
7. Black: `uv run black --check src tests`
8. Pytest: `uv run pytest --ignore=tests/knowledge` (first-run policy — `tests/knowledge/` deferred to follow-on issue pending verified footprint of `[knowledge-semantic]` extra on GitHub-hosted runners)

**Not included (deferred to follow-ups):**
- Codecov upload
- Windows/macOS matrix rows — see Risks entry
- Python 3.13 — see Risks entry
- CLI smoke (`aceengineer --help`) — can be added once entrypoint is validated
- mypy step — `dev` extra includes it but pyproject does not declare strict mode; adding it would likely fail first run
- `tests/knowledge/` subtree — re-enable in follow-on issue with `[knowledge-semantic]` extra (`sentence-transformers`, `numpy`) after confirming install footprint on ubuntu-latest runners
- `compileall` step (dropped; package-import smoke is a stronger check)

---

## Risks and Open Questions

- **Risk (MEDIUM, downgraded from HIGH):** `tests/knowledge/` suite. Re-verified via `grep -l "sentence_transformers\|numpy" tests/knowledge/*.py` — no top-level imports; matches are string-literal fixture payloads. Collection-time ImportError is unlikely but suite has not been executed end-to-end here. **Resolution (committed):** Option A2 — `pytest --ignore=tests/knowledge` on first CI run; follow-on issue re-enables the suite with verified `[knowledge-semantic]` extra footprint on GitHub-hosted runners.
- **Risk (MEDIUM, now a hard implementation item):** stale imports in three files (see §Files to Change). Without the rename fixes, pytest collection fails on `tests/unit/automation/test_cli.py` and `tests/unit/automation/common/test_config.py`. Mitigation: fix the three sites in the same PR as the workflow; verify with `grep -rn "aceengineer_automation" tests/ src/` returning zero hits.
- **Risk (MEDIUM):** ruff and black have never been enforced. First run may surface formatting issues across `src/`. Mitigation: run `uv run ruff check --fix src tests` + `uv run black src tests` locally during implementation (after `plan-approved`), commit the formatting fixes in the same PR as the workflow file.
- **Risk (LOW):** positive `paths:` filter may be too restrictive if future work adds a new top-level product directory. Tolerable — fix forward when noticed.
- **Risk (LOW):** `invoice_config_2025-10.yaml` (client name + rate) sits at repo root. Not included in positive `paths:` filter, so it will not trigger CI; GitHub event payload may still log the filename on commits. Acceptable (private repo); flagged for awareness.
- **Risk (LOW, tracked):** windows-latest and py3.13 intentionally out of scope; source template included `windows-latest`. aceengineer-admin is a Windows-first invoice/docx/xlsx toolchain in production, so Windows-specific regressions (path separators, openpyxl behaviors, locale) will not be caught. Revisit in follow-on issue if/when product code targets either; open that issue as part of the same PR's post-merge governance.
- **Decided (was Open):** `workflow_dispatch` — YES, included in the spec above. Manual re-runs are essential for first-run debugging.
- **Decided (was Open):** `fail-fast: false` — YES, retained. py3.11 and py3.12 failures surface independently on first run.
- **Open:** parent meta-issue #2424 may prescribe a standard workflow template. Not yet audited. If #2424 surfaces a canonical template after this plan lands, this workflow will be migrated in a follow-up.

---

## Adversarial Review Summary

### Wave 1

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | uv sync vs uv pip install contradiction; HIGH risk speculative and unmitigated; template step order silently swapped; package-import smoke dropped; `workflow_dispatch` omitted; issue-comment AC has no workflow step; no concurrency group; Windows drop untracked |
| Codex | MAJOR | Deliverable claims src/+tests/ scope but spec uses `paths-ignore` only (not positive `paths:`); `knowledge-semantic` decision unresolved while AC demands GREEN; stale `aceengineer_automation.*` imports in `tests/unit/automation/*` (collection-time failure); Deliverable/Spec command contradiction |
| Gemini | MINOR | `knowledge-semantic` decision punted to reviewer; `workflow_dispatch` omitted; redundant manual `$GITHUB_PATH` alongside `uv run` |

**Wave 1 overall:** MAJOR (two MAJOR, one MINOR; convergence on three issues — install-command contradiction, unresolved `knowledge-semantic` mitigation, missing `workflow_dispatch`).

### Revisions made (Wave 2 response)

- Resolved `uv sync` vs `uv pip install -e` contradiction — adopted `uv sync --frozen --extra dev --extra test` in both Deliverable and Detailed Spec (honors committed `uv.lock`).
- Committed to Option A2 for `knowledge-semantic`: `pytest --ignore=tests/knowledge` on first CI run; follow-on issue for re-enablement; acceptance scoped to `tests/unit/` + `src/`.
- Added `workflow_dispatch:` to the on-triggers block.
- Added three stale-import fixes to §Files to Change (`tests/unit/automation/test_cli.py`, `tests/unit/automation/common/test_config.py`, `src/aceengineer_admin/automation/cli.py`) — Codex's unique implementation-blocking finding. Added verification grep command.
- Converted workflow trigger from broad `paths-ignore` to positive `paths:` list (`src/**`, `tests/**`, `pyproject.toml`, `uv.lock`, `.github/workflows/**`) matching template's scoping style; updated Deliverable to match.
- Re-verified `knowledge-semantic` evidence — grep confirmed matches are string-literal fixture payloads, not real imports. Risk downgraded from HIGH to MEDIUM; rationale documented.
- Preserved source template's `setup-python` → `setup-uv` step order (reversed in earlier draft); disclosed in Pseudocode substitutions.
- Re-added package-import smoke (`uv run python -c "import aceengineer_admin"`) replacing the dropped `compileall` step.
- Removed the issue-comment acceptance criterion from the workflow scope; moved to a separate post-merge governance checklist.
- Added explicit Risks entry noting windows-latest + py3.13 out of scope with follow-on issue commitment.
- Added `concurrency: group: ${{ github.workflow }}-${{ github.ref }} cancel-in-progress: true` block.
- Removed the redundant manual `uv venv && echo "$PWD/.venv/bin" >> $GITHUB_PATH` step (Gemini finding).

### Revisions deferred

- None material. All Wave 1 convergent blockers and singleton high-severity findings were addressed in Wave 2. Open item: parent meta-issue #2424 canonical-template audit — remains an Open question in Risks because it is external to this plan's scope and would be addressed as a follow-up migration if #2424 surfaces a template after landing.

**Status:** revised — awaiting Wave 2 re-review.

---

## Complexity: T1

**T1** — single new file in an external repo, no code changes, no tests to author, adapts a well-understood sibling template. No Pseudocode needed. No TDD in the strict sense (CI infrastructure). Risk is confined to first-run green/red outcome, which is reversible.
