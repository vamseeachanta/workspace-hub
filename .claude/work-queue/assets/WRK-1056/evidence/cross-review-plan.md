# WRK-1056 Cross-Review — Plan Phase

## Summary

| Provider | Verdict | Key Findings |
|----------|---------|--------------|
| Claude   | APPROVE | Minor: mypy via project venv, bats availability, --json flag |
| Codex    | MAJOR   | mypy execution model, test non-determinism, template scope, --structure out of scope |
| Gemini   | MINOR   | mypy isolation, central ruff config, pre-commit vs CI divergence |

## MAJOR Findings (Codex) — Resolution

1. **Mypy execution model** → FIXED: plan updated to `cd <repo> && uv run mypy src/`
   so each repo's project venv is used (correct dependency resolution)

2. **Test non-determinism** → FIXED: plan updated to use fixture temp dirs, not live repos

3. **Pre-commit template too broad** → FIXED: plan now specifies minimal ruff-only snippet,
   not a copy of digitalmodel

4. **--structure out of scope** → FIXED: removed from WRK-1056 plan; deferred to WRK-1058

## MINOR Findings (Gemini) — Deferred to WRK-1058/WRK-1060

- Central ruff.toml: good idea, captured as WRK-1060 gap discovery
- mypy as pre-push hook: valid, but out of scope for this WRK
- --json output: deferred to WRK-1058

## Result
All MAJOR findings addressed. Plan revised. Proceeding to Stage 7.
