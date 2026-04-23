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

assethold/modules/reporting/utils/path_utils.py
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
- `gh run view 24792043821 --job 72551839963 --log-failed | grep -E "E999|F821" -n` (2026-04-22) → includes `./.agent-os/modules/prompt_enhancement.py:460:17: E999 SyntaxError: unterminated triple-quoted string literal`, `./scripts/agent-os/create-spec-enhanced.py:464:10: F821 undefined name 'validate'`, and `./src/assethold/modules/reporting/utils/path_utils.py:125:24: F821 undefined name 'os'`.
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
| New workflow-scope regression test | `assethold/tests/unit/workflows/test_python_tests_workflow_scope.py` |
| New workflow-order regression test | `assethold/tests/unit/workflows/test_python_tests_workflow_order.py` |
| Bounded source fixes | `assethold/src/assethold/signals/watchlist.py`, `assethold/src/assethold/modules/reporting/utils/path_utils.py` |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2459-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2459-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2459-gemini.md` |

---

## Deliverable

A bounded post-smoke CI contract patch that removes the current first post-smoke blockers by (1) scoping both flake8 commands to `src/assethold` plus the touched smoke/watchlist/path-utils tests, (2) changing the workflow mypy gate to a targeted watchlist/path-utils tranche with explicit `types-PyYAML` installation, and (3) repairing those concrete source files plus tests so the matrix can advance past the current lint/mypy failure points without claiming repo-wide type-debt cleanup.

---

## Pseudocode

```text
function harden_python_tests_workflow():
    keep smoke step first unchanged
    change both flake8 commands from repo-root to:
        src/assethold
        tests/test_smoke.py
        tests/unit/signals/test_watchlist.py
        tests/unit/modules/reporting/utils/test_path_utils.py
        tests/unit/workflows/test_python_tests_workflow_scope.py
        tests/unit/workflows/test_python_tests_workflow_order.py
    leave any root auxiliary paths (.agent-os/, scripts/agent-os/, modules/) out of this tranche
    preserve smoke-before-lint ordering and preserve the single-line shell-neutral smoke command
    change mypy gate from repo-wide src/ to two explicit files:
        src/assethold/signals/watchlist.py
        src/assethold/modules/reporting/utils/path_utils.py
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
| Modify | `assethold/.github/workflows/python-tests.yml` | Change both flake8 commands from repo-root to the exact maintained tranche (`src/assethold`, `tests/test_smoke.py`, `tests/unit/signals/test_watchlist.py`, `tests/unit/modules/reporting/utils/test_path_utils.py`, `tests/unit/workflows/test_python_tests_workflow_scope.py`, `tests/unit/workflows/test_python_tests_workflow_order.py`), add `types-PyYAML`, preserve smoke-before-lint / shell-neutral smoke invariants, and change mypy from repo-wide `src/` to the targeted two-file tranche for this issue |
| Modify | `assethold/src/assethold/signals/watchlist.py` | Repair the concrete mypy blocker cluster already visible in CI and local repro |
| Modify | `assethold/src/assethold/modules/reporting/utils/path_utils.py` | Fix missing `os` import / type-check blocker |
| Create | `assethold/tests/unit/modules/reporting/utils/test_path_utils.py` | Add targeted regression coverage for the package path-utils helper |
| Modify | `assethold/tests/unit/signals/test_watchlist.py` | Extend existing watchlist coverage to lock in the typed/nullable behavior repaired in this issue |
| Create | `assethold/tests/unit/workflows/test_python_tests_workflow_scope.py` | Add an executable red→green test for the workflow scope changes rather than relying on prose |
| Create | `assethold/tests/unit/workflows/test_python_tests_workflow_order.py` | Add an executable guard that smoke stays before lint/mypy and remains shell-neutral |
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
| `test_python_tests_workflow_scope_targets_exact_maintained_tranche` | workflow YAML encodes the exact flake8/mypy target paths agreed in this plan | parsed workflow YAML | exact maintained-tranche path list present |

### TDD protocol for execution
- First write/extend `assethold/tests/unit/workflows/test_python_tests_workflow_scope.py`, `assethold/tests/unit/signals/test_watchlist.py`, and `assethold/tests/unit/modules/reporting/utils/test_path_utils.py`.
- Before editing workflow/source files, run the narrowed static-analysis commands expected after the workflow change and confirm they fail on current main:
  - `cd assethold && uv run mypy src/assethold/signals/watchlist.py src/assethold/modules/reporting/utils/path_utils.py --ignore-missing-imports`
  - `cd assethold && uv run python -m pytest tests/unit/workflows/test_python_tests_workflow_scope.py --noconftest -q`
- Run the targeted pytest commands and confirm at least one new/extended assertion fails before changing workflow or source files.
- Only then edit `assethold/.github/workflows/python-tests.yml`, `src/assethold/signals/watchlist.py`, and `src/assethold/modules/reporting/utils/path_utils.py`.
- Re-run the same targeted tests, then the targeted mypy command, then CI.

---

## Acceptance Criteria

- [ ] This plan is indexed in `docs/plans/README.md`.
- [ ] Adversarial review evidence is complete with at least 2 valid provider artifacts, and the summary table reflects the real verdicts / any invalid empty-artifact runs honestly.
- [ ] The workflow continues to pass `pytest tests/test_smoke.py --verbose --tb=short` before later gates.
- [ ] Both flake8 commands are changed from `.` to the exact maintained tranche: `src/assethold`, `tests/test_smoke.py`, `tests/unit/signals/test_watchlist.py`, and `tests/unit/modules/reporting/utils/test_path_utils.py`.
- [ ] The workflow mypy gate is changed from `mypy src/ --ignore-missing-imports` to a targeted command covering only `src/assethold/signals/watchlist.py` and `src/assethold/modules/reporting/utils/path_utils.py` for this tranche.
- [ ] `types-PyYAML` is added explicitly in the workflow dependency-install step so the targeted mypy command is reproducible.
- [ ] Local targeted validators pass using the repo’s canonical pytest invocation style:
  - `cd assethold && uv run python -m pytest tests/unit/signals/test_watchlist.py --noconftest -q`
  - `cd assethold && uv run python -m pytest tests/unit/modules/reporting/utils/test_path_utils.py --noconftest -q`
  - `cd assethold && uv run python -m pytest tests/unit/workflows/test_python_tests_workflow_scope.py --noconftest -q`
  - `cd assethold && uv run mypy src/assethold/signals/watchlist.py src/assethold/modules/reporting/utils/path_utils.py --ignore-missing-imports`
- [ ] The targeted mypy command reports zero errors on the two repaired source files.
- [ ] The post-change CI run shows the matrix advancing past the current first post-smoke blockers (linux/macos no longer stop at repo-root flake8; windows no longer stop at repo-wide mypy on the watchlist/path-utils tranche).
- [ ] Auxiliary broken Python outside the maintained tranche is explicitly tracked via `assethold#45`, and broad repo-wide type debt remains tracked via `assethold#31`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR (latest valid artifact) | Required stronger CI success definition, explicit handling of coverage/next-stage residual-red risk, exact test marker / lint-tranche coverage, and clearer evidence for excluded follow-up items |
| Codex | INVALID (empty artifact) | Latest rerun left `scripts/review/results/2026-04-22-plan-2459-codex.md` empty; this does not count as a completed review |
| Gemini | MAJOR (latest valid artifact) | Required honest review bookkeeping, stronger closure target relative to issue #2459 wording, and consistent `uv run python -m pytest` commands |

**Overall result:** FAIL (re-draft required before `status:plan-review`)

Revisions made based on review:
- fixed the core mypy contradiction by explicitly changing the planned workflow gate from repo-wide `src/` to a targeted two-file tranche, with broad debt anchored to `assethold#31`
- defined the exact maintained flake8 tranche, applied it to both flake8 commands, and added a concrete workflow-scope regression test artifact path
- made `types-PyYAML` explicit in the workflow dependency-install step
- added a real red-phase for the narrowed static-analysis commands before workflow/source edits
- corrected the pytest command sequence to consistently use `uv run python -m pytest`
- created/linked `assethold#45` and `assethold#46` so excluded auxiliary `.agent-os/` / `scripts/agent-os/` debt and the duplicate non-package `path_utils.py` are explicitly tracked
- tightened acceptance criteria around honest review-artifact state, zero mypy errors on the targeted files, canonical pytest invocation, and future-issue linkage

---

## Risks and Open Questions

- **Risk:** Scoping flake8 to the maintained tranche may intentionally leave auxiliary root paths ungoverned; that is acceptable only because this plan explicitly tracks `.agent-os/` / `scripts/agent-os/` debt in `assethold#45` and the duplicate root `path_utils.py` in `assethold#46`.
- **Risk:** The targeted mypy tranche removes the current Windows blocker but does not solve repo-wide typing debt; the plan must stay explicit that broad cleanup remains under `assethold#31`.
- **Risk:** A later-stage unit/integration/coverage failure may appear once flake8/mypy no longer fail first; execution must classify that honestly rather than claiming #2459 made the whole workflow green.
- **Open:** None inside the bounded implementation contract. The lint target list, PyYAML strategy, and exclusion tracking are fixed by this plan revision.
- **Approval gate note:** `.planning/plan-approved/2459.md` is intentionally absent during planning; it must be created only by the user after the issue is in `status:plan-review` and explicitly approved.

---

## Complexity: T2

**T2** — this is a standard multi-file CI hardening issue with one workflow file, a small number of bounded source/test changes, and clear follow-up boundaries for broader debt.