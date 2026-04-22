# Plan for #2441: digitalmodel Quality Gates — add missing `pylife` dependency (60+ runs red since 2026-04-05)

> **Status:** draft (v3 — Wave 2 MAJOR findings addressed, awaiting Wave 3 re-review)
> **Complexity:** T1
> **Date:** 2026-04-21 (v3 revision: 2026-04-22)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2441
> **Parent meta-issue:** https://github.com/vamseeachanta/workspace-hub/issues/2424
> **Target repo:** vamseeachanta/digitalmodel (separate git repo at `/mnt/local-analysis/workspace-hub/digitalmodel/`)
> **Review artifacts:** `-claude.md` / `-codex.md` / `-gemini.md` (Wave 1), `-*-r2.md` (Wave 2), `-*-r3.md` (Wave 3 — to be generated for this revision)

---

## Resource Intelligence Summary

### Existing repo code (digitalmodel)
- Found: `digitalmodel/src/digitalmodel/fatigue/sn_curves.py` line 15 — unguarded `from pylife.materiallaws.woehlercurve import WoehlerCurve` import.
- Found: `digitalmodel/src/digitalmodel/fatigue/__init__.py` line 18 — unconditional `from .sn_curves import get_sn_curve, DNV_CURVES` which transitively re-raises the `pylife` ModuleNotFoundError at package import.
- Found: `digitalmodel/scripts/integrations/pylife_poc.py` (lines 20, 89) — proof-of-concept using `pylife.materiallaws.woehlercurve.WoehlerCurve` and `pylife.materialdata.woehler.elementary.Elementary`. This file already documents the intent to depend on pylife.
- Found: `digitalmodel/docs/integrations/pylife-evaluation.md` line 121 — evaluation doc explicitly recommends: *"Add `pylife>=2.2` to digitalmodel's dependencies"*.
- Gap: `pylife` is not declared anywhere in `digitalmodel/pyproject.toml` — it is absent from the `dependencies = [...]` array under `[project]` (PEP 621) and absent from `[project.optional-dependencies]`.
- Gap: `digitalmodel/uv.lock` contains zero occurrences of `pylife` — the lockfile has never resolved pylife.
- Gap: No smoke import test exists that guards `import digitalmodel.fatigue` against missing-dep regressions (tests/fatigue/test_*.py all assume the package imports cleanly and fail at collection when it does not).

### Standards
Not applicable — this is an infrastructure/dependency fix, not a physics / domain-standards change. DNV-RP-C203 coverage is already implemented in `sn_curves.py`; this plan only fixes the missing transitive dependency that stops the module from importing.

### LLM Wiki pages consulted
No relevant wiki pages — pylife is a third-party Python library, not a domain knowledge artifact. The repo's `docs/integrations/pylife-evaluation.md` covers the decision to use pylife and is already cited above.

### Documents consulted
- Issue #2441 body — documents investigation, cites commits `72c74350` (2026-03-30), `eb7e8229` and `cd510968` (2026-04-02) as the fatigue-module landing point, names run `24579096595` as representative failing run.
- Parent meta-issue #2424 — "6 of 7 ecosystem repos have red main CI"; #2441 is one child workstream. Confirmed OPEN, labels include `cat:infrastructure`, `status:plan-approved` at parent level (distinct from #2441's own state).
- `digitalmodel/docs/integrations/pylife-evaluation.md` — explicitly recommends `pylife>=2.2` be added to runtime dependencies.
- PyPI `pylife` — latest 2.2.1, `requires-python >=3.9`, Apache-2.0 license, compatible with digitalmodel's `requires-python = ">=3.11"`.
- Prior plans: grep of `docs/plans/` for `pylife` or `fatigue` returned no prior planning artifact covering this regression — this is the first plan.

### Gaps identified
- `pylife` declaration missing from `pyproject.toml` — must be added.
- `uv.lock` must be regenerated to pin pylife and its transitive graph.
- No CI-side smoke test asserts `import digitalmodel.fatigue` succeeds before the full pytest collection runs — a minimal regression test should be added so future missing-dep regressions fail fast with a clearer signal than 10 pytest collection errors.
- Plan file is now committed at `docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md` (git-tracked, landed in commit `3b09fc067`); no `.planning/plan-approved/2441*` marker exists — approval remains user-gated.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view`):
- `#2441` — OPEN — "chore(ci-health): digitalmodel Quality Gates — 60+ runs red since 2026-04-05 (pylife missing dep)" — current labels: `priority:medium`, `cat:infrastructure`, `status:plan-approved`. NOTE: this label predates any plan artifact and predates adversarial review — governance drift to be flagged in the issue comment alongside this plan.
- `#2424` — OPEN — parent meta-issue "cross-repo CI audit — 6 of 7 ecosystem repos have red main CI".

**File existence** (verified 2026-04-21 via `ls` / `gh api` on remote main):
- EXISTS (remote main, content verified via `gh api repos/vamseeachanta/digitalmodel/contents/src/digitalmodel/fatigue/sn_curves.py`): `digitalmodel/src/digitalmodel/fatigue/sn_curves.py`
- EXISTS (remote main): `digitalmodel/src/digitalmodel/fatigue/__init__.py`
- EXISTS (local, 391 lines): `digitalmodel/pyproject.toml`
- EXISTS (local): `digitalmodel/uv.lock`
- EXISTS (local, 14 test files — verified 2026-04-21 via `ls digitalmodel/tests/fatigue/test_*.py | wc -l`): `digitalmodel/tests/fatigue/test_*.py`
- EXISTS (local): `digitalmodel/.github/workflows/quality-gates.yml`
- EXISTS (git-tracked, verified 2026-04-21 via `git ls-files docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md`, landed in commit `3b09fc067`): `docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md`
- MISSING (implementation step will create in digitalmodel, post-approval): `tests/fatigue/test_package_imports.py` (smoke import regression test)

**Line excerpts** (verified via `gh api ... /contents/...` on vamseeachanta/digitalmodel main and local `sed`):

`src/digitalmodel/fatigue/sn_curves.py` (remote main, lines ~1–15):
```
"""
DNV-RP-C203 (2021) S-N Curve Library
...
Uses pyLife's WoehlerCurve for cycle calculations.
"""

import math
import numpy as np
import pandas as pd
from pylife.materiallaws.woehlercurve import WoehlerCurve
```

`src/digitalmodel/fatigue/__init__.py` (remote main, line 18):
```
from .sn_curves import get_sn_curve, DNV_CURVES
```

`pyproject.toml` grep for pylife (local):
```
$ grep -n pylife /mnt/local-analysis/workspace-hub/digitalmodel/pyproject.toml
# (no matches — pylife absent)
```

`uv.lock` grep for pylife (local):
```
$ grep -c pylife /mnt/local-analysis/workspace-hub/digitalmodel/uv.lock
0
```

**Failing CI run excerpt** (`gh run view 24579096595 --repo vamseeachanta/digitalmodel --log-failed`, 2026-04-17T17:54:09Z):
```
src/digitalmodel/fatigue/sn_curves.py:15: in <module>
    from pylife.materiallaws.woehlercurve import WoehlerCurve
E   ModuleNotFoundError: No module named 'pylife'

ERROR tests/fatigue/test_crack_growth.py
ERROR tests/fatigue/test_damage.py
ERROR tests/fatigue/test_environmental_correction.py
ERROR tests/fatigue/test_fatigue_reporting.py
ERROR tests/fatigue/test_hotspot_stress.py
ERROR tests/fatigue/test_multiaxial_fatigue.py
ERROR tests/fatigue/test_rainflow.py
ERROR tests/fatigue/test_scf_library.py
ERROR tests/fatigue/test_sn_curves.py
ERROR tests/fatigue/test_sn_library.py
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 10 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
============================== 10 errors in 3.65s ==============================
```
Confirms 10 test-collection failures, all tracing to the single `pylife` import at `sn_curves.py:15`, `--maxfail=10` aborts the run, Quality Gates "tests" gate fails fast.

**Failing-runs-on-main context** (`gh run list --repo vamseeachanta/digitalmodel --branch main --status failure --limit 5`):
- `24579096595` 2026-04-17 — failure (Quality Gates)
- `24483044968` 2026-04-15 — failure (Quality Gates)
- `24477438806` 2026-04-15 — failure (Quality Gates)
- `24475612637` 2026-04-15 — failure (Quality Gates)
- `24473451784` 2026-04-15 — failure (Quality Gates)
Confirms sustained failure pattern on main, consistent with "60+ runs red since 2026-04-05" framing.

**PyPI availability proof** (verified 2026-04-21 via `curl -sS https://pypi.org/pypi/pylife/json`):
- latest: `2.2.1`
- `requires-python`: `>=3.9`
- license: Apache-2.0
Compatible with digitalmodel's `requires-python = ">=3.11"`.

**Gap proofs** (verified 2026-04-21):
- `grep -n pylife digitalmodel/pyproject.toml` → no output → confirms pylife absent from deps.
- `grep -c pylife digitalmodel/uv.lock` → 0 → confirms pylife never resolved.
- `git ls-files docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md` → returns the path. First-landing commit: `3b09fc067` (2026-04-21 auto-sync). HEAD commit for this file will advance with each Wave revision; a reviewer running `git log --oneline -1 <path>` should not expect the first-landing SHA to remain HEAD. Wave 2 revision shipped in commit `bf2222da2`; Wave 3 revision in a new commit landing alongside the Wave 3 review artifacts. This supersedes an earlier draft's "plan file MISSING" claim.
- `ls .planning/plan-approved/2441*` → "No such file or directory" → confirms no local approval marker (despite the issue carrying `status:plan-approved` label — flagged as governance drift).

Source count: 6 distinct sources consulted (issue #2441 body, parent issue #2424, digitalmodel source files, digitalmodel pyproject/uv.lock, digitalmodel CI log run `24579096595`, PyPI pylife registry). Minimum of 3 satisfied.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md` |
| Target dep manifest | `digitalmodel/pyproject.toml` |
| Target lockfile | `digitalmodel/uv.lock` |
| Trigger site | `digitalmodel/src/digitalmodel/fatigue/sn_curves.py:15` |
| Package init (transitive failure site) | `digitalmodel/src/digitalmodel/fatigue/__init__.py:18` |
| New smoke test | `digitalmodel/tests/fatigue/test_package_imports.py` |
| CI workflow | `digitalmodel/.github/workflows/quality-gates.yml` |
| Plan review — Claude | `scripts/review/results/2026-04-21-plan-2441-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-21-plan-2441-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-21-plan-2441-gemini.md` |

---

## Deliverable

`digitalmodel/pyproject.toml` declares `pylife>=2.2,<3.0` as a runtime dependency, `uv.lock` is refreshed, a smoke import test guards `import digitalmodel.fatigue` against missing-dep regressions, and the `Quality Gates` workflow `tests` gate (gate 1 in `digitalmodel/.claude/quality-gates.yaml`) no longer fails with `ModuleNotFoundError: No module named 'pylife'` — the full `fatigue/` test subtree collects and runs. A separate pre-existing `coverage` gate (gate 2) blocker is explicitly out of scope for this T1 and tracked as a follow-up (see `Risks — coverage-gate blocker` below).

**Explicit scope boundary:** this plan does NOT promise an overall green Quality Gates workflow on the first post-fix run. Live code inspection of `digitalmodel/src/digitalmodel/workflows/automation/quality_gates.py:285-295` shows `_execute_coverage_gate` returns `GateStatus.ERROR` when `coverage.json` is missing, and the workflow has no step producing `coverage.json` (the `tests` gate command in `quality-gates.yaml:10` runs plain `python -m pytest` with no `--cov` flag). With `ci_cd.strict_mode: true` (`.claude/quality-gates.yaml:100`), the ERROR propagates. The pylife fix retires the `tests`-gate blocker only.

---

## Approach — Path A (preferred) vs Path B (rejected)

The issue body describes two candidate fixes:

- **Path A (chosen): add `pylife` as a runtime dependency.** Rationale: (1) pylife is imported unconditionally at module load, (2) the existing docs (`docs/integrations/pylife-evaluation.md`) already recommend `pylife>=2.2` as a runtime dep, (3) fatigue analysis is a first-class digitalmodel capability — not an optional extra, (4) all 14 test modules under `tests/fatigue/` depend on the import succeeding (the CI log surfaces only 10 because `--maxfail=10` aborts collection at that cutoff), indicating load-bearing runtime use. Cheapest, smallest, lowest-risk correct fix.
- **Path B (rejected): guard the import with `try/except ModuleNotFoundError`.** Rejected because this turns a core module into a silently-degraded one: `get_sn_curve`, `DNV_CURVES`, and all downstream fatigue functions would become `None` or stub-raising, 10 test modules would need `pytest.importorskip("pylife")`, and actual fatigue consumers would get deferred failures at call time instead of install time. The existing `OrcFxAPI` optional pattern is only appropriate for licensed/vendor-gated software, which pylife is not.

Trivial fix — no pseudocode required (T1). See `Files to Change` for exact deltas.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/pyproject.toml` | Append the string `"pylife>=2.2,<3.0"` to the `dependencies = [...]` array under `[project]` (PEP 621 — dependencies is an array, not a sub-table), alphabetically near `pykalman` / `pymssql`. |
| Regenerate | `digitalmodel/uv.lock` | Re-run `uv lock` after the pyproject change to pin pylife and its transitive graph (numpy/pandas/scipy already present — expected to be a pure add, not a bump). |
| Create | `digitalmodel/tests/fatigue/test_package_imports.py` | Smoke test asserting `import digitalmodel.fatigue` succeeds and exposes `get_sn_curve`, `DNV_CURVES`. Fails fast and clearly if pylife (or any other fatigue-package dep) is ever dropped again. |
| No change | `digitalmodel/src/digitalmodel/fatigue/sn_curves.py` | Intentional — Path A keeps the unguarded import. |
| No change | `digitalmodel/src/digitalmodel/fatigue/__init__.py` | Intentional. |
| No change | `digitalmodel/.github/workflows/quality-gates.yml` | The existing `UV_NO_SOURCES=true uv pip install -e .` install step resolves deps on the fly from `pyproject.toml` (ignoring `uv.lock`), so it will pick up the new `pylife` dep automatically once pyproject declares it. Note: this means `uv.lock` is local-reproducibility-only, not a CI gate — see `Risks` for the deferred `uv sync --frozen` follow-up. |
| No change | `docs/plans/README.md` | Per task constraint — not updating the workspace-hub plan index in this draft. |

Scope constraint (HARD): during implementation, code-write scope is limited to (a) files in the digitalmodel repo listed above, (b) this workspace-hub plan file, (c) the three adversarial-review artifacts at `scripts/review/results/2026-04-21-plan-2441-{claude,codex,gemini}.md`, and (d) GitHub comment posts on #2441 (closeout) and #2424 (cross-link). No changes to any other path. No `status:*` label edits or approval-marker creation inside this plan's execution — those remain user-gated governance actions.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_fatigue_package_imports` | `import digitalmodel.fatigue` succeeds without raising — this is the **whole-package import guard**; any broken import anywhere under `fatigue/__init__.py` trips it. | (import statement) | no exception; module is not None |
| `test_fatigue_exports_get_sn_curve` | Representative re-export from `sn_curves` (NOT exhaustive — `fatigue/__init__.py` re-exports many symbols; this test samples the one tied to the pylife regression). | `from digitalmodel.fatigue import get_sn_curve` | callable is not None |
| `test_fatigue_exports_dnv_curves` | Representative re-export of the DNV curve registry (NOT exhaustive — same caveat as above). | `from digitalmodel.fatigue import DNV_CURVES` | dict-like, non-empty |
| `test_pylife_woehlercurve_importable` | The exact third-party symbol used at `sn_curves.py:15` is resolvable and instantiable with the same call contract `sn_curves.py:148` uses (`return WoehlerCurve(params)` where `params` is a `pd.Series` with keys `k_1`, `SD`, `ND`, `k_2`). | `WoehlerCurve(pd.Series({"k_1": 3.0, "SD": 52.63, "ND": 1e7, "k_2": 5.0}))` (sample values from DNV curve D air in `sn_curves.py`) | class object resolves; instantiation returns a non-None `WoehlerCurve`. Cited source: `digitalmodel/src/digitalmodel/fatigue/sn_curves.py` lines 142-148. |

All four tests live in the new `tests/fatigue/test_package_imports.py` and must collect + run in under 2 seconds to keep the Quality Gates fail-fast loop tight.

Implementation order (after approval):
1. Capture pre-change baseline using **both** the CI tests-gate command and the fatigue-collect command, so step 7 has a diffable baseline for each. Scaffold a throwaway venv guaranteed to lack pylife to make the baseline deterministic independent of the developer's prior `uv sync` state:
   ```
   cd digitalmodel
   python3.11 -m venv /tmp/pre-2441-venv
   /tmp/pre-2441-venv/bin/pip install -e . pytest pytest-cov ruff bandit pyyaml loguru click
   /tmp/pre-2441-venv/bin/python -c "import pylife" 2>&1 | tee /tmp/pre-2441-pylife-check.txt   # must say ModuleNotFoundError
   /tmp/pre-2441-venv/bin/pytest --collect-only tests/fatigue/ 2>&1 | tee /tmp/pre-2441-fatigue-collect.txt
   /tmp/pre-2441-venv/bin/pytest --maxfail=10 -p no:asyncio -p no:randomly -p no:sugar -p no:capture --no-header -q --tb=line tests/ 2>&1 | tee /tmp/pre-2441-ci-command-baseline.txt
   ```
   (The third command mirrors `digitalmodel/.claude/quality-gates.yaml:10` exactly — no `-m "not solver"` filter, matching what CI runs.) The embedded CI-log excerpt under `Evidence` also remains a canonical pre-change CI signal for the `tests` gate.
2. Write the four tests (TDD red) in the throwaway venv from step 1 — before installing pylife, run the new `tests/fatigue/test_package_imports.py` via `/tmp/pre-2441-venv/bin/pytest tests/fatigue/test_package_imports.py -v` and confirm all four fail with `ModuleNotFoundError: No module named 'pylife'`. Keep the venv around so the green step below uses the same Python.
3. Append `"pylife>=2.2,<3.0"` to the `dependencies = [...]` array under `[project]` in `digitalmodel/pyproject.toml`.
4. Run `uv lock --upgrade-package pylife` in the digitalmodel repo (scoped refresh — avoids unintended bumps on other floating constraints like pydantic/pytest/hypothesis).
5. In the throwaway venv: `/tmp/pre-2441-venv/bin/pip install "pylife>=2.2,<3.0"` then `/tmp/pre-2441-venv/bin/pytest tests/fatigue/test_package_imports.py -v` — all four tests pass (TDD green).
6. Run full `/tmp/pre-2441-venv/bin/pytest tests/fatigue/ -v` — all 14 test modules collect cleanly.
7. Run the CI tests-gate command verbatim: `/tmp/pre-2441-venv/bin/pytest --maxfail=10 -p no:asyncio -p no:randomly -p no:sugar -p no:capture --no-header -q --tb=line tests/ 2>&1 | tee /tmp/post-2441-ci-command.txt`. Diff against `/tmp/pre-2441-ci-command-baseline.txt` from step 1: (a) no new `ModuleNotFoundError: No module named 'pylife'` lines, (b) the fatigue-collect error count drops to zero, (c) any pre-existing failures outside `tests/fatigue/` that existed pre-change may persist (they are pre-existing regressions, not regressions of this change). Record the pre/post failure counts in the closeout comment.
8. Commit directly to `main` of the digitalmodel repo and push, per workspace `AGENTS.md` line 15 ("Git: commit to `main` + push; branch only for multi-session work"). This fix is single-session, so no branch/PR is required. Observe the first Quality Gates run after push: **verify the `tests` gate stops logging `ModuleNotFoundError: No module named 'pylife'`** — this is the falsifiable success signal. The overall workflow may remain red due to the separately-tracked coverage-gate blocker (see `Risks`); that is expected and tracked as a follow-up, not a failure of this plan. If during implementation the work is split across sessions, switch to a branch/PR path and cite the multi-session exception in the closeout comment.

---

## Acceptance Criteria

- [ ] `digitalmodel/pyproject.toml` — the `dependencies = [...]` array under `[project]` contains the string `"pylife>=2.2,<3.0"` (PEP 621 array, not a sub-table).
- [ ] `digitalmodel/uv.lock` contains at least one `pylife` entry (`grep -c pylife uv.lock` > 0).
- [ ] Throwaway-venv smoke: `/tmp/pre-2441-venv/bin/pytest tests/fatigue/test_package_imports.py -v` — all 4 new tests pass.
- [ ] Throwaway-venv full fatigue: `/tmp/pre-2441-venv/bin/pytest tests/fatigue/ -v` — no collection errors, no `ModuleNotFoundError: No module named 'pylife'`; all 14 test modules collect.
- [ ] CI-command parity: post-change `/tmp/post-2441-ci-command.txt` (from step 7, which runs the exact `tests`-gate command from `digitalmodel/.claude/quality-gates.yaml:10`) contains **zero** `ModuleNotFoundError: No module named 'pylife'` lines. Pre-change baseline for the same command was captured in step 1 at `/tmp/pre-2441-ci-command-baseline.txt`; the diff shows fatigue-collection errors cleared, with pre-existing non-fatigue failures allowed to persist.
- [ ] First post-fix Quality Gates run on `vamseeachanta/digitalmodel` main: `tests` gate (gate 1) no longer surfaces a pylife `ModuleNotFoundError`. The overall workflow status is permitted to remain red **if and only if** the remaining failure is the pre-existing coverage-gate `ERROR: Coverage file not found: coverage.json` (see `Risks — coverage-gate blocker`) — any other new failure mode invalidates the fix.
- [ ] Follow-up issue opened to track the coverage-gate workflow blocker (`coverage.json` not produced by the `tests` gate command; `_execute_coverage_gate` returns `GateStatus.ERROR`). Cross-linked from #2441 closeout and from parent #2424.
- [ ] Wave 3 adversarial-review artifacts posted to `scripts/review/results/2026-04-21-plan-2441-{claude,codex,gemini}-r3.md` — zero new MAJOR findings outstanding that were not present in Wave 2. (Self-referential caveat: the implementing agent does not self-assess this; user inspects the r3 artifacts before setting `status:plan-approved`.)
- [ ] Closeout comment posted to #2441 linking the fix commit + the first post-fix Quality Gates run URL + the follow-up coverage-gate issue.

---

## Adversarial Review Summary

**Wave 1 (2026-04-21):** three-provider adversarial review executed.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE (minor drift) | Test count (15 vs actual 14); Path A rationale under-counts affected modules; `uv lock` unscoped; CI linkage (`quality_gates_cli` → pytest) unexplained; `WoehlerCurve` constructor kwargs unspecified; regression acceptance non-falsifiable without baseline. |
| Codex | MAJOR | Scope vs acceptance contradiction (review artifacts + GH comments outside declared HARD scope); TDD step 7 (branch/PR) conflicts with `AGENTS.md` commit-to-main default; embedded Evidence says plan file MISSING but plan is committed at `3b09fc067`; no captured pre-change baseline for "no regression" acceptance; `WoehlerCurve` constructor contract uncited. |
| Gemini | MINOR | PEP 621 wording: `dependencies` is an array under `[project]`, not a `[project.dependencies]` sub-table; CI uses `uv pip install -e .` which ignores `uv.lock`, so lockfile refresh is local-reproducibility only, not a CI gate. |

**Wave 1 overall verdict:** MAJOR (Codex dominant).

**Revisions made based on Wave 1 review:**
- Widened HARD scope (`Files to Change` footer) to include `scripts/review/results/*` artifacts and GH comment posts on #2441/#2424 — resolves the scope-vs-acceptance contradiction.
- Rewrote TDD step 8 (formerly step 7) to commit-to-main per `AGENTS.md` line 15, with an explicit multi-session escape hatch cited back to the same clause.
- Updated the Evidence block: plan file is now EXISTS (git-tracked at commit `3b09fc067`), not MISSING; removed the stale `ls docs/plans/2026-04-21-issue-2441*` "not found" gap-proof.
- Added implementation step 1 that captures a pre-change baseline (local `uv run pytest --collect-only tests/fatigue/` + the CI-log excerpt under `Evidence`) and rewrote the regression acceptance criterion as a testable "collection completes without ModuleNotFoundError; previously passing tests still pass" statement.
- Corrected PEP 621 wording throughout (pyproject.toml row in `Files to Change`, acceptance criterion, `Resource Intelligence Summary` gap bullet).
- Scoped the lockfile refresh to `uv lock --upgrade-package pylife` (implementation step 4) to avoid collateral bumps.
- Recounted tests: `14`, not `15` — propagated to `Evidence`, Path A rationale, TDD step 6, and the acceptance criterion on `tests/fatigue/`.
- Tightened `test_pylife_woehlercurve_importable`: now instantiates `WoehlerCurve(pd.Series({"k_1": 3.0, "SD": 52.63, "ND": 1e7, "k_2": 5.0}))` — the exact call contract used at `digitalmodel/src/digitalmodel/fatigue/sn_curves.py:142-148`, with that source cited in the TDD table.
- Added a `uv.lock` vs CI risk note (see `Risks` section): Quality Gates install line `UV_NO_SOURCES=true uv pip install -e .` resolves deps on the fly and ignores `uv.lock`; the lockfile regen is reproducibility insurance for local/agent environments, not a CI gate. A workflow migration to `uv sync --frozen` is tracked as a deferred follow-up, not in scope for #2441.

**Revisions deferred** (lower-severity, tracked as follow-up, not required for Wave 2):
- Claude's suggestion to add a one-line `quality_gates_cli → QualityGateValidator → pytest` trace — deferred; the existing `Evidence` block already proves the CI-visible failure is a pytest collection error at `sn_curves.py:15`, and the Quality Gates install step uses standard `uv pip install -e .`, so the mechanism is implicit. Low reader-confusion risk.
- Claude's open question on `conftest.py` in `digitalmodel/tests/fatigue/` — deferred; not implicated by the current failure mode (no `pylife` import in any conftest); will be reconsidered only if the smoke test collection misbehaves post-fix.
- Claude's open question on relocating the smoke test to package-level `tests/test_imports.py` — deferred; leaving it at `tests/fatigue/test_package_imports.py` keeps it scoped to the failing package and colocated with the regression it guards.
- Gemini's suggestion to migrate CI to `uv sync --frozen` — captured in `Risks` as a deferred follow-up to avoid scope creep on a T1 dep-declaration fix.
- Parent-issue #2424 red-CI enumeration — deferred; handled in #2424's own plan, not in #2441's closeout comment.

**Status (v2):** revised, awaiting Wave 2 re-review.

**Wave 2 (2026-04-21):** three-provider adversarial re-review executed against the v2 plan.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE (minor drift) | Stale commit-hash cite (`3b09fc067` historic vs current HEAD); TDD step 2 determinism fragile (depends on prior `uv sync` state); "Quality Gates green on first run" criterion silently assumes pylife was the only red signal; self-referential acceptance criterion on "zero MAJOR findings"; smoke-test naming over-promises coverage (2 symbols vs dozens). |
| Codex | MAJOR | (1) `Deliverable` / `Acceptance Criteria` claim first-post-fix Quality Gates returns green, but live code inspection of `digitalmodel/src/digitalmodel/workflows/automation/quality_gates.py:285-295` shows `_execute_coverage_gate` returns `ERROR` when `coverage.json` is missing, and the workflow has no step producing `coverage.json` (the `tests`-gate command `python -m pytest ...` has no `--cov` flag, and the workflow has no prior coverage step). (2) Regression-baseline step 1 only captures `--collect-only tests/fatigue/` plus an old CI log, but acceptance requires diff of `pytest tests/ -v -m "not solver"` — a fatigue-only collect baseline cannot establish a full-suite failure-set diff. (3) Local verification command `pytest tests/ -v -m "not solver"` diverges from the CI `tests`-gate command `python -m pytest --maxfail=10 -p no:asyncio -p no:randomly -p no:sugar -p no:capture --no-header -q --tb=line` (no `-m "not solver"` in CI); `digitalmodel/tests/solver/conftest.py` auto-marks the solver directory, so local results don't mirror CI. |
| Gemini | MAJOR | Structural: the `Adversarial Review Summary` documents Wave 1 only; it omits what the Wave 2 findings were and how they were addressed, making a Wave 3 re-review impossible to perform as specified. |

**Wave 2 overall verdict:** MAJOR (Codex + Gemini concurrent).

**Revisions made in v3 based on Wave 2 review:**

- (Codex.1 → resolved) `Deliverable` narrowed to "`tests` gate no longer fails with `ModuleNotFoundError` for `pylife`" and an explicit scope boundary paragraph states that an overall green workflow is NOT promised. The coverage-gate blocker is documented in `Risks — coverage-gate blocker` with the exact code cite (`quality_gates.py:285-295`) and the missing `--cov` flag cited at `.claude/quality-gates.yaml:10`. Acceptance criterion rewritten to the falsifiable form "`tests` gate stops logging `ModuleNotFoundError` for `pylife`; overall run is permitted to remain red IFF the remaining failure is the pre-existing coverage-gate ERROR". A new acceptance checkbox requires opening a follow-up issue tracking the coverage-gate wiring, cross-linked from #2441 closeout and parent #2424.
- (Codex.2 → resolved) `Implementation order` step 1 was rewritten to capture THREE baselines, all in a throwaway venv (so the baseline is deterministic regardless of prior `uv sync` state): (a) `python -c "import pylife"` failure proof, (b) `pytest --collect-only tests/fatigue/` output, (c) the exact CI `tests`-gate command verbatim (`pytest --maxfail=10 -p no:asyncio -p no:randomly -p no:sugar -p no:capture --no-header -q --tb=line tests/`) piped to `/tmp/pre-2441-ci-command-baseline.txt`. Step 7 now runs the same CI command post-change and diffs against that baseline.
- (Codex.3 → resolved) `Implementation order` steps 2–7 now run the CI command verbatim in the throwaway venv. Local-vs-CI divergence (`-m "not solver"` filter and `pytest tests/ -v` shorthand) removed from steps 7 and from the acceptance criteria. Step 7 is the exact CI `tests`-gate command; the solver auto-mark in `tests/solver/conftest.py` now behaves identically locally and in CI.
- (Gemini → resolved) This `Adversarial Review Summary` now includes a Wave 2 verdict table, a bulleted list of each Wave 2 finding mapped to its v3 resolution, and a Wave 3 status line below. A Wave 3 re-reviewer can now verify claims point-by-point.
- (Claude.1 → resolved) Evidence block commit-hash note rewritten to clarify `3b09fc067` as first-landing and `bf2222da2` as Wave 2 HEAD (and a fresh v3 commit SHA will appear after this revision lands). Reviewers running `git log --oneline -1` on the plan file should expect the HEAD SHA to advance with each wave.
- (Claude.2 → resolved) TDD step 2 now scaffolds `/tmp/pre-2441-venv` explicitly and asserts `python -c "import pylife"` returns `ModuleNotFoundError` before running the red pytest step — TDD red is deterministic regardless of developer prior state.
- (Claude.3 → resolved via narrowing) "Quality Gates returns green on first run" removed; replaced with falsifiable "`tests` gate no longer logs `ModuleNotFoundError` for `pylife`" (see Codex.1 resolution above).
- (Claude.4 → explicit acknowledgement) The acceptance criterion on "zero MAJOR findings in adversarial-review artifacts" is annotated as self-referential — the implementing agent does NOT self-assess it; the user inspects r3 artifacts before labeling `status:plan-approved`.
- (Claude.5 → resolved) Smoke-test scope note: the two targeted `__init__` exports (`get_sn_curve`, `DNV_CURVES`) are labeled in the TDD table description as "representative re-exports from the `sn_curves` module — NOT exhaustive; `test_fatigue_package_imports` is the whole-package import guard". The file remains at `tests/fatigue/test_package_imports.py` (keeping the regression colocated with the failing package).

**Revisions deferred in v3** (lower-severity, tracked as follow-up):
- Claude's suggestion to rename the smoke test file to `test_fatigue_smoke.py` — deferred; filename is already scoped to the package, and relabeling in-file description achieves the same truthfulness without churn.
- Claude's suggestion to specify the first post-fix `gh run` ID in advance — deferred; the implementing agent captures it immediately after `git push` in the closeout comment.
- Claude's question on pylife 2.x transitive extras fallback — deferred; will be resolved by inspecting `uv.lock` diff during implementation (step 4), then narrowing to `[project.optional-dependencies].fatigue` only if jupyter/matplotlib-weight deps appear. This is a runtime decision, not a plan-time decision.

**Status (v3):** revised, awaiting Wave 3 re-review. **Not approval-ready** until Wave 3 returns no new MAJOR findings AND user explicitly labels `status:plan-approved`. This plan MUST NOT be self-approved by any agent.

---

## Risks and Open Questions

- **Risk — transitive dep bloat:** `pylife>=2.2` may pull a noticeable transitive graph (scipy, pandas, numpy are already in digitalmodel deps, so the incremental cost should be small, but verify during `uv lock`). Mitigation: inspect `uv.lock` diff post-change; if pylife pulls unexpected heavyweight deps (e.g. Jupyter / plotting extras), consider moving to an `[project.optional-dependencies].fatigue` extra and gating the fatigue subpackage import with a clearer error message.
- **Risk — version-upper-bound drift:** Upper bound `<3.0` is defensive — pylife may never ship 3.x, or may ship 3.x with backward-compatible `WoehlerCurve`. Safe default; revisit if pylife 3.x lands.
- **Risk — uv.lock merge conflicts:** Concurrent unrelated PRs on digitalmodel may touch `uv.lock`. Mitigation: rebase immediately before merge and re-run `uv lock --upgrade-package pylife` if needed.
- **Risk — `uv.lock` is not a CI gate:** The Quality Gates workflow installs with `UV_NO_SOURCES=true uv pip install -e .` (`digitalmodel/.github/workflows/quality-gates.yml` line 36), which resolves dependencies on the fly from `pyproject.toml` and ignores `uv.lock`. Regenerating `uv.lock` is therefore **local-reproducibility insurance only** — it does NOT gate CI. The CI fix is driven entirely by the `pyproject.toml` change. Deferred follow-up: migrate the install step to `uv sync --frozen` so CI tests the locked graph; out of scope for this T1.
- **Risk — collateral lockfile bumps:** Bare `uv lock` can bump any dep whose constraint floats (e.g., `pydantic>=2.7.0,<3.0.0`, `pytest>=7.4.3,<9.0.0`, `hypothesis>=6.100.0,<7.0.0`). Mitigation: implementation step 4 scopes the refresh with `uv lock --upgrade-package pylife`. Post-change, inspect `uv.lock` diff; if any non-pylife/non-transitive line churns, revert and re-run with tighter scoping.
- **Risk — governance-drift optics:** Issue #2441 already carries `status:plan-approved` label before this plan existed. This plan is draft-only; the label does not reflect an actually-reviewed plan. Governance comment (separate from this plan) flags the drift for user resolution.
- **Risk — coverage-gate blocker (out of scope for #2441):** Codex Wave 2 surfaced a pre-existing Quality Gates blocker independent of pylife. `digitalmodel/.github/workflows/quality-gates.yml` has no coverage step; `.claude/quality-gates.yaml:10` runs the `tests` gate with plain `python -m pytest ...` (no `--cov` flag); `src/digitalmodel/workflows/automation/quality_gates.py:285-295` `_execute_coverage_gate` returns `GateStatus.ERROR` when `coverage.json` is missing; and `.claude/quality-gates.yaml:100` sets `ci_cd.strict_mode: true`, so the ERROR blocks the workflow. After this plan's fix lands, the workflow will likely remain red due to the coverage-gate ERROR — **this is expected and explicitly out of scope for #2441**. The coverage-gate fix is tracked as a required follow-up issue (open before closing #2441), cross-linked from the closeout comment and from parent #2424. Two candidate fixes for the follow-up: (a) add `--cov=src --cov-report=json:coverage.json` to `.claude/quality-gates.yaml:10` so the `tests` gate produces `coverage.json` inline, or (b) add a dedicated coverage step to `quality-gates.yml` before the `Run Quality Gates` step. Decision deferred to the follow-up issue.
- **Open — should `pylife-evaluation.md` be updated post-fix?** Its current phrasing is forward-looking ("Add pylife>=2.2 to digitalmodel's dependencies"). Low-priority follow-up; not blocking this plan.
- **Open — CI-level `pip install pylife` shortcut?** The Quality Gates workflow could add `uv pip install pylife` as a temporary hot-fix before `pyproject.toml` is updated. Rejected: hot-fixes in workflow YAML drift from declared deps and create the exact class of bug this plan is fixing. Fix it in `pyproject.toml` only.
- **Open — parent #2424 signal:** Closing this one red CI among the 7 ecosystem repos should update the parent meta-issue's tally. Post a cross-link comment on #2424 after #2441 closes.

---

## Complexity: T1

**T1** — single missing runtime dependency declaration, plus one small regression-guard test file. One-line pyproject change, auto-regenerated lockfile, four trivial smoke-import tests. No domain logic changes, no new module design, no multi-file refactor. Root cause is mechanically verified (remote main source + failing CI log + empty grep). Path A vs Path B decision is documented in-plan. Fits the T1 classification cleanly.
