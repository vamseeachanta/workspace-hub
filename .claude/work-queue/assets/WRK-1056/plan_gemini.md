# WRK-1056 Plan Review — Gemini

**Reviewer:** Gemini
**Date:** 2026-03-09
**Verdict:** MINOR

## Risks / Gaps

1. **Mypy environment isolation** — `uv tool run mypy` runs in an isolated env; third-party
   imports will silently degrade to Any without repo deps installed.
   Fix: use `uv run mypy` inside each repo root so the project venv is used.

2. **No central ruff config** — defaults may be inconsistent across 5 repos.
   Suggestion: create a workspace-root ruff.toml as the baseline.

3. **Pre-commit vs CI divergence** — ruff in pre-commit, mypy only in script/CI.
   Suggestion: add mypy as a pre-push hook (slow, so not pre-commit).

4. **Structure check rigidity** — enforcing src/ layout may break flat-layout repos.
   Suggestion: make structure checks warnings not failures for legacy repos.

## Improvements

- Use `uv run mypy` (repo venv) not `uv tool run mypy` (isolated tool env)
- Create workspace ruff.toml for consistent baseline across repos
- Pin same ruff version in pre-commit hooks as used by uv tool run
- Add `--json` output flag for CI integration
