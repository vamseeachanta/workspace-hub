# WRK-1056 Plan Review — Codex

**Reviewer:** Codex (gpt-5.4)
**Date:** 2026-03-09
**Verdict:** MAJOR

## Findings (must fix before Stage 7)

1. **Mypy execution model underspecified** — `uv tool run mypy <repo>/src --config-file pyproject.toml`
   from workspace root does not guarantee repo dependency resolution or import resolution.
   Fix: per-repo `cd` + `uv run mypy` inside each repo's own venv context.

2. **Test strategy non-deterministic** — "known-clean state" depends on live repo cleanliness.
   Fix: use fixture repos or command shims so exit-code aggregation is deterministic.

3. **Pre-commit template too broad** — "use digitalmodel as template" risks copying unrelated
   hooks. Fix: define a minimal ruff-only snippet for new .pre-commit-config.yaml files.

4. **--structure flag out of scope** — not in WRK-1056 acceptance criteria; weakens review trust.
   Fix: remove --structure from this plan; keep in WRK-1057/WRK-1058.

## Risks
- mypy may fail for environmental reasons, not real type errors
- Tests flaky against live workspace state
- New pre-commit files may inherit invalid local hooks
