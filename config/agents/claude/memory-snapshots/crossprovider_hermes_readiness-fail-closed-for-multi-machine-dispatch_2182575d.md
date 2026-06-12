---
name: crossprovider hermes readiness-fail-closed-for-multi-machine-dispatch
description: Readiness fail-closed for multi-machine dispatch: env vars, host-local evidence, clean worktree
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness-gate, multi-machine-dispatch, fail-closed]
---

Multi-machine Telegram/Hermes dispatch must fail closed on missing TELEGRAM_ALLOWED_USERS, TELEGRAM_BOT_TOKEN, host-local readiness evidence, or dirty workspace—not warn. Example: ace-linux-1 readiness fails with `overall_status: fail` when env vars missing; ace-linux-2 fails on missing host-local evidence. **Why:** permissive readiness gates allow silent dispatch failures or credentials leakage. **How to apply:** readiness scripts should exit non-zero on all blockers; orchestrator must check `overall_status: fail` before dispatch; use `--fail-closed` mode as default.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
