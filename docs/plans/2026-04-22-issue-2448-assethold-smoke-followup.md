# Plan for #2448: assethold python-tests smoke still blocked after #2442 P1/P2 — flake8 gates before smoke, Windows checkout path invalid

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2448
> **Parent / predecessor:** #2442 (P1 commit `457ea2d`, P2 commit `b8b5439` — landed on `vamseeachanta/assethold` main)
> **Review artifacts:** `scripts/review/results/20260422T101242Z-2026-04-22-issue-2448-assethold-smoke-followup.md-plan-claude.md` | `...-codex.md` | `...-gemini.md`
> **Note:** This is a **follow-up plan**. Implementation is NOT authorized by this draft. User must review and set `status:plan-approved` in-thread after adversarial review converges. No `status:plan-approved` label is set by this plan.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `assethold/.github/workflows/python-tests.yml` (393 lines) — at HEAD `b8b5439`. Step order in `test` job (lines 55-107): `Checkout code` → `Clone assetutilities sibling dependency` → `Set up Python` → `Install uv` → `Install dependencies with uv` → `Install project in development mode` → `Lint with flake8` (line 84-89) → `Type checking with mypy` → `Security check with bandit` → `Safety check` → **`Run smoke tests first`** (line 103-107). The "first" in the smoke-step name is a misnomer — it runs 4 steps after lint.
- Found: `assethold/.github/workflows/python-tests.yml:43-47` — matrix strategy already sets `fail-fast: false`, so a failure in another matrix leg will not cancel the target `py3.11 / ubuntu-latest` leg before smoke evidence can be collected. No extra fail-fast change is needed for #2448.
- Found: `assethold/.github/workflows/python-tests.yml:84-89` — `Lint with flake8` step runs under default shell `/bin/bash -e`, so the strict flake8 pass at line 87 (`flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`) aborts the job on first syntax / undefined-name hit.
- Found: `assethold/tests/test_smoke.py` — 11,615 bytes, exists, passes locally at `uv run pytest tests/test_smoke.py -v` per #2442 P2 attestation (17 passed).
- Found: `assethold/pyproject.toml:139-140` — `[tool.pytest.ini_options] testpaths = ["tests"]`. Product-code test scope is `tests/` only; `flake8 .` is broader than pytest's authoritative scope.
- Found: `assethold/.agent-os/`, `assethold/modules/`, `assethold/scripts/` — top-level tooling paths that are **not** part of the importable `src/assethold/` package and **not** under `tests/`. These hold the flake8 offenders (see Evidence).
- Gap: no existing follow-on remediation — #2448 currently has zero labels and zero prior plan. This plan is the canonical artifact.

### Standards
Not applicable — infrastructure/CI-health follow-up, not a domain engineering deliverable.

### LLM Wiki pages consulted
No relevant wiki pages — git-tree hygiene + workflow step ordering is repo hygiene, not domain knowledge.

### Documents consulted
- Issue #2448 body — drafted at split-off 2026-04-22; explicitly names both failure modes (flake8 gates before smoke; Windows `invalid path`) and suggests acceptance-criterion tradeoffs (bypass vs fix).
- Predecessor issue #2442 — all 6 review waves + execution attestations for `457ea2d` (P1) and `b8b5439` (P2). P2-comment confirms run `24756978995` is the failure snapshot this plan targets.
- `docs/plans/2026-04-21-issue-2442-assethold-python-tests.md` — the #2442 plan; this plan inherits its scope-bound discipline (direct-to-main on assethold per repo convention; phased commits; one smoke cell as close criterion).
- `gh run view 24756978995 --repo vamseeachanta/assethold --log-failed` — live fetch 2026-04-22 capturing the actual failure output on both Windows checkout (exit 128, `invalid path`) and macOS flake8 (`E999 SyntaxError` at `./.agent-os/modules/prompt_enhancement.py:460`, `F821 undefined name 'os'` at `./modules/reporting/utils/path_utils.py:125`, multiple `F821` at `./scripts/agent-os/create-spec-enhanced.py:464-478`). Same failure class hits py3.11 / ubuntu-latest.
- `git ls-tree -r HEAD` on `/mnt/local-analysis/workspace-hub/assethold` @ `b8b5439` — two pathological tree entries confirmed containing literal backslashes in filenames (same blob SHAs as the canonical forward-slash paths).

### Gaps identified
- No process preventing backslash-containing paths from entering the tree — recurrence risk after this cleanup. Out of scope for this plan; file follow-on for a `.gitattributes` / pre-commit rule if the user wants a durable guard.
- No dedicated smoke-only fast-path workflow. Not proposed; the existing `test` job with a step-reorder meets the close criterion at lower blast radius than a new workflow.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view --json state,labels`):
- `#2448` — OPEN — title "follow-up(ci): assethold python-tests smoke still blocked after #2442 P1/P2 — flake8 gates before smoke, Windows checkout path invalid" — labels: **none** (plan draft will post comment; no `status:plan-approved` label until user approves)
- `#2442` — OPEN — predecessor, P1/P2 landed on main, close criterion still unmet (see predecessor plan)

**File existence** (`ls -la` / `git ls-tree` 2026-04-22 on `/mnt/local-analysis/workspace-hub/assethold` @ `b8b5439`):
- EXISTS: `.github/workflows/python-tests.yml` (393 lines at HEAD)
- EXISTS: `tests/test_smoke.py` (11,615 bytes)
- EXISTS: `tests/modules/stocks/analysis/investment/results/Data/multiple_investment.csv` (forward-slash path, 320 bytes, blob `ff919799bf86d6b7838ad80c0b57106bb2cc2537`)
- EXISTS: `tests/modules/stocks/analysis/investment/results/Data/single_investment.csv` (forward-slash path, blob `a5f160b213349a514a847906d880f5a1ea4a5f86`)
- EXISTS (pathological, same blob SHA as above): filename literally `tests\modules\stocks\analysis\investment\results\Data\multiple_investment.csv` (single 92-char filename containing `\`)
- EXISTS (pathological, same blob SHA as above): filename literally `tests\modules\stocks\analysis\investment\results\Data\single_investment.csv`

**Backslash-name proof** (`git ls-tree -r HEAD -z | tr '\0' '\n' | awk -F'\t' '$2 ~ /\\\\/ {print $2}'`):
```
tests\modules\stocks\analysis\investment\results\Data\multiple_investment.csv
tests\modules\stocks\analysis\investment\results\Data\single_investment.csv
```
Exactly 2 matches. Both are duplicates of forward-slash paths at byte-identical blobs (same SHA). No other backslash-containing paths in the tree.

**Windows failure excerpt** (run `24756978995` — `Test on Python 3.11 (windows-latest) / Checkout code`):
```
[command]"C:\Program Files\Git\bin\git.exe" checkout --progress --force -B main refs/remotes/origin/main
##[error]error: invalid path 'tests\modules\stocks\analysis\investment\results\Data\multiple_investment.csv'
##[error]The process 'C:\Program Files\Git\bin\git.exe' failed with exit code 128
```
Confirms: Windows `git` aborts before any workflow step runs. Root cause is `core.protectNTFS` safety refusing to materialize a filename containing `\` (because NTFS treats `\` as a path separator). This is deterministic — every Windows cell will fail here until the pathological entries are purged from the tree.

**flake8-before-smoke proof** (`sed -n '84,107p' .github/workflows/python-tests.yml`):
```
84:    - name: Lint with flake8
85:      run: |
86:        # Stop the build if there are Python syntax errors or undefined names
87:        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
88:        # Exit-zero treats all errors as warnings
89:        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
...
103:    - name: Run smoke tests first
104:      run: |
105:        pytest tests/test_smoke.py \
106:          --verbose \
107:          --tb=short
```
flake8 is 19 lines earlier than the "smoke tests first" step. With `set -e` behavior, a line-87 failure exits the job.

**flake8 offenders excerpt** (run `24756978995`, macos-latest py3.12 log — same failures on ubuntu py3.11):
```
./.agent-os/modules/prompt_enhancement.py:460:17: E999 SyntaxError: unterminated triple-quoted string literal (detected at line 494)
./modules/reporting/utils/path_utils.py:125:24: F821 undefined name 'os'
./scripts/agent-os/create-spec-enhanced.py:464:10: F821 undefined name 'validate'
./scripts/agent-os/create-spec-enhanced.py:465:10: F821 undefined name 'sanitize'
./scripts/agent-os/create-spec-enhanced.py:466:10: F821 undefined name 'parse'
./scripts/agent-os/create-spec-enhanced.py:470:10: F821 undefined name 'execute'
./scripts/agent-os/create-spec-enhanced.py:471:10: F821 undefined name 'transform'
```
All offenders are in `.agent-os/`, `modules/`, `scripts/` — **outside** `src/` (importable package) and `tests/` (pytest scope). No real product code is broken; the `F821` hits are pseudo-code templates (`+validate()`, `+sanitize()`) in a spec-generator script.

**Gap proof** (scope comparison):
- `grep -n testpaths assethold/pyproject.toml` → `139: [tool.pytest.ini_options]\n140: testpaths = ["tests"]` — authoritative test-scope is `tests/`.
- `grep -n 'flake8 \.' .github/workflows/python-tests.yml` → lines 87, 89 — lint scope is the repo root, broader than pytest scope.

<!-- Source count: issue body (#2448) + predecessor issue (#2442) + predecessor plan + live `gh run view` log + live `git ls-tree` verification + workflow file read + `pyproject.toml` read = 7 distinct sources. Minimum ≥3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2448-assethold-smoke-followup.md` |
| Primary workflow to edit | `assethold/.github/workflows/python-tests.yml` |
| Tree cleanup targets (delete) | `assethold/'tests\modules\stocks\analysis\investment\results\Data\multiple_investment.csv'` and `...\single_investment.csv` (pathological filenames with literal backslashes) |
| Predecessor plan | `docs/plans/2026-04-21-issue-2442-assethold-python-tests.md` |
| Plan review — Claude | `scripts/review/results/20260422T101242Z-2026-04-22-issue-2448-assethold-smoke-followup.md-plan-claude.md` |
| Plan review — Codex | `scripts/review/results/20260422T101242Z-2026-04-22-issue-2448-assethold-smoke-followup.md-plan-codex.md` |
| Plan review — Gemini | `scripts/review/results/20260422T101242Z-2026-04-22-issue-2448-assethold-smoke-followup.md-plan-gemini.md` |

---

## Deliverable

**Issue-close criterion (same gate shape as #2442):** a single post-P2 `python-tests.yml` run on `vamseeachanta/assethold` main proves BOTH on the same final repository state:
1. at least one matrix cell (py3.11 / ubuntu-latest, `test` job) reaches `Run smoke tests first` with smoke-step `conclusion=success`; AND
2. every Windows cell reaches `Install dependencies with uv` without any `invalid path` checkout failure.

P1 remains an intermediate gate to prove the git-tree defect is removed, but the formal close criterion is evaluated only on the final post-P2 head commit, not by combining evidence from separate P1 and P2 runs.

Flake8 repair (fixing the `.agent-os/` / `modules/` / `scripts/` offenders) and full `quality-gate` chain green are **out of scope** — file follow-on issues when the smoke baseline is established.

Two scoped commits: P1 (git-tree backslash purge) + P2 (workflow step reorder).

---

## Pseudocode

```
# PHASE 1 — Purge pathological backslash-named tree entries (Windows unblock)

# Verified state: exactly 2 entries in `git ls-tree -r HEAD` contain `\` in the filename,
# both duplicate real forward-slash paths at byte-identical blob SHAs.
# Fix is a single commit on assethold main that removes these 2 paths.

on assethold main worktree:
    for each of {'tests\modules\stocks\analysis\investment\results\Data\multiple_investment.csv',
                  'tests\modules\stocks\analysis\investment\results\Data\single_investment.csv'}:
        # Use single-quotes in shell to keep `\` literal.
        # Preferred: remove the tree entry and filesystem file together.
        if test -f '<literal backslash path>' ; then
            git rm -- '<literal backslash path>'
        else
            # Fallback if the pathological path is index-only in the local checkout.
            git rm --cached -- '<literal backslash path>'
        fi
    git commit -m "fix(ci): remove backslash-duplicate tree entries blocking Windows checkout (#2448)"
    git push origin main

# ACCEPTANCE-PHASE-1:
#   Local: `git ls-tree -r HEAD | awk '{print $4}' | grep -c '\\\\'` == 0
#   CI (next push): every Windows cell reaches `Install dependencies with uv`
#     (not merely checkout success), and no run log contains `invalid path`.
#     Intermediate steps `Clone assetutilities sibling dependency`, `Set up Python`,
#     and `Install uv` must therefore also be passing.

# PHASE 2 — Reorder smoke step to run before flake8 (Linux/macOS smoke unblock)

# Minimum-change fix: move the `Run smoke tests first` step block so it runs
# immediately after `Install project in development mode` (current line 82)
# and BEFORE `Lint with flake8` (current line 84).
# No change to flake8 args, scope, or shell; lint remains configured as-is.
# Real flake8 offenders in `.agent-os/`, `modules/`, `scripts/` will still
# fail the lint step downstream — that is tracked as follow-on, not this plan.

in assethold/.github/workflows/python-tests.yml:
    current order:
        - Install project in development mode        # line 81-82
        - Lint with flake8                           # line 84-89   <- currently fails here
        - Type checking with mypy                    # line 91-93
        - Security check with bandit                 # line 95-97
        - Safety check for vulnerabilities           # line 99-101
        - Run smoke tests first                      # line 103-107 <- never reached
        - Run unit tests with coverage               # ...
        - Run all tests with coverage                # ...

    new order (move one block up):
        - Install project in development mode
        - Run smoke tests first                      # moved — now runs before lint
        - Lint with flake8                           # unchanged args/scope
        - Type checking with mypy
        - Security check with bandit
        - Safety check for vulnerabilities
        - Run unit tests with coverage
        - Run all tests with coverage

# Rationale for reorder over lint-scope-narrowing:
#   - Smaller diff (one YAML block moved, no argument changes)
#   - Does not silently tolerate real errors in tooling paths
#   - Matches the #2448 issue-suggested "bypass lint/type/security for first-green path"
#   - Leaves flake8 red — forces a follow-on to either fix offenders or narrow scope

# PHASE GATE ENFORCEMENT:
# P1 and P2 MUST be two separate commits on assethold main, pushed sequentially.
# Direct-to-main per assethold repo convention (same as #2442 execution).
# Executor sequence:
#   1. Commit P1 (tree purge). Push. Wait for CI.
#   2. Verify on the P1 run: every Windows cell reaches `Install dependencies with uv`
#      and no run log contains `invalid path`.
#   3. Only after P1 CI verification: commit P2 (step reorder). Push. Wait for CI.
#   4. Verify on the single post-P2 run for the final head commit:
#      - every Windows cell still reaches `Install dependencies with uv`
#      - py3.11 / ubuntu-latest `Run smoke tests first` has `conclusion=success`
# If P1 CI fails unexpectedly (e.g., reveals a second backslash path we missed):
#   investigate before P2 commit; extend P1 to cover the new entry.
# If P2 CI fails on the smoke step itself (not lint): file a follow-on — that's product test-debt.

# ACCEPTANCE-PHASE-2:
#   CI: py3.11 / ubuntu-latest `Run smoke tests first` step conclusion=success
#   on the same final run that also proves the Windows path is fixed.
#   Job may still be red downstream at `Lint with flake8` — that is expected
#   and tracked as follow-on.

# Combined close gate for #2448: one post-P2 main-branch run proves both conditions together.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Delete (P1) | `assethold/'tests\modules\stocks\analysis\investment\results\Data\multiple_investment.csv'` | Pathological tree entry with literal `\` in filename; duplicate of the forward-slash path at same blob SHA (`ff919799`). Blocks Windows checkout via `core.protectNTFS`. |
| Delete (P1) | `assethold/'tests\modules\stocks\analysis\investment\results\Data\single_investment.csv'` | Same defect; blob SHA `a5f160b2` duplicates the forward-slash file. |
| Modify (P2) | `assethold/.github/workflows/python-tests.yml` | Move `Run smoke tests first` step (currently lines 103-109) to run between `Install project in development mode` (line 82) and `Lint with flake8` (line 84). No changes to step arguments, env, or other jobs. |

**Out-of-scope for this plan** (deferred to follow-on issues, file when P1/P2 land):
- Fix real flake8 offenders: add `import os` in `modules/reporting/utils/path_utils.py`, repair or delete `.agent-os/modules/prompt_enhancement.py` (E999 unterminated string) and `scripts/agent-os/create-spec-enhanced.py` (F821 pseudo-code placeholders). Or alternatively narrow `flake8 . → flake8 src/ tests/`.
- Full `quality-gate` chain green (depends on lint fix + integration-tests + financial-data-tests).
- `.gitattributes` / pre-commit rule to prevent future backslash paths entering the tree.
- `docs.yml` (still orphaned; predecessor plan's P3).
- workspace-hub-side: update `docs/plans/README.md` index row for #2448. Deliberately skipped in this planning session to avoid cross-branch contention per orchestrator instructions; will land in a follow-on commit after plan approval.

---

## TDD Test List

Since this plan remediates CI config + git-tree hygiene (not application code), "tests" are **tree + workflow-state assertions** run via `git ls-tree`, `uv run ... python`, and `gh run view`.

| Test | What it verifies | Expected state after fix |
|---|---|---|
| P1-local-path-count-precheck | `cd assethold && uv run --no-project python - <<'PY'
from pathlib import Path
import subprocess
paths = subprocess.check_output(['git','ls-tree','-r','HEAD','--name-only'], text=True).splitlines()
print(sum('\\' in p for p in paths))
PY` | `2` before P1; catches any surprise extra backslash path before deletion |
| P1-local-index-clean | `cd assethold && uv run --no-project python - <<'PY'
import subprocess, sys
paths = subprocess.check_output(['git','ls-files'], text=True).splitlines()
count = sum('\\' in p for p in paths)
print(count)
sys.exit(0 if count == 0 else 1)
PY` | `0` after P1 staging/commit |
| P1-local-tree-clean | `cd assethold && uv run --no-project python - <<'PY'
import subprocess, sys
paths = subprocess.check_output(['git','ls-tree','-r','HEAD','--name-only'], text=True).splitlines()
count = sum('\\' in p for p in paths)
print(count)
sys.exit(0 if count == 0 else 1)
PY` | `0` after P1 lands |
| P1-local-forward-slash-blobs-intact | `cd assethold && git rev-parse HEAD:tests/modules/stocks/analysis/investment/results/Data/multiple_investment.csv && git rev-parse HEAD:tests/modules/stocks/analysis/investment/results/Data/single_investment.csv` | `ff919799...` and `a5f160b2...` remain present after P1 |
| P1-local-no-literal-consumers | `cd assethold && grep -rI 'tests\\\\modules\\\\stocks' src tests scripts .agent-os modules` | zero hits before P1 commit |
| P1-ci-windows-reaches-install-deps | `gh run view <p1-run-id> --repo vamseeachanta/assethold --json jobs` — each Windows matrix cell step list | every windows-latest row reaches `Install dependencies with uv` |
| P1-ci-no-windows-invalid-path | job-scoped Windows checkout logs from `gh run view <p1-run-id> --json jobs` / `gh run view --job <job-id> --log` | zero `##[error]error: invalid path` hits in every Windows `Checkout code` step |
| P2-local-step-order-precheck | `uv run --no-project --with pyyaml python - <<'PY' ... PY` parses current workflow and asserts `Run smoke tests first` index > `Lint with flake8` index before editing | pre-edit order proven wrong |
| P2-local-step-order | `uv run --no-project --with pyyaml python - <<'PY' ... PY` parses edited workflow and asserts `Run smoke tests first` index < `Lint with flake8` index | smoke index < lint index |
| P2-local-yaml-parses | `uv run --no-project --with pyyaml python -c "import yaml; yaml.safe_load(open('.github/workflows/python-tests.yml'))"` | exit 0 |
| P2-ci-step-order-proof | `gh run view <p2-run-id> --repo vamseeachanta/assethold --json jobs` — locate the `Test on Python 3.11 (ubuntu-latest)` job and assert step order in its step array places `Run smoke tests first` before `Lint with flake8` | job-scoped step order correct |
| P2-ci-smoke-step-green | same job-scoped JSON query on `Test on Python 3.11 (ubuntu-latest)` | `Run smoke tests first` step `conclusion=success` |
| combined-close-gate | The single post-P2 run on final `main` head shows both: Windows reaches `Install dependencies with uv` and py3.11/ubuntu-latest smoke succeeds | both true on same run |

Pre-push local gates:
- Before P1 commit: `git ls-tree -r HEAD | awk '{print $4}' | grep -c '\\\\'` returns `2` (the entries we're about to delete); after `git rm` + add, `git ls-files | grep -c '\\\\'` returns `0`.
- Before P2 commit: local YAML parse exit 0, Python-based step-order check passes, `uv run pytest tests/test_smoke.py -v` still green (same baseline as #2442 P2).
- If the P1 CI run fails in `Clone assetutilities sibling dependency`, `Set up Python`, or `Install uv` for transient/non-path reasons, rerun or classify it as non-P1 noise rather than treating the backslash-path purge itself as failed.

---

## Acceptance Criteria

- [ ] Two pathological backslash-named tree entries removed from `vamseeachanta/assethold` main at `tests\modules\stocks\analysis\investment\results\Data\{multiple,single}_investment.csv` (P1 commit on main)
- [ ] Zero backslash-containing paths remain in `git ls-tree -r HEAD` on assethold main after P1
- [ ] Forward-slash equivalents (`tests/modules/stocks/analysis/investment/results/Data/{multiple,single}_investment.csv`) remain untouched — same blob SHAs as before (`ff919799`, `a5f160b2`)
- [ ] P1 CI run: every `windows-latest` matrix cell reaches `Install dependencies with uv`; no `invalid path` string in the run log
- [ ] `python-tests.yml` step order in the `test` job is proven wrong before editing, then proven corrected after editing: `Install project in development mode` → `Run smoke tests first` → `Lint with flake8` (smoke before lint) (P2 commit on main)
- [ ] P2 commit preserves all existing step arguments, env blocks, and downstream jobs — diff is scope-limited to moving one step block
- [ ] Single post-P2 CI run on the final `main` head proves BOTH: all `windows-latest` cells reach `Install dependencies with uv` AND py3.11/ubuntu-latest `Run smoke tests first` has `conclusion=success`
- [ ] P1 and P2 are **separate commits** pushed sequentially with CI verification between (not bundled)
- [ ] Local smoke still green after P2: `cd assethold && uv run pytest tests/test_smoke.py -v` passes (same 17 baseline as #2442 P2)
- [ ] Review artifacts posted to `scripts/review/results/20260422T103138Z-2026-04-22-issue-2448-assethold-smoke-followup.md-plan-{claude,codex,gemini}.md`
- [ ] No changes pushed to `assethold/` during this planning session — fixes land only after user sets `status:plan-approved` on #2448 after reviewing this plan and adversarial review
- [ ] Flake8 job may remain red in the P2 run (expected) — close criterion is the **smoke step** plus Windows-progress proof on the final run, not full test-job greenness; follow-on issues filed for flake8 offender repair and `quality-gate` chain
- [ ] #2442 is **not** auto-closed as a side effect of #2448. If the final run satisfies the historical #2442 gate too, that is surfaced back to the user as a separate closeout decision in #2442 for audit-trail clarity

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE | Tight scope and correct diagnosis; suggested safer `git rm --cached` fallback, log-order proof instead of step timestamps, and explicit non-auto-close wording for #2442. |
| Codex | MAJOR | Required the final close gate to be proven on a single post-P2 run, not split across P1/P2; required Windows verification to reach `Install dependencies with uv`, not just checkout; flagged `yq` tooling assumption. |
| Gemini | APPROVE | No blocking defects; suggested optional wider Windows-workflow audit and recurrence-source question. |

**Wave 3 overall result:** MAJOR — remaining review concerns are now confined to verification-contract precision rather than diagnosis or scope. This revision hardens the final plan by (1) replacing shell-escape-sensitive backslash-detection commands with Python-based byte-level checks, (2) recording that matrix `fail-fast: false` is already set so the target ubuntu smoke leg remains provable, (3) updating review-artifact references to the latest concrete rerun set, and (4) promoting preservation/consumer checks into the gated TDD contract.

Revisions made based on review:
- Added resource-intel evidence that the test matrix already uses `fail-fast: false`.
- Replaced shell-escape-fragile path-detection commands with Python-based checks for single backslashes in tracked paths.
- Updated the review-artifact references to the latest rerun files.
- Promoted forward-slash blob preservation and literal-consumer grep checks into the TDD/acceptance gate set.
- Preserved the single-run post-P2 close gate and job-scoped CI verification shape.

The plan remains in `draft` pending the latest rerun review wave.

---

## Risks and Open Questions

- **Risk — git-tree surgery on main (P1):** Deleting tree entries on `main` is a direct-to-main rewrite of the index (not history-rewriting; no force-push). Duplicate blob content means the removed data is still accessible via the canonical forward-slash paths. Low-risk, but verify no code path hard-references the backslash names (`grep -rI 'tests\\\\modules\\\\stocks' assethold/src assethold/tests` at plan-approved time; expected: zero hits — these were Windows-user artifacts never intended to be imported).
- **Risk — second pathological path emerges after P1:** If additional backslash entries exist that weren't visible in `git ls-tree -r HEAD -z | awk '$2 ~ /\\\\/'` (evidence shows only 2, but theoretically a sparse history could hide more), Windows checkout may still fail after P1 on a different filename. **Mitigation:** verification step after P1 CI — if Windows checkout still fails on a *different* path, extend P1 rather than proceeding to P2; do not bundle.
- **Risk — recurrence:** Nothing in the current tooling prevents a Windows user from re-adding backslash-named files. **Mitigation:** file follow-on hygiene issue proposing a `.gitattributes` entry + pre-commit hook checking `git diff --cached --name-only | grep '\\\\'`. Not in scope for this plan.
- **Risk — P2 step reorder reveals smoke-test flakes on hosted runners:** Local smoke is green (#2442 attestation: 17 passed), but hosted runners may expose env / path / network flakes. **Mitigation:** if py3.11 / ubuntu-latest smoke is red on CI but green locally, file a follow-on for test-environment debt; do not revert P2 (the reorder itself is correct regardless of smoke content).
- **Risk — flake8 remaining red blocks `quality-gate` chain perpetually:** Per #2442 predecessor plan, `quality-gate` needs `test` + `integration-tests` + `financial-data-tests` all green; `test` won't be fully green until flake8 is fixed or narrowed. **Mitigation:** explicitly out-of-scope for #2448 close; acceptance criterion is smoke-step green, not full job green. Follow-on needed for flake8 repair.
- **Risk — label-drift from prior sessions:** #2448 currently has zero labels (verified 2026-04-22). No `status:plan-approved` label is being applied by this plan; user must apply after in-thread review. **Mitigation:** acceptance criterion explicitly requires this.
- **Open — flake8 fix strategy when it's eventually tackled (follow-on):** Narrow scope (`flake8 src/ tests/`) vs repair offenders (add `import os` in `path_utils.py`, delete or fix the `.agent-os/`/`scripts/` pseudo-code templates) vs both. **Flag for user decision when follow-on is filed.**
- **Open — should #2442 auto-close when #2448 P2 lands green?** The #2442 close criterion was "one smoke cell green on main." That gate is satisfied by #2448 P2 + P1. **Flag for user decision at P2 attestation time.**

---

## Complexity: T2

**T2** — two scoped commits on assethold main with distinct CI gates between them. P1 is mechanically deterministic (two file deletions with pre-verified blob-duplicate evidence). P2 is a one-block YAML step move with no argument changes. Not T3 because no architectural decisions, no new jobs, no cross-repo workflow changes. Not T1 because it spans two phases with independent failure modes (Windows NTFS vs Linux step-order) and requires sequential CI verification between phases.
