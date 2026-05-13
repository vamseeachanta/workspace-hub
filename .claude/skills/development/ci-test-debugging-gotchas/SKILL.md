---
name: ci-test-debugging-gotchas
version: 1.0.1
category: development
description: "Class-level CI/test/debugging gotchas: shell pipefail, stale pycache imports, lint restoration, GitHub Actions shell/platform quirks, and test-suite repair."
tags: [testing, ci, debugging, shell]
---

# Ci Test Debugging Gotchas

## When to Use
Use when tests or CI fail due to environment, shell, import cache, syntax/lint debt, cross-platform GitHub Actions drift, or broad assertion failures.

## Class-Level Workflow
1. Reproduce failure locally with the narrowest command that preserves the observed behavior.
2. For CI lint failures, inspect the workflow and run the exact CI commands locally (for example Black/isort/flake8 paths and flags), not just a nearby faster linter such as Ruff. A targeted `ruff check` pass does not prove a repo's Black/isort/flake8 CI gate is green.
3. Check shell semantics (`set -euo pipefail`, `grep -q`, pipes), platform shells, and cached imports before changing product code.
4. For large lint/test debt, restore gates incrementally with explicit baselines.
5. Use targeted test repair patterns when failures are assertion/schema drift rather than production regressions.
6. When GitHub Actions logs are noisy or include escaped JUnit XML, download artifacts (`gh run download <run-id> --dir /tmp/...`) and parse `*.xml` test result files with Python/XML instead of relying on grep. This quickly separates true failing test names/messages from enormous package lists or serialized XML noise.
6. If a broad test run times out with the log tail stopped at a generic scheduler/job smoke test, inspect whether `run(config={})` triggers live network refreshes or writes to checked-in data paths. Make empty-config smoke calls offline-safe (quick `skipped` result or explicit opt-in requirement) while preserving dedicated mocked adapter tests. See `references/offline-safe-scheduler-smoke-tests.md`.
7. For multi-repo CI readiness waves, do not stop at worker-reported test success. Reconcile every tier-1 repo from the control checkout: branch, local HEAD, origin HEAD, ahead/behind, dirty count, pushed commits, and intentional worktree/branch exceptions. Sanitize absolute machine-local paths in handoff artifacts before committing. See `references/multi-repo-ci-readiness-closeout.md`.

## CI Test Expectation Drift Gotchas
- Smoke/infrastructure tests often hard-require optional plugins (`pytest-html`, `pytest-json-report`, `pytest-xdist`) or a particular coverage invocation (`--cov=` in `pytest.ini`). Treat these as environment-contract checks: either install the plugin intentionally or relax tests to require only current CI-supported infrastructure and skip optional accelerators when absent.
- Numeric aggregation code that stores statistics in SQLite should coerce numpy/scalar values to plain Python types and clamp tiny negative floating-point variance before square root. Otherwise `variance ** 0.5` can create complex values that fail SQLite binding only in full CI-scale test runs.
- If a test explicitly asserts a historical bug still exists (e.g., expects a `RuntimeError` from dict mutation), update it to assert the fixed behavior once production code is corrected; don't preserve bug-existence assertions in CI recovery branches.
- When hardening export/adapter code so invalid or empty payloads fail instead of producing empty successful artifacts, first inventory all valid caller/test schemas before adding the guard. Preserve compatibility aliases for legacy and current key names (for example `well_data` vs `production_data`, `economic_metrics` vs `economic_data`, `verification_metadata` vs `verification_data`) and validate both the negative invalid-data test and the positive export path in the same bounded regression.
- When CI failures appear after a package/module split, treat legacy compatibility as a first-class CI contract before changing tests. Restore deep import namespaces and monkeypatch targets with tiny wrapper modules (for example `old.namespace.module` re-exporting the new canonical module plus patch-only symbols), and restore legacy method/constructor aliases where downstream tests/callers still target them. Validate the exact failing selectors plus a bounded regression around the refactored package before pushing.
- For compatibility modules that re-export split implementations, remember tests may patch names on the wrapper module itself. Import and route through the wrapper-level objects (`go`, `html`, `dcc`, `Input`, `Output`, etc.) when necessary so monkeypatches affect the code under test, then run lint/formatter gates because these shim imports can easily trigger ordering or unused-import failures.
- Tiny compatibility wrappers that intentionally import symbols only for legacy import/monkeypatch paths often need explicit lint annotations on the import lines (`# noqa: F401` for re-export-only imports and `# noqa: F401,F403` for intentional wildcard re-exports). Validate the exact CI lint command locally after adding the shim; if the repo does not expose `flake8` in the current environment but CI installs it, use `uv run --with flake8 flake8 <paths> ...` to mirror the CI gate without editing dependencies.
- When a legacy unit test patches a module-level handle (for example `pkg.module.production_from_zip`) but the class under test captures the real object in `__init__`, adding the missing module attribute is not enough: fixtures may instantiate the class before `@patch(...)` applies, so calls still hit the real implementation. Preserve the patchable module-level compatibility handle and route method calls through that handle dynamically (or through a property that reads it at call time). See `references/legacy-monkeypatch-handle-compatibility.md`.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
## Absorbed Narrow Skills (2026-04-29)

### `diagnose-stale-pycache-import-mismatch`

- Former skill demoted to `references/diagnose-stale-pycache-import-mismatch.md`.
- Preserved insight: Diagnose Python ImportError cases where a symbol cannot be imported even though the source file already defines it; verify live source, interpreter/venv selection, clear stale __pycache__, and rerun targeted imports/tests.

### `github-actions-cross-platform-validation-gotchas`

- Former skill demoted to `references/github-actions-cross-platform-validation-gotchas.md`.
- Preserved insight: Execution-time GitHub Actions pitfalls discovered while fixing cross-platform CI workflows — path-filter non-triggers, Windows shell parsing mismatches, and job-scoped validation.

### `github-actions-trigger-and-shell-gotchas`

- Former skill demoted to `references/github-actions-trigger-and-shell-gotchas.md`.
- Preserved insight: Prevent false verification gaps in GitHub Actions by checking push path filters, shell compatibility, and shared CI environment failures before concluding a workflow fix worked or failed.

### `large-lint-gate-restoration-wave`

- Former skill demoted to `references/large-lint-gate-restoration-wave.md`.
- Preserved insight: Restore a red repository Lint job when flake8 debt is large and mixed, by inventorying outliers, splitting issue ownership, using local direct-venv iteration, inspecting broad auto-format diffs, and closing only after exact local and GitHub Actions Lint proof.

### `pipefail-grep-q-sigpipe-guard`

- Former skill demoted to `references/pipefail-grep-q-sigpipe-guard.md`.
- Preserved insight: Diagnose and fix false negatives caused by `grep -q` short-circuiting upstream producers under `set -euo pipefail`.

### `test-fixer`

- Former skill demoted to `references/test-fixer.md`.
- Preserved insight: Safe workflow for fixing bulk test assertion failures in existing test suites — collection errors mask deeper problems, replace_all corrupts, fix source first then tests

### `test-suit-repair-pattern`

- Former skill demoted to `references/test-suit-repair-pattern.md`.
- Preserved insight: Systematically fix failing tests in a test suite — root cause analysis, targeted patches, regression verification, and documentation.

### `blender-worktree-test-hardening`

- Former skill demoted to `references/blender-worktree-test-hardening.md`.
- Preserved insight: Recover and harden digitalmodel Blender automation work in isolated worktrees when uv/editable dependency paths break and local machines lack a Blender executable.

### `digitalmodel-worktree-test-execution-with-shared-venv`

- Former skill demoted to `references/digitalmodel-worktree-test-execution-with-shared-venv.md`.
- Preserved insight: Run digitalmodel tests from isolated worktrees without uv editable-dependency failures by using the main repo's existing virtualenv and PYTHONPATH.

### `orcaflex-reporting-fixture-proof-pattern`

- Former skill demoted to `references/orcaflex-reporting-fixture-proof-pattern.md`.
- Preserved insight: Build and extend fixture-backed OrcaFlex reporting proof paths in digitalmodel using stable metadata baselines, normalized HTML snapshots, and reusable reporting test helpers.
