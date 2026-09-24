---
name: crossprovider codex parent-issue-closure-conditions-must-be-explicit
description: Parent issue closure conditions must be explicit and binding
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, decomposition, acceptance-criteria]
---

Umbrella/decomposition issues need to specify exactly what 'done' means: which repo branch verifies closure (e.g., 'worldenergydata main'), what gate must be green (e.g., exact flake8 command), and which provider/machine produces proof. Ambiguous closure semantics (e.g., 'branch is green' vs 'proof exists locally' vs 'main has landed') cause review churn and permit silent scope-weakening.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
