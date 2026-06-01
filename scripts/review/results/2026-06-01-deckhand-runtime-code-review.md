# Code review — Deckhand runtime orchestration (2026-06-01)

> Reviewer: Claude (main-session r1, inline). Subject: `src/deckhand/runtime.py` + `tests/deckhand/test_runtime.py` (codex TDD). Stage: code/artifact.

## VERDICT: APPROVE

Full deckhand suite **43/43 green** (verified independently). `handle()` composes engine + audit cleanly: DENY → one audit record, no executor call; ALLOW → rate-limit (sliding 1h window per operator + per scope, duplicate-request suppression) → PENDING audit → executor → FINAL audit, sharing one `decision_id`.

Strengths:
- **No silent loss:** PENDING persisted before the executor runs; executor exceptions persist a FINAL error record then return `executed:False`.
- **Privacy-conscious:** results redacted by key-fragment blocklist; errors reduced to exception *type* only (no message → no secret/path leak).
- **Fail-closed rate limiting:** write events recorded only when every limit check passes; per-scope override merges over policy defaults.
- Injected executor/clock/rate_store keep it fully unit-testable with no git/gh/gateway.

## Notes (non-blocking, live-wiring)
- **Concurrency:** `rate_store` is mutated without locking — fine for a single-process gateway, but a multi-worker deployment needs a shared/atomic store. Document the single-writer assumption when wiring.
- **Config double-load:** `engine.decide` and `_rate_limits` each load config; harmless, optionally memoize at wiring.
- **Error detail:** only exception type is stored (privacy win); if deeper debugging is needed, the *raw* private store could carry more — keep it out of the redacted summary.

## Deferred (correct)
The real `executor` (git/gh via the scoped PAT) and the `pre_tool_call` hook + PATH shim are the next chunk; elevation TTL + engine `scope_sensitivity` remain on `t_7f640411`.
