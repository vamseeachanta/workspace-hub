---
name: crossprovider codex issue-selector-enum-changes-require-cross-gate-a
description: Issue selector enum changes require cross-gate allowlist updates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [authorization, enum-closure, contract]
---

Adding a provider/round/root to the issue selector enum must be paired with updates to contract allow-context validation, manifest contracts, and CI retained selector loop assertions. A single enum closure point does not auto-propagate authorization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
