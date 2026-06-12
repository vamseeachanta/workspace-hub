---
name: crossprovider hermes git-hooks-pre-push-must-source-enforcement-env-l
description: Git hooks: pre-push must source enforcement-env like pre-commit does
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hooks, environment-sourcing, enforcement-env]
---

Environment-driven strictness (DISABLE_ENFORCEMENT, FORCE_PLAN_GATE_STRICT) unreliable in pre-push if enforcement-env is not sourced. Pre-commit hook handles this; pre-push typically doesn't. If pre-push lacks env bootstrap, --strict overrides and env vars don't take effect. Patch: ensure pre-push sources .git/hooks/enforcement-env before running gate scripts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
