---
name: crossprovider hermes plan-review-fanout-timeout-and-trust-workspace-d
description: Plan-review fanout timeout and trust-workspace defaults
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [fanout, provider-integration, timeout, cleanup]
---

Plan-review-fanout.sh needs per-provider timeout (default 600s, `PLAN_REVIEW_PROVIDER_TIMEOUT_SEC`), Gemini trust-workspace env (`GEMINI_CLI_TRUST_WORKSPACE=true`), Codex argv-based invocation with `</dev/null` (avoid `exec -` hang), and trap cleanup with `pids=()` reset + `trap - INT TERM EXIT` to clear signal handlers after waits (prevents PID-reuse race).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
