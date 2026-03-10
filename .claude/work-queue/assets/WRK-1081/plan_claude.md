# WRK-1081 Plan Review — Claude

## Summary
Extend check-all.sh with bandit (security), radon (complexity), vulture (dead code) across
5 tier-1 repos. Baseline YAML gates new violations. Pre-commit gets bandit on staged files.

## Assessment: APPROVE

### Strengths
1. Baseline-gating approach correctly avoids day-1 CI breakage on existing violations
2. Consistent `uv tool run` invocation pattern (same as ruff) — no new tool install friction
3. radon/vulture warn-only initially is pragmatic — avoids blocking on legacy complexity
4. Staged-files-only for pre-commit bandit keeps commit speed acceptable
5. TDD-first with 6 targeted tests covering all key behaviors

### Risks / Notes
1. `bandit -ll` includes LOW severity in output — the `run_bandit()` function must parse
   severity levels and only exit 1 for MEDIUM+. Parsing logic needs careful implementation.
2. Baseline capture must run at plan-time (not commit-time) to snapshot current state.
   If baseline is regenerated later, old violations may be re-gated in.
3. `[tool.radon]` in pyproject.toml is non-standard — radon reads `.radon.cfg` or CLI flags.
   Recommend using `.radon.cfg` per repo or passing threshold via CLI argument instead.
4. vulture has known false positives on `__all__` exports and pytest fixtures — the .bandit
   equivalent for vulture is a whitelist file (`vulture_whitelist.py`). Consider adding one.

### Recommendations
- Use `bandit -ll -f json` for machine-parseable output to simplify severity filtering
- Add `vulture_whitelist.py` stub per repo (empty initially) consistent with `.bandit`
- Confirm radon config mechanism before Phase 3 (CLI flag vs config file)

### Verdict: APPROVE with minor notes
