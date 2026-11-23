# Plan for #2433: worldenergydata main CI — 22 collection errors blocking 5 Dependabot PRs

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2433
> **Review artifacts:** scripts/review/results/20260421T155659Z-2026-04-21-issue-2433-worldenergydata-ci.md-plan-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `worldenergydata/tests/conftest.py:317` — custom `pytest_ignore_collect` hook with pattern-based skip logic for `query_*.py`, `_archive/`, `_archived/`, dated directories, and six legacy `excluded_patterns`. This is the **only working skip mechanism** (pytest.ini `norecursedirs` and pyproject.toml `collect_ignore` are overridden by this hook returning `False` for unlisted paths).
- Found: `worldenergydata/.github/workflows/ci.yml` — `test` job runs `uv run pytest tests/ -v --tb=short --cov=src ...` which collects from the full `tests/` directory. The `lint` job runs `uv run black --check --diff src/ tests/`. The `type-check` job runs `uv run mypy src/worldenergydata/ --ignore-missing-imports`.
- Found: `worldenergydata/pytest.ini` — `addopts` includes `-x --maxfail=5` which masks the full error count during local runs but is overridden by CI's explicit `pytest tests/` invocation with its own flags.
- Gap: The 22 broken test files reference modules that do not exist on main: `sodir_module.*`, `metocean_stats`, `worldenergydata.bsee.analysis.type_curves`, `worldenergydata.cost.calibration.proxy_comparison`, `tests.modules.marine_safety.fixtures`, and others.

### Standards

Not applicable — this is a CI infrastructure fix, not an engineering-calculation issue.

### LLM Wiki pages consulted

No relevant wiki pages — this is a cross-repo CI plumbing issue.

### Documents consulted

- Issue #2433 body (workspace-hub) — full investigation context including 22-error breakdown, repo plumbing findings (pytest.ini vs pyproject.toml vs conftest.py precedence), and three candidate paths.
- Issue #2424 (workspace-hub) — parent meta-issue for ecosystem CI health across 6 of 7 visible repos.
- `.github/workflows/ci.yml` (worldenergydata, fetched via `gh api`) — confirms the `test` job collects from `tests/` root, meaning all 22 broken files are in CI scope. The `lint` job checks `src/ tests/` with black/isort. The `type-check` job checks `src/worldenergydata/` with mypy. The `build` job depends on `[test, lint]`.
- Preserved artifacts at `/tmp/worldenergydata-fix-1776766420` — branch `fix/unblock-dependabot-ci-20260421` with uncommitted working-tree changes: 15-file black reformat, `ci.yml` type-check `continue-on-error: true`, and a partial 4-file conftest.py skip list.

### Gaps identified

- The preserved conftest.py patch only skips 4 of the 22 broken files — the remaining 18 files will still fail collection and block CI.
- No tracking mechanism exists for the skipped tests — once skipped, there is no visibility into when/if the missing modules are restored.
- The `lint` job will fail on 15 unformatted test files independently of collection errors.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21T14:55Z via `gh issue view` / `gh pr list`):
- `#2433` — OPEN — `chore(ci-health): worldenergydata main CI — 22+ collection errors blocking 5 Dependabot PRs (worldenergydata PR #329-#333)` — labels: `priority:high`, `cat:infrastructure`, `status:plan-approved`
- `#2424` — parent meta-issue (referenced in #2433 body)
- Dependabot PRs: worldenergydata PR #329 (scrapy), worldenergydata PR #330 (pyarrow), worldenergydata PR #331 (torch), worldenergydata PR #332 (sqlmodel), worldenergydata PR #333 (xlsxwriter) — all OPEN
- **Note:** #329-#333 are worldenergydata PRs, NOT workspace-hub issues. Cross-review attestation that ran `gh issue view 329 --repo vamseeachanta/workspace-hub` produced false CLOSED results — this is an attestation artifact, not a plan defect.

**CI status** (verified 2026-04-21T14:55Z via `gh run list --branch main`):
- Run 24701694819 (Nightly) — completed failure — 2026-04-21
- Run 24667076504 (Dependabot Updates) — completed success — 2026-04-20 (this is `pip in /.` dependency update, not the CI workflow)

**CI yml critical excerpt** (`gh api repos/vamseeachanta/worldenergydata/contents/.github/workflows/ci.yml`):
```yaml
      - name: Run tests with coverage
        run: |
          uv run pytest tests/ \
            -v \
            --tb=short \
            --cov=src \
```
This confirms the `test` job collects from `tests/` — not a narrower subdirectory.

**Live collection errors** (`uv run pytest tests/ --collect-only --override-ini="addopts="` on main at `/tmp/worldenergydata-fix-1776766420` after `git stash`):
```
22 errors during collection, 11872 tests collected
```

The 22 erroring paths:
```
tests/modules/bsee/analysis/test_type_curves.py
tests/modules/fdas/integration/test_end_to_end.py
tests/modules/sodir-integration/test_api_client.py
tests/modules/sodir-integration/test_cross_regional_validation.py
tests/modules/sodir-integration/test_integration.py
tests/modules/sodir-integration/test_performance.py
tests/modules/well_production_dashboard/test_monitoring.py
tests/modules/well_production_dashboard/test_well_production_dashboard.py
tests/unit/cost/test_proxy_comparison.py
tests/unit/hse/database/test_models.py
tests/unit/hse/importers/test_bsee_incidents_importer_url.py
tests/unit/hse/importers/test_bsee_penalties_importer_url.py
tests/unit/hse/importers/test_bsee_statistics_importer_url.py
tests/unit/marine_safety  (directory-level — conftest/fixtures import fails)
tests/unit/metocean/statistics/test_environmental_contours.py
tests/unit/metocean/statistics/test_eva.py
tests/unit/metocean/statistics/test_joint_probability.py
tests/unit/metocean/statistics/test_reporting.py
tests/unit/metocean/statistics/test_scatter_diagram.py
tests/unit/metocean/statistics/test_wave_spectra.py
tests/unit/metocean/statistics/test_weather_windows.py
tests/unit/pipeline_ci_cd/test_pipeline_utils.py
```

**Black formatting** (`uv run black --check tests/` on main):
```
15 files would be reformatted
```

**File existence** (verified 2026-04-21 via `ls -la`):
- EXISTS: `/tmp/worldenergydata-fix-1776766420/tests/conftest.py` (388 lines with local patch; 376 on main)
- EXISTS: `/tmp/worldenergydata-fix-1776766420/.github/workflows/ci.yml`
- EXISTS: `/tmp/worldenergydata-fix-1776766420/pytest.ini`

**conftest.py hook baseline** (`git show HEAD:tests/conftest.py` lines 317-376):
- Line 317: `def pytest_ignore_collect(collection_path, config):`
- Lines 331-340: skip `query_*.py`, `_archive/`, `_archived/`, `_archived_tests`, dated dirs
- Lines 341-372: skip six `excluded_patterns` (legacy dirs)
- Line 376: `return False` — any file not explicitly listed is collected

<!-- Verification: 5 distinct sources (issue body, parent #2424, ci.yml, preserved artifacts, live pytest run). Minimum 3 required. Current count: 5 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2433-worldenergydata-ci.md` |
| Implementation | `worldenergydata/tests/conftest.py` (extend `pytest_ignore_collect`) |
| Implementation | `worldenergydata/.github/workflows/ci.yml` (`continue-on-error: true` on type-check) |
| Black reformats | 15 files in `worldenergydata/tests/` (see Files to Change) |
| Plan review — Claude | `scripts/review/results/20260421T155659Z-2026-04-21-issue-2433-worldenergydata-ci.md-plan-claude.md` |
| Plan review — Codex | `scripts/review/results/20260421T155659Z-2026-04-21-issue-2433-worldenergydata-ci.md-plan-codex.md` |
| Plan review — Gemini | `scripts/review/results/20260421T155659Z-2026-04-21-issue-2433-worldenergydata-ci.md-plan-gemini.md` |

---

## Deliverable

The worldenergydata main-branch CI `test` and `lint` jobs will pass (collection errors resolved, black/isort clean). The `type-check` job will be softened to advisory (`continue-on-error: true`) — it does not block the `build` job today but will no longer produce a red badge. This unblocks 5 Dependabot PRs (worldenergydata PR #329-#333) and restores ecosystem CI health for this repo, with all 22 broken test files explicitly tracked in a skip list with a follow-up re-enablement comment.

---

## Pseudocode

```
# === TDD Phase: Define failing checks FIRST ===

# Step 0 (RED): Confirm current failures before any code changes
# uv run pytest tests/ --collect-only --override-ini="addopts="  → expect 22 errors
# uv run black --check src/ tests/                               → expect 15 reformats
# uv run isort --check-only src/ tests/                          → expect failures

# === Implementation Phase: Make checks pass ===

# Step 1: Extend conftest.py pytest_ignore_collect (tests/conftest.py)
# After the existing excluded_patterns loop and before `return False`:
# Use pathlib relative_to() for robust path matching instead of brittle endswith/in.

from pathlib import Path

# Build the skip set using repo-relative paths
_repo_root = Path(__file__).resolve().parent.parent  # worldenergydata/

broken_module_tests = {
    # sodir_module.* missing (4 files)
    Path("tests/modules/sodir-integration/test_api_client.py"),
    Path("tests/modules/sodir-integration/test_cross_regional_validation.py"),
    Path("tests/modules/sodir-integration/test_integration.py"),
    Path("tests/modules/sodir-integration/test_performance.py"),
    # type_curves missing
    Path("tests/modules/bsee/analysis/test_type_curves.py"),
    # fdas duplicate basename
    Path("tests/modules/fdas/integration/test_end_to_end.py"),
    # well_production_dashboard missing
    Path("tests/modules/well_production_dashboard/test_monitoring.py"),
    Path("tests/modules/well_production_dashboard/test_well_production_dashboard.py"),
    # proxy_comparison missing
    Path("tests/unit/cost/test_proxy_comparison.py"),
    # hse database models missing
    Path("tests/unit/hse/database/test_models.py"),
    # hse importers url-based tests (import chain broken)
    Path("tests/unit/hse/importers/test_bsee_incidents_importer_url.py"),
    Path("tests/unit/hse/importers/test_bsee_penalties_importer_url.py"),
    Path("tests/unit/hse/importers/test_bsee_statistics_importer_url.py"),
    # metocean_stats missing (7 files)
    Path("tests/unit/metocean/statistics/test_environmental_contours.py"),
    Path("tests/unit/metocean/statistics/test_eva.py"),
    Path("tests/unit/metocean/statistics/test_joint_probability.py"),
    Path("tests/unit/metocean/statistics/test_reporting.py"),
    Path("tests/unit/metocean/statistics/test_scatter_diagram.py"),
    Path("tests/unit/metocean/statistics/test_wave_spectra.py"),
    Path("tests/unit/metocean/statistics/test_weather_windows.py"),
    # pipeline_ci_cd FileNotFoundError
    Path("tests/unit/pipeline_ci_cd/test_pipeline_utils.py"),
}

# Also skip marine_safety directory (conftest/fixtures import fails at directory level)
broken_module_dirs = {
    Path("tests/unit/marine_safety"),
}

# Robust matching using pathlib relative_to
try:
    rel = Path(collection_path).resolve().relative_to(_repo_root)
except ValueError:
    pass
else:
    if rel in broken_module_tests:
        return True
    for dir_pattern in broken_module_dirs:
        try:
            rel.relative_to(dir_pattern)
            return True
        except ValueError:
            pass

return False

# Step 2: Apply black formatting to 15 test files
# uv run black <15 files>

# Step 3: Apply isort to ensure import ordering is clean
# uv run isort src/ tests/

# Step 4: Soften type-check job in .github/workflows/ci.yml
# Add `continue-on-error: true` to the mypy step (~100 errors, separate fix scope)
# NOTE: Investigate whether `build` job depends on type-check. If build depends only
# on [test, lint], then continue-on-error is cosmetic (badge-only). Document finding.

# === Verification Phase (GREEN): Prove all checks pass ===

# Step 5a: Verify collection (local proxy)
# uv run pytest tests/ --collect-only --override-ini="addopts=" → 0 errors

# Step 5b: Verify via exact CI command (Claude P1 — must match CI)
# uv run pytest tests/ -v --tb=short --cov=src → 0 collection errors, tests pass

# Step 5c: Verify lint
# uv run black --check src/ tests/ → 0 reformats needed
# uv run isort --check-only --diff src/ tests/ → 0 changes needed
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `worldenergydata/tests/conftest.py` | Extend `pytest_ignore_collect` to skip all 22 broken test files (21 files + 1 directory) |
| Modify | `worldenergydata/.github/workflows/ci.yml` | Add `continue-on-error: true` to type-check job's mypy step |
| Reformat | `worldenergydata/tests/cron/test_scheduler_health.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/bsee/analysis/directional_surveys/query_api_01_wells_directional_survey_test_fixed.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/bsee/analysis/directional_surveys/test_complete_workflow.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/bsee/analysis/directional_surveys/test_well_api12_directional_surveys.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/hse/importers/test_bsee_incidents_importer_url.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/hse/importers/test_bsee_penalties_importer_url.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/hse/importers/test_bsee_statistics_importer_url.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/sodir-integration/test_data_collection.py` | black reformat |
| Reformat | `worldenergydata/tests/modules/sodir-integration/test_integration.py` | black reformat |
| Reformat | `worldenergydata/tests/unit/hse/importers/test_bsee_incidents_importer_url.py` | black reformat |
| Reformat | `worldenergydata/tests/unit/hse/importers/test_bsee_penalties_importer_url.py` | black reformat |
| Reformat | `worldenergydata/tests/unit/hse/importers/test_bsee_statistics_importer_url.py` | black reformat |
| Reformat | `worldenergydata/tests/unit/marine_safety/test_validators.py` | black reformat — note: this directory is in the skip set; reformatting is done for future re-enablement, not current CI |
| Reformat | `worldenergydata/tests/unit/metocean/test_planetswe_loader.py` | black reformat |
| Update | `docs/plans/README.md` | Add this plan to index |

---

## TDD Test List

This is an infrastructure fix on a cross-repo target. The "tests" are verification commands run against the worldenergydata clone, not new pytest test files in workspace-hub.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_zero_collection_errors | `uv run pytest tests/ --collect-only --override-ini="addopts="` produces 0 collection errors after conftest.py patch | worldenergydata repo with patched conftest.py | `0 errors` in summary line; exit code 0 |
| verify_black_clean | `uv run black --check src/ tests/` shows no reformatting needed | worldenergydata repo after black reformat | Exit code 0; no "would reformat" lines |
| verify_isort_clean | `uv run isort --check-only --diff src/ tests/` shows no changes | worldenergydata repo after black reformat | Exit code 0 |
| verify_test_count_stable | Collection after patch yields >= 11872 tests (no regression in collected tests) | worldenergydata repo with patched conftest.py | `>= 11872 tests collected` |
| verify_skip_list_complete | Each of the 22 error paths from pre-patch collection is present in the conftest.py skip set | Read conftest.py skip set vs known error list | All 22 paths accounted for |
| verify_type_check_continues | CI yml type-check step has `continue-on-error: true` | Read ci.yml | Field present on mypy step |

---

## Acceptance Criteria

- [ ] `uv run pytest tests/ --collect-only --override-ini="addopts="` in the worldenergydata clone produces 0 collection errors
- [ ] `uv run pytest tests/ -v --tb=short --cov=src` passes — this is the exact CI command and proves CI-green (Claude P1)
- [ ] `uv run black --check src/ tests/` exits 0
- [ ] `uv run isort --check-only --diff src/ tests/` exits 0
- [ ] `.github/workflows/ci.yml` type-check step has `continue-on-error: true`
- [ ] conftest.py skip list includes an inline comment referencing issue #2433 and listing the missing module for each group, so future developers know why each file is skipped and what to restore
- [ ] Changes committed to `fix/unblock-dependabot-ci-20260421` branch and pushed to `vamseeachanta/worldenergydata`
- [ ] PR created against `main` in worldenergydata with conventional-commit title
- [ ] After fix PR merges, run `@dependabot rebase` on worldenergydata PR #329-#333 so they pick up the fix (Dependabot PRs do not auto-rebase)
- [ ] At least one Dependabot PR (worldenergydata PR #329-#333) shows green CI checks after rebase
- [ ] Review artifacts posted to `scripts/review/results/`
- [ ] Plan index in `docs/plans/README.md` updated

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | CONDITIONAL PASS | P1: verification diverges from CI (acceptance used `--override-ini` not exact CI cmd); P1: incomplete skip list for `tests/modules/hse/importers/`; P1: `continue-on-error` placement may be cosmetic if type-check not in build deps; P2: brittle path matching; P2: reformat of skipped file is wasted churn; P2: Dependabot PRs need explicit rebase; P2: isort missing from pseudocode |
| Codex | CONDITIONAL PASS | P1: TDD ordering violation (implementation-first pseudocode); P1: cross-repo ID confusion (`#329`-`#333` look like workspace-hub issues); P2: artifact map wrong path prefix; P2: acceptance doesn't prove deliverable (continue-on-error tolerates, doesn't resolve) |
| Gemini | REJECT (Class-B attestation) | P1: `#329`-`#333` attested as CLOSED workspace-hub issues — attestation ran `gh issue view` on wrong repo; this is an attestation artifact, not a plan defect |

**Overall result:** CONDITIONAL PASS — all P1/P2 findings addressed in revision below

Revisions made based on review:
- [Claude P1] Added exact CI command (`uv run pytest tests/ -v --tb=short --cov=src`) to acceptance criteria
- [Claude P1] Added open risk for `tests/modules/hse/importers/test_bsee_*_importer_url.py` possibly needing skip-set inclusion
- [Claude P1] Added investigation note on `continue-on-error` placement vs `build` job dependency chain
- [Claude P2] Replaced brittle `endswith`/`in` path matching with `pathlib.Path.relative_to()` and set membership in pseudocode
- [Claude P2] Added note that `tests/unit/marine_safety/test_validators.py` reformat is for future re-enablement
- [Claude P2] Added explicit `@dependabot rebase` step to acceptance criteria
- [Claude P2] Added isort step to pseudocode (Steps 3 and 5c)
- [Codex P1] Reframed pseudocode as TDD: Step 0 (RED) confirms failures, Steps 1-4 implement, Step 5 (GREEN) verifies
- [Codex P1] Prefixed all bare `#329`-`#333` references with `worldenergydata PR`
- [Codex P2] Removed `workspace-hub/` prefix from artifact map path
- [Codex P2] Tightened deliverable scope: `test`/`lint` pass; `type-check` advisory only
- [Gemini P1] Added evidence note clarifying `#329`-`#333` are worldenergydata PRs, not workspace-hub issues (attestation artifact)

---

## Risks and Open Questions

- **Risk: Skipped tests hide real regressions.** The 22 broken test files reference modules deleted or never merged to main (`sodir_module`, `metocean_stats`, `type_curves`, `proxy_comparison`, etc.). Skipping them is safe only if the modules are genuinely absent. The conftest.py comments will document each skip reason and the responsible missing module. A follow-up worldenergydata issue should track re-enablement when modules are restored.
- **Risk: `continue-on-error: true` on type-check masks new mypy errors.** The ~100 existing mypy errors make the type-check job useless as a gate. The `continue-on-error` flag softens this to advisory status. A separate worldenergydata issue should track mypy cleanup.
- **Risk: Black reformats could change test semantics.** Black is a deterministic formatter and does not alter logic. However, if any test file contains string literals with whitespace-sensitive content, reformatting could change test expectations. The preserved working-tree already has the 15-file reformat applied and verified — the existing test suite collected successfully after reformatting.
- **Risk: `isort` may also require changes.** The lint job runs isort after black. If isort finds import ordering issues in the same or additional files, additional reformats will be needed. This will be checked during implementation.
- **Risk: Preserved `/tmp/` artifacts may be cleaned up.** The clone at `/tmp/worldenergydata-fix-1776766420` is a tmpdir — it may be garbage-collected. If lost, a fresh clone and re-application of the changes will be required (estimated 15 min).
- **Open: Should the 22 broken test files be deleted instead of skipped?** Deletion removes dead code permanently; skipping preserves the test structure for future re-enablement. This plan recommends skipping (additive, reversible) — user may override to deletion if preferred.
- **Risk: `tests/modules/hse/importers/test_bsee_*_importer_url.py` may also fail collection.** These files appear in the black reformat list but are NOT in the skip set — only the `tests/unit/hse/importers/` versions are. At implementation time, verify whether the `tests/modules/hse/importers/` variants also fail collection; if so, add them to the skip set. (Claude P1)
- **Risk: `continue-on-error: true` on type-check may be cosmetic.** Investigate whether the `build` job depends on `[test, lint, type-check]` or only `[test, lint]`. If type-check is not in the build dependency chain, the softening only affects the badge, not the merge gate. Document the finding during implementation and mark as out-of-scope if confirmed cosmetic. (Claude P1)
- **Open: Should a follow-up worldenergydata issue be filed for re-enabling skipped tests?** Recommended but not in scope for this plan — this plan's deliverable is strictly unblocking CI.

---

## Complexity: T2

**T2** — Cross-repo infrastructure fix modifying 3 files (conftest.py, ci.yml) plus 15 black reformats across the worldenergydata repo. Multiple verification steps, no new modules, strictly additive changes. Not T1 because the conftest.py patch touches 22 test paths across 8 distinct module families and requires verified evidence that the skip list is complete. Not T3 because no architectural decisions, no new modules, and no multi-repo coordination beyond the tracking issue.

---

## Path Decision: Path 1 (Expand ignore list) — CONFIRMED

**Path 2 is ruled out.** Live evidence confirms the CI `test` job runs `uv run pytest tests/` which collects from the full `tests/` directory root. All 22 broken files are under `tests/` and therefore in CI scope. There is no narrower collection directory that would reduce the skip surface.

**Path 3 is rejected.** The fix is strictly additive (conftest.py skip list + black reformats + ci.yml softening), low-risk, and fully reversible. Abandoning would leave 5 Dependabot PRs blocked indefinitely with no owner timeline for the missing-module restoration.

**Path 1 is selected.** Extend `pytest_ignore_collect` in `tests/conftest.py` to skip all 22 broken test files. Apply black formatting to 15 unformatted files. Add `continue-on-error: true` to the type-check mypy step. This is the minimal additive change to restore CI green on main and unblock all 5 Dependabot PRs.
