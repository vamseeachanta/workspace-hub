# WRK-1056 Plan Review — Claude

**Reviewer:** Claude (Sonnet 4.6)
**Date:** 2026-03-09
**Route:** B (medium)

## Plan Summary

Create `scripts/quality/check-all.sh` that runs ruff + mypy across all 5 tier-1
repos, with per-repo config detection, `--fix`/`--repo`/`--ruff-only`/`--mypy-only`
flags, aggregate exit code, and pre-commit hook insertion where missing.
Add `--structure` flag for folder/file taxonomy validation.

## Verdict: APPROVE

## Strengths

1. Scope is well-bounded — medium complexity, single new script + pre-commit insertions
2. Repo path map correctly handles `OGManufacturing/` capitalisation
3. Config detection (pyproject.toml → `[tool.mypy]`) avoids duplicating existing settings
4. `uv tool run` invocation is consistent with workspace Python runtime rules
5. Pre-commit insertion distinguished from creation (assetutilities/assethold need new files)
6. Structure check complements existing `validate-file-placement.sh` without overlap

## Risks / Recommendations

1. **Mypy on OGManufacturing** — `--ignore-missing-imports` may hide real type errors;
   consider `--follow-imports=silent` instead for a cleaner baseline
2. **Ruff D-rules deferred** — correct call; enabling pydocstyle on zero-docstring repos
   would produce hundreds of warnings and obscure real linting signal
3. **Pre-commit file creation** — creating `.pre-commit-config.yaml` from scratch for
   assetutilities/assethold is a meaningful repo change; ensure it is tested
   (pre-commit --all-files dry-run) before committing
4. **bats vs pure bash tests** — bats may not be installed; plan should fall back to
   plain bash assert functions if bats unavailable

## Minor Suggestions

- Add `--json` output flag for CI consumption (can be Phase 2 / WRK-1058)
- Log tool versions (ruff, mypy) at top of report for reproducibility
