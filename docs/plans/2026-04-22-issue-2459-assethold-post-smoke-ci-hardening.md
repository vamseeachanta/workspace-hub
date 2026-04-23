# Plan for #2459: assethold post-smoke CI hardening

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2459
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2459-claude.md | scripts/review/results/2026-04-22-plan-2459-codex.md | scripts/review/results/2026-04-22-plan-2459-gemini.md
> **Parent issues:** #2442, #2448

---

## Resource Intelligence Summary

### Existing repo code
- Found: `assethold/.github/workflows/python-tests.yml` — current matrix workflow already clears checkout, dependency install, project install, and `Run smoke tests first` on all OSes after #2448, but still fails later at `Lint with flake8` on linux/macos and `Type checking with mypy` on windows.
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
- No current narrowing policy is documented for what #2459 should repair now versus split into follow-up issues later.

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
- `uv run --with flake8 python -m flake8 src/assethold tests/ --count --select=E9,F63,F7,F82 --show-source --statistics` (local, 2026-04-22) → currently reports only `src/assethold/modules/reporting/utils/path_utils.py:125:24: F821 undefined name 'os'`; this is the exact replacement lint gate the workflow will adopt.
- `gh run view 24792043821 --job 72551839963 --log-failed | grep -E "E999|F821" -n` (2026-04-22) → includes `./.agent-os/modules/prompt_enhancement.py:460:17: E999 SyntaxError: unterminated triple-quoted string literal`, `./scripts/agent-os/create-spec-enhanced.py:464:10: F821 undefined name 'validate'`, and `./src/assethold/modules/reporting/utils/path_utils.py:125:24: F821 undefined name 'os'`.
- `search_files` over `assethold/tests/` found watchlist tests but no existing tests for `path_utils`, confirming a missing targeted regression test for that helper.
- `pytest tests/unit/ --cov=src --cov=. --cov-report=term-missing --cov-fail-under=80 --junitxml=/tmp/assethold-pytest-unit.xml --verbose -m unit` (background run completed 2026-04-23) → FAIL after 604.32s with `Required test coverage of 80% not reached. Total coverage: 12.10%`; this proves the next exposed blocker after lint/mypy is expected to be the unit-coverage gate rather than a now-hypothetical future risk.

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

A bounded post-smoke CI contract patch that removes the current first post-smoke blockers by (1) scoping both flake8 commands to `src/assethold` plus `tests/`, (2) changing the workflow mypy gate to a targeted watchlist/path-utils tranche with explicit `types-PyYAML` installation and `--follow-imports=silent`, and (3) repairing those concrete source files plus tests so the matrix advances to the next real failure surface. Success for this tranche is: the workflow no longer stops first at linux/macos flake8 or windows repo-wide mypy, the next exposed blocker is explicitly recorded, and the plan honestly preserves that current evidence already predicts a later unit-coverage failure (`--cov-fail-under=80`) rather than immediate full-green CI.

---

## Pseudocode

```text
function harden_python_tests_workflow():
    keep smoke step first unchanged
    change both flake8 commands from repo-root to:
        src/assethold
        tests/
    leave any root auxiliary paths (.agent-os/, scripts/agent-os/, modules/) out of this tranche
    preserve smoke-before-lint ordering and preserve the single-line shell-neutral smoke command
    change mypy gate from repo-wide src/ to two explicit files:
        src/assethold/signals/watchlist.py
        src/assethold/modules/reporting/utils/path_utils.py
        with --follow-imports=silent
    install types-PyYAML in the workflow dependency step and use the same package for local targeted mypy verification
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
        reference assethold#31 for broad quality/type debt
        create an additional follow-up only if the newly exposed failure is not already covered
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `assethold/.github/workflows/python-tests.yml` | Change both flake8 commands from repo-root to the exact maintained tranche (`src/assethold` and `tests/`), add `types-PyYAML`, preserve smoke-before-lint / shell-neutral smoke invariants, and change mypy from repo-wide `src/` to the targeted two-file tranche for this issue using `--follow-imports=silent` to match the proven local red/green surface |
| Modify | `assethold/src/assethold/signals/watchlist.py` | Repair the concrete mypy blocker cluster already visible in CI and local repro |
| Modify | `assethold/src/assethold/modules/reporting/utils/path_utils.py` | Fix missing `os` import / type-check blocker |
| Create | `assethold/tests/unit/modules/reporting/utils/test_path_utils.py` | Add targeted regression coverage for the package path-utils helper |
| Modify | `assethold/tests/unit/signals/test_watchlist.py` | Extend existing watchlist coverage to lock in the typed/nullable behavior repaired in this issue |
| Create | `assethold/scripts/ci/verify_python_tests_workflow.py` | Add a persisted verifier for flake8 scope, smoke-before-lint ordering, and shell-neutral smoke command so workflow validation is not just an ad hoc inline snippet |
| Update | `docs/plans/README.md` | Add this plan to the canonical index |
| Reference (no edit in this tranche) | `assethold/modules/reporting/utils/path_utils.py` | Explicitly out of scope as a non-package duplicate once flake8 is narrowed to the maintained tranche; future cleanup remains tracked separately |
| Reference (existing future work) | `vamseeachanta/assethold#31` | Existing repo issue already tracks broad quality-gate / mypy debt beyond this bounded tranche |
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
| `verify_python_tests_workflow_contract` | persisted verifier script proves both flake8 commands target `src/assethold` + `tests/`, smoke remains before lint/mypy, and smoke command stays single-line/shell-neutral | `.github/workflows/python-tests.yml` | exit 0 from verifier script |

### TDD protocol for execution
- First extend `assethold/tests/unit/signals/test_watchlist.py`, create `assethold/tests/unit/modules/reporting/utils/test_path_utils.py`, and create `assethold/scripts/ci/verify_python_tests_workflow.py`.
- Mark the unit-test files with `pytestmark = pytest.mark.unit` so they execute under the existing CI `-m "unit"` filter.
- Before editing workflow/source files, run the narrowed static-analysis and persisted workflow-verifier commands expected after the workflow change and confirm they fail on current main:
  ```bash
  cd assethold && uv run --with types-PyYAML mypy \
    src/assethold/signals/watchlist.py \
    src/assethold/modules/reporting/utils/path_utils.py \
    --ignore-missing-imports \
    --follow-imports=silent

  cd assethold && uv run python scripts/ci/verify_python_tests_workflow.py
  ```
- Run the targeted pytest commands and confirm at least one new/extended assertion fails before changing workflow or source files:
  ```bash
  cd assethold && uv run python -m pytest tests/unit/signals/test_watchlist.py --noconftest -o addopts= -q
  cd assethold && uv run python -m pytest tests/unit/modules/reporting/utils/test_path_utils.py --noconftest -o addopts= -q
  ```
- Only then edit `assethold/.github/workflows/python-tests.yml`, `src/assethold/signals/watchlist.py`, and `src/assethold/modules/reporting/utils/path_utils.py`.
- Re-run the same targeted tests, then the targeted mypy command, then `uv run python scripts/ci/verify_python_tests_workflow.py`, then a CI run.

---

## Acceptance Criteria

- [ ] This plan is indexed in `docs/plans/README.md`.
- [ ] Adversarial review evidence is complete with 3 valid provider artifacts, and the summary table reflects the real verdicts / any invalid empty-artifact runs honestly.
- [ ] The workflow continues to pass `pytest tests/test_smoke.py --verbose --tb=short` before later gates.
- [ ] Both flake8 commands are changed from `.` to the exact maintained tranche: `src/assethold` and `tests/`.
- [ ] The workflow mypy gate is changed from `mypy src/ --ignore-missing-imports` to a targeted command covering only `src/assethold/signals/watchlist.py` and `src/assethold/modules/reporting/utils/path_utils.py` for this tranche, using `--follow-imports=silent` to match the proven local scope.
- [ ] `types-PyYAML` is added explicitly in the workflow dependency-install step and the same package is used in local targeted mypy verification.
- [ ] Local targeted validators pass using the repo’s canonical pytest invocation style with repo-wide addopts disabled for true red/green checks:
  ```bash
  cd assethold && uv run python -m pytest tests/unit/signals/test_watchlist.py --noconftest -o addopts= -q
  cd assethold && uv run python -m pytest tests/unit/modules/reporting/utils/test_path_utils.py --noconftest -o addopts= -q
  cd assethold && uv run python -m pytest tests/unit/ -m unit --noconftest -o addopts= -q
  cd assethold && uv run --with types-PyYAML mypy src/assethold/signals/watchlist.py src/assethold/modules/reporting/utils/path_utils.py --ignore-missing-imports --follow-imports=silent
  cd assethold && uv run python scripts/ci/verify_python_tests_workflow.py
  ```
- [ ] The targeted mypy command reports zero errors on the two repaired source files.
- [ ] A post-change CI run proves the workflow clears the current first post-smoke blockers and records the next exposed failure surface explicitly by run ID, job/step name, and either (a) a closeout note or (b) a linked follow-up issue if additional work remains.
- [ ] The execution/closeout notes explicitly distinguish blocker removal from full-green CI and preserve current evidence that the next likely gate after lint/mypy is unit coverage (`pytest tests/unit/ ... --cov-fail-under=80` currently fails at 12.10% total coverage on current main).
- [ ] Auxiliary broken Python outside the maintained tranche is explicitly tracked via `assethold#45`, the duplicate non-package `path_utils.py` is tracked via `assethold#46`, and broad repo-wide type debt remains tracked via `assethold#31`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR (latest valid artifact) | Required stronger CI success definition, alignment between local proof and CI behavior, explicit marker/coverage handling, and cleaner review-state framing |
| Codex | MAJOR (latest valid artifact) | Required verified evidence for issue-body / follow-up issue claims and a persisted workflow verifier instead of ad hoc inspection |
| Gemini | APPROVE (latest valid artifact) | Bounded scope and simpler `src/assethold` + `tests/` flake8 targeting are now acceptable; no further blocking findings in the latest Gemini pass |

**Current review state:** revision required; not approval-ready yet.

Revisions made based on review:
- aligned the issue body with the bounded blocker-removal tranche so the issue/plan target is no longer overstated
- fixed the core mypy contradiction by explicitly changing the planned workflow gate from repo-wide `src/` to a targeted two-file tranche using `--follow-imports=silent`, with broad debt anchored to `assethold#31`
- simplified flake8 targeting to `src/assethold` plus `tests/`, excluding only the already-split non-package auxiliary surfaces
- replaced brittle workflow-specific pytest-file ideas with a persisted workflow verifier script artifact (`assethold/scripts/ci/verify_python_tests_workflow.py`)
- made `types-PyYAML` explicit in both workflow dependency installation and local targeted mypy verification
- corrected the pytest command sequence to consistently use `uv run python -m pytest` with `-o addopts=` for isolated red/green checks
- embedded live issue evidence for assethold issues `#31`, `#45`, and `#46`
- added exact replacement-gate flake8 evidence for `python -m flake8 src/assethold tests/ ...`
- corrected the `path_utils.py` evidence citation to the in-scope package file
- tightened acceptance criteria around 3 valid provider artifacts, zero mypy errors on the targeted files, and explicit recording of the next exposed failure surface

---

## Risks and Open Questions

- **Risk:** Scoping flake8 to the maintained tranche may intentionally leave auxiliary root paths ungoverned; that is acceptable only because this plan explicitly tracks `.agent-os/` / `scripts/agent-os/` debt in `assethold#45` and the duplicate root `path_utils.py` in `assethold#46`.
- **Risk:** The targeted mypy tranche removes the current Windows blocker but does not solve repo-wide typing debt; the plan must stay explicit that broad cleanup remains under `assethold#31`.
- **Risk:** A later-stage unit/integration/coverage failure may appear once flake8/mypy no longer fail first; execution must classify that honestly rather than claiming #2459 made the whole workflow green.
- **Risk:** Current direct evidence already shows `pytest tests/unit/ --cov=src --cov=. --cov-fail-under=80 -m unit` failing at 12.10% total coverage on current main, so the likely next exposed blocker after the bounded lint/mypy tranche is the unit-coverage gate rather than a surprise regression.
- **Open:** None inside the bounded implementation contract. The lint target list, PyYAML strategy, exclusion tracking, and next-likely coverage blocker are now all explicit in the draft.
- **Approval gate note:** `.planning/plan-approved/2459.md` is intentionally absent during planning; it must be created only by the user after the issue is in `status:plan-review` and explicitly approved.

---

## Complexity: T2

**T2** — this is a standard multi-file CI hardening issue with one workflow file, a small number of bounded source/test changes, and clear follow-up boundaries for broader debt.