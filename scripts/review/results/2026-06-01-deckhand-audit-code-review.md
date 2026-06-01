# Code review — Deckhand audit persistence (2026-06-01)

> Reviewer: Claude (main-session r1, inline). Subject: `src/deckhand/audit.py` + `tests/deckhand/test_audit.py` (codex TDD). Stage: code/artifact.

## VERDICT: APPROVE with one integration follow-up

Full deckhand suite **38/38 green** (verified independently). 

Strengths:
- **Redaction by construction.** `redacted_summary` emits an allowlist of safe fields only (total, allow/deny, deny-reason histogram, sensitivity buckets) — sensitive fields are never copied in, so leakage is structurally impossible rather than blocklist-dependent. Deny reasons are the engine's static strings (no repo names/ids), and are further replaced with `"redacted"` when `error_specifics` is in the policy redact list (it is).
- **Append-only + fail-closed.** `"a"` mode, never truncates; raises `OSError` on unwritable path (no silent drop). Deterministic JSON (`sort_keys`, compact). Injected `clock()` keeps tests deterministic.
- **PENDING/FINAL** via same `decision_id` (generated or passed); HTML renderer escapes via `html.escape`.

## Finding (follow-up → bundle into `t_7f640411` engine hardening)
- **MINOR (integration, privacy-safe):** `redacted_summary` buckets by `record["scope_sensitivity"]`, but the engine's audit record (`engine._decision`) does **not** emit that field — so against real engine output every row buckets as `"unknown"`. The audit tests inject `scope_sensitivity` manually, masking the gap. Fix in the engine-hardening pass: add `scope_sensitivity` (resolved scope's `sensitivity`) to the engine audit record, and add an **end-to-end** test (engine `decide()` → `audit.redacted_summary`) so the integration is covered, not just the two units. Privacy is intact today (over-buckets to "unknown", leaks nothing).

## Deferred (correct)
Audit-store path env-expansion + the actual write destination, rate-limit counters, and the `pre_tool_call` hook wiring belong to the live-wiring layer.
