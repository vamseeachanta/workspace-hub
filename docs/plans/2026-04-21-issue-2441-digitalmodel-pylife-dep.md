# Plan for #2441: digitalmodel Quality Gates — add missing `pylife` dependency (60+ runs red since 2026-04-05)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2441
> **Parent meta-issue:** https://github.com/vamseeachanta/workspace-hub/issues/2424
> **Target repo:** vamseeachanta/digitalmodel (separate git repo at `/mnt/local-analysis/workspace-hub/digitalmodel/`)
> **Review artifacts:** scripts/review/results/2026-04-21-plan-2441-claude.md | ...-codex.md | ...-gemini.md (pending adversarial review wave)

---

## Resource Intelligence Summary

### Existing repo code (digitalmodel)
- Found: `digitalmodel/src/digitalmodel/fatigue/sn_curves.py` line 15 — unguarded `from pylife.materiallaws.woehlercurve import WoehlerCurve` import.
- Found: `digitalmodel/src/digitalmodel/fatigue/__init__.py` line 18 — unconditional `from .sn_curves import get_sn_curve, DNV_CURVES` which transitively re-raises the `pylife` ModuleNotFoundError at package import.
- Found: `digitalmodel/scripts/integrations/pylife_poc.py` (lines 20, 89) — proof-of-concept using `pylife.materiallaws.woehlercurve.WoehlerCurve` and `pylife.materialdata.woehler.elementary.Elementary`. This file already documents the intent to depend on pylife.
- Found: `digitalmodel/docs/integrations/pylife-evaluation.md` line 121 — evaluation doc explicitly recommends: *"Add `pylife>=2.2` to digitalmodel's dependencies"*.
- Gap: `pylife` is not declared anywhere in `digitalmodel/pyproject.toml` (neither `[project.dependencies]` nor `[project.optional-dependencies]`).
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
- No plan or approval marker for #2441 exists yet in workspace-hub (`docs/plans/` and `.planning/plan-approved/` both empty for this issue number).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view`):
- `#2441` — OPEN — "chore(ci-health): digitalmodel Quality Gates — 60+ runs red since 2026-04-05 (pylife missing dep)" — current labels: `priority:medium`, `cat:infrastructure`, `status:plan-approved`. NOTE: this label predates any plan artifact and predates adversarial review — governance drift to be flagged in the issue comment alongside this plan.
- `#2424` — OPEN — parent meta-issue "cross-repo CI audit — 6 of 7 ecosystem repos have red main CI".

**File existence** (verified 2026-04-21 via `ls` / `gh api` on remote main):
- EXISTS (remote main, content verified via `gh api repos/vamseeachanta/digitalmodel/contents/src/digitalmodel/fatigue/sn_curves.py`): `digitalmodel/src/digitalmodel/fatigue/sn_curves.py`
- EXISTS (remote main): `digitalmodel/src/digitalmodel/fatigue/__init__.py`
- EXISTS (local, 391 lines): `digitalmodel/pyproject.toml`
- EXISTS (local): `digitalmodel/uv.lock`
- EXISTS (local, 15 test files): `digitalmodel/tests/fatigue/test_*.py`
- EXISTS (local): `digitalmodel/.github/workflows/quality-gates.yml`
- MISSING (this plan will create): `docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md`
- MISSING (this plan will create in digitalmodel): `tests/fatigue/test_package_imports.py` (smoke import regression test)

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

**Gap proofs**:
- `grep -n pylife digitalmodel/pyproject.toml` → no output → confirms pylife absent from deps.
- `grep -c pylife digitalmodel/uv.lock` → 0 → confirms pylife never resolved.
- `ls docs/plans/2026-04-21-issue-2441*` → "No such file or directory" → confirms no prior plan.
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

`digitalmodel/pyproject.toml` declares `pylife>=2.2,<3.0` as a runtime dependency, `uv.lock` is refreshed, a smoke import test guards `import digitalmodel.fatigue` against missing-dep regressions, and the `Quality Gates` workflow on `vamseeachanta/digitalmodel` main returns green on the first run after the fix lands.

---

## Approach — Path A (preferred) vs Path B (rejected)

The issue body describes two candidate fixes:

- **Path A (chosen): add `pylife` as a runtime dependency.** Rationale: (1) pylife is imported unconditionally at module load, (2) the existing docs (`docs/integrations/pylife-evaluation.md`) already recommend `pylife>=2.2` as a runtime dep, (3) fatigue analysis is a first-class digitalmodel capability — not an optional extra, (4) ten separate test modules depend on the import succeeding, indicating load-bearing runtime use. Cheapest, smallest, lowest-risk correct fix.
- **Path B (rejected): guard the import with `try/except ModuleNotFoundError`.** Rejected because this turns a core module into a silently-degraded one: `get_sn_curve`, `DNV_CURVES`, and all downstream fatigue functions would become `None` or stub-raising, 10 test modules would need `pytest.importorskip("pylife")`, and actual fatigue consumers would get deferred failures at call time instead of install time. The existing `OrcFxAPI` optional pattern is only appropriate for licensed/vendor-gated software, which pylife is not.

Trivial fix — no pseudocode required (T1). See `Files to Change` for exact deltas.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/pyproject.toml` | Add `"pylife>=2.2,<3.0",` to `[project.dependencies]` (alphabetically near `pykalman` / `pymssql`). |
| Regenerate | `digitalmodel/uv.lock` | Re-run `uv lock` after the pyproject change to pin pylife and its transitive graph (numpy/pandas/scipy already present — expected to be a pure add, not a bump). |
| Create | `digitalmodel/tests/fatigue/test_package_imports.py` | Smoke test asserting `import digitalmodel.fatigue` succeeds and exposes `get_sn_curve`, `DNV_CURVES`. Fails fast and clearly if pylife (or any other fatigue-package dep) is ever dropped again. |
| No change | `digitalmodel/src/digitalmodel/fatigue/sn_curves.py` | Intentional — Path A keeps the unguarded import. |
| No change | `digitalmodel/src/digitalmodel/fatigue/__init__.py` | Intentional. |
| No change | `digitalmodel/.github/workflows/quality-gates.yml` | The existing `UV_NO_SOURCES=true uv pip install -e .` install step will pick up the new dep automatically once pyproject declares it. |
| No change | `docs/plans/README.md` | Per task constraint — not updating the workspace-hub plan index in this draft. |

Scope constraint (HARD): this plan modifies **only** the digitalmodel repo plus this workspace-hub plan file. No changes outside those paths. No commits, no pushes, no staging, no label changes, no approval marker creation — plan-draft only.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_fatigue_package_imports` | `import digitalmodel.fatigue` succeeds without raising | (import statement) | no exception; module is not None |
| `test_fatigue_exports_get_sn_curve` | Public API `get_sn_curve` is re-exported from package init | `from digitalmodel.fatigue import get_sn_curve` | callable is not None |
| `test_fatigue_exports_dnv_curves` | Public API `DNV_CURVES` registry is re-exported | `from digitalmodel.fatigue import DNV_CURVES` | dict-like, non-empty |
| `test_pylife_woehlercurve_importable` | The exact third-party symbol used at `sn_curves.py:15` is resolvable | `from pylife.materiallaws.woehlercurve import WoehlerCurve` | class is not None; instantiable with minimal kwargs |

All four tests live in the new `tests/fatigue/test_package_imports.py` and must collect + run in under 2 seconds to keep the Quality Gates fail-fast loop tight.

Implementation order (after approval):
1. Write the four tests above; confirm they fail (or collect-error) in a clean venv without pylife installed.
2. Add `pylife>=2.2,<3.0` to `[project.dependencies]` in `digitalmodel/pyproject.toml`.
3. Run `uv lock` (or `uv sync`) in the digitalmodel repo to refresh `uv.lock`.
4. Run `uv run pytest tests/fatigue/test_package_imports.py -v` — all four pass.
5. Run full `uv run pytest tests/fatigue/ -v` — all 15 test modules collect cleanly.
6. Run full `uv run pytest tests/ -v -m "not solver"` — no regressions elsewhere.
7. Commit on a branch (digitalmodel repo), push, open PR, confirm Quality Gates workflow returns green.

---

## Acceptance Criteria

- [ ] `digitalmodel/pyproject.toml` `[project.dependencies]` contains `"pylife>=2.2,<3.0"`.
- [ ] `digitalmodel/uv.lock` contains at least one `pylife` entry (`grep -c pylife uv.lock` > 0).
- [ ] `uv run pytest tests/fatigue/test_package_imports.py -v` — all 4 new tests pass locally.
- [ ] `uv run pytest tests/fatigue/ -v` — no collection errors, no ModuleNotFoundError for pylife.
- [ ] `uv run pytest tests/ -v -m "not solver"` — full suite shows no regression vs. pre-change baseline (i.e. any non-fatigue failures that existed pre-change may persist but no new failures introduced).
- [ ] `Quality Gates` workflow run on `vamseeachanta/digitalmodel` main returns **success** on the first run after the fix commit lands.
- [ ] `gh run list --repo vamseeachanta/digitalmodel --branch main --status failure --limit 5` no longer shows the fix commit (or any subsequent push) in the failure list for the Quality Gates workflow.
- [ ] Adversarial-review artifacts posted to `scripts/review/results/2026-04-21-plan-2441-{claude,codex,gemini}.md` — zero MAJOR findings outstanding.
- [ ] Closeout comment posted to #2441 linking the merged PR + first green run URL.

---

## Adversarial Review Summary

PENDING — this is the initial draft (2026-04-21). Three-provider adversarial review (Claude + Codex + Gemini) has **not** yet run. Will be populated after `bash scripts/review/cross-review.sh docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md all --type plan` executes. No cross-review artifacts exist yet under `scripts/review/results/`.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING — not approval-ready until cross-review returns no MAJOR findings and user explicitly labels `status:plan-approved` with an accompanying marker.

---

## Risks and Open Questions

- **Risk — transitive dep bloat:** `pylife>=2.2` may pull a noticeable transitive graph (scipy, pandas, numpy are already in digitalmodel deps, so the incremental cost should be small, but verify during `uv lock`). Mitigation: inspect `uv.lock` diff post-change; if pylife pulls unexpected heavyweight deps (e.g. Jupyter / plotting extras), consider moving to an `[project.optional-dependencies].fatigue` extra and gating the fatigue subpackage import with a clearer error message.
- **Risk — version-upper-bound drift:** Upper bound `<3.0` is defensive — pylife may never ship 3.x, or may ship 3.x with backward-compatible `WoehlerCurve`. Safe default; revisit if pylife 3.x lands.
- **Risk — uv.lock merge conflicts:** Concurrent unrelated PRs on digitalmodel may touch `uv.lock`. Mitigation: rebase immediately before merge and re-run `uv lock` if needed.
- **Risk — governance-drift optics:** Issue #2441 already carries `status:plan-approved` label before this plan existed. This plan is draft-only; the label does not reflect an actually-reviewed plan. Governance comment (separate from this plan) flags the drift for user resolution.
- **Open — should `pylife-evaluation.md` be updated post-fix?** Its current phrasing is forward-looking ("Add pylife>=2.2 to digitalmodel's dependencies"). Low-priority follow-up; not blocking this plan.
- **Open — CI-level `pip install pylife` shortcut?** The Quality Gates workflow could add `uv pip install pylife` as a temporary hot-fix before `pyproject.toml` is updated. Rejected: hot-fixes in workflow YAML drift from declared deps and create the exact class of bug this plan is fixing. Fix it in `pyproject.toml` only.
- **Open — parent #2424 signal:** Closing this one red CI among the 7 ecosystem repos should update the parent meta-issue's tally. Post a cross-link comment on #2424 after #2441 closes.

---

## Complexity: T1

**T1** — single missing runtime dependency declaration, plus one small regression-guard test file. One-line pyproject change, auto-regenerated lockfile, four trivial smoke-import tests. No domain logic changes, no new module design, no multi-file refactor. Root cause is mechanically verified (remote main source + failing CI log + empty grep). Path A vs Path B decision is documented in-plan. Fits the T1 classification cleanly.
