# Code review — Deckhand scope decision engine (2026-06-01)

> Reviewer: Claude (main-session r1, inline). Subject: `src/deckhand/engine.py` + `tests/deckhand/test_scope_decision_engine.py` (codex TDD build). Stage: code/artifact (post plan-approved #2931).

## VERDICT: APPROVE with minor follow-ups

30/30 tests pass (verified independently: `pytest tests/deckhand/ -q`). The engine is pure (no git/gh/network), fail-closed, and implements the POC Diagram 2 decision tree: config-load failure → deny, kill switches, known-operator, scope resolution (named + origin-bound-via-binding-only, never prose), per-scope operator authZ, destructive deny, repo-allowlist (incl. `owner:*/*` glob), read-only repo flags, diff-risk gate with elevation, reply-visibility, and a full audit record on every decision.

## Findings

- **MINOR (fixed):** `_diff_risk_reason` ignored `diff_risk_gate.enabled`. Now returns no-risk when disabled (default True). 
- **MINOR (follow-up — fail-closed-safe):** `_is_internal_operator` uses `elevation.approvers` as the "internal operator" set for the `external_disabled` (ecosystem) check. Not exploitable — the per-scope `operators` check still denies (`ecosystem.operators` is empty), so an approver who is not in `ecosystem.operators` is denied anyway — but the proxy is semantically wrong. Fix at live-wiring: define internal operators explicitly (scope `operators` or a dedicated internal group), drop the approvers proxy.
- **MINOR (follow-up — live-wiring):** `_valid_elevation` checks approver membership only; no TTL/evidence (the pure engine has no clock). Enforce `elevation.grant_ttl_seconds` + `evidence_required` in the stateful layer that wraps the engine.

## Not in scope of this engine (correctly deferred)
Rate-limit counters (stateful), audit persistence, the `pre_tool_call` hook + PATH shim, and per-scope PAT binding — all separate board tasks.
