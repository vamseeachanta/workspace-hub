# Plan for #2566: Full CI and package validation for yaw and rudder-stock sweep workflows

> **Status:** plan-review — adversarial reviewed; awaiting user approval
> **Complexity:** T2
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2566
> **Review artifacts:** scripts/review/results/2026-04-30-plan-2566-claude.md | scripts/review/results/2026-04-30-plan-2566-codex.md | scripts/review/results/2026-04-30-plan-2566-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- `digitalmodel` commit `3609b7dca981de3c6213413ddd6b404920b56f29` contains both recently landed workflows:
  - `src/digitalmodel/naval_architecture/yaw_moment.py`
  - `src/digitalmodel/naval_architecture/rudder_stock_torque.py`
  - `src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml`
  - `src/digitalmodel/naval_architecture/data/rudder_stock_torque_typical_ship.yml`
- `tests/naval_architecture/test_yaw_moment_sweep.py` and `tests/naval_architecture/test_rudder_stock_torque_sweep.py` already include targeted package-data and smoke-style checks; #2566 expands the validation envelope, not the calculation formulas.
- `pyproject.toml` has package-data coverage for `digitalmodel = ["subsea/cross_sections/fixtures/*.yml", "naval_architecture/data/*.yml"]`, so this issue validates that distribution behavior from a clean package/install path.

### Standards
- Standards-derived formulas are not introduced by #2566. The relevant quality standard is the repo calculation citation contract:
  - `.claude/rules/calc-citation-contract.md`
  - `docs/standards/calc-output-citation.md`
- Engineering references are indirectly validated through the existing #2564/#2565 provenance outputs rather than changed.

### LLM Wiki pages consulted
- `knowledge/wikis/naval-architecture/wiki/concepts/yaw-moment-rudder-sweep.md` — identifies #2564 boundary and future maneuvering validation.
- `knowledge/wikis/naval-architecture/wiki/concepts/rudder-force-modeling.md` — current shared rudder-force model context.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-validation-metrics.md` — confirms turning-circle/IMO metrics are future simulation checks, not blockers for #2566.

### Documents consulted
- #2564 closeout: yaw-moment workflow landed and passed targeted validation.
- #2565 closeout: rudder-stock torque workflow landed, cross-reviewed, and closed.
- `pyproject.toml` lines around `[tool.setuptools.package-data]`, `[tool.pytest.ini_options]`, and `[tool.uv]` define package and test behavior to validate.

### Gaps identified
- No durable full-CI/package-validation report exists for the combined #2564/#2565 workflows.
- Targeted tests passed, but a fresh-checkout broad validation and install-from-wheel smoke are not yet archived.
- Full repo tests may expose unrelated failures; the plan must classify those without absorbing unrelated remediation.

### Evidence
- `git rev-parse HEAD origin/main` in `/mnt/local-analysis/digitalmodel-issue2565` returned matching `3609b7dca981de3c6213413ddd6b404920b56f29`.
- `pyproject.toml` line 219 includes `naval_architecture/data/*.yml` in package data.
- `tests/naval_architecture/test_rudder_stock_torque_sweep.py` contains wheel/package-data coverage around lines 180-207.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-30-issue-2566-full-ci-package-validation-yaw-rudder-stock.md` |
| Validation report | `digitalmodel/docs/validation/2026-04-30-yaw-rudder-stock-ci-package-validation.md` |
| Optional helper test | `digitalmodel/tests/naval_architecture/test_yaw_rudder_package_validation.py` |
| Plan review artifacts | `scripts/review/results/2026-04-30-plan-2566-*.md` |

---

## Deliverable

A durable validation report proving the #2564 yaw-moment and #2565 rudder-stock torque workflows pass an enumerated locally runnable CI-like gate set, package-data/clean-install validation, and smoke generation, with any unrelated failures classified into separate issues.

---

## Hard-stop / execution gate

This plan is review-only until approval. No #2566 implementation or validation-report file changes may begin until the adversarial plan-review artifacts are published, the issue is moved to `status:plan-review`, and the user explicitly approves / applies `status:plan-approved`.

---

## Pseudocode

```text
function run_validation_matrix():
    sync/fetch clean digitalmodel checkout at origin/main
    record environment: git SHA, uv version, python version
    discover actual local gate surfaces from pyproject/workflows before running them
    record chosen gate matrix and any skipped/infeasible gate with rationale
    run targeted tests for maneuverability/yaw/torque
    run package-data distribution test or wheel build/install smoke
    run ruff on changed naval_architecture modules/tests/docs helpers
    run smoke generation for yaw and rudder-stock sample YAMLs into /tmp
    run bounded CI-like gates, minimum: targeted suite + ruff + wheel/install smoke + sample generation
    if broader pytest/full-suite attempt fails, classify each failure as related/unrelated/unknown with evidence
    write durable markdown report with commands, versions, exit codes, artifacts, and follow-up issue candidates
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/docs/validation/2026-04-30-yaw-rudder-stock-ci-package-validation.md` | durable evidence report |
| Optional create | `digitalmodel/tests/naval_architecture/test_yaw_rudder_package_validation.py` | if a missing clean-install/package smoke needs executable regression coverage |
| Update | `docs/plans/README.md` | plan index |

---

## TDD / Validation List

| Test/check | What it verifies | Expected result |
|---|---|---|
| targeted naval architecture suite | #2564/#2565 regressions still green | pass |
| wheel build/install smoke | YAML package data survives distribution | pass |
| public import smoke | exported APIs work outside pytest path injection | pass |
| sample generation smoke | both workflows emit CSV/JSON/provenance/manifest/charts | pass |
| bounded CI-like gate | enumerated locally runnable gates discovered from repo config are run or explicitly skipped with rationale | pass, or failures classified related/unrelated/unknown |

---

## Acceptance Criteria

- [ ] Validation report exists at `docs/validation/2026-04-30-yaw-rudder-stock-ci-package-validation.md` in the `digitalmodel` repo and includes exact commands, git SHA, `python --version`, `uv --version`, exit status, and result for each step.
- [ ] Targeted command is run and exits 0: `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_maneuverability.py tests/naval_architecture/test_yaw_moment_sweep.py tests/naval_architecture/test_rudder_stock_torque_sweep.py -q`.
- [ ] Wheel or clean-install smoke proves both `yaw_moment_typical_ship.yml` and `rudder_stock_torque_typical_ship.yml` are readable via `importlib.resources` from an installed distribution.
- [ ] Smoke generation lists exact output families for each workflow: CSV table, JSON summary, provenance sidecar, artifact manifest, and configured PNG/HTML chart families.
- [ ] Any broader/full-suite failure is recorded in a report table with: failing command, failing test/module, related/unrelated/unknown classification, evidence excerpt, and follow-up issue number or `not filed`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Engineering reviewer | MINOR -> resolved | Reframed “full CI” as enumerated local CI-like gates; added gate discovery and causal-language cleanup. |
| Governance reviewer | MAJOR -> resolved | Added explicit hard stop, measurable report fields, exact targeted command, and failure classification schema. |
| Package/test reviewer | UNAVAILABLE | Subagent timed out; package/test findings from engineering/governance reviews were incorporated. |

**Overall result:** PASS after revisions; ready for user approval gate.

---

## Risks and Open Questions

- **Risk:** full repo tests may be too slow or have pre-existing unrelated failures; this issue will classify rather than overclaim, and broad failures do not automatically imply #2564/#2565 regression.
- **Risk:** local `uv run` can hang when syncing; use `UV_NO_SYNC=1` when appropriate and record that constraint.
- **Open:** if broad CI fails due unrelated debt, create exact follow-up issues with failure evidence.

---

## Complexity: T2

**T2** — validation/report artifact with possible small helper test; no formula/code expansion expected.
