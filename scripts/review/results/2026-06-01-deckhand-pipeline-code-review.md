# Code review — Deckhand dry-run pipeline (2026-06-01)

> Reviewer: Claude (main-session r1). Subject: `src/deckhand/pipeline.py` + `tests/deckhand/test_pipeline.py` (codex TDD). Stage: code/artifact (capstone).

## VERDICT: APPROVE

Full suite **146/146 green**. `evaluate()` composes hook→runtime→audit: hook denial short-circuits (audited, no execute); allow path runs `runtime.handle` with a `dry_run_executor` that performs no git/gh/shell and returns a safe "would_execute" summary. Config loads from the real `config/deckhand/` (repo-root resolved) or an in-memory dict.

**Verified independently against the committed config** (not just unit tests): every request to `acma` denies — `unknown operator` (empty `operators` ⇒ fail-closed), destructive forms deny earlier. The shipped config is safe-by-default; nothing can be authorized until an owner adds operator IDs.

## Notes (non-blocking)
- `dry_run_executor` imports no subprocess path — confirmed safe for a live external dry-run demo without PATs/gateway.
- The real `executor` (git/gh via the per-scope PAT) is the only remaining piece, and it is owner-gated (PAT provisioning).

## State of the pure core (complete)
engine (30) + audit (8) + runtime (5) + hook (96) + pipeline (7) = **146 tests**, all reviewed APPROVE. The Layer-2 hook was adversarially reviewed (~60 bypasses) and hardened fail-closed. Per-scope PAT remains the load-bearing boundary for anything the classifier can't enumerate.
