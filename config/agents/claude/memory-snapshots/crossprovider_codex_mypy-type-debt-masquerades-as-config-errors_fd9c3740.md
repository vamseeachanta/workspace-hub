---
name: crossprovider codex mypy-type-debt-masquerades-as-config-errors
description: Mypy type-debt masquerades as config errors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [debugging, python, mypy, ci-workflow]
---

When mypy fails with directory/config errors, the real pre-push blocker is usually 1k+ unresolved type errors beneath. Distinguish syntax failures from type debt early; legacy baselines in config unblock faster than fixing errors retroactively.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
