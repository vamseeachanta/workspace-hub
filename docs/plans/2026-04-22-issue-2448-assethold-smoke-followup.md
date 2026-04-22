# Plan for #2448: assethold python-tests smoke still blocked after #2442 P1/P2 — flake8 gates before smoke, Windows checkout path invalid

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2448
> **Parent / predecessor:** #2442 (P1 commit `457ea2d`, P2 commit `b8b5439` — landed on `vamseeachanta/assethold` main)
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2448-claude.md | ...-codex.md | ...-gemini.md
> **Note:** This is a **follow-up plan**. Implementation is NOT authorized by this draft. User must review and set `status:plan-approved` in-thread after adversarial review converges. No `status:plan-approved` label is set by this plan.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `assethold/.github/workflows/python-tests.yml` (393 lines) — at HEAD `b8b5439`. Step order in `test` job (lines 55-107): `Checkout code` → `Clone assetutilities sibling dependency` → `Set up Python` → `Install uv` → `Install dependencies with uv` → `Install project in development mode` → `Lint with flake8` (line 84-89) → `Type checking with mypy` → `Security check with bandit` → `Safety check` → **`Run smoke tests first`** (line 103-107). The "first" in the smoke-step name is a misnomer — it runs 4 steps after lint.
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
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2448-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2448-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2448-gemini.md` |

---

## Deliverable

**Issue-close criterion (same gate shape as #2442):** `python-tests.yml` run on `vamseeachanta/assethold` main produces BOTH:
1. at least one matrix cell (py3.11 / ubuntu-latest, `test` job) reaches `Run smoke tests first` with smoke-step `conclusion=success`; AND
2. every Windows cell reaches the `Install dependencies with uv` step (i.e., `actions/checkout@v4` no longer fails with `invalid path`).

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
        # `git rm` removes both the tree entry and the filesystem file in one step.
        git rm -- '<literal backslash path>'
    git commit -m "fix(ci): remove backslash-duplicate tree entries blocking Windows checkout (#2448)"
    git push origin main

# ACCEPTANCE-PHASE-1:
#   Local: `git ls-tree -r HEAD | awk '{print $4}' | grep -c '\\\\'` == 0
#   CI (next push): Windows matrix cells advance past `Checkout code` (no more exit 128);
#     next observable failure is `Install dependencies with uv` (or similar),
#     i.e., Windows reaches parity with Linux/macOS in step progression.

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
#   2. Verify: Windows cells advance past `Checkout code` on the P1 run
#      (jobs register and Checkout step conclusion=success on windows-latest rows).
#   3. Only after P1 CI verification: commit P2 (step reorder). Push. Wait for CI.
#   4. Verify: py3.11 / ubuntu-latest cell's `Run smoke tests first` step conclusion=success.
# If P1 CI fails unexpectedly (e.g., reveals a second backslash path we missed):
#   investigate before P2 commit; extend P1 to cover the new entry.
# If P2 CI fails on the smoke step itself (not lint): file a follow-on — that's product test-debt.

# ACCEPTANCE-PHASE-2:
#   CI: py3.11 / ubuntu-latest `Run smoke tests first` step conclusion=success.
#   Job may still be red downstream at `Lint with flake8` — that is expected
#   and tracked as follow-on.

# Combined close gate for #2448: P1 + P2 both verified on main CI.
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

Since this plan remediates CI config + git-tree hygiene (not application code), "tests" are **tree + workflow-state assertions** run via `git ls-tree`, `yq`, and `gh run view`.

| Test | What it verifies | Expected state after fix |
|---|---|---|
| P1-local-tree-clean | `cd assethold && git ls-tree -r HEAD -z \| tr '\0' '\n' \| awk -F'\t' '$2 ~ /\\\\/ {print $2}' \| wc -l` | `0` (zero backslash-containing tree entries) |
| P1-local-fs-clean | `cd assethold && find . -path './.git' -prune -o -type f -name '*\\*' -print \| wc -l` | `0` (no files with `\` in name on disk) |
| P1-ci-windows-checkout-success | `gh run view <p1-run-id> --repo vamseeachanta/assethold` — each Windows matrix cell's `Checkout code` step | `conclusion=success` on all windows-latest rows |
| P1-ci-no-windows-invalid-path | `gh run view <p1-run-id> --log \| grep -c 'invalid path'` | `0` hits |
| P2-local-step-order | `yq '.jobs.test.steps[] \| .name' .github/workflows/python-tests.yml` — position of `Run smoke tests first` vs `Lint with flake8` | smoke index < lint index |
| P2-local-yaml-parses | `uv run --no-project --with pyyaml python -c "import yaml; yaml.safe_load(open('.github/workflows/python-tests.yml'))"` | exit 0 |
| P2-ci-smoke-step-green | `gh run view <p2-run-id>` — py3.11/ubuntu-latest `Run smoke tests first` step | `conclusion=success` |
| P2-ci-smoke-ran-before-lint | same run — step timestamps | smoke `completed_at` < lint `started_at` |
| combined-close-gate | Both P1 run (windows checkout success) and P2 run (ubuntu smoke success) visible on main | both true on same base |

Pre-push local gates:
- Before P1 commit: `git ls-tree -r HEAD | awk '{print $4}' | grep -c '\\\\'` returns `2` (the entries we're about to delete); after `git rm` + add, `git ls-files | grep -c '\\\\'` returns `0`.
- Before P2 commit: local YAML parse exit 0, `yq` step-order check passes, `uv run pytest tests/test_smoke.py -v` still green (same baseline as #2442 P2).

---

## Acceptance Criteria

- [ ] Two pathological backslash-named tree entries removed from `vamseeachanta/assethold` main at `tests\modules\stocks\analysis\investment\results\Data\{multiple,single}_investment.csv` (P1 commit on main)
- [ ] Zero backslash-containing paths remain in `git ls-tree -r HEAD` on assethold main after P1
- [ ] Forward-slash equivalents (`tests/modules/stocks/analysis/investment/results/Data/{multiple,single}_investment.csv`) remain untouched — same blob SHAs as before (`ff919799`, `a5f160b2`)
- [ ] P1 CI run: every `windows-latest` matrix cell's `Checkout code` step has `conclusion=success`; no `invalid path` string in the run log
- [ ] `python-tests.yml` step order in the `test` job: `Install project in development mode` → `Run smoke tests first` → `Lint with flake8` (smoke before lint) (P2 commit on main)
- [ ] P2 commit preserves all existing step arguments, env blocks, and downstream jobs — diff is scope-limited to moving one step block
- [ ] P2 CI run: `Run smoke tests first` step on py3.11/ubuntu-latest has `conclusion=success`
- [ ] P1 and P2 are **separate commits** pushed sequentially with CI verification between (not bundled)
- [ ] Local smoke still green after P2: `cd assethold && uv run pytest tests/test_smoke.py -v` passes (same 17 baseline as #2442 P2)
- [ ] Review artifacts posted to `scripts/review/results/2026-04-22-plan-2448-{claude,codex,gemini}.md`
- [ ] No changes pushed to `assethold/` during this planning session — fixes land only after user sets `status:plan-approved` on #2448 after reviewing this plan and adversarial review
- [ ] Flake8 job may remain red in the P2 run (expected) — close criterion is the **smoke step** conclusion, not the whole lint step; follow-on issues filed for flake8 offender repair and `quality-gate` chain
- [ ] Predecessor issue #2442 close criterion re-evaluated after P2 lands (if the smoke cell on main is green, does that satisfy #2442's gate too? flag for user decision during P2 attestation)

---

## Adversarial Review Summary

<!-- Filled in after Wave 1 adversarial review completes. Plan remains in draft status until at least one review wave converges; no `status:plan-approved` label is set until user re-confirms in-thread. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | |
| Codex | (pending) | |
| Gemini | (pending) | |

**Wave 1 overall result:** (pending)

Revisions made based on review:
- (to be populated after first review wave)

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
