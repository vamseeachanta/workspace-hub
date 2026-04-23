# Plan for #2459: assethold post-smoke CI hardening

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2459
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2459-claude.md | scripts/review/results/2026-04-22-plan-2459-codex.md | scripts/review/results/2026-04-22-plan-2459-gemini.md | scripts/review/results/2026-04-23-plan-2459-claude.md | scripts/review/results/2026-04-23-plan-2459-codex.md | scripts/review/results/2026-04-23-plan-2459-gemini.md | scripts/review/results/2026-04-23-plan-2459-disagreement.md
> **Parent issues:** #2442, #2448

---

## Resource Intelligence Summary

### Existing repo code
- Found: `assethold/.github/workflows/python-tests.yml` — current matrix workflow already clears checkout, dependency install, project install, and `Run smoke tests first` on all OSes after #2448, but still fails later at `Lint with flake8` on linux/macos and `Type checking with mypy` on windows.
- Found: `assethold/.github/workflows/python-tests.yml` lines 75-119 — the `test` job installs lint/type/test tooling, runs smoke first, then flake8 + mypy, then `Run unit tests with coverage` using `pytest tests/unit/ --cov=src --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing --cov-fail-under=80 --junitxml=pytest-unit.xml --verbose -m "unit"`; any local validation story therefore needs both isolated TDD commands and a workflow-shape coverage command.
- Found: `assethold/.github/workflows/python-tests.yml` lines 89-98 — `flake8 .` currently targets the repo root while `mypy src/ --ignore-missing-imports` targets the package tree only, producing an asymmetric gate surface.
- Found: `assethold/src/assethold/signals/watchlist.py` — current mypy blocker cluster includes nullable `_data` handling plus `yaml` stub/import typing issues; this file already has unit coverage under `assethold/tests/unit/signals/test_watchlist.py`.
- Found: `assethold/src/assethold/modules/reporting/utils/path_utils.py` — current mypy blocker includes missing `os` import in the package copy; the repo also contains a duplicate non-package copy at `assethold/modules/reporting/utils/path_utils.py`, which is one of the root-level lint surfaces.
- Found: `assethold/.agent-os/modules/prompt_enhancement.py` and `assethold/scripts/agent-os/create-spec-enhanced.py` — current linux flake8 failures include syntax/undefined-name errors in these auxiliary paths, demonstrating that `flake8 .` is currently enforcing more than the installable package surface.
- Found: `assethold/tests/test_smoke.py` — smoke suite exists and is already green in CI, so #2459 is strictly a post-smoke hardening tranche rather than another smoke-unblock issue.

### Standards
Not applicable — this is CI/infrastructure hardening, not a domain engineering standards issue.

### LLM Wiki pages consulted
No relevant wiki pages; the issue is workflow/repo hygiene rather than domain knowledge.

### Documents consulted
- Issue #2459 body — defines the split scope: post-smoke lint/mypy/quality-gate hardening only, explicitly separate from #2448 smoke unblock.
- Issue #2448 closeout comments — confirm the exact split at run `24792043821`: smoke milestone complete, broader lint/mypy/quality-gate debt intentionally deferred into #2459.
- `docs/plans/2026-04-21-issue-2442-assethold-python-tests.md` — earlier approved CI plan establishes the repo convention that matrix/test-gate work should be split into bounded tranches rather than silently absorbing broader debt.
- `assethold/AGENTS.md` — repo contract identifies `src/assethold/` as the source surface and `uv run python -m pytest tests/ --noconftest` as the canonical test command.
- `vamseeachanta/assethold#31` — existing open repo issue already tracks broad quality-gate / type-coverage debt across many modules, so #2459 does not need to absorb the entire 286-error mypy backlog.
- `vamseeachanta/assethold#45` — newly created follow-up to clean or retire broken auxiliary `.agent-os/` / `scripts/agent-os/` Python files once they are excluded from the package lint gate.
- `vamseeachanta/assethold#46` — newly created follow-up to reconcile the duplicate non-package `modules/reporting/utils/path_utils.py` helper once the package CI tranche excludes it.

### Gaps identified
- No canonical local plan artifact existed for #2459 before this planning pass.
- No approval-state artifacts existed for #2459 (`status:plan-review`, `status:plan-approved`, `.planning/plan-approved/2459.md`).
- Lint gate is not aligned with the bounded package surface: linux/macos currently fail on auxiliary root-level files outside `src/assethold/`.
- Mypy gate is too broad to fix opportunistically in one pass: local repro shows 286 errors across 39 files in `src/assethold/`.
- No current narrowing policy is documented for what #2459 should repair now versus split into follow-up issues later, including the fact that narrowing mypy from `src/` to two files is an intentional temporary regression in gate breadth to unblock the first real post-smoke failures.
- No persisted enforcement currently ensures the workflow-shape contract after this tranche; a verifier script alone would drift unless the workflow runs it in CI.
- Coverage is now the most likely next blocker once flake8/mypy are cleared: a CI-parity local run currently finishes 869 unit tests green but fails `--cov-fail-under=80` with total coverage `60.70%`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view`):
- `#2459` — OPEN — `follow-up(ci): assethold python-tests still red after smoke unblock — lint/mypy/quality-gate hardening`
- `#2448` — CLOSED — smoke unblock landed; closeout explicitly defers broader lint/mypy/quality-gate work to #2459
- `#2442` — CLOSED — original assethold python-tests repair milestone
- `assethold#31` — OPEN — `Enforce quality gates — test coverage, mypy, loguru initialization`
- `assethold#45` — OPEN — `follow-up(ci): clean or retire auxiliary agent-os Python files excluded from package lint gate`
- `assethold#46` — OPEN — `follow-up(ci): reconcile duplicate non-package reporting path_utils helper`

**Issue body / closeout excerpts**
```text
#2459 body excerpt:
- deliverables explicitly call for removing the current first post-smoke blockers and capturing the next exposed failure surface
- scope note explicitly says this tranche does not promise full repo-wide lint/type debt cleanup in one issue

#2448 final closeout excerpt:
- final run `24792043821`
- residual work explicitly split out:
  - Linux/macOS later fail at `Lint with flake8`
  - Windows later fail at `Type checking with mypy`
  - `Quality Gate` remains red because upstream jobs remain red
- tracked separately in: `#2459`

assethold#31 excerpt:
- broad repo quality work: test coverage, repo-wide mypy enforcement, logging initialization

assethold#45 excerpt:
- tracks excluded `.agent-os/` / `scripts/agent-os/` Python cleanup after package lint is narrowed

assethold#46 excerpt:
- tracks the duplicate non-package `modules/reporting/utils/path_utils.py` helper after package CI stops checking it

assethold follow-up JSON excerpt:
- `{"number":31,"state":"OPEN","title":"Enforce quality gates — test coverage, mypy, loguru initialization","url":"https://github.com/vamseeachanta/assethold/issues/31"}`
- `{"number":45,"state":"OPEN","title":"follow-up(ci): clean or retire auxiliary agent-os Python files excluded from package lint gate","url":"https://github.com/vamseeachanta/assethold/issues/45"}`
- `{"number":46,"state":"OPEN","title":"follow-up(ci): reconcile duplicate non-package reporting path_utils helper","url":"https://github.com/vamseeachanta/assethold/issues/46"}`

runtime-safety grep excerpt:
- `git grep -n "prompt_enhancement" -- src tests` -> no matches
- `git grep -n "create-spec-enhanced" -- src tests` -> no matches
- `git grep -n "agent-os" -- src tests` -> only config / shell / doc-string references, not Python imports of the broken auxiliary files
```

**File existence** (verified 2026-04-22):
- EXISTS: `assethold/.github/workflows/python-tests.yml`
- EXISTS: `assethold/src/assethold/signals/watchlist.py`
- EXISTS: `assethold/src/assethold/modules/reporting/utils/path_utils.py`
- EXISTS: `assethold/modules/reporting/utils/path_utils.py`
- EXISTS: `assethold/.agent-os/modules/prompt_enhancement.py`
- EXISTS: `assethold/scripts/agent-os/create-spec-enhanced.py`
- EXISTS: `assethold/tests/unit/signals/test_watchlist.py`
- EXISTS (created in this planning pass): `docs/plans/2026-04-22-issue-2459-assethold-post-smoke-ci-hardening.md`

**Line excerpts**
```text
assethold/.github/workflows/python-tests.yml
84-97:
- Run smoke tests first
- run: pytest tests/test_smoke.py --verbose --tb=short
- Lint with flake8
- flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
- flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
- Type checking with mypy
- run: mypy src/ --ignore-missing-imports

assethold/.agent-os/modules/prompt_enhancement.py
460-494:
- returns an unterminated triple-quoted string block; CI flake8 reports E999 at line 460 detected at line 494

assethold/src/assethold/modules/reporting/utils/path_utils.py
118-132:
- uses `os.path.commonprefix(...)` at line 125 without importing `os`

assethold/AGENTS.md
1-5:
- `entry_points: [src/assethold/engine.py, src/assethold/fundamentals.py, src/assethold/analysis/]`
- `test_command: uv run python -m pytest tests/ --noconftest`
- `depends_on: [assetutilities]`
```

**Gap proofs**
- `gh run view 24792043821 --json jobs` → ubuntu/macos jobs fail at step `Lint with flake8`; windows jobs pass flake8 and fail at step `Type checking with mypy`; `Quality Gate` fails only because upstream jobs are red.
- `uv run mypy src/ --ignore-missing-imports` (local, 2026-04-22) → `Found 286 errors in 39 files (checked 98 source files)`.
- `uv run --with types-PyYAML mypy src/assethold/signals/watchlist.py --ignore-missing-imports --follow-imports=silent` (local, 2026-04-22) → `Found 13 errors in 1 file (checked 1 source file)`.
- `uv run --with types-PyYAML mypy src/assethold/modules/reporting/utils/path_utils.py --ignore-missing-imports --follow-imports=silent` (local, 2026-04-22) → `Found 1 error in 1 file (checked 1 source file)`.
- `uv run --with ruff ruff check src/assethold tests/ --select E9,F63,F7,F82` (local, 2026-04-22) → currently reports only `src/assethold/modules/reporting/utils/path_utils.py:125:24 F821 Undefined name os`; this supports the bounded flake8 tranche choice.
- `uv run --with flake8 python -m flake8 src/assethold tests/ --count --select=E9,F63,F7,F82 --show-source --statistics` (local, 2026-04-22) → currently reports only `src/assethold/modules/reporting/utils/path_utils.py:125:24: F821 undefined name 'os'`; this is the exact first replacement lint gate the workflow will adopt.
- `uv run --with flake8 python -m flake8 src/assethold tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics` (planned validator, must be recorded during execution) → second replacement lint gate is warning-only because of `--exit-zero`, but the same path scope must still be exercised and preserved in the verifier.
- `gh run view 24792043821 --job 72551839963 --log-failed | grep -E "E999|F821" -n` (2026-04-22) → includes `./.agent-os/modules/prompt_enhancement.py:460:17: E999 SyntaxError: unterminated triple-quoted string literal`, `./scripts/agent-os/create-spec-enhanced.py:464:10: F821 undefined name 'validate'`, and `./src/assethold/modules/reporting/utils/path_utils.py:125:24: F821 undefined name 'os'`.
- `gh issue view 31 --repo vamseeachanta/assethold --json number,title,state,url` (2026-04-23) → confirms the broad quality-gate follow-up exists and remains open.
- `gh issue view 45 --repo vamseeachanta/assethold --json number,title,state,url` and `gh issue view 46 --repo vamseeachanta/assethold --json number,title,state,url` (2026-04-23) → confirm both exclusion-tracking follow-ups exist and remain open.
- `git grep -n "prompt_enhancement" -- src tests` and `git grep -n "create-spec-enhanced" -- src tests` (2026-04-23) → no matches; `git grep -n "agent-os" -- src tests` shows only config / shell / doc-string references, not Python imports of the broken auxiliary files.
- `uv run --project . python -m pytest -c pyproject.toml tests/unit/ --cov=src --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing --cov-fail-under=80 --junitxml=pytest-unit.xml --verbose -m unit` (local, 2026-04-23) → `869 passed` but `Coverage failure: total of 60.70 is less than fail-under=80.00`; this matches the workflow’s pass/fail + reporting shape closely enough to treat coverage as the evidence-backed next blocker after the flake8/mypy tranche.
- `search_files` over `assethold/tests/` found watchlist tests but no existing tests for `path_utils`, confirming a missing targeted regression test for that helper.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2459-assethold-post-smoke-ci-hardening.md` |
| Plan index row | `docs/plans/README.md` |
| Primary workflow | `assethold/.github/workflows/python-tests.yml` |
| Existing watchlist tests | `assethold/tests/unit/signals/test_watchlist.py` |
| New path-utils regression test | `assethold/tests/unit/modules/reporting/utils/test_path_utils.py` |
| Workflow verifier script | `assethold/scripts/ci/verify_python_tests_workflow.py` |
| Bounded source fixes | `assethold/src/assethold/signals/watchlist.py`, `assethold/src/assethold/modules/reporting/utils/path_utils.py` |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2459-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2459-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2459-gemini.md` |

---

## Deliverable

A bounded post-smoke CI contract patch that removes the current first post-smoke blockers by (1) scoping both flake8 commands to `src/assethold` plus `tests/`, (2) changing the workflow mypy gate to a targeted watchlist/path-utils tranche with explicit `types-PyYAML` installation and `--follow-imports=silent`, (3) enforcing a persisted workflow verifier inside the `test` job so those workflow-shape decisions stay guarded, and (4) repairing those concrete source files plus tests so the matrix advances to the next real failure surface. This plan explicitly treats the mypy narrowing as a temporary breadth regression accepted for unblock value, with re-expansion debt kept on `assethold#31`. Success for this tranche is: the workflow no longer stops first at linux/macos flake8 or windows repo-wide mypy, the verifier is enforced in CI, and the next exposed blocker is explicitly recorded; current evidence says that blocker is likely unit coverage rather than immediate full-green CI.

---

## Pseudocode

```text
function harden_python_tests_workflow():
    keep smoke step first unchanged
    run persisted workflow verifier inside the test job so future drift fails CI
    change both flake8 commands from repo-root to:
        src/assethold
        tests/
    leave any root auxiliary paths (.agent-os/, scripts/agent-os/, modules/) out of this tranche
    preserve smoke-before-lint ordering and preserve the single-line shell-neutral smoke command
    change mypy gate from repo-wide src/ to two explicit files:
        src/assethold/signals/watchlist.py
        src/assethold/modules/reporting/utils/path_utils.py
        with --follow-imports=silent
    document in workflow comments and plan text that this is a temporary gate narrowing,
        not a claim that repo-wide typing debt is solved
    install types-PyYAML in the workflow dependency step and use the same package for local targeted mypy verification
    add the verifier invocation to the same test job; dependency scope is test-job only, not integration/financial jobs
    implement verifier with YAML parse + explicit invariant checks + aggregated non-zero exit
    keep broad type-debt cleanup delegated to assethold#31 unless new evidence narrows it further

function repair_watchlist_typing():
    annotate _data as Optional[dict[str, Any]]
    normalize yaml.safe_load result to {} when file is empty/null
    guard all .get/index/save paths before dereferencing _data
    add/update unit tests proving load/add/remove behavior remains stable
    reach zero mypy errors under the targeted two-file mypy command

function repair_path_utils_typing():
    import os in the package path_utils module
    add targeted regression test for cross-root relative path fallback
    reach zero mypy errors under the targeted two-file mypy command
    explicitly leave the duplicate non-package path_utils copy out of scope for this tranche

function track_auxiliary_python_debt():
    reference assethold#45 for broken `.agent-os/` and `scripts/agent-os/` Python files excluded from package lint

function closeout_boundary(post_change_ci):
    if workflow advances past current flake8/mypy blockers and exposes a later-stage failure:
        keep #2459 scoped to the blocker-removal tranche
        explicitly record whether the next failure is the already-predicted coverage gate
        reference assethold#31 for broad quality/type debt
        create an additional follow-up only if the newly exposed failure is not already covered

function define_mypy_reexpansion_trigger():
    keep this tranche limited to watchlist + package path_utils
    require follow-up widening once assethold#31 lands a typed-surface inventory / next-file tranche
    do not claim two-file mypy scope is a stable end state
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `assethold/.github/workflows/python-tests.yml` | Change both flake8 commands from repo-root to the exact maintained tranche (`src/assethold` and `tests/`), add `types-PyYAML` in the `test` job install step, preserve smoke-before-lint / shell-neutral smoke invariants, change mypy from repo-wide `src/` to the targeted two-file tranche for this issue using `--follow-imports=silent`, and invoke the persisted workflow verifier in CI so the contract stays enforced |
| Modify | `assethold/src/assethold/signals/watchlist.py` | Repair the concrete mypy blocker cluster already visible in CI and local repro |
| Modify | `assethold/src/assethold/modules/reporting/utils/path_utils.py` | Fix missing `os` import / type-check blocker |
| Create | `assethold/tests/unit/modules/reporting/utils/test_path_utils.py` | Add targeted regression coverage for the package path-utils helper |
| Modify | `assethold/tests/unit/signals/test_watchlist.py` | Extend existing watchlist coverage to lock in the typed/nullable behavior repaired in this issue |
| Create | `assethold/scripts/ci/verify_python_tests_workflow.py` | Add a persisted verifier for flake8 scope, smoke-before-lint ordering, shell-neutral smoke command, targeted mypy command, verifier self-enforcement, and required `types-PyYAML` install so workflow validation is not just an ad hoc inline snippet |
| Update | `docs/plans/README.md` | Keep this plan indexed in the canonical ledger and update the row text only if the draft status note materially changes |
| Reference (no edit in this tranche) | `assethold/modules/reporting/utils/path_utils.py` | Explicitly out of scope as a non-package duplicate once flake8 is narrowed to the maintained tranche; future cleanup remains tracked separately |
| Reference (existing future work) | `vamseeachanta/assethold#31` | Existing repo issue already tracks broad quality-gate / mypy debt beyond this bounded tranche, including the now-evidenced coverage blocker |
| Reference (existing future work) | `vamseeachanta/assethold#45` | Tracks cleanup/removal of broken auxiliary `.agent-os/` / `scripts/agent-os/` Python files excluded from the package lint tranche |
| Reference (existing future work) | `vamseeachanta/assethold#46` | Tracks reconciliation of the duplicate non-package `modules/reporting/utils/path_utils.py` helper that this tranche intentionally excludes |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_relative_path_fallback_uses_common_prefix_root` | package path-utils fallback works when `relative_to` fails | two paths without direct parent/child relation | stable relative path string, no NameError |
| `test_watchlist_load_returns_mapping_when_yaml_empty` | empty/nullable YAML load is normalized safely | empty watchlist YAML | `{}`-compatible mapping, no None attr errors |
| `test_watchlist_add_stock_persists_without_nullable_internal_state_errors` | add/update path still persists after typing changes | valid temp YAML + new ticker | ticker saved, tests stay green |
| `test_watchlist_remove_stock_persists_without_nullable_internal_state_errors` | remove path still saves correctly | existing ticker in temp YAML | returns True and persists removal |
| `verify_python_tests_workflow_contract` | persisted verifier script proves both flake8 commands target `src/assethold` + `tests/`, smoke remains before lint/mypy, the verifier is self-enforced in the `test` job, and the smoke command stays single-line/shell-neutral | `.github/workflows/python-tests.yml` | exit 0 from verifier script |
| `test_unit_suite_ci_parity_coverage_gate` | CI-parity command still runs the unit suite and reports the real next blocker under the same marker/coverage shape as GitHub Actions | `tests/unit/` under `-m unit --cov=src --cov=. --cov-fail-under=80` | currently red on main because coverage is below 80; post-change verdict must be recorded honestly |

### TDD protocol for execution
- First extend `assethold/tests/unit/signals/test_watchlist.py`, create `assethold/tests/unit/modules/reporting/utils/test_path_utils.py`, and create `assethold/scripts/ci/verify_python_tests_workflow.py`.
- Mark the unit-test files with `pytestmark = pytest.mark.unit` so they execute under the existing CI `-m "unit"` filter.
- Before editing workflow/source files, run the narrowed static-analysis and persisted workflow-verifier commands expected after the workflow change and confirm they fail on current main. The verifier must fail explicitly when any of these are still true: flake8 target token is `.`, mypy target is `src/`, `types-PyYAML` is absent from the `test` job install step, or the workflow does not run the verifier script.
  ```bash
  cd assethold && uv run --with types-PyYAML mypy \
    src/assethold/signals/watchlist.py \
    src/assethold/modules/reporting/utils/path_utils.py \
    --ignore-missing-imports \
    --follow-imports=silent

  cd assethold && uv run python scripts/ci/verify_python_tests_workflow.py
  ```
- Also run the exact replacement flake8 gate and the CI-parity unit-coverage command before source/workflow edits so the plan has executable red-state proof for both the replacement lint surface and the next predicted blocker:
  ```bash
  cd assethold && uv run --with flake8 python -m flake8 src/assethold tests/ \
    --count --select=E9,F63,F7,F82 --show-source --statistics

  cd assethold && uv run --project . python -m pytest -c pyproject.toml tests/unit/ \
    --cov=src --cov=. --cov-fail-under=80 --verbose -m unit
  ```
- Run the targeted pytest commands and confirm at least one new/extended assertion fails before changing workflow or source files:
  ```bash
  cd assethold && uv run python -m pytest tests/unit/signals/test_watchlist.py --noconftest -o addopts= -q
  cd assethold && uv run python -m pytest tests/unit/modules/reporting/utils/test_path_utils.py --noconftest -o addopts= -q
  ```
- Only then edit `assethold/.github/workflows/python-tests.yml`, `src/assethold/signals/watchlist.py`, and `src/assethold/modules/reporting/utils/path_utils.py`.
- Re-run the same targeted tests, then `uv run python -m pytest tests/unit/ -m unit --noconftest -o addopts= -q`, then the exact replacement flake8 command, then the targeted mypy command, then `uv run python scripts/ci/verify_python_tests_workflow.py`, then the CI-parity unit-coverage command, then a CI run.

---

## Acceptance Criteria

- [ ] This plan is indexed in `docs/plans/README.md`.
- [ ] Adversarial review evidence is complete with 3 valid provider artifacts, and the summary table reflects the real verdicts / any invalid empty-artifact runs honestly.
- [ ] The workflow continues to pass `pytest tests/test_smoke.py --verbose --tb=short` before later gates.
- [ ] Both flake8 commands are changed from `.` to the exact maintained tranche: `src/assethold` and `tests/`.
- [ ] The exact replacement lint gate is verified locally with the same command shape the workflow will run:
  ```bash
  cd assethold && uv run --with flake8 python -m flake8 src/assethold tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
  ```
- [ ] The workflow mypy gate is changed from `mypy src/ --ignore-missing-imports` to a targeted command covering only `src/assethold/signals/watchlist.py` and `src/assethold/modules/reporting/utils/path_utils.py` for this tranche, using `--follow-imports=silent` to match the proven local scope.
- [ ] The plan and workflow comments explicitly frame the mypy change as a temporary gate narrowing / unblock tradeoff, not a claim that repo-wide mypy debt is solved; broad re-expansion remains tracked under `assethold#31`.
- [ ] `types-PyYAML` is added explicitly in the `test` job dependency-install step and the same package is used in local targeted mypy verification.
- [ ] The persisted workflow verifier is enforced in the `test` job itself, not only as a local developer aid.
- [ ] Local targeted validators pass using the repo’s canonical pytest invocation style with repo-wide addopts disabled for true red/green checks:
  ```bash
  cd assethold && uv run python -m pytest tests/unit/signals/test_watchlist.py --noconftest -o addopts= -q
  cd assethold && uv run python -m pytest tests/unit/modules/reporting/utils/test_path_utils.py --noconftest -o addopts= -q
  cd assethold && uv run python -m pytest tests/unit/ -m unit --noconftest -o addopts= -q
  cd assethold && uv run --with types-PyYAML mypy src/assethold/signals/watchlist.py src/assethold/modules/reporting/utils/path_utils.py --ignore-missing-imports --follow-imports=silent
  cd assethold && uv run python scripts/ci/verify_python_tests_workflow.py
  ```
- [ ] CI-parity local validation is also recorded with the same coverage/marker shape as the workflow, even if it remains red and becomes the next blocker:
  ```bash
  cd assethold && uv run --project . python -m pytest -c pyproject.toml tests/unit/ --cov=src --cov=. --cov-fail-under=80 --verbose -m unit
  ```
- [ ] The targeted mypy command reports zero errors on the two repaired source files.
- [ ] A post-change CI run proves the workflow clears the current first post-smoke blockers on the matrix cells that currently fail first (linux + macOS flake8, windows mypy) and records the next exposed failure surface explicitly by run ID, job/step name, and either (a) a closeout note or (b) a linked follow-up issue if additional work remains.
- [ ] Coverage is pre-called as the likely next blocker and the closeout must report whether the workflow in fact next fails at `Run unit tests with coverage`; if so, the failure is linked back to `assethold#31` unless a narrower new issue is required.
- [ ] Auxiliary broken Python outside the maintained tranche is explicitly tracked via `assethold#45`, the duplicate non-package `path_utils.py` is tracked via `assethold#46`, and broad repo-wide type debt remains tracked via `assethold#31`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR (fresh 2026-04-23 rerun) | Flagged approval-state contradiction (`draft` plan text vs existing `.planning/plan-approved/2459.md` and live `status:plan-approved`), stale review-state framing, Codex wrapper breakage, incomplete proof for the second flake8 command, and underspecified verifier contract / boundary evidence |
| Codex | UNAVAILABLE (fresh 2026-04-23 rerun) / MAJOR (last valid 2026-04-22 artifact) | Fresh rerun failed before review because the wrapper still passes unsupported `--no-interactive`; last valid Codex artifact remained MAJOR on boundary attestation and persisted-verifier concerns |
| Gemini | MAJOR (fresh 2026-04-23 rerun) | Flagged verifier script falling outside the narrowed flake8 boundary, `types-PyYAML` dependency-drift risk, local-command CI-parity overstatement, self-verifying workflow weakness, and missing negative tests for verifier failures |

**Current review state:** revision required; not approval-ready yet. Fresh 2026-04-23 rerun did not converge: two providers returned MAJOR and Codex was unavailable due to wrapper failure. The 2026-04-22 artifacts remain useful historical evidence, but they are no longer the newest wave.

Revisions made based on review:

- fixed the core mypy contradiction by explicitly changing the planned workflow gate from repo-wide `src/` to a targeted two-file tranche using `--follow-imports=silent`, with broad debt anchored to `assethold#31`
- made the mypy change’s tradeoff explicit: this tranche intentionally narrows a broken broader gate, and re-expansion remains future work rather than an implied green-state claim
- simplified flake8 targeting to `src/assethold` plus `tests/`, excluding only the already-split non-package auxiliary surfaces
- replaced brittle workflow-specific pytest-file ideas with a persisted workflow verifier script artifact (`assethold/scripts/ci/verify_python_tests_workflow.py`) and now require that verifier to run inside the workflow’s `test` job
- made `types-PyYAML` explicit in both workflow dependency installation and local targeted mypy verification, with scope stated as the `test` job only
- split local validation into two layers: isolated red/green pytest commands for TDD plus a CI-parity unit-suite coverage command so local acceptance cannot drift from CI behavior
- embedded live issue evidence for assethold issues `#31`, `#45`, and `#46`
- embedded no-import grep evidence showing the excluded broken auxiliary `.agent-os` / `scripts/agent-os` files are not imported from `src` or `tests`
- added exact replacement-gate flake8 evidence for `python -m flake8 src/assethold tests/ ...`
- added fresh coverage evidence showing the CI-parity unit command currently fails at `60.70%`, so the next likely blocker is now evidence-backed instead of speculative
- corrected the `path_utils.py` evidence citation to the in-scope package file
- tightened acceptance criteria around 3 valid provider artifacts, zero mypy errors on the targeted files, CI enforcement of the verifier, and explicit recording of the next exposed failure surface on the specific failing OS cells

---

## Risks and Open Questions

- **Risk:** Scoping flake8 to the maintained tranche may intentionally leave auxiliary root paths ungoverned; that is acceptable only because this plan explicitly tracks `.agent-os/` / `scripts/agent-os/` debt in `assethold#45` and the duplicate root `path_utils.py` in `assethold#46`.
- **Risk:** The targeted mypy tranche removes the current Windows blocker but also narrows an existing broader gate to two files for this tranche; the plan must stay explicit that this is a temporary unblock tradeoff and that broad cleanup / re-expansion remains under `assethold#31`.
- **Risk:** A later-stage unit/integration/coverage failure may appear once flake8/mypy no longer fail first; local CI-parity evidence already indicates unit coverage is below the current 80% threshold (`60.70%`), so execution must classify that honestly rather than claiming #2459 made the whole workflow green.
- **Open:** None inside the bounded implementation contract. The lint target list, PyYAML strategy, exclusion tracking, verifier enforcement requirement, and next-likely coverage blocker are now all explicit in the draft.
- **Approval gate note:** `.planning/plan-approved/2459.md` is intentionally absent during planning; it must be created only by the user after the issue is in `status:plan-review` and explicitly approved.

---

## Complexity: T2

**T2** — this is a standard multi-file CI hardening issue with one workflow file, a small number of bounded source/test changes, and clear follow-up boundaries for broader debt.